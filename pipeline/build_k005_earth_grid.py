"""Build real, resumable regional Earth terrain packages for K-005."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import time

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds

from features.terrain import compute_terrain_features, manual_terrain_sample
from grid.earth_grid import (
    ProjectedGrid,
    global_60_arcsecond_budget,
    grid_cell_areas_km2,
    grid_centers_wgs84,
    make_local_utm_grid,
    warp_raster_to_grid,
)
from gshhg_mask import DEFAULT_SHAPE_ROOT, classify_land_points, rasterize_land_mask


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST_PATH = REPO_ROOT / "data" / "manifests" / "k017-earth-validation.json"
OUTPUT_ROOT = REPO_ROOT / "data" / "derived" / "k005-earth-grid"
CHECKPOINT_ROOT = REPO_ROOT / "data" / "processed" / "k005-earth-grid"
MANIFEST_ROOT = REPO_ROOT / "data" / "manifests"
REPORT_PATH = REPO_ROOT / "data" / "reports" / "k005-earth-grid.json"
CELL_SIZE_M = 2_000
WINDOW_RADIUS_M = 10_000
MIN_VALID_FRACTION = 0.9
LAND_FRACTION_OVERSAMPLE = 4
GRID_VERSION_PREFIX = "k005-earth-2km"
MODEL_VERSION = "terrain-p0-k005-v2"
CSV_FIELDS = [
    "pixel_id",
    "grid_row",
    "grid_col",
    "center_lon_deg",
    "center_lat_deg",
    "pixel_area_km2",
    "land_fraction_4x",
    "is_land_center",
    "dem_valid",
    "slope_deg",
    "roughness_m",
    "relief_m",
    "slope_support_fraction",
    "window_land_fraction",
    "window_valid_fraction",
    "window_valid_count",
    "window_sample_count",
    "is_eligible",
    "missing_reason",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _code_fingerprint() -> str:
    paths = [
        Path(__file__),
        REPO_ROOT / "pipeline" / "grid" / "earth_grid.py",
        REPO_ROOT / "pipeline" / "features" / "terrain.py",
        REPO_ROOT / "pipeline" / "gshhg_mask.py",
    ]
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda value: value.as_posix()):
        digest.update(path.relative_to(REPO_ROOT).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _find_source_file_record(
    manifest: dict[str, object],
    filename: str,
    *,
    preferred_dataset_id: str | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    file_record: dict[str, object] | None = None
    for dataset in manifest.get("datasets", []):
        if not isinstance(dataset, dict):
            continue
        for record in dataset.get("files", []):
            if isinstance(record, dict) and record.get("filename") == filename:
                file_record = record
                break
        if file_record is not None:
            break
    if file_record is None:
        raise KeyError(f"No pinned source record for {filename} in {SOURCE_MANIFEST_PATH}")
    if preferred_dataset_id is None:
        for dataset in manifest.get("datasets", []):
            if isinstance(dataset, dict) and file_record in dataset.get("files", []):
                return dataset, file_record
        raise KeyError(f"No source dataset context for {filename}")
    for dataset in manifest.get("datasets", []):
        if isinstance(dataset, dict) and dataset.get("dataset_id") == preferred_dataset_id:
            return dataset, file_record
    raise KeyError(f"No dataset context {preferred_dataset_id!r} in {SOURCE_MANIFEST_PATH}")


def _verify_pinned_source(path: Path, record: dict[str, object]) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}; run `python pipeline/download_k005_sources.py` first")
    size_bytes = path.stat().st_size
    digest = sha256_file(path)
    expected_size = record.get("size_bytes")
    expected_sha = record.get("sha256")
    if expected_size is not None and size_bytes != int(expected_size):
        raise ValueError(f"Pinned size mismatch for {path.name}: {size_bytes} != {expected_size}")
    if expected_sha is not None and digest.lower() != str(expected_sha).lower():
        raise ValueError(f"Pinned SHA-256 mismatch for {path.name}")
    return {"path": path.relative_to(REPO_ROOT).as_posix(), "size_bytes": size_bytes, "sha256": digest}


def _source_manifest() -> dict[str, object]:
    return json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))


def _aoi_records(source_manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(aoi["aoi_id"]): aoi for aoi in source_manifest["comparison_aois"]}


def _gshhg_archive(source_manifest: dict[str, object]) -> tuple[Path, dict[str, object], dict[str, object]]:
    dataset, file_record = _find_source_file_record(source_manifest, "gshhg-shp-2.3.7.zip")
    path = REPO_ROOT / "data" / "raw" / "k017" / "gshhg" / "gshhg-shp-2.3.7.zip"
    verified = _verify_pinned_source(path, file_record)
    return path, dataset, {**file_record, **verified}


def _check_mask_controls() -> list[dict[str, object]]:
    checks = [
        ("big-island-land", -155.5, 19.5, True, "island land is retained"),
        ("big-island-ocean", -155.99, 19.5, False, "coastal ocean is excluded"),
        ("qattara-depression", 27.1, 29.1, True, "below-sea-level land is retained"),
        ("antarctica-grounded", 0.0, -85.0, True, "grounded Antarctic L6 land is retained"),
    ]
    classified = classify_land_points(
        [(name, longitude, latitude) for name, longitude, latitude, _, _ in checks],
        shape_root=DEFAULT_SHAPE_ROOT,
    )
    by_id = {row["id"]: row for row in classified}
    results = []
    for name, longitude, latitude, expected, purpose in checks:
        row = by_id[name]
        actual = bool(row["land"])
        results.append(
            {
                "id": name,
                "longitude": longitude,
                "latitude": latitude,
                "expected_land": expected,
                "actual_land": actual,
                "deepest_gshhg_level": row["deepest_level"],
                "passed": actual is expected,
                "purpose": purpose,
            }
        )
    if not all(row["passed"] for row in results):
        raise AssertionError("GSHHG point controls failed")

    qattara_record = next(row for row in results if row["id"] == "qattara-depression")
    qattara_report_path = REPO_ROOT / "data" / "reports" / "k017-validation.json"
    qattara_report = json.loads(qattara_report_path.read_text(encoding="utf-8"))
    qattara_evidence = next(row for row in qattara_report["mask_checks"] if row["id"] == "qattara-depression")
    if not qattara_evidence["passed"] or not qattara_evidence["nasadem_below_sea_level_passed"]:
        raise AssertionError("Pinned K-017 NASADEM Qattara depression control did not pass")
    qattara_record["nasadem_height_m_egm96"] = qattara_evidence["nasadem_hgt_m_egm96"]
    qattara_record["nasadem_swb_class"] = qattara_evidence["nasadem_swb_class"]
    qattara_record["validation_evidence"] = {
        "report_path": qattara_report_path.relative_to(REPO_ROOT).as_posix(),
        "report_sha256": sha256_file(qattara_report_path),
        "method": "Reuse the already committed K-017 point check; it records the raw NASADEM HGT value, SWB class, and GSHHG classification.",
    }
    return results


def _land_fraction_supersampled(grid: ProjectedGrid, factor: int) -> np.ndarray:
    height, width = grid.shape
    left, bottom, right, top = grid.bounds_m
    transform = from_origin(left, top, grid.cell_size_m / factor, grid.cell_size_m / factor)
    mask_bounds = transform_bounds(grid.crs, "EPSG:4326", left, bottom, right, top, densify_pts=21)
    subcell_mask = rasterize_land_mask(
        bounds=mask_bounds,
        out_shape=(height * factor, width * factor),
        transform=transform,
        shape_root=DEFAULT_SHAPE_ROOT,
        dst_crs=grid.crs,
    )
    return subcell_mask.reshape(height, factor, width, factor).mean(axis=(1, 3), dtype="float32")


def _cell_reason(
    *,
    is_land: bool,
    dem_valid: bool,
    slope_valid: bool,
    window_fraction: float,
    min_valid_fraction: float,
) -> str | None:
    if not is_land:
        return "not_land"
    if not dem_valid:
        return "dem_nodata"
    if not slope_valid:
        return "insufficient_slope_support"
    if window_fraction + 1e-7 < min_valid_fraction:
        return "insufficient_window_support"
    return None


def _format_number(value: float | np.floating | None, significant: int = 9) -> str:
    if value is None or not np.isfinite(value):
        return ""
    return format(float(value), f".{significant}g")


def _write_cells(
    path: Path,
    *,
    aoi_id: str,
    grid_version: str,
    grid: ProjectedGrid,
    longitude: np.ndarray,
    latitude: np.ndarray,
    in_aoi: np.ndarray,
    elevation: np.ndarray,
    land: np.ndarray,
    land_fraction: np.ndarray,
    features: object,
) -> dict[str, object]:
    rows, columns = np.nonzero(in_aoi)
    cell_areas_km2 = grid_cell_areas_km2(grid, rows, columns)
    exclusion_counts = {
        "not_land": 0,
        "dem_nodata": 0,
        "insufficient_slope_support": 0,
        "insufficient_window_support": 0,
    }
    eligible_count = 0
    eligible_area_km2 = 0.0
    temp_path = path.with_suffix(path.suffix + ".part")
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with temp_path.open("wb") as raw_output:
            with gzip.GzipFile(fileobj=raw_output, mode="wb", filename="", mtime=0, compresslevel=6) as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as text_output:
                    writer = csv.DictWriter(text_output, fieldnames=CSV_FIELDS, lineterminator="\n")
                    writer.writeheader()
                    for row, column, area_km2 in zip(rows.tolist(), columns.tolist(), cell_areas_km2.tolist()):
                        is_land = bool(land[row, column])
                        dem_valid = bool(np.isfinite(elevation[row, column]))
                        slope_fraction = float(features.slope_support_fraction[row, column])
                        window_fraction = float(features.window_valid_fraction[row, column])
                        reason = _cell_reason(
                            is_land=is_land,
                            dem_valid=dem_valid,
                            slope_valid=slope_fraction >= 1.0 - 1e-7,
                            window_fraction=window_fraction,
                            min_valid_fraction=MIN_VALID_FRACTION,
                        )
                        if reason is None:
                            eligible_count += 1
                            eligible_area_km2 += area_km2
                        else:
                            exclusion_counts[reason] += 1
                        writer.writerow(
                            {
                                "pixel_id": f"earth:{grid_version}:r{row:05d}:c{column:05d}",
                                "grid_row": row,
                                "grid_col": column,
                                "center_lon_deg": _format_number(longitude[row, column], 10),
                                "center_lat_deg": _format_number(latitude[row, column], 10),
                                "pixel_area_km2": _format_number(area_km2, 8),
                                "land_fraction_4x": _format_number(land_fraction[row, column], 8),
                                "is_land_center": str(is_land).lower(),
                                "dem_valid": str(dem_valid).lower(),
                                "slope_deg": _format_number(features.slope_deg[row, column]),
                                "roughness_m": _format_number(features.roughness_m[row, column]),
                                "relief_m": _format_number(features.relief_m[row, column]),
                                "slope_support_fraction": _format_number(slope_fraction, 8),
                                "window_land_fraction": _format_number(features.window_land_fraction[row, column], 8),
                                "window_valid_fraction": _format_number(window_fraction, 8),
                                "window_valid_count": int(features.window_valid_count[row, column]),
                                "window_sample_count": features.window_sample_count,
                                "is_eligible": str(reason is None).lower(),
                                "missing_reason": reason or "",
                            }
                        )
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return {
        "total_pixels": int(rows.size),
        "eligible_pixels": eligible_count,
        "excluded_by_reason": exclusion_counts,
        "nominal_cell_area_km2": grid.cell_area_km2,
        "minimum_pixel_area_km2": float(cell_areas_km2.min()) if cell_areas_km2.size else 0.0,
        "maximum_pixel_area_km2": float(cell_areas_km2.max()) if cell_areas_km2.size else 0.0,
        "total_area_km2": float(cell_areas_km2.sum()),
        "eligible_area_km2": eligible_area_km2,
    }


def _summary(values: np.ndarray) -> dict[str, float | int | None]:
    valid = np.asarray(values)[np.isfinite(values)]
    if not valid.size:
        return {"count": 0, "mean": None, "p05": None, "median": None, "p95": None}
    return {
        "count": int(valid.size),
        "mean": float(valid.mean()),
        "p05": float(np.percentile(valid, 5)),
        "median": float(np.median(valid)),
        "p95": float(np.percentile(valid, 95)),
    }


def _manual_check(
    *,
    grid: ProjectedGrid,
    aoi_bounds: tuple[float, float, float, float],
    longitude: np.ndarray,
    latitude: np.ndarray,
    elevation: np.ndarray,
    land: np.ndarray,
    features: object,
) -> dict[str, object]:
    west, south, east, north = aoi_bounds
    candidates = np.argwhere(
        (longitude >= west)
        & (longitude <= east)
        & (latitude >= south)
        & (latitude <= north)
        & land
        & np.isfinite(features.slope_deg)
        & np.isfinite(features.roughness_m)
        & np.isfinite(features.relief_m)
    )
    if not candidates.size:
        raise RuntimeError("No eligible real cell is available for the manual feature check")
    mid_lon = (west + east) / 2.0
    mid_lat = (south + north) / 2.0
    centers = np.asarray(
        [
            (longitude[row, column] - mid_lon) ** 2 + (latitude[row, column] - mid_lat) ** 2
            for row, column in candidates
        ]
    )
    row, column = (int(value) for value in candidates[int(np.argmin(centers))])
    manual = manual_terrain_sample(
        elevation,
        land,
        row=row,
        column=column,
        cell_size_m=grid.cell_size_m,
        window_radius_m=WINDOW_RADIUS_M,
    )
    processed = {
        "slope_deg": float(features.slope_deg[row, column]),
        "roughness_m": float(features.roughness_m[row, column]),
        "relief_m": float(features.relief_m[row, column]),
    }
    differences = {key: abs(processed[key] - float(manual[key])) for key in processed}
    passed = all(value <= 0.001 for value in differences.values())
    if not passed:
        raise AssertionError(f"Manual terrain check differs from pipeline values: {differences}")
    return {
        "pixel_id": f"earth:{GRID_VERSION_PREFIX}-{aoi_id_from_bounds(aoi_bounds)}:r{row:05d}:c{column:05d}",
        "center_lon_deg": float(longitude[row, column]),
        "center_lat_deg": float(latitude[row, column]),
        "pipeline_values": processed,
        "manual_values": {key: float(manual[key]) for key in processed},
        "absolute_differences": differences,
        "maximum_absolute_difference": max(differences.values()),
        "passed": passed,
    }


def aoi_id_from_bounds(bounds: tuple[float, float, float, float]) -> str:
    source = _source_manifest()
    for aoi in source["comparison_aois"]:
        b = aoi["bounds_wgs84"]
        if bounds == (b["west"], b["south"], b["east"], b["north"]):
            return str(aoi["aoi_id"])
    raise KeyError("AOI bounds are not in the K-017 source manifest")


def _build_source_objects(
    source_manifest: dict[str, object],
    etopo_dataset: dict[str, object],
    gshhg_dataset: dict[str, object],
    etopo_file: dict[str, object],
) -> tuple[list[dict[str, object]], str]:
    accessed_date = str(source_manifest.get("accessed_at", ""))
    accessed_reason = (
        f"The pinned K-017 source record gives access date {accessed_date!r} at date precision only; time of day is unavailable."
    )
    return [
        {
            "source_id": "noaa-etopo-2022",
            "provider": etopo_dataset["provider"],
            "title": etopo_dataset["title"],
            "product_version": etopo_dataset["product_version"],
            "url": etopo_file["url"],
            "doi": etopo_dataset["doi"],
            "citation": "NOAA National Centers for Environmental Information. ETOPO 2022 15 Arc-Second Global Relief Model, surface elevation tiles. https://doi.org/10.25921/fd45-gt74.",
            "accessed_at": None,
            "license": {"name": etopo_dataset["license"]["id"], "url": etopo_dataset["license"]["evidence_url"]},
            "role": "Earth surface elevation input. GSHHG ocean/water samples are excluded before area-averaging land heights to the regional metric grid; absolute elevation is not a cross-body scoring feature.",
        },
        {
            "source_id": "gshhg-2.3.7",
            "provider": "Paul Wessel and Walter H. F. Smith, SOEST University of Hawai'i and NOAA",
            "title": gshhg_dataset["title"],
            "product_version": str(gshhg_dataset["product_version"]),
            "url": "https://www.soest.hawaii.edu/pwessel/gshhg/gshhg-shp-2.3.7.zip",
            "doi": gshhg_dataset["doi"],
            "citation": "Wessel, P. and W. H. F. Smith. Global Self-consistent, Hierarchical, High-resolution Geography Database (GSHHG), version 2.3.7. https://doi.org/10.5281/zenodo.7007502.",
            "accessed_at": None,
            "license": {"name": "LGPL-3.0-or-later", "url": "https://www.soest.hawaii.edu/wessel/gshhg/"},
            "role": "Independent land/water mask. L1/L3 land, L2/L4 water, L5 excluded, L6 grounded Antarctic land.",
        },
    ], accessed_reason


def _make_dataset_manifest(
    *,
    aoi: dict[str, object],
    grid: ProjectedGrid,
    counts: dict[str, object],
    output_path: Path,
    output_sha256: str,
    source_file: dict[str, object],
    gshhg_file: dict[str, object],
    etopo_dataset: dict[str, object],
    gshhg_dataset: dict[str, object],
    source_manifest: dict[str, object],
    code_sha256: str,
    generated_at: str,
) -> dict[str, object]:
    bounds = aoi["bounds_wgs84"]
    bounds_tuple = (bounds["west"], bounds["south"], bounds["east"], bounds["north"])
    grid_version = f"{GRID_VERSION_PREFIX}-{aoi['aoi_id']}-v2"
    sources, access_reason = _build_source_objects(source_manifest, etopo_dataset, gshhg_dataset, source_file)
    missing_reasons = {
        "sources[0].accessed_at": access_reason,
        "sources[1].accessed_at": access_reason,
        "temporal_coverage.start_date": "ETOPO 2022 is a static topographic product; the source manifest does not provide one acquisition date for the regional tile.",
        "temporal_coverage.end_date": "ETOPO 2022 is a static topographic product; the source manifest does not provide one acquisition date for the regional tile.",
    }
    left, bottom, right, top = grid.bounds_m
    return {
        "contract_version": "1.0.0",
        "is_synthetic": False,
        "dataset_id": f"earth-{aoi['aoi_id']}-terrain",
        "dataset_version": grid_version,
        "provider": "Terra Analog, derived from NOAA NCEI ETOPO 2022 with the GSHHG land mask",
        "role": "earth_search",
        "body": "earth",
        "product_version": "K-005 v2 land-masked features; ETOPO_2022_v1 15 arc-second surface",
        "generated_at": generated_at,
        "sources": sources,
        "files": [
            {
                "path": output_path.relative_to(REPO_ROOT).as_posix(),
                "sha256": output_sha256,
                "size_bytes": output_path.stat().st_size,
                "source_id": "noaa-etopo-2022",
            }
        ],
        "temporal_coverage": {"start_date": None, "end_date": None, "missing_reason": "Static terrain surface; no single acquisition interval is provided."},
        "spatial_coverage": {
            "coordinate_system_id": "EPSG:4326",
            "bounds": [bounds_tuple[0], bounds_tuple[1], bounds_tuple[2], bounds_tuple[3]],
            "bounds_order": ["min_x", "min_y", "max_x", "max_y"],
            "bounds_unit": "degree",
            "missing_reason": None,
            "total_pixels": counts["total_pixels"],
            "eligible_pixels": counts["eligible_pixels"],
            "excluded_by_reason": counts["excluded_by_reason"],
            "total_area_km2": counts["total_area_km2"],
            "eligible_area_km2": counts["eligible_area_km2"],
        },
        "grid": {
            "grid_version": grid_version,
            "model_version": MODEL_VERSION,
            "cell_id_scheme": f"earth:{grid_version}:r<zero-based-row>:c<zero-based-column> in the aligned {grid.crs} grid",
            "nominal_resolution_m": grid.cell_size_m,
            "effective_resolution_m": grid.cell_size_m,
            "resolution_missing_reason": None,
            "mask_id": "GSHHG-2.3.7 source land-only, target L1-L4-L6 land-center; land fraction sampled at 4x",
            "vertical_reference": "EGM2008 geoid in source ETOPO; scored features are relative terrain measures.",
        },
        "measurements": [
            {"feature_id": "slope_deg", "unit": "degree", "measurement_scale": "ratio", "source_ids": ["noaa-etopo-2022"]},
            {"feature_id": "roughness_m", "unit": "m", "measurement_scale": "ratio", "source_ids": ["noaa-etopo-2022"]},
            {"feature_id": "relief_m", "unit": "m", "measurement_scale": "ratio", "source_ids": ["noaa-etopo-2022"]},
        ],
        "processing": {
            "code_version": f"sha256:{code_sha256}",
            "processed_at": generated_at,
            "steps": [
                "Verify input file size and SHA-256 against the pinned K-017 source manifest.",
                "Rasterize GSHHG L1/L3/L6 as land and L2/L4 as water at the ETOPO source posting; mask ocean and source no-data before area-averaging land heights to the metric grid.",
                "Rasterize the independent GSHHG hierarchy on the 2,000 m target grid and estimate coastal land fraction from 4x subcell centre samples.",
                "Retain the centre-based land candidate rule; no bathymetry is used as a land elevation sample.",
                "Compute slope with metric 2,000 m gradients; compute local-plane roughness and P95-P05 relief in a 10,000 m circular window.",
                "Retain every AOI cell with stable row/column ID; store unavailable measurements as blank CSV fields with QA reason.",
            ],
            "parameters": {
                "aoi_id": aoi["aoi_id"],
                "aoi_label": aoi["label"],
                "aoi_bounds_wgs84": list(bounds_tuple),
                "aoi_candidate_rule": "Cell centre is inside the declared regional bbox; margin cells support local windows but are not candidates.",
                "metric_crs": grid.crs,
                "grid_transform": [grid.transform.a, grid.transform.b, grid.transform.c, grid.transform.d, grid.transform.e, grid.transform.f],
                "grid_bounds_m": [left, bottom, right, top],
                "grid_shape_rows_columns": list(grid.shape),
                "nominal_cell_size_m": grid.cell_size_m,
                "nominal_cell_area_km2": grid.cell_area_km2,
                "pixel_area_measurement": "WGS84 ellipsoidal polygon area from each cell's four UTM-transformed corners; regional coverage areas sum these pixel areas.",
                "source_etopo_file": source_file,
                "source_mask_archive": gshhg_file,
                "source_resolution_arc_seconds": 15,
                "source_resolution_at_aoi_center_m": {
                    "north_south_approx": 111_132.0 * 15.0 / 3600.0,
                    "east_west_approx": 111_320.0 * math.cos(math.radians((bounds_tuple[1] + bounds_tuple[3]) / 2.0)) * 15.0 / 3600.0,
                },
                "source_vertical_reference": "EGM2008 geoid",
                "elevation_resampling": "average of GSHHG land-only source samples; ocean and source no-data are excluded before resampling",
                "feature_window_shape": "circular",
                "feature_window_radius_m": WINDOW_RADIUS_M,
                "feature_window_radius_cells": int(round(WINDOW_RADIUS_M / grid.cell_size_m)),
                "feature_window_sample_count": 81,
                "minimum_valid_sample_fraction": MIN_VALID_FRACTION,
                "minimum_valid_window_samples": math.ceil(81 * MIN_VALID_FRACTION),
                "slope_requires_complete_3x3_land_dem_support": True,
                "land_fraction_supersampling_factor": LAND_FRACTION_OVERSAMPLE,
                "nodata_policy": "Missing or non-land samples reduce support; no interpolation or zero fill.",
                "output_sha256": output_sha256,
            },
        },
        "quality": {
            "qa_rules": [
                "is_land_center is independent of ETOPO elevation and uses GSHHG hierarchy.",
                "land_fraction_4x is a 4x subcell-centre estimate, not an exact polygon area fraction.",
                "slope requires all 9 cells in its 3x3 neighbourhood to be land with finite DEM.",
                f"roughness_m and relief_m require at least {math.ceil(81 * MIN_VALID_FRACTION)} of 81 expected cells in the 10 km disk to be finite land DEM samples.",
                "A cell is eligible only when it is centre-land and all three feature values are present.",
                "Exclusion reasons are mutually exclusive and sum with eligible_pixels to total_pixels.",
                "Ocean bathymetry is excluded before ETOPO resampling; all unmeasured CSV values are empty strings and zero is never a missing-data sentinel.",
            ],
            "nodata_convention": "Empty CSV cell plus is_eligible=false and missing_reason; source no-data remains NaN during warp and is never filled.",
            "interpolation_fraction": 0.0,
        },
        "limitations": [
            "This is a set of regional candidate cells, not a global search or proof of a global optimum.",
            "A local UTM grid is used only within each declared AOI; pixels from different regional grid versions are not mixed into one ranking.",
            "2 km is the analytical cell and effective output scale; ETOPO source posting is approximately 0.42–0.46 km at these latitudes and aggregation does not add source detail.",
            "The candidate rule uses cell centres in an AOI bbox, so edge cells can extend outside the bbox; the bbox and rule are explicit.",
            "The source land mask follows GSHHG polygon centres at the 15 arc-second ETOPO posting; the separate 4x target-cell land fraction can miss sub-500 m islands or narrow coastline features.",
            "NASADEM's SRTM latitude coverage and its vertical conversion are not used for this ETOPO feature package; NASADEM is an independent validation source in K-017.",
        ],
        "synthetic_reason": None,
        "missing_reasons": missing_reasons,
    }


def _safe_json_value(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _safe_json_value(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_safe_json_value(child) for child in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    return value


def _checkpoint_path(aoi_id: str) -> Path:
    return CHECKPOINT_ROOT / aoi_id / "checkpoint.json"


def _process_aoi(
    aoi_id: str,
    aoi: dict[str, object],
    *,
    source_manifest: dict[str, object],
    gshhg_file: dict[str, object],
    gshhg_dataset: dict[str, object],
    code_sha256: str,
    force: bool,
) -> dict[str, object]:
    started = time.perf_counter()
    bounds = aoi["bounds_wgs84"]
    bounds_wgs84 = (bounds["west"], bounds["south"], bounds["east"], bounds["north"])
    etopo_relative = Path(aoi["etopo_file"])
    etopo_path = REPO_ROOT / etopo_relative
    etopo_dataset, etopo_record = _find_source_file_record(
        source_manifest,
        etopo_path.name,
        preferred_dataset_id="ETOPO_2022_v1_15s_surface",
    )
    etopo_file = {**etopo_record, **_verify_pinned_source(etopo_path, etopo_record)}
    grid = make_local_utm_grid(bounds_wgs84, cell_size_m=CELL_SIZE_M, margin_m=WINDOW_RADIUS_M + 2 * CELL_SIZE_M)
    grid_version = f"{GRID_VERSION_PREFIX}-{aoi_id}-v2"
    config = {
        "aoi_id": aoi_id,
        "aoi_bounds_wgs84": bounds_wgs84,
        "grid_crs": grid.crs,
        "grid_transform": [grid.transform.a, grid.transform.b, grid.transform.c, grid.transform.d, grid.transform.e, grid.transform.f],
        "grid_shape": grid.shape,
        "cell_size_m": CELL_SIZE_M,
        "window_radius_m": WINDOW_RADIUS_M,
        "minimum_valid_fraction": MIN_VALID_FRACTION,
        "land_fraction_oversample": LAND_FRACTION_OVERSAMPLE,
        "etopo_sha256": etopo_file["sha256"],
        "gshhg_sha256": gshhg_file["sha256"],
        "code_sha256": code_sha256,
    }
    config_sha256 = hashlib.sha256(_canonical_json(config)).hexdigest()
    output_path = OUTPUT_ROOT / aoi_id / "earth-cells.csv.gz"
    checkpoint_path = _checkpoint_path(aoi_id)
    if not force and output_path.is_file() and checkpoint_path.is_file():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("config_sha256") == config_sha256 and checkpoint.get("output_sha256") == sha256_file(output_path):
            result = checkpoint["result"]
            result["resumed_from_checkpoint"] = True
            result["processing_seconds"] = 0.0
            manifest_path = MANIFEST_ROOT / f"k005-earth-grid-{aoi_id}.json"
            manifest_sha_matches = False
            if manifest_path.is_file():
                prior_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest_sha_matches = bool(
                    prior_manifest.get("files")
                    and prior_manifest["files"][0].get("sha256") == checkpoint["output_sha256"]
                )
            if not manifest_sha_matches:
                _write_json_atomic(
                    manifest_path,
                    _make_dataset_manifest(
                        aoi=aoi,
                        grid=grid,
                        counts=result["counts"],
                        output_path=output_path,
                        output_sha256=checkpoint["output_sha256"],
                        source_file=etopo_file,
                        gshhg_file=gshhg_file,
                        etopo_dataset=etopo_dataset,
                        gshhg_dataset=gshhg_dataset,
                        source_manifest=source_manifest,
                        code_sha256=code_sha256,
                        generated_at=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    ),
                )
            result["manifest_path"] = manifest_path.relative_to(REPO_ROOT).as_posix()
            return result

    with rasterio.open(etopo_path) as source:
        source_bounds = (source.bounds.left, source.bounds.bottom, source.bounds.right, source.bounds.top)
        source_land_mask = rasterize_land_mask(
            bounds=source_bounds,
            out_shape=(source.height, source.width),
            transform=source.transform,
            shape_root=DEFAULT_SHAPE_ROOT,
            dst_crs="EPSG:4326",
        )
    elevation, source_raster = warp_raster_to_grid(
        etopo_path,
        grid,
        resampling=Resampling.average,
        source_valid_mask=source_land_mask,
    )
    source_raster["source_valid_mask"] = "GSHHG 2.3.7 land at native ETOPO grid; ocean and source no-data excluded before resampling"
    land = rasterize_land_mask(
        bounds=transform_bounds(grid.crs, "EPSG:4326", *grid.bounds_m, densify_pts=21),
        out_shape=grid.shape,
        transform=grid.transform,
        shape_root=DEFAULT_SHAPE_ROOT,
        dst_crs=grid.crs,
    )
    land_fraction = _land_fraction_supersampled(grid, LAND_FRACTION_OVERSAMPLE)
    longitude, latitude = grid_centers_wgs84(grid)
    west, south, east, north = bounds_wgs84
    in_aoi = (longitude >= west) & (longitude <= east) & (latitude >= south) & (latitude <= north)
    features = compute_terrain_features(
        elevation,
        land,
        cell_size_m=CELL_SIZE_M,
        window_radius_m=WINDOW_RADIUS_M,
        minimum_valid_fraction=MIN_VALID_FRACTION,
    )
    counts = _write_cells(
        output_path,
        aoi_id=aoi_id,
        grid_version=grid_version,
        grid=grid,
        longitude=longitude,
        latitude=latitude,
        in_aoi=in_aoi,
        elevation=elevation,
        land=land,
        land_fraction=land_fraction,
        features=features,
    )
    output_sha256 = sha256_file(output_path)
    candidate_mask = in_aoi
    eligible_mask = (
        candidate_mask
        & land
        & np.isfinite(elevation)
        & np.isfinite(features.slope_deg)
        & np.isfinite(features.roughness_m)
        & np.isfinite(features.relief_m)
    )
    manual = _manual_check(
        grid=grid,
        aoi_bounds=bounds_wgs84,
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        land=land,
        features=features,
    )
    manual["pixel_id"] = manual["pixel_id"].replace(
        f"{GRID_VERSION_PREFIX}-{aoi_id_from_bounds(bounds_wgs84)}", grid_version
    )
    excluded_fraction = {
        reason: int(count)
        for reason, count in counts["excluded_by_reason"].items()
        if count
    }
    retained_array_bytes = int(
        elevation.nbytes
        + land.nbytes
        + land_fraction.nbytes
        + longitude.nbytes
        + latitude.nbytes
        + in_aoi.nbytes
        + features.slope_deg.nbytes
        + features.roughness_m.nbytes
        + features.relief_m.nbytes
        + features.slope_support_fraction.nbytes
        + features.window_land_fraction.nbytes
        + features.window_valid_fraction.nbytes
        + features.window_valid_count.nbytes
    )
    result = {
        "aoi_id": aoi_id,
        "label": aoi["label"],
        "bounds_wgs84": list(bounds_wgs84),
        "candidate_rule": "Cell centre lies inside the declared bbox; margin cells are used only for metric windows.",
        "grid_version": grid_version,
        "target_crs": grid.crs,
        "grid_shape_rows_columns": list(grid.shape),
        "grid_cells_in_full_metric_buffer": int(grid.shape[0] * grid.shape[1]),
        "candidate_cells": counts["total_pixels"],
        "land_center_cells": int((in_aoi & land).sum()),
        "cells_with_valid_dem_center": int((in_aoi & np.isfinite(elevation)).sum()),
        "eligible_cells": counts["eligible_pixels"],
        "excluded_by_reason": excluded_fraction,
        "counts": counts,
        "feature_summaries_eligible_only": {
            "slope_deg": _summary(features.slope_deg[eligible_mask]),
            "roughness_m": _summary(features.roughness_m[eligible_mask]),
            "relief_m": _summary(features.relief_m[eligible_mask]),
        },
        "nodata_center_cells": int((candidate_mask & ~np.isfinite(elevation)).sum()),
        "land_fraction_4x_summary_candidates": _summary(land_fraction[candidate_mask]),
        "mean_window_valid_fraction_land_centres": float(features.window_valid_fraction[in_aoi & land].mean()) if (in_aoi & land).any() else None,
        "feature_window": {
            "shape": "circular",
            "radius_m": WINDOW_RADIUS_M,
            "radius_cells": int(round(WINDOW_RADIUS_M / CELL_SIZE_M)),
            "sample_count": features.window_sample_count,
            "minimum_valid_fraction": MIN_VALID_FRACTION,
            "minimum_valid_samples": features.minimum_window_samples,
        },
        "input_etopo": {**etopo_file, "raster": source_raster},
        "input_gshhg_archive": gshhg_file,
        "output": {
            "path": output_path.relative_to(REPO_ROOT).as_posix(),
            "sha256": output_sha256,
            "size_bytes": output_path.stat().st_size,
        },
        "manual_feature_check": manual,
        "retained_numpy_array_bytes_lower_bound": retained_array_bytes,
        "processing_seconds": time.perf_counter() - started,
        "resumed_from_checkpoint": False,
    }
    result = _safe_json_value(result)
    _write_json_atomic(checkpoint_path, {"checkpoint_version": 1, "config_sha256": config_sha256, "output_sha256": output_sha256, "result": result})
    manifest = _make_dataset_manifest(
        aoi=aoi,
        grid=grid,
        counts=counts,
        output_path=output_path,
        output_sha256=output_sha256,
        source_file=etopo_file,
        gshhg_file=gshhg_file,
        etopo_dataset=etopo_dataset,
        gshhg_dataset=gshhg_dataset,
        source_manifest=source_manifest,
        code_sha256=code_sha256,
        generated_at=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )
    manifest_path = MANIFEST_ROOT / f"k005-earth-grid-{aoi_id}.json"
    _write_json_atomic(manifest_path, manifest)
    result["manifest_path"] = manifest_path.relative_to(REPO_ROOT).as_posix()
    return result


def build(aoi_ids: list[str] | None = None, *, force: bool = False) -> dict[str, object]:
    source_manifest = _source_manifest()
    aois = _aoi_records(source_manifest)
    selected = list(aois) if aoi_ids is None else aoi_ids
    unknown = set(selected) - set(aois)
    if unknown:
        raise ValueError(f"Unknown AOI(s): {', '.join(sorted(unknown))}")
    _, gshhg_dataset, gshhg_file = _gshhg_archive(source_manifest)
    mask_controls = _check_mask_controls()
    code_sha256 = _code_fingerprint()
    region_results = []
    for aoi_id in selected:
        print(f"K-005: building {aoi_id}...")
        result = _process_aoi(
            aoi_id,
            aois[aoi_id],
            source_manifest=source_manifest,
            gshhg_file=gshhg_file,
            gshhg_dataset=gshhg_dataset,
            code_sha256=code_sha256,
            force=force,
        )
        region_results.append(result)
        print(
            f"K-005: {aoi_id}: {result['candidate_cells']} cells, "
            f"{result['eligible_cells']} eligible, "
            f"{result['output']['size_bytes']} compressed bytes, "
            f"{result['processing_seconds']:.2f}s"
        )
    report = {
        "report_version": 1,
        "task_id": "K-005",
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "code_sha256": code_sha256,
        "global_scale_budget": global_60_arcsecond_budget(
            feature_window_radius_m=WINDOW_RADIUS_M,
            batch_rows=64,
        ),
        "regional_processing": {
            "analytical_cell_size_m": CELL_SIZE_M,
            "effective_dem_output_scale_m": CELL_SIZE_M,
            "effective_dem_source": "NOAA ETOPO 2022 v1 surface, 15 arc-second posting; GSHHG ocean samples are masked before land-only area averaging to metric target cells",
            "feature_window_radius_m": WINDOW_RADIUS_M,
            "minimum_window_valid_fraction": MIN_VALID_FRACTION,
            "regional_batch_unit": "one AOI package; output and checkpoint are atomically written after each AOI, and a verified checkpoint lets subsequent runs resume without recalculation",
            "global_scope_status": "not built; this task establishes exact scale arithmetic and reproducible regional processing only",
        },
        "mask_controls": mask_controls,
        "mask_controls_passed": all(row["passed"] for row in mask_controls),
        "regional_packages": region_results,
        "limitations": [
            "Three regional AOIs do not establish global coverage, global feature validity, or a global ranking.",
            "Global cost figures are exact grid and array-size arithmetic, not a measured whole-world runtime or measured peak resident set.",
            "The regional builder stores one AOI in memory; global processing still needs spatial tiles, bounded raster windows, and checkpoints per tile.",
            "Polar metric windows and raster geometry require a separate stereographic tile path; the current UTM builder intentionally rejects polar AOIs.",
            "Coastal land fraction is a 4x sampled estimate; small islands and sub-cell coastline detail require a higher-resolution regional check.",
        ],
    }
    report = _safe_json_value(report)
    _write_json_atomic(REPORT_PATH, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build real regional 2 km Earth terrain packages and a 60 arc-second global scale budget.")
    parser.add_argument("--aoi", action="append", help="Process one of the K-017 AOI ids; repeat to select several. Defaults to all three.")
    parser.add_argument("--force", action="store_true", help="Rebuild packages even when a matching output/checkpoint pair is verified.")
    args = parser.parse_args()
    report = build(args.aoi, force=args.force)
    if not report["mask_controls_passed"]:
        raise SystemExit("K-005 GSHHG mask controls failed")
    print(f"K-005 report: {REPORT_PATH.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
