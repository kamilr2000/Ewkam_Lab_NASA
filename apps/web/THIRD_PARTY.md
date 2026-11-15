# Web dependencies

Direct runtime and build dependencies are pinned in `package.json` and `package-lock.json`.

| Package | Version | Use | License |
|---|---:|---|---|
| React | 19.3.1 | UI runtime | MIT |
| React DOM | 19.3.1 | Browser rendering | MIT |
| MapLibre GL JS | 6.18.0 | Interactive globe and raster/vector map layers | BSD-3-Clause |
| Vite | 8.3.8 | Development server and production bundler | MIT |
| `@vitejs/plugin-react` | 6.3.0 | React transform for Vite | MIT |
| TypeScript | 7.0.2 | Type checking | Apache-2.0 |
| `@types/react`, `@types/react-dom` | 19.2.14, 19.2.3 | React type definitions | MIT |

Versions and package license metadata were checked against the npm registry on 2026-11-14. The map uses visible-viewport tiles from the OpenStreetMap standard raster endpoint. OSM attribution is shown in the map and links to the [copyright and license page](https://www.openstreetmap.org/copyright); tile requests follow the [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/). Tile service availability is best-effort. No satellite provider or NASA imagery layer is connected. The MapLibre package license does not grant rights to map tiles or data.
