# API

Owner: Kamil. The API serves versioned reference profiles, three regional Earth datasets, regional search results, map aggregates, and pixel details. It owns all scoring; the web client does not recalculate scores.

## Run locally

Requirements: Python 3.12 and uv. From the repository root:

```powershell
uv sync --locked --dev
uv run --locked python -m uvicorn apps.api.main:app --reload --workers 1
```

The API listens on `http://127.0.0.1:8000`. Open `/docs` for the interactive route reference.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/catalog
```

Use one worker. Analyses are kept in process memory for one hour, up to 16 at a time. A map or pixel-detail request routed to another worker cannot resolve the same analysis ID, and a process restart clears stored analyses. Multiple workers require a shared persistent analysis store.

## Browser access from another origin

By default, browser requests are allowed only from the local Vite origins `http://localhost:5173` and `http://127.0.0.1:5173`. To allow a different frontend origin, set `TERRA_ANALOG_CORS_ORIGINS` to a comma-separated list of exact HTTP(S) origins without paths or wildcards. If unset, the local defaults apply; an explicitly empty value disables cross-origin access. The API permits GET and POST with the `Content-Type` header and does not allow cookies or credentials. CORS is a browser access rule, not API authentication.

Start the API in one terminal:

```powershell
uv run --locked python -m uvicorn apps.api.main:app --reload --workers 1
```

In a second terminal, from `apps/web`, point the frontend at the API and run Vite:

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

For a deployed split-origin setup, set the API allow-list to the exact frontend origin (for example, `https://demo.example`) and set `VITE_API_BASE_URL` to the API origin. Do not include a path or trailing slash in either value.

## Current data scope

Reference profiles: Mars Jezero (`mars-jezero-mola128-v1`) and the lunar south polar region, 80–90°S (`moon-south-polar-80s-lola80-v1`). Earth search packages: Atacama / Andes (`k005-earth-2km-atacama-andes-v2`), Hawaii Big Island (`k005-earth-2km-hawaii-big-island-v2`), and the Himalaya (`k005-earth-2km-himalaya-v2`). Each request selects one catalogued package and version.

`POST /api/v1/search` evaluates the selected regional package and returns either a pixel ranking or distinct-area representatives, plus map cells. The three criteria are surface slope (degrees), local roughness (metres), and local relief (metres). Missing active measurements remain unavailable with reasons. Map records retain the winning pixel ID and analysis ID.

Global search is unavailable and returns `SCOPE_UNAVAILABLE`; the server does not silently substitute a regional result. A regional ranking is not a global optimum.

## Map and data handling

The analysis map endpoint accepts `bbox=west,south,east,north`, `level` 0–30, and optional `limit` and `cursor`. `level` is the XYZ Web Mercator zoom. Tile averages are area-weighted; `max_pixel_id` identifies a pixel with the corresponding value. A tile that intersects the requested bbox may also contain cells outside the bbox if they fall within the same tile.

The health endpoint verifies the size and SHA-256 of the three tracked K-005 packages. It reports `dataset_ready: true` when those files pass integrity checks; `dataset_version` is `null` because the regional packages have separate immutable versions.

## Dependencies and limits

Exact Python dependency versions are pinned in the root `pyproject.toml` and `uv.lock`. The documented test environment uses Python 3.12.14, FastAPI 0.162.7, NumPy 2.5.4, Rasterio 1.5.2, pyproj 3.8.0, and Uvicorn 0.54.0. The API is a regional MVP, not a global Earth scan or a durable multi-worker service. K-008 covers global processing, full coverage, scale measurements, and global map aggregates.
