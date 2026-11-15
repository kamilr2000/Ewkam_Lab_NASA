"""Contract v1 catalog, regional scoring, analysis details and map aggregation."""

from __future__ import annotations

import base64
import binascii
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, replace
import json
import math
import time
from typing import Any, Iterable
from uuid import uuid4

import numpy as np

from apps.api.data_store import (
    EARTH_FEATURE_IDS,
    DataRegistry,
    EarthCell,
    EarthDataset,
    canonical_unit,
)
from apps.api.errors import ApiProblem
from apps.api.scoring.engine import (
    AreaRank,
    FeatureCriterion,
    NormalizedCriterion,
    RankingResult,
    ScoredPixel,
    ScoringBatch,
    normalize_criteria,
    rank_pixel_batches,
    score_batch,
    select_distinct_areas,
)


CONTRACT_VERSION = "1.0.0"
OVERVIEW_LEVEL = 8
ANALYSIS_TTL_SECONDS = 60 * 60
MAX_ANALYSES = 16
BATCH_SIZE = 512
_QUALITY_EXCLUSION_REASONS = {"insufficient_slope_support", "insufficient_window_support"}


@dataclass(frozen=True, slots=True)
class AnalysisSnapshot:
    analysis_id: str
    dataset: EarthDataset
    profile_response: dict[str, Any]
    body: str
    profile_id: str
    criteria: tuple[FeatureCriterion, ...]
    normalized_criteria: tuple[NormalizedCriterion, ...]
    result_mode: str
    top_k: int
    min_distance_km: float | None
    scored_by_id: dict[str, ScoredPixel]
    total_pixels: int
    eligible_pixels: int
    excluded_by_reason: dict[str, int]
    total_area_km2: float
    eligible_area_km2: float


@dataclass(slots=True)
class _TileAccumulator:
    total_count: int = 0
    valid_count: int = 0
    total_area_km2: float = 0.0
    eligible_area_km2: float = 0.0
    area_weighted_score_sum: float = 0.0
    max_score_pct: float | None = None
    max_pixel_id: str | None = None


_ANALYSES: OrderedDict[str, tuple[float, AnalysisSnapshot]] = OrderedDict()
_EXPIRED_ANALYSIS_IDS: set[str] = set()


