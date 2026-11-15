# E-022 review — K-022 hotspot fixture coverage

- Reviewer: Ewelina (`codex-ewelina-e022-review`)
- Date: 2026-11-15
- Reviewed PR: [#28](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/28)
- Exact reviewed implementation commit: `8fb3ab5da9117090b430fbe29df76862c6e70cda`
- Result: **APPROVED** for the synthetic fixture extent, coverage accounting, and regression guard.

## Checks performed

1. Compared the exact commit diff. The search scope and map query bbox both changed from `[3, 3, 3.04, 3.02]` to `[3, 3, 3.04, 3.01]`; the four pixel geometries and two map-cell geometries stayed unchanged. The scope, bbox, ranked pixel union, and map-cell union now use the same extent. Every pixel is contained by exactly one fixture map cell, and both responses retain the same `analysis_id` and map cells.
2. Independently read the fixture values. It contains 4/4 eligible synthetic pixels, no excluded pixels, map-cell count sums of 4 total and 4 valid, and cell fractions of 3/3 and 1/1. `total_area_km2` and `eligible_area_km2` are sums of the fixture's explicit `pixel_area_km2` values (4 km²); they are not calculated from the longitude/latitude degree area. These values remain synthetic examples, not measured physical areas.
3. Confirmed the hotspot regression still ranks `synthetic-hotspot-p001` first at 100, while its containing weak cell reports maximum 100 and mean `46.666666666666664`. The other cell reports maximum and mean 60. The values and cell assignments match the fixture geometries and scores.
4. Extracted commit `8fb3ab5da9117090b430fbe29df76862c6e70cda` to a temporary snapshot and ran `contracts/tests/test_contracts.py` with the repository virtual environment: **42 passed**. This includes the in-memory mutation restoring the old 3.02°N extent; the guard rejects the resulting unrepresented strip. `tools/check_planning.py` passed (115 Markdown files, 32 JSON files, 56 task cards, acyclic dependencies, five synthetic cases). `git diff --check 8fb3ab5da9117090b430fbe29df76862c6e70cda^ 8fb3ab5da9117090b430fbe29df76862c6e70cda` reported no whitespace errors.
5. Compared the fixture with E-019 at its exact reviewed ref `fde069cb35342986c5d2cc656a66fa90191377a9`. Its map specification and SVG show 3.00–3.01°N and 3.00–3.04°E, matching the corrected fixture. The design labels the view synthetic and has no kilometre scale bar.
6. Confirmed the PR's current head is `abd0697df98c47e87b56043683029e7f73d20417`, with the reviewed commit as an ancestor and no later changes to the reviewed fixture, test, or AI disclosure files.

## Findings and limits

No blocking findings in the reviewed scope. The exact diff repairs the previously unrepresented north strip without inventing pixels or measurements, and the tests cover both complete rectangular fixture coverage and the original regression.

This review validates static synthetic fixtures and their contract tests only. It does not establish real geographic area, live API behavior, completeness of any runtime scan, global Top 10 optimality, or results from planetary observations. No runtime API test was performed.

## Outcome

I approved PR #28 for the exact commit above. Kamil still owns merging K-022 and updating its implementation card. This report is published for the E-022 review task and does not merge or mark K-022 done.
