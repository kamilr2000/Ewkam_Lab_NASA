from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from apps.api.scoring import (
    FeatureCriterion,
    ScoredPixel,
    ScoringBatch,
    normalize_criteria,
    rank_pixel_batches,
    score_batch,
    select_distinct_areas,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "contracts"
    / "fixtures"
    / "hotspot-regression.json"
)


def make_criterion(
    feature_id: str,
    weight: float = 1.0,
    interval: tuple[float, float] = (0.0, 0.0),
    tolerance: float = 1.0,
    *,
    unit: str = "1",
    scale: str = "ratio",
    sources: tuple[str, ...] = ("synthetic-profile",),
) -> FeatureCriterion:
    return FeatureCriterion(
        feature_id=feature_id,
        weight=weight,
        reference_interval=interval,
        tolerance=tolerance,
        unit=unit,
        measurement_scale=scale,
        reference_source_ids=sources,
    )


def make_batch(
    pixel_ids: list[str],
    values: dict[str, list[float | None]],
    *,
    units: dict[str, str] | None = None,
    scales: dict[str, str] | None = None,
    source_ids: dict[str, list[str]] | None = None,
    validity: dict[str, list[bool]] | None = None,
    quality_flags: dict[str, list[list[str]]] | None = None,
    preexcluded: dict[str, list[bool]] | None = None,
    longitude_deg: list[float] | None = None,
    latitude_deg: list[float] | None = None,
) -> ScoringBatch:
    array_values = {
        feature_id: np.array(
            [np.nan if value is None else value for value in column], dtype=np.float64
        )
        for feature_id, column in values.items()
    }
    array_validity = {
        feature_id: np.asarray(mask, dtype=bool)
        for feature_id, mask in (validity or {}).items()
    }
    return ScoringBatch(
        pixel_ids=pixel_ids,
        values=array_values,
        units=units or {feature_id: "1" for feature_id in values},
        measurement_scales=scales or {feature_id: "ratio" for feature_id in values},
        source_ids=source_ids or {feature_id: ["synthetic-earth"] for feature_id in values},
        validity=array_validity,
        quality_flags=quality_flags or {},
        preexcluded={
            reason: np.asarray(mask, dtype=bool)
            for reason, mask in (preexcluded or {}).items()
        },
        longitude_deg=longitude_deg,
        latitude_deg=latitude_deg,
    )


def batch_slice(batch: ScoringBatch, start: int, stop: int) -> ScoringBatch:
    def slice_rows(rows: Any) -> Any:
        return None if rows is None else rows[start:stop]

    return ScoringBatch(
        pixel_ids=batch.pixel_ids[start:stop],
        values={key: value[start:stop] for key, value in batch.values.items()},
        units=batch.units,
        measurement_scales=batch.measurement_scales,
        source_ids=batch.source_ids,
        validity={key: value[start:stop] for key, value in batch.validity.items()},
        quality_flags={key: value[start:stop] for key, value in batch.quality_flags.items()},
        preexcluded={key: value[start:stop] for key, value in batch.preexcluded.items()},
        longitude_deg=slice_rows(batch.longitude_deg),
        latitude_deg=slice_rows(batch.latitude_deg),
    )