def build_catalog(registry: DataRegistry) -> dict[str, Any]:
    profiles = [wrapper["profile"] for wrapper in registry.profiles.values()]
    profile_features: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        for feature in profile["features"]:
            profile_features.setdefault(feature["feature_id"], feature)

    earth_sources: dict[str, set[str]] = defaultdict(set)
    for dataset in registry.datasets.values():
        for measurement in dataset.manifest["measurements"]:
            earth_sources[measurement["feature_id"]].update(measurement["source_ids"])

    features = []
    for feature_id, feature in sorted(profile_features.items()):
        source_ids = set(feature["source_ids"])
        source_ids.update(earth_sources.get(feature_id, set()))
        features.append(
            {
                "feature_id": feature_id,
                "name": feature["name"],
                "description": feature["description"],
                "unit": feature["unit"],
                "measurement_scale": feature["measurement_scale"],
                "domain_id": "topography",
                "domain_label": "Topography",
                "availability": "available" if earth_sources.get(feature_id) else "unavailable",
                "is_proxy": feature["is_proxy"],
                "proxy_description": feature["proxy_description"],
                "source_ids": sorted(source_ids),
            }
        )

    datasets = []
    regions = []
    for dataset in sorted(registry.datasets.values(), key=lambda item: item.version):
        manifest = dataset.manifest
        datasets.append(
            {
                "dataset_version": dataset.version,
                "role": manifest["role"],
                "body": manifest["body"],
                "grid_version": dataset.grid_version,
                "model_version": dataset.model_version,
                "availability": "available",
                "coverage_description": (
                    f"Regional candidate cells for {dataset.region_name}; "
                    f"{manifest['spatial_coverage']['eligible_pixels']} of "
                    f"{manifest['spatial_coverage']['total_pixels']} cells meet the dataset's "
                    "three-feature eligibility rule."
                ),
                "manifest_path": dataset.manifest_path,
            }
        )
        regions.append(
            {
                "region_id": dataset.region_id,
                "name": dataset.region_name,
                "dataset_version": dataset.version,
                "availability": "available",
                "geometry": dataset.region_geometry,
                "mask_id": manifest["grid"]["mask_id"],
                "description": (
                    f"{manifest['processing']['parameters']['aoi_candidate_rule']} "
                    "Only this declared regional package is searchable."
                ),
            }
        )

    catalog_generated_at = max(
        dataset.manifest["generated_at"] for dataset in registry.datasets.values()
    )
    profile_summaries = [
        {
            "profile_id": profile["profile_id"],
            "name": profile["name"],
            "body": profile["body"],
            "region_name": profile["region"]["name"],
            "profile_version": profile["profile_version"],
            "availability": "available",
            "feature_ids": [feature["feature_id"] for feature in profile["features"]],
            "source_ids": profile["source_ids"],
        }
        for profile in profiles
    ]
    return {
        "contract_version": CONTRACT_VERSION,
        "catalog_version": "k007-regional-catalog-v1",
        "generated_at": catalog_generated_at,
        "is_synthetic": False,
        "datasets": datasets,
        "features": features,
        "profiles": profile_summaries,
        "search_regions": regions,
        "warnings": [
            {"code": "REGIONAL_COVERAGE", "message": "Searchable Earth data cover three declared regional AOIs; no global Earth search dataset is published."},
            {"code": "TOPOGRAPHY_ONLY", "message": "Available comparisons use slope, local roughness and local relief; no mineralogy or biological evidence is included."},
            {"code": "COARSE_RESOLUTION", "message": "Earth candidate cells have a nominal 2 km analytical resolution."},
        ],
        "limitations": [
            "The two planetary profiles represent Jezero crater on Mars and the source-covered lunar 80–90°S cap; neither represents its whole body.",
            "Earth search data are limited to Atacama/Andes, Big Island and the Himalayas; a global request is rejected rather than reduced to these regions.",
            "Earth outputs are real regional topographic measurements; similarity values are experimental comparisons against the declared profile intervals and tolerances.",
            "Qattara NASADEM validation is not an Earth search dataset in this API.",
        ],
    }


def get_profile(registry: DataRegistry, profile_id: str) -> dict[str, Any]:
    try:
        return registry.profiles[profile_id]
    except KeyError as exc:
        raise ApiProblem(404, "UNKNOWN_PROFILE", f"Unknown profile_id: {profile_id}") from exc


def get_manifest(registry: DataRegistry, dataset_version: str) -> dict[str, Any]:
    try:
        return registry.datasets[dataset_version].manifest
    except KeyError as exc:
        raise ApiProblem(404, "DATASET_VERSION_UNAVAILABLE", f"Unknown dataset_version: {dataset_version}") from exc


