# Handoff: E-014 — mobile layout fix

- Owner: Ewelina
- Review requested from: Kamil
- Related implementation: PR #5, `ewelina/E-002-information-flow`
- Build artifact reviewed: production preview from the E-014 branch
- Scope: responsive layout only; no API, scoring, or data changes

## Changes

- Stacked target/profile labels and selects in their reading order on widths up to 780 CSS px.
- Kept each criterion on its own row at phone widths, with the full name, unit, and `CORE` state visible.
- Added min-width guards to the workspace and selects so intrinsic text widths cannot force horizontal page overflow.
- Allowed map coordinates to wrap, reserved room for the upper-right grid label, and wrapped the phone toolbar when needed.
- Preserved the explicit disconnected-service, empty-map, empty-ranking, and disabled-control states.

## Verification

- `npm run build --prefix apps/web` passed after the overflow fix: TypeScript check and Vite production build.
- Served the production build locally in Chrome on Windows. Each width was rendered in a fixed-width iframe with a classic 15 CSS px vertical scrollbar, matching the review case; the acceptance check is `document.documentElement.scrollWidth <= document.documentElement.clientWidth`.
- At all seven widths, document and body `scrollWidth` equal `clientWidth`; no inspected body element extends beyond the usable viewport.
- Programmatic keyboard-visible focus on the first link produced a solid outline at every width. Computed outline width was 1.6 CSS px in this browser context (the stylesheet declares 2px).
- Both selects and the analysis button remained disabled, matching the unconnected API scaffold.

| Viewport | `innerWidth` | `clientWidth` | `scrollWidth` | Right-edge overflow |
| ---: | ---: | ---: | ---: | :--- |
| 320 | 320 | 305 | 305 | none |
| 375 | 375 | 360 | 360 | none |
| 390 | 390 | 375 | 375 | none |
| 780 | 780 | 765 | 765 | none |
| 781 | 781 | 766 | 766 | none |
| 1150 | 1150 | 1135 | 1135 | none |
| 1151 | 1151 | 1136 | 1136 | none |

The 15 px reduction from `innerWidth` to `clientWidth` is the visible classic vertical scrollbar. The previous check compared with `innerWidth` and missed this usable-width failure at 320 px; this check now compares against `clientWidth`.

## Screenshots

- [320 px](screenshots/E-014-320px.png)
- [375 px](screenshots/E-014-375px.png)
- [390 px](screenshots/E-014-390px.png)
- [780 px](screenshots/E-014-780px.png)
- [781 px](screenshots/E-014-781px.png)
- [1150 px](screenshots/E-014-1150px.png)
- [1151 px](screenshots/E-014-1151px.png)
- [Viewport measurements](e014-viewport-metrics.json)

## Limits

This is a desktop-browser check of the production build using fixed-width iframes with classic scrollbars. The seven screenshots above were refreshed after the 320 px correction; each shows the iframe viewport crop. It does not claim physical-device, screen-reader, or full accessibility-audit coverage; E-008 remains responsible for the broader UX/accessibility audit. The frontend still has no connected analysis API or real measurements. Updated scrollbar/client-width measurements are in `e014-viewport-metrics.json`.
