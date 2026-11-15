"""Rasterize or query the GSHHG 2.3.7 full-resolution land polygons.

GSHHG polygon hierarchy: L1 land, L2 lakes/water, L3 islands in lakes, L4
ponds. The Antarctica alternative is selected separately: this project uses
L6 (grounding line) as land and skips L5 (ice front), as required for a
grounded-land mask.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import shapefile
from rasterio.features import rasterize
from rasterio.transform import Affine
from rasterio.warp import transform_geom


DEFAULT_SHAPE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "k017"
    / "gshhg"
    / "extracted"
    / "GSHHS_shp"
    / "f"
)


def _layer_path(shape_root: Path, level: int) -> Path:
    path = shape_root / f"GSHHS_f_L{level}.shp"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing GSHHG full-resolution L{level} shapefile at {path}; "
            "run pipeline/download_k017_assets.py first."
        )
    return path


def _bbox_intersects(left: float, bottom: float, right: float, top: float, bbox: Iterable[float]) -> bool:
    west, south, east, north = bbox
    return not (east < left or west > right or north < bottom or south > top)


def _iter_raster_shapes(
    shape_root: Path,
    level: int,
    bbox: tuple[float, float, float, float],
) -> Iterable[tuple[dict[str, object], int]]:
    left, bottom, right, top = bbox
    reader = shapefile.Reader(str(_layer_path(shape_root, level)))
    try:
        for shape_record in reader.iterShapeRecords():
            shape = shape_record.shape
            if shape.bbox and _bbox_intersects(left, bottom, right, top, shape.bbox):
                # L1/L3/L6 are land; L2/L4 are water. L5 is intentionally skipped.
                yield shape.__geo_interface__, int(level in (1, 3, 6))
    finally:
        reader.close()


def rasterize_land_mask(
    *,
    bounds: tuple[float, float, float, float],
    out_shape: tuple[int, int],
    transform: Affine,
    shape_root: Path = DEFAULT_SHAPE_ROOT,
    dst_crs: str = "EPSG:4326",
) -> np.ndarray:
    """Return a bool mask for GSHHG L1–L4 plus Antarctica grounding-line L6.

    ``bounds`` is always a WGS84 bounding box for source-feature filtering;
    ``transform`` and ``dst_crs`` describe the destination raster grid.
    """
    burn_shapes = []
    # The order encodes the nesting: land, water, island, pond, grounded Antarctica.
    for level in (1, 2, 3, 4, 6):
        for geometry, value in _iter_raster_shapes(shape_root, level, bounds):
            if dst_crs != "EPSG:4326":
                geometry = transform_geom(
                    "EPSG:4326", dst_crs, geometry
                )
            burn_shapes.append((geometry, value))

    result = rasterize(
        burn_shapes,
        out_shape=out_shape,
        transform=transform,
        fill=0,
        dtype="uint8",
        all_touched=False,
    )
    return result.astype(bool, copy=False)


def _point_in_ring(point_x: float, point_y: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    if len(ring) < 3:
        return False
    previous_x, previous_y = ring[-1]
    for current_x, current_y in ring:
        if (current_y > point_y) != (previous_y > point_y):
            crossing_x = (previous_x - current_x) * (point_y - current_y) / (
                previous_y - current_y
            ) + current_x
            if point_x < crossing_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def _point_in_shape(point_x: float, point_y: float, shape: shapefile.Shape) -> bool:
    if not shape.bbox:
        return False
    west, south, east, north = shape.bbox
    if not (west <= point_x <= east and south <= point_y <= north):
        return False
    parts = list(shape.parts) + [len(shape.points)]
    inside = False
    for start, end in zip(parts, parts[1:]):
        ring = shape.points[start:end]
        if _point_in_ring(point_x, point_y, ring):
            inside = not inside
    return inside


def classify_land_points(
    points: Iterable[tuple[str, float, float]],
    shape_root: Path = DEFAULT_SHAPE_ROOT,
) -> list[dict[str, object]]:
    """Classify points by the deepest containing GSHHG polygon level."""
    requested = list(points)
    matches: dict[str, list[tuple[int, str]]] = {name: [] for name, _, _ in requested}

    for level in (1, 2, 3, 4, 6):
        reader = shapefile.Reader(str(_layer_path(shape_root, level)))
        try:
            for shape_record in reader.iterShapeRecords():
                shape = shape_record.shape
                west, south, east, north = shape.bbox
                for name, lon, lat in requested:
                    if west <= lon <= east and south <= lat <= north:
                        if _point_in_shape(lon, lat, shape):
                            matches[name].append((level, str(shape_record.record[0])))
        finally:
            reader.close()

    results = []
    for name, lon, lat in requested:
        point_matches = matches[name]
        # An Antarctic L6 polygon is the selected outer boundary there. For the
        # ordinary L1–L4 hierarchy the deepest containing level sets land/water.
        if any(level == 6 for level, _ in point_matches):
            deepest = 6
            land = True
        elif point_matches:
            deepest = max(level for level, _ in point_matches)
            land = deepest in (1, 3)
        else:
            deepest = None
            land = False
        results.append(
            {
                "id": name,
                "longitude": lon,
                "latitude": lat,
                "land": land,
                "deepest_level": deepest,
                "matched_features": [
                    {"level": level, "id": feature_id}
                    for level, feature_id in point_matches
                ],
            }
        )
    return results
