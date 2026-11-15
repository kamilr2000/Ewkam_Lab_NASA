# E-018 review — K-006 MCDA and pixel ranking

- Reviewer: Ewelina (`codex-ewelina-e018-k006-review`)
- Date: 2026-11-15
- Reviewed PR: [#15](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/15)
- Exact reviewed head: `aa464eb33cc023e63bd24f2f6b60a2d5a69b7fcf`
- Result: **APPROVED** for the scoring primitives and the documented handoff scope.

## Checks performed

1. Read the exact PR diff, `apps/api/scoring/engine.py`, its tests, the frozen search request/response schemas, `docs/METHODOLOGY.md` §§5–9, and the K-006 handoff.
2. Ran the scoring and contract suites on the reviewed commit:

   ```powershell
   uv run --cache-dir C:\studia\NASA\.uv-cache-e018 --locked pytest apps/api/tests/test_scoring.py contracts/tests/test_contracts.py -q
   ```

   Result: **71 passed in 2.32 s**.

3. Independently recomputed a three-pixel example from the v0.1 formula. For weights 1:2, feature A interval [10,20] with tolerance 5 and feature B interval [0,4] with tolerance 2, the expected scores are `p3 = 83.33333333333333`, `p1 = p2 = 33.33333333333333`; the engine returned that order, values, and contributions. Equal scores use ascending pixel ID.
4. Confirmed `python tools/check_planning.py` passes on the reviewed commit (96 Markdown files, 30 JSON files, 45 task cards, no dependency cycles, five synthetic cases). `git diff --check` from main `ce3085c8e2134c0f2b8bd7d72cf63e858d6cf6f6` to reviewed head returned no errors.

## Review findings

No blocking or high-priority algorithm defect found in the reviewed scope. The implementation matches the v0.1 interval similarity, normalizes active weights, requires valid measurements for every active feature, leaves excluded scores unavailable, and retains deterministic Top K by unrounded score and pixel ID. The tests cover interval boundaries, zero and invalid weights/scales, unit and scale mismatches, missing measurements, independent full-sort comparison across batch sizes, large ties, all five published synthetic hotspot regressions, the dateline geodesic case, and sorted-stream/location validation for `distinct_areas`.

The engine intentionally ranks every row it receives but cannot establish that the caller supplied the complete declared Earth scope exactly once or detect duplicate IDs across separate batches. That is explicitly handed off to K-005/K-008 and is not presented as a global-coverage guarantee. `select_distinct_areas` requires the complete eligible stream sorted by unrounded score and pixel ID; K-008 still needs to provide and validate the scalable external sort. This PR does not implement the search endpoint, real-data loading, map aggregation, or real-pixel processing.

`coverage_fraction = 1` on materialized eligible pixels is consistent with the current method's feature-completeness definition: every active feature must have a valid measurement before a pixel can be materialized. It is not a claim that source sampling is 100% complete or that the result is scientifically certain; upstream sample coverage and QA must remain separately documented.

## Outcome

I approved PR #15 for the exact head above. The approval does not merge K-006 or establish global scan completeness, availability of the future HTTP search endpoint, or results on non-synthetic data. K-006 remains in `review` until its owner integrates the implementation into `origin/main`.
