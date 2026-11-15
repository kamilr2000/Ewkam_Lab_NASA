"""Reproducible, measured pilot for a tiled global metric Earth grid.

The pilot processes four complete 64x64 candidate tiles at 2 km, with a 14 km
feature halo, from real NOAA ETOPO 15-arc-second tiles and an independent
GSHHG mask. It deliberately does not produce a global raster or ranking.
"""

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
import platform
import time
from contextlib import ExitStack

import numpy as np
import rasterio
from pyproj import Geod, Transformer
from rasterio.enums import Resampling
from rasterio.transform import Affine
from rasterio.merge import merge
from rasterio.transform import array_bounds
from rasterio.warp import reproject, transform_bounds

from pipeline.features.terrain import compute_terrain_features, manual_terrain_sample
from pipeline.grid.earth_grid import grid_cell_areas_km2, grid_centers_wgs84
from pipeline.grid.global_metric import (
    adaptive_longitude_columns,
    arcminute_cell_metrics,
    local_projection_scale_factor,
    make_metric_tile_grid,
)
from pipeline.gshhg_mask import DEFAULT_SHAPE_ROOT, classify_land_points, rasterize_land_mask


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = REPO_ROOT / "data" / "raw"
OUTPUT_ROOT = REPO_ROOT / "data" / "derived" / "k042-global-grid-pilot"
CHECKPOINT_ROOT = REPO_ROOT / "data" / "processed" / "k042-global-grid-pilot"
MANIFEST_PATH = REPO_ROOT / "data" / "manifests" / "k042-global-grid-pilot.json"
REPORT_PATH = REPO_ROOT / "data" / "reports" / "k042-global-grid-pilot.json"
CELL_SIZE_M = 2_000
WINDOW_RADIUS_M = 10_000
MIN_VALID_FRACTION = 0.9
CORE_CELLS = 64
GSHHG_RECORD = {
    "filename": "gshhg-shp-2.3.7.zip",
    "path": "data/raw/k017/gshhg/gshhg-shp-2.3.7.zip",
    "url": "https://www.soest.hawaii.edu/pwessel/gshhg/gshhg-shp-2.3.7.zip",
    "size_bytes": 149_157_845,
    "sha256": "8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41",
}
ETOPO_RECORDS = {
    "hawaii-coast": {
        "filename": "ETOPO_2022_v1_15s_N30W165_surface.tif",
        "path": "data/raw/k017/etopo/ETOPO_2022_v1_15s_N30W165_surface.tif",
        "url": "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_N30W165_surface.tif",
        "size_bytes": 22_411_557,
        "sha256": "8265ec91d7db7644d227374afe91d23662203a4eb3fd580626b3f7d3d27dc85c",
    },
    "qattara-depression": {
        "filename": "ETOPO_2022_v1_15s_N30E015_surface.tif",
        "path": "data/raw/k042/etopo/ETOPO_2022_v1_15s_N30E015_surface.tif",
        "url": "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_N30E015_surface.tif",
        "size_bytes": 33_429_495,
        "sha256": "1ee225cb379eb7c95d446337004f413a2eb270a4682383afb6930270ec04515c",
    },
    "greenland-high-north": {
        "filename": "ETOPO_2022_v1_15s_N90W045_surface.tif",
        "path": "data/raw/k042/etopo/ETOPO_2022_v1_15s_N90W045_surface.tif",
        "url": "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_N90W045_surface.tif",
        "size_bytes": 14_851_825,
        "sha256": "d0999cc6b029eae2eb266c607778ac109052d9beb9588d53117e33d637bf92fe",
    },
    "antimeridian-east": {
        "filename": "ETOPO_2022_v1_15s_N00E165_surface.tif",
        "path": "data/raw/k042/etopo/ETOPO_2022_v1_15s_N00E165_surface.tif",
        "url": "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_N00E165_surface.tif",
        "size_bytes": 11_640_090,
        "sha256": "228580011ba4995553da6c72e2d17af3f55df4ac730dd64a27bfcb26648bf516",
    },
    "antimeridian-west": {
        "filename": "ETOPO_2022_v1_15s_N00W180_surface.tif",
        "path": "data/raw/k042/etopo/ETOPO_2022_v1_15s_N00W180_surface.tif",
        "url": "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_N00W180_surface.tif",
        "size_bytes": 16_843_500,
        "sha256": "62ac5ab585cff2a6cffd862d63123f187bf03aff81fee0ffc08cadaf2d601fdc",
    },
    "antarctica-grounded": {
        "filename": "ETOPO_2022_v1_15s_S75E000_surface.tif",
        "path": "data/raw/k042/etopo/ETOPO_2022_v1_15s_S75E000_surface.tif",
        "url": "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_S75E000_surface.tif",
        "size_bytes": 22_866_882,
        "sha256": "946c142b64712f789931a3e9c863328343a517a2987f84cadd4c7ddfb75b5f4f",
    },
    "antarctica-grounded-west": {
        "filename": "ETOPO_2022_v1_15s_S75W015_surface.tif",
        "path": "data/raw/k042/etopo/ETOPO_2022_v1_15s_S75W015_surface.tif",
        "url": "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_S75W015_surface.tif",
        "size_bytes": 23_694_802,
        "sha256": "f3329a47b67dff29382cf1679302bb0db3940b091dba110331615f12b9d736b0",
    },
}
PILOT_SITES = {
    "hawaii-coast": {
        "center_lon_deg": -155.5,
        "center_lat_deg": 19.5,
        "expected_land": True,
        "purpose": "Big Island coast and small-island preservation",
        "source_keys": ["hawaii-coast"],
    },
    "qattara-depression": {
        "center_lon_deg": 27.1,
        "center_lat_deg": 29.1,
        "expected_land": True,
        "purpose": "Below-sea-level land must remain land and retain negative elevation",
        "source_keys": ["qattara-depression"],
    },
    "greenland-high-north": {
        "center_lon_deg": -40.0,
        "center_lat_deg": 82.0,
        "expected_land": True,
        "purpose": "High-north metric cells and polar-tile path",
        "source_keys": ["greenland-high-north"],
    },
    "antarctica-grounded": {
        "center_lon_deg": 5.0,
        "center_lat_deg": -85.0,
        "expected_land": True,
        "purpose": "Grounded Antarctic mask uses GSHHG L6",
        "source_keys": ["antarctica-grounded-west", "antarctica-grounded"],
    },
}
SEAM_POINTS = [
    ("antimeridian-east", 179.99, -0.1),
    ("antimeridian-west", -179.99, -0.1),
]
OUTPUT_FIELDS = [
    "pixel_id",
    "grid_row",
    "grid_col",
    "center_lon_deg",
    "center_lat_deg",
    "pixel_area_km2",
    "land_fraction_4x",
    "is_land_center",
    "dem_valid",
    "elevation_m_egm2008",
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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    content = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _code_sha256() -> str:
    paths = [
        Path(__file__),
        REPO_ROOT / "pipeline" / "grid" / "earth_grid.py",
        REPO_ROOT / "pipeline" / "grid" / "global_metric.py",
        REPO_ROOT / "pipeline" / "features" / "terrain.py",
        REPO_ROOT / "pipeline" / "gshhg_mask.py",
    ]
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        digest.update(path.relative_to(REPO_ROOT).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _verify_file(record: dict[str, object]) -> dict[str, object]:
    path = REPO_ROOT / str(record["path"])
    if not path.is_file():
        raise FileNotFoundError(f"Pinned source is missing: {record['path']}")
    size = path.stat().st_size
    digest = _sha256_file(path)
    if size != record["size_bytes"] or digest != record["sha256"]:
        raise ValueError(
            f"Pinned source mismatch for {record['filename']}: "
            f"size={size}, sha256={digest}"
        )
    return {**record, "verified": True}


def _peak_rss_bytes() -> int | None:
    if os.name == "nt":
        import ctypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        get_current_process = kernel32.GetCurrentProcess
        get_current_process.argtypes = []
        get_current_process.restype = ctypes.c_void_p
        get_process_memory_info = psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ProcessMemoryCounters),
            ctypes.c_ulong,
        ]
        get_process_memory_info.restype = ctypes.c_int
        succeeded = get_process_memory_info(
            get_current_process(), ctypes.byref(counters), counters.cb
        )
        return int(counters.PeakWorkingSetSize) if succeeded else None
    try:
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if platform.system() == "Darwin" else value * 1024)
    except (ImportError, AttributeError):
        return None


