from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from contracts.validation import (
    ContractSemanticError,
    validate_dataset_manifest_semantics,
    validate_search_request_semantics,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"
FIXTURES = CONTRACTS / "fixtures"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rectangular_geometry_bounds(
    geometry: dict,
) -> tuple[float, float, float, float]:
    assert geometry["type"] == "Polygon"
    assert len(geometry["coordinates"]) == 1
    ring = [tuple(position) for position in geometry["coordinates"][0]]
    assert len(ring) == 5
    assert ring[0] == ring[-1]

    west = min(position[0] for position in ring[:-1])
    east = max(position[0] for position in ring[:-1])
    south = min(position[1] for position in ring[:-1])
    north = max(position[1] for position in ring[:-1])
    assert set(ring[:-1]) == {
        (west, south),
        (east, south),
        (east, north),
        (west, north),
    }
    return west, south, east, north


def _assert_rectangles_partition_scope(
    scope_bounds: tuple[float, float, float, float],
    geometries: list[dict],
    label: str,
) -> None:
    west, south, east, north = scope_bounds
    assert west < east and south < north
    rectangles = [_rectangular_geometry_bounds(geometry) for geometry in geometries]
    for cell_west, cell_south, cell_east, cell_north in rectangles:
        assert west <= cell_west < cell_east <= east
        assert south <= cell_south < cell_north <= north

    x_edges = sorted(
        {
            west,
            east,
            *(edge for rect in rectangles for edge in (rect[0], rect[2])),
        }
    )
    y_edges = sorted(
        {
            south,
            north,
            *(edge for rect in rectangles for edge in (rect[1], rect[3])),
        }
    )
    for left, right in zip(x_edges, x_edges[1:]):
        for bottom, top in zip(y_edges, y_edges[1:]):
            x_mid = (left + right) / 2
            y_mid = (bottom + top) / 2
            covering_rectangles = sum(
                rect_west <= x_mid < rect_east and rect_south <= y_mid < rect_north
                for rect_west, rect_south, rect_east, rect_north in rectangles
            )
            assert covering_rectangles == 1, (
                f"{label} does not partition declared scope at "
                f"({x_mid}, {y_mid}); found {covering_rectangles} covering geometries"
            )


def _assert_hotspot_fixture_spatial_coverage(search: dict, map_response: dict) -> None:
    scope_bounds = _rectangular_geometry_bounds(search["scope"]["geometry"])
    assert tuple(map_response["query"]["bbox"]) == scope_bounds
    assert map_response["analysis_id"] == search["analysis_id"]
    assert map_response["map_cells"] == search["map_cells"]
    _assert_rectangles_partition_scope(
        scope_bounds,
        [cell["geometry"] for cell in search["map_cells"]],
        "map-cell union",
    )
    _assert_rectangles_partition_scope(
        scope_bounds,
        [pixel["geometry"] for pixel in search["ranking"]],
        "ranked-pixel union",
    )


SCHEMA_FIXTURES = [
    ("health-response.schema.json", "health-ready-no-dataset.json"),
    ("catalog-response.schema.json", "catalog-synthetic.json"),
    ("profile-response.schema.json", "profile-synthetic.json"),
    ("dataset-manifest.schema.json", "dataset-manifest-synthetic.json"),
    ("search-request.schema.json", "search-request-synthetic.json"),
    ("search-response.schema.json", "search-success-synthetic.json"),
    ("search-response.schema.json", "search-empty-synthetic.json"),
    ("search-response.schema.json", "search-no-data-synthetic.json"),
    ("search-response.schema.json", "search-hotspot-synthetic.json"),
    ("search-response.schema.json", "search-distinct-areas-synthetic.json"),
    ("pixel-details-response.schema.json", "pixel-hotspot-synthetic.json"),
    ("map-response.schema.json", "map-hotspot-synthetic.json"),
    ("error-response.schema.json", "error-dataset-unavailable-synthetic.json"),
]


@pytest.mark.parametrize(
    "schema_path",
    sorted(CONTRACTS.glob("*.schema.json")),
    ids=lambda path: path.name,
)
def test_schema_is_valid_draft_2020_12(schema_path: Path) -> None:
    Draft202012Validator.check_schema(load_json(schema_path))


@pytest.mark.parametrize("schema_name,fixture_name", SCHEMA_FIXTURES)
def test_contract_fixture_matches_schema(schema_name: str, fixture_name: str) -> None:
    schema = load_json(CONTRACTS / schema_name)
    instance = load_json(FIXTURES / fixture_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    assert not errors, "\n".join(error.message for error in errors)


@pytest.mark.parametrize(
    ("schema_name", "fixture_name", "geometry_path"),
    [
        ("catalog-response.schema.json", "catalog-synthetic.json", ("search_regions", 0, "geometry")),
        ("map-response.schema.json", "map-hotspot-synthetic.json", ("map_cells", 0, "geometry")),
        ("pixel-details-response.schema.json", "pixel-hotspot-synthetic.json", ("pixel", "geometry")),
    ],
)
@pytest.mark.parametrize(
    "invalid_coordinates",
    [
        ["not-a-polygon"],
        [[[[181, 0], [0, 0], [0, 0], [0, 0]]]],
    ],
    ids=["non-polygon-entry", "out-of-range-position"],
)
def test_response_schemas_reject_malformed_multipolygon_coordinates(
    schema_name: str,
    fixture_name: str,
    geometry_path: tuple[str | int, ...],
    invalid_coordinates: list,
) -> None:
    schema = load_json(CONTRACTS / schema_name)
    instance = load_json(FIXTURES / fixture_name)
    geometry = instance
    for path_part in geometry_path[:-1]:
        geometry = geometry[path_part]
    geometry[geometry_path[-1]] = {
        "type": "MultiPolygon",
        "coordinates": invalid_coordinates,
    }

    assert not Draft202012Validator(schema).is_valid(instance)


def test_search_request_rejects_invalid_mode_parameters() -> None:
    schema = load_json(CONTRACTS / "search-request.schema.json")
    validator = Draft202012Validator(schema)
    request = load_json(FIXTURES / "search-request-synthetic.json")

    pixels_with_distance = copy.deepcopy(request)
    pixels_with_distance["min_distance_km"] = 25
    assert not validator.is_valid(pixels_with_distance)

    distinct_without_distance = copy.deepcopy(request)
    distinct_without_distance["result_mode"] = "distinct_areas"
    assert not validator.is_valid(distinct_without_distance)

    distinct = copy.deepcopy(distinct_without_distance)
    distinct["min_distance_km"] = 25
    assert validator.is_valid(distinct)


def test_semantic_validation_rejects_duplicate_feature_ids_with_different_weights() -> None:
    schema = load_json(CONTRACTS / "search-request.schema.json")
    validator = Draft202012Validator(schema)
    request = load_json(FIXTURES / "search-request-synthetic.json")
    request["criteria"].append({"feature_id": "slope_deg", "weight": 2})

    # JSON Schema uniqueItems compares whole objects; different weights still
    # make these objects distinct, so the cross-item rule is checked separately.
    assert validator.is_valid(request)
    with pytest.raises(ContractSemanticError) as exc_info:
        validate_search_request_semantics(request)

    assert exc_info.value.code == "DUPLICATE_FEATURE_ID"
    assert exc_info.value.details == {"feature_ids": ["slope_deg"]}


def test_search_response_requires_complete_scoring_fields() -> None:
    schema = load_json(CONTRACTS / "search-response.schema.json")
    validator = Draft202012Validator(schema)
    response = load_json(FIXTURES / "search-success-synthetic.json")

    missing_analysis_id = copy.deepcopy(response)
    del missing_analysis_id["analysis_id"]
    assert not validator.is_valid(missing_analysis_id)

    missing_active_measurement = copy.deepcopy(response)
    missing_active_measurement["ranking"][0]["features"][0]["value"] = None
    assert not validator.is_valid(missing_active_measurement)


def test_distinct_areas_response_does_not_expose_pixel_ranking_field() -> None:
    schema = load_json(CONTRACTS / "search-response.schema.json")
    response = load_json(FIXTURES / "search-distinct-areas-synthetic.json")
    Draft202012Validator(schema).validate(response)
    assert "ranking" not in response
    assert len(response["area_ranking"]) == 2
    assert response["query"]["min_distance_km"] == 25


def test_missing_data_is_null_with_reason_and_never_a_zero_score() -> None:
    response = load_json(FIXTURES / "search-no-data-synthetic.json")
    assert response["ranking"] == []
    assert response["coverage"]["no_data_reason"] == "missing_feature_values"
    cell = response["map_cells"][0]
    assert cell["max_score_pct"] is None
    assert cell["mean_score_pct"] is None
    assert cell["max_pixel_id"] is None
    assert cell["missing_reason"] == "missing_feature_value"


def test_search_response_rejects_null_map_scores_without_a_missing_reason() -> None:
    schema = load_json(CONTRACTS / "search-response.schema.json")
    validator = Draft202012Validator(schema)
    response = load_json(FIXTURES / "search-success-synthetic.json")
    cell = response["map_cells"][0]
    cell["max_score_pct"] = None
    cell["mean_score_pct"] = None
    cell["max_pixel_id"] = None

    assert not validator.is_valid(response)


def test_search_response_global_scope_does_not_claim_regional_metadata() -> None:
    schema = load_json(CONTRACTS / "search-response.schema.json")
    validator = Draft202012Validator(schema)
    response = load_json(FIXTURES / "search-success-synthetic.json")
    response["scope"].update({"type": "global", "region_id": "synthetic-region-1"})

    assert not validator.is_valid(response)


def test_analytical_response_fixtures_are_explicitly_synthetic() -> None:
    response_fixtures = [
        "catalog-synthetic.json",
        "dataset-manifest-synthetic.json",
        "error-dataset-unavailable-synthetic.json",
        "map-hotspot-synthetic.json",
        "pixel-hotspot-synthetic.json",
        "profile-synthetic.json",
        "search-distinct-areas-synthetic.json",
        "search-empty-synthetic.json",
        "search-hotspot-synthetic.json",
        "search-no-data-synthetic.json",
        "search-success-synthetic.json",
    ]
    for fixture_name in response_fixtures:
        assert load_json(FIXTURES / fixture_name)["is_synthetic"] is True


def test_hotspot_survives_pixel_ranking_and_map_aggregation() -> None:
    response = load_json(FIXTURES / "search-hotspot-synthetic.json")
    assert response["ranking"][0]["pixel_id"] == "synthetic-hotspot-p001"
    assert response["ranking"][0]["score_pct"] == 100
    weak_cell = next(cell for cell in response["map_cells"] if cell["cell_id"] == "synthetic-weak-map-cell")
    assert weak_cell["max_pixel_id"] == "synthetic-hotspot-p001"
    assert weak_cell["max_score_pct"] == 100
    assert weak_cell["mean_score_pct"] < weak_cell["max_score_pct"]


def test_hotspot_fixture_scope_map_cells_pixels_and_coverage_align() -> None:
    search = load_json(FIXTURES / "search-hotspot-synthetic.json")
    map_response = load_json(FIXTURES / "map-hotspot-synthetic.json")

    assert search["is_synthetic"] is True
    assert map_response["is_synthetic"] is True
    _assert_hotspot_fixture_spatial_coverage(search, map_response)

    coverage = search["coverage"]
    excluded_count = sum(coverage["excluded_by_reason"].values())
    assert coverage["total_pixels"] == coverage["eligible_pixels"] + excluded_count
    assert len(search["ranking"]) == coverage["eligible_pixels"]
    assert (
        sum(cell["total_pixel_count"] for cell in search["map_cells"])
        == coverage["total_pixels"]
    )
    assert (
        sum(cell["valid_pixel_count"] for cell in search["map_cells"])
        == coverage["eligible_pixels"]
    )

    total_pixel_area = sum(pixel["pixel_area_km2"] for pixel in search["ranking"])
    eligible_pixel_area = sum(
        pixel["pixel_area_km2"]
        for pixel in search["ranking"]
        if pixel["coverage_fraction"] == 1
    )
    assert coverage["total_area_km2"] == pytest.approx(total_pixel_area)
    assert coverage["eligible_area_km2"] == pytest.approx(eligible_pixel_area)
    assert coverage["eligible_area_fraction"] == pytest.approx(
        eligible_pixel_area / total_pixel_area
    )
    for cell in search["map_cells"]:
        assert cell["coverage_fraction"] == pytest.approx(
            cell["valid_pixel_count"] / cell["total_pixel_count"]
        )


def test_hotspot_coverage_guard_rejects_unrepresented_scope_strip() -> None:
    search = load_json(FIXTURES / "search-hotspot-synthetic.json")
    map_response = load_json(FIXTURES / "map-hotspot-synthetic.json")
    scope_ring = search["scope"]["geometry"]["coordinates"][0]
    scope_ring[2][1] = 3.02
    scope_ring[3][1] = 3.02
    map_response["query"]["bbox"][3] = 3.02

    with pytest.raises(
        AssertionError,
        match="map-cell union does not partition declared scope",
    ):
        _assert_hotspot_fixture_spatial_coverage(search, map_response)


def test_success_contributions_and_map_mean_match_synthetic_ranking() -> None:
    response = load_json(FIXTURES / "search-success-synthetic.json")
    for pixel in response["ranking"]:
        assert sum(feature["contribution_pct"] for feature in pixel["features"]) == pytest.approx(pixel["score_pct"])
    cell = response["map_cells"][0]
    assert cell["max_score_pct"] == max(pixel["score_pct"] for pixel in response["ranking"])
    assert cell["mean_score_pct"] == pytest.approx(sum(pixel["score_pct"] for pixel in response["ranking"]) / len(response["ranking"]))


def test_real_manifest_requires_source_rights_and_file_provenance() -> None:
    schema = load_json(CONTRACTS / "dataset-manifest.schema.json")
    manifest = load_json(FIXTURES / "dataset-manifest-synthetic.json")
    manifest["is_synthetic"] = False
    manifest["synthetic_reason"] = None
    assert not Draft202012Validator(schema, format_checker=FormatChecker()).is_valid(manifest)


def test_manifest_nulls_require_field_specific_reasons() -> None:
    manifest = load_json(FIXTURES / "dataset-manifest-synthetic.json")
    validate_dataset_manifest_semantics(manifest)

    del manifest["missing_reasons"]["sources[0].license"]
    with pytest.raises(ContractSemanticError) as exc_info:
        validate_dataset_manifest_semantics(manifest)
    assert exc_info.value.code == "MISSING_REASON_REQUIRED"
    assert exc_info.value.details == {"paths": ["sources[0].license"]}
