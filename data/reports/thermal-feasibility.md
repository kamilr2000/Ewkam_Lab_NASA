# K-047 — Thermal feasibility sample

Generated: 2026-11-15T16:05:42+00:00.

## Decision

**NO-GO for a single scored thermal feature in K-010.** The products do not measure the same physical quantity with compatible observation conditions and support. The MODIS split-window retrieval depends on atmospheric transmission and emissivity estimates; Diviner TB3 is a radiance-derived channel brightness temperature, and this audit does not invert it to kinetic temperature using emissivity. TES thermal inertia is an inversion output whose model depends on observing time, season, albedo, pressure and dust opacity. It is a material response property rather than a surface-temperature observation. Its source posting near Jezero is coarser than the project’s 2 km target cells.

This decision is limited to the exact products and samples listed here. It does not rule out a separately specified temperature-only research layer with matched conditions, or a separate thermal-inertia comparison with suitable Earth and lunar products. K-010 remains P1; this experiment changes no production scoring, API, contract, or P0 result.

## Earth — MOD11A1.061 daily surface temperature

Each value below is a one-day snapshot for a solstice/equinox date in 2023, not a climatology. MOD11A1 derives clear-sky LST with a generalized split-window retrieval; the result depends on atmospheric transmission and surface emissivity estimates and is not air temperature. A MODIS native pixel centre is counted as good only when the LST raw value is in the product valid range and mandatory QA bits 1–0 are `00`. The 2 km cell support rule requires at least three land pixel centres and good mandatory QA for at least 75% of the land pixel centres in that cell. This is an experiment rule, not a MODIS product guarantee.

| AOI | Date | Candidate land 2 km cells | Day supported | Good MODIS-pixel LST p50 (K) | Good-pixel local time p50 (h) | Night supported | Good MODIS-pixel LST p50 (K) | Good-pixel local time p50 (h) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Atacama / Andes | 2023-03-20 | 1793 | 1783 (99.4%) | 309.7 | 10.5 | 1783 (99.4%) | 279.5 | 21.9 |
| Atacama / Andes | 2023-06-21 | 1793 | 1608 (89.7%) | 290.1 | 10.1 | 78 (4.4%) | 268.6 | 23.1 |
| Atacama / Andes | 2023-09-23 | 1793 | 1783 (99.4%) | 309.4 | 10.2 | 1622 (90.5%) | 274.1 | 21.7 |
| Atacama / Andes | 2023-12-21 | 1793 | 1783 (99.4%) | 315.9 | 10.0 | 0 (0.0%) | null | null |
| Hawaii, Big Island | 2023-03-20 | 1704 | 1 (0.1%) | 294.2 | 11.0 | 0 (0.0%) | null | null |
| Hawaii, Big Island | 2023-06-21 | 1704 | 145 (8.5%) | 308.4 | 10.7 | 187 (11.0%) | 279.1 | 22.5 |
| Hawaii, Big Island | 2023-09-23 | 1704 | 84 (4.9%) | 310.5 | 10.8 | 0 (0.0%) | null | null |
| Hawaii, Big Island | 2023-12-21 | 1704 | 0 (0.0%) | null | null | 0 (0.0%) | null | null |
| Himalaya | 2023-03-20 | 1731 | 898 (51.9%) | 288.5 | 10.7 | 108 (6.2%) | 261.0 | 21.7 |
| Himalaya | 2023-06-21 | 1731 | 315 (18.2%) | 305.4 | 10.3 | 304 (17.6%) | 276.8 | 21.3 |
| Himalaya | 2023-09-23 | 1731 | 39 (2.3%) | 298.9 | 10.4 | 1108 (64.0%) | 272.0 | 21.4 |
| Himalaya | 2023-12-21 | 1731 | 1321 (76.3%) | 280.7 | 10.3 | 1284 (74.2%) | 260.2 | 21.2 |

The detailed QA flags below are counted among pixels passing mandatory QA. They expose the product's stated per-pixel LST and emissivity error categories; they are reported as-is and are not extra filters in the support rule.

