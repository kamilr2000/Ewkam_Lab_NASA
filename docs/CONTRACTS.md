# Kontrakt API v1

Status: **zamrożony kontrakt `1.0.0` dla K-003**. Źródłem operacji HTTP jest [OpenAPI](../contracts/openapi.yaml), a źródłem kształtu payloadów są wskazane w nim schematy JSON Schema Draft 2020-12.

K-001 wdraża obecnie wyłącznie `GET /api/v1/health`. Pozostałe operacje opisują uzgodniony interfejs do wdrożenia w kolejnych kartach; sama obecność w OpenAPI nie oznacza działającego API, danych ani wyników naukowych.

## Wspólne reguły

- JSON używa angielskich kluczy `snake_case`. Daty są ISO 8601, a timestampy mają offset lub `Z`.
- Procenty mają zakres 0–100; frakcje kompletności 0–1. Nie kodujemy braków jako zera, `NaN` ani `Infinity`.
- Każda odpowiedź analityczna zawiera `contract_version`, `dataset_version`, `grid_version`, `model_version`, `profile_version`, `analysis_id` i `is_synthetic`.
- `is_synthetic: true` oznacza wartości demonstracyjne/testowe, które nie są pomiarami planety. Każdy fixture w `contracts/fixtures/` z wynikiem analitycznym jest syntetyczny.
- Pomiary mają `unit`, `measurement_scale`, `source_ids` i kontekst przestrzenny. Proxy ma `is_proxy: true` oraz opis, który mówi, czego jest przybliżeniem.
- Earth GeoJSON używa WGS84 i kolejności `[longitude, latitude]`. Geometria profilu Księżyca lub Marsa pozostaje w osobnym układzie z nazwanym ciałem i referencją; nie traktujemy jej jako Earth GeoJSON.
- Identyfikator piksela jest stringiem powiązanym z wersją siatki. Szczegóły i wynik zawsze należą do tego samego `analysis_id`.

## Operacje v1

| Operacja | Kontrakt odpowiedzi | Stan implementacji po K-001 |
|---|---|---|
| `GET /api/v1/health` | [HealthResponse](../contracts/health-response.schema.json) | Zaimplementowana |
| `GET /api/v1/catalog` | [CatalogResponse](../contracts/catalog-response.schema.json) | Planowana |
| `GET /api/v1/catalog/profiles/{profile_id}` | [ProfileResponse](../contracts/profile-response.schema.json) | Planowana |
| `GET /api/v1/catalog/datasets/{dataset_version}/manifest` | [DatasetManifest](../contracts/dataset-manifest.schema.json) | Planowana |
| `POST /api/v1/search` | [SearchRequest](../contracts/search-request.schema.json) → [SearchResponse](../contracts/search-response.schema.json) | Planowana |
| `GET /api/v1/analyses/{analysis_id}/pixels/{pixel_id}` | [PixelDetailsResponse](../contracts/pixel-details-response.schema.json) | Planowana |
| `GET /api/v1/analyses/{analysis_id}/map` | [MapResponse](../contracts/map-response.schema.json) | Planowana |

`CatalogResponse.search_regions` wylicza regionalne scope ID dopuszczone dla wskazanych datasetów. Scope globalny jest jawny i nie wymaga geometrii w request.

Eksport wyników i asynchroniczne job API nie należą do tego zamrożenia; wymagają osobnej decyzji i wersjonowanej zmiany kontraktu.

## SearchRequest

Przykład poprawnego requestu jest syntetyczny i pokazuje wyłącznie kształt konfiguracji:

```json
{
  "contract_version": "1.0.0",
  "body": "mars",
  "profile_id": "synthetic-mars-reference",
  "dataset_version": "synthetic-earth-v1",
  "scope": {"type": "regional", "region_id": "synthetic-region-1"},
  "criteria": [
    {"feature_id": "slope_deg", "weight": 1},
    {"feature_id": "roughness_m", "weight": 2}
  ],
  "result_mode": "pixels",
  "top_k": 10
}
```

- `scope` jest jawne: `{"type":"global"}` albo `{"type":"regional","region_id":"…"}`. Nie przekazujemy dowolnej geometrii wyszukiwania. Serwer rozwiązuje `region_id` w `CatalogResponse.search_regions` dla wybranej wersji danych i odrzuca nieobsługiwany zakres; nie może po cichu obciąć globalnego żądania do próbki regionalnej.
- `criteria` ma od 1 do 16 aktywnych cech o dodatnich wagach. `feature_id` musi być unikalne. JSON Schema nie wyraża tej reguły między polami; serwer najpierw waliduje schemat, a potem wywołuje [walidację semantyczną](../contracts/validation.py), która zwraca `DUPLICATE_FEATURE_ID`.
- Serwer sprawdza, czy dataset i profil istnieją, ciało jest zgodne z profilem, a wszystkie cechy są dostępne dla wybranej wersji. Komórki porównuje na tym samym aktywnym zestawie cech i wag.
- `top_k` wynosi 1–10. Porządek jest po niezaokrąglonym `score_pct` malejąco, a remisy rozstrzyga `pixel_id` rosnąco.

Tryb `pixels` nie przyjmuje `min_distance_km` i zwraca wyłącznie `ranking`. Tryb `distinct_areas` wymaga dodatniego `min_distance_km` i zwraca wyłącznie `area_ranking`. To osobne nazwy, by nie pomylić rankingu komórek z wyborem różnych lokalizacji.

## SearchResponse

