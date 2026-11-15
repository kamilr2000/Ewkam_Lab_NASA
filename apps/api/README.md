# API

Owner: Kamil. The API serves versioned reference profiles, three regional Earth datasets, regional search results, map aggregates, and pixel details. The API owns all scoring; the web client does not recalculate scores.

## Run locally

Requirements: Python 3.12 and uv. From the repository root:

```powershell
uv sync --locked --dev
uv run --locked python -m uvicorn apps.api.main:app --reload --workers 1
```

The API listens on http://127.0.0.1:8000. Open /docs for the interactive route reference.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/catalog
```

Use one worker. Analyses are held in process memory; a map or pixel-detail request routed to another worker cannot resolve the same analysis ID. Restarting the process clears stored analyses.

## Current data scope

Profiles: Mars Jezero, mars-jezero-mola128-v1; lunar south polar 80–90°S, moon-south-polar-80s-lola80-v1.

Earth search packages: Atacama / Andes, Hawaii Big Island, and Himalaya. Each request selects one catalogued package and dataset version. Search evaluates that regional package and returns either pixel ranking or distinct-area representatives. Global search is unavailable and returns SCOPE_UNAVAILABLE; the server does not silently replace it with a regional result.

The three criteria are surface slope (degrees), local roughness (metres), and local relief (metres). Missing active measurements remain unavailable with reasons. Map data preserve the winning pixel ID and are linked to the search analysis ID.

## Dependencies and limits

Exact Python dependency versions are pinned in the root pyproject.toml and uv.lock. The API is a regional MVP, not a global Earth scan. Its current in-memory analysis store is not suitable for multiple workers or durable public deployment.
