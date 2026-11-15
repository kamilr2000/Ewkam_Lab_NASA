# Terra Analog

## Project summary

Terra Analog is a regional terrain-comparison prototype for exploring where selected Earth topographic measurements fall within measured terrain profiles for Jezero crater on Mars or the Moon’s south polar region. In the tested build, a user selects a reference profile, one to three terrain criteria with positive weights, one catalogued Earth region, and either an individual-pixel Top 10 or a distinct-area ranking with an explicit minimum separation. The app links each result to its map context and measured values. It is a comparison of selected topographic features; it does not establish a complete environmental analogue, habitability, or a best site for a mission.

## Project and demo links

- Project name: **Terra Analog**.
- Public project URL: **No public project or demo URL was available on 15 November 2026.** The repository is private and this tested build has not been deployed for anonymous access.
- Demo: **Seven-slide PowerPoint** — [`terra-analog-demo.pptx`](terra-analog-demo.pptx). The local file is not a public submission link. It must be hosted externally with public, no-login access before it can be entered in the submission form.
- Tested implementation: E-006 pull request [#96](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/96), head `c0df63a50f196ef89793ec1345d3c5ca3636d18c`. This is a locally tested branch, not yet integrated into `origin/main` as of this package. Browser evidence used the local API and a same-origin development proxy; public deployment and anonymous access were not tested.

## What the tested build does

The Live catalogue exposes two NASA-derived reference profiles: Jezero crater on Mars (`mars-jezero-mola128-v1`) and the lunar south polar 80–90°S region (`moon-south-polar-80s-lola80-v1`). The Earth search is limited to three named, versioned regional packages built from NOAA ETOPO 2022 surface data and a GSHHG land mask: Atacama / Andes, Hawaii Big Island, and Himalaya. Selecting Live mode requires an available catalogue region and its exact dataset version. If Live data fail to load, the interface shows the error; it does not substitute the synthetic fixture. Synthetic examples are kept separate and visibly labelled.

The available measured terrain criteria are surface slope in degrees, local roughness in metres, and local relief in metres. Positive weights are normalized over the selected criteria. Each eligible Earth cell in the selected regional package is evaluated before the Top 10 pixels are returned. Cells without all active measurements are excluded from ranking with recorded missing-data reasons; a missing value is not treated as zero. In `distinct_areas` mode, the API continues through ranked pixels to select representatives at least the user-specified geodesic distance apart. A representative is a selected pixel, not a new polygon or an average score for an area.

The score is a configured similarity index from 0 to 100. For each feature, similarity is 100 inside the profile interval and declines linearly toward zero outside it according to that feature’s tolerance. The weighted contributions sum to the score. A score of 100 means all active measurements fall inside the chosen profile intervals; it is not a probability, confidence estimate, habitability measure, or indication that two environments are identical. The profile intervals use area-weighted P10–P90 feature values. The current tolerance (`1.5 × IQR`) is explicitly an experimental assumption, not instrument uncertainty or a NASA threshold. See [`docs/METHODOLOGY.md`](../docs/METHODOLOGY.md) for the full formula and caveats.

Map cells are a display aggregation made after scoring. Their colour uses the highest eligible pixel’s score and identifies that pixel; a mean is context only. The map, ranking, and pixel explanation are tied to the same API analysis. Zoom changes the view, not the analysis grid resolution.

## Reproducible examples from the tested local build

These are observations from the E-006 browser run against the local API, not results from a public deployment.

### Mars profile — Atacama / Andes, individual pixels

- Reference profile: Jezero crater, MOLA-derived `mars-jezero-mola128-v1`.
- Earth package: `k005-earth-2km-atacama-andes-v2`; 2 km analysis grid; NOAA ETOPO 2022 v1 surface plus GSHHG 2.3.7 land mask.
- Criteria: slope, local roughness, and local relief, with raw weight 1 for each (normalized share 33.33% each); Top 10 individual pixels.
- Candidate coverage: 1,791 eligible of 1,796 cells (99.72%).
- Selected top pixel: `earth:k005-earth-2km-atacama-andes-v2:r00008:c00009`; score 100; nominal cell area 4 km²; measurement coverage 100%; no quality flags or missing reasons in the returned detail.
- Measurements and reference intervals: slope 5.52° (0.38–5.68°); roughness 161.68 m (20.66–175.21 m); relief 694.22 m (138.33–887.63 m). Each value is inside its displayed interval, which explains the score ceiling.
- API analysis ID: `bf7bb4ae-b405-44f3-9ae4-94677aa0808a`.
- The regional map returned two display cells. The cell containing the named winner had a 100% maximum; the 81.45% display-cell mean is context and does not replace the individual pixel result.

### Lunar south-polar profile — Hawaii Big Island, distinct areas

- Reference profile: lunar 80–90°S, LOLA-derived `moon-south-polar-80s-lola80-v1`.
- Earth package: `k005-earth-2km-hawaii-big-island-v2`.
- Mode: `distinct_areas`, minimum separation 25 km entered in the UI; 10 representative pixels returned. Inspected nearest selected distances included 25.28, 25.60, and 28.42 km.
- Candidate coverage: 1,497 eligible of 1,854 cells.
- API analysis ID: `dad73910-2f05-4e71-bac8-a2e84ae27c5c`.
- These representatives remain separate pixel candidates. The mode does not create region polygons or claim a distance-separated global ranking.

The API returned `SCOPE_UNAVAILABLE` for a global request. Global Earth ranking has not been run and is not available in this tested build.

## Data, sources, and rights

- **Mars reference profile:** NASA Planetary Data System, MOLA MEGDR / Topography Derived, including MEGT/MEGC source data used to build the Jezero profile at 128 pixels per degree. DOI [10.17189/1z1b-kv84](https://doi.org/10.17189/1z1b-kv84); [PDS product page](https://pds-geosciences.wustl.edu/missions/mgs/megdr.html). The profile uses derivatives of topography; the application does not compare absolute height values across Earth, Mars, and Moon vertical references. The profile manifest does not assign a separate licence.
- **Moon reference profile:** NASA GSFC Planetary Geodesy and Geophysics Archive, LOLA Product 90, adjusted south-polar DEM and quality layers used for the 80–90°S profile. Cite Barker et al. (2023), *The Planetary Science Journal* 4, 183, DOI [10.3847/PSJ/acf3e1](https://doi.org/10.3847/PSJ/acf3e1); source data DOI [10.60903/gsfcpgda-lola-spole](https://doi.org/10.60903/gsfcpgda-lola-spole); [PGDA Product 90](https://pgda.gsfc.nasa.gov/products/90). The profile manifest does not assign a separate licence.
- **Earth search terrain:** NOAA National Centers for Environmental Information, ETOPO 2022 15-arc-second surface elevation tiles, product `ETOPO_2022_v1`, DOI [10.25921/fd45-gt74](https://doi.org/10.25921/fd45-gt74); [product page](https://www.ncei.noaa.gov/products/etopo-global-relief-model). The regional package manifest records CC0-1.0 and links to the [NOAA metadata/terms](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Aetopo_2022). These are three regional packages; the product’s global extent does not mean Terra Analog searched globally.
- **Land mask:** GSHHG 2.3.7, DOI [10.5281/zenodo.7007502](https://doi.org/10.5281/zenodo.7007502), [project page and LGPL-3.0-or-later terms](https://www.soest.hawaii.edu/wessel/gshhg/). It masks ocean/water source samples and is not a planetary measurement.
- **Separate Earth-data validation:** NASA/JPL NASADEM HGT v001, DOI [10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001](https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001), CC0-1.0 in its manifest. It was used in a separate comparison of three Earth regions; it does **not** supply the Earth terrain measurements scored in the examples above. That comparison does not establish global error or global coverage.
- Input files, processing parameters, cell-grid versions, and recorded checksums are listed in the versioned manifests under [`data/manifests/`](../data/manifests/). K-004 profile details and their limits are described in [`docs/DATA.md`](../docs/DATA.md).
- **Software and tools:** OpenAI Codex (model version not recorded) assisted with coding, source checking, English editing, and preparing this deck. The web client uses React 19.3.1, MapLibre GL JS 6.18.0, Vite 8.3.8, and TypeScript 7.0.2; pinned package versions are in [`apps/web/package.json`](../apps/web/package.json). See [React](https://react.dev/), [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/), [Vite](https://vite.dev/), and [TypeScript](https://www.typescriptlang.org/). The profile-generation pipeline records Python and geospatial library versions in its manifests. No third-party basemap tiles, photos, audio, or generated media are used in this deck.
- **NASA relationship:** NASA datasets are used as described above. This project is not endorsed by NASA or the Space Apps Challenge organizers.

## AI assistance disclosure

OpenAI Codex (exact model version not recorded) assisted with web application code, source and documentation checks, translation/editing into English, and authoring the seven-slide presentation. The project team and deterministic software performed the data processing and ran the API analyses. Codex did not create or alter scientific measurements, analysis results, or source data. No AI-generated photographs, illustrations, video, audio, or NASA-branded material are included. This disclosure describes this package; the internal project AI-use ledger remains under its separate follow-up tasks.

## Scope and limitations

- The tested interface supports a **regional prototype with three named Earth packages**, not a global Earth search. A successful local browser run is not proof of public availability.
- All current ranking criteria are topographic. Climate, illumination, radiation, atmosphere, water, geology/mineralogy, and biological suitability are not scored. Similar lithology is not inferred from this terrain score.
- The two planetary profiles are geographically limited. Their samples, vertical references, resolutions, and quality differ from Earth data. The system compares selected derivatives at an explicitly configured scale; it does not prove that the corresponding environments are interchangeable.
- Each analysis cell is nominally 2 km, while terrain features use a 10 km neighbourhood. ETOPO’s 15-arc-second source posting is not uniform in physical size and does not guarantee 2 km feature accuracy. Zooming the map does not add input detail.
- The score and tolerance are experimental and compensatory. A high score does not imply that all important factors match, and ties at the ceiling are possible.
- Missing or unsupported observations remain unavailable with reasons and are not converted to zero or silently filled. NASADEM/SRTM validation does not cover the poles.
- Public deployment, anonymous-link access, and the online submission form have not been verified. The private repository and local PowerPoint file cannot satisfy those public-link requirements by themselves.

## Planned work (not in the tested build)

Global Earth coverage and a true global Top 10; additional non-topographic layers such as climate, illumination, geology/mineralogy or environmental conditions; profile and tolerance sensitivity analysis; public deployment and anonymous access. These are future work and are not shown as implemented capabilities here.