Odpowiedź zawiera skuteczną konfigurację w `query`, zadeklarowany `scope`, raport `coverage`, wyniki oraz ostrzeżenia. Pole `scope.type` pozostaje `global` dla globalnego żądania także wtedy, gdy dane mają braki; zasięg i braki opisują `coverage`, a nie ukryta zmiana zakresu.

`coverage` zawiera `total_pixels`, `eligible_pixels`, wzajemnie rozłączne liczniki `excluded_by_reason`, powierzchnię całkowitą i kwalifikującą się oraz `eligible_area_fraction`. Liczniki spełniają `total_pixels = eligible_pixels + sum(excluded_by_reason)`. Jeśli całkowita powierzchnia wynosi zero, frakcja jest `null` z `no_data_reason: "empty_scope"`; brak kwalifikujących się pomiarów ma frakcję 0 i konkretny powód. Powierzchnie i udziały dotyczą tego samego zakresu oraz maski.

| Pole | Znaczenie |
|---|---|
| `ranking[]` | Tryb `pixels`: pojedyncze kwalifikujące się piksele. Każdy ma `rank`, `pixel_id`, `score_pct`, geometrię, faktyczną powierzchnię, jakość i wyniki cech. |
| `features[]` | Wartość, jednostka, skala pomiaru, podobieństwo, znormalizowana waga, wkład, przedział referencyjny, tolerancja, źródła i flagi QA. W kwalifikującym się rankingu wszystkie aktywne cechy mają wartość. |
| `area_ranking[]` | Tryb `distinct_areas`: wybrane reprezentatywne piksele z `candidate_id` oraz odległością od poprzednio wybranego reprezentanta. To heurystyka różnorodności, nie granice klastrów ani średnie obszarów. |
| `map_cells[]` | Agregaty liczone dopiero po wspólnym wyniku pikseli: maksimum, średnia ważona powierzchnią, ID piksela maksimum, liczność kwalifikująca się/całkowita i geometria komórki mapy. |

W `distinct_areas` selekcja zachłanna porównuje kandydatów od najlepszych do spełnienia `top_k` lub wyczerpania zbioru. Używa geodezyjnej odległości na Ziemi i jawnego `min_distance_km`; nie ogranicza się do pierwszych 10 pikseli. `map_cells` nadal agreguje wszystkie policzone piksele, a nie tylko reprezentantów.

Ranking pojedynczych pikseli zachowuje sąsiednie i izolowane hotspoty. Nie odrzucamy komórki przez średnią regionu przed oceną jej piksela. Mapy nie łączą osobnych maksimów różnych cech. Dla komórki bez kwalifikujących się pikseli `max_score_pct`, `mean_score_pct` i `max_pixel_id` są `null`, z `missing_reason`; nie zastępujemy ich zerem.

## PixelDetails, Profile i Manifest

- `PixelDetailsResponse` podaje wersje analizy, faktyczną geometrię i rozmiar pikseli oraz wartości, jednostki, wkłady i źródła. Brak wartości to `null` z `missing_reason`; gdy piksel nie może być oceniony, również `score_pct` jest `null`.
- `ProfileResponse` opisuje ciało, region, układ współrzędnych, przedziały referencyjne, tolerancje, jednostki, skalę pomiaru i przestrzenne wsparcie każdej cechy. Wartości wsparcia `null` mają `missing_reason`; geometria planetarna zachowuje jawny, właściwy układ ciała.
- `DatasetManifest` rejestruje identyfikator i wersje produktu/zbioru, dostawcę, cytowanie/URL/DOI, datę dostępu, licencję i warunki, SHA-256 plików, czas i zasięg, układ ciała, jednostki, siatkę, maski/QA, parametry przetwarzania, ograniczenia i status syntetyczny. Nieznane wartości pozostają `null` z powodem w `missing_reasons` (klucze to ścieżki pól, np. `sources[0].license`); walidacja semantyczna odrzuca nieopisane `null`. Nie tworzymy fikcyjnych licencji, checksum ani pomiarów. Manifest rzeczywistego zbioru musi mieć źródła z URL i warunkami licencji oraz przynajmniej jeden plik z SHA-256.

## Błędy

Operacje używają wspólnej struktury [ErrorResponse](../contracts/error-response.schema.json): `contract_version`, `request_id`, `is_synthetic` oraz `error.code`, `error.message` i opcjonalne `error.details`. Kody obejmują m.in. `INVALID_QUERY`, `DUPLICATE_FEATURE_ID`, `UNKNOWN_PROFILE`, `INCOMPATIBLE_FEATURE`, `DATASET_UNAVAILABLE`, `DATASET_VERSION_UNAVAILABLE`, `SCOPE_UNAVAILABLE`, `ANALYSIS_EXPIRED` i `LIMIT_EXCEEDED`. Błąd nie może zastąpić brakującego wyniku zerem ani podmienić wygasłej analizy aktualnym zbiorem.

## Walidacja i zmiany wersji

Schematy i przykłady walidują `contracts/tests/`; fixture'y zawierają wyłącznie syntetyczne dane i nigdy nie dowodzą wyniku naukowego. `uniqueItems` całych obiektów nie zastępuje semantycznej unikalności `feature_id`. Szczegóły uruchomienia znajdują się w [contracts/README.md](../contracts/README.md).

Zmiana znaczenia, usunięcie pola lub niekompatybilna zmiana struktury wymaga nowego `contract_version`, aktualizacji OpenAPI, schematów, fixture'ów, testów oraz uzgodnienia z konsumentem. Jednostki, sposób agregacji, tryb rankingu i reguły braków są częścią kontraktu.