def run_search(registry: DataRegistry, request: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    if request["scope"]["type"] == "global":
        raise ApiProblem(
            409,
            "SCOPE_UNAVAILABLE",
            "Global Earth coverage is not published; choose an available regional scope.",
            details={"available_scope_type": "regional"},
        )

    dataset_version = request["dataset_version"]
    dataset = registry.datasets.get(dataset_version)
    if dataset is None:
        raise ApiProblem(404, "DATASET_VERSION_UNAVAILABLE", f"Unknown dataset_version: {dataset_version}")
    scope_region_id = request["scope"]["region_id"]
    if scope_region_id != dataset.region_id:
        raise ApiProblem(
            409,
            "SCOPE_UNAVAILABLE",
            "The requested region is not part of the selected immutable dataset version.",
            details={"requested_region_id": scope_region_id, "dataset_region_id": dataset.region_id},
        )

    profile_wrapper = get_profile(registry, request["profile_id"])
    profile = profile_wrapper["profile"]
    if request["body"] != profile["body"]:
        raise ApiProblem(422, "INCOMPATIBLE_FEATURE", "body does not match the selected planetary profile.")

    criteria = _build_criteria(request, profile, dataset)
    normalized = normalize_criteria(criteria)
    top_k = request["top_k"]
    ranking = rank_pixel_batches(_scoring_batches(dataset, criteria), criteria, top_k=top_k)
    scored_by_id = _score_all(dataset, criteria)
    if len(scored_by_id) != ranking.eligible_pixels:
        raise ApiProblem(503, "DATASET_UNAVAILABLE", "Scoring passes produced inconsistent eligible-pixel counts.")

    total_area = math.fsum(cell.area_km2 for cell in dataset.cells)
    eligible_area = math.fsum(dataset.cells_by_id[pixel_id].area_km2 for pixel_id in scored_by_id)
    analysis_id = str(uuid4())
    result_mode = request["result_mode"]
    min_distance = request.get("min_distance_km")
    snapshot = AnalysisSnapshot(
        analysis_id=analysis_id,
        dataset=dataset,
        profile_response=profile_wrapper,
        body=request["body"],
        profile_id=request["profile_id"],
        criteria=tuple(criteria),
        normalized_criteria=normalized,
        result_mode=result_mode,
        top_k=top_k,
        min_distance_km=min_distance,
        scored_by_id=scored_by_id,
        total_pixels=ranking.total_pixels,
        eligible_pixels=ranking.eligible_pixels,
        excluded_by_reason=dict(ranking.excluded_by_reason),
        total_area_km2=total_area,
        eligible_area_km2=eligible_area,
    )
    _store_analysis(snapshot)

    query_criteria = [
        {
            "feature_id": item.criterion.feature_id,
            "weight": item.criterion.weight,
            "normalized_weight": item.normalized_weight,
        }
        for item in normalized
    ]
    query = {
        "body": request["body"],
        "profile_id": request["profile_id"],
        "criteria": query_criteria,
        "scope": {"type": "regional", "region_id": dataset.region_id},
        "result_mode": result_mode,
        "top_k": top_k,
        "min_distance_km": min_distance,
        "area_selection_rule": "greedy_geodesic_representatives" if result_mode == "distinct_areas" else "none",
    }
    scope = {
        "type": "regional",
        "region_id": dataset.region_id,
        "region_name": dataset.region_name,
        "geometry": dataset.region_geometry,
        "mask_id": dataset.manifest["grid"]["mask_id"],
        "grid_version": dataset.grid_version,
        "description": (
            f"{dataset.manifest['processing']['parameters']['aoi_candidate_rule']} "
            "Regional bounds and candidate rule are retained; this response does not claim global coverage."
        ),
    }
    coverage = _coverage_payload(snapshot)
    response: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "dataset_version": dataset.version,
        "grid_version": dataset.grid_version,
        "model_version": dataset.model_version,
        "profile_version": profile["profile_version"],
        "analysis_id": analysis_id,
        "is_synthetic": False,
        "query": query,
        "elapsed_ms": max(0.0, (time.perf_counter() - started) * 1000.0),
        "scope": scope,
        "coverage": coverage,
        "map_cells": _aggregate_map_cells(snapshot, level=OVERVIEW_LEVEL),
        "warnings": _analysis_warnings(dataset),
    }
    if result_mode == "pixels":
        response["ranking"] = [
            _ranked_pixel_payload(pixel, index, dataset, scored_by_id)
            for index, pixel in enumerate(ranking.ranked_pixels, start=1)
        ]
    else:
        sorted_pixels = sorted(scored_by_id.values(), key=lambda pixel: (-pixel.score_pct, pixel.pixel_id))
        areas = select_distinct_areas(sorted_pixels, min_distance_km=min_distance, top_k=top_k)
        response["area_ranking"] = [_area_payload(area, dataset, scored_by_id) for area in areas]
    return response