def load_hotspot_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_all_published_hotspot_regressions_match_the_engine() -> None:
    fixture = load_hotspot_fixture()
    assert fixture["is_synthetic"] is True

    for case in fixture["cases"]:
        features = case["features"]
        criteria = [
            make_criterion(
                feature_id,
                case["weights"][feature_id],
                tuple(target["interval"]),
                target["tolerance"],
            )
            for feature_id, target in features.items()
        ]
        pixels = case["pixels"]
        feature_ids = list(features)
        batch = make_batch(
            [pixel["pixel_id"] for pixel in pixels],
            {
                feature_id: [pixel["values"].get(feature_id) for pixel in pixels]
                for feature_id in feature_ids
            },
            validity={
                feature_id: [
                    pixel["values"].get(feature_id) is not None for pixel in pixels
                ]
                for feature_id in feature_ids
            },
            quality_flags={
                feature_id: [["SYNTHETIC_FIXTURE"] for _ in pixels]
                for feature_id in feature_ids
            },
        )

        result = rank_pixel_batches([batch], criteria, top_k=10)
        expected = case["expected"]
        assert [pixel.pixel_id for pixel in result.ranked_pixels] == expected[
            "ranked_pixel_ids"
        ], case["id"]
        if expected["top_score_pct"] is None:
            assert result.ranked_pixels == ()
        else:
            assert result.ranked_pixels[0].score_pct == pytest.approx(
                expected["top_score_pct"]
            ), case["id"]

        assert result.total_pixels == len(pixels)
        assert result.eligible_pixels == len(expected["ranked_pixel_ids"])
        assert result.total_pixels == result.eligible_pixels + sum(
            result.excluded_by_reason.values()
        )
        for scored_pixel in result.ranked_pixels:
            assert sum(feature.contribution_pct for feature in scored_pixel.features) == pytest.approx(
                scored_pixel.score_pct
            )
            assert "SYNTHETIC_FIXTURE" in scored_pixel.quality_flags

        # Verify the fixture's map expectations from already-combined pixel
        # scores. The engine itself deliberately does not aggregate map cells.
        expected_map = expected["map_cells"]
        pixel_to_cell = {pixel["pixel_id"]: pixel["map_cell_id"] for pixel in pixels}
        for cell_id, cell_expected in expected_map.items():
            cell_scores = [
                pixel.score_pct
                for pixel in result.ranked_pixels
                if pixel_to_cell[pixel.pixel_id] == cell_id
            ]
            if cell_expected["max_score_pct"] is None:
                assert cell_scores == []
                continue
            assert max(cell_scores) == pytest.approx(cell_expected["max_score_pct"])
            assert math.fsum(cell_scores) / len(cell_scores) == pytest.approx(
                cell_expected["mean_score_pct"]
            )
            max_pixel_id = min(
                pixel.pixel_id
                for pixel in result.ranked_pixels
                if pixel_to_cell[pixel.pixel_id] == cell_id
                and pixel.score_pct == max(cell_scores)
            )
            assert max_pixel_id == cell_expected["max_pixel_id"]


def test_linear_interval_similarity_and_weighted_contributions() -> None:
    criteria = [
        make_criterion("slope_deg", 1, (0, 0), 1, unit="deg"),
        make_criterion("relief_m", 3, (0, 0), 1, unit="m"),
    ]
    batch = make_batch(
        ["pixel-1", "pixel-2", "pixel-3"],
        {"slope_deg": [1, 0, 0.5], "relief_m": [0, 1, 0]},
        units={"slope_deg": "deg", "relief_m": "m"},
    )

    result = rank_pixel_batches([batch], criteria)
    first, second, third = result.ranked_pixels
    assert [pixel.pixel_id for pixel in result.ranked_pixels] == [
        "pixel-3",
        "pixel-1",
        "pixel-2",
    ]
    assert first.score_pct == pytest.approx(87.5)
    assert [feature.normalized_weight for feature in first.features] == pytest.approx(
        [0.25, 0.75]
    )
    assert [feature.contribution_pct for feature in first.features] == pytest.approx(
        [12.5, 75]
    )
    assert sum(feature.contribution_pct for feature in first.features) == pytest.approx(
        first.score_pct
    )
    assert second.score_pct == pytest.approx(75)
    assert third.score_pct == pytest.approx(25)


def test_missing_active_feature_excludes_without_weight_renormalization() -> None:
    criteria = [make_criterion("a", 1), make_criterion("b", 1)]
    batch = make_batch(
        ["missing-b", "complete"],
        {"a": [0, 0.3], "b": [None, 0.3]},
        validity={"a": [True, True], "b": [False, True]},
    )

    scored = score_batch(batch, criteria)
    assert scored.eligible_mask.tolist() == [False, True]
    assert np.isnan(scored.scores_pct[0])
    assert scored.excluded_by_reason == {"missing_feature_value": 1}

    result = rank_pixel_batches([batch], criteria)
    assert [pixel.pixel_id for pixel in result.ranked_pixels] == ["complete"]
    assert result.ranked_pixels[0].score_pct == pytest.approx(70)
    assert result.excluded_by_reason == {"missing_feature_value": 1}
    assert result.total_pixels == result.eligible_pixels + sum(
        result.excluded_by_reason.values()
    )


def test_zero_weight_disables_a_feature_but_all_zero_weights_fail() -> None:
    criteria = [make_criterion("active", 2), make_criterion("disabled", 0)]
    normalized = normalize_criteria(criteria)
    assert [item.criterion.feature_id for item in normalized] == ["active"]
    assert normalized[0].normalized_weight == pytest.approx(1)

    batch = make_batch(["p1"], {"active": [0], "disabled": [None]})
    result = rank_pixel_batches([batch], criteria)
    assert result.ranked_pixels[0].score_pct == 100
    assert [feature.feature_id for feature in result.ranked_pixels[0].features] == [
        "active"
    ]

    with pytest.raises(ValueError, match="positive weight"):
        normalize_criteria([make_criterion("a", 0)])


