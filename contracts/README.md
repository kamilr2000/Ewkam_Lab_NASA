# API contracts

Contract version 1.0.0 defines API operations in openapi.yaml and payload shapes in the local JSON Schema files. Semantic rules that JSON Schema cannot express are documented in docs/CONTRACTS.md and enforced by the API validator.

## Main schemas

| Schema | Purpose |
|---|---|
| health-response.schema.json | API process and local dataset readiness |
| catalog-response.schema.json | Available profiles, criteria, datasets, and search regions |
| profile-response.schema.json | Versioned planetary reference profile with body, units, and scale |
| dataset-manifest.schema.json | Provenance, licences, files, grid, QA, coverage, and processing |
| search-request.schema.json | Explicit scope, selected criteria and weights, and ranking mode |
| search-response.schema.json | Pixel or distinct-area ranking and map-cell aggregates |
| pixel-details-response.schema.json | Measurements and provenance for one cell in an analysis |
| map-response.schema.json | Bounded map aggregates for that same analysis |
| error-response.schema.json | Shared API error envelope |

## Synthetic fixtures

Fixture payloads are synthetic examples for contract and UI tests. They are not measured terrain and must not be used as an automatic fallback for Live API errors. Their synthetic state must stay explicit.

The fixture set covers successful ranking, empty scope, no-data/null handling, isolated hotspots, distinct-area selection, unavailable datasets, and API health without a ready dataset.

## Validation

Install the pinned development dependencies and run:

```powershell
uv sync --locked --dev
uv run --locked pytest contracts/tests/test_contracts.py
```

Schema checks do not prove that scientific inputs, coverage, or a live deployment are correct. See the source manifests and validation records for those claims.