def get_pixel_details(analysis_id: str, pixel_id: str) -> dict[str, Any]:
    snapshot = get_analysis(analysis_id)
    cell = snapshot.dataset.cells_by_id.get(pixel_id)
    if cell is None:
        raise ApiProblem(404, "NOT_FOUND", f"Unknown pixel_id for analysis: {pixel_id}")
    if not cell.is_land:
        raise ApiProblem(
            404,
            "NOT_FOUND",
            "The pixel is outside the independent land mask and has no Earth analog score.",
            details={"pixel_id": pixel_id, "reason": "outside_mask"},
        )

    scored = snapshot.scored_by_id.get(pixel_id)
    feature_payloads: list[dict[str, Any]] = []
    missing_reasons: set[str] = set()
    if scored is not None:
        feature_payloads = [
            {
                "feature_id": feature.feature_id,
                "value": feature.value,
                "unit": feature.unit,
                "measurement_scale": feature.measurement_scale,
                "similarity_pct": feature.similarity_pct,
                "normalized_weight": feature.normalized_weight,
                "contribution_pct": feature.contribution_pct,
                "reference_interval": list(feature.reference_interval),
                "tolerance": feature.tolerance,
                "source_ids": list(feature.source_ids),
                "missing_reason": None,
            }
            for feature in scored.features
        ]
    else:
        profile_features = {
            feature["feature_id"]: feature
            for feature in snapshot.profile_response["profile"]["features"]
        }
        earth_measurements = snapshot.dataset.measurements
        for normalized in snapshot.normalized_criteria:
            criterion = normalized.criterion
            feature = profile_features[criterion.feature_id]
            value = cell.values[criterion.feature_id]
            reason = _missing_reason(cell, criterion.feature_id, value)
            if reason is not None:
                missing_reasons.add(reason)
                similarity = None
                contribution = None
            else:
                distance = max(
                    feature["reference_interval"][0] - value,
                    0.0,
                    value - feature["reference_interval"][1],
                )
                similarity = max(0.0, min(1.0, 1.0 - distance / feature["tolerance"]["value"])) * 100.0
                contribution = normalized.normalized_weight * similarity
            source_ids = list(dict.fromkeys(
                [*earth_measurements[criterion.feature_id]["source_ids"], *feature["source_ids"]]
            ))
            feature_payloads.append(
                {
                    "feature_id": criterion.feature_id,
                    "value": value,
                    "unit": criterion.unit,
                    "measurement_scale": criterion.measurement_scale,
                    "similarity_pct": similarity,
                    "normalized_weight": normalized.normalized_weight,
                    "contribution_pct": contribution,
                    "reference_interval": list(criterion.reference_interval),
                    "tolerance": criterion.tolerance,
                    "source_ids": source_ids,
                    "missing_reason": reason,
                }
            )
    if scored is None and not missing_reasons:
        # A row with all active measurements but an exclusion mask is not expected
        # for land pixels; avoid returning a misleading zero or partial score.
        missing_reasons.add("failed_quality")

    return {
        "contract_version": CONTRACT_VERSION,
        "dataset_version": snapshot.dataset.version,
        "grid_version": snapshot.dataset.grid_version,
        "model_version": snapshot.dataset.model_version,
        "profile_version": snapshot.profile_response["profile"]["profile_version"],
        "analysis_id": snapshot.analysis_id,
        "is_synthetic": False,
        "result_mode": snapshot.result_mode,
        "pixel": {
            "pixel_id": cell.pixel_id,
            "score_pct": None if scored is None else scored.score_pct,
            "center": [cell.center_lon, cell.center_lat],
            "geometry": cell.geometry,
            "pixel_area_km2": cell.area_km2,
            "coverage_fraction": cell.coverage_fraction,
            "features": feature_payloads,
            "quality_flags": list(cell.quality_flags),
            "missing_reasons": sorted(missing_reasons),
        },
    }


