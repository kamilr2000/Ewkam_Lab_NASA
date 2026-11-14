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

- `npm run build --prefix apps/web` passed: TypeScript check and Vite production build.
- Served the production build locally and checked it in headless Chrome 157.0.8103.78 at 320, 375, 390, 780, 781, 1150, and 1151 CSS px.
- At every width, `document.documentElement.scrollWidth <= innerWidth`; no visible element had a right edge beyond the viewport.
- Keyboard Tab showed a 2 px visible focus outline on the first link at every width.
- Both selects and the analysis button remained disabled, matching the unconnected API scaffold.

| Viewport | `scrollWidth` | `innerWidth` | Right-edge overflow |
| ---: | ---: | ---: | :--- |
| 320 | 320 | 320 | none |
| 375 | 375 | 375 | none |
| 390 | 390 | 390 | none |
| 780 | 765 | 780 | none |
| 781 | 766 | 781 | none |
| 1150 | 1135 | 1150 | none |
| 1151 | 1136 | 1151 | none |

The 15 px difference at 780 px and wider is the headless browser's vertical scrollbar; the document remains within the viewport.

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

This is a desktop headless-browser check of the production build. It does not claim physical-device, screen-reader, or full accessibility-audit coverage; E-008 remains responsible for the broader UX/accessibility audit. The frontend still has no connected analysis API or real measurements.
