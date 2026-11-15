"""HTTP layer for the versioned regional Terra Analog API."""

from __future__ import annotations

import math
from typing import Annotated, Literal, Union
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from apps.api.data_store import DataIntegrityError, load_registry
from apps.api.errors import ApiProblem
from apps.api.service import build_catalog, get_map_cells, get_manifest, get_pixel_details, get_profile, run_search
from contracts.validation import ContractSemanticError, validate_search_request_semantics


class GlobalScopeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["global"]


class RegionalScopeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["regional"]
    region_id: str = Field(min_length=1, max_length=128)


class SearchCriterionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str = Field(min_length=1, max_length=128)
    weight: float = Field(strict=True, gt=0, le=1_000_000)


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["1.0.0"]
    body: Literal["mars", "moon"]
    profile_id: str = Field(min_length=1, max_length=128)
    dataset_version: str = Field(min_length=1, max_length=128)
    scope: Annotated[Union[GlobalScopeRequest, RegionalScopeRequest], Field(discriminator="type")]
    criteria: list[SearchCriterionRequest] = Field(min_length=1, max_length=16)
    result_mode: Literal["pixels", "distinct_areas"]
    top_k: int = Field(strict=True, ge=1, le=10)
    min_distance_km: float | None = Field(default=None, gt=0, le=10_000)

    @field_validator("top_k", mode="before")
    @classmethod
    def accept_integral_json_number(cls, value: object) -> object:
        # Draft 2020-12 considers a JSON number such as 2.0 an integer when it
        # has no fractional part. Normalize only that numeric case before the
        # strict int validator; strings, booleans, and fractional numbers stay
        # invalid instead of being coerced or rounded.
        if isinstance(value, float) and math.isfinite(value) and value.is_integer():
            return int(value)
        return value

    @model_validator(mode="after")
    def validate_mode_distance(self) -> SearchRequest:
        distance_was_sent = "min_distance_km" in self.model_fields_set
        if self.result_mode == "distinct_areas" and self.min_distance_km is None:
            raise ValueError("a positive min_distance_km is required for distinct_areas")
        if self.result_mode == "pixels" and distance_was_sent:
            raise ValueError("min_distance_km is not allowed for pixels")
        return self


app = FastAPI(
    title="Terra Analog API",
    version="1.0.0",
    description=(
        "Version-pinned API for real planetary reference profiles and three regional Earth "
        "topography packages. Global Earth coverage is not yet available."
    ),
)


@app.exception_handler(ApiProblem)
async def handle_api_problem(_: Request, problem: ApiProblem) -> JSONResponse:
    return JSONResponse(status_code=problem.status_code, content=_error_payload(problem))


@app.exception_handler(RequestValidationError)
async def handle_request_validation(_: Request, error: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            ApiProblem(
                422,
                "INVALID_QUERY",
                "The request does not match the API contract.",
                details={"fields": _validation_details(error.errors())},
            )
        ),
    )


@app.get("/api/v1/health", tags=["health"])
async def get_health() -> dict[str, str | bool | None]:
    """Report API readiness separately from availability of real regional data."""
    try:
        registry = load_registry()
    except DataIntegrityError:
        return {"status": "degraded", "dataset_ready": False, "dataset_version": None}
    return {
        "status": "ready",
        "dataset_ready": bool(registry.datasets),
        # More than one immutable regional version exists; there is no single active version.
        "dataset_version": None,
    }


@app.get("/api/v1/catalog", tags=["catalog"])
async def get_catalog() -> dict:
    return build_catalog(_load_registry_or_problem())


@app.get("/api/v1/catalog/profiles/{profile_id}", tags=["catalog"])
async def get_profile_route(profile_id: str) -> dict:
    return get_profile(_load_registry_or_problem(), profile_id)


@app.get("/api/v1/catalog/datasets/{dataset_version}/manifest", tags=["catalog"])
async def get_dataset_manifest(dataset_version: str) -> dict:
    return get_manifest(_load_registry_or_problem(), dataset_version)


@app.post("/api/v1/search", tags=["analysis"])
async def create_search_analysis(model: SearchRequest) -> dict:
    payload = model.model_dump(mode="python")
    try:
        validate_search_request_semantics(payload)
    except ContractSemanticError as exc:
        raise ApiProblem(422, exc.code, str(exc), details=exc.details) from exc
    try:
        return run_search(_load_registry_or_problem(), model.model_dump(mode="python"))
    except DataIntegrityError as exc:
        raise ApiProblem(503, "DATASET_UNAVAILABLE", "A pinned dataset package failed integrity checks.") from exc


@app.get("/api/v1/analyses/{analysis_id}/pixels/{pixel_id}", tags=["analysis"])
async def get_pixel_details_route(analysis_id: str, pixel_id: str) -> dict:
    return get_pixel_details(analysis_id, pixel_id)


@app.get("/api/v1/analyses/{analysis_id}/map", tags=["analysis"])
async def get_analysis_map_route(analysis_id: str, request: Request) -> dict:
    query = request.query_params
    bbox_value = query.get("bbox")
    if bbox_value is None:
        raise ApiProblem(422, "INVALID_QUERY", "bbox is required as west,south,east,north.")
    try:
        bbox_parts = tuple(float(value.strip()) for value in bbox_value.split(","))
    except ValueError as exc:
        raise ApiProblem(422, "INVALID_QUERY", "bbox must contain four finite numbers.") from exc
    if len(bbox_parts) != 4 or not all(math.isfinite(value) for value in bbox_parts):
        raise ApiProblem(422, "INVALID_QUERY", "bbox must contain four finite numbers.")
    west, south, east, north = bbox_parts
    if not (-180 <= west <= 180 and -180 <= east <= 180 and -90 <= south <= 90 and -90 <= north <= 90):
        raise ApiProblem(422, "INVALID_QUERY", "bbox coordinates are outside WGS84 longitude/latitude bounds.")

    level = _parse_query_int(query.get("level"), "level", required=True)
    limit = _parse_query_int(query.get("limit", "1000"), "limit", required=False)
    cursor = query.get("cursor")
    if cursor is not None and (not cursor or len(cursor) > 512):
        raise ApiProblem(422, "INVALID_QUERY", "cursor must contain 1 to 512 characters.")
    return get_map_cells(
        analysis_id,
        bbox=(west, south, east, north),
        level=level,
        limit=limit,
        cursor=cursor,
    )


def _load_registry_or_problem():
    try:
        return load_registry()
    except DataIntegrityError as exc:
        raise ApiProblem(503, "DATASET_UNAVAILABLE", "A pinned dataset package failed integrity checks.") from exc


def _parse_query_int(raw: str | None, label: str, *, required: bool) -> int:
    if raw is None:
        if required:
            raise ApiProblem(422, "INVALID_QUERY", f"{label} is required.")
        raise ApiProblem(422, "INVALID_QUERY", f"{label} is invalid.")
    try:
        value = int(raw)
    except ValueError as exc:
        raise ApiProblem(422, "INVALID_QUERY", f"{label} must be an integer.") from exc
    return value


def _validation_details(errors: list[dict]) -> list[dict[str, str]]:
    return [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())),
            "message": str(error.get("msg", "Invalid value"))[:500],
        }
        for error in errors[:32]
    ]


def _error_payload(problem: ApiProblem) -> dict:
    error: dict = {"code": problem.code, "message": problem.message}
    if problem.details:
        error["details"] = problem.details
    return {
        "contract_version": "1.0.0",
        "is_synthetic": False,
        "request_id": str(uuid4()),
        "error": error,
    }
