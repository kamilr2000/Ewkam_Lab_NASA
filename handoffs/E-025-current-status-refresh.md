# Handoff: E-025 current submission evidence refresh

- From: Ewelina, `codex-ewelina-e025-k045-revision`
- To: Kamil
- Date: 2026-11-15
- Task / PR / exact matrix commit: E-025 / [PR #50](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/50) / `343df614dbadccef0dbf4eb3a66c0099f9313662`.
- Repository / branch: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-025-submission-evidence-matrix`
- Scope: internal English `submission/evidence-matrix.md`; status refresh after K-045 requested changes to the previous exact matrix ref.
- Integrated base inspected: `origin/main` at `5ab319437d7ec3994c77f1bc61b4664022f441d0`.

## Updated facts

- E-005 controls and K-004/K-005 data work are integrated. PR #44 merged as `1fa00555a00f695afa947abd205104000d819f4a`; K-005 status commit is `25b10663baa984137a7c5e9effc8084188a9a2bb`, and corrected code fingerprint is `d3b880cacbbdf339d078a2fbedbe8fd373db7bef`.
- E-004 map code is integrated by PR #37 merge `f316db24d183bbbe2a9de05307fcb5b8fa446503`, but E-004 remains `review` because visual confirmation of map polygons, legend and full polar rendering is still missing.
- E-021 remains `review` in open PR #35. The current render/CSS ref is `765a4fce0426662806e8d0a5249492eb7ee8e1f0`; the PR head at inspection was `676554f12ea2d66aab34f5cfdf2100c6d9db3057`. Evidence covers actual widths 320/375/390/780/782/1150/1151, equal layout widths, no observed overflow/clipping/overlap, and visible keyboard focus at 320 px. K-039 posted a recommendation, but GitHub rejected formal approval because the connected account authored the PR; that recommendation is not independent approval.
- K-007's real regional API and runs are available only in open PR #70, exact review ref `cd9caff3fb700cd6683c468b8937d815dcc5a1be`. The reported Mars/Atacama and Moon/Hawaii top scores are restricted to those regional datasets and declared three-feature model; PR #70 is not integrated.
- K-042 is `review` in open PR #72 at exact ref `affcd909bf3ac343ecb3a6d96f45b2d40658dbea`. The four complete 64×64 cores yielded 16,384 candidates and 13,912 eligible cells; 705,886 compressed output bytes and all four CSV.GZ hashes match the manifest. E-029 independently reproduced the outputs and controls at 63.14 s and 448,479,232 B peak working set after manually creating the ignored `data/raw` directories. E-029 published `REQUEST_CHANGES` review `5911195024`: the source downloader fails on a clean clone because the parent directory for the first `.part` file is not created. Full reproduction detail is in [E-029's report](E-029-review-K-042.md). K-044 remains the global cell ownership/seam gate.
- I-012's latest disclosure correction is available only in open PR #46 at exact ref `57c36d1c7d69c40ab14b97037238345224cf406b`; it is `review` with K-043 assigned. Its synthetic inventory remains 14 paths (12/14 with top-level `is_synthetic`, 1/14 with top-level `ai_assisted`), no generated media, and no AI-generated measurements.
- There is no public demo or deployment URL, no global ranking, no NASA endorsement, and no completed formal submission. I-006 remains human-only.

## Checks and limits

The planning check, local-link audit, and `git diff --check` are recorded after they pass on the published branch. This is a documentation refresh only; no application run, new scientific processing, public-link availability check, or submission action was performed.

K-045 reviewed prior matrix commit `7113bf1a1ce6edc655be4acaf741ab71ed18f1fb` and issued `REQUEST_CHANGES` review `5911168157`, requiring K-042 to be added as an unintegrated pilot and the integrated-base snapshot to be refreshed. E-025 correction is reserved on `origin/main` as `6b1bbece8989d299fc46dc181740e493cb5cd2df`. The refreshed matrix is exact commit `343df614dbadccef0dbf4eb3a66c0099f9313662` and points to the inspected integrated snapshot `5ab319437d7ec3994c77f1bc61b4664022f441d0`. It adds K-042's limited pilot evidence, records E-029's clean-clone P1, and preserves the no-global-ranking boundary. K-046 is the one required re-review for this corrected scope; its `review_ref` will be set on `origin/main` alongside E-025's transition to `review`.