def test_single_feature_scores_match_interval_boundaries_and_clipping() -> None:
    criterion = make_criterion("x", interval=(10, 20), tolerance=5)
    batch = make_batch(
        ["lower", "upper", "near-lower", "near-upper", "at-tolerance", "past"],
        {"x": [10, 20, 9.999, 20.001, 25, 40]},
    )

    scored = score_batch(batch, [criterion])
    assert scored.scores_pct.tolist() == pytest.approx(
        [100, 100, 99.98, 99.98, 0, 0]
    )


def test_top_k_is_unrounded_and_ties_use_pixel_id_across_batches() -> None:
    criterion = make_criterion("x", interval=(0, 0), tolerance=1)
    batch = make_batch(
        ["z-slightly-better", "a-slightly-worse", "tie-z", "tie-a"],
        {"x": [0.499999999, 0.5, 0.5, 0.5]},
    )
    all_at_once = rank_pixel_batches([batch], [criterion], top_k=4)
    by_one = rank_pixel_batches(
        [batch_slice(batch, index, index + 1) for index in range(4)],
        [criterion],
        top_k=4,
    )
    assert [pixel.pixel_id for pixel in all_at_once.ranked_pixels] == [
        "z-slightly-better",
        "a-slightly-worse",
        "tie-a",
        "tie-z",
    ]
    assert [pixel.pixel_id for pixel in by_one.ranked_pixels] == [
        pixel.pixel_id for pixel in all_at_once.ranked_pixels
    ]
    assert all_at_once.ranked_pixels[0].score_pct > all_at_once.ranked_pixels[1].score_pct


def test_argpartition_cutoff_keeps_lexically_first_ids_from_large_tie() -> None:
    batch = make_batch(
        [f"pixel-{index:04d}" for index in reversed(range(1000))],
        {"x": [0] * 1000},
    )
    result = rank_pixel_batches([batch], [make_criterion("x")], top_k=10)
    assert [pixel.pixel_id for pixel in result.ranked_pixels] == [
        f"pixel-{index:04d}" for index in range(10)
    ]


def test_chunked_full_scan_matches_independent_full_sort_reference() -> None:
    random = np.random.default_rng(20261115)
    count = 257
    feature_ids = ["a", "b", "c"]
    criteria = [
        make_criterion("a", 1, (-0.2, 0.3), 0.7),
        make_criterion("b", 4, (0.1, 0.4), 0.9),
        make_criterion("c", 2, (-0.1, 0.2), 0.5),
    ]
    raw = {feature_id: random.normal(size=count) for feature_id in feature_ids}
    masks = {
        feature_id: random.random(count) > (0.08 + index * 0.04)
        for index, feature_id in enumerate(feature_ids)
    }
    batch = ScoringBatch(
        pixel_ids=[f"grid-v1-r{index:04d}" for index in range(count)],
        values=raw,
        units={feature_id: "1" for feature_id in feature_ids},
        measurement_scales={feature_id: "ratio" for feature_id in feature_ids},
        source_ids={feature_id: ["synthetic-earth"] for feature_id in feature_ids},
        validity=masks,
    )

    normalized = normalize_criteria(criteria)
    reference: list[tuple[float, str]] = []
    for index, pixel_id in enumerate(batch.pixel_ids):
        if not all(masks[item.criterion.feature_id][index] for item in normalized):
            continue
        score = math.fsum(
            item.normalized_weight
            * max(
                0.0,
                1.0
                - max(
                    item.criterion.reference_interval[0] - raw[item.criterion.feature_id][index],
                    0.0,
                    raw[item.criterion.feature_id][index]
                    - item.criterion.reference_interval[1],
                )
                / item.criterion.tolerance,
            )
            for item in normalized
        ) * 100.0
        reference.append((score, pixel_id))
    reference.sort(key=lambda item: (-item[0], item[1]))

    expected_top = reference[:10]
    for chunk_size in [1, 7, 32, 100, 257]:
        chunks = [
            batch_slice(batch, start, min(start + chunk_size, count))
            for start in range(0, count, chunk_size)
        ]
        result = rank_pixel_batches(chunks, criteria, top_k=10)
        assert [pixel.pixel_id for pixel in result.ranked_pixels] == [
            pixel_id for _, pixel_id in expected_top
        ]
        np.testing.assert_allclose(
            [pixel.score_pct for pixel in result.ranked_pixels],
            [score for score, _ in expected_top],
            rtol=0,
            atol=1e-12,
        )
        assert result.total_pixels == count
        assert result.eligible_pixels == len(reference)
        assert result.total_pixels == result.eligible_pixels + sum(
            result.excluded_by_reason.values()
        )


