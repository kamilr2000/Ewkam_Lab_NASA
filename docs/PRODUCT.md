# Product scope

## User question

Where on Earth do selected terrain measurements resemble a chosen region of Mars or the Moon?

Terra Analog is a screening tool for researchers, rover and instrument teams, educators, and analogue-fieldwork planners. It identifies candidates for further investigation; it does not certify a site or establish environmental equivalence.

## Implemented regional MVP

The current integrated application supports:

1. Mars / Jezero and Moon / south-polar reference profiles.
2. Three named, versioned Earth search regions: Atacama / Andes, Hawaii Big Island, and the Himalaya.
3. Three topographic criteria: surface slope, local roughness, and local relief.
4. Positive criterion weights, with map visibility managed independently from analysis criteria.
5. Regional analysis, individual-pixel Top 10, and a separate distinct-area ranking with a user-specified minimum separation.
6. A map with OpenStreetMap streets, separately controlled result-cell and ranked-marker layers, plus linked pixel measurements and score explanations.

The integrated API does not provide global Earth search. A global request returns SCOPE_UNAVAILABLE; do not present a regional ranking as a global optimum. Additional environmental domains are planned, not part of this MVP.

## Analysis and map semantics

- The API scores every eligible cell in the selected regional package before selecting the pixel Top 10.
- Adjacent pixels may each appear in the default ranking. Distinct-area ranking is a separate API mode that returns selected pixel representatives; it does not create polygons or area-average scores.
- Map-cell colours use the maximum score of an eligible pixel and preserve that pixel's ID. A cell mean is context only.
- The map, ranking, and pixel detail must refer to the same analysis ID. Zoom changes the view, not the input grid or analysis resolution.
- Missing active measurements make a cell ineligible and retain a reason. Missing is never converted to zero.
- The score is a configured similarity index, not probability, confidence, habitability, or proof that two places are alike in every respect.

## Data domains and planned work

The three implemented criteria are related topographic measures. They do not represent a complete planetary environment. Climate, illumination, radiation, atmosphere, water, geology/mineralogy, and biological suitability are not scored. Future criteria require independent evidence for compatible sources, units, measurement scales, coverage, and quality.

Do not call lithology mineralogy. NDVI is a terrestrial vegetation index and is not evidence of life on Mars. Never compare absolute elevations across planetary vertical references without a documented, valid transformation.

## Product acceptance boundaries

A release description must match observable code and recorded evidence. Keep Live and synthetic modes distinct. Report the region, dataset version, grid scale, feature scale, criteria, weights, missing-data policy, analysis ID, and source limits for each example. Do not claim public deployment, global coverage, additional layers, or organizer endorsement without direct evidence.
