# Terra Analog web app

The web client is a React + TypeScript application built with Vite. It reads contract `1.0.0` catalog/profile/search fixtures from `contracts/fixtures/` and includes an explicit live API mode. It never calculates scientific scores in the browser and never substitutes fixture responses after a live API failure.

## Requirements

- Node.js 22.12 or newer (Vite 8 requirement)
- npm 10 or newer

## Local development

From `apps/web/`:

```sh
npm ci
npm run dev
```

Vite prints the local URL. Build and type-check with:

```sh
npm run build
npm run preview
```

`npm run build` runs TypeScript checking before creating the production bundle in `dist/`. `npm run preview` serves that bundle locally for a production-build check.

## Integration notes

- The default **Synthetic fixture demo** mode is visibly labeled and offers success, empty-scope, no-data, isolated-hotspot, distinct-area, and dataset-unavailable fixtures. These are fixed contract examples, not measured planetary data or a live scoring service.
- **Live API** mode requests the versioned catalog, profile, regional search, and map-cell endpoints. The K-007 API serves three declared Earth search regions: Atacama/Andes, Big Island, and Himalayas; each selection pins a dataset version and region ID. Global Earth search is not published and returns an explicit SCOPE_UNAVAILABLE error. The browser never falls back to fixtures after a live request fails.
- Set VITE_API_BASE_URL to an absolute API origin when hosted separately; otherwise the client uses the current origin. A separately hosted API must allow the web origin through CORS or be exposed through a same-origin reverse proxy. The current API app has no CORS middleware configured.
- The adapter checks response contract versions, required envelope fields, score ranges, and whether a live search echoes the requested dataset, query scope, top-level result scope, profile, criteria and normalized weights, ranking mode and size, and distance. Map responses must echo the requested bbox, level, and limit in both live and synthetic modes; map/pixel details must also belong to the requested `analysis_id`. A live mismatch raises an explicit API error and never switches to a fixture.
- Run `npm test` from `apps/web/` to exercise the adapter's positive and negative request-echo cases without a live backend. These tests use synthetic fixtures as controlled response payloads and do not represent scientific measurements.
- The map renders API display-cell maxima and ranked pixel markers; live viewport requests use the same analysis_id. OpenStreetMap raster tiles provide geographic context only and never enter the score. Visible attribution links to the OSM copyright/license page. The public tile service is best-effort; the app requests the visible viewport only and does not prefetch or offer offline tiles. Zoom changes the view, not measurement resolution. No satellite imagery layer is connected.
- OpenStreetMap data is available under ODbL; follow the [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/) and [copyright/license terms](https://www.openstreetmap.org/copyright). The npm dependency license does not grant map-tile rights.
- Product copy is English. Internal setup and scientific source documentation is maintained in the repository docs.