def _safe_number(value: float | int | np.floating | np.integer) -> float | int | None:
    number = float(value)
    if not math.isfinite(number):
        return None
    if isinstance(value, (int, np.integer)):
        return int(value)
    return number


def _summary(values: np.ndarray) -> dict[str, float | int | None]:
    valid = np.asarray(values)[np.isfinite(values)]
    if not valid.size:
        return {"count": 0, "minimum": None, "p50": None, "p95": None, "maximum": None}
    return {
        "count": int(valid.size),
        "minimum": float(np.min(valid)),
        "p50": float(np.percentile(valid, 50)),
        "p95": float(np.percentile(valid, 95)),
        "maximum": float(np.max(valid)),
    }


def _format_number(value: float | int | np.floating | np.integer) -> str:
    number = float(value)
    return "" if not math.isfinite(number) else format(number, ".10g")


def _source_window_bounds(grid: object) -> tuple[float, float, float, float]:
    return transform_bounds(
        grid.crs,
        "EPSG:4326",
        *grid.bounds_m,
        densify_pts=41,
    )


def _land_fraction_4x(grid: object, *, bounds_wgs84: tuple[float, float, float, float]) -> np.ndarray:
    factor = 4
    high_shape = (grid.shape[0] * factor, grid.shape[1] * factor)
    high_transform = grid.transform * Affine.scale(1.0 / factor, 1.0 / factor)
    high_mask = rasterize_land_mask(
        bounds=bounds_wgs84,
        out_shape=high_shape,
        transform=high_transform,
        shape_root=DEFAULT_SHAPE_ROOT,
        dst_crs=grid.crs,
    )
    return high_mask.reshape(grid.shape[0], factor, grid.shape[1], factor).mean(axis=(1, 3)).astype("float32")


def _missing_reason(
    *,
    is_land: bool,
    dem_valid: bool,
    slope_support_fraction: float,
    window_valid_fraction: float,
) -> str | None:
    if not is_land:
        return "not_land"
    if not dem_valid:
        return "dem_nodata_or_no_land_source_sample"
    if slope_support_fraction < 1.0 - 1e-7:
        return "insufficient_slope_support"
    if window_valid_fraction < MIN_VALID_FRACTION:
        return "insufficient_window_support"
    return None


