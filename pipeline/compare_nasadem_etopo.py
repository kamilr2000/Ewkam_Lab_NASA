"""Compare NASADEM and ETOPO topographic features at a common metric scale."""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path

import numpy as np
import pyproj
import rasterio
from pyproj import CRS, Transformer, datadir
from pyproj.transformer import TransformerGroup
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform_bounds

from gshhg_mask import DEFAULT_SHAPE_ROOT, classify_land_points, rasterize_land_mask


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "manifests" / "k017-earth-validation.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "reports" / "k017-validation.json"
RAW_ROOT = REPO_ROOT / "data" / "raw" / "k017"


def _transformer(source: str, target: str) -> Transformer:
    return Transformer.from_crs(source, target, always_xy=True)


def _nasadem_path(manifest: dict[str, object], granule_id: str, layer: str) -> Path:
    tile = next(tile for tile in manifest["nasadem"]["tiles"] if tile["granule_id"] == granule_id)
    filename = tile["files"][layer]["filename"]
    path = RAW_ROOT / "nasadem" / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}; run pipeline/download_k017_assets.py first")
    return path


def _read_hgt(path: Path) -> tuple[np.ndarray, rasterio.Affine, str, float | None]:
    with rasterio.open(path) as source:
        array = source.read(1).astype("float32")
        return array, source.transform, "EPSG:4326", source.nodata


def _warp(
    source_array: np.ndarray,
    source_transform: rasterio.Affine,
    source_crs: str,
    source_nodata: float | int | None,
    destination_shape: tuple[int, int],
    destination_transform: rasterio.Affine,
    destination_crs: str,
    *,
    resampling: Resampling = Resampling.bilinear,
    dtype: str = "float32",
    fill: float | int = np.nan,
) -> np.ndarray:
    destination = np.full(destination_shape, fill, dtype=dtype)
    reproject(
        source=source_array,
        destination=destination,
        src_transform=source_transform,
        src_crs=source_crs,
        src_nodata=source_nodata,
        dst_transform=destination_transform,
        dst_crs=destination_crs,
        dst_nodata=fill,
        resampling=resampling,
        init_dest_nodata=True,
        num_threads=2,
    )
    return destination


def _target_grid(
    bounds: dict[str, float], cell_size_m: int, margin_m: int
) -> tuple[str, rasterio.Affine, tuple[int, int], tuple[float, float, float, float]]:
    center_lon = (bounds["west"] + bounds["east"]) / 2.0
    center_lat = (bounds["south"] + bounds["north"]) / 2.0
    zone = min(60, max(1, math.floor((center_lon + 180.0) / 6.0) + 1))
    epsg = (32600 if center_lat >= 0 else 32700) + zone
    target_crs = f"EPSG:{epsg}"
    west, south, east, north = transform_bounds(
        "EPSG:4326",
        target_crs,
        bounds["west"],
        bounds["south"],
        bounds["east"],
        bounds["north"],
        densify_pts=21,
    )
    left = math.floor((west - margin_m) / cell_size_m) * cell_size_m
    bottom = math.floor((south - margin_m) / cell_size_m) * cell_size_m
    right = math.ceil((east + margin_m) / cell_size_m) * cell_size_m
    top = math.ceil((north + margin_m) / cell_size_m) * cell_size_m
    width = int((right - left) / cell_size_m)
    height = int((top - bottom) / cell_size_m)
    transform = from_origin(left, top, cell_size_m, cell_size_m)
    geographic_bounds = transform_bounds(
        target_crs, "EPSG:4326", left, bottom, right, top, densify_pts=21
    )
    return target_crs, transform, (height, width), geographic_bounds


def _grid_centers(
    shape: tuple[int, int], transform: rasterio.Affine, source_crs: str
) -> tuple[np.ndarray, np.ndarray]:
    rows, columns = np.indices(shape, dtype="float64")
    x = transform.c + (columns + 0.5) * transform.a
    y = transform.f + (rows + 0.5) * transform.e
    lon, lat = _transformer(source_crs, "EPSG:4326").transform(x, y)
    return np.asarray(lon), np.asarray(lat)


