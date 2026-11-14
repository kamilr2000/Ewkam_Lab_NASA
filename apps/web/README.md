# Terra Analog web app

The web client is a React + TypeScript application built with Vite. Its first screen establishes the workspace for an analysis; the search controls and results remain explicitly unavailable until the shared data API is connected. It does not calculate scientific scores in the browser or show sample values as measured results.

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

- MapLibre GL JS is included for the map implementation task. This scaffold intentionally loads no basemap, tiles, or fabricated result layer; a tile provider and its attribution/licensing must be reviewed before use.
- The controls are disabled and the empty states are deliberate. Connect them to the shared versioned API and its analysis IDs; do not add a second scoring implementation in this client.
- Product copy is English. Internal setup and scientific source documentation is maintained in the repository docs.
