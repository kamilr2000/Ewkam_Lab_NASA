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
- **Live API** mode requests the shared endpoints. Set `VITE_API_BASE_URL` to an absolute API origin when it is hosted separately; otherwise the client uses the current origin. Catalog, profile, search, map-cell, and pixel-detail paths follow `contracts/openapi.yaml`. As of K-003, only `/api/v1/health` is implemented, so the other live requests currently return an explicit API error.
- The adapter checks response contract versions, required envelope fields, score ranges, and whether a live search echoes the requested dataset, query scope, top-level result scope, profile, criteria and normalized weights, ranking mode and size, and distance. Map responses must echo the requested bbox, level, and limit in both live and synthetic modes; map/pixel details must also belong to the requested `analysis_id`. A live mismatch raises an explicit API error and never switches to a fixture.
- Run `npm test` from `apps/web/` to exercise the adapter's positive and negative request-echo cases without a live backend. These tests use synthetic fixtures as controlled response payloads and do not represent scientific measurements.
- MapLibre GL JS is included for the map implementation task. This E-003 view shows the response's map-cell summary but intentionally loads no basemap, tiles, or fabricated result layer. A tile provider and its attribution/licensing must be reviewed before map rendering is implemented.
- Product copy is English. Internal setup and scientific source documentation is maintained in the repository docs.
