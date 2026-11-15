# Handoff: E-025 current submission evidence refresh

- From: Ewelina, `codex-ewelina-e031-current-snapshot-correction`
- To: Kamil
- Date: 2026-11-15
- Task / PR: E-031 follow-up to E-025 / [PR #50](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/50)
- Repository / work branch: `kamilr2000/Ewkam_Lab_NASA`, PR #50 head branch `ewelina/E-025-submission-evidence-matrix`.
- Integrated snapshot checked: `origin/main` at `3bdefd34018f6f219bd6b8a97792771c87769d50`.
- Exact matrix content commit: pending the current correction commit.
- Exact review ref: the corrected matrix commit will be pinned in `tasks/E-025.md` on `origin/main` after publication.

## Current state and evidence

- E-005 controls are integrated and `done`; PR #31 merged as `00561365c7d42cd7ffd4083968adb5c386e81aca` after review of code ref `98be49cac38e6d72245a092e7a59bab7c5599424`.
- E-004 base map code is integrated by PR #37 (`f316db24d183bbbe2a9de05307fcb5b8fa446503`). Its latest visual finalization is unmerged in PR #83, exact head `8ef9060be576fb90f9c624b09148e6dc532ecb6f`; K-048 is in progress. A production preview confirmed the synthetic isolated hotspot and legend at a narrow viewport; the 4/4 fixture ranking persisted through zoom changes. There was no polar-data fixture, so this does not validate polar measurements.
- E-021 remains `review` in PR #35: evidence ref `bff33641cf44906ad3ad8fbe073e55cc6e3ccf42`, current head `a2087b0fde4bd2968cffcc34ab956839f7492c3b`, recorded base `18803b793019069f87ce1fd2d51ebd78d24831e4`. The updated production evidence covers 320/375/390/780/782/1150/1151 CSS px, no horizontal overflow, overlap corrected by the `.field-help` spacing change, visible focus at 320 px, and a fresh 320 px screenshot. K-039's recommendation is not a formal independent approval. PR #35's base includes the earlier `e601d91` matrix snapshot but predates refreshed snapshot `3bdefd34018f6f219bd6b8a97792771c87769d50`; it remains open and needs synchronization to this latest main before independent review.
- K-007 is `review`, not integrated. PR #70 has head `4f7e296624b7ea1e9889906c23b3b9fedcb94f4a`, recorded base `23c57b1331cde3eb0a98a644c81f32d4fab9f495`, and review ref `cd9caff3fb700cd6683c468b8937d815dcc5a1be`; its regional runs remain branch evidence.
- K-042's original measured pilot is `affcd909bf3ac343ecb3a6d96f45b2d40658dbea`: four 64×64 cores, 16,384 candidate cells, 13,912 eligible cells, and four output hashes matching the manifest. E-029 reproduced outputs only after manually creating ignored raw directories, then filed P1 review `5911195024` for the clean-clone downloader failure. The correction commit is `60da3d2e8f57113c87380b00302ccfe3cc6c52ec`; exact code review ref `935fb086ce874eb89b7ed9342ea8f7be4f458bda` is an ancestor of live PR #72 head `50d01f7a421bfc199c23e73a43cfc055e615bb55`. GitHub metadata reports base `1aa727de584a45fdbbf8b78249fbf392bb0ea781`, older than this snapshot. The PR description instead gives head/base `7e20e38b83fe84332c0b8a16d1651d22da9a245c` / `3af229563fad7a804d93b6f4f6c2b3effa3cbc80`; please synchronize the branch and refresh that description. K-042 is `review`; E-030 is `todo` and cannot start until the branch is synced and the correction is independently reviewed.
- I-012 is `review` in open PR #46 at exact correction ref `57c36d1c7d69c40ab14b97037238345224cf406b`; current head `de3813d30f44719fb8c1c4d6ce6c077e04602ca1`, recorded base `9fb81c35024c0e1a3db22d740a62ea3e62f3e737`. K-043 is `todo`, and its synchronization condition is not met. The disclosure remains unintegrated; it records 14 synthetic paths (12 with top-level `is_synthetic`, 1 with `ai_assisted`), no generated media, and no AI-generated measurements.
- The integrated API remains health-only; K-007's real regional search is not released. There is no public demo or deployment URL, no global build/ranking/coverage proof, no NASA endorsement, and no completed submission. K-044 remains the global ownership/seam gate. I-006 is `human_only`.

## Submission boundaries and next actions

S03 requires English form/materials; demo video up to 30 seconds or presentation up to 7 slides including title slides; public external links without sign-in for documents/videos; permitted direct image uploads only in JPG/PNG/GIF up to 10 MB; NASA resource and all source/tool citations; AI/SI disclosures; and no identifiable minors in submission media. The current project title and applicable event details still need human confirmation. No project-wide live workflow or submission package is ready to claim as complete.

Kamil: sync PR #72 to current main, update its stale description, then E-030 can start on the exact correction. Also synchronize PR #46 before K-043 and continue independent technical review/integration for E-004, E-021, and K-007. E-025 remains an internal evidence document, not submission material. No app run, new scientific processing, public-link check, or formal submission was performed for this documentation refresh.

## Review history

K-045 requested that the matrix add K-042 as unintegrated pilot evidence and refresh the integrated snapshot. K-046 then found the E-004/K-042 statuses and refs stale and requested this follow-up. The current matrix and E-025 task card preserve the integrated snapshot, open-PR evidence, exact refs and missing actions separately.

K-049 reviewed exact matrix ref `8be43106baa2954f585ad275829787bf0d6f6ac2` and returned a `REQUEST CHANGES` recommendation: the E-021 refs were stale, and the statement that PR #35 was unsynced to the older `e601d91` snapshot was inaccurate. The [K-049 report](K-049-review-E025.md) records the comparisons, checks and limits. E-031 was re-reserved to correct both documents against current `origin/main` snapshot `3bdefd34018f6f219bd6b8a97792771c87769d50` before another review.