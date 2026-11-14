# Kontrakt współpracy v0.1

Status: **draft startowy**. Kamil zamraża v1 w K-003, zanim oba tory połączą implementację. Ewelina może rozpocząć UI na dostarczonych fixture'ach. Schematy requestu i regresja hotspotu są już w `contracts/`; odpowiedzi poniżej wymagają schema/OpenAPI w K-003.

## Wspólne reguły

- JSON: klucze angielskie `snake_case`; daty ISO 8601, znaczniki czasu z offsetem lub `Z`.
- Geometria Earth GeoJSON: `[longitude, latitude]`, WGS84. Profile planetarne mają własny układ w metadanych i nie trafiają bez transformacji do ziemskiego GeoJSON.
- Wszystkie procenty mają skalę 0–100; frakcje kompletności 0–1. Wartości brakujące to `null` wraz z powodem.
- Identyfikatory pikseli są stringami powiązanymi z konkretną siatką, np. wersją i wierszem/kolumną rastra. Brak `NaN`, `Infinity` i niejawnej zamiany braku na 0.
- Każda odpowiedź analityczna zawiera `contract_version`, `dataset_version`, `grid_version`, `model_version`, `profile_version`, `analysis_id` i `is_synthetic`.
- Konfiguracja obejmuje profile, wagi, reguły QA i wersje; w odpowiedzi zwracamy jej efektywną postać.

## Powierzchnia API

| Endpoint planowany | Wynik |
|---|---|
| `GET /api/v1/catalog` | Profile, cechy, jednostki, dostępność, reguły QA, siatka, źródła i aktualne wersje |
| `POST /api/v1/search` | Globalny ranking, agregaty mapowe i raport kwalifikowalności |
| `GET /api/v1/analyses/{analysis_id}/pixels/{pixel_id}` | Dokładna geometria, pomiary, wyniki cech i źródła w kontekście tej analizy |
| `GET /api/v1/analyses/{analysis_id}/map?bbox=...&level=...&limit=...` | Ograniczone przestrzennie wyniki tej samej konfiguracji; paginacja / limit |
| `GET /api/v1/analyses/{analysis_id}/export` | Konfiguracja, wersje i wynik do odtworzenia; CSV/JSON z jednostkami i cytowaniami |
| `GET /api/v1/health` | Gotowość i wersja zbioru, bez danych uwierzytelniających |

Nieudokumentowane endpointy nie są wymaganiem P0. Eksport jest rozwinięciem po pierwszej integracji. Długie obliczenia mogą później wymagać job API; zmianę zatwierdzamy w K-003 / osobnej karcie, nie jednostronnie.

## SearchRequest

Przykład ma wartości konfiguracyjne, a nie wynik naukowy:

```json
{
  "body": "mars",
  "profile_id": "mars-jezero",
  "dataset_version": "VERSION_FROM_CATALOG",
  "criteria": [
    {"feature_id": "slope_deg", "weight": 1},
    {"feature_id": "roughness_m", "weight": 2}
  ],
  "result_mode": "pixels",
  "top_k": 10,
  "min_distance_km": 25
}
```

`min_distance_km` działa wyłącznie w `distinct_areas`; w trybie pikseli pozostaje w konfiguracji, ale nie filtruje sąsiadów. Schema: [search-request.schema.json](../contracts/search-request.schema.json). Dodatkowa walidacja semantyczna: unikalne `feature_id`, zgodność profilu z ciałem i datasetem, warstwa dostępna dla profilu oraz wersja zbioru istniejąca na serwerze. Lista zawiera wyłącznie aktywne cechy o dodatnich wagach.

## SearchResponse — wymagane pola

| Obiekt | Pola |
|---|---|
| Nagłówek | Wersje, `analysis_id`, `is_synthetic`, `query`, `elapsed_ms`, `scope` |
| `scope` | `type` global/regional, geometria/identyfikator zasięgu, opis maski i siatki |
| `coverage` | `total_pixels`, `eligible_pixels`, `excluded_by_reason`, frakcja powierzchni z kompletem danych |
| `ranking[]` | `rank`, `pixel_id`, `score_pct`, `center`, `pixel_area_km2`, `coverage_fraction`, `quality_flags`, `features[]` |
| `features[]` | `feature_id`, `value`, `unit`, `similarity_pct`, `normalized_weight`, `contribution_pct`, `reference_interval`, `tolerance`, `source_ids`, `missing_reason` |
| `map_cells[]` | `cell_id`, `level`, `max_score_pct`, `mean_score_pct`, `max_pixel_id`, `valid_pixel_count`, `total_pixel_count` |
| `warnings[]` | Kody i czytelne komunikaty, np. `TOPOGRAPHY_ONLY`, `COARSE_RESOLUTION`, `REGIONAL_COVERAGE` |

Brak ważnych komórek: HTTP 200, puste `ranking`, jawny raport braków i komunikat. Nie zerujemy mapy. W mapie brak ważnych pikseli daje `max_score_pct = null`, `mean_score_pct = null`, `max_pixel_id = null`.

`distinct_areas` dodaje dystans i regułę wyboru reprezentantów. `score_pct` nadal jest wynikiem konkretnego reprezentanta. Nie zwracamy tego samego pola raz jako maksimum, raz jako średniej bez zmiany nazwy.

## PixelDetails

Obejmuje geometrię komórki, faktyczną powierzchnię, rozdzielczość źródeł i siatki, okna cech, wszystkie pomiary i wkłady, źródła i flagi. Gdy użytkownik kliknie brak danych, szczegóły mają `score_pct = null` i przyczynę. Pole `center` służy do nawigacji, nie sugeruje precyzji pojedynczego punktu w terenie.

Nie wolno wyświetlać szczegółów policzonych dla poprzednich wag obok nowej mapy. UI identyfikuje stan przez `analysis_id` i ignoruje opóźnione odpowiedzi wcześniejszego zapytania.

## Błędy

Jedna struktura: `error.code`, `error.message`, opcjonalne `error.details`, `request_id`. Co najmniej: `INVALID_QUERY`, `UNKNOWN_PROFILE`, `INCOMPATIBLE_FEATURE`, `DATASET_UNAVAILABLE`, `ANALYSIS_EXPIRED`, `LIMIT_EXCEEDED`. Utrata analizy nie może po cichu podmienić jej na aktualną wersję danych.

## Zasada zmiany kontraktu

Kamil proponuje zmianę w karcie i wersji; dołącza fixture oraz opis migracji. Ewelina potwierdza wpływ na UI. Zmiana usuwająca pole / zmieniająca semantykę wymaga nowej wersji i uzgodnionej integracji. Jednostki i znaczenie agregacji również należą do kontraktu.
