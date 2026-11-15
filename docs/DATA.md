# Data sources and provenance

Data products are owned and prepared by Kamil. The source manifests under data/manifests/ record product identifiers, versions, licences or known licence gaps, file checksums, processing parameters, and output versions. Raw archives and intermediate rasters are downloaded locally and excluded from Git.

## Planetary reference profiles

| Profile | Source | Role |
|---|---|---|
| Mars Jezero | NASA PDS MOLA MEGDR v2, MEGT/MEGC, source tile 44N000HB at 128 px/degree | Derive the selected-region reference profile and terrain-feature intervals |
| Lunar south pole, 80–90°S | NASA GSFC PGDA LOLA Product 90, including LDEM, LDEC, EFFRES, and ERR | Derive the selected polar reference profile with quality and effective-resolution checks |

The profile bounds, source checksums, feature statistics, and missing-support reasons are in data/manifests/k004-planetary-profiles.json and data/manifests/k004-source-files.json. The profile regions do not represent either entire planetary surface. Source posting does not guarantee effective measurement resolution.

## Earth terrain packages

Three compact, versioned regional packages are tracked for the current API: Atacama / Andes, Hawaii Big Island, and the Himalaya. Their elevation input is NOAA NCEI ETOPO 2022 v1 at 15 arc-seconds; GSHHG 2.3.7 provides land/water masks. Output cells use a nominal 2 km UTM grid and local terrain features use a 10 km neighbourhood. The exact AOI, grid, checksums, coverage, QA, and processing version are recorded in the K-005 manifests and report.

These are three regional datasets, not a global sample or a complete global ranking. Keep their dataset versions and pixel IDs distinct from any future global grid.

## Separate NASADEM validation

NASA/JPL NASADEM HGT v001, together with quality layers and selected ETOPO/GSHHG comparisons, is used in a separate Earth-data validation workflow. It does not provide the Earth feature values scored in the recorded API demo. The comparison covers selected AOIs only; it is not a global validation or accuracy guarantee.

## Acquisition and retention

Use the reproducible commands and pinned source manifests in [pipeline/README.md](../pipeline/README.md). Downloaders verify file sizes and SHA-256 before use. Store raw, intermediate, and cache files in ignored data directories. Keep manifests, reports, compact API input tables, and source/attribution notices in Git.

Check THIRD_PARTY.md and the product's source terms before copying or redistributing external files. Public access to a dataset does not by itself prove that every associated document or derivative has the same licence.
