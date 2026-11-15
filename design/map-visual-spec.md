# Map visual specification — E-019

**Purpose:** show where the best individual Earth pixels occur while keeping the cell summary honest. This is an interaction and visual design handoff for E-004, not a map renderer or a claim about real terrain.

## Data meaning and hierarchy

One map should communicate one result: the fill of each map cell represents **`max_score_pct`**, the best scored pixel inside that cell. It is a 0–100 similarity index for the active profile features, not a probability, a measure of habitability, or a score for the whole cell. Show `mean_score_pct` and `valid_pixel_count / total_pixel_count` in the selected-cell detail or tooltip as context; do not blend them into the fill.

Keep individual ranking results on a separate layer. Use numbered, keyboard-selectable markers for the API's Top 10 pixels, with a strong outline for the selected pixel. In `distinct_areas` mode, show a different diamond marker and label it as a representative pixel; never combine those representatives with the pixel ranking. A viewport or zoom request may change visible map cells, but it must not recalculate or truncate the global ranking.

## Color and missing data

- Use a fixed five-class sequential ramp over the similarity index so the same value has the same visual meaning between scenarios: `[0,20)`, `[20,40)`, `[40,60)`, `[60,80)`, `[80,100]`.
- Choose a perceptually ordered, color-vision-deficiency-aware ramp from the Cividis/viridis family. Keep rank labels and selection outlines visible without color.
- `null`/no eligible scores use a neutral gray hatch and their own legend label, never the lowest score class. Show the contract's `missing_reason` and counts in the cell detail.
- Label the legend “Cell maximum similarity index (0–100%) for active features”. The mean is context only.

## Projection and extent

For the global overview, use **Equal Earth** as the design target: it is equal-area and keeps both poles in the frame. Split or wrap cell geometries at the antimeridian before drawing; never omit polar cells because a basemap projection cannot display them. A regional view can fit the selected geometry, but the selected pixel, `analysis_id`, score, and global ranking remain unchanged when the projection or extent changes. Do not place a scale bar on an unprojected longitude/latitude sketch; the concept SVG labels degrees and therefore has no scale bar.

## Controls, detail, and attribution

- Make layer/mode controls keyboard operable with visible focus. Pair color with a number, outline, or distinct shape; expose the same cell and pixel data in a text detail panel.
- Keep `analysis_id`, dataset/grid/profile/model versions, synthetic/live state, and warnings available beside the map. The pixel selection must stay tied to the displayed analysis.
- A basemap is optional context, never a dependency. Do not add a tile source until its terms and required attribution are approved. If tiles fail, keep scored geometries, legend, ranking, and selection visible.
- At the world scale, aggregate cells from the API instead of downloading every pixel geometry. Loading a smaller viewport is a display optimization, not evidence that other pixels were excluded from the analysis.

## Synthetic concept verification

`map-hotspot-concept.svg` uses only the two map-cell polygons, four pixel geometries, and values in `contracts/fixtures/search-hotspot-synthetic.json`. At its displayed values:

- `synthetic-weak-map-cell`: maximum `100`, mean `46.666666666666664`, max pixel `synthetic-hotspot-p001`, 3 valid / 3 total, coverage 1.
- `synthetic-steady-map-cell`: maximum and mean `60`, max pixel `synthetic-steady-p001`, 1 valid / 1 total, coverage 1.
- Rank markers are the fixture order: hotspot `01 / 100`, steady `02 / 60`, weak pixels `03 / 20` and `04 / 20`.

The SVG labels this as a synthetic fixture and not a planetary observation; the gray missing-data swatch is a legend example, not an added data cell. Its local coordinate axes use degrees near 3°N. They are not a kilometre scale, and the drawing contains no basemap or invented land shapes. The selected numeric values and pixel IDs were checked against the fixture. No separate CVD simulator was run; the ramp choice is from the CVD-aware sequential families above and markers retain non-color cues. E-004 should repeat the accessibility and legend checks against its actual renderer.
