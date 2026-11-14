# Handoff: E-013 review K-003

- Review URL: https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/7
- Reviewed contract commit: `b439941e1a6d33573b5de46654004fe2ab8a51b0`
- PR head reviewed for later deltas: `c3d82171185746d29a6e4d8e684cdf43638030c9`
- GitHub review: `REQUEST_CHANGES`, review ID `5906550283`
- Owner for requested correction: Kamil, within existing K-003 scope

## Confirmed contract behavior

The contract separates the pixel ranking, `distinct_areas` representative ranking, and map aggregates. Responses carry the analysis ID, effective query and scope, units, measurement scale, source references, missing-value reasons, and synthetic status. Fixtures are explicitly synthetic. OpenAPI documents only `/api/v1/health` as implemented; the other operations are planned contracts.

## Required correction

Nested MultiPolygon coordinates are not validated in `catalog-response.schema.json`, `map-response.schema.json`, and `pixel-details-response.schema.json`. Reproduction against `map-response.schema.json` showed `coordinates: ["not-a-polygon"]` passes Draft 2020-12 validation. Reuse the nested polygon/ring/position definitions in `search-response.schema.json` and add negative regression coverage for all affected response schemas.

## Evidence and limitations

- `uv run --locked pytest -q contracts/tests/test_contracts.py`: **34 passed**.
- `python tools/check_planning.py`: passed on the exact review target.
- `git diff --check`: passed on the exact review target.
- No production search API or scientific data are included in this contract PR.
