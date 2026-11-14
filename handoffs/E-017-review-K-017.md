# E-017 review handoff — K-017 NASADEM sample and land mask

Date: 2026-11-15  
Result: **APPROVED for the documented K-017 sample-validation and mask-selection scope**  
Review request: [PR #12](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/12)  
Requested review ref: `40e06853a49de1dc663b82b0df891f068c3a8efe`  
Reviewed PR head: `549d1700b00dd3684068b38b134cd0501e4545dd`  
GitHub review node: `PRR_kwDOVuLLic8AAAABYCJugA`

The requested ref was compared with the PR head. K-017 pipeline, data manifest/report, source documentation, and dependency files did not change between them; subsequent commits only brought in unrelated main changes and task metadata.

## Evidence reviewed

- NASADEM manifest records HGT/NUM/SWB dimensions, types, units, classes, no-data declaration, DOI, access route, versions, sizes, and SHA-256. The downloader checks layer sizes and checksums, accepted ranges/classes, filenames, and ZIP member paths. Earthdata credentials are obtained through environment authentication and are not printed.
- The [official NASADEM guide](https://lpdaac.usgs.gov/documents/2237/NASADEM_User_Guide_V13.pdf) confirms HGT meters relative to EGM96, 3601-by-3601 tile posting, valid HGT range, and SWB classes 0=land and 255=water. [LP DAAC confirms CC0 and citation](https://forum.earthdata.nasa.gov/viewtopic.php?p=18837&t=5421).
- The comparison uses three AOIs on 2 km local UTM grids and a stated 10 km circular feature window. EGM96 heights are transformed to EGM2008 with local NGA grids; the [PROJ grid registry](https://cdn.proj.org/) identifies the grids with EPSG:5773 and EPSG:3855.
- The mask uses GSHHG L1/L3 as land, L2/L4 as water, skips L5, and selects L6 grounding-line polygons for grounded Antarctica. [Upstream GSHHG documentation](https://www.soest.hawaii.edu/wessel/gshhg/) describes its hierarchy, Antarctic alternatives, WGS84 coordinates, and LGPL license.
- Manifest/report SHA and size fields agree internally; all four recorded point checks pass. AOI mask agreement totals 5377/5387 cells (~99.814%). A scan found no credential-like values in the reviewed code or report.

## Checks reproduced

- `python tools/check_planning.py` — passed: 89 Markdown files, 10 JSON files, 44 task cards, acyclic dependencies, 5 synthetic cases. This checker does not validate live application behavior or raw data.
- `uv lock --check` — passed.
- `git diff --check origin/main 40e06853a49de1dc663b82b0df891f068c3a8efe` — passed.
- `python -m py_compile` for the three K-017 scripts — passed.
- Manifest/report consistency checks — passed for the recorded hashes, sizes, point checks, and mask-agreement arithmetic.

## Limits

The Ewelina clone has no `data/raw/k017` assets, so the downloaded bytes could not be independently reread and AOI metrics could not be recalculated. The locked data-group CLI could not install a missing wheel because DNS/network access was unavailable. This review verifies code, authoritative metadata, and internal report/manifest consistency, not the underlying local NASADEM files.

K-017 does not produce a global mask raster or global ranking. Antimeridian and polar raster tiling, global behavior, and representation of islands smaller than 2 km remain outside this review and need validation in the global pipeline work. The approval does not assert global validation, a production global mask, or an implemented search API.

No change is requested within K-017's documented sample-validation and mask-selection scope. The complete review evidence was also posted as an APPROVE review on PR #12.
