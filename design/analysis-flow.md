# Analysis flow and information hierarchy

This document describes the current interaction goals for the regional analysis UI. It is a product guide, not proof of a feature unless that behaviour is also present in the integrated app and review evidence.

## Main journey

1. Choose a target body and a reference profile.
2. Choose one or more available terrain criteria and positive weights.
3. Select one of the catalogued regional Earth datasets.
4. Run a regional analysis and inspect the individual-pixel Top 10.
5. Select a ranked pixel to inspect its map location, outline, measurements, units, score contributions, provenance, and quality flags.
6. Optionally switch to distinct-area ranking with an explicit minimum separation.
7. Change map-layer visibility without changing analysis criteria or ranking. Re-run after changing criteria.

The map, ranking, and explanation must share one analysis ID. A new request clears stale results, and a late response must not replace the current result. A missing measurement stays visibly missing; it is not shown as zero.

## Layout and map

On desktop, keep criteria controls, map, ranking, and explanation visible as related parts of one analysis. On small screens, stack these sections without clipping the main controls or selected result.

The map provides geographic context with an OSM basemap and visible attribution. Result-cell and ranked-marker layers have independent switches. Hiding a layer is a display action only. A basemap failure must leave the results and details available.

## Result language

Label the current search as regional. Do not imply global coverage, satellite imagery, increased measurement resolution from zoom, probability, habitability, or an overall environmental analogue. Separate Live API data from synthetic fixture demonstrations.
