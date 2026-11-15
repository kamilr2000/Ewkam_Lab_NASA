# Methodology and result interpretation

## Comparison target

A run is defined by the target body, reference region and profile version, active features and positive weights, Earth dataset version and region, and ranking mode. “Mars” alone is not a single reference condition. The current profiles cover Jezero crater and the lunar 80–90°S region; see their manifests for source IDs and profile statistics.

Absolute elevation values are not compared across Earth, Mars, and Moon vertical references. The MVP compares terrain derivatives with documented units and spatial support.

## Current scales and features

The three K-005 Earth packages use a nominal 2 km UTM cell grid. Local terrain features use a 10 km physical neighbourhood. Source posting, analysis-cell size, feature neighbourhood, and map display aggregation are different scales and must be reported separately.

| Feature | Unit | Definition |
|---|---|---|
| Surface slope | degrees | Local gradient computed with distances in metres |
| Local roughness | metres | Standard deviation of elevation residuals after removal of a local plane |
| Local relief | metres | P95 minus P05 elevation in the physical neighbourhood |

The three features are related measures of topography; they are not independent evidence for a complete environmental analogue.

## Measured K-004 reference profiles

Both profiles use a nominal 2 km analysis cell and a 10 km physical feature neighbourhood. Each source is processed on a grid appropriate to its body; absolute Earth, Mars, and lunar elevations are not compared.

| Profile | Region and source | Profile support |
|---|---|---|
| Mars — Jezero | A 47.52 km diameter circle around 18.41°N, 77.69°E, based on the USGS Gazetteer; this is a geometric envelope, not a crater-rim boundary. MOLA MEGDR v2 MEGT/MEGC, source tile 44N000HB, 128 px/degree. | 448 target cells; all 448 have the three features. At Jezero, source posting is about 463 m/pixel at the equator and 439 m east–west. On average 35.4% of MEGC bins have direct observations; 95.5% of 2 km cells intersect at least one such bin. |
| Moon — 80–90°S | Spherical polar cap bounded by LOLA Product 90 coverage; radius about 304.1 km in polar stereographic coordinates. NASA GSFC PGDA LDEM, LDEC, EFFRES, and ERR; nominal 80 m DEM posting. | 72,580 target cells; 72,100 (99.34%) contain all three features. Effective resolution after averaging to 2 km: median 42.49 m and P95 69.76 m. |

The intervals use area-weighted P10–P90 profile values. Tolerance is 1.5 × IQR for the same profile. This is a provisional modelling assumption, not instrument uncertainty, a known-analogue fit, or a NASA threshold.

| Profile | Feature | P10–P90 | Tolerance |
|---|---|---:|---:|
| Jezero | Slope | 0.377–5.682° | 3.040° |
| Jezero | Roughness after local-plane removal | 20.658–175.207 m | 151.788 m |
| Jezero | Local relief, P95–P05 | 138.334–887.632 m | 630.221 m |
| Moon 80–90°S | Slope | 1.281–14.385° | 10.412° |
| Moon 80–90°S | Roughness after local-plane removal | 115.063–452.243 m | 252.451 m |
| Moon 80–90°S | Local relief, P95–P05 | 572.221–2,959.491 m | 1,947.640 m |

Exact source checksums and profile outputs are recorded in data/manifests/k004-planetary-profiles.json and data/manifests/k004-source-files.json. The full coverage and edge-window audit remains there: 480 lunar 10 km windows at the source edge fall below the 90% support threshold for roughness/relief, and 96 edge cells lack neighbours required for central-difference slope. Missing measurements remain null; none are replaced with zero. MOLA MEGC records the proportion of interpolated or non-directly observed support; it is not treated as entirely direct measurement.

## Profile intervals and feature similarity

K-004 profile intervals use area-weighted P10–P90 values for each measured feature. The current tolerance is 1.5 times that feature's interquartile range. This is an experimental modelling choice, not instrument uncertainty, a NASA threshold, or a validated probability.

For candidate value x, reference interval [a, b], and positive tolerance t:

- d = max(a − x, 0, x − b)
- s(x) = max(0, 1 − d/t)

Similarity s is 1 inside the interval and decreases linearly to 0 outside it. The exact intervals and tolerances are recorded in the versioned profile manifest. Do not tune them to force a known location to rank first.

## Weighted score

For selected feature set A with positive weights wᵢ:

- αᵢ = wᵢ / Σwⱼ
- score = 100 × Σ(αᵢ × sᵢ)
- contributionᵢ = 100 × αᵢ × sᵢ

Contributions sum to the displayed score. The score is a configured, compensatory similarity index from 0 to 100. A score of 100 means every active feature falls within its selected profile interval. It is not probability, confidence, habitability, or overall environmental equivalence.

The API calculates scores. The browser must not recalculate or reinterpret them.

## Missing data and quality

A candidate must have valid values for every active feature under the dataset's QA rules. Missing values remain null with a reason; the score is not silently recalculated using a different subset of features. Coverage/completeness and quality flags are distinct from the score.

Compare candidates only when they use the same active criteria and dataset scope. Water masks, invalid source support, and quality failures must not be turned into zero-valued terrain.

## Pixel ranking and map aggregation

The API evaluates eligible pixels in the selected regional dataset before returning the pixel Top 10. Adjacent pixels remain separate candidates, so several positions can come from one locality. Ties use the API's deterministic pixel-ID ordering.

The distinct-area mode is a separate ranking. It selects pixel representatives subject to the requested geodesic minimum separation; it does not create polygons or area-average scores.

Map aggregation follows scoring. A display cell identifies the highest-scoring eligible pixel and may also show a mean for context. The map's maximum is the score of that actual pixel, not a sum of feature maxima from different places. Selecting a pixel links the map, ranking, and explanation to the same analysis ID. Zoom does not change measurement resolution.

## Current coverage limit

The three named Earth packages are regional. A global search returns SCOPE_UNAVAILABLE. The project has not completed global preprocessing or global-ranking validation; no global optimum or coverage claim is supported.
