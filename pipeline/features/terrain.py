"""P0 topographic features with explicit metric windows and support QA."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class TerrainFeatureResult:
    slope_deg: np.ndarray
    roughness_m: np.ndarray
    relief_m: np.ndarray
    slope_support_fraction: np.ndarray
    window_land_fraction: np.ndarray
    window_valid_fraction: np.ndarray
    window_valid_count: np.ndarray
    window_sample_count: int
    minimum_window_samples: int


def circle_offsets(radius_m: int, cell_size_m: int) -> tuple[np.ndarray, np.ndarray]:
    if radius_m <= 0 or cell_size_m <= 0:
        raise ValueError("radius_m and cell_size_m must be positive")
    radius_cells = int(round(radius_m / cell_size_m))
    rows, columns = np.mgrid[-radius_cells : radius_cells + 1, -radius_cells : radius_cells + 1]
    inside = np.hypot(rows * cell_size_m, columns * cell_size_m) <= radius_m + 1e-9
    return rows[inside].astype("int32"), columns[inside].astype("int32")


def _support_fraction(mask: np.ndarray) -> np.ndarray:
    height, width = mask.shape
    support = np.zeros((height, width), dtype="float32")
    if height < 3 or width < 3:
        return support
    valid_u8 = mask.astype("uint8", copy=False)
    counts = np.zeros((height, width), dtype="uint8")
    for row_offset in (-1, 0, 1):
        for column_offset in (-1, 0, 1):
            source_rows = slice(max(0, row_offset), min(height, height + row_offset))
            source_columns = slice(max(0, column_offset), min(width, width + column_offset))
            target_rows = slice(max(0, -row_offset), min(height, height - row_offset))
            target_columns = slice(max(0, -column_offset), min(width, width - column_offset))
            counts[target_rows, target_columns] += valid_u8[source_rows, source_columns]
    support[:] = counts.astype("float32") / 9.0
    return support


def compute_terrain_features(
    elevation_m: np.ndarray,
    land_mask: np.ndarray,
    *,
    cell_size_m: int,
    window_radius_m: int,
    minimum_valid_fraction: float = 0.9,
) -> TerrainFeatureResult:
    """Compute slope, local-plane residual roughness and P95−P05 relief.

    Window statistics use a circular physical-radius neighbourhood. Their
    support fractions count finite land DEM samples against every expected
    sample in that circle; missing or water samples are never filled or
    treated as zero.
    """
    elevation = np.asarray(elevation_m, dtype="float32")
    land = np.asarray(land_mask, dtype=bool)
    if elevation.ndim != 2 or elevation.shape != land.shape:
        raise ValueError("elevation_m and land_mask must be same-shape 2D arrays")
    if cell_size_m <= 0 or window_radius_m <= 0:
        raise ValueError("cell_size_m and window_radius_m must be positive")
    if not (0 < minimum_valid_fraction <= 1):
        raise ValueError("minimum_valid_fraction must be in (0, 1]")

    valid = land & np.isfinite(elevation)
    slope = np.full(elevation.shape, np.nan, dtype="float32")
    roughness = np.full(elevation.shape, np.nan, dtype="float32")
    relief = np.full(elevation.shape, np.nan, dtype="float32")
    slope_support = _support_fraction(valid)

    if min(elevation.shape) >= 2:
        dz_drow, dz_dcolumn = np.gradient(elevation, float(cell_size_m), float(cell_size_m), edge_order=1)
        slope_values = np.degrees(np.arctan(np.hypot(dz_drow, dz_dcolumn)))
        complete_slope = slope_support >= (1.0 - 1e-7)
        slope[complete_slope] = slope_values[complete_slope].astype("float32")

    row_offsets, column_offsets = circle_offsets(window_radius_m, cell_size_m)
    total_samples = int(row_offsets.size)
    minimum_samples = math.ceil(total_samples * minimum_valid_fraction)
    height, width = elevation.shape
    window_land_fraction = np.zeros(elevation.shape, dtype="float32")
    window_valid_fraction = np.zeros(elevation.shape, dtype="float32")
    window_valid_count = np.zeros(elevation.shape, dtype="uint16")
    radius_rows = int(np.max(np.abs(row_offsets)))
    radius_columns = int(np.max(np.abs(column_offsets)))

    for row in range(radius_rows, height - radius_rows):
        sample_rows = row + row_offsets
        for column in range(radius_columns, width - radius_columns):
            sample_columns = column + column_offsets
            sample_land = land[sample_rows, sample_columns]
            sample_valid = sample_land & np.isfinite(elevation[sample_rows, sample_columns])
            count = int(sample_valid.sum())
            window_land_fraction[row, column] = float(sample_land.sum() / total_samples)
            window_valid_fraction[row, column] = float(count / total_samples)
            window_valid_count[row, column] = count
            if count < minimum_samples:
                continue

            values = elevation[sample_rows[sample_valid], sample_columns[sample_valid]].astype("float64")
            dx = column_offsets[sample_valid].astype("float64") * cell_size_m
            dy = -row_offsets[sample_valid].astype("float64") * cell_size_m
            design = np.column_stack((np.ones(values.size), dx, dy))
            coefficients, _, _, _ = np.linalg.lstsq(design, values, rcond=None)
            residuals = values - design @ coefficients
            roughness[row, column] = float(np.std(residuals, ddof=0))
            relief[row, column] = float(np.percentile(values, 95) - np.percentile(values, 5))

    return TerrainFeatureResult(
        slope_deg=slope,
        roughness_m=roughness,
        relief_m=relief,
        slope_support_fraction=slope_support,
        window_land_fraction=window_land_fraction,
        window_valid_fraction=window_valid_fraction,
        window_valid_count=window_valid_count,
        window_sample_count=total_samples,
        minimum_window_samples=minimum_samples,
    )


def manual_terrain_sample(
    elevation_m: np.ndarray,
    land_mask: np.ndarray,
    *,
    row: int,
    column: int,
    cell_size_m: int,
    window_radius_m: int,
) -> dict[str, float | int]:
    """Independently calculate one cell directly from its DEM window."""
    elevation = np.asarray(elevation_m, dtype="float64")
    land = np.asarray(land_mask, dtype=bool)
    valid = land & np.isfinite(elevation)
    if not (1 <= row < elevation.shape[0] - 1 and 1 <= column < elevation.shape[1] - 1):
        raise ValueError("manual slope sample needs a complete 3x3 neighbourhood")
    if not valid[row - 1 : row + 2, column - 1 : column + 2].all():
        raise ValueError("manual slope sample must have a fully valid 3x3 neighbourhood")

    dz_drow = (elevation[row + 1, column] - elevation[row - 1, column]) / (2 * cell_size_m)
    dz_dcolumn = (elevation[row, column + 1] - elevation[row, column - 1]) / (2 * cell_size_m)
    slope_deg = math.degrees(math.atan(math.hypot(dz_drow, dz_dcolumn)))
    row_offsets, column_offsets = circle_offsets(window_radius_m, cell_size_m)
    sample_rows = row + row_offsets
    sample_columns = column + column_offsets
    if (
        sample_rows.min() < 0
        or sample_rows.max() >= elevation.shape[0]
        or sample_columns.min() < 0
        or sample_columns.max() >= elevation.shape[1]
    ):
        raise ValueError("manual feature sample needs the complete physical-radius window")
    sample_valid = valid[sample_rows, sample_columns]
    values = elevation[sample_rows[sample_valid], sample_columns[sample_valid]]
    dx = column_offsets[sample_valid].astype("float64") * cell_size_m
    dy = -row_offsets[sample_valid].astype("float64") * cell_size_m
    design = np.column_stack((np.ones(values.size), dx, dy))
    coefficients, _, _, _ = np.linalg.lstsq(design, values, rcond=None)
    residuals = values - design @ coefficients
    return {
        "slope_deg": slope_deg,
        "roughness_m": float(np.std(residuals, ddof=0)),
        "relief_m": float(np.percentile(values, 95) - np.percentile(values, 5)),
        "window_valid_count": int(values.size),
    }