def test_upstream_exclusions_are_counted_without_becoming_scores() -> None:
    batch = make_batch(
        ["land", "ocean", "poor-quality", "missing"],
        {"x": [0, 0, 0, None]},
        preexcluded={
            "outside_mask": [False, True, False, False],
            "failed_quality": [False, False, True, False],
        },
    )
    result = rank_pixel_batches([batch], [make_criterion("x")])
    assert [pixel.pixel_id for pixel in result.ranked_pixels] == ["land"]
    assert result.excluded_by_reason == {
        "failed_quality": 1,
        "missing_feature_value": 1,
        "outside_mask": 1,
    }
    assert result.total_pixels == result.eligible_pixels + sum(
        result.excluded_by_reason.values()
    )


@pytest.mark.parametrize(
    "criteria",
    [
        [],
        [make_criterion("a", 1), make_criterion("a", 1)],
        [make_criterion("a", -1)],
        [make_criterion("a", True)],
        [make_criterion("a", math.inf)],
        [make_criterion("a", 1, (2, 1))],
        [make_criterion("a", 1, (0, 1), 0)],
        [make_criterion("a", 1, (0, 1), math.nan)],
        [make_criterion("mineral_class", 1, scale="nominal")],
        [make_criterion("ordinal_code", 1, scale="ordinal")],
    ],
)
def test_invalid_criterion_definitions_are_rejected(criteria: list[FeatureCriterion]) -> None:
    with pytest.raises(ValueError):
        normalize_criteria(criteria)


def test_units_scales_and_invalid_numeric_input_are_never_silently_coerced() -> None:
    criterion = make_criterion("slope", unit="deg")
    with pytest.raises(ValueError, match="Unit mismatch"):
        score_batch(
            make_batch(["p1"], {"slope": [2]}, units={"slope": "m"}),
            [criterion],
        )
    with pytest.raises(ValueError, match="Measurement-scale mismatch"):
        score_batch(
            make_batch(
                ["p1"],
                {"slope": [2]},
                units={"slope": "deg"},
                scales={"slope": "interval"},
            ),
            [criterion],
        )
    with pytest.raises(ValueError, match="real numeric"):
        score_batch(
            ScoringBatch(
                pixel_ids=["p1"],
                values={"slope": np.array(["2"])},
                units={"slope": "deg"},
                measurement_scales={"slope": "ratio"},
                source_ids={"slope": ["synthetic-earth"]},
            ),
            [criterion],
        )


def area_pixel(pixel_id: str, score_pct: float, center: tuple[float, float]) -> ScoredPixel:
    return ScoredPixel(
        pixel_id=pixel_id,
        score_pct=score_pct,
        center=center,
        coverage_fraction=1.0,
        quality_flags=(),
        features=(),
    )


def test_distinct_areas_searches_past_pixel_top_k_and_uses_geodesics() -> None:
    candidates = [
        area_pixel("hotspot-a", 100, (179.95, 0)),
        area_pixel("nearby-across-dateline", 99, (-179.95, 0)),
        area_pixel("distant-b", 95, (0, 0)),
        area_pixel("distant-c", 90, (90, 0)),
    ]

    result = select_distinct_areas(candidates, min_distance_km=25, top_k=2)
    assert [area.representative_pixel.pixel_id for area in result] == [
        "hotspot-a",
        "distant-b",
    ]
    assert result[0].candidate_id == "hotspot-a"
    assert result[0].nearest_selected_distance_km is None
    assert result[1].nearest_selected_distance_km == pytest.approx(
        20_000, abs=100
    )


def test_distinct_area_stream_must_be_ordered_and_have_valid_locations() -> None:
    with pytest.raises(ValueError, match="sorted"):
        select_distinct_areas(
            [area_pixel("lower", 50, (0, 0)), area_pixel("higher", 60, (30, 0))],
            min_distance_km=25,
            top_k=2,
        )
    with pytest.raises(ValueError, match="missing Earth coordinates"):
        select_distinct_areas(
            [ScoredPixel("p1", 100, None, 1, (), ())],
            min_distance_km=25,
        )
    with pytest.raises(ValueError, match="longitude/latitude bounds"):
        select_distinct_areas(
            [area_pixel("p1", 100, (181, 0))], min_distance_km=25
        )


@pytest.mark.parametrize("top_k", [0, 11, True, 1.5])
def test_top_k_contract_bounds_are_enforced(top_k: int) -> None:
    with pytest.raises(ValueError, match="top_k"):
        rank_pixel_batches([], [make_criterion("x")], top_k=top_k)


@pytest.mark.parametrize("distance", [0, -1, math.inf, math.nan, 10_001])
def test_min_distance_km_contract_bounds_are_enforced(distance: float) -> None:
    with pytest.raises(ValueError, match="min_distance_km"):
        select_distinct_areas([], min_distance_km=distance)