def _write_cells(
    path: Path,
    *,
    site_id: str,
    tile_family: str,
    grid: object,
    core_slice: tuple[slice, slice],
    longitude: np.ndarray,
    latitude: np.ndarray,
    area_km2: np.ndarray,
    land: np.ndarray,
    dem: np.ndarray,
    land_fraction: np.ndarray,
    features: object,
) -> dict[str, object]:
    rows = np.arange(core_slice[0].start, core_slice[0].stop)
    columns = np.arange(core_slice[1].start, core_slice[1].stop)
    grid_rows, grid_columns = np.meshgrid(rows, columns, indexing="ij")
    candidate_rows = grid_rows.ravel()
    candidate_columns = grid_columns.ravel()
    counts = {
        "candidate_cells": int(candidate_rows.size),
        "land_center_cells": 0,
        "valid_dem_center_cells": 0,
        "eligible_cells": 0,
        "excluded_by_reason": {},
    }
    temporary = path.with_suffix(path.suffix + ".part")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("wb") as raw_output:
        with gzip.GzipFile(
            fileobj=raw_output,
            mode="wb",
            filename="",
            mtime=0,
            compresslevel=6,
        ) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as text_output:
                writer = csv.DictWriter(text_output, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
                writer.writeheader()
                for row, column in zip(candidate_rows.tolist(), candidate_columns.tolist()):
                    is_land = bool(land[row, column])
                    dem_valid = bool(np.isfinite(dem[row, column]))
                    slope_support = float(features.slope_support_fraction[row, column])
                    window_support = float(features.window_valid_fraction[row, column])
                    reason = _missing_reason(
                        is_land=is_land,
                        dem_valid=dem_valid,
                        slope_support_fraction=slope_support,
                        window_valid_fraction=window_support,
                    )
                    counts["land_center_cells"] += int(is_land)
                    counts["valid_dem_center_cells"] += int(dem_valid)
                    counts["eligible_cells"] += int(reason is None)
                    if reason is not None:
                        reasons = counts["excluded_by_reason"]
                        reasons[reason] = reasons.get(reason, 0) + 1
                    writer.writerow(
                        {
                            "pixel_id": f"earth:k042-metric-2km:{tile_family}:{site_id}:r{row-core_slice[0].start:03d}:c{column-core_slice[1].start:03d}",
                            "grid_row": row - core_slice[0].start,
                            "grid_col": column - core_slice[1].start,
                            "center_lon_deg": _format_number(longitude[row, column]),
                            "center_lat_deg": _format_number(latitude[row, column]),
                            "pixel_area_km2": _format_number(area_km2[row, column]),
                            "land_fraction_4x": _format_number(land_fraction[row, column]),
                            "is_land_center": str(is_land).lower(),
                            "dem_valid": str(dem_valid).lower(),
                            "elevation_m_egm2008": _format_number(dem[row, column]),
                            "slope_deg": _format_number(features.slope_deg[row, column]),
                            "roughness_m": _format_number(features.roughness_m[row, column]),
                            "relief_m": _format_number(features.relief_m[row, column]),
                            "slope_support_fraction": _format_number(slope_support),
                            "window_land_fraction": _format_number(features.window_land_fraction[row, column]),
                            "window_valid_fraction": _format_number(window_support),
                            "window_valid_count": int(features.window_valid_count[row, column]),
                            "window_sample_count": int(features.window_sample_count),
                            "is_eligible": str(reason is None).lower(),
                            "missing_reason": reason or "",
                        }
                    )
    os.replace(temporary, path)
    return counts


def _resume_result(site_id: str, config_sha256: str, output_path: Path) -> dict[str, object] | None:
    checkpoint_path = CHECKPOINT_ROOT / f"{site_id}.json"
    if not checkpoint_path.is_file() or not output_path.is_file():
        return None
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if checkpoint.get("config_sha256") != config_sha256:
        return None
    output_sha = _sha256_file(output_path)
    if checkpoint.get("output_sha256") != output_sha:
        return None
    result = checkpoint.get("result")
    if not isinstance(result, dict):
        return None
    return {**result, "resumed_from_checkpoint": True}


def _run_site(
    site_id: str,
    site: dict[str, object],
    source_files: list[dict[str, object]],
    *,
    code_sha256: str,
    force: bool,
) -> dict[str, object]:
    started = time.perf_counter()
    longitude_focus = float(site["center_lon_deg"])
    latitude_focus = float(site["center_lat_deg"])
    grid, core_slice, tile_family = make_metric_tile_grid(
        longitude_focus,
        latitude_focus,
        cell_size_m=CELL_SIZE_M,
        core_cells=CORE_CELLS,
        feature_window_radius_m=WINDOW_RADIUS_M,
    )
    bounds_wgs84 = _source_window_bounds(grid)
    config = {
        "site_id": site_id,
        "center_lon_deg": longitude_focus,
        "center_lat_deg": latitude_focus,
        "grid_crs": grid.crs,
        "grid_transform": [grid.transform.a, grid.transform.b, grid.transform.c, grid.transform.d, grid.transform.e, grid.transform.f],
        "grid_shape": list(grid.shape),
        "core_slice": [[core_slice[0].start, core_slice[0].stop], [core_slice[1].start, core_slice[1].stop]],
        "cell_size_m": CELL_SIZE_M,
        "window_radius_m": WINDOW_RADIUS_M,
        "minimum_valid_fraction": MIN_VALID_FRACTION,
        "source_sha256": [record["sha256"] for record in source_files],
        "gshhg_sha256": GSHHG_RECORD["sha256"],
        "code_sha256": code_sha256,
    }
    config_sha256 = _canonical_sha256(config)
    output_path = OUTPUT_ROOT / f"{site_id}.csv.gz"
    if not force:
        cached = _resume_result(site_id, config_sha256, output_path)
        if cached is not None:
            return cached

    with ExitStack() as stack:
        sources = [stack.enter_context(rasterio.open(REPO_ROOT / str(record["path"]))) for record in source_files]
        for source, record in zip(sources, source_files):
            if source.count != 1 or source.dtypes[0] not in ("float32", "float64"):
                raise ValueError(f"Unexpected ETOPO raster layout for {record['filename']}")
        if len({source.crs for source in sources}) != 1:
            raise ValueError(f"ETOPO source tiles do not share a CRS for {site_id}")
        mosaicked, source_transform = merge(
            sources,
            bounds=bounds_wgs84,
            res=sources[0].res,
            nodata=sources[0].nodata,
            dtype="float32",
        )
        source_values = mosaicked[0].astype("float32", copy=False)
        source_window_bounds = array_bounds(
            source_values.shape[0], source_values.shape[1], source_transform
        )
        source_nodata = sources[0].nodata
        source_land = rasterize_land_mask(
            bounds=source_window_bounds,
            out_shape=source_values.shape,
            transform=source_transform,
            shape_root=DEFAULT_SHAPE_ROOT,
            dst_crs="EPSG:4326",
        )
        source_nodata_mask = ~np.isfinite(source_values)
        if source_nodata is not None:
            source_nodata_mask |= source_values == source_nodata
        source_valid = source_land & np.isfinite(source_values)
        if source_nodata is not None:
            source_valid &= source_values != source_nodata
        source_values[~source_valid] = np.nan
        dem = np.full(grid.shape, np.nan, dtype="float32")
        reproject(
            source=source_values,
            destination=dem,
            src_transform=source_transform,
            src_crs="EPSG:4326",
            src_nodata=np.nan,
            dst_transform=grid.transform,
            dst_crs=grid.crs,
            dst_nodata=np.nan,
            resampling=Resampling.average,
            init_dest_nodata=True,
        )
        source_raster = {
            "width": source_values.shape[1],
            "height": source_values.shape[0],
            "dtype": sources[0].dtypes[0],
            "native_crs": sources[0].crs.to_string() if sources[0].crs else None,
            "horizontal_crs_used_for_warp": "EPSG:4326",
            "vertical_reference": "EGM2008 geoid; values are unchanged by horizontal reprojection",
            "nodata": source_nodata,
            "source_tile_count": len(sources),
            "source_tile_window_shape_rows_columns": [int(source_values.shape[0]), int(source_values.shape[1])],
            "source_window_bounds_wgs84": [float(value) for value in source_window_bounds],
            "source_window_land_cells": int(source_land.sum()),
            "source_window_valid_land_dem_cells": int(source_valid.sum()),
            "source_window_nodata_cells": int(source_nodata_mask.sum()),
            "source_window_nonland_cells": int((~source_land).sum()),
            "source_window_nodata_or_water_cells": int(source_values.size - source_valid.sum()),
        }

    target_land = rasterize_land_mask(
        bounds=bounds_wgs84,
        out_shape=grid.shape,
        transform=grid.transform,
        shape_root=DEFAULT_SHAPE_ROOT,
        dst_crs=grid.crs,
    )
    land_fraction = _land_fraction_4x(grid, bounds_wgs84=bounds_wgs84)
    features = compute_terrain_features(
        dem,
        target_land,
        cell_size_m=CELL_SIZE_M,
        window_radius_m=WINDOW_RADIUS_M,
        minimum_valid_fraction=MIN_VALID_FRACTION,
    )
    longitude, latitude = grid_centers_wgs84(grid)
    core_rows, core_columns = np.indices((CORE_CELLS, CORE_CELLS), dtype="int64")
    core_rows += core_slice[0].start
    core_columns += core_slice[1].start
    core_rows = core_rows.ravel()
    core_columns = core_columns.ravel()
    area_km2 = np.full(grid.shape, np.nan, dtype="float64")
    area_km2[core_rows, core_columns] = grid_cell_areas_km2(grid, core_rows, core_columns)
    scale_points = [
        (longitude_focus, latitude_focus),
        (longitude[core_slice[0].start, core_slice[1].start], latitude[core_slice[0].start, core_slice[1].start]),
        (longitude[core_slice[0].start, core_slice[1].stop - 1], latitude[core_slice[0].start, core_slice[1].stop - 1]),
        (longitude[core_slice[0].stop - 1, core_slice[1].start], latitude[core_slice[0].stop - 1, core_slice[1].start]),
        (longitude[core_slice[0].stop - 1, core_slice[1].stop - 1], latitude[core_slice[0].stop - 1, core_slice[1].stop - 1]),
    ]
    scale_factors = [
        local_projection_scale_factor(grid.crs, float(lon), float(lat))
        for lon, lat in scale_points
    ]
    manual_candidates = (
        np.isfinite(features.slope_deg[core_rows, core_columns])
        & np.isfinite(features.roughness_m[core_rows, core_columns])
        & np.isfinite(features.relief_m[core_rows, core_columns])
    )
    if not manual_candidates.any():
        raise ValueError(f"No fully supported candidate cells in pilot tile {site_id}")
    supported_rows = core_rows[manual_candidates]
    supported_columns = core_columns[manual_candidates]
    geod = Geod(ellps="WGS84")
    _, _, distances = geod.inv(
        np.full(supported_rows.shape, longitude_focus),
        np.full(supported_rows.shape, latitude_focus),
        longitude[supported_rows, supported_columns],
        latitude[supported_rows, supported_columns],
    )
    manual_index = int(np.argmin(np.abs(distances)))
    manual_row = int(supported_rows[manual_index])
    manual_column = int(supported_columns[manual_index])
    manual = manual_terrain_sample(
        dem,
        target_land,
        row=manual_row,
        column=manual_column,
        cell_size_m=CELL_SIZE_M,
        window_radius_m=WINDOW_RADIUS_M,
    )
    manual_comparison = {
        "pixel_id": f"earth:k042-metric-2km:{tile_family}:{site_id}:r{manual_row-core_slice[0].start:03d}:c{manual_column-core_slice[1].start:03d}",
        "center_lon_deg": float(longitude[manual_row, manual_column]),
        "center_lat_deg": float(latitude[manual_row, manual_column]),
        "distance_to_focus_m": float(distances[manual_index]),
        "direct_check": manual,
        "pipeline_values": {
            "slope_deg": float(features.slope_deg[manual_row, manual_column]),
            "roughness_m": float(features.roughness_m[manual_row, manual_column]),
            "relief_m": float(features.relief_m[manual_row, manual_column]),
        },
        "passed": all(
            math.isclose(
                float(manual[key]),
                float(getattr(features, key)[manual_row, manual_column]),
                rel_tol=2e-7,
                abs_tol=5e-5,
            )
            for key in ("slope_deg", "roughness_m", "relief_m")
        ),
    }
    if not manual_comparison["passed"]:
        raise AssertionError(
            f"Manual feature calculation differs in {site_id}: "
            f"direct={manual_comparison['direct_check']}, "
            f"pipeline={manual_comparison['pipeline_values']}"
        )

    counts = _write_cells(
        output_path,
        site_id=site_id,
        tile_family=tile_family,
        grid=grid,
        core_slice=core_slice,
        longitude=longitude,
        latitude=latitude,
        area_km2=area_km2,
        land=target_land,
        dem=dem,
        land_fraction=land_fraction,
        features=features,
    )
    output_sha256 = _sha256_file(output_path)
    core_elevation = dem[core_rows, core_columns]
    core_land = target_land[core_rows, core_columns]
    core_eligible = (
        core_land
        & np.isfinite(core_elevation)
        & np.isfinite(features.slope_deg[core_rows, core_columns])
        & np.isfinite(features.roughness_m[core_rows, core_columns])
        & np.isfinite(features.relief_m[core_rows, core_columns])
    )
    area_values = area_km2[core_rows, core_columns]
    result = {
        "site_id": site_id,
        "purpose": site["purpose"],
        "focus_point": {
            "longitude_deg": longitude_focus,
            "latitude_deg": latitude_focus,
            "expected_land": site["expected_land"],
        },
        "tile_family": tile_family,
        "grid_version": "k042-metric-2km-pilot-v1",
        "grid_crs": grid.crs,
        "physical_cell_size_target_m": CELL_SIZE_M,
        "projected_grid_spacing_m": grid.cell_size_m,
        "projection_scale_factor_at_focus": scale_factors[0],
        "projection_scale_factor_core_corners_min": min(scale_factors[1:]),
        "projection_scale_factor_core_corners_max": max(scale_factors[1:]),
        "physical_cell_size_method": "Projected spacing is rounded from target_m * local conformal scale at the tile focus; feature distances use target physical metres, and geodesic cell areas are stored.",
        "core_cells_rows_columns": [CORE_CELLS, CORE_CELLS],
        "core_candidate_rule": "Every cell in the declared projected 64x64 tile core is emitted once; halo cells are context only.",
        "feature_window": {
            "shape": "circular",
            "radius_m": WINDOW_RADIUS_M,
            "sample_count": features.window_sample_count,
            "minimum_valid_fraction": MIN_VALID_FRACTION,
            "minimum_valid_samples": features.minimum_window_samples,
            "projected_equivalent_radius_at_focus_m": WINDOW_RADIUS_M * scale_factors[0],
            "halo_cells_each_side": int(core_slice[0].start),
            "halo_size_m_each_side": int(core_slice[0].start * CELL_SIZE_M),
        },
        "candidate_counts": counts,
        "center_land_fraction": float(core_land.mean()),
        "negative_elevation_land_cells": int(np.sum(core_land & np.isfinite(core_elevation) & (core_elevation < 0.0))),
        "minimum_negative_land_elevation_m": (
            float(np.min(core_elevation[core_land & np.isfinite(core_elevation) & (core_elevation < 0.0)]))
            if np.any(core_land & np.isfinite(core_elevation) & (core_elevation < 0.0))
            else None
        ),
        "feature_summaries_eligible_only": {
            "slope_deg": _summary(features.slope_deg[core_rows[core_eligible], core_columns[core_eligible]]),
            "roughness_m": _summary(features.roughness_m[core_rows[core_eligible], core_columns[core_eligible]]),
            "relief_m": _summary(features.relief_m[core_rows[core_eligible], core_columns[core_eligible]]),
        },
        "candidate_cell_area_km2": _summary(area_values),
        "source_raster": source_raster,
        "source_files": source_files,
        "manual_feature_check": manual_comparison,
        "output": {
            "path": output_path.relative_to(REPO_ROOT).as_posix(),
            "sha256": output_sha256,
            "size_bytes": output_path.stat().st_size,
        },
        "processing_seconds": time.perf_counter() - started,
        "resumed_from_checkpoint": False,
    }
    CHECKPOINT_ROOT.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(
        CHECKPOINT_ROOT / f"{site_id}.json",
        {"checkpoint_version": 1, "config_sha256": config_sha256, "output_sha256": output_sha256, "result": result},
    )
    return result


def _read_point_dem(record: dict[str, object], longitude: float, latitude: float) -> float | None:
    path = REPO_ROOT / str(record["path"])
    with rasterio.open(path) as dataset:
        value = float(next(dataset.sample([(longitude, latitude)]))[0])
        if not math.isfinite(value) or value == dataset.nodata:
            return None
        return value


def _run_antimeridian_control(
    east_record: dict[str, object],
    west_record: dict[str, object],
    point_land: dict[str, dict[str, object]],
) -> dict[str, object]:
    point_results = []
    for name, longitude, latitude in SEAM_POINTS:
        record = east_record if name == "antimeridian-east" else west_record
        dem_value = _read_point_dem(record, longitude, latitude)
        point_results.append(
            {
                "id": name,
                "longitude_deg": longitude,
                "latitude_deg": latitude,
                "gshhg_land": point_land[name]["land"],
                "etopo_surface_m_egm2008": dem_value,
                "source_tile": record["filename"],
            }
        )
    geod = Geod(ellps="WGS84")
    _, _, distance_m = geod.inv(SEAM_POINTS[0][1], SEAM_POINTS[0][2], SEAM_POINTS[1][1], SEAM_POINTS[1][2])
    delta_lon = ((SEAM_POINTS[1][1] - SEAM_POINTS[0][1] + 180.0) % 360.0) - 180.0
    expected = (
        all(item["gshhg_land"] is False and item["etopo_surface_m_egm2008"] is not None for item in point_results)
        and abs(delta_lon) < 0.03
        and distance_m < 3_000.0
    )
    return {
        "source_tiles": [east_record["filename"], west_record["filename"]],
        "points": point_results,
        "wrapped_longitude_delta_deg": delta_lon,
        "geodesic_distance_m": float(distance_m),
        "both_points_are_water_in_gshhg": all(item["gshhg_land"] is False for item in point_results),
        "both_source_dem_samples_valid": all(item["etopo_surface_m_egm2008"] is not None for item in point_results),
        "passed": bool(expected),
        "scope_limit": "Antimeridian points and metric wrap are verified from adjacent real source tiles; a full cross-seam metric raster tile is not part of this pilot.",
    }


def _run_mask_controls(
    selected_sites: list[str],
    source_by_key: dict[str, dict[str, object]],
) -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    requested: list[tuple[str, float, float]] = [
        (
            f"focus:{site_id}",
            float(PILOT_SITES[site_id]["center_lon_deg"]),
            float(PILOT_SITES[site_id]["center_lat_deg"]),
        )
        for site_id in selected_sites
    ]
    if "hawaii-coast" in selected_sites:
        requested.append(("hawaii-ocean", -155.99, 19.5))
    requested.extend(SEAM_POINTS)
    classifications = {
        str(result["id"]): result
        for result in classify_land_points(requested, DEFAULT_SHAPE_ROOT)
    }
    controls = []
    for site_id in selected_sites:
        site = PILOT_SITES[site_id]
        control_id = f"focus:{site_id}"
        classification = classifications[control_id]
        source_key = site["source_keys"][-1]
        source_record = source_by_key[source_key]
        source_elevation = _read_point_dem(
            source_record,
            float(site["center_lon_deg"]),
            float(site["center_lat_deg"]),
        )
        elevation_check = source_elevation is not None
        if site_id == "qattara-depression":
            elevation_check = elevation_check and source_elevation < 0.0
        passed = classification["land"] == site["expected_land"] and elevation_check
        controls.append(
            {
                "id": control_id,
                "longitude_deg": site["center_lon_deg"],
                "latitude_deg": site["center_lat_deg"],
                "expected_land": site["expected_land"],
                "gshhg_land": classification["land"],
                "gshhg_deepest_level": classification["deepest_level"],
                "etopo_surface_m_egm2008": source_elevation,
                "source_tile": source_record["filename"],
                "negative_land_elevation_required": site_id == "qattara-depression",
                "passed": bool(passed),
            }
        )
    hawaii_ocean = classifications.get("hawaii-ocean")
    hawaii_water = None
    if hawaii_ocean is not None:
        water_elevation = _read_point_dem(
            source_by_key["hawaii-coast"], -155.99, 19.5
        )
        hawaii_water = {
            "id": "hawaii-ocean",
            "longitude_deg": -155.99,
            "latitude_deg": 19.5,
            "gshhg_land": hawaii_ocean["land"],
            "etopo_bathymetry_m_egm2008": water_elevation,
            "expected_candidate_land": False,
            "passed": hawaii_ocean["land"] is False and water_elevation is not None,
        }
    all_passed = all(control["passed"] for control in controls)
    if hawaii_water is not None:
        all_passed = all_passed and bool(hawaii_water["passed"])
    return (
        {
            "sites": controls,
            "hawaii_ocean_control": hawaii_water,
            "passed": bool(all_passed),
        },
        classifications,
    )


def _global_measurements() -> dict[str, object]:
    sample_latitudes = [-89.5, -85.0, -60.0, 0.0, 60.0, 82.0, 85.0, 89.5]
    angular_rows = 10_800
    angular_columns = 21_600
    metric_columns_total = sum(
        adaptive_longitude_columns(-90.0 + (row + 0.5) / 60.0, cell_size_m=CELL_SIZE_M)
        for row in range(angular_rows)
    )
    cells = []
    for latitude in sample_latitudes:
        cells.append(
            {
                "latitude_deg": latitude,
                "fixed_60_arcsecond_cell": arcminute_cell_metrics(latitude),
                "fixed_60_arcsecond_columns_per_row": angular_columns,
                "approximately_2km_metric_columns_per_row": adaptive_longitude_columns(
                    latitude, cell_size_m=CELL_SIZE_M
                ),
            }
        )
    return {
        "proposed_angular_grid": {
            "cell_size_arc_seconds": 60,
            "rows": angular_rows,
            "columns_per_row": angular_columns,
            "candidate_positions": angular_rows * angular_columns,
        },
        "approximately_2km_metric_reference": {
            "north_south_row_step_arc_seconds": 60,
            "east_west_spacing_m": CELL_SIZE_M,
            "estimated_cell_count": metric_columns_total,
            "estimate_method": "Sum of rounded WGS84 parallel circumferences / 2,000 m for each 60-arcsecond latitude-row centre; geometric estimate, not a generated global grid.",
        },
        "sample_latitudes": cells,
    }


def _build_report(
    results: list[dict[str, object]],
    seam_result: dict[str, object],
    mask_controls: dict[str, object],
    source_records: list[dict[str, object]],
    total_seconds: float,
    code_sha256: str,
) -> tuple[dict[str, object], dict[str, object]]:
    candidate_count = sum(int(result["candidate_counts"]["candidate_cells"]) for result in results)
    output_bytes = sum(int(result["output"]["size_bytes"]) for result in results)
    output_uncompressed_bytes = 0
    for result in results:
        with gzip.open(REPO_ROOT / result["output"]["path"], "rt", encoding="utf-8") as stream:
            output_uncompressed_bytes += sum(len(line.encode("utf-8")) for line in stream)
    if candidate_count:
        bytes_per_candidate = output_bytes / candidate_count
        uncompressed_bytes_per_candidate = output_uncompressed_bytes / candidate_count
    else:
        bytes_per_candidate = 0.0
        uncompressed_bytes_per_candidate = 0.0
    global_metrics = _global_measurements()
    estimated_cells = int(global_metrics["approximately_2km_metric_reference"]["estimated_cell_count"])
    rates = [
        float(result["processing_seconds"]) / int(result["candidate_counts"]["candidate_cells"])
        for result in results
        if int(result["candidate_counts"]["candidate_cells"]) > 0
    ]
    extrapolation = {
        "basis": "Linear scale-up from the slowest and fastest measured full 64x64 core pilot tiles; this is an order-of-magnitude extrapolation, not a global run estimate validated at scale.",
        "metric_cell_count_estimate": estimated_cells,
        "candidate_count_scope": "Approximate geometric grid positions before land/NoData exclusions.",
        "processing_seconds_low_from_fastest_tile": estimated_cells * min(rates) if rates else None,
        "processing_seconds_high_from_slowest_tile": estimated_cells * max(rates) if rates else None,
        "compressed_output_bytes_at_pilot_mean_per_candidate": int(round(estimated_cells * bytes_per_candidate)),
        "uncompressed_output_bytes_at_pilot_mean_per_candidate": int(round(estimated_cells * uncompressed_bytes_per_candidate)),
        "omitted_costs": [
            "Global source-file reads and tile scheduling",
            "Global GSHHG selection/rasterization and geometry caching",
            "Checkpoint metadata, index construction, compression variance, API storage, and reprocessing retries",
            "Land and NoData filtering changes the actual eligible count and output bytes",
        ],
    }
    manifest = {
        "manifest_version": 1,
        "task_id": "K-042",
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "purpose": "Measured real-data pilot for selecting the global Earth candidate grid, DEM source scale, physical feature windows, and processing tile size.",
        "source_datasets": [
            {
                "dataset_id": "ETOPO_2022_v1_15s_surface",
                "title": "ETOPO 2022 15 arc-second global relief model, Ice Surface tiles",
                "provider": "NOAA National Centers for Environmental Information",
                "product_version": "ETOPO_2022_v1",
                "doi": "https://doi.org/10.25921/fd45-gt74",
                "license": {"id": "CC0-1.0", "evidence_url": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Aetopo_2022"},
                "horizontal_crs": "WGS84 longitude/latitude",
                "vertical_reference": "EGM2008 geoid",
                "surface_variant": "Ice Surface: top of Greenland and Antarctic ice sheets; ground-surface elevations elsewhere.",
                "files": [record for record in source_records if str(record["filename"]).endswith(".tif")],
            },
            {
                "dataset_id": "GSHHG_2.3.7_full_resolution",
                "title": "Global Self-consistent, Hierarchical, High-resolution Geography Database",
                "provider": "Paul Wessel, SOEST University of Hawai'i, and Walter H. F. Smith, NOAA",
                "doi": "https://doi.org/10.5281/zenodo.7007502",
                "license": {"id": "LGPL-3.0-or-later", "evidence_url": "https://www.soest.hawaii.edu/wessel/gshhg/"},
                "role": "Independent land/water mask: L1/L3 land, L2/L4 water, L6 Antarctic grounding line; L5 ice front omitted.",
                "files": [record for record in source_records if record["filename"] == GSHHG_RECORD["filename"]],
            },
        ],
        "processing": {
            "grid_version": "k042-metric-2km-pilot-v1",
            "candidate_cell_size_m": CELL_SIZE_M,
            "tile_core_cells": [CORE_CELLS, CORE_CELLS],
            "feature_radius_m": WINDOW_RADIUS_M,
            "feature_window_minimum_valid_fraction": MIN_VALID_FRACTION,
            "tile_halo_m": int(results[0]["feature_window"]["halo_size_m_each_side"]) if results else None,
            "candidate_policy": "Every cell in each projected tile core is retained as a candidate row; no area-average pruning, region score, or ranking is performed.",
            "source_mask_policy": "Rasterize GSHHG at the native ETOPO 15-arc-second window; exclude non-land and source NoData before averaging to metric cells; apply independent target land-centre mask.",
            "feature_model_version": "terrain-p0-k005-v2",
            "feature_model_source": "pipeline/features/terrain.py",
            "nodata_policy": "Missing source or QA support remains NaN/null with an explicit missing_reason; negative land elevation remains valid.",
            "polar_crs_policy": "UTM by 6-degree zone for |latitude|<80 degrees; EPSG:3413 north and EPSG:3031 south for polar tiles.",
            "code_sha256": code_sha256,
        },
        "outputs": [result["output"] for result in results],
        "validation_controls": mask_controls,
        "global_run_performed": False,
        "global_ranking_performed": False,
    }
    report = {
        "report_version": 1,
        "task_id": "K-042",
        "generated_at": manifest["generated_at"],
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "rasterio": rasterio.__version__,
            "gdal": rasterio.__gdal_version__,
            "proj": rasterio.__proj_version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
            "peak_working_set_bytes": _peak_rss_bytes(),
        },
        "global_grid_geometry_comparison": global_metrics,
        "measured_pilot": {
            "site_count": len(results),
            "candidate_cells_processed": candidate_count,
            "eligible_cells": sum(int(result["candidate_counts"]["eligible_cells"]) for result in results),
            "total_processing_seconds": total_seconds,
            "output_compressed_bytes": output_bytes,
            "output_uncompressed_bytes": output_uncompressed_bytes,
            "compressed_bytes_per_candidate": bytes_per_candidate,
            "uncompressed_bytes_per_candidate": uncompressed_bytes_per_candidate,
            "sites": results,
            "mask_controls": mask_controls,
            "antimeridian_control": seam_result,
        },
        "global_extrapolation": extrapolation,
        "limitations": [
            "This is four local metric tile cores plus an antimeridian point control, not a global feature build, full-coverage mask, map pyramid, or ranking.",
            "The 60-arcsecond candidate count is an angular-layout arithmetic count; it does not equal the approximately 2 km metric grid count.",
            "The 60-arcsecond ETOPO product was not separately downloaded; the source choice is tested through actual 15-arcsecond tiles and the measured geometry/source-support comparison.",
            "The antimeridian test samples both real ETOPO tiles and GSHHG points and checks geodesic wrapping; it does not yet rasterize a complete cross-seam feature tile.",
            "ETopo Ice Surface is a surface DEM over grounded ice, not bare bedrock or a measure of ice thickness.",
        ],
        "global_run_performed": False,
        "global_ranking_performed": False,
    }
    return manifest, report


def run_pilot(*, site_ids: list[str] | None = None, force: bool = False) -> dict[str, object]:
    selected_sites = list(PILOT_SITES) if site_ids is None else site_ids
    unknown = set(selected_sites) - set(PILOT_SITES)
    if unknown:
        raise ValueError(f"Unknown pilot sites: {sorted(unknown)}")
    source_records = [_verify_file(GSHHG_RECORD)]
    source_by_key: dict[str, dict[str, object]] = {}
    for site_id in selected_sites:
        for source_key in PILOT_SITES[site_id]["source_keys"]:
            source_record = _verify_file(ETOPO_RECORDS[source_key])
            source_by_key[source_key] = source_record
            source_records.append(source_record)
    seam_east = _verify_file(ETOPO_RECORDS["antimeridian-east"])
    seam_west = _verify_file(ETOPO_RECORDS["antimeridian-west"])
    source_records.extend([seam_east, seam_west])
    mask_controls, point_land = _run_mask_controls(selected_sites, source_by_key)
    if not mask_controls["passed"]:
        raise AssertionError("GSHHG/ETOPO point controls failed")
    code_sha256 = _code_sha256()
    started = time.perf_counter()
    results = [
        _run_site(
            site_id,
            PILOT_SITES[site_id],
            [source_by_key[source_key] for source_key in PILOT_SITES[site_id]["source_keys"]],
            code_sha256=code_sha256,
            force=force,
        )
        for site_id in selected_sites
    ]
    seam_result = _run_antimeridian_control(seam_east, seam_west, point_land)
    if not seam_result["passed"]:
        raise AssertionError("Antimeridian source/mask/geodesic control failed")
    total_seconds = time.perf_counter() - started
    manifest, report = _build_report(
        results, seam_result, mask_controls, source_records, total_seconds, code_sha256
    )
    _write_json_atomic(MANIFEST_PATH, manifest)
    _write_json_atomic(REPORT_PATH, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", action="append", choices=sorted(PILOT_SITES), help="Run only this named pilot site; may be repeated.")
    parser.add_argument("--force", action="store_true", help="Rebuild tile outputs even when their checkpoint and SHA match.")
    args = parser.parse_args()
    report = run_pilot(site_ids=args.site, force=args.force)
    measured = report["measured_pilot"]
    print(
        json.dumps(
            {
                "candidate_cells_processed": measured["candidate_cells_processed"],
                "eligible_cells": measured["eligible_cells"],
                "total_processing_seconds": measured["total_processing_seconds"],
                "output_compressed_bytes": measured["output_compressed_bytes"],
                "peak_working_set_bytes": report["environment"]["peak_working_set_bytes"],
                "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
                "manifest": MANIFEST_PATH.relative_to(REPO_ROOT).as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
