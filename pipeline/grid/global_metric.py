"""Metric candidate grid helpers for a tiled global Earth analysis."""

from __future__ import annotations

import math

import numpy as np
from pyproj import Geod, Proj, Transformer
from rasterio.transform import from_origin

from pipeline.grid.earth_grid import ProjectedGrid


POLAR_LIMIT_DEG = 80.0
WGS84_SEMI_MAJOR_M = 6_378_137.0
WGS84_INVERSE_FLATTENING = 298.257223563
ARC_MINUTE_DEG = 1.0 / 60.0


def normalize_longitude(longitude_deg: float) -> float:
    """Normalize longitude to [-180, 180), including the antimeridian."""
    if not math.isfinite(longitude_deg):
        raise ValueError("longitude must be finite")
    return (longitude_deg + 180.0) % 360.0 - 180.0


def metric_crs_for_location(longitude_deg: float, latitude_deg: float) -> tuple[str, str]:
    """Select a low-distortion metric tile CRS and stable tile family."""
    if not (math.isfinite(longitude_deg) and math.isfinite(latitude_deg)):
        raise ValueError("longitude and latitude must be finite")
    if not -90.0 <= latitude_deg <= 90.0:
        raise ValueError("latitude must be within [-90, 90]")
    longitude_deg = normalize_longitude(longitude_deg)
    if latitude_deg >= POLAR_LIMIT_DEG:
        return "EPSG:3413", "ups-north"
    if latitude_deg <= -POLAR_LIMIT_DEG:
        return "EPSG:3031", "ups-south"
    zone = min(60, max(1, math.floor((longitude_deg + 180.0) / 6.0) + 1))
    epsg = (32600 if latitude_deg >= 0 else 32700) + zone
    hemisphere = "n" if latitude_deg >= 0 else "s"
    return f"EPSG:{epsg}", f"utm{zone:02d}{hemisphere}"


def local_projection_scale_factor(crs: str, longitude_deg: float, latitude_deg: float) -> float:
    """Return the conformal linear scale factor at a WGS84 location."""
    factors = Proj(crs).get_factors(longitude_deg, latitude_deg)
    scale = (float(factors.meridional_scale) + float(factors.parallel_scale)) / 2.0
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError(f"Could not determine a finite local scale for {crs}")
    return scale


def make_metric_tile_grid(
    longitude_deg: float,
    latitude_deg: float,
    *,
    cell_size_m: int = 2_000,
    core_cells: int = 64,
    feature_window_radius_m: int = 10_000,
) -> tuple[ProjectedGrid, tuple[slice, slice], str]:
    """Make a square metric pilot tile with a feature halo.

    Candidate ownership is the 64x64 metric core. The additional cells are
    context only; they let the feature pipeline calculate full-radius windows
    without treating tile edges as missing terrain.
    """
    if cell_size_m <= 0 or core_cells <= 0 or feature_window_radius_m <= 0:
        raise ValueError("cell size, core size, and feature radius must be positive")
    longitude_deg = normalize_longitude(longitude_deg)
    if not -90.0 <= latitude_deg <= 90.0:
        raise ValueError("latitude must be within [-90, 90]")

    crs, tile_family = metric_crs_for_location(longitude_deg, latitude_deg)
    projection_scale = local_projection_scale_factor(crs, longitude_deg, latitude_deg)
    map_cell_size_m = max(1, int(round(cell_size_m * projection_scale)))
    to_metric = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    center_x, center_y = to_metric.transform(longitude_deg, latitude_deg)
    core_width_m = core_cells * map_cell_size_m
    core_left = math.floor((center_x - core_width_m / 2.0) / map_cell_size_m) * map_cell_size_m
    core_bottom = math.floor((center_y - core_width_m / 2.0) / map_cell_size_m) * map_cell_size_m
    core_right = core_left + core_width_m
    core_top = core_bottom + core_width_m
    halo_cells = math.ceil(feature_window_radius_m / cell_size_m) + 2
    halo_m = halo_cells * map_cell_size_m
    left = core_left - halo_m
    bottom = core_bottom - halo_m
    right = core_right + halo_m
    top = core_top + halo_m
    width = core_cells + 2 * halo_cells
    height = core_cells + 2 * halo_cells

    to_wgs84 = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    corner_lon, corner_lat = to_wgs84.transform(
        [core_left, core_right, core_right, core_left],
        [core_bottom, core_bottom, core_top, core_top],
    )
    requested_bounds = (
        float(np.min(corner_lon)),
        float(np.min(corner_lat)),
        float(np.max(corner_lon)),
        float(np.max(corner_lat)),
    )
    grid = ProjectedGrid(
        crs=crs,
        transform=from_origin(left, top, map_cell_size_m, map_cell_size_m),
        shape=(height, width),
        cell_size_m=map_cell_size_m,
        requested_bounds_wgs84=requested_bounds,
        bounds_m=(left, bottom, right, top),
    )
    core_slice = (
        slice(halo_cells, halo_cells + core_cells),
        slice(halo_cells, halo_cells + core_cells),
    )
    return grid, core_slice, tile_family


