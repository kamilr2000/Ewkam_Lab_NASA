# K-024 review — E-020 response scope binding

- Reviewer: Kamil (`codex-kamil-k024-review-e020`)
- Date: 2026-11-15, Europe/Warsaw
- Reviewed task/PR: K-024 / [PR #20](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/20)
- Exact `review_ref`: `04aee3f6dc88f7338334d1d70a0fe51793c6911d`
- Current PR head checked: `d08876d01903e73ad2ee6565a9ef3a9340d3828f`; adapter, tests, and README are unchanged from the exact review ref.
- Result: **APPROVED**, GitHub review `5908300727`.
- K-021 inline finding `PRRT_kwDOVuLLic63kyBe` was resolved after verifying the correction.

## Scope binding checked

`responseScopeMatchesRequest` rejects a top-level scope whose `type` differs from the request and requires the requested `region_id` for regional scope. Global scope must have `region_id`, `region_name`, and `geometry` equal to `null`. `parseSearch` applies this guard after the query-scope echo check, so a matching `query.scope` cannot mask a mismatching top-level result scope.

The added regressions reject a different top-level regional ID and type, plus global responses with a non-null region ID or name. Existing coverage also accepts a valid global distinct-area response, checks map `bbox`/`level`/`limit`, preserves `analysis_id` and pixel ID checks, and ensures a live error does not trigger a fixture fallback. The implementation explicitly rejects non-null global geometry; the suite has no dedicated test mutating only that field, which is a small coverage limitation rather than a behavior defect.

## Checks

Run on the exact `review_ref` `04aee3f6dc88f7338334d1d70a0fe51793c6911d`:

- Node `v22.18.0`, npm `10.4.0`.
- `npm test --prefix apps/web` — **28 passed**.
- `npm run build --prefix apps/web` — TypeScript typecheck and Vite production build passed.
- `git diff --check 133340376837620cff69a5b7d821f37c5c1c14d8 d08876d01903e73ad2ee6565a9ef3a9340d3828f -- apps/web` — passed.
- Comparison of the adapter, regression suite, and README between the exact review ref and current PR head — no changes.

## Integration boundary

At the last PR metadata read, PR #20 was open and `mergeable: false`; its base SHA `133340376837620cff69a5b7d821f37c5c1c14d8` lagged behind `origin/main` `35c71bea98c808e7b19419eb6a477648b467b5f`. Ewelina must synchronize her branch with current main, preserve the K-024 task status, then integrate the PR. E-003/E-020 remain in `review` until that integration. The backend still implements only `/api/v1/health`; this approval covers the UI adapter's response binding and tests, not a live search service or scientific results.
