# K-039 — Re-review E-021 render proof

Date: 2026-11-15
Decision: **RECOMMEND APPROVE** for the reviewed UI readability and responsive-render scope. This review does not mark E-021 done or merge PR #35.

## Reviewed refs

- Exact E-021 review ref: `765a4fce0426662806e8d0a5249492eb7ee8e1f0`.
- Current PR #35 head: `676554f12ea2d66aab34f5cfdf2100c6d9db3057`.
- Current base: `origin/main` `cd0928ee7dbb9e6f8a06996c205351c46851baee`.
- Git ancestry check: the current main tip and exact review ref are both ancestors of the PR head. GitHub currently reports the PR as open and `mergeable=true`.
- The diff from the exact review ref to the current PR head changes task status/history only; the reviewed CSS and render evidence are unchanged.

## Findings

No blocking or actionable code findings in the reviewed scope. The previous P1 request for fresh post-sync viewport and keyboard-focus evidence is satisfied.

The current production preview evidence uses the synthetic `Successful ranking` fixture and does not call the live API. At each listed actual CSS width, all four document width measurements match; the handoff records no horizontal overflow, clipped text, or overlapping labels.

| Actual CSS viewport | `innerWidth` | `clientWidth` | `scrollWidth` | `body.scrollWidth` | Visual inspection |
|---:|---:|---:|---:|---:|---|
| 320 | 320 | 320 | 320 | 320 | Pass |
| 375 | 375 | 375 | 375 | 375 | Pass |
| 390 | 390 | 390 | 390 | 390 | Pass |
| 780 | 780 | 780 | 780 | 780 | Pass |
| 782 | 782 | 782 | 782 | 782 | Pass |
| 1150 | 1150 | 1150 | 1150 | 1150 | Pass |
| 1151 | 1151 | 1151 | 1151 | 1151 | Pass |

At 320 px, keyboard Tab navigation showed the configured 2 px `:focus-visible` outline on the focused select. The refreshed handoff links three screenshots (320, 782, and 1151 px) and the machine-readable metrics JSON. The viewport pair at 780/782 straddles the `max-width: 780px` breakpoint; it makes no claim to have measured exactly 781 px.

Static CSS review found no text font declarations below 9 px. Recomputed representative foreground/background sRGB contrasts agree with the handoff; the lowest checked pair is 4.68:1. This review covers text pairs and the declared font-size floor, not every icon, border, interactive state, or the full E-008 accessibility audit.

## Checks on current PR head

- `npm test --prefix apps/web` — 40/40 passed.
- `npm run build --prefix apps/web` — typecheck and production Vite build passed. Vite reports the async map chunk at 1,085.35 kB minified.
- `python tools/check_planning.py` — passed (166 Markdown, 41 JSON, 83 task cards, DAG/dependency checks and five synthetic cases).
- `git diff --check origin/main...HEAD` — clean.
- Production preview measurements and visual/focus inspection are recorded in the [E-021 handoff](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/E-021-ui-readability/handoffs/E-021-ui-readability.md), with [machine-readable metrics](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/E-021-ui-readability/handoffs/e021-viewport-metrics-2026-11-15.json), [320 px screenshot](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/E-021-ui-readability/handoffs/screenshots/E-021-320px-2026-11-15.png), [782 px screenshot](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/E-021-ui-readability/handoffs/screenshots/E-021-782px-2026-11-15.png), and [1151 px screenshot](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/E-021-ui-readability/handoffs/screenshots/E-021-1151px-2026-11-15.png).

## Limitations and disposition

No physical phone was tested and a classic non-overlay scrollbar was not forced. The preview shows synthetic fixture data, not scientific results. These limitations are explicit and do not block the stated E-021 acceptance criteria.

The old PR description incorrectly said that current render evidence was missing. It has been refreshed to point to the current ref and proof. No owner follow-up is needed for the reviewed scope. E-021 remains `review` until Kamil integrates and accepts it on `origin/main`.

GitHub rejected the formal `APPROVE` review with HTTP 422 because the connected account authored PR #35. The review outcome and evidence were therefore published as PR comment [6895059234](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/35#issuecomment-6895059234), anchored in its text to current head `676554f12ea2d66aab34f5cfdf2100c6d9db3057`.