def arcminute_cell_metrics(latitude_deg: float) -> dict[str, float]:
    """Return ellipsoidal dimensions and area for a 60-arcsecond cell."""
    if not math.isfinite(latitude_deg) or not -90.0 < latitude_deg < 90.0:
        raise ValueError("latitude must be finite and strictly between the poles")
    half_step = ARC_MINUTE_DEG / 2.0
    geod = Geod(ellps="WGS84")
    _, _, width_m = geod.inv(0.0, latitude_deg, ARC_MINUTE_DEG, latitude_deg)
    _, _, height_m = geod.inv(
        0.0, latitude_deg - half_step, 0.0, latitude_deg + half_step
    )
    area_m2, _ = geod.polygon_area_perimeter(
        [0.0, ARC_MINUTE_DEG, ARC_MINUTE_DEG, 0.0],
        [latitude_deg - half_step, latitude_deg - half_step,
         latitude_deg + half_step, latitude_deg + half_step],
    )
    return {
        "east_west_width_m": abs(float(width_m)),
        "north_south_height_m": abs(float(height_m)),
        "ellipsoidal_area_km2": abs(float(area_m2)) / 1_000_000.0,
    }


def adaptive_longitude_columns(latitude_deg: float, *, cell_size_m: int = 2_000) -> int:
    """Approximate columns in a 60-arcsecond latitude row at fixed EW scale."""
    if not math.isfinite(latitude_deg) or not -90.0 < latitude_deg < 90.0:
        raise ValueError("latitude must be finite and strictly between the poles")
    if cell_size_m <= 0:
        raise ValueError("cell_size_m must be positive")
    flattening = 1.0 / WGS84_INVERSE_FLATTENING
    eccentricity_sq = flattening * (2.0 - flattening)
    latitude_rad = math.radians(latitude_deg)
    prime_vertical_radius = WGS84_SEMI_MAJOR_M / math.sqrt(
        1.0 - eccentricity_sq * math.sin(latitude_rad) ** 2
    )
    circumference_m = 2.0 * math.pi * prime_vertical_radius * math.cos(latitude_rad)
    return max(1, int(round(circumference_m / cell_size_m)))


def global_grid_comparison(*, cell_size_m: int = 2_000) -> dict[str, object]:
    """Compare the proposed angular grid with metric row spacing."""
    angular_rows = int(180.0 / ARC_MINUTE_DEG)
    angular_columns = int(360.0 / ARC_MINUTE_DEG)
    sample_latitudes = [-89.5, -85.0, -60.0, 0.0, 60.0, 82.0, 85.0, 89.5]
    rows = []
    for latitude in sample_latitudes:
        metrics = arcminute_cell_metrics(latitude)
        rows.append(
            {
                "latitude_deg": latitude,
                **metrics,
                "nominal_60_arcsecond_columns_per_row": angular_columns,
                "approx_metric_columns_per_row": adaptive_longitude_columns(
                    latitude, cell_size_m=cell_size_m
                ),
            }
        )
    total_metric_cells = sum(
        adaptive_longitude_columns(
            -90.0 + (row + 0.5) * ARC_MINUTE_DEG,
            cell_size_m=cell_size_m,
        )
        for row in range(angular_rows)
    )
    return {
        "angular_grid": {
            "resolution_arc_seconds": 60,
            "rows": angular_rows,
            "columns_per_row": angular_columns,
            "total_candidate_cells": angular_rows * angular_columns,
        },
        "metric_reference": {
            "north_south_step_arc_seconds": 60,
            "target_east_west_spacing_m": cell_size_m,
            "approx_total_cells": total_metric_cells,
            "row_count_matches_angular_grid": True,
            "column_count_varies_by_latitude": True,
        },
        "sample_latitudes": rows,
        "candidate_density_warning": (
            "A fixed 60-arcsecond longitude step creates progressively smaller cells "
            "toward the poles; equal per-pixel ranking can overrepresent polar area."
        ),
    }
