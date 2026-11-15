from __future__ import annotations

import math

import numpy as np
import pytest
from pyproj import Geod

from pipeline.global_grid_pilot import _missing_reason
from pipeline.grid.earth_grid import grid_cell_areas_km2
from pipeline.grid.global_metric import (
    adaptive_longitude_columns,
    arcminute_cell_metrics,
    local_projection_scale_factor,
    make_metric_tile_grid,
    metric_crs_for_location,
    normalize_longitude,
)


def test_60_arcsecond_cell_area_shrinks_toward_poles_and_metric_rows_adapt() -> None:
    equator = arcminute_cell_metrics(0.0)
    high_arctic = arcminute_cell_metrics(85.0)

    assert equator["ellipsoidal_area_km2"] == pytest.approx(3.4, abs=0.1)
    assert equator["ellipsoidal_area_km2"] / high_arctic["ellipsoidal_area_km2"] > 10.0
    assert adaptive_longitude_columns(85.0) < adaptive_longitude_columns(0.0)


def test_projection_selection_uses_utm_then_polar_stereographic() -> None:
    assert metric_crs_for_location(-155.5, 19.5) == ("EPSG:32605", "utm05n")
    assert metric_crs_for_location(27.1, 29.1) == ("EPSG:32635", "utm35n")
    assert metric_crs_for_location(-40.0, 82.0) == ("EPSG:3413", "ups-north")
    assert metric_crs_for_location(5.0, -85.0) == ("EPSG:3031", "ups-south")


def test_metric_tile_has_exact_core_and_feature_halo() -> None:
    grid, core_slice, tile_family = make_metric_tile_grid(-40.0, 82.0)

    assert grid.crs == "EPSG:3413"
    assert tile_family == "ups-north"
    assert grid.shape == (78, 78)
    assert (core_slice[0].start, core_slice[0].stop) == (7, 71)
    assert (core_slice[1].start, core_slice[1].stop) == (7, 71)
    scale = local_projection_scale_factor(grid.crs, -40.0, 82.0)
    assert grid.cell_size_m / scale == pytest.approx(2_000.0, abs=0.6)
    areas = grid_cell_areas_km2(
        grid,
        rows=np.array([39]),
        columns=np.array([39]),
    )
    assert math.isclose(float(areas[0]), 4.0, rel_tol=0.02)


def test_antimeridian_normalization_and_geodesic_distance_are_short() -> None:
    assert normalize_longitude(180.0) == -180.0
    assert normalize_longitude(540.0) == -180.0
    assert metric_crs_for_location(179.99, 0.1) == ("EPSG:32660", "utm60n")
    assert metric_crs_for_location(-179.99, 0.1) == ("EPSG:32601", "utm01n")
    geod = Geod(ellps="WGS84")
    _, _, distance = geod.inv(179.99, 0.1, -179.99, 0.1)
    assert distance < 3_000.0


def test_negative_elevation_is_not_a_missing_or_ocean_reason() -> None:
    assert _missing_reason(
        is_land=True,
        dem_valid=True,
        slope_support_fraction=1.0,
        window_valid_fraction=1.0,
    ) is None
    assert _missing_reason(
        is_land=False,
        dem_valid=True,
        slope_support_fraction=1.0,
        window_valid_fraction=1.0,
    ) == "not_land"
    assert _missing_reason(
        is_land=True,
        dem_valid=False,
        slope_support_fraction=1.0,
        window_valid_fraction=1.0,
    ) == "dem_nodata_or_no_land_source_sample"
