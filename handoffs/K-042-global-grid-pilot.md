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
- Implementation commit: `a2b9c1aa755e1040e624b016f20f98fdc725bdc8`
- PR #72: [K-042 measured 2 km global grid pilot](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/72)
- Initial published branch head before the later handoff/status updates: `5c99455a36cb6558e0e9269ef87ca867ebc5450e`; the current synchronized base and PR head are recorded in the latest PR #72 metadata and the sync note below.
- `python -m pytest pipeline/tests contracts/tests -q` using the project `.venv`: 50 passed in 2.65 s; the pilot and K-005 feature regression subset: 10 passed in 1.45 s.
- `python tools/check_planning.py`: passed (168 Markdown files, 42 JSON files, 84 task cards; acyclic dependencies).
- `git diff --check`: passed. All four derived CSV gzip files match their manifest SHA-256 and byte sizes; report totals are 16,384 candidates and 13,912 eligible.
- An additional full-suite run stalled at the existing first API test `apps/api/tests/test_health.py::test_health_reports_api_ready_and_dataset_unavailable` for more than 30 seconds and was interrupted. This did not block the pipeline and contract test suites above.
- Independent review: E-029 reported a clean-clone downloader defect; E-030 is the re-review of the correction, owned by Ewelina.

## Follow-up after E-029 — clean-clone source download

E-029 reported that `download_public_file()` tried to open a `.part` file before its ignored parent directory existed. Commit `60da3d2e8f57113c87380b00302ccfe3cc6c52ec` now creates the destination directory in the shared K-017/K-042 helper. The regression test `pipeline/tests/test_download_k017_assets.py::test_download_public_file_creates_missing_destination_directory` starts with a nested path that does not exist, stubs only the HTTP response, then checks the downloaded bytes, pinned size/SHA-256, and removal of the temporary `.part` file.

The fix was then run in a fresh, separate Git clone at branch head `93e27b441da2c871ab865bff7ce1e5b4cd300e3b`, which matched the pushed PR #72 branch. `data/raw/k042` was absent before the run. `uv run --locked --group data python -m pipeline.download_k042_sources` downloaded all eight pinned ETOPO/GSHHG inputs, verified each against the manifest, and extracted GSHHG without a manually created directory. `uv run --locked --group data python -m pipeline.download_k042_sources --verify-only` then passed on the same clone. Exact source sizes and hashes are in the [independent E-029 report](E-029-review-K-042.md); no Earthdata token was needed.

### Synchronization after K-022 integration

The K-042 branch was synchronized with `origin/main` at `a36e045ebfa97d0e1c3c9d98d296e4ff944f73e3` by merge commit `907295f1d1f40a5943fb1066c5b0548974c0036f`. The exact implementation/fix ref for E-030 remains `935fb086ce874eb89b7ed9342ea8f7be4f458bda`; synchronization did not change K-042's code, manifest, report or derived pilot tables.

On the synchronized tree, `python -m pipeline.download_k042_sources --verify-only` verified all eight pinned ETOPO/GSHHG inputs by size and SHA-256. `python -m pytest pipeline/tests contracts/tests -q` passed 53 tests in 1.58 s; `python tools/check_planning.py` passed (188 Markdown files, 44 JSON files, 96 cards, acyclic dependencies, 5 synthetic cases); `git diff --check origin/main...HEAD` passed. The original measured pilot remains four complete tiles, 16,384 candidates and 13,912 eligible cells. At the time of this sync, E-030 could begin after Ewelina published her own reservation; the later regional-MVP priority update below defers it until E-006 works. K-042 is still not integrated and does not claim a full global build, complete coverage or ranking.

### Synchronization after the regional-MVP priority update

The branch is synchronized with `origin/main` `8c19f1a8e44295aa3cdede34bf94e614cd8b2e28` by merge commit `8010160af4e3392a91944e52da6665bb02c4d675`; this is the current PR #72 head. K-042 implementation/data remain unchanged from the post-fix code ref `935fb086ce874eb89b7ed9342ea8f7be4f458bda`. On this branch, all eight pinned source files verified by size/SHA-256, `uv run --locked --group data --group dev python -m pytest pipeline/tests contracts/tests -q` passed 53 tests, the planning checker passed (188 Markdown, 44 JSON, 96 task cards, acyclic dependencies, 5 synthetic cases), and `git diff --check origin/main...HEAD` passed.

The current user priority is the regional MVP: E-006 is first because the web criteria builder currently sends global scope while K-007 publishes regional search packages only. E-030, owned by Ewelina, is explicitly deferred until E-006 works; no status or reservation was changed for her. The pilot's 5.7–8.0 day global runtime range is a coarse extrapolation, not a validated promise. No full scan or global ranking was run, so the demo must remain limited to a tested regional scope unless K-008 later establishes global coverage.

### Synchronization after E-006 reservation

`origin/main` now contains Ewelina's own E-006 reservation (`11f978d`, `status: in_progress`, branch `ewelina/E-006-mvp-results`). The K-042 branch includes that exact main state through merge commit `dfdcffa`; no E-006 files were edited on the K-042 branch. K-042 code/data remain unchanged at `935fb086ce874eb89b7ed9342ea8f7be4f458bda`. E-006 is the current first task; E-030 remains deferred until the regional live flow works. The updated PR #72 head is recorded in its description. No full global scan or ranking was run.
