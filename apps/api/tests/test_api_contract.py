"""API integration checks against the frozen v1 JSON Schemas and real K-005 data."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from jsonschema import Draft202012Validator, FormatChecker

from apps.api.data_store import ROOT, load_registry
from apps.api.main import app


def _request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    async def perform() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(perform())


def _assert_schema(schema_name: str, value: dict[str, Any]) -> None:
    schema_path = ROOT / "contracts" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(map(str, error.absolute_path)),
    )
    assert not errors, "\n".join(
        f"{list(error.absolute_path)}: {error.message}" for error in errors
    )


def _search_request(
    *,
    body: str,
    profile_id: str,
    dataset_version: str,
    region_id: str,
    result_mode: str = "pixels",
    min_distance_km: float | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "contract_version": "1.0.0",
        "body": body,
        "profile_id": profile_id,
        "dataset_version": dataset_version,
        "scope": {"type": "regional", "region_id": region_id},
        "criteria": [
            {"feature_id": "slope_deg", "weight": 1},
            {"feature_id": "roughness_m", "weight": 2},
            {"feature_id": "relief_m", "weight": 1},
        ],
        "result_mode": result_mode,
        "top_k": 5,
    }
    if min_distance_km is not None:
        value["min_distance_km"] = min_distance_km
    return value


def test_catalog_profiles_and_real_regional_search_match_contracts() -> None:
    registry = load_registry()
    catalog_response = _request("GET", "/api/v1/catalog")
    assert catalog_response.status_code == 200
    catalog = catalog_response.json()
    _assert_schema("catalog-response.schema.json", catalog)
    assert catalog["is_synthetic"] is False
    assert {region["region_id"] for region in catalog["search_regions"]} == {
        "atacama-andes",
        "hawaii-big-island",
        "himalaya",
    }
    assert {profile["body"] for profile in catalog["profiles"]} == {"mars", "moon"}

    cases = [
        ("mars", "mars-jezero-mola128-v1", "atacama-andes"),
        ("moon", "moon-south-polar-80s-lola80-v1", "hawaii-big-island"),
    ]
    for body, profile_id, region_id in cases:
        dataset = next(item for item in registry.datasets.values() if item.region_id == region_id)
        profile_response = _request("GET", f"/api/v1/catalog/profiles/{profile_id}")
        assert profile_response.status_code == 200
        _assert_schema("profile-response.schema.json", profile_response.json())
        assert profile_response.json()["is_synthetic"] is False

        manifest_response = _request(
            "GET", f"/api/v1/catalog/datasets/{dataset.version}/manifest"
        )
        assert manifest_response.status_code == 200
        _assert_schema("dataset-manifest.schema.json", manifest_response.json())

        response = _request(
            "POST",
            "/api/v1/search",
            json=_search_request(
                body=body,
                profile_id=profile_id,
                dataset_version=dataset.version,
                region_id=region_id,
            ),
        )
        assert response.status_code == 200, response.text
        result = response.json()
        _assert_schema("search-response.schema.json", result)
        assert result["is_synthetic"] is False
        assert result["scope"]["type"] == "regional"
        assert result["coverage"]["total_pixels"] == len(dataset.cells)
        assert result["coverage"]["eligible_pixels"] > 0
        assert len(result["ranking"]) == 5
        assert len(result["map_cells"]) > 0
        assert all(cell["level"] == 8 for cell in result["map_cells"])

        winner = result["ranking"][0]
        detail_response = _request(
            "GET",
            f"/api/v1/analyses/{result['analysis_id']}/pixels/{winner['pixel_id']}",
        )
        assert detail_response.status_code == 200
        details = detail_response.json()
        _assert_schema("pixel-details-response.schema.json", details)
        assert details["analysis_id"] == result["analysis_id"]
        assert details["pixel"]["score_pct"] == winner["score_pct"]
        assert abs(
            sum(feature["contribution_pct"] for feature in details["pixel"]["features"])
            - details["pixel"]["score_pct"]
        ) < 1e-8


def test_map_endpoint_pages_xyz_aggregates_from_same_analysis() -> None:
    dataset = next(
        item for item in load_registry().datasets.values() if item.region_id == "atacama-andes"
    )
    created = _request(
        "POST",
        "/api/v1/search",
        json=_search_request(
            body="mars",
            profile_id="mars-jezero-mola128-v1",
            dataset_version=dataset.version,
            region_id=dataset.region_id,
        ),
    ).json()
    params = {"bbox": "-69.1,-25.1,-67.9,-23.9", "level": 10, "limit": 2}
    first = _request("GET", f"/api/v1/analyses/{created['analysis_id']}/map", params=params)
    assert first.status_code == 200
    first_page = first.json()
    _assert_schema("map-response.schema.json", first_page)
    assert len(first_page["map_cells"]) == 2
    assert first_page["next_cursor"] is not None

    second = _request(
        "GET",
        f"/api/v1/analyses/{created['analysis_id']}/map",
        params={**params, "cursor": first_page["next_cursor"]},
    )
    assert second.status_code == 200
    second_page = second.json()
    _assert_schema("map-response.schema.json", second_page)
    assert second_page["analysis_id"] == created["analysis_id"]
    assert first_page["map_cells"][0]["cell_id"] != second_page["map_cells"][0]["cell_id"]


def test_distinct_areas_are_separate_from_pixel_ranking() -> None:
    dataset = next(
        item for item in load_registry().datasets.values() if item.region_id == "himalaya"
    )
    request = _search_request(
        body="moon",
        profile_id="moon-south-polar-80s-lola80-v1",
        dataset_version=dataset.version,
        region_id=dataset.region_id,
        result_mode="distinct_areas",
        min_distance_km=5,
    )
    response = _request("POST", "/api/v1/search", json=request)
    assert response.status_code == 200, response.text
    result = response.json()
    _assert_schema("search-response.schema.json", result)
    assert "ranking" not in result
    assert len(result["area_ranking"]) == 5
    assert result["query"]["area_selection_rule"] == "greedy_geodesic_representatives"


def test_real_profile_search_accepts_one_active_feature_and_normalizes_its_weight() -> None:
    dataset = next(
        item for item in load_registry().datasets.values() if item.region_id == "hawaii-big-island"
    )
    payload = _search_request(
        body="moon",
        profile_id="moon-south-polar-80s-lola80-v1",
        dataset_version=dataset.version,
        region_id=dataset.region_id,
    )
    payload["criteria"] = [{"feature_id": "slope_deg", "weight": 7}]

    response = _request("POST", "/api/v1/search", json=payload)
    assert response.status_code == 200, response.text
    result = response.json()
    _assert_schema("search-response.schema.json", result)
    assert result["query"]["criteria"] == [
        {"feature_id": "slope_deg", "weight": 7, "normalized_weight": 1}
    ]
    assert all(
        [feature["feature_id"] for feature in pixel["features"]] == ["slope_deg"]
        for pixel in result["ranking"]
    )


def test_global_and_duplicate_feature_requests_return_contract_errors() -> None:
    dataset = next(
        item for item in load_registry().datasets.values() if item.region_id == "atacama-andes"
    )
    global_request = _search_request(
        body="mars",
        profile_id="mars-jezero-mola128-v1",
        dataset_version=dataset.version,
        region_id=dataset.region_id,
    )
    global_request["scope"] = {"type": "global"}
    global_response = _request("POST", "/api/v1/search", json=global_request)
    assert global_response.status_code == 409
    _assert_schema("error-response.schema.json", global_response.json())
    assert global_response.json()["error"]["code"] == "SCOPE_UNAVAILABLE"

    duplicate_request = _search_request(
        body="mars",
        profile_id="mars-jezero-mola128-v1",
        dataset_version=dataset.version,
        region_id=dataset.region_id,
    )
    duplicate_request["criteria"].append({"feature_id": "slope_deg", "weight": 3})
    duplicate_response = _request("POST", "/api/v1/search", json=duplicate_request)
    assert duplicate_response.status_code == 422
    _assert_schema("error-response.schema.json", duplicate_response.json())
    assert duplicate_response.json()["error"]["code"] == "DUPLICATE_FEATURE_ID"


def test_distinct_areas_rejects_null_minimum_distance() -> None:
    dataset = next(
        item for item in load_registry().datasets.values() if item.region_id == "atacama-andes"
    )
    payload = _search_request(
        body="mars",
        profile_id="mars-jezero-mola128-v1",
        dataset_version=dataset.version,
        region_id=dataset.region_id,
        result_mode="distinct_areas",
    )
    payload["min_distance_km"] = None

    response = _request("POST", "/api/v1/search", json=payload)
    assert response.status_code == 422
    _assert_schema("error-response.schema.json", response.json())
    assert response.json()["error"]["code"] == "INVALID_QUERY"


def test_unknown_analysis_and_profile_do_not_fall_back_to_current_data() -> None:
    missing_analysis = _request(
        "GET", "/api/v1/analyses/never-created/pixels/earth:unknown"
    )
    assert missing_analysis.status_code == 404
    _assert_schema("error-response.schema.json", missing_analysis.json())

    dataset = next(
        item for item in load_registry().datasets.values() if item.region_id == "atacama-andes"
    )
    payload = _search_request(
        body="mars",
        profile_id="not-a-profile",
        dataset_version=dataset.version,
        region_id=dataset.region_id,
    )
    unknown_profile = _request("POST", "/api/v1/search", json=payload)
    assert unknown_profile.status_code == 404
    _assert_schema("error-response.schema.json", unknown_profile.json())
    assert unknown_profile.json()["error"]["code"] == "UNKNOWN_PROFILE"