def get_map_cells(
    analysis_id: str,
    *,
    bbox: tuple[float, float, float, float],
    level: int,
    limit: int,
    cursor: str | None,
) -> dict[str, Any]:
    snapshot = get_analysis(analysis_id)
    west, south, east, north = bbox
    if south > north:
        raise ApiProblem(422, "INVALID_QUERY", "bbox south must not exceed north.")
    if level < 0 or level > 30:
        raise ApiProblem(422, "INVALID_QUERY", "level must be between 0 and 30.")
    if limit < 1 or limit > 10_000:
        raise ApiProblem(413, "LIMIT_EXCEEDED", "limit must be between 1 and 10000.")

    cells = _aggregate_map_cells(snapshot, level=level, bbox=bbox)
    offset = _decode_cursor(cursor, analysis_id, bbox, level) if cursor else 0
    page = cells[offset : offset + limit]
    next_offset = offset + len(page)
    next_cursor = _encode_cursor(analysis_id, bbox, level, next_offset) if next_offset < len(cells) else None
    return {
        "contract_version": CONTRACT_VERSION,
        "dataset_version": snapshot.dataset.version,
        "grid_version": snapshot.dataset.grid_version,
        "model_version": snapshot.dataset.model_version,
        "profile_version": snapshot.profile_response["profile"]["profile_version"],
        "analysis_id": analysis_id,
        "is_synthetic": False,
        "query": {"bbox": list(bbox), "level": level, "limit": limit},
        "map_cells": page,
        "next_cursor": next_cursor,
    }


def get_analysis(analysis_id: str) -> AnalysisSnapshot:
    now = time.monotonic()
    _prune_analyses(now)
    record = _ANALYSES.get(analysis_id)
    if record is None:
        if analysis_id in _EXPIRED_ANALYSIS_IDS:
            raise ApiProblem(410, "ANALYSIS_EXPIRED", "The frozen analysis expired and cannot be replaced silently.")
        raise ApiProblem(404, "NOT_FOUND", f"Unknown analysis_id: {analysis_id}")
    _ANALYSES.move_to_end(analysis_id)
    return record[1]


def _store_analysis(snapshot: AnalysisSnapshot) -> None:
    now = time.monotonic()
    _prune_analyses(now)
    _ANALYSES[snapshot.analysis_id] = (now, snapshot)
    _ANALYSES.move_to_end(snapshot.analysis_id)
    while len(_ANALYSES) > MAX_ANALYSES:
        expired_id, _ = _ANALYSES.popitem(last=False)
        _EXPIRED_ANALYSIS_IDS.add(expired_id)
    if len(_EXPIRED_ANALYSIS_IDS) > 256:
        _EXPIRED_ANALYSIS_IDS.pop()


def _prune_analyses(now: float) -> None:
    expired = [
        analysis_id
        for analysis_id, (created, _) in _ANALYSES.items()
        if now - created > ANALYSIS_TTL_SECONDS
    ]
    for analysis_id in expired:
        _ANALYSES.pop(analysis_id, None)
        _EXPIRED_ANALYSIS_IDS.add(analysis_id)


def _build_criteria(request: dict[str, Any], profile: dict[str, Any], dataset: EarthDataset) -> list[FeatureCriterion]:
    profile_features = {feature["feature_id"]: feature for feature in profile["features"]}
    earth_features = dataset.measurements
    criteria: list[FeatureCriterion] = []
    for item in request["criteria"]:
        feature_id = item["feature_id"]
        feature = profile_features.get(feature_id)
        measurement = earth_features.get(feature_id)
        if feature is None:
            raise ApiProblem(422, "INCOMPATIBLE_FEATURE", f"Feature {feature_id!r} is not part of profile {profile['profile_id']}.")
        if measurement is None:
            raise ApiProblem(422, "INCOMPATIBLE_FEATURE", f"Feature {feature_id!r} is not measured in dataset {dataset.version}.")
        profile_unit = canonical_unit(feature["unit"])
        earth_unit = canonical_unit(measurement["unit"])
        if profile_unit != earth_unit or feature["measurement_scale"] != measurement["measurement_scale"]:
            raise ApiProblem(
                422,
                "INCOMPATIBLE_FEATURE",
                f"Feature {feature_id!r} has incompatible units or measurement scales in the selected profile and dataset.",
                details={"profile_unit": feature["unit"], "earth_unit": measurement["unit"]},
            )
        criteria.append(
            FeatureCriterion(
                feature_id=feature_id,
                weight=float(item["weight"]),
                reference_interval=tuple(float(value) for value in feature["reference_interval"]),
                tolerance=float(feature["tolerance"]["value"]),
                unit=feature["unit"],
                measurement_scale=feature["measurement_scale"],
                reference_source_ids=tuple(feature["source_ids"]),
            )
        )
    return criteria


