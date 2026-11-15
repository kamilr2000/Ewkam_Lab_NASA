"""Metric regional grids and a transparent 60-arc-second global budget."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Geod, Transformer
from rasterio.enums import Resampling
from rasterio.transform import Affine, from_origin
from rasterio.warp import reproject, transform_bounds


@dataclass(frozen=True)
class ProjectedGrid:
    crs: str
    transform: Affine
    shape: tuple[int, int]
    cell_size_m: int
    requested_bounds_wgs84: tuple[float, float, float, float]
    bounds_m: tuple[float, float, float, float]

    @property
    def cell_area_km2(self) -> float:
        return (self.cell_size_m * self.cell_size_m) / 1_000_000.0


def make_local_utm_grid(
    bounds_wgs84: tuple[float, float, float, float],
    *,
    cell_size_m: int,
    margin_m: int,
) -> ProjectedGrid:
    """Create a cell-centred UTM grid aligned to whole-cell metre multiples.

    ``bounds_wgs84`` is west, south, east, north. The grid includes a metric
    margin around the AOI so local windows can be calculated without treating
    the AOI boundary as missing terrain.
    """
    west, south, east, north = bounds_wgs84
    if not (-180 <= west < east <= 180 and -80 <= south < north <= 84):
        raise ValueError("UTM AOIs must be ordered, non-wrapping, and inside 80°S–84°N")
    if cell_size_m <= 0 or margin_m < 0:
        raise ValueError("cell_size_m must be positive and margin_m must be non-negative")

    center_lon = (west + east) / 2.0
    center_lat = (south + north) / 2.0
    zone = min(60, max(1, math.floor((center_lon + 180.0) / 6.0) + 1))
    epsg = (32600 if center_lat >= 0 else 32700) + zone
    target_crs = f"EPSG:{epsg}"
    projected = transform_bounds(
        "EPSG:4326", target_crs, west, south, east, north, densify_pts=21
    )
    left = math.floor((projected[0] - margin_m) / cell_size_m) * cell_size_m
    bottom = math.floor((projected[1] - margin_m) / cell_size_m) * cell_size_m
    right = math.ceil((projected[2] + margin_m) / cell_size_m) * cell_size_m
    top = math.ceil((projected[3] + margin_m) / cell_size_m) * cell_size_m
    width = int(round((right - left) / cell_size_m))
    height = int(round((top - bottom) / cell_size_m))
    if width <= 0 or height <= 0:
        raise ValueError("AOI produced an empty projected grid")

    return ProjectedGrid(
        crs=target_crs,
        transform=from_origin(left, top, cell_size_m, cell_size_m),
        shape=(height, width),
        cell_size_m=cell_size_m,
        requested_bounds_wgs84=bounds_wgs84,
        bounds_m=(left, bottom, right, top),
    )


def grid_centers_wgs84(
    grid: ProjectedGrid,
    *,
    start_row: int = 0,
    end_row: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return centre longitudes/latitudes for all or a row slice of a grid."""
    height, width = grid.shape
    end_row = height if end_row is None else end_row
    if not (0 <= start_row <= end_row <= height):
        raise ValueError("row slice is outside the grid")
    x = grid.transform.c + (np.arange(width, dtype="float64") + 0.5) * grid.transform.a
    rows = np.arange(start_row, end_row, dtype="float64")
    y = grid.transform.f + (rows + 0.5) * grid.transform.e
    x_mesh = np.broadcast_to(x, (len(rows), width))
    y_mesh = np.broadcast_to(y[:, None], (len(rows), width))
    transformer = Transformer.from_crs(grid.crs, "EPSG:4326", always_xy=True)
    longitude, latitude = transformer.transform(x_mesh, y_mesh)
    return np.asarray(longitude), np.asarray(latitude)


def grid_cell_areas_km2(
    grid: ProjectedGrid,
    rows: np.ndarray,
    columns: np.ndarray,
) -> np.ndarray:
    """Estimate physical cell areas from the ellipsoidal polygon corners."""
    rows = np.asarray(rows, dtype="int64")
    columns = np.asarray(columns, dtype="int64")
    if rows.shape != columns.shape or rows.ndim != 1:
        raise ValueError("rows and columns must be same-length one-dimensional arrays")
    if np.any(rows < 0) or np.any(rows >= grid.shape[0]) or np.any(columns < 0) or np.any(columns >= grid.shape[1]):
        raise ValueError("cell index is outside the grid")
    if not rows.size:
        return np.empty(0, dtype="float64")

    x_left = grid.transform.c + columns * grid.transform.a
    x_right = x_left + grid.transform.a
    y_top = grid.transform.f + rows * grid.transform.e
    y_bottom = y_top + grid.transform.e
    x = np.column_stack((x_left, x_right, x_right, x_left))
    y = np.column_stack((y_top, y_top, y_bottom, y_bottom))
    transformer = Transformer.from_crs(grid.crs, "EPSG:4326", always_xy=True)
    longitude, latitude = transformer.transform(x, y)
    geod = Geod(ellps="WGS84")
    areas = np.empty(rows.size, dtype="float64")
    for index in range(rows.size):
        area_m2, _ = geod.polygon_area_perimeter(longitude[index], latitude[index])
        areas[index] = abs(area_m2) / 1_000_000.0
    return areas


