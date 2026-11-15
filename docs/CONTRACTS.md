# API contract and frontend integration

Contract v1.0.0 defines the boundary between the API and web application. The API owns catalogue contents, validation, scoring, ranking, map aggregation, and pixel explanations. The frontend renders those responses and must not implement a second scoring engine.

## Shared rules

- Every response uses the contract version and explicit profile/dataset identifiers required by its schema.
- A search pins the selected body/profile, one Earth dataset and region, active feature IDs and weights, and ranking mode.
- A candidate missing any active feature is not scored as zero. It is excluded with a reason; null remains explicit.
- Map cells, pixel ranking, and pixel detail must refer to the same analysis ID.
- Global scope is currently unavailable and returns SCOPE_UNAVAILABLE. It must never silently fall back to one of the regional datasets.
- Synthetic fixtures are marked synthetic. A Live API error or response mismatch must remain an error and must not switch to a fixture.
- Map request echoes (including bbox, zoom level and limits) and search query echoes must match the request. A mismatch is rejected rather than shown as a current result.
- Map-layer visibility is presentation state and does not alter query criteria or ranking.

## Operations

The versioned OpenAPI file is contracts/openapi.yaml. The local JSON Schemas define health, catalog, profile, dataset manifest, search request and response, pixel detail, map response, and error payloads. See [contracts/README.md](../contracts/README.md) for the schema inventory and validation commands.

The current API exposes health and catalogue checks, versioned profiles, regional search, map aggregates, and details for a selected pixel. Exact paths and response fields are owned by the OpenAPI document and schemas; update those contracts together with API code and frontend adapter.

## Geometry and numeric semantics

GeoJSON coordinates are longitude/latitude in WGS 84 unless a schema says otherwise. IDs are strings to avoid browser integer precision loss. Physical distances use metres or kilometres explicitly; Web Mercator zoom is a display parameter, not measurement scale.

Null values require a corresponding missing-data reason. Fractions and percentages must state their denominator and interpretation. Validate finite numbers, valid geometry nesting, query echoes, and semantic uniqueness of selected criteria.

## Synthetic fixtures and tests

Fixtures cover successful search, empty scope, missing data, isolated hotspot, distinct areas, unavailable datasets, and health without a ready dataset. They validate the interface and contract, not real-world measurements.

Run contract validation from the repository root:

```powershell
uv sync --locked --dev
uv run --locked pytest contracts/tests/test_contracts.py
```
