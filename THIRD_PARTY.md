# Third-party data, software, and attribution

The repository's MIT licence applies only to project-authored code and documentation. It does not grant rights to external datasets, software, map tiles, or media. Check the cited source terms before redistribution. Exact input versions and checksums are recorded in data/manifests/.

## Scientific data

| Material | Project use | Recorded terms and attribution |
|---|---|---|
| NOAA ETOPO 2022 v1, 15-arc-second surface | Terrain input for the three regional K-005 Earth packages and selected NASADEM comparisons | NOAA NCEI; DOI 10.25921/fd45-gt74. The source metadata records CC0-1.0. The product is not intended for navigation. Cite NOAA NCEI and the DOI. |
| NASA PDS LOLA LDEM_4, dataset V3.0 | Verified lunar source sample | DOI 10.17189/1520642. PDS data are public domain; documentation may have separate terms. Cite the PDS product and DOI. |
| NASA PDS MOLA MEGT/MEGC, 4 px/degree sample | Verified Mars topography and observation-support sample | DOI 10.17189/1z1b-kv84. PDS data are public domain; documentation may have separate terms. Cite the PDS bundle and DOI. |
| NASA GSFC PGDA LOLA Product 90: LDEM/LDEC/EFFRES/ERR, 80 m posting | Lunar south-polar reference profile for 80–90°S | DOI 10.60903/gsfcpgda-lola-spole; Barker et al. (2023), DOI 10.3847/psj/acf3e1. The product page requests citation but provides no licence identifier; no unverified licence is asserted. |
| NASA PDS MOLA MEGT/MEGC, 128 px/degree, tile 44N000HB | Jezero reference profile and observation-support data | DOI 10.17189/1z1b-kv84. Cite the MGS MOLA Topography Derived bundle and DOI. |
| NASADEM HGT v001 tiles s25w069, n19w156, n28e086, n29e027 | Separate DEM and land-mask validation | NASA JPL / LP DAAC; DOI 10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001. LP DAAC records CC0-1.0; download requires Earthdata Login. Cite NASADEM v001 and document NUM provenance. |
| GSHHG 2.3.7 full-resolution shapefiles | Land, lake, island, and grounded-Antarctica masks | Wessel, SOEST Hawai'i, and Smith, NOAA; DOI 10.5281/zenodo.7007502. LGPL-3.0-or-later. Preserve licence text and attribution when redistributing or modifying. |
| PROJ NGA EGM96/EGM2008 grids | Local vertical transformation from NASADEM EGM96 to ETOPO EGM2008 | Grid names, sizes, and SHA-256 are recorded in the K-017 manifest. CDN metadata indicates an open licence but no SPDX identifier; no more specific licence is asserted. |

The recorded sample files were downloaded and checksum-verified as stated in their manifests. This does not mean the full global raster was downloaded, processed, or validated. NASADEM validation covers selected regions and is separate from the ETOPO-derived search measurements.

## Web software and map

Direct runtime and build dependency versions are pinned in apps/web/package.json and apps/web/package-lock.json. See [apps/web/THIRD_PARTY.md](apps/web/THIRD_PARTY.md) for package versions and licence metadata.

The map uses MapLibre GL JS with visible-viewport tiles from the OpenStreetMap standard raster endpoint. Keep attribution visible when OSM is enabled and follow the [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/) and [copyright and licence terms](https://www.openstreetmap.org/copyright). The tile service is best-effort. No satellite provider or NASA imagery layer is connected. A library's licence does not grant rights to its data or tiles.

## Adding a dependency or source

Add the product/version, project use, source URL, rights evidence, required attribution, checksum or manifest, and validation status. Do not infer redistribution rights from free access or the fact that a source appears in an organizer resource list. Never label the entire data catalogue as MIT-licensed.
