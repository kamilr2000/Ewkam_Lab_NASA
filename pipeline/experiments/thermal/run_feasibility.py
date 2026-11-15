"""Reproduce the K-047 thermal-data feasibility sample and report.

Raw Earth and planetary data stay in the ignored ``data/raw`` tree.  The
Earthdata token is read only by earthaccess when a protected MODIS file is
missing; it is never written to files or printed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from importlib.metadata import version as package_version

import numpy as np
import rasterio
from pyhdf.SD import SD, SDC
from pyproj import CRS, Transformer


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "data/manifests/thermal-feasibility.json"
DEFAULT_REPORT = ROOT / "data/reports/thermal-feasibility.md"
SAMPLE_DATES = ("2023-03-20", "2023-06-21", "2023-09-23", "2023-12-21")
MODIS_DATES = {"2023-03-20": "A2023079", "2023-06-21": "A2023172", "2023-09-23": "A2023266", "2023-12-21": "A2023355"}
TILE_SIZE_M = 1111950.5196666667
SINUSOIDAL = CRS.from_proj4("+proj=sinu +R=6371007.181 +nadgrids=@null +units=m +no_defs +type=crs")
WGS84 = CRS.from_epsg(4326)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(relative: str) -> Path:
    path = (ROOT / PurePosixPath(relative)).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"Manifest path leaves the repository: {relative}") from exc
    return path


def verify_asset(path: Path, asset: dict[str, Any]) -> tuple[int, str]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing sample asset: {path.relative_to(ROOT)}")
    actual_size = path.stat().st_size
    actual_hash = sha256_file(path)
    if actual_size != int(asset["size_bytes"]):
        raise ValueError(f"{path.name}: expected {asset['size_bytes']} bytes, got {actual_size}")
    if actual_hash != str(asset["sha256"]).lower():
        raise ValueError(f"{path.name}: SHA-256 mismatch")
    return actual_size, actual_hash


def _download(url: str, target: Path, headers: dict[str, str] | None = None, byte_ranges: list[list[int]] | None = None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".part")
    request_headers = {"User-Agent": "terra-analog-k047-thermal-feasibility/1.0"}
    if headers:
        request_headers.update(headers)
    try:
        with temporary.open("wb") as output:
            ranges = byte_ranges or [None]
            for byte_range in ranges:
                current_headers = dict(request_headers)
                if byte_range is not None:
                    current_headers["Range"] = f"bytes={int(byte_range[0])}-{int(byte_range[1])}"
                request = urllib.request.Request(url, headers=current_headers)
                with urllib.request.urlopen(request, timeout=180) as response:
                    if byte_range is not None:
                        expected_range = f"bytes {int(byte_range[0])}-{int(byte_range[1])}/"
                        content_range = response.headers.get("Content-Range", "")
                        if response.status != 206 or not content_range.startswith(expected_range):
                            raise ValueError("PDS server did not honor the requested byte range")
                    shutil.copyfileobj(response, output, length=1024 * 1024)
        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def download_assets(manifest: dict[str, Any]) -> None:
    protected = [a for a in manifest["assets"] if a["access"] == "earthdata"]
    auth = None
    if any(not repo_path(a["path"]).is_file() for a in protected):
        if not os.environ.get("EARTHDATA_TOKEN"):
            raise RuntimeError("EARTHDATA_TOKEN is required to download missing MODIS samples; it is never stored by this script")
        import earthaccess

        auth = earthaccess.login(strategy="environment", persist=False)
    for asset in manifest["assets"]:
        target = repo_path(asset["path"])
        if target.is_file():
            verify_asset(target, asset)
            continue
        if asset["access"] == "earthdata":
            if auth is None:
                raise RuntimeError("Earthdata authentication was not initialized")
            session = auth.get_session()
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".part")
            try:
                with session.get(asset["url"], stream=True, timeout=180) as response:
                    response.raise_for_status()
                    with temporary.open("wb") as output:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                output.write(chunk)
                temporary.replace(target)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
        else:
            if asset["access"] == "pds_range":
                source_block = target.with_name(target.name + ".source")
                _download(asset["url"], source_block, byte_ranges=[asset["byte_range"]])
                crop = asset["crop"]
                raw = source_block.read_bytes()
                bytes_per_sample = int(crop["bytes_per_sample"])
                row_bytes = int(crop["row_bytes"])
                width = int(crop["sample_width"])
                target_bytes = b"".join(raw[row * row_bytes:row * row_bytes + width * bytes_per_sample] for row in range(width))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(target_bytes)
                source_block.unlink(missing_ok=True)
            else:
                _download(asset["url"], target)
        verify_asset(target, asset)

    nasadem_assets = manifest["nasadem_swbd"]
    missing = [a for a in nasadem_assets if not repo_path(a["path"]).is_file()]
    if missing:
        helper = ROOT / "pipeline/download_k017_assets.py"
        subprocess.run([sys.executable, str(helper), "--nasadem-only"], cwd=ROOT, check=True)
    for asset in nasadem_assets:
        verify_asset(repo_path(asset["path"]), asset)


def verify_all_assets(manifest: dict[str, Any]) -> dict[str, Any]:
    checked = []
    for asset in manifest["assets"]:
        size, digest = verify_asset(repo_path(asset["path"]), asset)
        checked.append({"path": asset["path"], "size_bytes": size, "sha256": digest})
    for asset in manifest["nasadem_swbd"]:
        size, digest = verify_asset(repo_path(asset["path"]), asset)
        checked.append({"path": asset["path"], "size_bytes": size, "sha256": digest})
    return {"verified_file_count": len(checked), "verified_bytes": sum(x["size_bytes"] for x in checked), "files": checked}


def parse_pds_label(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="ascii", errors="replace")
    values: dict[str, Any] = {}
    for key in ("PRODUCT_VERSION_ID", "DATA_SET_ID", "START_TIME", "STOP_TIME", "MAP_SCALE", "SCALING_FACTOR", "OFFSET", "MISSING_CONSTANT", "COORDINATE_SYSTEM_NAME", "A_AXIS_RADIUS", "MINIMUM_WAVELENGTH", "MAXIMUM_WAVELENGTH"):
        match = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$", text, re.MULTILINE)
        if match:
            values[key.lower()] = match.group(1).strip().strip('"')
    return values


def quantiles(values: np.ndarray) -> dict[str, float | None]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"p05": None, "p50": None, "p95": None}
    q05, q50, q95 = np.percentile(values, [5, 50, 95])
    return {"p05": float(q05), "p50": float(q50), "p95": float(q95)}


def parse_tile(tile_id: str) -> tuple[int, int]:
    match = re.fullmatch(r"h(\d{2})v(\d{2})", tile_id)
    if not match:
        raise ValueError(f"Unexpected MODIS tile id: {tile_id}")
    return int(match.group(1)), int(match.group(2))


def nasadem_swbd(path: Path) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)
    if data.size != 3601 * 3601:
        raise ValueError(f"{path.name}: NASADEM SWBD must contain 3601x3601 samples")
    return data.reshape((3601, 3601))


def swbd_values(swbd: np.ndarray, tile_id: str, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    match = re.fullmatch(r"([ns])(\d{2})([ew])(\d{3})", tile_id.lower())
    if not match:
        raise ValueError(f"Unexpected NASADEM tile suffix: {tile_id}")
    south = int(match.group(2)) * (1 if match.group(1) == "n" else -1)
    west = int(match.group(4)) * (1 if match.group(3) == "e" else -1)
    rows = np.rint((south + 1 - lat) * 3600).astype(np.int64)
    cols = np.rint((lon - west) * 3600).astype(np.int64)
    rows = np.clip(rows, 0, 3600)
    cols = np.clip(cols, 0, 3600)
    return swbd[rows, cols]


def earth_grid(aoi: dict[str, Any], resolution_m: float, swbd: np.ndarray) -> dict[str, Any]:
    bounds = aoi["bounds_wgs84"]
    epsg = int(aoi["analysis_epsg"])
    to_utm = Transformer.from_crs(WGS84, CRS.from_epsg(epsg), always_xy=True)
    to_geo = Transformer.from_crs(CRS.from_epsg(epsg), WGS84, always_xy=True)
    edge_lon = np.array([bounds["west"], bounds["east"], bounds["east"], bounds["west"]])
    edge_lat = np.array([bounds["south"], bounds["south"], bounds["north"], bounds["north"]])
    bx, by = to_utm.transform(edge_lon, edge_lat)
    x0 = math.floor(min(bx) / resolution_m) * resolution_m
    x1 = math.ceil(max(bx) / resolution_m) * resolution_m
    y0 = math.floor(min(by) / resolution_m) * resolution_m
    y1 = math.ceil(max(by) / resolution_m) * resolution_m
    width, height = int(round((x1 - x0) / resolution_m)), int(round((y1 - y0) / resolution_m))
    col, row = np.meshgrid(np.arange(width), np.arange(height))
    x = x0 + (col + 0.5) * resolution_m
    y = y0 + (row + 0.5) * resolution_m
    lon, lat = to_geo.transform(x, y)
    inside = (lon >= bounds["west"]) & (lon <= bounds["east"]) & (lat >= bounds["south"]) & (lat <= bounds["north"])
    land = swbd_values(swbd, aoi["nasadem_tile_suffix"], np.asarray(lon), np.asarray(lat)) == 0
    candidate = inside & land
    return {"x0": x0, "y0": y0, "width": width, "height": height, "candidate": candidate, "to_utm": to_utm, "to_geo": to_geo}


def earth_source_centres(tile_id: str) -> tuple[np.ndarray, np.ndarray]:
    h, v = parse_tile(tile_id)
    pixel = TILE_SIZE_M / 1200.0
    x0 = -20015109.354 + h * TILE_SIZE_M
    y0 = 10007554.677 - v * TILE_SIZE_M
    xs = x0 + (np.arange(1200, dtype=np.float64) + 0.5) * pixel
    ys = y0 - (np.arange(1200, dtype=np.float64) + 0.5) * pixel
    return np.meshgrid(xs, ys)


def analyse_earth(manifest: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    assets_by_name = {Path(a["path"]).name: a for a in manifest["assets"] if a["product"] == "MOD11A1.061"}
    nasadem_by_aoi = {a["aoi_id"]: a for a in manifest["nasadem_swbd"]}
    inverse_sinusoidal = Transformer.from_crs(SINUSOIDAL, WGS84, always_xy=True)
    resolution = float(manifest["analysis_grid"]["earth_cell_size_m"])
    support_fraction = float(manifest["analysis_grid"]["earth_minimum_valid_land_fraction"])
    for aoi in manifest["earth_aois"]:
        swbd = nasadem_swbd(repo_path(nasadem_by_aoi[aoi["aoi_id"]]["path"]))
        grid = earth_grid(aoi, resolution, swbd)
        candidate = grid["candidate"]
        results = []
        xp, yp = earth_source_centres(aoi["tile_id"])
        lon, lat = inverse_sinusoidal.transform(xp, yp)
        bounds = aoi["bounds_wgs84"]
        in_aoi = (lon >= bounds["west"]) & (lon <= bounds["east"]) & (lat >= bounds["south"]) & (lat <= bounds["north"])
        source_rows, source_cols = np.nonzero(in_aoi)
        source_lon, source_lat = np.asarray(lon)[in_aoi], np.asarray(lat)[in_aoi]
        source_land = swbd_values(swbd, aoi["nasadem_tile_suffix"], source_lon, source_lat) == 0
        source_rows, source_cols = source_rows[source_land], source_cols[source_land]
        source_lon, source_lat = source_lon[source_land], source_lat[source_land]
        utm_x, utm_y = grid["to_utm"].transform(source_lon, source_lat)
        target_cols = np.floor((utm_x - grid["x0"]) / resolution).astype(np.int64)
        target_rows = np.floor((utm_y - grid["y0"]) / resolution).astype(np.int64)
        in_grid = (target_cols >= 0) & (target_cols < grid["width"]) & (target_rows >= 0) & (target_rows < grid["height"])
        target_flat = target_rows[in_grid] * grid["width"] + target_cols[in_grid]
        source_rows, source_cols = source_rows[in_grid], source_cols[in_grid]
        total = np.bincount(target_flat, minlength=grid["width"] * grid["height"])
        land_source_count = int(total.sum())
        date_metrics = []
        for day in SAMPLE_DATES:
            granule_day = MODIS_DATES[day]
            filename = next(n for n in assets_by_name if n.startswith(f"MOD11A1.{granule_day}.{aoi['tile_id']}"))
            hdf = SD(str(repo_path(assets_by_name[filename]["path"])), SDC.READ)
            period_metrics = {}
            for period in ("Day", "Night"):
                lst_sds = hdf.select(f"LST_{period}_1km")
                qc_sds = hdf.select(f"QC_{period}")
                time_sds = hdf.select(f"{period}_view_time")
                lst_raw = np.asarray(lst_sds[:])[source_rows, source_cols]
                qa = np.asarray(qc_sds[:])[source_rows, source_cols]
                local_time = np.asarray(time_sds[:])[source_rows, source_cols]
                valid_lst = (lst_raw >= 7500) & (lst_raw <= 65535)
                qa_class = qa & 0b11
                good = valid_lst & (qa_class == 0)
                good_count = np.bincount(target_flat[good], minlength=grid["width"] * grid["height"])
                target_candidate = candidate.ravel()
                support = (total >= 3) & (good_count / np.maximum(total, 1) >= support_fraction) & target_candidate
                classes = {
                    "good": int(good.sum()),
                    "other_quality_produced": int((valid_lst & (qa_class == 1)).sum()),
                    "not_produced_cloud": int((qa_class == 2).sum()),
                    "not_produced_other": int((qa_class == 3).sum()),
                    "fill_or_outside_valid_range": int((~valid_lst).sum()),
                }
                good_qa = qa[good].astype(np.uint8)
                data_quality = (good_qa >> 2) & 0b11
                emissivity_error = (good_qa >> 4) & 0b11
                lst_error = (good_qa >> 6) & 0b11
                classes["detailed_flags_for_mandatory_good_pixels"] = {
                    "data_quality": {"good": int(np.count_nonzero(data_quality == 0)), "other": int(np.count_nonzero(data_quality == 1)), "tbd_10": int(np.count_nonzero(data_quality == 2)), "tbd_11": int(np.count_nonzero(data_quality == 3))},
                    "emissivity_error": {"<=0.01": int(np.count_nonzero(emissivity_error == 0)), "<=0.02": int(np.count_nonzero(emissivity_error == 1)), "<=0.04": int(np.count_nonzero(emissivity_error == 2)), ">0.04": int(np.count_nonzero(emissivity_error == 3))},
                    "lst_error_k": {"<=1": int(np.count_nonzero(lst_error == 0)), "<=2": int(np.count_nonzero(lst_error == 1)), "<=3": int(np.count_nonzero(lst_error == 2)), ">3": int(np.count_nonzero(lst_error == 3))},
                }
                time_valid = good & (local_time <= 240)
                temperature = lst_raw[good].astype(np.float64) * 0.02
                time_hours = local_time[time_valid].astype(np.float64) * 0.1
                period_metrics[period.lower()] = {
                    "good_native_land_pixel_centres": int(good.sum()),
                    "good_native_land_coverage_pct": 100.0 * float(good.sum()) / land_source_count if land_source_count else None,
                    "supported_2km_land_cells": int(support.sum()),
                    "candidate_2km_land_cells": int(np.count_nonzero(target_candidate)),
                    "supported_2km_land_cell_pct": 100.0 * float(support.sum()) / max(int(np.count_nonzero(target_candidate)), 1),
                    "qa_pixel_centre_counts": classes,
                    "surface_temperature_k": quantiles(temperature),
                    "local_solar_observation_time_hours": quantiles(time_hours),
                }
            date_metrics.append({"date": day, "land_modis_pixel_centres": land_source_count, "periods": period_metrics})
            hdf.end()
        result[aoi["aoi_id"]] = {
            "label": aoi["label"],
            "tile_id": aoi["tile_id"],
            "target_grid": {"crs": f"EPSG:{aoi['analysis_epsg']}", "cell_size_m": resolution, "candidate_land_cells": int(np.count_nonzero(candidate)), "support_rule": f"at least 3 native land pixel centres and {support_fraction:.0%} or more of those centres with good mandatory QA"},
            "dates": date_metrics,
        }
    return result


def analyse_diviner(manifest: dict[str, Any]) -> dict[str, Any]:
    moon = manifest["moon_profile"]
    n = int(moon["grid_width"])
    cell = float(moon["cell_size_m"])
    cap_radius = float(moon["cap_radius_m"])
    left, top = -n * cell / 2.0, n * cell / 2.0
    rr, cc = np.indices((n, n))
    centre_x = left + (cc + 0.5) * cell
    centre_y = top - (rr + 0.5) * cell
    candidate = (centre_x * centre_x + centre_y * centre_y) <= cap_radius * cap_radius
    root = ROOT / "data/raw/k047/diviner"
    results = {}
    for cycle in manifest["diviner_cycles"]:
        key = cycle["period"]
        stem = cycle["cycle_id"]
        paths = {
            "tb": root / f"dgdr_tb3_avg_pols_{stem}_240_jp2.jp2",
            "count": root / f"dgdr_tb3_cnt_pols_{stem}_240_jp2.jp2",
            "error": root / f"dgdr_tb3_err_pols_{stem}_240_jp2.jp2",
            "local_time": root / f"dgdr_ltim_avg_pols_{stem}_240_jp2.jp2",
        }
        label_paths = {k: root / f"{v.stem}.lbl" for k, v in paths.items()}
        labels = {k: parse_pds_label(v) for k, v in label_paths.items()}
        scalars = {k: float(v["scaling_factor"]) for k, v in labels.items()}
        offsets = {k: float(v["offset"]) for k, v in labels.items()}
        missing = {k: int(v["missing_constant"]) for k, v in labels.items()}
        maps = {}
        source_transform = None
        source_crs = None
        source_layout = None
        for name, path in paths.items():
            with rasterio.open(path) as ds:
                window = ds.window(-310000, -310000, 310000, 310000).round_offsets().round_lengths()
                layout = (ds.width, ds.height, ds.crs, ds.transform, window)
                if source_layout is not None and layout != source_layout:
                    raise ValueError(f"Diviner {stem} {name} raster grid differs from its paired products")
                source_layout = layout
                maps[name] = ds.read(1, window=window)
                source_transform = ds.window_transform(window)
                source_crs = ds.crs
        shape = maps["tb"].shape
        source_rows, source_cols = np.indices(shape)
        source_x, source_y = rasterio.transform.xy(source_transform, source_rows, source_cols, offset="center")
        source_x, source_y = np.asarray(source_x), np.asarray(source_y)
        target_col = np.floor((source_x - left) / cell).astype(np.int64)
        target_row = np.floor((top - source_y) / cell).astype(np.int64)
        in_grid = (target_col >= 0) & (target_col < n) & (target_row >= 0) & (target_row < n)
        flat = target_row[in_grid] * n + target_col[in_grid]
        candidates = candidate.ravel()[flat]
        flat = flat[candidates]
        for name in maps:
            maps[name] = maps[name].ravel()[in_grid][candidates]
        total = np.bincount(flat, minlength=n * n)
        tb_dn = maps["tb"].astype(np.int64)
        tb_k = tb_dn * scalars["tb"] + offsets["tb"]
        count_dn = maps["count"].astype(np.int64)
        err_dn = maps["error"].astype(np.int64)
        valid = (tb_dn != missing["tb"]) & (tb_k >= 10.0) & (tb_k <= 450.0)
        valid &= (count_dn != missing["count"]) & (count_dn * scalars["count"] + offsets["count"] > 0)
        valid &= err_dn != missing["error"]
        valid_count = np.bincount(flat[valid], minlength=n * n)
        fraction = valid_count / np.maximum(total, 1)
        support = candidate.ravel() & (total > 0) & (fraction >= float(manifest["analysis_grid"]["moon_minimum_valid_posting_fraction"]))
        time_dn = maps["local_time"].astype(np.int64)
        local_time_hours = time_dn * scalars["local_time"] + offsets["local_time"]
        time_valid = valid & (time_dn != missing["local_time"]) & (local_time_hours >= 0.0) & (local_time_hours <= 24.0)
        errors_k = err_dn * scalars["error"] + offsets["error"]
        results[key] = {
            "cycle_id": stem,
            "cycle_start_utc": labels["tb"]["start_time"],
            "cycle_stop_utc": labels["tb"]["stop_time"],
            "source_label_product_version": labels["tb"]["product_version_id"],
            "valid_source_posting_centres": int(valid.sum()),
            "candidate_2km_cells": int(candidate.sum()),
            "coverage_qualified_2km_cells": int(support.sum()),
            "coverage_qualified_2km_cell_pct": 100.0 * float(support.sum()) / int(candidate.sum()),
            "posting_coverage_fraction_in_candidate_cells": quantiles(fraction[candidate.ravel()]),
            "brightness_temperature_k": quantiles(tb_k[valid]),
            "local_solar_time_hours": quantiles(local_time_hours[time_valid]),
            "count_product_values": quantiles((count_dn[valid] * scalars["count"] + offsets["count"])),
            "error_estimates_k": quantiles(errors_k[valid & np.isfinite(errors_k)]),
            "qa_rule": "TB3 in the PDS-described 10–450 K range, a positive count estimate, a present error estimate, and at least 80% of native posting centres valid per 2 km target cell.",
            "grid_posting_m": float(labels["tb"]["map_scale"].split()[0]),
            "effective_spatial_resolution_m": None,
            "crs": source_crs.to_string() if source_crs else None,
        }
    return {"profile_id": moon["profile_id"], "candidate_2km_cells": int(candidate.sum()), "grid_cell_size_m": cell, "periods": results}


def _mars_cell_area_stats(manifest: dict[str, Any]) -> dict[str, Any]:
    mars = manifest["mars_profile"]
    lat0, lon0 = map(float, mars["center_planetocentric_lat_lon_east_deg"])
    radius = float(mars["planetary_radius_m"])
    region_radius = float(mars["region_diameter_m"]) / 2.0
    sample = manifest["mars_sample"]
    row0, col0 = int(sample["source_first_row"]), int(sample["source_first_column"])
    size = int(sample["sample_width"])
    rows, cols = np.indices((size, size))
    lat = np.deg2rad(90.0 - (row0 + rows + 0.5) / float(sample["pixels_per_degree"]))
    lon = np.deg2rad(-180.0 + (col0 + cols + 0.5) / float(sample["pixels_per_degree"]))
    lat_c, lon_c = math.radians(lat0), math.radians(lon0)
    cosine = np.sin(lat_c) * np.sin(lat) + np.cos(lat_c) * np.cos(lat) * np.cos(lon - lon_c)
    inside = radius * np.arccos(np.clip(cosine, -1.0, 1.0)) <= region_radius
    out = {}
    for period in ("day", "night"):
        ti = np.fromfile(repo_path(sample[f"{period}_thermal_inertia_path"]), dtype=">i2").reshape((size, size)).astype(np.float64)
        mask = np.fromfile(repo_path(sample[f"{period}_interpolation_mask_path"]), dtype=np.uint8).reshape((size, size))
        valid = inside & (ti >= 5.0) & (ti <= 5000.0)
        direct = valid & (mask == 1)
        interpolated = valid & (mask == 0)
        out[period] = {
            "native_source_pixels_inside_jezero_geometry": int(inside.sum()),
            "valid_source_pixels": int(valid.sum()),
            "direct_source_pixels": int(direct.sum()),
            "interpolated_source_pixels": int(interpolated.sum()),
            "direct_source_pixel_pct": 100.0 * float(direct.sum()) / int(valid.sum()) if valid.any() else None,
            "thermal_inertia_j_m2_k_sqrt_s": quantiles(ti[direct]),
            "source_pixel_size_at_profile_latitude_m": {
                "north_south_posting_m": radius * math.pi / 180.0 / float(sample["pixels_per_degree"]),
                "east_west_posting_m": radius * math.pi / 180.0 / float(sample["pixels_per_degree"]) * math.cos(math.radians(lat0)),
            },
        }
    return {
        "profile_id": mars["profile_id"],
        "target_grid_cell_size_m": float(mars["target_cell_size_m"]),
        "candidate_target_2km_cells": int(mars["candidate_target_cells"]),
        "independent_2km_target_support": {
            "cell_count": None,
            "reason": "The native TES posting near Jezero (about 2.8–3.0 km) is coarser than the 2 km target cell; no independent per-cell target values are assigned.",
        },
        "sample_window_source_pixels": size * size,
        "periods": out,
    }


def render_report(manifest: dict[str, Any]) -> str:
    analysis = manifest["analysis"]
    lines = [
        "# K-047 — Thermal feasibility sample",
        "",
        f"Generated: {analysis['generated_at_utc']}.",
        "",
        "## Decision",
        "",
        "**NO-GO for a single scored thermal feature in K-010.** The products do not measure the same physical quantity with compatible observation conditions and support. The MODIS split-window retrieval depends on atmospheric transmission and emissivity estimates; Diviner TB3 is a radiance-derived channel brightness temperature, and this audit does not invert it to kinetic temperature using emissivity. TES thermal inertia is an inversion output whose model depends on observing time, season, albedo, pressure and dust opacity. It is a material response property rather than a surface-temperature observation. Its source posting near Jezero is coarser than the project’s 2 km target cells.",
        "",
        "This decision is limited to the exact products and samples listed here. It does not rule out a separately specified temperature-only research layer with matched conditions, or a separate thermal-inertia comparison with suitable Earth and lunar products. K-010 remains P1; this experiment changes no production scoring, API, contract, or P0 result.",
        "",
        "## Earth — MOD11A1.061 daily surface temperature",
        "",
        "Each value below is a one-day snapshot for a solstice/equinox date in 2023, not a climatology. MOD11A1 derives clear-sky LST with a generalized split-window retrieval; the result depends on atmospheric transmission and surface emissivity estimates and is not air temperature. A MODIS native pixel centre is counted as good only when the LST raw value is in the product valid range and mandatory QA bits 1–0 are `00`. The 2 km cell support rule requires at least three land pixel centres and good mandatory QA for at least 75% of the land pixel centres in that cell. This is an experiment rule, not a MODIS product guarantee.",
        "",
        "| AOI | Date | Candidate land 2 km cells | Day supported | Good MODIS-pixel LST p50 (K) | Good-pixel local time p50 (h) | Night supported | Good MODIS-pixel LST p50 (K) | Good-pixel local time p50 (h) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for aoi_id, aoi in analysis["earth"].items():
        for day in aoi["dates"]:
            p = day["periods"]
            count = p["day"]["candidate_2km_land_cells"]
            dtemp, dtime = p["day"]["surface_temperature_k"]["p50"], p["day"]["local_solar_observation_time_hours"]["p50"]
            ntemp, ntime = p["night"]["surface_temperature_k"]["p50"], p["night"]["local_solar_observation_time_hours"]["p50"]
            fmt = lambda value: "null" if value is None else f"{value:.1f}"
            lines.append(f"| {aoi['label']} | {day['date']} | {count} | {p['day']['supported_2km_land_cells']} ({p['day']['supported_2km_land_cell_pct']:.1f}%) | {fmt(dtemp)} | {fmt(dtime)} | {p['night']['supported_2km_land_cells']} ({p['night']['supported_2km_land_cell_pct']:.1f}%) | {fmt(ntemp)} | {fmt(ntime)} |")
    lines += [
        "",
        "The detailed QA flags below are counted among pixels passing mandatory QA. They expose the product's stated per-pixel LST and emissivity error categories; they are reported as-is and are not extra filters in the support rule.",
        "",
        "| AOI | Period | LST QA good pixels | LST error ≤1 K | ≤2 K | ≤3 K | >3 K | Emissivity error ≤0.01 | ≤0.02 | ≤0.04 | >0.04 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for aoi in analysis["earth"].values():
        for period in ("day", "night"):
            aggregated = {"lst_error_k": {k: 0 for k in ("<=1", "<=2", "<=3", ">3")}, "emissivity_error": {k: 0 for k in ("<=0.01", "<=0.02", "<=0.04", ">0.04")}}
            good_total = 0
            for day in aoi["dates"]:
                flags = day["periods"][period]["qa_pixel_centre_counts"]["detailed_flags_for_mandatory_good_pixels"]
                good_total += day["periods"][period]["qa_pixel_centre_counts"]["good"]
                for family in aggregated:
                    for category in aggregated[family]:
                        aggregated[family][category] += flags[family][category]
            lst = aggregated["lst_error_k"]
            emis = aggregated["emissivity_error"]
            lines.append(f"| {aoi['label']} | {period} | {good_total} | {lst['<=1']} | {lst['<=2']} | {lst['<=3']} | {lst['>3']} | {emis['<=0.01']} | {emis['<=0.02']} | {emis['<=0.04']} | {emis['>0.04']} |")
    lines += [
        "",
        "The coverage denominator is candidate 2 km UTM cells whose centres lie inside the published K-017 AOI bounds and are classified as land by the referenced NASADEM SWBD tile. Day/night times are local solar times recorded per pixel. This sample does not normalize view angle, terrain shading, seasonal solar incidence, atmospheric state, or emissivity across the three land regions.",
        "",
        "## Moon — LRO Diviner TB3",
        "",
        "The polar GDR L2 maps below are two separate 27-day mapping cycles with exact PDS label start and stop times shown in the table. Each map is a radiance-derived channel-3 brightness temperature at 7.55–8.05 μm, not the MODIS retrieval or an emissivity-normalized kinetic temperature. A 2 km cell is supported when at least 80% of its native 240 m posting centres have TB3 in the PDS-described 10–450 K range, a positive count product and a present error estimate. Nominal posting is not called effective resolution.",
        "",
        "| Cycle interval | Candidate 2 km cells | Coverage-qualified cells | TB3 p50 (K) | Local solar time p50 (h) | Scaled count product p50 | Error estimate p50 (K) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for period, values in analysis["moon"]["periods"].items():
        t, lt, count, err = values["brightness_temperature_k"]["p50"], values["local_solar_time_hours"]["p50"], values["count_product_values"]["p50"], values["error_estimates_k"]["p50"]
        fmt = lambda value: "null" if value is None else f"{value:.1f}"
        start = values["cycle_start_utc"][:10]
        stop = values["cycle_stop_utc"][:10]
        lines.append(f"| {period} {start}–{stop} | {values['candidate_2km_cells']} | {values['coverage_qualified_2km_cells']} ({values['coverage_qualified_2km_cell_pct']:.1f}%) | {fmt(t)} | {fmt(lt)} | {fmt(count)} | {fmt(err)} |")
    lines += [
        "",
        "Night coverage is especially sparse in this single sampled cycle. These coverage-qualified counts describe valid map-posting density, not independent detector observations per 2 km cell. Diviner GDR maps are binned and averaged by 27-day LRO cycles, split into local-time day/night, and local time drifts across longitude within a cycle. The polar map’s 240 m posting must not be presented as 240 m independent thermal resolution; PDS documents its footprint handling but does not provide one effective-resolution number for this sample. This sample does not match solar incidence, shadow or seasonal illumination across the lunar profile.",
        "",
        "## Mars — MGS TES derived thermal inertia",
        "",
        "| Period | Candidate target cells at 2 km | Independently supported target cells | Source pixels in Jezero geometry | Direct pixels | Interpolated pixels | Direct thermal-inertia p50 (J/(m² K √s)) | Native posting (N–S × E–W, m) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for period, values in analysis["mars"]["periods"].items():
        q = values["thermal_inertia_j_m2_k_sqrt_s"]["p50"]
        size = values["source_pixel_size_at_profile_latitude_m"]
        lines.append(f"| {period} | {analysis['mars']['candidate_target_2km_cells']} | null | {values['native_source_pixels_inside_jezero_geometry']} | {values['direct_source_pixels']} | {values['interpolated_source_pixels']} | {'null' if q is None else f'{q:.1f}'} | {size['north_south_posting_m']:.0f} × {size['east_west_posting_m']:.0f} |")
    lines += [
        "",
        "The TES maps were derived from dayside or nightside bolometer surface-temperature observations over three Mars years (1999–2004), then infilled where the interpolation mask says so. The thermal-inertia inversion depends on observing time, season, albedo, surface pressure and dust opacity; PDS explicitly cautions that the model for this map product differs from the one used for the published TES bolometer tables. Only direct source pixels are summarized in the table. The Jezero target grid has 448 cells at 2 km; TES posts at roughly 2.8–3.0 km near Jezero, so this audit assigns no independent 2 km cell support. It does not duplicate or interpolate TES values onto the finer grid.",
        "",
        "## Reproduction and limits",
        "",
        "Run `uv run --group data python pipeline/experiments/thermal/run_feasibility.py --download-missing`. The script verifies every file against the manifest SHA-256 and size, reuses the K-017 NASADEM water mask, recomputes the measurements, and rewrites this report plus the JSON manifest. MODIS downloads use the local `EARTHDATA_TOKEN` through earthaccess only when a file is missing. This run also verified a fresh MODIS Earthdata download and a PDS byte-range crop against their pinned hashes. The token is never printed or stored.",
        "",
        "The sample is intentionally small: four daily dates for each of three Earth AOIs, one lunar day and one lunar night mapping cycle, and a 25 × 25 native TES byte-range window centered on Jezero. It is evidence about feasibility and QA, not a globally representative seasonal analysis. Source files remain outside Git under `data/raw/k047` and `data/raw/k017`.",
        "",
        "Sources, provider use terms and citation guidance are recorded in `data/manifests/thermal-feasibility.json`; unknown SPDX identifiers remain `null` rather than being invented.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--download-missing", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if args.download_missing:
        download_assets(manifest)
    verified = verify_all_assets(manifest)
    manifest["analysis"] = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "software": {"python": sys.version.split()[0], "numpy": np.__version__, "rasterio": rasterio.__version__, "pyhdf": package_version("pyhdf"), "pyproj": package_version("pyproj"), "earthaccess": package_version("earthaccess")},
        "code_sha256": sha256_file(Path(__file__).resolve()),
        "reference_manifest_sha256": {path: sha256_file(ROOT / path) for path in manifest["reference_manifests"]},
        "asset_verification": verified,
        "earth": analyse_earth(manifest),
        "moon": analyse_diviner(manifest),
        "mars": _mars_cell_area_stats(manifest),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(manifest), encoding="utf-8")
    print(f"Verified {verified['verified_file_count']} files ({verified['verified_bytes']} bytes); wrote {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
