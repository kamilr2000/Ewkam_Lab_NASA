# K-042 — global metric grid pilot

## Scope and reproduction

This handoff reports four measured local pilot tiles and one point control at the antimeridian. It does not report a global raster, full land coverage, map pyramid, ranking, or NASA endorsement.

On a clean clone with `uv` installed, prepare the pinned public inputs and rerun the pilot:

```text
uv run --locked --group data python -m pipeline.download_k042_sources
uv run --locked --group data python -m pipeline.global_grid_pilot --force
```

The source helper downloads about 295 MB of public NOAA ETOPO and GSHHG files, verifies the recorded sizes and SHA-256 values, and safely extracts the GSHHG shapefiles. No Earthdata token is required for K-042. The helper also supports `--verify-only`. Sources are ignored under `data/raw/`; the four compressed result tables, manifest, and report are tracked. For a faster rerun after verified checkpoints exist, omit `--force`.

Pinned inputs and output hashes are in [the manifest](../data/manifests/k042-global-grid-pilot.json). The [measurement report](../data/reports/k042-global-grid-pilot.json) records the full control results, environment, coverage, reasons for exclusion, projection scale factors, and extrapolation assumptions.

## Data and method

- NOAA NCEI ETOPO 2022 v1, 15 arc-second **Ice Surface**, WGS84, vertical reference EGM2008; DOI `10.25921/fd45-gt74`, CC0-1.0. This represents the top of the grounded ice sheets and terrain surface elsewhere. It is not bedrock beneath the ice or ice thickness.
- GSHHG 2.3.7 full resolution provides an independent mask: L1/L3 land, L2/L4 water, L6 grounded Antarctic land; L5 ice front is omitted. The source mask is applied before ETOPO aggregation; a separate target-cell centre mask is recorded.
- Cell target: nominal physical 2,000 m. Use local UTM by 6-degree zone below 80° absolute latitude, UPS EPSG:3413 north and EPSG:3031 south at/above 80°. Correct projected spacing with the local projection scale factor and record ellipsoidal WGS84 cell area.
- Tile core: 64 × 64 cells (4,096 candidates, nominally 128 km across), with seven contextual cells per edge (14 km physical halo) for a circular 10 km feature radius. Minimum valid feature-window support is 73/81 samples (90%). Every core cell is written; water, missing DEM, and low support retain explicit exclusion reasons. Negative land elevation remains valid.
- Feature code/version: `terrain-p0-k005-v2` from `pipeline/features/terrain.py`; slope in degrees, plane-fit roughness in metres, and P95−P05 relief in metres.

## Measured results

| Pilot area | CRS | Candidate core | Land-centre cells | Eligible |
|---|---|---:|---:|---:|
| Big Island coast | EPSG:32605 | 4,096 | 2,449 | 1,861 |
| Qattara depression | EPSG:32635 | 4,096 | 4,096 | 4,096 |
| Greenland, 82°N | EPSG:3413 | 4,096 | 4,046 | 3,859 |
| Grounded Antarctica, 85°S | EPSG:3031 | 4,096 | 4,096 | 4,096 |

The four tiles processed 16,384 candidates and returned 13,912 eligible cells. Runtime was 66.933 seconds for the four core tiles; peak Windows working set was 447,012,864 bytes. Output size was 705,886 bytes compressed and 2,941,138 bytes uncompressed. Manual checks reproduced all three terrain features at one cell in each tile.

Controls passed:

- Big Island focus point: GSHHG L1 land and ETOPO +3,173.58 m. An adjacent ocean point is GSHHG water with valid ETOPO bathymetry −792.71 m; it is not treated as a land candidate or included in land aggregation.
- Qattara: GSHHG L1 land, focus ETOPO −78.35 m; 2,424 below-zero land cells in the core and minimum −128.45 m. Height is not used to decide land membership.
- Greenland and Antarctica: correct UPS projections and local scale correction. Greenland at 82°N had scale factor 0.97460 and projected cell step 1,949 m for a target near 2,000 physical metres. Antarctica used two adjacent ETOPO tiles to remove a false source-edge NoData gap; 4,096 land cells in the core had valid DEM and features. GSHHG class L6 marks the focus as grounded land.
- Antimeridian: real N00E165 and N00W180 ETOPO tiles and GSHHG points at 179.99°E/W, 0.1°S. Wrapped longitude difference was 0.02° and geodesic distance 2,226.39 m. Both source samples were valid water. This is a point control; no complete metric raster tile or feature window crosses 180° yet.

## Grid comparison and limits

A fixed 60 arc-second grid contains 233,280,000 angular positions. Its WGS84 cell area is 3.4192 km² at the equator, 0.4822 km² at 82°, 0.3020 km² at 85°, and 0.03024 km² at 89.5°. Equal-weight pixel ranking would therefore overrepresent polar land. An arithmetic reference with 60 arc-second north-south rows and approximately 2 km east-west spacing totals 137,921,962 positions; it is not a materialized grid or a committed global cell count.

Linear extrapolation from the fastest/slowest measured pilot tiles gives 496,565–694,691 seconds (about 5.7–8.0 days), 5.94 GB compressed, and 24.76 GB uncompressed. This is a coarse extrapolation, not a global runtime promise. It omits global source selection and reads, GSHHG geometry selection/cache, scheduling, indexes, retries, and coverage-driven output differences.

K-042 recommends a 2 km metric candidate scale, ETOPO Ice Surface 15″ as the input product, a 10 km physical feature radius, and 64 × 64 cores with a 14 km physical halo. D-024 records this as a recommendation pending global validation. K-044 is a required precursor to K-008: define a canonical global grid and prove unique stable cell IDs, no ownership gaps/duplicates at UTM/UPS boundaries, ±80°, ±180°, and the poles. K-008 must still establish full source mosaic, coverage counts, global processing cost, and global ranking before making any global claim.

## AI disclosure handoff

Codex assisted with the source-verifying downloader, grid/pipeline code, controls, reports, documentation, and test cases. NOAA ETOPO and GSHHG measurements came from the pinned source files and were calculated by the pipeline; Codex did not synthesize or edit scientific observations or derived cell measurements. Add this K-042 scope to `docs/AI_USAGE.md` and `docs/ai-usage.json` through their current owner Ewelina's E-028 work; this handoff is not a substitute for updating that disclosure.

## Exact publication

Update after the implementation commit and PR are published:

- Implementation branch: `kamil/K-042-global-grid-pilot`
- Exact implementation SHA: pending
- PR: pending
- `python -m pytest pipeline/tests contracts/tests -q` using the project `.venv`: 50 passed in 2.65 s; the pilot and K-005 feature regression subset: 10 passed in 1.45 s.
- `python tools/check_planning.py`: passed (168 Markdown files, 42 JSON files, 84 task cards; acyclic dependencies).
- `git diff --check`: passed. All four derived CSV gzip files match their manifest SHA-256 and byte sizes; report totals are 16,384 candidates and 13,912 eligible.
- An additional full-suite run stalled at the existing first API test `apps/api/tests/test_health.py::test_health_reports_api_ready_and_dataset_unavailable` for more than 30 seconds and was interrupted. This did not block the pipeline and contract test suites above.
- Independent review: E-029, owner Ewelina
