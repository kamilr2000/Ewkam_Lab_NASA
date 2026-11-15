from __future__ import annotations

import math

import numpy as np
import pytest
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin

from pipeline.features.terrain import compute_terrain_features, manual_terrain_sample
from pipeline.grid.earth_grid import (
    ProjectedGrid,
    global_60_arcsecond_budget,
    grid_cell_areas_km2,
    grid_centers_wgs84,
    make_local_utm_grid,
    warp_raster_to_grid,
)


def test_global_60_arcsecond_budget_is_explicit_and_includes_batch_halos() -> None:
    budget = global_60_arcsecond_budget(feature_window_radius_m=10_000, batch_rows=64)

    assert budget["grid"]["columns"] == 21_600
    assert budget["grid"]["rows"] == 10_800
    assert budget["grid"]["total_cells"] == 233_280_000
    assert budget["storage_model"]["raw_60_arcsecond_float32_dem_bytes"] == 933_120_000
    assert budget["storage_model"]["three_float32_feature_arrays_bytes"] == 2_799_360_000
    assert budget["storage_model"]["full_candidate_state_bytes_per_cell"] == 26
    assert budget["storage_model"]["full_candidate_state_bytes"] == 6_065_280_000
    assert budget["working_batch_model"]["halo_rows_each_side"] == 7
    assert budget["working_batch_model"]["estimated_bytes_before_gdal_and_geometry_buffers"] == 208_094_400
    assert budget["working_batch_model"]["batch_count"] == 169
    assert budget["global_run_performed"] is False


def test_local_grid_uses_metric_cells_and_returns_centres_inside_aoi() -> None:
    bounds = (-68.9, -24.9, -68.1, -24.1)
    grid = make_local_utm_grid(bounds, cell_size_m=2_000, margin_m=12_000)
    longitude, latitude = grid_centers_wgs84(grid)

    assert grid.crs == "EPSG:32719"
    assert grid.cell_area_km2 == 4.0
    assert longitude.shape == grid.shape
    assert latitude.shape == grid.shape
    assert np.isfinite(longitude).all()
    assert np.isfinite(latitude).all()
    assert grid.shape[0] * grid.shape[1] > 0
    rows = np.array([grid.shape[0] // 2, grid.shape[0] // 2 + 1])
    columns = np.array([grid.shape[1] // 2, grid.shape[1] // 2 + 1])
    areas = grid_cell_areas_km2(grid, rows, columns)
    assert areas.shape == (2,)
    assert np.all(areas > 3.99)
    assert np.all(areas < 4.01)
    with pytest.raises(ValueError, match="inside 80°S–84°N"):
        make_local_utm_grid((0, -86, 1, -85), cell_size_m=2_000, margin_m=12_000)


def test_terrain_features_match_a_direct_manual_window_calculation() -> None:
    cell_size_m = 2_000
    rows, columns = np.indices((25, 25), dtype="float64")
    elevation = (0.1 * columns * cell_size_m + 0.2 * rows * cell_size_m + 7 * np.sin(columns / 3)).astype("float32")
    land = np.ones(elevation.shape, dtype=bool)

    result = compute_terrain_features(
        elevation,
        land,
        cell_size_m=cell_size_m,
        window_radius_m=10_000,
        minimum_valid_fraction=0.9,
    )
    manual = manual_terrain_sample(
        elevation,
        land,
        row=12,
        column=12,
        cell_size_m=cell_size_m,
        window_radius_m=10_000,
    )

    assert result.window_sample_count == 81
    assert result.minimum_window_samples == 73
    assert result.window_valid_count[12, 12] == 81
    assert math.isclose(float(result.slope_deg[12, 12]), float(manual["slope_deg"]), abs_tol=1e-5)
    assert math.isclose(float(result.roughness_m[12, 12]), float(manual["roughness_m"]), abs_tol=1e-5)
    assert math.isclose(float(result.relief_m[12, 12]), float(manual["relief_m"]), abs_tol=1e-5)


def test_nodata_is_counted_as_missing_and_does_not_become_zero() -> None:
    elevation = np.full((25, 25), -80.0, dtype="float32")
    land = np.ones(elevation.shape, dtype=bool)
    # Nine cells in the 10 km window are unavailable but outside the central 3x3.
    for row_offset, column_offset in [
        (-5, 0),
        (-4, -3),
        (-4, 3),
        (4, -3),
        (4, 3),
        (5, 0),
        (0, -5),
        (0, 5),
        (-3, -4),
    ]:
        elevation[12 + row_offset, 12 + column_offset] = np.nan

    result = compute_terrain_features(
        elevation,
        land,
        cell_size_m=2_000,
        window_radius_m=10_000,
        minimum_valid_fraction=0.9,
    )

    assert result.slope_support_fraction[12, 12] == 1.0
    assert result.window_valid_count[12, 12] == 72
    assert math.isclose(float(result.window_valid_fraction[12, 12]), 72 / 81, abs_tol=1e-7)
    assert math.isnan(float(result.roughness_m[12, 12]))
    assert math.isnan(float(result.relief_m[12, 12]))
    # A valid negative height stays a valid land measurement; elevation is not a land filter.
    assert np.isfinite(result.slope_deg[12, 12])


def test_land_only_average_does_not_mix_ocean_bathymetry_into_coastal_cell(tmp_path) -> None:
    source_path = tmp_path / "mixed-land-ocean.tif"
    source_transform = from_origin(500_000, 2_000_002, 1, 1)
    values = np.array([[100.0, -100.0], [100.0, -100.0]], dtype="float32")
    land_mask = np.array([[True, False], [True, False]])
    with rasterio.open(
        source_path,
        "w",
        driver="GTiff",
        height=2,
        width=2,
        count=1,
        dtype="float32",
        crs="EPSG:32631",
        transform=source_transform,
    ) as destination:
        destination.write(values, 1)

    target_grid = ProjectedGrid(
        crs="EPSG:32631",
        transform=from_origin(500_000, 2_000_002, 2, 2),
        shape=(1, 1),
        cell_size_m=2,
        requested_bounds_wgs84=(0.0, 0.0, 0.0, 0.0),
        bounds_m=(500_000, 2_000_000, 500_002, 2_000_002),
    )
    elevation, _ = warp_raster_to_grid(
        source_path,
        target_grid,
        resampling=Resampling.average,
        source_valid_mask=land_mask,
    )

    assert elevation.shape == (1, 1)
    assert elevation[0, 0] == pytest.approx(100.0)
