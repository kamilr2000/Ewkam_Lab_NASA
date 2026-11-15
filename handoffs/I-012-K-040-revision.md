# I-012 — refreshed disclosure after K-040

Date: 2026-11-15  
Base used: `origin/main` at reservation `c474a93cd859fcf77d4eb354f6160038a563d708`.  
Previous review ref: `3a7a313960a713c168f31caf63eaf83bef097c6e`; K-040 returned `REQUEST_CHANGES` (review `5910708916`).

## Corrections

- Corrected the K-005 status commit in the disclosure and JSON. The status commit is `25b10663baa984137a7c5e9effc8084188a9a2bb`; `7deddad9f992ef69c13248195747349a283ce54b` is not the K-005 status commit. PR #44 merged as `1fa00555a00f695afa947abd205104000d819f4a`; K-005 is `done`.
- Replaced the stale E-021 state with its current state: the render/CSS ref is `765a4fce0426662806e8d0a5249492eb7ee8e1f0`, current PR #35 head is `676554f12ea2d66aab34f5cfdf2100c6d9db3057`, and E-021 is `review`, not integrated. Current synthetic-fixture evidence covers actual widths 320/375/390/780/782/1150/1151, document widths match, no clipping/overlap/overflow was observed, and keyboard focus is visible at 320 px.
- Recorded K-039's recommendation and the GitHub limitation accurately: review evidence is in [K-039 report](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/K-039-review-e021/handoffs/K-039-review-E021.md) and [PR #35 comment](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/35#issuecomment-6895059234). GitHub rejected formal `APPROVE` because the connected account authored PR #35. This is not an independent approval and does not change E-021's `review` state.
- Removed reliance on transient PR `mergeable` metadata. PR state, reviewed SHA and integration status are recorded separately.
- Updated the I-012 correction history and marked the prior K-038 handoff as historical; this report is the current source for the K-040 follow-up.

## Other verified boundaries

- E-005 is `done`; PR #31 merged as `00561365c7d42cd7ffd4083968adb5c386e81aca`. The API still exposes only `GET /api/v1/health`.
- E-004 is `review` after PR #37 merged as `f316db24d183bbbe2a9de05307fcb5b8fa446503` and K-032 approved the lazy-load ref. Current visual map/polygon/legend and full polar rendering are still not confirmed.
- E-023 is a review of the K-004 regional profiles; PR #36 merged as `4301744bddab0bfc56b6dc8c7908d4f8849df890`.
- E-024's `REQUEST_CHANGES` was for the historical K-005 fingerprint. E-026 approved correction `d3b880cacbbdf339d078a2fbedbe8fd373db7bef` before PR #44 was integrated.
- The 14-path synthetic inventory remains central; top-level `is_synthetic: true` appears in 12/14 fixtures and `ai_assisted: true` in 1/14. `generated_media` is empty and `measurements_generated_by_ai` is false.
- No global result, NASA endorsement, public live workflow, or completed submission is claimed. I-006 remains human-only.

## Checks

The exact correction ref and reproducible checks will be appended after the disclosure commit is recorded. Re-review will be requested from Kamil on the new exact ref before I-012 is marked `done` or integrated.
