# K-020 review — map design handoff E-019

- Reviewer: Kamil (`codex-kamil-k020-review-e019`)
- Date: 2026-11-15, Europe/Warsaw
- Reviewed task/PR: K-020 / [PR #18](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/18)
- Exact `review_ref`: `fde069cb35342986c5d2cc656a66fa90191377a9`
- Current PR head during review: `25e53c8285da31f38139bf68c0048cb21ad6776e`; `design/` files are unchanged from `review_ref`.
- Result: **REQUEST_CHANGES**, GitHub review ID `5908123529`.
- Follow-up owner/task: Kamil / [K-021](../tasks/K-021.md).

## Zakres i poprawne elementy

Sprawdziłem `design/map-visual-spec.md`, `design/map-hotspot-concept.svg`, `contracts/fixtures/search-hotspot-synthetic.json`, `contracts/fixtures/map-hotspot-synthetic.json`, kontrakt K-003 oraz definicje semantyki coverage w `docs/CONTRACTS.md`.

Projekt poprawnie odróżnia `max_score_pct` od średniej i rankingu pikseli. Wartości w szczegółach zgadzają się z fixture'em: słaba komórka ma maksimum 100 i średnią 46.666666666666664, a komórka steady 60/60; cztery markery mają kolejność 100, 60, 20, 20 i identyfikatory z rankingu. SVG nie dodaje rzeczywistych lądów, wyników, źródeł ani poparcia NASA. Skala klas 0–100 jest stała, NoData ma osobną klasę, osie są opisane w stopniach bez skali kilometrowej, a spec opisuje Equal Earth, bieguny, antymeridian, stabilny ranking po zoomie, klawiaturę i opcjonalny podkład.

## Finding — P1: declared scope is larger than the returned map extent

Fixture `search-hotspot-synthetic.json` declares a regional scope bbox `(3, 3, 3.04, 3.02)`. The map fixture requests the same north bound, `3.02`, but the union of both returned `map_cells` reaches only `3.01`. The SVG axes also stop at `3.01`; no map cell or explicit NoData geometry represents the remaining `0.01°` northward strip.

The response simultaneously reports `coverage.total_pixels = 4`, `eligible_pixels = 4`, `eligible_area_fraction = 1`, and the sum of map-cell `total_pixel_count` as 4. Under `docs/CONTRACTS.md`, coverage and surface fractions refer to the same scope and mask, and `map_cells[]` aggregates the counted pixels. The concept therefore depicts all coverage as complete while leaving part of the declared search extent unrepresented. This is a fixture/contract issue that the design artifact currently inherits; a static diagram that copies the fixture does not remove the inconsistency.

K-021 asks Kamil to reconcile the search scope, map bbox, cells/pixels and coverage counts, or to represent any uncovered area explicitly as NoData with correct accounting. After that correction, recheck E-019 against the updated fixture. The design can keep its current cell positions if the corrected extent matches those cells.

## Sprawdzenia i ograniczenia

- XML parser accepted the SVG. A coordinate check mapped both SVG cell rectangles and all four pixel marker centers to fixture geometries; all four pixel IDs appear in the detail list.
- The check reproduced the spatial mismatch: scope bbox `(3, 3, 3.04, 3.02)`, map-cell union `(3, 3, 3.04, 3.01)`, northern difference `0.01°`; declared and summed pixel counts are both four.
- `git diff` confirmed no design-file changes between `review_ref` and current PR head.
- No rendered browser preview or CVD-simulator run was independently available in this review. E-004 should repeat those checks against its actual map renderer.
- `python tools/check_planning.py` and `git diff --check` are recorded after the review report and K-021 card are added to this branch.
