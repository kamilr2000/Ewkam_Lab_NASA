"""Version-independent scoring primitives for the Terra Analog API.

This module scores each supplied pixel independently.  It does not aggregate
pixels into map cells, infer missing values, convert units, or choose a smaller
search scope.  Callers must supply every cell in the declared scope in batches.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
import math
from numbers import Real
from typing import Literal

import numpy as np
from pyproj import Geod


MeasurementScale = Literal["ratio", "interval"]
_SUPPORTED_SCALES = frozenset({"ratio", "interval"})
_QUALITY_FLAGS = frozenset(
    {"LOW_COVERAGE", "INTERPOLATED", "SOURCE_EDGE", "SYNTHETIC_FIXTURE"}
)
_EXCLUSION_REASONS = frozenset(
    {
        "missing_feature_value",
        "outside_mask",
        "outside_scope",
        "failed_quality",
        "invalid_geometry",
        "source_nodata",
        "unsupported_resolution",
    }
)
_EARTH_GEOD = Geod(ellps="WGS84")


@dataclass(frozen=True, slots=True)
class FeatureCriterion:
    """A numeric feature target and its relative importance in one analysis."""

    feature_id: str
    weight: float
    reference_interval: tuple[float, float]
    tolerance: float
    unit: str
    measurement_scale: str
    reference_source_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NormalizedCriterion:
    criterion: FeatureCriterion
    normalized_weight: float


@dataclass(frozen=True, slots=True)
class FeatureResult:
    feature_id: str
    value: float
    unit: str
    measurement_scale: str
    similarity_pct: float
    normalized_weight: float
    contribution_pct: float
    reference_interval: tuple[float, float]
    tolerance: float
    source_ids: tuple[str, ...]
    quality_flags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScoredPixel:
    pixel_id: str
    score_pct: float
    center: tuple[float, float] | None
    coverage_fraction: float
    quality_flags: tuple[str, ...]
    features: tuple[FeatureResult, ...]


@dataclass(frozen=True, slots=True)
class RankingResult:
    ranked_pixels: tuple[ScoredPixel, ...]
    total_pixels: int
    eligible_pixels: int
    excluded_by_reason: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class AreaRank:
    rank: int
    candidate_id: str
    representative_pixel: ScoredPixel
    nearest_selected_distance_km: float | None


@dataclass(frozen=True, slots=True)
class ScoringBatch:
    """Columnar measurements for one bounded chunk of candidate pixels.

    `validity` is an explicit per-feature mask.  If omitted for a present
    feature, finite values are considered valid.  A missing feature column or
    false validity mask is missing data; it is never interpreted as zero.

    `preexcluded` carries mutually exclusive upstream scope, mask, geometry,
    resolution, and QA masks. Every excluded row therefore has one explicit
    reason without allocating a Python string per pixel.
    """

    pixel_ids: Sequence[str]
    values: Mapping[str, Sequence[float] | np.ndarray]
    units: Mapping[str, str] = field(default_factory=dict)
    measurement_scales: Mapping[str, str] = field(default_factory=dict)
    source_ids: Mapping[str, Sequence[str]] = field(default_factory=dict)
    validity: Mapping[str, Sequence[bool] | np.ndarray] = field(default_factory=dict)
    quality_flags: Mapping[str, Sequence[Sequence[str]]] = field(default_factory=dict)
    preexcluded: Mapping[str, Sequence[bool] | np.ndarray] = field(default_factory=dict)
    longitude_deg: Sequence[float] | np.ndarray | None = None
    latitude_deg: Sequence[float] | np.ndarray | None = None


@dataclass(frozen=True, slots=True)
class ScoredBatch:
    """Vectorized score arrays. Ineligible scores and similarities are NaN."""

    pixel_ids: tuple[str, ...]
    scores_pct: np.ndarray
    eligible_mask: np.ndarray
    excluded_by_reason: Mapping[str, int]
    similarities_pct: Mapping[str, np.ndarray]
    normalized_criteria: tuple[NormalizedCriterion, ...]
    _batch: ScoringBatch = field(repr=False, compare=False)
    _values: Mapping[str, np.ndarray] = field(repr=False, compare=False)
    _centers: tuple[np.ndarray, np.ndarray] | None = field(
        repr=False, compare=False
    )

    def materialize(self, index: int) -> ScoredPixel:
        """Build one rich result row; scanners call this only for Top K rows."""

        if index < 0 or index >= len(self.pixel_ids):
            raise IndexError(index)
        if not bool(self.eligible_mask[index]):
            raise ValueError("Cannot materialize a pixel excluded from scoring")

        feature_results: list[FeatureResult] = []
        combined_quality_flags: set[str] = set()
        for normalized in self.normalized_criteria:
            criterion = normalized.criterion
            feature_id = criterion.feature_id
            raw_flags = self._batch.quality_flags.get(feature_id)
            flags = tuple(sorted(set(raw_flags[index]))) if raw_flags else ()
            combined_quality_flags.update(flags)

            dataset_sources = self._batch.source_ids.get(feature_id, ())
            sources = tuple(
                dict.fromkeys((*dataset_sources, *criterion.reference_source_ids))
            )
            similarity_pct = float(self.similarities_pct[feature_id][index])
            feature_results.append(
                FeatureResult(
                    feature_id=feature_id,
                    value=float(self._values[feature_id][index]),
                    unit=criterion.unit,
                    measurement_scale=criterion.measurement_scale,
                    similarity_pct=similarity_pct,
                    normalized_weight=normalized.normalized_weight,
                    contribution_pct=normalized.normalized_weight * similarity_pct,
                    reference_interval=criterion.reference_interval,
                    tolerance=criterion.tolerance,
                    source_ids=sources,
                    quality_flags=flags,
                )
            )

        center = None
        if self._centers is not None:
            center = (
                float(self._centers[0][index]),
                float(self._centers[1][index]),
            )
        return ScoredPixel(
            pixel_id=self.pixel_ids[index],
            score_pct=float(self.scores_pct[index]),
            center=center,
            coverage_fraction=1.0,
            quality_flags=tuple(sorted(combined_quality_flags)),
            features=tuple(feature_results),
        )


def normalize_criteria(
    criteria: Sequence[FeatureCriterion],
) -> tuple[NormalizedCriterion, ...]:
    """Validate targets and normalize positive weights once per analysis.

    A zero weight disables a criterion, matching METHODOLOGY.md. Negative or
    non-finite weights are errors. At least one active criterion is required.
    """

    if not criteria:
        raise ValueError("At least one feature criterion is required")
    if len(criteria) > 16:
        raise ValueError("At most 16 feature criteria are supported")

    seen: set[str] = set()
    active: list[FeatureCriterion] = []
    for criterion in criteria:
        feature_id = criterion.feature_id
        if not isinstance(feature_id, str) or not feature_id or len(feature_id) > 128:
            raise ValueError("feature_id must be a non-empty string of at most 128 characters")
        if feature_id in seen:
            raise ValueError(f"Duplicate feature_id: {feature_id}")
        seen.add(feature_id)

        weight = _finite_number(criterion.weight, f"weight for {feature_id}")
        if weight < 0 or weight > 1_000_000:
            raise ValueError("Feature weights must be between 0 and 1,000,000")

        interval = criterion.reference_interval
        if len(interval) != 2:
            raise ValueError(f"Reference interval for {feature_id} must have two values")
        lower = _finite_number(interval[0], f"lower reference bound for {feature_id}")
        upper = _finite_number(interval[1], f"upper reference bound for {feature_id}")
        if lower > upper:
            raise ValueError(f"Reference interval for {feature_id} is reversed")

        tolerance = _finite_number(criterion.tolerance, f"tolerance for {feature_id}")
        if tolerance <= 0:
            raise ValueError(f"Tolerance for {feature_id} must be positive")
        if not isinstance(criterion.unit, str) or not criterion.unit or len(criterion.unit) > 64:
            raise ValueError(f"Unit for {feature_id} must be a non-empty string")
        if criterion.measurement_scale not in _SUPPORTED_SCALES:
            raise ValueError(
                f"Linear interval similarity is only defined for ratio/interval scales; "
                f"{feature_id} uses {criterion.measurement_scale!r}"
            )

        reference_sources = _validate_source_ids(
            criterion.reference_source_ids, f"reference sources for {feature_id}"
        )
        if weight > 0:
            active.append(
                replace(
                    criterion,
                    weight=weight,
                    reference_interval=(lower, upper),
                    tolerance=tolerance,
                    reference_source_ids=reference_sources,
                )
            )

    if not active:
        raise ValueError("At least one criterion must have a positive weight")

    weight_sum = math.fsum(criterion.weight for criterion in active)
    if not math.isfinite(weight_sum) or weight_sum <= 0:
        raise ValueError("The sum of active feature weights must be finite and positive")
    return tuple(
        NormalizedCriterion(criterion, criterion.weight / weight_sum)
        for criterion in active
    )


def score_batch(
    batch: ScoringBatch,
    criteria: Sequence[FeatureCriterion],
) -> ScoredBatch:
    """Score every row in one batch using the linear interval function.

    For observed value x, reference interval [a, b], and tolerance t:
    `similarity = max(0, 1 - max(a - x, 0, x - b) / t)`.
    Incomplete or upstream-ineligible rows receive no score.
    """

    normalized = normalize_criteria(criteria)
    pixel_ids = _validate_pixel_ids(batch.pixel_ids)
    size = len(pixel_ids)
    values = _validate_value_columns(batch, size, normalized)
    centers = _validate_centers(batch.longitude_deg, batch.latitude_deg, size)
    base_eligible, exclusion_counts = _validate_base_eligibility(batch, size)

    eligible_mask = base_eligible.copy()
    missing_any = np.zeros(size, dtype=bool)
    scores = np.zeros(size, dtype=np.float64)
    similarities_pct: dict[str, np.ndarray] = {}

    for item in normalized:
        criterion = item.criterion
        feature_id = criterion.feature_id
        feature_values = values[feature_id]

        raw_validity = batch.validity.get(feature_id)
        if feature_id not in batch.values:
            valid = np.zeros(size, dtype=bool)
        elif raw_validity is None:
            valid = np.isfinite(feature_values)
        else:
            validity = np.asarray(raw_validity)
            if validity.ndim != 1 or len(validity) != size:
                raise ValueError(f"Validity mask for {feature_id} must match pixel_ids")
            if validity.dtype != np.dtype(bool):
                raise ValueError(f"Validity mask for {feature_id} must be boolean")
            valid = validity & np.isfinite(feature_values)

        missing_any |= base_eligible & ~valid
        lower, upper = criterion.reference_interval
        distance = np.maximum(np.maximum(lower - feature_values, 0.0), feature_values - upper)
        similarity = np.clip(1.0 - distance / criterion.tolerance, 0.0, 1.0)
        similarity[~valid] = np.nan
        similarities_pct[feature_id] = similarity * 100.0

        # Accumulate only valid rows. Rows missing any active feature are
        # invalidated below instead of receiving locally renormalized weights.
        scores[valid] += item.normalized_weight * similarity[valid]

    eligible_mask &= ~missing_any
    scores_pct = scores * 100.0
    scores_pct[~eligible_mask] = np.nan

    missing_count = int(np.count_nonzero(base_eligible & missing_any))
    if missing_count:
        exclusion_counts["missing_feature_value"] = missing_count
    return ScoredBatch(
        pixel_ids=pixel_ids,
        scores_pct=scores_pct,
        eligible_mask=eligible_mask,
        excluded_by_reason=dict(sorted(exclusion_counts.items())),
        similarities_pct=similarities_pct,
        normalized_criteria=normalized,
        _batch=batch,
        _values=values,
        _centers=centers,
    )


def rank_pixel_batches(
    batches: Iterable[ScoringBatch],
    criteria: Sequence[FeatureCriterion],
    *,
    top_k: int = 10,
) -> RankingResult:
    """Full-scan batches while retaining only the exact global Top K pixels.

    Every row in every supplied batch is scored or counted as excluded. Memory
    used for rich results is O(top_k); numeric arrays are bounded by the input
    batch size. The caller is responsible for supplying the complete declared
    scope exactly once and in a stable grid version.
    """

    _validate_top_k(top_k)
    normalized = normalize_criteria(criteria)
    top_pixels: list[ScoredPixel] = []
    exclusions: Counter[str] = Counter()
    total = 0
    eligible_total = 0

    for batch in batches:
        scored = score_batch(batch, tuple(item.criterion for item in normalized))
        total += len(scored.pixel_ids)
        eligible_total += int(np.count_nonzero(scored.eligible_mask))
        exclusions.update(scored.excluded_by_reason)

        indices = _top_indices(scored.scores_pct, scored.pixel_ids, top_k)
        candidates = [scored.materialize(index) for index in indices]
        top_pixels = sorted(
            (*top_pixels, *candidates), key=_ranking_key
        )[:top_k]

    if total != eligible_total + sum(exclusions.values()):
        raise RuntimeError("Scan coverage counts do not reconcile")
    return RankingResult(
        ranked_pixels=tuple(top_pixels),
        total_pixels=total,
        eligible_pixels=eligible_total,
        excluded_by_reason=dict(sorted(exclusions.items())),
    )


def select_distinct_areas(
    sorted_candidates: Iterable[ScoredPixel],
    *,
    min_distance_km: float,
    top_k: int = 10,
) -> tuple[AreaRank, ...]:
    """Greedily select spatially distinct representatives from a full sorted stream.

    `sorted_candidates` must contain all eligible scored pixels ordered by
    unrounded score descending, then pixel_id ascending. This function consumes
    candidates beyond the pixel Top K until it finds `top_k` representatives
    or exhausts the stream. K-008's bounded/external sorter supplies this stream;
    the ordinary `rank_pixel_batches` Top K output is intentionally insufficient.
    Distances are WGS84 geodesics in kilometres, including across the dateline.
    """

    _validate_top_k(top_k)
    distance_threshold = _finite_number(min_distance_km, "min_distance_km")
    if distance_threshold <= 0 or distance_threshold > 10_000:
        raise ValueError("min_distance_km must be greater than 0 and at most 10,000")

    selected: list[AreaRank] = []
    previous_key: tuple[float, str] | None = None
    for candidate in sorted_candidates:
        if not math.isfinite(candidate.score_pct) or not 0 <= candidate.score_pct <= 100:
            raise ValueError(f"Invalid score for pixel {candidate.pixel_id}")
        current_key = _ranking_key(candidate)
        if previous_key is not None and current_key < previous_key:
            raise ValueError("Candidates must be sorted by score descending, then pixel_id")
        previous_key = current_key

        if candidate.center is None:
            raise ValueError(f"Pixel {candidate.pixel_id} is missing Earth coordinates")
        longitude, latitude = _validate_coordinate(*candidate.center, candidate.pixel_id)

        nearest_distance_km: float | None = None
        if selected:
            nearest_distance_km = min(
                _geodesic_distance_km(
                    longitude,
                    latitude,
                    area.representative_pixel.center[0],  # type: ignore[index]
                    area.representative_pixel.center[1],  # type: ignore[index]
                )
                for area in selected
            )
            if nearest_distance_km < distance_threshold:
                continue

        rank = len(selected) + 1
        selected.append(
            AreaRank(
                rank=rank,
                candidate_id=candidate.pixel_id,
                representative_pixel=candidate,
                nearest_selected_distance_km=nearest_distance_km,
            )
        )
        if len(selected) == top_k:
            break
    return tuple(selected)


def _validate_value_columns(
    batch: ScoringBatch,
    size: int,
    normalized: tuple[NormalizedCriterion, ...],
) -> dict[str, np.ndarray]:
    converted: dict[str, np.ndarray] = {}
    for feature_id, raw_values in batch.values.items():
        array = np.asarray(raw_values)
        if array.ndim != 1 or len(array) != size:
            raise ValueError(f"Values for {feature_id} must match pixel_ids")
        if not np.issubdtype(array.dtype, np.number) or np.issubdtype(
            array.dtype, np.complexfloating
        ):
            raise ValueError(f"Values for {feature_id} must be real numeric values")
        converted[feature_id] = array.astype(np.float64, copy=False)

    for item in normalized:
        criterion = item.criterion
        feature_id = criterion.feature_id
        if feature_id not in converted:
            converted[feature_id] = np.full(size, np.nan, dtype=np.float64)
            continue
        if batch.units.get(feature_id) != criterion.unit:
            raise ValueError(
                f"Unit mismatch for {feature_id}: expected {criterion.unit!r}, "
                f"received {batch.units.get(feature_id)!r}"
            )
        if batch.measurement_scales.get(feature_id) != criterion.measurement_scale:
            raise ValueError(f"Measurement-scale mismatch for {feature_id}")
        _validate_source_ids(batch.source_ids.get(feature_id, ()), f"sources for {feature_id}")

    for feature_id, raw_mask in batch.validity.items():
        validity = np.asarray(raw_mask)
        if validity.ndim != 1 or len(validity) != size:
            raise ValueError(f"Validity mask for {feature_id} must match pixel_ids")
        if validity.dtype != np.dtype(bool):
            raise ValueError(f"Validity mask for {feature_id} must be boolean")

    for feature_id, rows in batch.quality_flags.items():
        if len(rows) != size:
            raise ValueError(f"Quality flags for {feature_id} must match pixel_ids")
        for row in rows:
            unknown = set(row) - _QUALITY_FLAGS
            if unknown:
                raise ValueError(
                    f"Unknown quality flag(s) for {feature_id}: {sorted(unknown)}"
                )
    return converted


def _validate_base_eligibility(
    batch: ScoringBatch, size: int
) -> tuple[np.ndarray, dict[str, int]]:
    eligible = np.ones(size, dtype=bool)
    exclusions: dict[str, int] = {}
    for reason, raw_mask in batch.preexcluded.items():
        if reason not in _EXCLUSION_REASONS:
            raise ValueError(f"Unknown exclusion reason: {reason}")
        mask = np.asarray(raw_mask)
        if mask.ndim != 1 or len(mask) != size:
            raise ValueError(f"Pre-exclusion mask for {reason} must match pixel_ids")
        if mask.dtype != np.dtype(bool):
            raise ValueError(f"Pre-exclusion mask for {reason} must be boolean")
        if np.any(mask & ~eligible):
            raise ValueError("Pre-exclusion reason masks must be mutually exclusive")
        count = int(np.count_nonzero(mask))
        if count:
            exclusions[reason] = count
        eligible &= ~mask
    return eligible, exclusions


def _validate_centers(
    longitudes: Sequence[float] | np.ndarray | None,
    latitudes: Sequence[float] | np.ndarray | None,
    size: int,
) -> tuple[np.ndarray, np.ndarray] | None:
    if longitudes is None and latitudes is None:
        return None
    if longitudes is None or latitudes is None:
        raise ValueError("Longitude and latitude arrays must be supplied together")
    raw_longitude = np.asarray(longitudes)
    raw_latitude = np.asarray(latitudes)
    for coordinate_values, label in (
        (raw_longitude, "longitude"),
        (raw_latitude, "latitude"),
    ):
        if not np.issubdtype(coordinate_values.dtype, np.number) or np.issubdtype(
            coordinate_values.dtype, np.complexfloating
        ):
            raise ValueError(f"{label} values must be real numeric values")
    longitude = raw_longitude.astype(np.float64, copy=False)
    latitude = raw_latitude.astype(np.float64, copy=False)
    if longitude.ndim != 1 or latitude.ndim != 1 or len(longitude) != size or len(latitude) != size:
        raise ValueError("Coordinate arrays must match pixel_ids")
    if not np.isfinite(longitude).all() or not np.isfinite(latitude).all():
        raise ValueError("Coordinates must be finite")
    if np.any(longitude < -180) or np.any(longitude > 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")
    if np.any(latitude < -90) or np.any(latitude > 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    return longitude, latitude


def _validate_pixel_ids(pixel_ids: Sequence[str]) -> tuple[str, ...]:
    if isinstance(pixel_ids, (str, bytes)):
        raise ValueError("pixel_ids must be a sequence of pixel ID strings")
    result = tuple(pixel_ids)
    if any(not isinstance(pixel_id, str) or not pixel_id or len(pixel_id) > 200 for pixel_id in result):
        raise ValueError("pixel_ids must be non-empty strings of at most 200 characters")
    if len(set(result)) != len(result):
        raise ValueError("pixel_ids must be unique within each batch")
    return result


def _validate_source_ids(source_ids: Sequence[str], label: str) -> tuple[str, ...]:
    if isinstance(source_ids, (str, bytes)):
        raise ValueError(f"{label} must be a sequence of source ID strings")
    if not source_ids:
        raise ValueError(f"At least one source ID is required for {label}")
    values = tuple(source_ids)
    if any(not isinstance(source_id, str) or not source_id or len(source_id) > 128 for source_id in values):
        raise ValueError(f"Source IDs for {label} must be non-empty strings of at most 128 characters")
    if len(set(values)) != len(values):
        raise ValueError(f"Source IDs for {label} must be unique")
    return values


def _finite_number(value: float, label: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite number")
    try:
        converted = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be a finite number") from error
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be a finite number")
    return converted


def _validate_top_k(top_k: int) -> None:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 10:
        raise ValueError("top_k must be an integer between 1 and 10")


def _top_indices(scores_pct: np.ndarray, pixel_ids: tuple[str, ...], top_k: int) -> list[int]:
    valid_indices = np.flatnonzero(np.isfinite(scores_pct))
    if valid_indices.size <= top_k:
        return sorted(valid_indices.tolist(), key=lambda index: (-float(scores_pct[index]), pixel_ids[index]))

    candidate_indices = valid_indices[
        np.argpartition(scores_pct[valid_indices], -top_k)[-top_k:]
    ]
    cutoff = float(np.min(scores_pct[candidate_indices]))
    better = valid_indices[scores_pct[valid_indices] > cutoff]
    tied = valid_indices[scores_pct[valid_indices] == cutoff]
    ties_needed = top_k - len(better)
    # argpartition does not define tie order. Select the lexical IDs explicitly
    # with NumPy so large all-equal score batches do not trigger a Python sort.
    id_keys = np.asarray(pixel_ids, dtype=str)
    tied_order = tied[np.argsort(id_keys[tied], kind="stable")[:ties_needed]]
    chosen = [*better.tolist(), *tied_order.tolist()]
    return sorted(chosen, key=lambda index: (-float(scores_pct[index]), pixel_ids[index]))


def _ranking_key(pixel: ScoredPixel) -> tuple[float, str]:
    return (-pixel.score_pct, pixel.pixel_id)


def _validate_coordinate(longitude: float, latitude: float, pixel_id: str) -> tuple[float, float]:
    longitude = _finite_number(longitude, f"longitude for {pixel_id}")
    latitude = _finite_number(latitude, f"latitude for {pixel_id}")
    if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
        raise ValueError(f"Coordinates for {pixel_id} are outside WGS84 longitude/latitude bounds")
    return longitude, latitude


def _geodesic_distance_km(
    longitude_a: float,
    latitude_a: float,
    longitude_b: float,
    latitude_b: float,
) -> float:
    distance_m = _EARTH_GEOD.inv(longitude_a, latitude_a, longitude_b, latitude_b)[2]
    return abs(float(distance_m)) / 1000.0
