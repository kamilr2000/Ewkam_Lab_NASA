# Handoff: E-025 current submission evidence refresh

- From: Ewelina, `codex-ewelina-e025-current-status-refresh`
- To: Kamil
- Date: 2026-11-15
- Task / PR / exact matrix commit: E-025 / [PR #50](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/50) / `7113bf1a1ce6edc655be4acaf741ab71ed18f1fb`
- Repository / branch: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-025-submission-evidence-matrix`
- Scope: internal English `submission/evidence-matrix.md`; status refresh after K-035 approved the previous exact matrix ref.
- Integrated base inspected: `origin/main` at `f86f8a67e5e0c8a2098573dda8641a93f9b9278a`.

## Updated facts

- E-005 controls and K-004/K-005 data work are integrated. PR #44 merged as `1fa00555a00f695afa947abd205104000d819f4a`; K-005 status commit is `25b10663baa984137a7c5e9effc8084188a9a2bb`, and corrected code fingerprint is `d3b880cacbbdf339d078a2fbedbe8fd373db7bef`.
- E-004 map code is integrated by PR #37 merge `f316db24d183bbbe2a9de05307fcb5b8fa446503`, but E-004 remains `review` because visual confirmation of map polygons, legend and full polar rendering is still missing.
- E-021 remains `review` in open PR #35. The current render/CSS ref is `765a4fce0426662806e8d0a5249492eb7ee8e1f0`; the PR head at inspection was `676554f12ea2d66aab34f5cfdf2100c6d9db3057`. Evidence covers actual widths 320/375/390/780/782/1150/1151, equal layout widths, no observed overflow/clipping/overlap, and visible keyboard focus at 320 px. K-039 posted a recommendation, but GitHub rejected formal approval because the connected account authored the PR; that recommendation is not independent approval.
- K-007's real regional API and runs are available only in open PR #70, exact review ref `cd9caff3fb700cd6683c468b8937d815dcc5a1be`. The reported Mars/Atacama and Moon/Hawaii top scores are restricted to those regional datasets and declared three-feature model; PR #70 is not integrated.
- I-012's latest disclosure correction is available only in open PR #46 at exact ref `57c36d1c7d69c40ab14b97037238345224cf406b`; it is `review` with K-043 assigned. Its synthetic inventory remains 14 paths (12/14 with top-level `is_synthetic`, 1/14 with top-level `ai_assisted`), no generated media, and no AI-generated measurements.
- There is no public demo or deployment URL, no global ranking, no NASA endorsement, and no completed formal submission. I-006 remains human-only.

## Checks and limits

The planning check, local-link audit, and `git diff --check` are recorded after they pass on the published branch. This is a documentation refresh only; no application run, new scientific processing, public-link availability check, or submission action was performed.

K-035 approved the previous snapshot `d755352240f003b7609104f500355c14df065251`. The changed status rows require a fresh review. K-044 is requested for exact matrix ref `7113bf1a1ce6edc655be4acaf741ab71ed18f1fb` after the task and review card are published on `origin/main`.