def _scoring_batches(dataset: EarthDataset, criteria: Iterable[FeatureCriterion]) -> Iterable[ScoringBatch]:
    feature_ids = tuple(criterion.feature_id for criterion in criteria)
    measurements = dataset.measurements
    for start in range(0, len(dataset.cells), BATCH_SIZE):
        cells = dataset.cells[start : start + BATCH_SIZE]
        values = {
            feature_id: np.asarray(
                [np.nan if cell.values[feature_id] is None else cell.values[feature_id] for cell in cells],
                dtype=np.float64,
            )
            for feature_id in feature_ids
        }
        validity = {feature_id: np.isfinite(column) for feature_id, column in values.items()}
        preexcluded_rows: dict[str, list[bool]] = defaultdict(list)
        reasons: list[str | None] = []
        for cell in cells:
            reason = _row_exclusion_reason(cell, feature_ids)
            reasons.append(reason)
            for known_reason in ("outside_mask", "source_nodata", "failed_quality"):
                preexcluded_rows[known_reason].append(reason == known_reason)
        preexcluded = {
            reason: np.asarray(mask, dtype=bool)
            for reason, mask in preexcluded_rows.items()
            if any(mask)
        }
        quality_flags = {
            feature_id: [list(cell.quality_flags) for cell in cells]
            for feature_id in feature_ids
        }
        yield ScoringBatch(
            pixel_ids=[cell.pixel_id for cell in cells],
            values=values,
            units={feature_id: canonical_unit(measurements[feature_id]["unit"]) for feature_id in feature_ids},
            measurement_scales={feature_id: measurements[feature_id]["measurement_scale"] for feature_id in feature_ids},
            source_ids={feature_id: tuple(measurements[feature_id]["source_ids"]) for feature_id in feature_ids},
            validity=validity,
            quality_flags=quality_flags,
            preexcluded=preexcluded,
            longitude_deg=np.asarray([cell.center_lon for cell in cells], dtype=np.float64),
            latitude_deg=np.asarray([cell.center_lat for cell in cells], dtype=np.float64),
        )


def _row_exclusion_reason(cell: EarthCell, feature_ids: tuple[str, ...]) -> str | None:
    if not cell.is_land:
        return "outside_mask"
    if not cell.dem_valid:
        return "source_nodata"
    missing_active = [feature_id for feature_id in feature_ids if cell.values[feature_id] is None]
    if not missing_active:
        return None
    if cell.missing_reason in _QUALITY_EXCLUSION_REASONS:
        return "failed_quality"
    return None


def _score_all(dataset: EarthDataset, criteria: list[FeatureCriterion]) -> dict[str, ScoredPixel]:
    scored_by_id: dict[str, ScoredPixel] = {}
    for batch in _scoring_batches(dataset, criteria):
        scored = score_batch(batch, criteria)
        for index, eligible in enumerate(scored.eligible_mask):
            if eligible:
                pixel = scored.materialize(index)
                cell = dataset.cells_by_id[pixel.pixel_id]
                scored_by_id[pixel.pixel_id] = replace(pixel, coverage_fraction=cell.coverage_fraction)
    return scored_by_id


def _coverage_payload(snapshot: AnalysisSnapshot) -> dict[str, Any]:
    if snapshot.total_area_km2 <= 0:
        fraction: float | None = None
        reason = "empty_scope"
    else:
        fraction = snapshot.eligible_area_km2 / snapshot.total_area_km2
        reason = None if snapshot.eligible_pixels else "all_cells_excluded"
    return {
        "total_pixels": snapshot.total_pixels,
        "eligible_pixels": snapshot.eligible_pixels,
        "excluded_by_reason": snapshot.excluded_by_reason,
        "total_area_km2": snapshot.total_area_km2,
        "eligible_area_km2": snapshot.eligible_area_km2,
        "eligible_area_fraction": fraction,
        "no_data_reason": reason,
    }


