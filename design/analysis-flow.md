# Analysis flow and information hierarchy

Status: E-002 design artifact. It describes the intended interface; it does not claim that the API, map, measurements, or analysis are connected.

## Main journey

1. **Choose a target.** Select Mars or Moon, then a named reference profile. Show the profile version and body beside its name. Keep the analysis action unavailable until the catalog confirms a valid profile.
2. **Choose terrain criteria.** List only criteria available for that profile. For each criterion, expose two separate controls: **Include in score** and **Show on map**. The score control accepts a positive weight; a hidden map layer can still affect the score, and a visible layer can be excluded from it.
3. **Run the analysis.** Summarize the active criteria and their normalized weights immediately above the action. The pending state keeps the current result visible only as historical and labels it with its earlier `analysis_id`; never present it as the response to the new request.
4. **Read the global pixel ranking.** Show `Top 10 pixels` first. Each row is one qualifying analysis-grid cell, with its score index, location, area, and a clear selection action. Nearby cells may occupy multiple ranks.
5. **Inspect a cell.** Selecting a row moves the map to the exact cell and opens its details for the same `analysis_id`. Show its true outline and area, source/grid resolution, feature window, measurements and units, reference interval, similarity, normalized weight, contribution, sources, coverage, and quality flags.
6. **Explore spatially.** Keep the map legend and selected pixel visible. At overview zoom, color each map bucket by the maximum combined score of a real pixel and identify `max_pixel_id`; show the mean only as a separate context value. Zoom changes the displayed geography, not the analysis grid or source resolution.
7. **Optionally compare distinct places.** Switch to a separate `Distinct areas` list with its explicit minimum distance in kilometres and representative-selection explanation. Provide a direct way back to `Top 10 pixels`; never replace or filter the pixel ranking silently.

## Desktop and tablet layout

At wide widths, use a two-column workspace:

```text
┌──────────────────────────────┬─────────────────────────────────────────┐
│ Target and criteria          │ Analysis status · active analysis ID   │
│ body → profile               ├─────────────────────────────────────────┤
│ include + weight + map toggle│                                         │
│ run analysis                 │ Map, legend, selected pixel outline     │
│                              │                                         │
├──────────────────────────────┼────────────────────┬────────────────────┤
│                              │ Top 10 pixels      │ Pixel explanation  │
└──────────────────────────────┴────────────────────┴────────────────────┘
```

Keep setup controls in a labelled panel. The map is the primary result surface; ranking and explanation remain adjacent below it or in a stable side panel when the viewport allows. At tablet widths, stack ranking and explanation before reducing their text size. Do not put the explanation only in a hover tooltip.

## Phone layout

Use one column in this order: target and profile → criteria and weights → run/status → map → result-mode tabs → ranking → selected pixel details. Keep the map controls reachable and let the map use the available viewport height. Selecting a result scrolls or opens the detail panel without losing the selected row; provide a labelled close/back control. Avoid side-by-side criterion cards when their names or units would truncate.

## Result and scale language

- Label `score_pct` as **Similarity index**, followed by the percent value. Explain that it is a score for the selected features, not probability, habitability, or complete environmental equivalence.
- Label a ranked result **Pixel** or **analysis-grid cell**, never a map-screen pixel. Show `pixel_area_km2`, `grid_version`, source resolution, and feature-window scale as distinct quantities.
- Use **Map overview** for zoomed-out aggregate buckets. Describe the default color as the highest combined score among real pixels in the bucket; never imply that every part of the bucket has that score.
- Keep the topography-only scope note beside criteria and in the explanation: the three P0 criteria are related topographic measures and do not constitute a full environmental comparison.
- Use `null` values as **No data** with the supplied reason. Do not render missing score, measurement, coverage, or map maximum as 0 or as a favorable color.
- Show a `Synthetic example` label on all fixture-backed results, including the map, ranking, and details.

## Interaction and keyboard behavior

- Use native labelled selects, checkboxes, numeric weight inputs, buttons, tabs, and links. Tab order follows the journey from target through criteria to analysis and results.
- Group each feature's inclusion, weight, and map visibility under one accessible feature name; announce weight bounds and validation errors in text.
- Give each ranking row a button such as `Open pixel <pixel_id> details`; Enter and Space activate it. The selected row has a non-color indicator and visible focus state.
- When selection changes, announce the pixel ID and rank through a polite live region. Do not steal keyboard focus from the activating row; if details open in a dialog, move focus into it and return focus on close.
- Give map actions explicit accessible names (zoom in, zoom out, reset view). Provide the ranking and pixel details as a complete non-map path to the same data.
- Represent pending, empty, failure, no-data, and synthetic states with text and semantics, not color alone. Preserve visible focus and sufficient contrast at 320 CSS pixels.

## State copy and behavior

| State | Visible message | Behavior |
|---|---|---|
| Catalog loading | `Loading profiles and available criteria…` | Disable analysis; expose `aria-busy` on the setup/results region. |
| No compatible profile | `No profiles are available for this body yet.` | Keep criteria empty; do not invent a default profile or values. |
| Ready to run | `Ready to analyze <profile>.` | Enable the action only with a profile and at least one valid, included criterion. |
| Analysis pending | `Analyzing the global eligible grid…` | Keep prior results visibly marked as previous; prevent duplicate submission or allow explicit cancellation. |
| Successful result | `Analysis <analysis_id> complete.` | Bind map, ranking, and details to this same analysis ID and dataset version. |
| No eligible pixels | `No cells meet the active data and quality requirements.` | Show coverage and exclusion reasons; leave the ranking empty. |
| Missing value | `No data — <missing_reason>.` | Show `score_pct: null`; do not substitute zero or renormalize weights per cell. |
| Request or service failure | `Analysis could not be loaded. <message>` | Preserve configuration; offer retry. Do not silently fall back to synthetic or stale results. |
| Synthetic fixture | `Synthetic example — not an observed result.` | Show the label persistently in setup, map, ranking, and details. |
| Map tiles unavailable | `Basemap unavailable; analysis results are still available.` | Keep ranking, selected pixel, and details usable; identify missing map context. |

## Contract mapping

The layout consumes the versioned catalog and `SearchResponse`; it does not calculate scores in the browser. The results workspace keys all children by `analysis_id`. The ranking uses `ranking[]`, the overview uses `map_cells[]` with its explicit maximum and mean, and the detail panel uses the selected `pixel_id` endpoint. It must discard late responses for a different analysis. `distinct_areas` is a separate result mode with its own configured distance.

The scaffold now includes the main result hierarchy and a selected-cell placeholder. This artifact defines intended UX, not a connected analysis; fixture-backed selection and browser verification remain necessary before E-002 is complete.
