# Architecture

## Components and ownership

| Path | Responsibility | Owner |
|---|---|---|
| pipeline/ | Source downloads, coordinate handling, QA, profile extraction, regional features, and manifests | Kamil |
| apps/api/ | FastAPI catalogue, request validation, regional scoring, ranking, map data, and pixel details | Kamil |
| apps/web/ | React and TypeScript interface, MapLibre map, criteria, ranking, explanations, and API client | Ewelina |
| contracts/ | Versioned schemas, OpenAPI, fixtures, and contract tests | Kamil publishes; Ewelina consumes |
| data/ | Tracked manifests, reports, and compact derived regional packages | Kamil |
| design/ | Interaction and map handoffs | Ewelina |
| submission/ | English jury copy and demo materials | Ewelina |

## Data flow

Public Earth and planetary sources
→ reproducible pipeline and QA
→ versioned reference profiles and regional cell packages
→ API catalogue and regional analysis
→ pixel and distinct-area rankings plus map aggregation
→ web interface and selected-pixel explanation

The API owns scoring. The browser renders returned analyses; it must not implement a second scoring engine. A map-layer toggle affects presentation only and does not alter the query or ranking.

## Analysis identity and service limits

Every search has an analysis ID; map and detail requests resolve against that analysis. The current API stores analyses in process memory for a bounded period and has a one-worker requirement so follow-up requests reach the same store. Restarting the process invalidates those IDs. Multi-worker deployment requires a shared durable analysis store.

The current data scope is three regional Earth packages. Global requests fail explicitly with SCOPE_UNAVAILABLE; the service does not silently substitute one region. A future global pipeline will need separate coverage, scale, memory, and correctness evidence before a global claim is made.

## Map rendering

The web client uses MapLibre GL JS with an OpenStreetMap tile basemap. Keep visible attribution and respect the tile usage policy. OSM is a cartographic reference layer, not an analysis input. Result cells and ranked markers have independent visibility state. Basemap failure must not hide the ranking, pixel details, or analysis errors.

The map is a display of API output. Its zoom level does not refine the source grid. Preserve a winning pixel ID through aggregation so an isolated hotspot remains selectable and explainable.

## Dependencies and reproducibility

Python dependencies are pinned in the root pyproject.toml and uv.lock; web dependencies are pinned in apps/web/package.json and apps/web/package-lock.json. Raw downloads are kept out of Git. Versioned manifests, compact derived packages, and reports provide source and checksum evidence.