def _ranked_pixel_payload(
    pixel: ScoredPixel,
    rank: int,
    dataset: EarthDataset,
    scored_by_id: dict[str, ScoredPixel],
) -> dict[str, Any]:
    cell = dataset.cells_by_id[pixel.pixel_id]
    pixel = scored_by_id[pixel.pixel_id]
    return {
        "rank": rank,
        "pixel_id": pixel.pixel_id,
        "score_pct": pixel.score_pct,
        "center": [cell.center_lon, cell.center_lat],
        "geometry": cell.geometry,
        "pixel_area_km2": cell.area_km2,
        "coverage_fraction": cell.coverage_fraction,
        "quality_flags": list(cell.quality_flags),
        "features": [_feature_result_payload(feature) for feature in pixel.features],
    }


def _area_payload(area: AreaRank, dataset: EarthDataset, scored_by_id: dict[str, ScoredPixel]) -> dict[str, Any]:
    representative = _ranked_pixel_payload(area.representative_pixel, area.rank, dataset, scored_by_id)
    representative.pop("rank")
    return {
        "rank": area.rank,
        "candidate_id": area.candidate_id,
        "representative_pixel": representative,
        "nearest_selected_distance_km": area.nearest_selected_distance_km,
    }


def _feature_result_payload(feature: Any) -> dict[str, Any]:
    return {
        "feature_id": feature.feature_id,
        "value": feature.value,
        "unit": feature.unit,
        "measurement_scale": feature.measurement_scale,
        "similarity_pct": feature.similarity_pct,
        "normalized_weight": feature.normalized_weight,
        "contribution_pct": feature.contribution_pct,
        "reference_interval": list(feature.reference_interval),
        "tolerance": feature.tolerance,
        "source_ids": list(feature.source_ids),
        "quality_flags": list(feature.quality_flags),
    }


def _missing_reason(cell: EarthCell, feature_id: str, value: float | None) -> str | None:
    if value is not None:
        return None
    if not cell.dem_valid or cell.missing_reason == "dem_nodata":
        return "source_nodata"
    if cell.missing_reason in _QUALITY_EXCLUSION_REASONS:
        return "failed_quality"
    if cell.missing_reason == "unsupported_resolution":
        return "unsupported_resolution"
    return "missing_feature_value"


def _analysis_warnings(dataset: EarthDataset) -> list[dict[str, str]]:
    return [
        {
            "code": "REGIONAL_COVERAGE",
            "message": f"Results cover only {dataset.region_name}; they do not establish a global Earth ranking.",
        },
        {
            "code": "TOPOGRAPHY_ONLY",
            "message": "The comparison uses slope, local roughness and local relief; it does not measure mineralogy or life.",
        },
        {
            "code": "COARSE_RESOLUTION",
            "message": "Earth analysis cells have a nominal 2 km resolution and derive from approximately 0.42–0.46 km ETOPO posting in this AOI.",
        },
    ]