def warp_raster_to_grid(
    source_path: Path,
    grid: ProjectedGrid,
    *,
    resampling: Resampling = Resampling.average,
    source_valid_mask: np.ndarray | None = None,
) -> tuple[np.ndarray, dict[str, object]]:
    """Warp one raster band to a metric grid without filling missing samples.

    A source validity mask excludes classified non-target samples before
    resampling. This is needed for surface DEMs such as ETOPO, whose ocean
    cells contain valid bathymetry rather than source no-data.
    """
    destination = np.full(grid.shape, np.nan, dtype="float32")
    with rasterio.open(source_path) as source:
        if source.count < 1 or source.crs is None:
            raise ValueError(f"Source raster has no usable first band/CRS: {source_path}")
        source_data = rasterio.band(source, 1)
        source_nodata = source.nodata
        if source_valid_mask is not None:
            valid_mask = np.asarray(source_valid_mask, dtype=bool)
            if valid_mask.shape != (source.height, source.width):
                raise ValueError("source_valid_mask must match the source raster shape")
            source_values = source.read(1).astype("float32", copy=False)
            valid = valid_mask & np.isfinite(source_values)
            if source.nodata is not None:
                if np.isnan(source.nodata):
                    valid &= ~np.isnan(source_values)
                else:
                    valid &= source_values != np.float32(source.nodata)
            source_values[~valid] = np.nan
            source_data = source_values
            source_nodata = np.nan
        reproject(
            source=source_data,
            destination=destination,
            src_transform=source.transform,
            src_crs=source.crs,
            src_nodata=source_nodata,
            dst_transform=grid.transform,
            dst_crs=grid.crs,
            dst_nodata=np.nan,
            resampling=resampling,
            init_dest_nodata=True,
            num_threads=2,
        )
        metadata: dict[str, object] = {
            "width": source.width,
            "height": source.height,
            "crs": source.crs.to_string(),
            "transform": [
                source.transform.a,
                source.transform.b,
                source.transform.c,
                source.transform.d,
                source.transform.e,
                source.transform.f,
            ],
            "nodata": source.nodata,
            "dtype": source.dtypes[0],
        }
    return destination, metadata


def global_60_arcsecond_budget(
    *,
    feature_window_radius_m: int = 10_000,
    batch_rows: int = 64,
) -> dict[str, object]:
    """Calculate exact grid dimensions and explicit array-memory bounds.

    This is an arithmetic scale model, not a measured global preprocessing
    run. It models a 60-arc-second cell-centred Earth grid and the float32
    15-arc-second ETOPO source, including a source-resolution land mask, with
    no duplicate antimeridian sample or polar endpoint.
    """
    arc_seconds = 60
    if feature_window_radius_m <= 0 or batch_rows <= 0:
        raise ValueError("feature_window_radius_m and batch_rows must be positive")
    columns = 360 * 3600 // arc_seconds
    rows = 180 * 3600 // arc_seconds
    cells = columns * rows
    source_ratio = 60 // 15
    north_south_cell_m = 110_574.0 * arc_seconds / 3600.0
    halo_rows = math.ceil(feature_window_radius_m / north_south_cell_m) + 1
    working_rows = min(rows, batch_rows + 2 * halo_rows)

    # Full candidate arrays: target DEM float32; three float32 features; centre
    # land/valid masks; window support and 4x-sampled land fraction float32.
    full_state_bytes_per_cell = 4 + (3 * 4) + 1 + 1 + 4 + 4
    # Working arrays also include DEM float32, validity, feature outputs,
    # sample support, eligibility, longitude/latitude float64 and land fraction.
    working_bytes_per_cell = 4 + 1 + 1 + (3 * 4) + 4 + 1 + (2 * 8) + 4
    working_arrays = working_rows * columns * working_bytes_per_cell
    # ETOPO is float32; the source land mask has one byte per 15″ source cell.
    source_rows = working_rows * source_ratio + 2
    source_columns = columns * source_ratio
    source_float32_window_bytes = source_rows * source_columns * 4
    source_land_mask_bytes = source_rows * source_columns

    return {
        "grid": {
            "angular_resolution_arc_seconds": arc_seconds,
            "cell_layout": "one cell-centred sample per angular interval; no duplicate seam or pole endpoint",
            "columns": columns,
            "rows": rows,
            "total_cells": cells,
        },
        "storage_model": {
            "raw_60_arcsecond_float32_dem_bytes": cells * 4,
            "three_float32_feature_arrays_bytes": cells * 3 * 4,
            "full_candidate_state_bytes_per_cell": full_state_bytes_per_cell,
            "full_candidate_state_bytes": cells * full_state_bytes_per_cell,
        },
        "working_batch_model": {
            "core_rows": batch_rows,
            "halo_rows_each_side": halo_rows,
            "resident_rows_including_halo": working_rows,
            "working_arrays_bytes_per_cell": working_bytes_per_cell,
            "working_arrays_bytes": working_arrays,
            "source_grid_arc_seconds": 15,
            "source_window_rows": source_rows,
            "source_window_columns": source_columns,
            "source_float32_window_bytes": source_float32_window_bytes,
            "source_gshhg_land_mask_bytes": source_land_mask_bytes,
            "estimated_bytes_before_gdal_and_geometry_buffers": working_arrays + source_float32_window_bytes + source_land_mask_bytes,
            "batch_count": math.ceil(rows / batch_rows),
        },
        "basis": "Exact integer grid/array arithmetic for a 60-arc-second global layout; byte totals exclude file compression, Python objects, GDAL/PROJ caches, GSHHG geometry buffers, and polar-specific reprojection.",
        "global_run_performed": False,
        "polar_processing": "A latitude/longitude disk is singular at the poles; use a separate polar stereographic metric processing tile and map its cell results back to the declared angular candidate IDs. This is a planned control, not implemented by the regional UTM builder.",
    }
