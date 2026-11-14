# E-016 — Review audytu źródeł i próbek K-002

## Oceniany zakres

- K-002 implementation target: `413c84bb814018b550470c77c186079a7bc1b641` (PR #8).
- K-002 PR was later merged at `fc3e4f0c191c6c47fad1685b16e1346619390706`; the manifest and downloader are byte-for-byte unchanged between the reviewed target and merged head `e6c907c862d22f1e0da8e32bf24a4c5da66e131c`.
- Initial review result: COMMENT, no requested code changes in the audited scope: https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/8#pullrequestreview-5907099968.

## Independent source and metadata checks

- **ETOPO 2022:** NOAA metadata confirms DOI `10.25921/fd45-gt74` and CC0-1.0. The manifest's S15W075 sample is one 15° × 15° tile containing land and bathymetry, not a global-validation claim. The downloaded GeoTIFF independently reads as 3600 × 3600 float32, EPSG:9518 (WGS 84 + EGM2008), 15 arc-second resolution, bounds `[-75, -30, -60, -15]`, metres, and nodata `-99999`. Raster min/max are `-8997` and `6806.77880859375 m`; mean and standard deviation agree with the manifest within float32 rounding. https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Aetopo_2022
- **LOLA LDEM_4:** NASA PDS confirms dataset `LRO-L-LOLA-4-GDR-V1.0` and DOI `10.17189/1520642`. The detached PDS3 label describes a 720 × 1440, 16-bit little-endian image, unit metres, scaling `0.5 m/DN`, offset `1,737,400 m`, and a shape/radius map. The sample bytes independently read as int16 with DN range `-17757..21008`, matching the manifest. The label explicitly defines topography as planetary radius minus geoid radius; the manifest correctly treats this product as radius/shape and does not invent a missing-data constant. https://pds.nasa.gov/ds-view/pds/viewDataset.jsp?dsid=LRO-L-LOLA-4-GDR-V1.0 ; https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/document/rdrsis.htm
- **MOLA MEGT/MEGC:** PDS labels describe paired 720 × 1440, 16-bit big-endian arrays. MEGT is median topography in metres relative to the Mars areoid; its label states that bins without observations receive interpolated values. MEGC is the number of observations per bin. The sample arrays independently read with MEGT range `-8068..21134 m`; MEGC ranges `0..2611`. Exactly 9,137 pixels have count zero, while their MEGT values remain populated (`-3049..4788 m`), confirming why count zero means no direct observation rather than a zero elevation. https://pds-geosciences.wustl.edu/missions/mgs/megdr.html ; https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/document/egdrsis.htm
- **NASADEM:** NASA's catalog confirms DOI `10.5067/MEASURES/NASADEM/NASADEM_HGT.001`; Earthdata documentation confirms DAAC downloads require Earthdata Login. K-002 does not claim a downloaded NASADEM file or an independent comparison. These remain explicit follow-up work in K-017. https://doi.org/10.5067/MEASURES/NASADEM/NASADEM_HGT.001 ; https://urs.earthdata.nasa.gov/documentation/what_do_i_need_to_know

## Reproduction and integrity

- `python pipeline/download_samples.py --output-dir <temporary-directory>` independently replayed the exact manifest. It verified all 10 files by expected byte size and SHA-256: ETOPO GeoTIFF; LOLA IMG/LBL/XML; MOLA MEGT IMG/LBL/XML and MEGC IMG/LBL/XML. Files were kept only in a temporary directory, outside `data/` and Git.
- Read ETOPO through the repository `.venv` `rasterio` and read the PDS image arrays from the downloaded bytes; dimensions, dtypes, units, no-data handling, scale/offset, and sample ranges above agree with the manifest and source labels.
- Reviewed the downloader loop and existing-file path: it iterates every manifest file, verifies size and SHA-256 before accepting a file, downloads to `.part`, verifies before rename, and removes a failed partial. No silent checksum bypass was found.

## Result and limits

The initial attempt failed because the sandbox could not resolve public DNS; a later read-only approved run succeeded and completed the missing independent byte and raster checks. The source claims are supported by downloaded bytes and official labels/metadata. ETOPO remains a single-tile sample, LOLA is a radius/shape product rather than areoid topography, and the bodies' different vertical references are not compared as absolute elevations. NASADEM has not been downloaded or independently compared; K-017 owns that follow-up. This review does not claim global Earth coverage or formal NASA submission.
