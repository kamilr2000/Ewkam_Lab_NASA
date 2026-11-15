"""Load the versioned real profiles and regional Earth cell packages."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pyproj import Transformer


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATHS = (
    ROOT / "pipeline" / "profiles" / "mars-jezero-v1.json",
    ROOT / "pipeline" / "profiles" / "moon-south-polar-80s-v1.json",
)
MANIFEST_PATHS = (
    ROOT / "data" / "manifests" / "k005-earth-grid-atacama-andes.json",
    ROOT / "data" / "manifests" / "k005-earth-grid-hawaii-big-island.json",
    ROOT / "data" / "manifests" / "k005-earth-grid-himalaya.json",
)
EARTH_FEATURE_IDS = ("slope_deg", "roughness_m", "relief_m")


class DataIntegrityError(RuntimeError):
    """A tracked data package does not match its pinned manifest."""


@dataclass(frozen=True, slots=True)
class EarthCell:
    pixel_id: str
    row: int
    col: int
    center_lon: float
    center_lat: float
    area_km2: float
    geometry: dict[str, Any]
    land_fraction: float
    is_land: bool
    dem_valid: bool
    values: dict[str, float | None]
    slope_support_fraction: float
    window_land_fraction: float
    window_valid_fraction: float
    window_valid_count: int
    window_sample_count: int
    is_eligible_all_features: bool
    missing_reason: str | None

    @property
    def coverage_fraction(self) -> float:
        return min(
            self.slope_support_fraction,
            self.window_valid_fraction,
            self.window_land_fraction,
        )

    @property
    def quality_flags(self) -> tuple[str, ...]:
        return ("LOW_COVERAGE",) if self.coverage_fraction < 1.0 else ()


@dataclass(frozen=True, slots=True)
class EarthDataset:
    manifest_path: str
    manifest: dict[str, Any]
    region_id: str
    region_name: str
    region_geometry: dict[str, Any]
    cells: tuple[EarthCell, ...]
    cells_by_id: dict[str, EarthCell]

    @property
    def version(self) -> str:
        return self.manifest["dataset_version"]

    @property
    def grid_version(self) -> str:
        return self.manifest["grid"]["grid_version"]

    @property
    def model_version(self) -> str:
        return self.manifest["grid"]["model_version"]

    @property
    def measurements(self) -> dict[str, dict[str, Any]]:
        return {item["feature_id"]: item for item in self.manifest["measurements"]}


@dataclass(frozen=True, slots=True)
class DataRegistry:
    profiles: dict[str, dict[str, Any]]
    datasets: dict[str, EarthDataset]


def canonical_unit(unit: str) -> str:
    """Normalize equivalent unit labels without converting measured values."""
    return {"m": "meter", "meters": "meter", "metres": "meter"}.get(unit, unit)


@lru_cache(maxsize=1)
def load_registry() -> DataRegistry:
    """Load immutable profile files and verify each compressed output against SHA-256."""
    profiles: dict[str, dict[str, Any]] = {}
    for path in PROFILE_PATHS:
        raw = _read_json(path)
        profile = raw.get("profile")
        if (
            raw.get("contract_version") != "1.0.0"
            or raw.get("is_synthetic") is not False
            or not isinstance(profile, dict)
        ):
            raise DataIntegrityError(f"Invalid profile package: {path.name}")
        profile_id = profile.get("profile_id")
        if not isinstance(profile_id, str) or profile_id in profiles:
            raise DataIntegrityError(f"Missing or duplicate profile ID in {path.name}")
        profiles[profile_id] = raw

    datasets: dict[str, EarthDataset] = {}
    for path in MANIFEST_PATHS:
        dataset = _load_earth_dataset(path)
        if dataset.version in datasets:
            raise DataIntegrityError(f"Duplicate dataset version: {dataset.version}")
        datasets[dataset.version] = dataset
    return DataRegistry(profiles=profiles, datasets=datasets)


def _load_earth_dataset(manifest_path: Path) -> EarthDataset:
    manifest = _read_json(manifest_path)
    if manifest.get("contract_version") != "1.0.0" or manifest.get("is_synthetic") is not False:
        raise DataIntegrityError(f"Invalid real-data manifest: {manifest_path.name}")
    if manifest.get("role") != "earth_search" or manifest.get("body") != "earth":
        raise DataIntegrityError(f"Unexpected dataset role or body: {manifest_path.name}")

    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != 1:
        raise DataIntegrityError(f"Expected one output file in {manifest_path.name}")
    output = files[0]
    relative_path = output.get("path")
    if not isinstance(relative_path, str):
        raise DataIntegrityError(f"Missing output path in {manifest_path.name}")
    output_path = (ROOT / relative_path).resolve()
    if not output_path.is_relative_to(ROOT.resolve()) or not output_path.is_file():
        raise DataIntegrityError(f"Dataset output is missing or outside the repository: {relative_path}")

    digest = hashlib.sha256()
    size_bytes = 0
    with output_path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
            size_bytes += len(chunk)
    if size_bytes != output.get("size_bytes") or digest.hexdigest() != output.get("sha256"):
        raise DataIntegrityError(f"Dataset bytes do not match {manifest_path.name}")

    params = manifest.get("processing", {}).get("parameters", {})
    grid = manifest.get("grid", {})
    transform = params.get("grid_transform")
    metric_crs = params.get("metric_crs")
    if (
        not isinstance(transform, list)
        or len(transform) != 6
        or not isinstance(metric_crs, str)
    ):
        raise DataIntegrityError(f"Missing metric grid definition in {manifest_path.name}")
    transform = tuple(float(value) for value in transform)
    to_wgs84 = Transformer.from_crs(metric_crs, "EPSG:4326", always_xy=True)

    cells: list[EarthCell] = []
    cell_ids: set[str] = set()
    with gzip.open(output_path, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "pixel_id", "grid_row", "grid_col", "center_lon_deg", "center_lat_deg",
            "pixel_area_km2", "land_fraction_4x", "is_land_center", "dem_valid",
            *EARTH_FEATURE_IDS, "slope_support_fraction", "window_land_fraction",
            "window_valid_fraction", "window_valid_count", "window_sample_count",
            "is_eligible", "missing_reason",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise DataIntegrityError(f"Unexpected CSV columns in {relative_path}")
        for source_row in reader:
            pixel_id = source_row["pixel_id"]
            if not pixel_id or pixel_id in cell_ids:
                raise DataIntegrityError(f"Missing or duplicate pixel ID in {relative_path}")
            cell_ids.add(pixel_id)
            row = _parse_int(source_row["grid_row"], "grid_row")
            col = _parse_int(source_row["grid_col"], "grid_col")
            values = {feature_id: _parse_optional_float(source_row[feature_id], feature_id) for feature_id in EARTH_FEATURE_IDS}
            area_km2 = _parse_float(source_row["pixel_area_km2"], "pixel_area_km2")
            if area_km2 <= 0:
                raise DataIntegrityError(f"Non-positive pixel area for {pixel_id}")
            cells.append(
                EarthCell(
                    pixel_id=pixel_id,
                    row=row,
                    col=col,
                    center_lon=_parse_float(source_row["center_lon_deg"], "center_lon_deg"),
                    center_lat=_parse_float(source_row["center_lat_deg"], "center_lat_deg"),
                    area_km2=area_km2,
                    geometry=_cell_geometry(to_wgs84, transform, row, col),
                    land_fraction=_parse_fraction(source_row["land_fraction_4x"], "land_fraction_4x"),
                    is_land=_parse_bool(source_row["is_land_center"], "is_land_center"),
                    dem_valid=_parse_bool(source_row["dem_valid"], "dem_valid"),
                    values=values,
                    slope_support_fraction=_parse_fraction(source_row["slope_support_fraction"], "slope_support_fraction"),
                    window_land_fraction=_parse_fraction(source_row["window_land_fraction"], "window_land_fraction"),
                    window_valid_fraction=_parse_fraction(source_row["window_valid_fraction"], "window_valid_fraction"),
                    window_valid_count=_parse_int(source_row["window_valid_count"], "window_valid_count"),
                    window_sample_count=_parse_int(source_row["window_sample_count"], "window_sample_count"),
                    is_eligible_all_features=_parse_bool(source_row["is_eligible"], "is_eligible"),
                    missing_reason=source_row["missing_reason"] or None,
                )
            )

    if not cells:
        raise DataIntegrityError(f"Dataset contains no candidate cells: {relative_path}")
    coverage = manifest.get("spatial_coverage", {})
    eligible_count = sum(cell.is_eligible_all_features for cell in cells)
    if len(cells) != coverage.get("total_pixels") or eligible_count != coverage.get("eligible_pixels"):
        raise DataIntegrityError(f"CSV counts do not match {manifest_path.name}")
    if any(
        cell.is_eligible_all_features
        and (
            not cell.is_land
            or not cell.dem_valid
            or not all(value is not None for value in cell.values.values())
        )
        for cell in cells
    ):
        raise DataIntegrityError(f"Eligible cell is missing land or feature support in {relative_path}")

    bounds = coverage.get("bounds")
    if not isinstance(bounds, list) or len(bounds) != 4 or coverage.get("bounds_order") != ["min_x", "min_y", "max_x", "max_y"]:
        raise DataIntegrityError(f"Invalid WGS84 bounds in {manifest_path.name}")
    min_lon, min_lat, max_lon, max_lat = (float(value) for value in bounds)
    region_geometry = {
        "type": "Polygon",
        "coordinates": [[[min_lon, min_lat], [max_lon, min_lat], [max_lon, max_lat], [min_lon, max_lat], [min_lon, min_lat]]],
    }
    region_id = params.get("aoi_id")
    region_name = params.get("aoi_label")
    if not isinstance(region_id, str) or not isinstance(region_name, str):
        raise DataIntegrityError(f"Missing regional scope in {manifest_path.name}")
    return EarthDataset(
        manifest_path=relative_path,
        manifest=manifest,
        region_id=region_id,
        region_name=region_name,
        region_geometry=region_geometry,
        cells=tuple(cells),
        cells_by_id={cell.pixel_id: cell for cell in cells},
    )


def _cell_geometry(
    transformer: Transformer,
    transform: tuple[float, float, float, float, float, float],
    row: int,
    col: int,
) -> dict[str, Any]:
    a, b, c, d, e, f = transform
    ring: list[list[float]] = []
    for pixel_col, pixel_row in ((col, row), (col + 1, row), (col + 1, row + 1), (col, row + 1), (col, row)):
        x = c + pixel_col * a + pixel_row * b
        y = f + pixel_col * d + pixel_row * e
        lon, lat = transformer.transform(x, y)
        ring.append([float(lon), float(lat)])
    return {"type": "Polygon", "coordinates": [ring]}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataIntegrityError(f"Cannot read JSON package {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise DataIntegrityError(f"Expected JSON object in {path.name}")
    return value


def _parse_bool(raw: str, label: str) -> bool:
    if raw == "true":
        return True
    if raw == "false":
        return False
    raise DataIntegrityError(f"Invalid {label} boolean: {raw!r}")


def _parse_int(raw: str, label: str) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise DataIntegrityError(f"Invalid integer {label}: {raw!r}") from exc


def _parse_float(raw: str, label: str) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise DataIntegrityError(f"Invalid number {label}: {raw!r}") from exc
    if not math.isfinite(value):
        raise DataIntegrityError(f"Non-finite number {label}: {raw!r}")
    return value


def _parse_optional_float(raw: str, label: str) -> float | None:
    return None if raw == "" else _parse_float(raw, label)


def _parse_fraction(raw: str, label: str) -> float:
    value = _parse_float(raw, label)
    if not 0 <= value <= 1:
        raise DataIntegrityError(f"Fraction outside [0,1] for {label}: {value}")
    return value
