# K-049 review — E-031 / PR #50

- Date: 2026-11-15
- Reviewer: Ewelina (`codex-ewelina-k049-review`)
- Exact matrix review ref: `8be43106baa2954f585ad275829787bf0d6f6ac2`
- Matrix content commit: `3d617310b039e84c6cac319c3d3fae10fd859726`
- PR: [#50](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/50), open; head equals the exact review ref.
- Snapshot declared by E-031: `origin/main` `e601d91a1184ea8ea0d8d198f5b3be1368c2ef7e`.
- Latest main when review began: `6aa9438c682358f252174348235521e2afe43345` (the K-049 reservation was then published as `a49d9afa1f68ccdd80fa8a2363efeebac981510e`).

## Verdict

**REQUEST CHANGES recommendation.** The matrix is careful about submission boundaries, but its E-021 refs and the statement about PR #35 synchronization are stale or inaccurate. Update the matrix and its handoff against the current main before using it as the current submission evidence snapshot.

## Findings

### P1 — E-021 evidence refs in the matrix and handoff are stale

The matrix and `handoffs/E-025-current-status-refresh.md` still identify E-021 render ref `765a4fce0426662806e8d0a5249492eb7ee8e1f0`, PR #35 head `676554f12ea2d66aab34f5cfdf2100c6d9db3057`, and base `cd0928ee7dbb9e6f8a06996c205351c46851baee`. On the current main, `tasks/E-021.md` pins render ref `bff33641cf44906ad3ad8fbe073e55cc6e3ccf42`; live PR #35 is open at head `a2087b0fde4bd2968cffcc34ab956839f7492c3b`, base `18803b793019069f87ce1fd2d51ebd78d24831e4`. The updated evidence includes the `.field-help` overlap correction and a fresh 320 px screenshot. E-021 remains in review and unintegrated; K-039's recommendation is not an independent formal approval.

**Owner:** Ewelina. **Acceptance:** refresh both the matrix and handoff from the latest `origin/main`, pin the current render ref and PR head/base, and keep the unintegrated and non-approved status explicit. Run the planning checker and diff check on the corrected exact tree.

### P2 — PR #35 synchronization statement contradicts its recorded snapshot

The matrix says PR #35 “is not synced to the current matrix snapshot” while declaring snapshot `e601d91a1184ea8ea0d8d198f5b3be1368c2ef7e`. PR #35's recorded base `18803b793019069f87ce1fd2d51ebd78d24831e4` descends from that snapshot, and its head includes that base. Thus it was based on a newer main than the matrix snapshot, not behind that snapshot. At review time, current main had advanced again to `6aa9438c682358f252174348235521e2afe43345`; distinguish this newer state from the older snapshot instead of calling the PR unsynced to `e601`.

**Owner:** Ewelina. **Acceptance:** state the precise matrix snapshot and PR base/head relationship, and identify any later main commits separately.

## Checks and remaining boundaries

- `python tools/check_planning.py` on the exact review tree: passed (181 Markdown files, 40 JSON files, 92 task cards, acyclic dependencies, five synthetic cases).
- `git diff --check` for the declared snapshot-to-review range `e601d91a1184ea8ea0d8d198f5b3be1368c2ef7e..8be43106baa2954f585ad275829787bf0d6f6ac2`: passed.
- The matrix covers the S03 fields and boundaries: event/title confirmation, English materials, demo limits and public access, NASA/source attribution, AI/SI, minors, release limitations, and human-only submission.
- K-042's measured pilot is kept distinct from the clean-clone downloader correction. PR #72's recorded clean-clone ref and current head are distinguished; its stale PR-description refs are called out. E-030 remains todo while PR #72 is not synchronized. K-005's merge and status refs, K-007's regional-only review state, I-012's unintegrated disclosure, and I-006's human-only boundary are consistent with the checked cards and PR metadata.
- K-042's pilot counters were cross-checked against its task/PR descriptions only; I did not independently regenerate raw data or support counts. They remain documented branch evidence, not an independent validation.
- This was a documentation and metadata review only: no application run, new scientific processing, anonymous public-link check, or submission was performed.

The connected GitHub account authored PR #50, so this report is a review recommendation, not a formal GitHub `APPROVE` event. The findings are being posted on PR #50 with a link to this report.
