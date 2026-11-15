# Data pipeline

Owner: Kamil. The scripts download pinned public inputs, verify their checksums, build reference profiles, and prepare the three regional Earth search packages. Raw source data stay in ignored local directories.

## Environment

Python 3.12 is pinned by .python-version. Install the data-processing group from the repository root:

```powershell
uv sync --locked --group data
```

## Mars and Moon reference profiles

```powershell
python pipeline/download_k004_sources.py
python pipeline/profiles/build_profiles.py
```

The downloader checks manifest-pinned file sizes and SHA-256 values. It writes raw files under the ignored data/raw/k004 directory. The profile builder writes versioned outputs and a reproducibility manifest. These two profiles represent selected regions, not complete planetary environments.

## Regional Earth packages

```powershell
uv run --locked --group data python pipeline/download_k005_sources.py
uv run --locked --group data python pipeline/build_k005_earth_grid.py
```

The build supports three AOIs: atacama-andes, hawaii-big-island, and himalaya. Each AOI is a regional package with a nominal 2 km cell grid and a 10 km feature neighbourhood. The build records its data and QA in data/manifests/ and data/reports/. Raw downloads, intermediate rasters, and checkpoints remain ignored. These packages are the current API inputs; they do not constitute global processing.

## NASADEM validation

This is a separate Earth-data validation workflow. It requires Earthdata authentication configured locally; do not commit or print the token.

```powershell
uv run --locked --group data python pipeline/download_k017_assets.py
uv run --locked --group data python pipeline/compare_nasadem_etopo.py
```

The workflow compares selected AOIs and documents mask, elevation, and derived-feature differences. It does not establish global DEM accuracy or supply the scored demo measurements.

See [data inventory](../data/README.md), [data sources and limits](../docs/DATA.md), and [third-party terms](../THIRD_PARTY.md) before redistributing any output.
