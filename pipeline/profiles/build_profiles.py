"""Build measured Mars and lunar target profiles from the pinned K-004 rasters."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pyproj
import rasterio
from affine import Affine
from pyproj import CRS, Geod, Transformer
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject
from numpy.lib.stride_tricks import sliding_window_view


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW = ROOT / "data" / "raw" / "k004"
DEFAULT_SOURCE_MANIFEST = ROOT / "data" / "manifests" / "k004-source-files.json"
DEFAULT_MANIFEST = ROOT / "data" / "manifests" / "k004-planetary-profiles.json"
PROFILE_DIR = ROOT / "pipeline" / "profiles"

GRID_M = 2_000.0
WINDOW_RADIUS_M = 10_000.0
MIN_WINDOW_VALID_FRACTION = 0.90
TOLERANCE_IQR_MULTIPLIER = 1.5
MARS_RADIUS_M = 3_396_000.0
MOON_RADIUS_M = 1_737_400.0
MARS_CENTER_LAT = 18.41
MARS_CENTER_LON = 77.69
MARS_DIAMETER_M = 47_520.0
MARS_RADIUS_REGION_M = MARS_DIAMETER_M / 2
MOON_CAP_LAT_DEG = -80.0

MOLA_ROWS = 5_632
MOLA_COLS = 11_520
MOLA_PPD = 128.0
MOLA_PX_M = 463.0576672
MOLA_UL_X_M = -10_668_848.652
MOLA_UL_Y_M = 2_607_940.782

MARS_DEM_ID = "mola-megdr-v2-megt-44n000-128ppd"
MARS_COUNT_ID = "mola-megdr-v2-megc-44n000-128ppd"
MOON_DEM_ID = "lola-pgda-80s-80mpp-adjusted-dem"
MOON_COUNT_ID = "lola-pgda-80s-80mpp-adjusted-counts"
MOON_EFFRES_ID = "lola-pgda-80s-80mpp-effective-resolution"
MOON_ERROR_ID = "lola-pgda-80s-80mpp-height-error"

FEATURES = (
    ("slope_deg", "Surface slope", "degree"),
    ("roughness_m", "Local topographic roughness", "meter"),
    ("relief_m", "Local topographic relief", "meter"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text_file(path: Path) -> str:
    """Hash UTF-8 text with normalized newlines so provenance is cross-platform stable."""
    canonical = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def xml_value(path: Path, local_name: str) -> str:
    root = ET.parse(path).getroot()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == local_name and element.text:
            return element.text.strip()
    raise ValueError(f"{path.name}: PDS4 label has no {local_name!r}")


def pds3_value(path: Path, key: str) -> str:
    text = path.read_text(encoding="ascii", errors="replace")
    match = re.search(rf"^\s*{re.escape(key)}\s*=\s*([^\r\n]+)", text, re.MULTILINE)
    if not match:
        raise ValueError(f"{path.name}: PDS3 label has no {key!r}")
    return match.group(1).split("/*", 1)[0].strip().strip('"')


def pds3_number(path: Path, key: str) -> float:
    """Read a numeric PDS3 value while ignoring a trailing unit annotation."""
    value = pds3_value(path, key).split(maxsplit=1)[0]
    return float(value)


def _reproject_array(
    source: np.ndarray,
    *,
    src_transform: Affine,
    src_crs: CRS,
    shape: tuple[int, int],
    dst_transform: Affine,
    dst_crs: CRS,
    src_nodata: float | None = None,
) -> np.ndarray:
    destination = np.full(shape, np.nan, dtype=np.float32)
    reproject(
        source=source,
        destination=destination,
        src_transform=src_transform,
        src_crs=src_crs,
        src_nodata=src_nodata,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        dst_nodata=np.nan,
        resampling=Resampling.average,
        init_dest_nodata=True,
        num_threads=2,
        warp_mem_limit=256,
    )
    return destination


def _reproject_raster(
    path: Path,
    *,
    shape: tuple[int, int],
    dst_transform: Affine,
    dst_crs: CRS,
    expected_crs: CRS | None = None,
    expected_transform: Affine | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    with rasterio.open(path) as source:
        if source.count != 1:
            raise ValueError(f"{path.name}: expected one raster band")
        if expected_crs is not None and source.crs != expected_crs:
            raise ValueError(f"{path.name}: CRS differs from the selected LOLA DEM")
        if expected_transform is not None and source.transform != expected_transform:
            raise ValueError(f"{path.name}: pixel grid differs from the selected LOLA DEM")
        destination = np.full(shape, np.nan, dtype=np.float32)
        reproject(
            source=rasterio.band(source, 1),
            destination=destination,
            src_transform=source.transform,
            src_crs=source.crs,
            src_nodata=source.nodata,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=np.nan,
            resampling=Resampling.average,
            init_dest_nodata=True,
            num_threads=2,
            warp_mem_limit=256,
        )
        metadata = {
            "width": source.width,
            "height": source.height,
            "dtype": source.dtypes[0],
            "crs_wkt": source.crs.to_wkt(),
            "transform": [float(value) for value in source.transform[:6]],
            "nodata": "NaN" if isinstance(source.nodata, float) and math.isnan(source.nodata) else source.nodata,
            "overview_factors": source.overviews(1),
            "band_tags": source.tags(1),
        }
    return destination, metadata


def _profile_grid(
    z: np.ndarray,
    source_valid: np.ndarray,
    region_mask: np.ndarray,
    scale_factor: np.ndarray,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    rows, cols = z.shape
    slope = np.full(z.shape, np.nan, dtype=np.float32)
    cell_ground_m = GRID_M / scale_factor
    if rows >= 3 and cols >= 3:
        local_valid = (
            source_valid[1:-1, 1:-1]
            & source_valid[1:-1, :-2]
            & source_valid[1:-1, 2:]
            & source_valid[:-2, 1:-1]
            & source_valid[2:, 1:-1]
        )
        dz_dx = (z[1:-1, 2:] - z[1:-1, :-2]) / (2.0 * cell_ground_m[1:-1, 1:-1])
        dz_dy = (z[:-2, 1:-1] - z[2:, 1:-1]) / (2.0 * cell_ground_m[1:-1, 1:-1])
        slope_inner = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))
        slope[1:-1, 1:-1] = np.where(local_valid, slope_inner, np.nan)

    max_scale = float(np.nanmax(scale_factor))
    half_window_cells = int(math.ceil(WINDOW_RADIUS_M * max_scale / GRID_M))
    offsets = np.arange(-half_window_cells, half_window_cells + 1, dtype=np.float64) * GRID_M
    yy, xx = np.meshgrid(-offsets, offsets, indexing="ij")
    dx_map = xx.ravel()
    dy_map = yy.ravel()
    squared_distance_map = dx_map * dx_map + dy_map * dy_map
    window_shape = (2 * half_window_cells + 1, 2 * half_window_cells + 1)
    pad = half_window_cells
    z_pad = np.pad(z.astype(np.float32, copy=False), pad, constant_values=np.nan)
    valid_pad = np.pad(source_valid.astype(bool, copy=False), pad, constant_values=False)
    windows_z = sliding_window_view(z_pad, window_shape)
    windows_valid = sliding_window_view(valid_pad, window_shape)
    flat_z = windows_z.reshape(rows, cols, -1)
    flat_valid = windows_valid.reshape(rows, cols, -1)

    window_valid_fraction = np.full(z.shape, np.nan, dtype=np.float32)
    roughness = np.full(z.shape, np.nan, dtype=np.float32)
    relief = np.full(z.shape, np.nan, dtype=np.float32)
    chunk_rows = 16

    for row_start in range(0, rows, chunk_rows):
        row_end = min(rows, row_start + chunk_rows)
        center_scale = scale_factor[row_start:row_end].reshape(-1).astype(np.float64)
        center_radius_map = WINDOW_RADIUS_M * center_scale
        in_physical_radius = squared_distance_map[None, :] <= center_radius_map[:, None] ** 2
        source_mask = flat_valid[row_start:row_end].reshape(-1, flat_valid.shape[-1])
        values = flat_z[row_start:row_end].reshape(-1, flat_z.shape[-1]).astype(np.float64)
        use_mask = source_mask & in_physical_radius
        expected_counts = in_physical_radius.sum(axis=1)
        actual_counts = use_mask.sum(axis=1)
        fractions = actual_counts / np.maximum(expected_counts, 1)
        window_valid_fraction[row_start:row_end] = fractions.reshape(row_end - row_start, cols)
        good = (
            (fractions >= MIN_WINDOW_VALID_FRACTION)
            & region_mask[row_start:row_end].reshape(-1)
        )
        if not np.any(good):
            continue

        good_values = values[good]
        good_mask = use_mask[good]
        good_dx = dx_map[None, :] / center_scale[good, None]
        good_dy = dy_map[None, :] / center_scale[good, None]
        weights = good_mask.astype(np.float64)
        valid_values = np.where(good_mask, good_values, 0.0)

        sxx = np.sum(weights * good_dx * good_dx, axis=1)
        syy = np.sum(weights * good_dy * good_dy, axis=1)
        sxy = np.sum(weights * good_dx * good_dy, axis=1)
        sx = np.sum(weights * good_dx, axis=1)
        sy = np.sum(weights * good_dy, axis=1)
        sz = np.sum(valid_values, axis=1)
        sxz = np.sum(valid_values * good_dx, axis=1)
        syz = np.sum(valid_values * good_dy, axis=1)
        n = good_mask.sum(axis=1).astype(np.float64)

        normal = np.zeros((good.sum(), 3, 3), dtype=np.float64)
        normal[:, 0, 0], normal[:, 1, 1], normal[:, 0, 1] = sxx, syy, sxy
        normal[:, 1, 0] = sxy
        normal[:, 0, 2] = normal[:, 2, 0] = sx
        normal[:, 1, 2] = normal[:, 2, 1] = sy
        normal[:, 2, 2] = n
        rhs = np.column_stack((sxz, syz, sz))
        coefficients = np.linalg.solve(normal, rhs[..., None])[..., 0]
        residual = valid_values - (
            coefficients[:, 0, None] * good_dx
            + coefficients[:, 1, None] * good_dy
            + coefficients[:, 2, None]
        )
        roughness_values = np.sqrt(np.sum(weights * residual * residual, axis=1) / n)
        roughness_flat = roughness[row_start:row_end].reshape(-1)
        relief_flat = relief[row_start:row_end].reshape(-1)
        selected_indices = np.flatnonzero(good)
        roughness_flat[selected_indices] = roughness_values.astype(np.float32)

        q05 = np.empty(good.sum(), dtype=np.float64)
        q95 = np.empty(good.sum(), dtype=np.float64)
        for index, mask in enumerate(good_mask):
            samples = good_values[index, mask]
            q05[index], q95[index] = np.percentile(samples, [5, 95])
        relief_flat[selected_indices] = (q95 - q05).astype(np.float32)

    roughness[~region_mask] = np.nan
    relief[~region_mask] = np.nan
    slope[~region_mask] = np.nan
    feature_grids = {
        "slope_deg": slope,
        "roughness_m": roughness,
        "relief_m": relief,
    }
    return feature_grids, window_valid_fraction


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantiles: list[float]) -> list[float]:
    keep = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    values = values[keep].astype(np.float64)
    weights = weights[keep].astype(np.float64)
    if values.size == 0:
        raise ValueError("Cannot summarize an empty profile feature")
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    sorted_weights = weights[order]
    midpoints = (np.cumsum(sorted_weights) - 0.5 * sorted_weights) / np.sum(sorted_weights)
    return [float(np.interp(q, midpoints, sorted_values)) for q in quantiles]


def _feature_statistics(
    feature_grids: dict[str, np.ndarray],
    region_mask: np.ndarray,
    pixel_area_weights: np.ndarray,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    core_count = int(np.count_nonzero(region_mask))
    for feature_id, _, unit in FEATURES:
        grid = feature_grids[feature_id]
        values = grid[region_mask]
        weights = pixel_area_weights[region_mask]
        finite = np.isfinite(values)
        quantiles = _weighted_quantile(values[finite], weights[finite], [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95])
        q05, q10, q25, q50, q75, q90, q95 = quantiles
        tolerance = (q75 - q25) * TOLERANCE_IQR_MULTIPLIER
        if not math.isfinite(tolerance) or tolerance <= 0:
            raise ValueError(f"{feature_id}: empirical IQR is zero; a positive tolerance cannot be justified")
        result[feature_id] = {
            "unit": unit,
            "reference_interval": [q10, q90],
            "tolerance": tolerance,
            "weighted_quantiles": {
                "p05": q05,
                "p10": q10,
                "p25": q25,
                "p50": q50,
                "p75": q75,
                "p90": q90,
                "p95": q95,
            },
            "interquartile_range": q75 - q25,
            "valid_cell_count": int(np.count_nonzero(finite)),
            "valid_cell_fraction": float(np.count_nonzero(finite) / core_count) if core_count else 0.0,
        }
    all_valid = region_mask.copy()
    for _, feature_grid in feature_grids.items():
        all_valid &= np.isfinite(feature_grid)
    result["joint_coverage"] = {
        "region_candidate_cell_count": core_count,
        "all_three_features_valid_cell_count": int(np.count_nonzero(all_valid)),
        "all_three_features_valid_cell_fraction": float(np.count_nonzero(all_valid) / core_count) if core_count else 0.0,
    }
    return result


def _manual_feature_reproduction(
    z: np.ndarray,
    source_valid: np.ndarray,
    region_mask: np.ndarray,
    feature_grids: dict[str, np.ndarray],
    scale_factor: np.ndarray,
) -> dict[str, Any]:
    joint = region_mask.copy()
    for grid in feature_grids.values():
        joint &= np.isfinite(grid)
    candidates = np.argwhere(joint)
    if candidates.size == 0:
        raise ValueError("No profile cell has all three P0 features for a manual reproduction")
    rows, cols = z.shape
    yy, xx = np.indices(z.shape, dtype=np.float64)
    x_centers = (xx + 0.5) * GRID_M - (cols * GRID_M / 2)
    y_centers = (rows * GRID_M / 2) - (yy + 0.5) * GRID_M
    center_distances = (x_centers[candidates[:, 0], candidates[:, 1]] ** 2 + y_centers[candidates[:, 0], candidates[:, 1]] ** 2)
    row, col = (int(value) for value in candidates[int(np.argmin(center_distances))])
    k = float(scale_factor[row, col])
    physical_cell = GRID_M / k
    dz_dx = float((z[row, col + 1] - z[row, col - 1]) / (2 * physical_cell))
    dz_dy = float((z[row - 1, col] - z[row + 1, col]) / (2 * physical_cell))
    slope = math.degrees(math.atan(math.hypot(dz_dx, dz_dy)))

    radius_cells = int(math.ceil(WINDOW_RADIUS_M * float(np.nanmax(scale_factor)) / GRID_M))
    row_slice = slice(row - radius_cells, row + radius_cells + 1)
    col_slice = slice(col - radius_cells, col + radius_cells + 1)
    offsets = np.arange(-radius_cells, radius_cells + 1, dtype=np.float64) * GRID_M
    dx, dy = np.meshgrid(offsets, -offsets, indexing="xy")
    physical_radius = np.hypot(dx, dy) / k
    local_z = z[row_slice, col_slice]
    local_valid = source_valid[row_slice, col_slice] & (physical_radius <= WINDOW_RADIUS_M)
    values = local_z[local_valid].astype(np.float64)
    x = (dx / k)[local_valid]
    y = (dy / k)[local_valid]
    coefficients = np.linalg.lstsq(np.column_stack((x, y, np.ones_like(x))), values, rcond=None)[0]
    residual = values - (coefficients[0] * x + coefficients[1] * y + coefficients[2])
    roughness = float(np.sqrt(np.mean(residual * residual)))
    relief = float(np.percentile(values, 95) - np.percentile(values, 5))
    comparisons = {
        "slope_deg": (slope, float(feature_grids["slope_deg"][row, col])),
        "roughness_m": (roughness, float(feature_grids["roughness_m"][row, col])),
        "relief_m": (relief, float(feature_grids["relief_m"][row, col])),
    }
    checked = {}
    for name, (manual, pipeline) in comparisons.items():
        checked[name] = {
            "manual_value": manual,
            "pipeline_value": pipeline,
            "absolute_difference": abs(manual - pipeline),
            "passed": math.isclose(manual, pipeline, rel_tol=1e-6, abs_tol=1e-6),
        }
        if not checked[name]["passed"]:
            raise ValueError(f"Manual reproduction mismatch for {name}: {checked[name]}")
    return {
        "grid_row": row,
        "grid_col": col,
        "projected_cell_center_m": [float(x_centers[row, col]), float(y_centers[row, col])],
        "window_radius_m": WINDOW_RADIUS_M,
        "valid_samples_in_window": int(values.size),
        "feature_reproduction": checked,
    }


def _body_coordinates_from_projected(
    *,
    x: float,
    y: float,
    projected_crs: CRS,
    geographic_crs: CRS,
) -> dict[str, float]:
    inverse = Transformer.from_crs(projected_crs, geographic_crs, always_xy=True)
    longitude, latitude = inverse.transform(x, y)
    longitude_east = float(longitude % 360.0)
    return {"longitude_east_0_360_deg": longitude_east, "latitude_planetocentric_deg": float(latitude)}


def _mars_source(raw_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    dem_path = raw_dir / "megt44n000hb.img"
    count_path = raw_dir / "megc44n000hb.img"
    dem_label = raw_dir / "megt44n000hb.lbl"
    count_label = raw_dir / "megc44n000hb.lbl"
    dem_xml = raw_dir / "megt44n000hb.xml"
    count_xml = raw_dir / "megc44n000hb.xml"

    expected_dem_size = MOLA_ROWS * MOLA_COLS * 2
    expected_count_size = MOLA_ROWS * MOLA_COLS
    if dem_path.stat().st_size != expected_dem_size or count_path.stat().st_size != expected_count_size:
        raise ValueError("MOLA 128 ppd tile has an unexpected byte size")
    if pds3_value(dem_label, "SAMPLE_TYPE") != "MSB_INTEGER" or pds3_value(dem_label, "SAMPLE_BITS") != "16":
        raise ValueError("MOLA topography label does not match signed MSB 16-bit values")
    if pds3_value(dem_label, "UNIT") != "METER":
        raise ValueError("MOLA topography label does not declare metre values")
    if pds3_value(count_label, "SAMPLE_TYPE") != "UNSIGNED_INTEGER" or pds3_value(count_label, "SAMPLE_BITS") != "8":
        raise ValueError("MOLA count label does not match unsigned byte values")
    if pds3_value(count_label, "PRODUCT_VERSION_ID") != pds3_value(dem_label, "PRODUCT_VERSION_ID"):
        raise ValueError("MOLA topography and count labels declare different product versions")
    if pds3_value(count_label, "POSITIVE_LONGITUDE_DIRECTION") != pds3_value(dem_label, "POSITIVE_LONGITUDE_DIRECTION"):
        raise ValueError("MOLA topography and count longitude directions differ")
    if pds3_value(count_label, "COORDINATE_SYSTEM_NAME") != pds3_value(dem_label, "COORDINATE_SYSTEM_NAME"):
        raise ValueError("MOLA topography and count coordinate frames differ")
    for key in ("LINES", "LINE_SAMPLES"):
        if pds3_value(count_label, key) != pds3_value(dem_label, key):
            raise ValueError(f"MOLA topography and count dimensions differ at {key}")
    for key in ("MAP_RESOLUTION", "CENTER_LONGITUDE", "CENTER_LATITUDE", "MAXIMUM_LATITUDE", "MINIMUM_LATITUDE", "WESTERNMOST_LONGITUDE", "EASTERNMOST_LONGITUDE"):
        if not math.isclose(pds3_number(count_label, key), pds3_number(dem_label, key), abs_tol=1e-9):
            raise ValueError(f"MOLA topography and count map labels differ at {key}")
    if pds3_value(dem_label, "POSITIVE_LONGITUDE_DIRECTION") != "EAST":
        raise ValueError("MOLA source does not declare east-positive longitude")
    if pds3_value(dem_label, "COORDINATE_SYSTEM_NAME") != "PLANETOCENTRIC":
        raise ValueError("MOLA source coordinate frame is not planetocentric")
    if pds3_number(dem_label, "MAP_RESOLUTION") != MOLA_PPD:
        raise ValueError("MOLA source resolution differs from the selected 128 ppd tile")
    if pds3_value(dem_label, "PRODUCT_VERSION_ID") != "2.0":
        raise ValueError("MOLA source is not the final product version 2.0")
    for key in ("START_TIME", "STOP_TIME"):
        if pds3_value(count_label, key) != pds3_value(dem_label, key):
            raise ValueError(f"MOLA topography and count time coverage differs at {key}")
    if not math.isclose(float(xml_value(dem_xml, "pixel_resolution_x")) * 1000.0, MOLA_PX_M, abs_tol=1e-9):
        raise ValueError("MOLA source PDS4 map scale changed")
    x_ul = float(xml_value(dem_xml, "upperleft_corner_x"))
    y_ul = float(xml_value(dem_xml, "upperleft_corner_y"))
    if not math.isclose(x_ul, MOLA_UL_X_M, abs_tol=0.001) or not math.isclose(y_ul, MOLA_UL_Y_M, abs_tol=0.001):
        raise ValueError("MOLA source PDS4 upper-left map coordinate changed")
    count_resolution = float(xml_value(count_xml, "pixel_resolution_x")) * 1000.0
    count_x_ul = float(xml_value(count_xml, "upperleft_corner_x"))
    count_y_ul = float(xml_value(count_xml, "upperleft_corner_y"))
    if not math.isclose(count_resolution, MOLA_PX_M, abs_tol=1e-9):
        raise ValueError("MOLA count PDS4 map scale differs from the topography map")
    if not math.isclose(count_x_ul, x_ul, abs_tol=0.001) or not math.isclose(count_y_ul, y_ul, abs_tol=0.001):
        raise ValueError("MOLA count PDS4 upper-left map coordinate differs from topography")
    if xml_value(count_xml, "version_id") != xml_value(dem_xml, "version_id"):
        raise ValueError("MOLA topography and count PDS4 labels have different label versions")

    metadata = {
        "dem_path": dem_path,
        "count_path": count_path,
        "dem_label": dem_label,
        "count_label": count_label,
        "dem_xml": dem_xml,
        "count_xml": count_xml,
        "rows": MOLA_ROWS,
        "cols": MOLA_COLS,
        "pixel_size_m_at_equator": MOLA_PX_M,
        "x_ul_m": x_ul,
        "y_ul_m": y_ul,
    }
    longitude_check = {
        "source_positive_longitude_direction": pds3_value(dem_label, "POSITIVE_LONGITUDE_DIRECTION"),
        "source_longitude_bounds_deg": [
            pds3_number(dem_label, "WESTERNMOST_LONGITUDE"),
            pds3_number(dem_label, "EASTERNMOST_LONGITUDE"),
        ],
        "source_center_longitude_deg": pds3_number(dem_label, "CENTER_LONGITUDE"),
        "coordinate_system": pds3_value(dem_label, "COORDINATE_SYSTEM_NAME"),
        "pds4_label_version": xml_value(dem_xml, "version_id"),
        "pds4_map_scale_m_per_pixel": MOLA_PX_M,
        "topography_description": xml_value(dem_xml, "description"),
    }
    return metadata, longitude_check


def _mars_source_quality(
    raw_dir: Path,
    *,
    output_transform: Affine,
    output_crs: CRS,
    output_shape: tuple[int, int],
    core_mask: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any], dict[str, Any]]:
    source, longitude_check = _mars_source(raw_dir)
    geod = Geod(a=MARS_RADIUS_M, b=MARS_RADIUS_M)
    halo_extent = MARS_RADIUS_REGION_M + WINDOW_RADIUS_M
    bearings = np.array([0.0, 90.0, 180.0, 270.0])
    lons, lats, _ = geod.fwd(
        np.full(4, MARS_CENTER_LON),
        np.full(4, MARS_CENTER_LAT),
        bearings,
        np.full(4, halo_extent),
    )
    lon_min, lon_max = float(np.min(lons)), float(np.max(lons))
    lat_min, lat_max = float(np.min(lats)), float(np.max(lats))
    col0 = max(0, int(math.floor(lon_min * MOLA_PPD)))
    col1 = min(MOLA_COLS, int(math.ceil(lon_max * MOLA_PPD)))
    row0 = max(0, int(math.floor((44.0 - lat_max) * MOLA_PPD)))
    row1 = min(MOLA_ROWS, int(math.ceil((44.0 - lat_min) * MOLA_PPD)))
    if col1 <= col0 or row1 <= row0:
        raise ValueError("The Jezero region does not intersect the selected MOLA tile")

    dem_map = np.memmap(source["dem_path"], mode="r", dtype=">i2", shape=(MOLA_ROWS, MOLA_COLS))
    count_map = np.memmap(source["count_path"], mode="r", dtype=np.uint8, shape=(MOLA_ROWS, MOLA_COLS))
    dem_window = np.asarray(dem_map[row0:row1, col0:col1], dtype=np.float32)
    count_window = np.asarray(count_map[row0:row1, col0:col1])
    pixel_m = MOLA_PX_M
    source_transform = Affine(
        pixel_m,
        0.0,
        source["x_ul_m"] + col0 * pixel_m,
        0.0,
        -pixel_m,
        source["y_ul_m"] - row0 * pixel_m,
    )
    source_crs = CRS.from_proj4(
        f"+proj=eqc +lat_ts=0 +lon_0=180 +R={MARS_RADIUS_M} +units=m +no_defs +type=crs"
    )
    mars_geo = CRS.from_proj4(f"+proj=longlat +R={MARS_RADIUS_M} +no_defs +type=crs")
    destination_dem = _reproject_array(
        dem_window,
        src_transform=source_transform,
        src_crs=source_crs,
        shape=output_shape,
        dst_transform=output_transform,
        dst_crs=output_crs,
    )
    direct_bins = (count_window > 0).astype(np.float32)
    direct_fraction = _reproject_array(
        direct_bins,
        src_transform=source_transform,
        src_crs=source_crs,
        shape=output_shape,
        dst_transform=output_transform,
        dst_crs=output_crs,
    )
    mean_count = _reproject_array(
        count_window.astype(np.float32),
        src_transform=source_transform,
        src_crs=source_crs,
        shape=output_shape,
        dst_transform=output_transform,
        dst_crs=output_crs,
    )
    direct_fraction = np.clip(direct_fraction, 0.0, 1.0)
    sample_x, sample_y = Transformer.from_crs(mars_geo, source_crs, always_xy=True).transform(
        MARS_CENTER_LON, MARS_CENTER_LAT
    )
    sample_col = int(math.floor((sample_x - source["x_ul_m"]) / pixel_m))
    sample_row = int(math.floor((source["y_ul_m"] - sample_y) / pixel_m))
    sample_dem = int(dem_map[sample_row, sample_col])
    sample_count = int(count_map[sample_row, sample_col])
    sample_center_x = source["x_ul_m"] + (sample_col + 0.5) * pixel_m
    sample_center_y = source["y_ul_m"] - (sample_row + 0.5) * pixel_m
    sample_lon, sample_lat = Transformer.from_crs(source_crs, mars_geo, always_xy=True).transform(
        sample_center_x, sample_center_y
    )
    quality = {
        "mola_source_pixel_count": int((row1 - row0) * (col1 - col0)),
        "mola_source_row_range_zero_based_half_open": [row0, row1],
        "mola_source_col_range_zero_based_half_open": [col0, col1],
        "direct_observation_bin_fraction_in_profile_region": float(np.nanmean(direct_fraction[core_mask])),
        "profile_cells_with_at_least_one_direct_source_bin_fraction": float(
            np.mean(direct_fraction[core_mask] > 0.0)
        ),
        "profile_cells_with_count_data_fraction": float(np.mean(np.isfinite(mean_count[core_mask]))),
        "mean_source_observations_per_463m_bin_in_profile_region": float(np.nanmean(mean_count[core_mask])),
        "quality_interpretation": (
            "MEGT supplies interpolated topography in source bins with MEGC count 0. The gridded surface values are used; "
            "direct-observation support is retained separately and is not represented as complete area coverage."
        ),
        "manual_source_pixel": {
            "row_zero_based": sample_row,
            "column_zero_based": sample_col,
            "source_center_longitude_east_0_360_deg": float(sample_lon % 360.0),
            "source_center_latitude_planetocentric_deg": float(sample_lat),
            "topography_m_relative_to_mola_gmm3_areoid": sample_dem,
            "direct_observation_count_uint8": sample_count,
            "is_directly_observed_bin": sample_count > 0,
        },
    }
    mars_geo_to_aeqd = Transformer.from_crs(mars_geo, output_crs, always_xy=True)
    aeqd_to_mars_geo = Transformer.from_crs(output_crs, mars_geo, always_xy=True)
    check_x, check_y = mars_geo_to_aeqd.transform(MARS_CENTER_LON, MARS_CENTER_LAT)
    check_lon, check_lat = aeqd_to_mars_geo.transform(check_x, check_y)
    longitude_check.update(
        {
            "round_trip_input_lon_east_deg": MARS_CENTER_LON,
            "round_trip_input_lat_planetocentric_deg": MARS_CENTER_LAT,
            "round_trip_lon_east_0_360_deg": float(check_lon % 360.0),
            "round_trip_lat_planetocentric_deg": float(check_lat),
            "round_trip_passed": math.isclose(check_lon % 360.0, MARS_CENTER_LON, abs_tol=1e-8)
            and math.isclose(check_lat, MARS_CENTER_LAT, abs_tol=1e-8),
            "profile_center_source_pixel": quality["manual_source_pixel"],
        }
    )
    if not longitude_check["round_trip_passed"]:
        raise ValueError("MOLA east-positive longitude round-trip failed")
    return destination_dem, quality, longitude_check


def _moon_source(raw_dir: Path, output_shape: tuple[int, int], output_transform: Affine) -> tuple[dict[str, np.ndarray], dict[str, Any], dict[str, Any]]:
    dem_path = raw_dir / "LDEM_80S_80MPP_ADJ.TIF"
    count_path = raw_dir / "LDEC_80S_80MPP_ADJ.TIF"
    effres_path = raw_dir / "LDEM_80S_80MPP_ADJ_EFFRES.TIF"
    error_path = raw_dir / "LDEM_80S_80MPP_ADJ_ERR.TIF"
    dem_label = raw_dir / "ldem_80s_80m.lbl"
    count_label = raw_dir / "ldec_80s_80m.lbl"
    for label in (dem_label, count_label):
        if pds3_value(label, "POSITIVE_LONGITUDE_DIRECTION") != "EAST":
            raise ValueError(f"{label.name}: source longitude direction is not east-positive")
        if pds3_value(label, "COORDINATE_SYSTEM_NAME") != "MEAN EARTH/POLAR AXIS OF DE421":
            raise ValueError(f"{label.name}: source coordinate frame is not MOON_ME/DE421")
        if pds3_value(label, "MAP_PROJECTION_TYPE") != "POLAR STEREOGRAPHIC":
            raise ValueError(f"{label.name}: expected a south polar stereographic source")
        for key, expected in (("A_AXIS_RADIUS", 1737.4), ("B_AXIS_RADIUS", 1737.4), ("C_AXIS_RADIUS", 1737.4), ("MAP_SCALE", 80.0), ("CENTER_LATITUDE", -90.0), ("CENTER_LONGITUDE", 0.0), ("MINIMUM_LATITUDE", -90.0), ("MAXIMUM_LATITUDE", -80.0)):
            if not math.isclose(pds3_number(label, key), expected, abs_tol=1e-9):
                raise ValueError(f"{label.name}: unexpected {key} value")
    for key in ("START_TIME", "STOP_TIME"):
        if pds3_value(count_label, key) != pds3_value(dem_label, key):
            raise ValueError(f"LOLA DEM and count reference labels differ at {key}")
    with rasterio.open(dem_path) as dem_source:
        if dem_source.width != 7600 or dem_source.height != 7600 or dem_source.res != (80.0, 80.0):
            raise ValueError("LOLA PGDA DEM is not the selected 7600 x 7600, 80 m posting product")
        if dem_source.transform != Affine(80.0, 0.0, -304_000.0, 0.0, -80.0, 304_000.0):
            raise ValueError("LOLA PGDA DEM polar grid transform changed")
        dem_crs = dem_source.crs
        dem_transform = dem_source.transform
        dem_shape = (dem_source.height, dem_source.width)
        dem, dem_meta = _reproject_raster(
            dem_path,
            shape=output_shape,
            dst_transform=output_transform,
            dst_crs=dem_crs,
            expected_crs=dem_crs,
            expected_transform=dem_transform,
        )
    ldec, ldec_meta = _reproject_raster(
        count_path,
        shape=output_shape,
        dst_transform=output_transform,
        dst_crs=dem_crs,
        expected_crs=dem_crs,
        expected_transform=dem_transform,
    )
    effres, effres_meta = _reproject_raster(
        effres_path,
        shape=output_shape,
        dst_transform=output_transform,
        dst_crs=dem_crs,
        expected_crs=dem_crs,
        expected_transform=dem_transform,
    )
    error, error_meta = _reproject_raster(
        error_path,
        shape=output_shape,
        dst_transform=output_transform,
        dst_crs=dem_crs,
        expected_crs=dem_crs,
        expected_transform=dem_transform,
    )
    northing, easting = np.indices(output_shape, dtype=np.float64)
    x_centers = output_transform.c + (easting + 0.5) * output_transform.a
    y_centers = output_transform.f + (northing + 0.5) * output_transform.e
    rho = np.hypot(x_centers, y_centers)
    cap_radius_map_m = 2.0 * MOON_RADIUS_M * math.tan(math.radians(90.0 + MOON_CAP_LAT_DEG) / 2.0)
    region_mask = rho <= cap_radius_map_m
    scale_factor = 1.0 + (rho / (2.0 * MOON_RADIUS_M)) ** 2
    # The polar stereographic DEM is a shape map relative to the 1,737,400 m sphere.
    valid = np.isfinite(dem) & np.isfinite(effres) & (effres <= 2_000.0)
    raw_count_sample: dict[str, Any] = {}
    manual_row = output_shape[0] // 2 - 1
    manual_col = output_shape[1] // 2 - 1
    sample_x = output_transform.c + (manual_col + 0.5) * output_transform.a
    sample_y = output_transform.f + (manual_row + 0.5) * output_transform.e
    with rasterio.open(dem_path) as src_dem, rasterio.open(count_path) as src_count, rasterio.open(
        effres_path
    ) as src_effres, rasterio.open(error_path) as src_error:
        src_row, src_col = src_dem.index(sample_x, sample_y)
        for label, dataset in (
            ("height_m_relative_to_1737400m_sphere", src_dem),
            ("lola_return_count_per_80m_pixel", src_count),
            ("effective_resolution_m", src_effres),
            ("height_error_m", src_error),
        ):
            raw_count_sample[label] = float(dataset.read(1, window=((src_row, src_row + 1), (src_col, src_col + 1)))[0, 0])
        raw_count_sample.update({"source_row_zero_based": src_row, "source_col_zero_based": src_col})
    geographic_crs = CRS.from_proj4(f"+proj=longlat +R={MOON_RADIUS_M} +no_defs +type=crs")
    source_roundtrip = Transformer.from_crs(geographic_crs, dem_crs, always_xy=True)
    source_inverse = Transformer.from_crs(dem_crs, geographic_crs, always_xy=True)
    test_x, test_y = source_roundtrip.transform(45.0, -85.0)
    test_lon, test_lat = source_inverse.transform(test_x, test_y)
    longitude_check = {
        "source_positive_longitude_direction_from_PDS_label": pds3_value(dem_label, "POSITIVE_LONGITUDE_DIRECTION"),
        "source_longitude_projection_center_deg": pds3_number(dem_label, "CENTER_LONGITUDE"),
        "source_coordinate_system": pds3_value(dem_label, "COORDINATE_SYSTEM_NAME"),
        "PGDA_projection_wkt": dem_meta["crs_wkt"],
        "round_trip_input_lon_east_deg": 45.0,
        "round_trip_input_lat_planetocentric_deg": -85.0,
        "projected_xy_m": [float(test_x), float(test_y)],
        "round_trip_lon_east_0_360_deg": float(test_lon % 360.0),
        "round_trip_lat_planetocentric_deg": float(test_lat),
        "round_trip_passed": math.isclose(test_lon % 360.0, 45.0, abs_tol=1e-8)
        and math.isclose(test_lat, -85.0, abs_tol=1e-8),
    }
    if longitude_check["source_positive_longitude_direction_from_PDS_label"] != "EAST" or not longitude_check["round_trip_passed"]:
        raise ValueError("LOLA east-positive longitude round-trip failed")
    source_meta = {
        "dem": dem_meta,
        "counts": ldec_meta,
        "effective_resolution": effres_meta,
        "height_error": error_meta,
        "source_rows_cols": [dem_shape[0], dem_shape[1]],
        "cap_radius_in_stereographic_m": cap_radius_map_m,
        "source_resolution_m": 80.0,
        "reference_radius_m": MOON_RADIUS_M,
    }
    quality = {
        "native_source_height_posting_m": 80.0,
        "effective_resolution_limit_m": 2_000.0,
        "profile_cells_with_valid_height_and_effective_resolution_fraction": float(
            np.mean(valid[region_mask])
        ),
        "profile_cells_without_LOLA_returns_fraction": float(np.mean(ldec[region_mask] <= 0.0)),
        "mean_LOLA_returns_per_native_80m_pixel": float(np.nanmean(ldec[region_mask])),
        "effective_resolution_m_p50": float(np.nanmedian(effres[region_mask])),
        "effective_resolution_m_p95": float(np.nanpercentile(effres[region_mask], 95)),
        "height_error_m_p50": float(np.nanmedian(error[region_mask])),
        "height_error_m_p95": float(np.nanpercentile(error[region_mask], 95)),
        "quality_interpretation": (
            "LDEC is a return-count layer, not area coverage. LDEM posting is 80 m; the official effective-resolution "
            "and error rasters are retained. Analysis cells are excluded only when their averaged effective resolution "
            "exceeds the declared 2 km analysis scale or source values are nodata."
        ),
        "manual_source_pixel": raw_count_sample,
    }
    return (
        {"dem": dem, "counts_mean": ldec, "effective_resolution": effres, "height_error": error, "valid": valid, "region_mask": region_mask, "scale_factor": scale_factor},
        source_meta,
        {"quality": quality, "longitude_check": longitude_check},
    )


def _projected_circle_geometry(radius_m: float, resolution_deg: int = 360) -> list[list[list[float]]]:
    angles = np.arange(resolution_deg, dtype=np.float64) * (2.0 * math.pi / resolution_deg)
    ring = [[float(radius_m * math.cos(a)), float(radius_m * math.sin(a))] for a in angles]
    ring.append(ring[0])
    return [ring]


def _cell_area_weights(scale_factor: np.ndarray) -> np.ndarray:
    return (GRID_M * GRID_M) / (scale_factor * scale_factor)


def _profile_feature_objects(
    stats: dict[str, dict[str, Any]],
    *,
    source_ids: list[str],
    source_resolution_m: float,
    projection_description: str,
    profile_limitations: list[str],
) -> list[dict[str, Any]]:
    features = []
    for feature_id, display_name, unit in FEATURES:
        data = stats[feature_id]
        interval = [round(v, 6) for v in data["reference_interval"]]
        tolerance = round(data["tolerance"], 6)
        features.append(
            {
                "feature_id": feature_id,
                "name": display_name,
                "description": {
                    "slope_deg": "Slope angle from central finite differences on the common 2 km physical analysis grid.",
                    "roughness_m": "Standard deviation of residuals from a local least-squares plane inside a 10 km physical-radius window.",
                    "relief_m": "P95 minus P05 of the common-grid surface heights inside a 10 km physical-radius window.",
                }[feature_id],
                "unit": unit,
                "measurement_scale": "ratio",
                "reference_interval": interval,
                "tolerance": {
                    "value": tolerance,
                    "unit": unit,
                    "basis": "assumption",
                    "rationale": (
                        "Predeclared result-blind rule: the target interval is its area-weighted P10–P90 distribution; "
                        "the external tolerance is 1.5 times that same measured profile's IQR (P75–P25). This is an "
                        "experimental screening margin, not instrument uncertainty or a NASA threshold; K-009 must test sensitivity."
                    ),
                    "source_ids": source_ids,
                },
                "spatial_support": {
                    "source_resolution_m": source_resolution_m,
                    "analysis_cell_resolution_m": GRID_M,
                    "window_radius_m": WINDOW_RADIUS_M,
                    "description": projection_description,
                    "missing_reason": None,
                },
                "is_proxy": False,
                "proxy_description": None,
                "source_ids": source_ids,
                "limitations": profile_limitations,
            }
        )
    return features


def _file_records(raw_dir: Path) -> list[dict[str, Any]]:
    file_sources = {
        "megt44n000hb.img": (MARS_DEM_ID, "measurement", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megt44n000hb.img"),
        "megt44n000hb.xml": (MARS_DEM_ID, "pds4_label", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megt44n000hb.xml"),
        "megt44n000hb.lbl": (MARS_DEM_ID, "pds3_label", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megt44n000hb.lbl"),
        "megt44n000hb.hdr": (MARS_DEM_ID, "envi_label", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megt44n000hb.hdr"),
        "megc44n000hb.img": (MARS_COUNT_ID, "measurement", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megc44n000hb.img"),
        "megc44n000hb.xml": (MARS_COUNT_ID, "pds4_label", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megc44n000hb.xml"),
        "megc44n000hb.lbl": (MARS_COUNT_ID, "pds3_label", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megc44n000hb.lbl"),
        "megc44n000hb.hdr": (MARS_COUNT_ID, "envi_label", "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/megc44n000hb.hdr"),
        "LDEM_80S_80MPP_ADJ.TIF": (MOON_DEM_ID, "measurement", "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_80MPP_ADJ.TIF"),
        "LDEC_80S_80MPP_ADJ.TIF": (MOON_COUNT_ID, "measurement", "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEC_80S_80MPP_ADJ.TIF"),
        "LDEM_80S_80MPP_ADJ_EFFRES.TIF": (MOON_EFFRES_ID, "quality", "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_80MPP_ADJ_EFFRES.TIF"),
        "LDEM_80S_80MPP_ADJ_ERR.TIF": (MOON_ERROR_ID, "quality", "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_80MPP_ADJ_ERR.TIF"),
        "ldem_80s_80m.lbl": (MOON_DEM_ID, "coordinate_metadata", "https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/ldem_80s_80m.lbl"),
        "ldec_80s_80m.lbl": (MOON_COUNT_ID, "coordinate_metadata", "https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/ldec_80s_80m.lbl"),
    }
    records = []
    for filename, (dataset_id, role, url) in file_sources.items():
        path = raw_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing K-004 source file: {path}")
        records.append(
            {
                "dataset_id": dataset_id,
                "filename": filename,
                "url": url,
                "role": role,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return records


def _verify_source_lock(raw_dir: Path, source_manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source_lock = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source_lock.get("manifest_version") != 1 or source_lock.get("task_id") != "K-004":
        raise ValueError(f"Unsupported K-004 source manifest: {source_manifest_path}")
    expected_files = source_lock.get("files")
    if not isinstance(expected_files, list) or not expected_files:
        raise ValueError("K-004 source manifest must contain pinned files")
    actual_records = _file_records(raw_dir)
    expected_by_name = {record.get("filename"): record for record in expected_files}
    actual_by_name = {record["filename"]: record for record in actual_records}
    if None in expected_by_name or len(expected_by_name) != len(expected_files):
        raise ValueError("K-004 source manifest contains an empty or duplicate filename")
    if expected_by_name.keys() != actual_by_name.keys():
        raise ValueError("K-004 source manifest file inventory differs from the profile builder")
    for filename, expected in expected_by_name.items():
        actual = actual_by_name[filename]
        for key in ("dataset_id", "url", "role", "size_bytes", "sha256"):
            if expected.get(key) != actual[key]:
                raise ValueError(
                    f"{filename}: pinned {key} differs from the downloaded file inventory; "
                    "restore the source file or review and update the source lock explicitly"
                )
    return source_lock, actual_records


def _source_catalog(file_records: list[dict[str, Any]], raw_dir: Path) -> list[dict[str, Any]]:
    ids = sorted({record["dataset_id"] for record in file_records})
    mola_label = raw_dir / "megt44n000hb.lbl"
    lola_label = raw_dir / "ldem_80s_80m.lbl"
    mola_period = {
        "start_utc": pds3_value(mola_label, "START_TIME"),
        "stop_utc": pds3_value(mola_label, "STOP_TIME"),
        "metadata_file": mola_label.name,
    }
    lola_reference_period = {
        "start_utc": pds3_value(lola_label, "START_TIME"),
        "stop_utc": pds3_value(lola_label, "STOP_TIME"),
        "metadata_file": lola_label.name,
        "note": "Observation interval copied from the associated LOLA PDS3 GDR label; the PGDA adjusted raster has no per-pixel timestamps.",
    }
    metadata = {
        MARS_DEM_ID: {
            "title": "MGS MOLA MEGDR map of Mars topography, 128 pixels/degree, 44N 0E tile",
            "provider": "NASA Planetary Data System Geosciences Node",
            "product_version": "2.0",
            "doi": "https://doi.org/10.17189/1z1b-kv84",
            "source_url": "https://pds-geosciences.wustl.edu/missions/mgs/megdr.html",
            "citation": "MGS MOLA Topography Derived Bundle, MEGT44N000HB; cite DOI 10.17189/1z1b-kv84.",
            "license": "PDS archived data are public domain; cite the PDS data set and product.",
            "license_evidence_url": "https://pds-geosciences.wustl.edu/faq.html",
            "temporal_coverage": mola_period,
            "spatial_coverage": {"minimum_latitude_deg": 0.0, "maximum_latitude_deg": 44.0, "westernmost_longitude_east_deg": 0.0, "easternmost_longitude_east_deg": 90.0},
            "horizontal_reference": "Planetocentric east-positive simple cylindrical map on the 3,396,000 m Mars sphere.",
            "measurement_units": "m relative to the MOLA GMM-3 areoid, degree/order 50.",
            "role": "Mars target topography; values are relative to the MOLA GMM-3 areoid and unobserved bins are interpolated by the product.",
        },
        MARS_COUNT_ID: {
            "title": "MGS MOLA MEGDR observation counts, 128 pixels/degree, 44N 0E tile",
            "provider": "NASA Planetary Data System Geosciences Node",
            "product_version": "2.0",
            "doi": "https://doi.org/10.17189/1z1b-kv84",
            "source_url": "https://pds-geosciences.wustl.edu/missions/mgs/megdr.html",
            "citation": "MGS MOLA Topography Derived Bundle, MEGC44N000HB; cite DOI 10.17189/1z1b-kv84.",
            "license": "PDS archived data are public domain; cite the PDS data set and product.",
            "license_evidence_url": "https://pds-geosciences.wustl.edu/faq.html",
            "temporal_coverage": mola_period,
            "spatial_coverage": {"minimum_latitude_deg": 0.0, "maximum_latitude_deg": 44.0, "westernmost_longitude_east_deg": 0.0, "easternmost_longitude_east_deg": 90.0},
            "horizontal_reference": "Planetocentric east-positive simple cylindrical map on the 3,396,000 m Mars sphere.",
            "measurement_units": "Unsigned count of direct observations per 1/128 degree bin.",
            "role": "Quality layer identifying direct MOLA observation counts in each 1/128 degree bin.",
        },
        MOON_DEM_ID: {
            "title": "LOLA-adjusted DEM of the lunar south polar region, 80S, 80 m/pixel",
            "provider": "NASA Goddard Space Flight Center Planetary Geodesy Data Archive",
            "product_version": "PGDA Product 90; file LDEM_80S_80MPP_ADJ.TIF (published 2023)",
            "doi": "https://doi.org/10.60903/gsfcpgda-lola-spole",
            "paper_doi": "https://doi.org/10.3847/psj/acf3e1",
            "source_url": "https://pgda.gsfc.nasa.gov/products/90",
            "citation": "Barker et al. 2023, Planetary Science Journal 4, 183; data DOI 10.60903/gsfcpgda-lola-spole.",
            "license": "The PGDA product page requests citation but lists no explicit license identifier; do not assign one.",
            "license_evidence_url": "https://pgda.gsfc.nasa.gov/products/90",
            "reference_product_temporal_coverage": lola_reference_period,
            "spatial_coverage": "South-polar stereographic raster covering 80–90°S in the MOON_ME/DE421 frame.",
            "horizontal_reference": "MOON_ME body-fixed frame of JPL DE421; south polar stereographic coordinates in metres.",
            "measurement_units": "m relative to the 1,737,400 m lunar reference sphere.",
            "role": "Lunar target surface heights in the MOON_ME/DE421 south polar stereographic frame; height datum is the 1,737,400 m reference sphere.",
        },
        MOON_COUNT_ID: {
            "title": "LOLA south polar return-count map, 80S, 80 m/pixel",
            "provider": "NASA Goddard Space Flight Center Planetary Geodesy Data Archive",
            "product_version": "PGDA Product 90; file LDEC_80S_80MPP_ADJ.TIF",
            "doi": "https://doi.org/10.60903/gsfcpgda-lola-spole",
            "paper_doi": "https://doi.org/10.3847/psj/acf3e1",
            "source_url": "https://pgda.gsfc.nasa.gov/products/90",
            "citation": "Barker et al. 2023, Planetary Science Journal 4, 183; data DOI 10.60903/gsfcpgda-lola-spole.",
            "license": "The PGDA product page requests citation but lists no explicit license identifier; do not assign one.",
            "license_evidence_url": "https://pgda.gsfc.nasa.gov/products/90",
            "reference_product_temporal_coverage": lola_reference_period,
            "spatial_coverage": "South-polar stereographic raster covering 80–90°S in the MOON_ME/DE421 frame.",
            "horizontal_reference": "MOON_ME body-fixed frame of JPL DE421; south polar stereographic coordinates in metres.",
            "measurement_units": "Number of LOLA laser spots per native raster pixel.",
            "role": "LOLA return count per native 80 m DEM pixel; a count is a measurement-support indicator, not area coverage.",
        },
        MOON_EFFRES_ID: {
            "title": "LOLA south polar DEM effective-resolution map, 80S, 80 m/pixel",
            "provider": "NASA Goddard Space Flight Center Planetary Geodesy Data Archive",
            "product_version": "PGDA Product 90; file LDEM_80S_80MPP_ADJ_EFFRES.TIF",
            "doi": "https://doi.org/10.60903/gsfcpgda-lola-spole",
            "paper_doi": "https://doi.org/10.3847/psj/acf3e1",
            "source_url": "https://pgda.gsfc.nasa.gov/products/90",
            "citation": "Barker et al. 2023, Planetary Science Journal 4, 183; data DOI 10.60903/gsfcpgda-lola-spole.",
            "license": "The PGDA product page requests citation but lists no explicit license identifier; do not assign one.",
            "license_evidence_url": "https://pgda.gsfc.nasa.gov/products/90",
            "reference_product_temporal_coverage": lola_reference_period,
            "spatial_coverage": "South-polar stereographic raster covering 80–90°S in the MOON_ME/DE421 frame.",
            "horizontal_reference": "MOON_ME body-fixed frame of JPL DE421; south polar stereographic coordinates in metres.",
            "measurement_units": "m, reported effective horizontal resolution.",
            "role": "Source quality layer; cells averaging above the 2 km analysis scale are excluded from lunar profile features.",
        },
        MOON_ERROR_ID: {
            "title": "LOLA south polar DEM height-error map, 80S, 80 m/pixel",
            "provider": "NASA Goddard Space Flight Center Planetary Geodesy Data Archive",
            "product_version": "PGDA Product 90; file LDEM_80S_80MPP_ADJ_ERR.TIF",
            "doi": "https://doi.org/10.60903/gsfcpgda-lola-spole",
            "paper_doi": "https://doi.org/10.3847/psj/acf3e1",
            "source_url": "https://pgda.gsfc.nasa.gov/products/90",
            "citation": "Barker et al. 2023, Planetary Science Journal 4, 183; data DOI 10.60903/gsfcpgda-lola-spole.",
            "license": "The PGDA product page requests citation but lists no explicit license identifier; do not assign one.",
            "license_evidence_url": "https://pgda.gsfc.nasa.gov/products/90",
            "reference_product_temporal_coverage": lola_reference_period,
            "spatial_coverage": "South-polar stereographic raster covering 80–90°S in the MOON_ME/DE421 frame.",
            "horizontal_reference": "MOON_ME body-fixed frame of JPL DE421; south polar stereographic coordinates in metres.",
            "measurement_units": "m, reported height error.",
            "role": "Source uncertainty layer; summarized with the lunar profile and not mistaken for target terrain roughness.",
        },
    }
    result = []
    for dataset_id in ids:
        entry = {"dataset_id": dataset_id, **metadata[dataset_id]}
        entry["files"] = [record["filename"] for record in file_records if record["dataset_id"] == dataset_id]
        result.append(entry)
    return result


def build(raw_dir: Path, manifest_path: Path, source_manifest_path: Path) -> dict[str, Any]:
    raw_dir = raw_dir.resolve()
    source_manifest_path = source_manifest_path.resolve()
    source_lock, file_records = _verify_source_lock(raw_dir, source_manifest_path)
    try:
        source_manifest_location = source_manifest_path.relative_to(ROOT).as_posix()
    except ValueError:
        source_manifest_location = str(source_manifest_path)
    mars_outer = MARS_RADIUS_REGION_M + WINDOW_RADIUS_M
    mars_half = math.ceil(mars_outer / GRID_M) * GRID_M
    mars_cols = mars_rows = int(2 * mars_half / GRID_M)
    mars_transform = from_origin(-mars_half, mars_half, GRID_M, GRID_M)
    mars_projection = CRS.from_proj4(
        f"+proj=aeqd +lat_0={MARS_CENTER_LAT} +lon_0={MARS_CENTER_LON} +R={MARS_RADIUS_M} +units=m +no_defs +type=crs"
    )
    mars_y, mars_x = np.indices((mars_rows, mars_cols), dtype=np.float64)
    mars_x = mars_transform.c + (mars_x + 0.5) * mars_transform.a
    mars_y = mars_transform.f + (mars_y + 0.5) * mars_transform.e
    mars_region = np.hypot(mars_x, mars_y) <= MARS_RADIUS_REGION_M
    mars_z, mars_quality, mars_longitude_check = _mars_source_quality(
        raw_dir,
        output_transform=mars_transform,
        output_crs=mars_projection,
        output_shape=(mars_rows, mars_cols),
        core_mask=mars_region,
    )
    mars_valid = np.isfinite(mars_z)
    mars_scale = np.ones_like(mars_z, dtype=np.float32)
    mars_features, mars_window_coverage = _profile_grid(mars_z, mars_valid, mars_region, mars_scale)
    mars_stats = _feature_statistics(mars_features, mars_region, _cell_area_weights(mars_scale))
    mars_manual = _manual_feature_reproduction(mars_z, mars_valid, mars_region, mars_features, mars_scale)
    mars_center_coordinates = _body_coordinates_from_projected(
        x=mars_manual["projected_cell_center_m"][0],
        y=mars_manual["projected_cell_center_m"][1],
        projected_crs=mars_projection,
        geographic_crs=CRS.from_proj4(f"+proj=longlat +R={MARS_RADIUS_M} +no_defs +type=crs"),
    )
    mars_manual["body_coordinates"] = mars_center_coordinates

    moon_extent_m = 304_000.0
    moon_grid_size = int(2 * moon_extent_m / GRID_M)
    moon_transform = from_origin(-moon_extent_m, moon_extent_m, GRID_M, GRID_M)
    moon_profiles, moon_source_meta, moon_info = _moon_source(
        raw_dir,
        (moon_grid_size, moon_grid_size),
        moon_transform,
    )
    moon_z = moon_profiles["dem"]
    moon_valid = moon_profiles["valid"]
    moon_region = moon_profiles["region_mask"]
    moon_scale = moon_profiles["scale_factor"].astype(np.float32)
    moon_features, moon_window_coverage = _profile_grid(moon_z, moon_valid, moon_region, moon_scale)
    moon_stats = _feature_statistics(moon_features, moon_region, _cell_area_weights(moon_scale))
    moon_manual = _manual_feature_reproduction(moon_z, moon_valid, moon_region, moon_features, moon_scale)
    moon_manual["body_coordinates"] = _body_coordinates_from_projected(
        x=moon_manual["projected_cell_center_m"][0],
        y=moon_manual["projected_cell_center_m"][1],
        projected_crs=moon_source_meta["dem"]["crs_wkt"],
        geographic_crs=CRS.from_proj4(f"+proj=longlat +R={MOON_RADIUS_M} +no_defs +type=crs"),
    )

    mars_source_ids = [MARS_DEM_ID, MARS_COUNT_ID]
    moon_source_ids = [MOON_DEM_ID, MOON_COUNT_ID, MOON_EFFRES_ID, MOON_ERROR_ID]
    mars_limitations = [
        "USGS Gazetteer center and diameter define a circular envelope; the USGS depiction is approximate and this is not a digitized crater-rim polygon.",
        "MOLA MEGT interpolates bins without direct observations. MEGC support is retained in the source-quality report; interpolated values are not direct measurements.",
        "Topographic derivatives use a 2 km area-averaged grid and 10 km physical-radius windows; no absolute elevations are compared across bodies.",
        "Neighbouring target-cell feature windows overlap heavily; profile cells are spatially dependent and are not independent samples.",
    ]
    moon_limitations = [
        "The profile is limited to the source-covered 80–90°S cap; it does not represent the full lunar south-polar region north of 80°S.",
        "80 m is raster posting, not a claim of 80 m effective resolution. LOLA return counts, effective resolution, and height error remain separate quality layers.",
        "LOLA heights are relative to the 1,737,400 m reference sphere; only terrain derivatives are used, never cross-body absolute height.",
        "Polar-stereographic metric scale is corrected in feature windows; the nominal 2 km cell ground size varies slightly toward the 80°S boundary.",
        "Neighbouring target-cell feature windows overlap heavily; profile cells are spatially dependent and are not independent samples.",
    ]
    mars_profile = {
        "profile_id": "mars-jezero-mola128-v1",
        "name": "Jezero crater, Mars",
        "body": "mars",
        "profile_version": "mola128-2km-grid-10km-window-v1",
        "region": {
            "region_id": "mars-jezero-crater-usgs-envelope",
            "name": "Jezero crater circular envelope (USGS center and diameter)",
            "coordinate_system": {
                "coordinate_system_id": "mars-jezero-local-aeqd-m",
                "body": "mars",
                "name": "Local spherical azimuthal equidistant centered at 18.41°N, 77.69°E on the 3,396,000 m MOLA sphere; geometry axes X/Y in metres.",
                "longitude_direction": "not_applicable",
                "longitude_domain": "not_applicable",
                "latitude_type": "other",
                "vertical_reference": "MOLA areoid GMM-3 (degree/order 50); only derivative features are compared.",
                "vertical_reference_missing_reason": None,
            },
            "geometry": {
                "type": "Polygon",
                "coordinate_system_id": "mars-jezero-local-aeqd-m",
                "coordinates": _projected_circle_geometry(MARS_RADIUS_REGION_M),
            },
            "geometry_missing_reason": None,
        },
        "features": _profile_feature_objects(
            mars_stats,
            source_ids=mars_source_ids,
            source_resolution_m=MOLA_PX_M,
            projection_description=(
                "MEGT 128 px/degree is 463.058 m/pixel at the equator and about 439 m east-west at 18.41°N. "
                "Area-average to a 2 km local spherical azimuthal-equidistant grid; slope spacing and the 10 km windows are in metres."
            ),
            profile_limitations=mars_limitations,
        ),
        "source_ids": mars_source_ids,
        "limitations": mars_limitations,
    }
    moon_cap_radius = float(moon_source_meta["cap_radius_in_stereographic_m"])
    moon_profile = {
        "profile_id": "moon-south-polar-80s-lola80-v1",
        "name": "Lunar south polar cap, 80–90°S",
        "body": "moon",
        "profile_version": "lola-pgda-80m-2km-grid-10km-window-v1",
        "region": {
            "region_id": "moon-south-polar-cap-80s",
            "name": "Lunar south polar cap from the LOLA 80°S product boundary",
            "coordinate_system": {
                "coordinate_system_id": "moon-me-de421-south-polar-stereographic-m",
                "body": "moon",
                "name": "South polar stereographic in the MOON_ME frame of JPL DE421; sphere radius 1,737,400 m; geometry axes X/Y in metres.",
                "longitude_direction": "not_applicable",
                "longitude_domain": "not_applicable",
                "latitude_type": "other",
                "vertical_reference": "LOLA shape height relative to the 1,737,400 m reference sphere; only derivative features are compared.",
                "vertical_reference_missing_reason": None,
            },
            "geometry": {
                "type": "Polygon",
                "coordinate_system_id": "moon-me-de421-south-polar-stereographic-m",
                "coordinates": _projected_circle_geometry(moon_cap_radius),
            },
            "geometry_missing_reason": None,
        },
        "features": _profile_feature_objects(
            moon_stats,
            source_ids=moon_source_ids,
            source_resolution_m=80.0,
            projection_description=(
                "LOLA PGDA 80 m/pixel south polar stereographic DEM; area-average to a nominal 2 km grid. "
                "Feature distances use the local spherical-stereographic scale correction and a 10 km physical-radius window."
            ),
            profile_limitations=moon_limitations,
        ),
        "source_ids": moon_source_ids,
        "limitations": moon_limitations,
    }

    source_datasets = _source_catalog(file_records, raw_dir)
    code_hash = sha256_text_file(Path(__file__))
    try:
        code_revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        code_revision = None
    manifest: dict[str, Any] = {
        "manifest_version": 1,
        "task_id": "K-004",
        "accessed_at": source_lock["accessed_at"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file_manifest": source_manifest_location,
        "source_file_manifest_sha256": sha256_text_file(source_manifest_path),
        "processing": {
            "code_file": "pipeline/profiles/build_profiles.py",
            "code_sha256": code_hash,
            "git_revision": code_revision,
            "software_versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "rasterio": rasterio.__version__,
                "gdal": rasterio.__gdal_version__,
                "pyproj": pyproj.__version__,
                "proj": pyproj.proj_version_str,
            },
            "analysis_cell_resolution_m": GRID_M,
            "source_resampling": "area-weighted average of source DEM bins/cells",
            "feature_window_radius_m": WINDOW_RADIUS_M,
            "minimum_valid_fraction_per_feature_window": MIN_WINDOW_VALID_FRACTION,
            "slope_method": "central finite difference using local ground spacing in metres",
            "roughness_method": "population standard deviation of least-squares plane residuals within the circular window",
            "relief_method": "P95 minus P05 within the circular window",
            "profile_reference_interval": "area-weighted P10 through P90 of valid target-grid features",
            "tolerance_rule": "1.5 times the area-weighted profile IQR (P75-P25); explicit experimental assumption, not sensor uncertainty",
            "lunar_effective_resolution_filter_m": 2_000.0,
            "planetary_height_policy": "Derivative features only; no absolute height is compared between planetary vertical references.",
        },
        "profiles": [
            {
                "profile_id": mars_profile["profile_id"],
                "response_path": "pipeline/profiles/mars-jezero-v1.json",
                "profile_version": mars_profile["profile_version"],
                "region": {
                    "published_center_planetocentric_lat_lon_east_deg": [MARS_CENTER_LAT, MARS_CENTER_LON],
                    "published_diameter_m": MARS_DIAMETER_M,
                    "geometry_rule": "Circle on the MOLA reference sphere using USGS Gazetteer feature center and diameter.",
                },
                "grid": {
                    "width": mars_cols,
                    "height": mars_rows,
                    "pixel_size_m": GRID_M,
                    "crs_wkt": mars_projection.to_wkt(),
                    "region_candidate_cell_count": int(np.count_nonzero(mars_region)),
                    "feature_window_valid_fraction_by_grid_cell": {
                        "p05": float(np.nanpercentile(mars_window_coverage[mars_region], 5)),
                        "p50": float(np.nanpercentile(mars_window_coverage[mars_region], 50)),
                        "p95": float(np.nanpercentile(mars_window_coverage[mars_region], 95)),
                    },
                },
                "feature_statistics": mars_stats,
                "source_quality": mars_quality,
                "longitude_convention_check": mars_longitude_check,
                "manual_extraction_check": mars_manual,
                "sources": mars_source_ids,
            },
            {
                "profile_id": moon_profile["profile_id"],
                "response_path": "pipeline/profiles/moon-south-polar-80s-v1.json",
                "profile_version": moon_profile["profile_version"],
                "region": {
                    "coordinate_system_id": "moon-me-de421-south-polar-stereographic-m",
                    "boundary_latitude_planetocentric_deg": MOON_CAP_LAT_DEG,
                    "projected_cap_radius_m": moon_cap_radius,
                    "geometry_rule": "Geodesic 80-90°S cap in the MOON_ME/DE421 sphere, converted to its south-polar stereographic circle.",
                },
                "grid": {
                    "width": moon_grid_size,
                    "height": moon_grid_size,
                    "pixel_size_nominal_m": GRID_M,
                    "source_crs_wkt": moon_source_meta["dem"]["crs_wkt"],
                    "region_candidate_cell_count": int(np.count_nonzero(moon_region)),
                    "feature_window_valid_fraction_by_grid_cell": {
                        "p05": float(np.nanpercentile(moon_window_coverage[moon_region], 5)),
                        "p50": float(np.nanpercentile(moon_window_coverage[moon_region], 50)),
                        "p95": float(np.nanpercentile(moon_window_coverage[moon_region], 95)),
                    },
                },
                "feature_statistics": moon_stats,
                "source_quality": moon_info["quality"],
                "source_raster_metadata": moon_source_meta,
                "longitude_convention_check": moon_info["longitude_check"],
                "manual_extraction_check": moon_manual,
                "sources": moon_source_ids,
            },
        ],
        "datasets": source_datasets,
        "files": file_records,
        "limitations": [
            "The two target regions have different physical area and geomorphology; their source statistics are not interchangeable targets.",
            "Neighbouring target-cell feature windows overlap heavily; profile cells are spatially dependent and are not independent samples.",
            "Reference intervals and tolerances are provisional, result-blind engineering rules; validate their sensitivity before using them as scientific thresholds.",
            "Mars MEGT bins without direct MOLA observations are product-provided interpolations; the MEGC support fraction is reported.",
            "LOLA map posting, effective resolution, return counts, and height error are separate quantities and must not be conflated.",
        ],
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    profile_outputs = [
        (PROFILE_DIR / "mars-jezero-v1.json", mars_profile),
        (PROFILE_DIR / "moon-south-polar-80s-v1.json", moon_profile),
    ]
    for path, profile in profile_outputs:
        response = {"contract_version": "1.0.0", "is_synthetic": False, "profile": profile}
        path.write_text(json.dumps(response, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive the measured K-004 planetary reference profiles.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW, help="Directory containing pinned public input rasters and labels.")
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST, help="Pinned input sizes and SHA-256 values.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Output provenance and quality manifest.")
    args = parser.parse_args()
    result = build(args.raw_dir, args.manifest, args.source_manifest)
    for profile in result["profiles"]:
        print(
            f"{profile['profile_id']}: {profile['grid']['region_candidate_cell_count']} region cells; "
            f"all-feature valid={profile['feature_statistics']['joint_coverage']['all_three_features_valid_cell_count']}"
        )
        for feature_id in ("slope_deg", "roughness_m", "relief_m"):
            stats = profile["feature_statistics"][feature_id]
            print(
                f"  {feature_id}: interval={stats['reference_interval']} {stats['unit']}; "
                f"tolerance={stats['tolerance']}; n={stats['valid_cell_count']}"
            )
        print(f"  longitude convention round-trip: {profile['longitude_convention_check']['round_trip_passed']}")
        print(
            "  manual feature reproduction: "
            + str(all(check["passed"] for check in profile["manual_extraction_check"]["feature_reproduction"].values()))
        )
    print(f"Wrote {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
