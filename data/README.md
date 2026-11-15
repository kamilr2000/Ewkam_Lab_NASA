# Data inventory

Owner: Kamil. Tracked files document provenance and provide compact regional packages that the API uses. Raw archives and large intermediate rasters are excluded from Git.

## Tracked data

- data/manifests/: source IDs, versions, licence and provenance notes, file sizes, checksums, and processing parameters.
- data/reports/: reproducibility and quality summaries.
- data/derived/k005-earth-grid/: small, versioned regional Earth cell tables consumed by the current API.

Do not remove the derived packages: they are runtime inputs, not disposable build output. Do not add raw downloads or temporary rasters to Git.

## Current sources and roles

- NASA MOLA supplies the Mars Jezero reference profile.
- NASA LOLA PGDA Product 90 supplies the lunar south-polar reference profile.
- NOAA ETOPO 2022 supplies terrain elevation for the three regional Earth search packages.
- GSHHG supplies a land/water mask during Earth processing.
- NASADEM HGT is used in a separate Earth-data validation exercise. It does not supply the scored Earth measurements in the recorded demo examples.

These sources have different grids, scales, and roles. The app compares documented terrain derivatives; it does not compare planetary elevation datums as if they were interchangeable. NASADEM validation over selected regions is not a global accuracy assessment.

## Reproduce data products

Follow the versioned commands in [pipeline/README.md](../pipeline/README.md). Downloaders verify pinned checksums. Use the corresponding manifest and report to confirm each result. Some NASADEM inputs require local Earthdata authentication; never write credentials into the repository.

The compact packages represent three regional areas only. They do not provide global Earth coverage or a global ranking.