def _aggregate_map_cells(
    snapshot: AnalysisSnapshot,
    *,
    level: int,
    bbox: tuple[float, float, float, float] | None = None,
) -> list[dict[str, Any]]:
    if not 0 <= level <= 30:
        raise ApiProblem(422, "INVALID_QUERY", "level must be between 0 and 30.")
    tiles: dict[tuple[int, int], _TileAccumulator] = defaultdict(_TileAccumulator)
    for cell in snapshot.dataset.cells:
        x, y = _tile_xy(cell.center_lon, cell.center_lat, level)
        accumulator = tiles[(x, y)]
        accumulator.total_count += 1
        accumulator.total_area_km2 += cell.area_km2
        pixel = snapshot.scored_by_id.get(cell.pixel_id)
        if pixel is None:
            continue
        accumulator.valid_count += 1
        accumulator.eligible_area_km2 += cell.area_km2
        accumulator.area_weighted_score_sum += pixel.score_pct * cell.area_km2
        if (
            accumulator.max_score_pct is None
            or pixel.score_pct > accumulator.max_score_pct
            or (pixel.score_pct == accumulator.max_score_pct and pixel.pixel_id < (accumulator.max_pixel_id or ""))
        ):
            accumulator.max_score_pct = pixel.score_pct
            accumulator.max_pixel_id = pixel.pixel_id

    result = []
    for (x, y), accumulator in tiles.items():
        tile_bounds = _tile_bounds(x, y, level)
        if bbox is not None and not _bbox_intersects(tile_bounds, bbox):
            continue
        cell_id = f"{level}/{x}/{y}"
        valid_count = accumulator.valid_count
        result.append(
            {
                "cell_id": cell_id,
                "level": level,
                "geometry": _tile_geometry(tile_bounds),
                "max_score_pct": accumulator.max_score_pct,
                "mean_score_pct": (
                    accumulator.area_weighted_score_sum / accumulator.eligible_area_km2
                    if accumulator.eligible_area_km2 > 0
                    else None
                ),
                "max_pixel_id": accumulator.max_pixel_id,
                "valid_pixel_count": valid_count,
                "total_pixel_count": accumulator.total_count,
                "coverage_fraction": valid_count / accumulator.total_count if accumulator.total_count else 0.0,
                "missing_reason": None if valid_count else "no_eligible_pixels",
            }
        )
    return sorted(result, key=lambda item: (int(item["cell_id"].split("/")[1]), int(item["cell_id"].split("/")[2])))


def _tile_xy(longitude: float, latitude: float, level: int) -> tuple[int, int]:
    n = 1 << level
    lon = min(180.0 - 1e-12, max(-180.0, longitude))
    lat = min(85.0511287798066, max(-85.0511287798066, latitude))
    x = int((lon + 180.0) / 360.0 * n)
    lat_radians = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_radians)) / math.pi) / 2.0 * n)
    return min(n - 1, max(0, x)), min(n - 1, max(0, y))


def _tile_bounds(x: int, y: int, level: int) -> tuple[float, float, float, float]:
    n = 1 << level
    west = x / n * 360.0 - 180.0
    east = (x + 1) / n * 360.0 - 180.0
    north = math.degrees(math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n))))
    south = math.degrees(math.atan(math.sinh(math.pi * (1.0 - 2.0 * (y + 1) / n))))
    return west, south, east, north


def _tile_geometry(bounds: tuple[float, float, float, float]) -> dict[str, Any]:
    west, south, east, north = bounds
    return {
        "type": "Polygon",
        "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]],
    }


def _bbox_intersects(
    tile: tuple[float, float, float, float],
    query: tuple[float, float, float, float],
) -> bool:
    tile_west, tile_south, tile_east, tile_north = tile
    west, south, east, north = query
    if tile_north < south or tile_south > north:
        return False
    query_intervals = [(west, east)] if west <= east else [(west, 180.0), (-180.0, east)]
    return any(tile_east >= query_west and tile_west <= query_east for query_west, query_east in query_intervals)


def _encode_cursor(analysis_id: str, bbox: tuple[float, float, float, float], level: int, offset: int) -> str:
    raw = json.dumps(
        {"analysis_id": analysis_id, "bbox": list(bbox), "level": level, "offset": offset},
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_cursor(
    cursor: str | None,
    analysis_id: str,
    bbox: tuple[float, float, float, float],
    level: int,
) -> int:
    if cursor is None:
        return 0
    try:
        padding = "=" * ((4 - len(cursor) % 4) % 4)
        value = json.loads(base64.urlsafe_b64decode(cursor + padding))
    except (ValueError, TypeError, binascii.Error, json.JSONDecodeError) as exc:
        raise ApiProblem(422, "INVALID_QUERY", "cursor is malformed.") from exc
    if (
        not isinstance(value, dict)
        or value.get("analysis_id") != analysis_id
        or value.get("bbox") != list(bbox)
        or value.get("level") != level
        or not isinstance(value.get("offset"), int)
        or value["offset"] < 0
    ):
        raise ApiProblem(422, "INVALID_QUERY", "cursor does not match this analysis, bbox and level.")
    return value["offset"]