def _circle_offsets(radius_cells: int, cell_size_m: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows, columns = np.mgrid[-radius_cells : radius_cells + 1, -radius_cells : radius_cells + 1]
    distances = np.hypot(rows * cell_size_m, columns * cell_size_m)
    inside = distances <= radius_cells * cell_size_m + 1e-9
    return rows[inside], columns[inside], inside


def _shifted_all(valid: np.ndarray, radius: int) -> np.ndarray:
    output = np.ones(valid.shape, dtype=bool)
    height, width = valid.shape
    for row_shift in range(-radius, radius + 1):
        for column_shift in range(-radius, radius + 1):
            shifted = np.zeros(valid.shape, dtype=bool)
            src_r0 = max(0, row_shift)
            src_r1 = min(height, height + row_shift)
            src_c0 = max(0, column_shift)
            src_c1 = min(width, width + column_shift)
            dst_r0 = max(0, -row_shift)
            dst_r1 = min(height, height - row_shift)
            dst_c0 = max(0, -column_shift)
            dst_c1 = min(width, width - column_shift)
            shifted[dst_r0:dst_r1, dst_c0:dst_c1] = valid[
                src_r0:src_r1, src_c0:src_c1
            ]
            output &= shifted
    return output


def _terrain_features(
    elevation: np.ndarray,
    valid_land: np.ndarray,
    cell_size_m: int,
    radius_m: int,
) -> dict[str, np.ndarray]:
    valid = valid_land & np.isfinite(elevation)
    slope = np.full(elevation.shape, np.nan, dtype="float32")
    roughness = np.full(elevation.shape, np.nan, dtype="float32")
    relief = np.full(elevation.shape, np.nan, dtype="float32")

    # Full 3x3 metric support prevents gradients from crossing a coast or gap.
    dz_drow, dz_dcolumn = np.gradient(elevation, float(cell_size_m), edge_order=1)
    slope_values = np.degrees(np.arctan(np.hypot(dz_drow, dz_dcolumn)))
    slope_valid = _shifted_all(valid, 1)
    slope[slope_valid] = slope_values[slope_valid].astype("float32")

    radius_cells = int(round(radius_m / cell_size_m))
    row_offsets, column_offsets, disk = _circle_offsets(radius_cells, cell_size_m)
    total_samples = int(disk.sum())
    min_samples = math.ceil(total_samples * 0.7)
    height, width = elevation.shape
    for row, column in np.argwhere(valid):
        if (
            row < radius_cells
            or column < radius_cells
            or row + radius_cells >= height
            or column + radius_cells >= width
        ):
            continue
        sample_rows = row + row_offsets
        sample_columns = column + column_offsets
        sample_mask = valid[sample_rows, sample_columns]
        if int(sample_mask.sum()) < min_samples:
            continue
        values = elevation[sample_rows[sample_mask], sample_columns[sample_mask]].astype(
            "float64"
        )
        dx = column_offsets[sample_mask].astype("float64") * cell_size_m
        dy = -row_offsets[sample_mask].astype("float64") * cell_size_m
        design = np.column_stack((np.ones(values.size), dx, dy))
        coefficients, _, _, _ = np.linalg.lstsq(design, values, rcond=None)
        residuals = values - design @ coefficients
        roughness[row, column] = float(np.std(residuals, ddof=0))
        relief[row, column] = float(np.percentile(values, 95) - np.percentile(values, 5))

    return {"slope_deg": slope, "roughness_m": roughness, "relief_m": relief}


def _summary(values: np.ndarray) -> dict[str, float | int | None]:
    values = values[np.isfinite(values)]
    if not values.size:
        return {"count": 0, "mean": None, "p05": None, "median": None, "p95": None}
    return {
        "count": int(values.size),
        "mean": float(values.mean()),
        "p05": float(np.percentile(values, 5)),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
    }


def _difference_metrics(left: np.ndarray, right: np.ndarray, valid: np.ndarray) -> dict[str, float | int | None]:
    common = valid & np.isfinite(left) & np.isfinite(right)
    count = int(common.sum())
    if not count:
        return {"count": 0, "mean_bias": None, "mae": None, "rmse": None, "median_abs_error": None}
    difference = left[common].astype("float64") - right[common].astype("float64")
    return {
        "count": count,
        "mean_bias": float(difference.mean()),
        "mae": float(np.abs(difference).mean()),
        "rmse": float(np.sqrt(np.square(difference).mean())),
        "median_abs_error": float(np.median(np.abs(difference))),
    }


def _load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_mask_checks(manifest: dict[str, object]) -> list[dict[str, object]]:
    points = [
        (record["id"], float(record["longitude"]), float(record["latitude"]))
        for record in manifest["mask_checks"]
    ]
    actual = {row["id"]: row for row in classify_land_points(points, DEFAULT_SHAPE_ROOT)}
    expected = {record["id"]: record for record in manifest["mask_checks"]}
    results = []
    tile_arrays: dict[str, tuple[np.ndarray, Path]] = {}
    for name, row in actual.items():
        record = expected[name]
        wanted = record["expected"] == "land"
        checks_passed = [row["land"] == wanted]
        result = {**row, "expected": record["expected"]}

        granule_id = record.get("nasadem_granule")
        if granule_id:
            hgt_path = _nasadem_path(manifest, str(granule_id), "hgt")
            swb_path = _nasadem_path(manifest, str(granule_id), "swb")
            with rasterio.open(hgt_path) as source:
                sample = float(list(source.sample([(row["longitude"], row["latitude"])]))[0][0])
                raster_row, raster_column = source.index(row["longitude"], row["latitude"])
                if not (0 <= raster_row < source.height and 0 <= raster_column < source.width):
                    raise ValueError(f"{name}: NASADEM point falls outside {granule_id}")
            if str(granule_id) not in tile_arrays:
                swb_values = np.fromfile(swb_path, dtype="uint8").reshape((3601, 3601))
                tile_arrays[str(granule_id)] = (swb_values, hgt_path)
            swb_values, _ = tile_arrays[str(granule_id)]
            swb_class_code = int(swb_values[raster_row, raster_column])
            swb_class = {0: "land", 255: "water"}.get(swb_class_code, "unknown")
            result["nasadem_hgt_m_egm96"] = sample
            result["nasadem_swb_class"] = swb_class
            if "nasadem_swb_expected" in record:
                swb_passed = swb_class == record["nasadem_swb_expected"]
                result["nasadem_swb_expected"] = record["nasadem_swb_expected"]
                result["nasadem_swb_passed"] = swb_passed
                checks_passed.append(swb_passed)
            if "nasadem_hgt_below_m" in record:
                below_passed = sample < float(record["nasadem_hgt_below_m"])
                result["nasadem_hgt_below_m"] = record["nasadem_hgt_below_m"]
                result["nasadem_below_sea_level_passed"] = below_passed
                checks_passed.append(below_passed)

        result["passed"] = all(checks_passed)
        results.append(result)
    return results


def run_comparison(manifest: dict[str, object], manifest_path: Path) -> dict[str, object]:
    nasadem = manifest["nasadem"]
    cell_size_m = int(manifest["comparison"]["common_grid_resolution_m"])
    radius_m = int(manifest["comparison"]["feature_window_radius_m"])
    proj_dir = RAW_ROOT / "proj"
    datadir.append_data_dir(str(proj_dir))
    group = TransformerGroup(
        CRS.from_user_input("EPSG:4326+5773"),
        CRS.from_user_input("EPSG:4326+3855"),
        always_xy=True,
    )
    if not group.transformers or group.transformers[0].accuracy < 0:
        raise RuntimeError("PROJ could not construct an EGM96-to-EGM2008 grid transformation")
    vertical_transformer = group.transformers[0]
    to_geographic = None
    results = []

    for aoi in manifest["comparison_aois"]:
        bounds = aoi["bounds_wgs84"]
        target_crs, target_transform, shape, source_mask_bounds = _target_grid(
            bounds, cell_size_m, radius_m + 2 * cell_size_m
        )
        granule_id = aoi["nasadem_granule"]
        hgt_path = _nasadem_path(manifest, granule_id, "hgt")
        swb_path = _nasadem_path(manifest, granule_id, "swb")
        num_path = _nasadem_path(manifest, granule_id, "num")
        etopo_path = REPO_ROOT / aoi["etopo_file"]
        if not etopo_path.is_file():
            raise FileNotFoundError(f"Missing comparison ETOPO tile {etopo_path}")

        nasa_source, nasa_transform, nasa_crs, nasa_nodata = _read_hgt(hgt_path)
        nasa = _warp(
            nasa_source,
            nasa_transform,
            nasa_crs,
            nasa_nodata,
            shape,
            target_transform,
            target_crs,
        )
        with rasterio.open(etopo_path) as source:
            etopo_source = source.read(1).astype("float32")
            etopo_transform = source.transform
            etopo_nodata = source.nodata
        etopo = _warp(
            etopo_source,
            etopo_transform,
            "EPSG:4326",
            etopo_nodata,
            shape,
            target_transform,
            target_crs,
        )

        swb_raw = np.fromfile(swb_path, dtype="uint8").reshape((3601, 3601))
        num_raw = np.fromfile(num_path, dtype="uint8").reshape((3601, 3601))
        swb = _warp(
            swb_raw,
            nasa_transform,
            nasa_crs,
            None,
            shape,
            target_transform,
            target_crs,
            resampling=Resampling.nearest,
            dtype="uint8",
            fill=127,
        )
        num = _warp(
            num_raw,
            nasa_transform,
            nasa_crs,
            None,
            shape,
            target_transform,
            target_crs,
            resampling=Resampling.nearest,
            dtype="uint8",
            fill=255,
        )
        land = rasterize_land_mask(
            bounds=source_mask_bounds,
            out_shape=shape,
            transform=target_transform,
            shape_root=DEFAULT_SHAPE_ROOT,
            dst_crs=target_crs,
        )
        lon, lat = _grid_centers(shape, target_transform, target_crs)
        in_aoi = (
            (lon >= bounds["west"])
            & (lon <= bounds["east"])
            & (lat >= bounds["south"])
            & (lat <= bounds["north"])
        )
        swb_known = (swb == 0) | (swb == 255)
        swb_land = swb == 0
        swb_evaluable = in_aoi & swb_known
        mask_agreement = land == swb_land

        if to_geographic is None:
            to_geographic = _transformer(target_crs, "EPSG:4326")
        x = target_transform.c + (np.indices(shape, dtype="float64")[1] + 0.5) * cell_size_m
        y = target_transform.f + (np.indices(shape, dtype="float64")[0] + 0.5) * -cell_size_m
        grid_lon, grid_lat = to_geographic.transform(x, y)
        _, _, vertical_offset = vertical_transformer.transform(
            grid_lon, grid_lat, np.zeros(shape, dtype="float64")
        )
        vertical_offset = np.asarray(vertical_offset, dtype="float32")
        nasa_egm2008 = nasa + vertical_offset

        common_land = (
            land
            & swb_land
            & np.isfinite(nasa_egm2008)
            & np.isfinite(etopo)
        )
        nasa_features = _terrain_features(nasa_egm2008, common_land, cell_size_m, radius_m)
        etopo_features = _terrain_features(etopo, common_land, cell_size_m, radius_m)

        feature_results = {}
        for feature_id in ("slope_deg", "roughness_m", "relief_m"):
            nasa_values = nasa_features[feature_id]
            etopo_values = etopo_features[feature_id]
            eligible = in_aoi & land & swb_land
            feature_results[feature_id] = {
                "unit": next(
                    item["unit"]
                    for item in manifest["comparison"]["features"]
                    if item["id"] == feature_id
                ),
                "nasadem": _summary(nasa_values[eligible]),
                "etopo": _summary(etopo_values[eligible]),
                "nasadem_minus_etopo": _difference_metrics(
                    nasa_values, etopo_values, eligible
                ),
            }

        height_valid = in_aoi & common_land
        num_values, num_counts = np.unique(num[height_valid], return_counts=True)
        record_by_granule = next(
            tile for tile in nasadem["tiles"] if tile["granule_id"] == granule_id
        )
        comparison = {
            "aoi_id": aoi["aoi_id"],
            "label": aoi["label"],
            "nasadem_granule": granule_id,
            "target_crs": target_crs,
            "cell_size_m": cell_size_m,
            "feature_window": {
                "shape": "circular",
                "radius_m": radius_m,
                "radius_cells": int(round(radius_m / cell_size_m)),
                "minimum_valid_fraction": 0.7,
            },
            "counts": {
                "target_grid_cells": int(shape[0] * shape[1]),
                "aoi_cells": int(in_aoi.sum()),
                "gshhg_land_cells_in_aoi": int((in_aoi & land).sum()),
                "nasadem_swb_land_cells_in_aoi": int((in_aoi & swb_land).sum()),
                "nasadem_swb_water_cells_in_aoi": int((in_aoi & (swb == 255)).sum()),
                "gshhg_swb_evaluable_cells": int(swb_evaluable.sum()),
                "gshhg_swb_agreement_cells": int((swb_evaluable & mask_agreement).sum()),
                "gshhg_swb_disagreement_cells": int((swb_evaluable & ~mask_agreement).sum()),
                "common_land_dem_cells": int(height_valid.sum()),
            },
            "gshhg_swb_agreement_fraction": (
                float((swb_evaluable & mask_agreement).sum() / swb_evaluable.sum())
                if swb_evaluable.any()
                else None
            ),
            "nasadem_sources": {
                "hgt_sha256": record_by_granule["files"]["hgt"]["sha256"],
                "num_sha256": record_by_granule["files"]["num"]["sha256"],
                "swb_sha256": record_by_granule["files"]["swb"]["sha256"],
                "num_class_histogram": {
                    str(int(value)): int(count)
                    for value, count in zip(num_values, num_counts)
                },
            },
            "vertical_conversion": {
                "source": "EGM96 geoid height",
                "target": "EGM2008 geoid height",
                "operation": vertical_transformer.description,
                "accuracy_m": vertical_transformer.accuracy,
                "offset_m": _summary(vertical_offset[in_aoi & land & swb_land]),
                "absolute_height_difference_m": _difference_metrics(
                    nasa_egm2008, etopo, height_valid
                ),
            },
            "features": feature_results,
        }
        results.append(comparison)
        print(
            f"{aoi['aoi_id']}: {comparison['counts']['common_land_dem_cells']} common land cells; "
            f"SWB disagreements {comparison['counts']['gshhg_swb_disagreement_cells']}"
        )

    mask_checks = _load_mask_checks(manifest)
    return {
        "report_version": 1,
        "task_id": "K-017",
        "manifest": manifest_path.relative_to(REPO_ROOT).as_posix(),
        "accessed_at": manifest["accessed_at"],
        "processing": {
            "comparison_grid_resolution_m": cell_size_m,
            "feature_window_radius_m": radius_m,
            "horizontal_resampling": "bilinear for HGT; nearest-neighbor for NUM and SWB",
            "validity": "same GSHHG land, NASADEM SWB land, and finite DEM cells for both products",
            "vertical_conversion": "PROJ EGM96-to-EGM2008 operation with local NGA grids; ETOPO already uses EGM2008",
            "python": platform.python_version(),
            "numpy": np.__version__,
            "rasterio": rasterio.__version__,
            "pyproj": pyproj.__version__,
        },
        "vertical_operation": {
            "name": vertical_transformer.description,
            "accuracy_m": vertical_transformer.accuracy,
            "definition": vertical_transformer.definition,
        },
        "comparison_aois": results,
        "nasadem_tile_validation": [
            {
                "granule_id": tile["granule_id"],
                "archive_size_bytes": tile["archive_size_bytes"],
                "archive_sha256": tile["archive_sha256"],
                "files": tile["files"],
                "observed_value_summary": tile["observed_value_summary"],
            }
            for tile in nasadem["tiles"]
        ],
        "mask_checks": mask_checks,
        "mask_checks_passed": all(row["passed"] for row in mask_checks),
        "limitations": [
            "NASADEM covers the SRTM latitude band only; GSHHG L6 supplies grounded Antarctica outside that band.",
            "This validation compares three selected AOIs and does not establish global DEM agreement or a global ranking.",
            "A full global GSHHG mask raster was not materialized; this run validates point classification and rasterization over the three AOIs.",
            "GSHHG full-resolution polygons do not guarantee that islands smaller than a 2 km cell remain individually resolvable.",
            "Global antimeridian and polar raster tiling behavior remains to be checked in the global pipeline task.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare NASADEM and ETOPO in three K-017 AOIs on a common 2 km grid."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = _load_manifest(args.manifest)
    report = run_comparison(manifest, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote validation report: {args.output}")
    return 0 if report["mask_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
