# K-023 review — I-011 AI/SI disclosure

- Reviewer: Kamil (`codex-kamil-k023-review-i011`)
- Date: 2026-11-15, Europe/Warsaw
- Reviewed task/PR: K-023 / [PR #22](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/22)
- Exact `review_ref`: `9855b1d8347dc8a4a5582b066d672798a15ae9df`
- Current PR head checked: `0a85e337e80b5bc4fe194c629ebb65e14fec668d`; the two disclosure files are unchanged from the exact review ref.
- Result: **REQUEST_CHANGES, P1**, GitHub review `5908252660`.
- Owner of correction: Ewelina, within I-011 / PR #22.

## Finding — P1: current E-020 review state is stale

At the declared `review_ref`, the sentence that E-020 was under K-021 review matched the task state at that point. By the current PR head, however, K-021 had completed and published **REQUEST_CHANGES** on PR #20 for a P0 response-scope binding gap. `docs/AI_USAGE.md` and `docs/ai-usage.json` still say the corrections are under K-021 review. Update both summaries to reflect the K-021 finding and the next review state.

After the inline review was submitted, Ewelina published correction commit `04aee3f6dc88f7338334d1d70a0fe51793c6911d`; K-024 now tracks its re-review. The review thread was updated to reflect that new state. The backend remains health-only until the relevant API implementation is integrated.

## Claims checked

- K-003 is integrated and its contract fixtures are synthetic; only `/api/v1/health` is implemented in the backend.
- K-006's 71 scoring/contract tests and E-018 approval are documented with their synthetic-data and global-coverage limits.
- K-017 reports four NASADEM HGT/SWB tiles and three AOI comparisons in unmerged PR #12. E-017 approved the documented scope but could not reread the raw assets or reproduce the AOI metrics.
- The JSON lists all 14 contract fixture JSON files in the reviewed snapshot. The fixtures are not reported as measurements.
- The E-019 SVG is described as a code-authored synthetic schematic. Generated photo/video/audio media remains empty; AI is not credited with producing scientific observations, licensing, NASA endorsement, or a submission.
- K-019's adapter findings and the later E-020 work are described as UI validation, not as a working live search backend.

## Checks

- `python tools/check_planning.py` on an isolated export of the exact `review_ref` — passed: 108 Markdown files, 30 JSON files, 53 task cards, acyclic dependencies, five synthetic cases.
- `python -m json.tool docs/ai-usage.json` on the same snapshot — passed.
- `git diff --check b44646343f0a35ae4158b9a04b5d75f2349d6ca6 9855b1d8347dc8a4a5582b066d672798a15ae9df -- docs/AI_USAGE.md docs/ai-usage.json tasks/I-011.md` — passed.

The review did not fetch or reread NASADEM raw products; it checks the disclosure against the published task cards and review reports, not the raw scientific bytes.