| AOI | Period | LST QA good pixels | LST error ≤1 K | ≤2 K | ≤3 K | >3 K | Emissivity error ≤0.01 | ≤0.02 | ≤0.04 | >0.04 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Atacama / Andes | day | 32776 | 32776 | 0 | 0 | 0 | 32776 | 0 | 0 | 0 |
| Atacama / Andes | night | 16600 | 16600 | 0 | 0 | 0 | 16600 | 0 | 0 | 0 |
| Hawaii, Big Island | day | 1373 | 1373 | 0 | 0 | 0 | 1373 | 0 | 0 | 0 |
| Hawaii, Big Island | night | 961 | 961 | 0 | 0 | 0 | 961 | 0 | 0 | 0 |
| Himalaya | day | 13177 | 13177 | 0 | 0 | 0 | 13177 | 0 | 0 | 0 |
| Himalaya | night | 14169 | 14169 | 0 | 0 | 0 | 14169 | 0 | 0 | 0 |

The coverage denominator is candidate 2 km UTM cells whose centres lie inside the published K-017 AOI bounds and are classified as land by the referenced NASADEM SWBD tile. Day/night times are local solar times recorded per pixel. This sample does not normalize view angle, terrain shading, seasonal solar incidence, atmospheric state, or emissivity across the three land regions.

## Moon — LRO Diviner TB3

The polar GDR L2 maps below are two separate 27-day mapping cycles with exact PDS label start and stop times shown in the table. Each map is a radiance-derived channel-3 brightness temperature at 7.55–8.05 μm, not the MODIS retrieval or an emissivity-normalized kinetic temperature. A 2 km cell is supported when at least 80% of its native 240 m posting centres have TB3 in the PDS-described 10–450 K range, a positive count product and a present error estimate. Nominal posting is not called effective resolution.

| Cycle interval | Candidate 2 km cells | Coverage-qualified cells | TB3 p50 (K) | Local solar time p50 (h) | Scaled count product p50 | Error estimate p50 (K) |
|---|---:|---:|---:|---:|---:|---:|
| day 2016-01-11–2016-02-08 | 72580 | 26576 (36.6%) | 231.8 | 11.1 | 0.3 | 13.9 |
| night 2016-01-25–2016-02-21 | 72580 | 828 (1.1%) | 101.6 | 2.0 | 0.3 | 159.9 |

Night coverage is especially sparse in this single sampled cycle. These coverage-qualified counts describe valid map-posting density, not independent detector observations per 2 km cell. Diviner GDR maps are binned and averaged by 27-day LRO cycles, split into local-time day/night, and local time drifts across longitude within a cycle. The polar map’s 240 m posting must not be presented as 240 m independent thermal resolution; PDS documents its footprint handling but does not provide one effective-resolution number for this sample. This sample does not match solar incidence, shadow or seasonal illumination across the lunar profile.

## Mars — MGS TES derived thermal inertia

| Period | Candidate target cells at 2 km | Independently supported target cells | Source pixels in Jezero geometry | Direct pixels | Interpolated pixels | Direct thermal-inertia p50 (J/(m² K √s)) | Native posting (N–S × E–W, m) |
|---|---:|---:|---:|---:|---:|---:|---:|
| day | 448 | null | 214 | 212 | 2 | 282.5 | 2964 × 2812 |
| night | 448 | null | 214 | 210 | 4 | 301.0 | 2964 × 2812 |

The TES maps were derived from dayside or nightside bolometer surface-temperature observations over three Mars years (1999–2004), then infilled where the interpolation mask says so. The thermal-inertia inversion depends on observing time, season, albedo, surface pressure and dust opacity; PDS explicitly cautions that the model for this map product differs from the one used for the published TES bolometer tables. Only direct source pixels are summarized in the table. The Jezero target grid has 448 cells at 2 km; TES posts at roughly 2.8–3.0 km near Jezero, so this audit assigns no independent 2 km cell support. It does not duplicate or interpolate TES values onto the finer grid.

## Reproduction and limits

Run `uv run --group data python pipeline/experiments/thermal/run_feasibility.py --download-missing`. The script verifies every file against the manifest SHA-256 and size, reuses the K-017 NASADEM water mask, recomputes the measurements, and rewrites this report plus the JSON manifest. MODIS downloads use the local `EARTHDATA_TOKEN` through earthaccess only when a file is missing. This run also verified a fresh MODIS Earthdata download and a PDS byte-range crop against their pinned hashes. The token is never printed or stored.

The sample is intentionally small: four daily dates for each of three Earth AOIs, one lunar day and one lunar night mapping cycle, and a 25 × 25 native TES byte-range window centered on Jezero. It is evidence about feasibility and QA, not a globally representative seasonal analysis. Source files remain outside Git under `data/raw/k047` and `data/raw/k017`.

Sources, provider use terms and citation guidance are recorded in `data/manifests/thermal-feasibility.json`; unknown SPDX identifiers remain `null` rather than being invented.
