# Handoff: E-025 current submission evidence refresh

- From: Ewelina, `codex-ewelina-e031-refresh-submission-matrix`
- To: Kamil
- Date: 2026-11-15
- Task / PR: E-031 follow-up to E-025 / [PR #50](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/50)
- Repository / work branch: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-031-refresh-submission-matrix`; PR #50 remains on `ewelina/E-025-submission-evidence-matrix`.
- Integrated snapshot checked: `origin/main` at `e601d91a1184ea8ea0d8d198f5b3be1368c2ef7e`.
- Exact matrix content commit: `3d617310b039e84c6cac319c3d3fae10fd859726` (`docs(E-031): refresh submission evidence snapshot`).
- Exact review ref: recorded in `tasks/E-025.md` on `origin/main` after this handoff is published; it points to the final PR #50 head.

## Current state and evidence

- E-005 controls are integrated and `done`; PR #31 merged as `00561365c7d42cd7ffd4083968adb5c386e81aca` after review of code ref `98be49cac38e6d72245a092e7a59bab7c5599424`.
- E-004 base map code is integrated by PR #37 (`f316db24d183bbbe2a9de05307fcb5b8fa446503`). Its latest visual finalization is unmerged in PR #83, exact head `8ef9060be576fb90f9c624b09148e6dc532ecb6f`, with K-048 assigned. A production preview confirmed the synthetic isolated hotspot and legend at a narrow viewport; the 4/4 fixture ranking persisted through zoom changes. There was no polar-data fixture, so this does not validate polar measurements.
- E-021 remains `review` in PR #35: evidence ref `765a4fce0426662806e8d0a5249492eb7ee8e1f0`, current head `676554f12ea2d66aab34f5cfdf2100c6d9db3057`, recorded base `cd0928ee7dbb9e6f8a06996c205351c46851baee`. The render check covers 320/375/390/780/782/1150/1151 CSS px. K-039's comment is not formal independent approval. The PR still needs synchronization to the current main before review.
- K-007 is `review`, not integrated. PR #70 has head `4f7e296624b7ea1e9889906c23b3b9fedcb94f4a`, recorded base `23c57b1331cde3eb0a98a644c81f32d4fab9f495`, and review ref `cd9caff3fb700cd6683c468b8937d815dcc5a1be`; its regional runs remain branch evidence.
- K-042's original measured pilot is `affcd909bf3ac343ecb3a6d96f45b2d40658dbea`: four 64×64 cores, 16,384 candidate cells, 13,912 eligible cells, and four output hashes matching the manifest. E-029 reproduced outputs only after manually creating ignored raw directories, then filed P1 review `5911195024` for the clean-clone downloader failure. The correction commit is `60da3d2e8f57113c87380b00302ccfe3cc6c52ec`; exact code review ref `935fb086ce874eb89b7ed9342ea8f7be4f458bda` is an ancestor of live PR #72 head `50d01f7a421bfc199c23e73a43cfc055e615bb55`. GitHub metadata reports base `1aa727de584a45fdbbf8b78249fbf392bb0ea781`, older than this snapshot. The PR description instead gives head/base `7e20e38b83fe84332c0b8a16d1651d22da9a245c` / `3af229563fad7a804d93b6f4f6c2b3effa3cbc80`; please synchronize the branch and refresh that description. K-042 is `review`; E-030 is `todo` and cannot start until the branch is synced and the correction is independently reviewed.
- I-012 is `review` in open PR #46 at exact correction ref `57c36d1c7d69c40ab14b97037238345224cf406b`; current head `de3813d30f44719fb8c1c4d6ce6c077e04602ca1`, recorded base `9fb81c35024c0e1a3db22d740a62ea3e62f3e737`. K-043 is `todo`, and its synchronization condition is not met. The disclosure remains unintegrated; it records 14 synthetic paths (12 with top-level `is_synthetic`, 1 with `ai_assisted`), no generated media, and no AI-generated measurements.
- The integrated API remains health-only; K-007's real regional search is not released. There is no public demo or deployment URL, no global build/ranking/coverage proof, no NASA endorsement, and no completed submission. K-044 remains the global ownership/seam gate. I-006 is `human_only`.

## Submission boundaries and next actions

S03 requires English form/materials; demo video up to 30 seconds or presentation up to 7 slides including title slides; public external links without sign-in for documents/videos; permitted direct image uploads only in JPG/PNG/GIF up to 10 MB; NASA resource and all source/tool citations; AI/SI disclosures; and no identifiable minors in submission media. The current project title and applicable event details still need human confirmation. No project-wide live workflow or submission package is ready to claim as complete.

Kamil: sync PR #72 to current main, update its stale description, then E-030 can start on the exact correction. Also synchronize PR #46 before K-043 and continue independent technical review/integration for E-004, E-021, and K-007. E-025 remains an internal evidence document, not submission material. No app run, new scientific processing, public-link check, or formal submission was performed for this documentation refresh.

## Review history

K-045 requested that the matrix add K-042 as unintegrated pilot evidence and refresh the integrated snapshot. K-046 then found the E-004/K-042 statuses and refs stale and requested this follow-up. The current matrix and E-025 task card preserve the integrated snapshot, open-PR evidence, exact refs and missing actions separately.
