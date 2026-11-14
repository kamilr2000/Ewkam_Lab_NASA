# Kontrakty API

Kontrakt v1 ma `contract_version: 1.0.0`. [openapi.yaml](openapi.yaml) opisuje operacje HTTP; lokalne schematy Draft 2020-12 definiują payloady odpowiedzi i requestu. Zasady semantyczne i implementowane endpointy opisuje [docs/CONTRACTS.md](../docs/CONTRACTS.md).

## Schematy

| Plik | Payload |
|---|---|
| [health-response.schema.json](health-response.schema.json) | Stan procesu API i datasetu |
| [catalog-response.schema.json](catalog-response.schema.json) | Datasety, cechy, profile i dozwolone regiony wyszukiwania |
| [profile-response.schema.json](profile-response.schema.json) | Wersjonowany profil Marsa lub Księżyca z układem ciała, jednostkami i skalą |
| [dataset-manifest.schema.json](dataset-manifest.schema.json) | Pochodzenie, licencje, pliki, siatka, QA, pokrycie i przetwarzanie |
| [search-request.schema.json](search-request.schema.json) | Jawny scope, aktywne cechy/wagi i odrębny tryb wyników |
| [search-response.schema.json](search-response.schema.json) | Ranking pikseli **albo** ranking reprezentantów różnych obszarów oraz agregaty mapy |
| [pixel-details-response.schema.json](pixel-details-response.schema.json) | Pomiary/źródła jednej komórki z kontekstu analizy |
| [map-response.schema.json](map-response.schema.json) | Ograniczone bbox agregaty dla tej samej analizy |
| [error-response.schema.json](error-response.schema.json) | Wspólna struktura błędu |

`uniqueItems` nie wykrywa powtórzonego `feature_id`, jeśli wagi dwóch obiektów kryteriów są inne. Po walidacji JSON Schema API wywołuje [walidację semantyczną](validation.py); kolejny etap sprawdza zgodność datasetu, profilu, ciała i dostępności cech z katalogiem. Null w manifeście ma przyczynę w lokalnym polu albo w `missing_reasons` podającym ścieżkę pola; walidator semantyczny sprawdza, czy przyczyna została zapisana.

## Fixture'y

Każdy fixture z wartościami profilu lub analizy jest syntetyczny i nie opisuje rzeczywistego miejsca ani danych NASA/NOAA. Pole `is_synthetic: true`, nazwa pliku i opisy ostrzeżeń pozwalają UI ujawnić stan demo.

- `catalog-synthetic.json`, `profile-synthetic.json`, `dataset-manifest-synthetic.json` — przykładowy katalog/profil/manifest.
- `search-request-synthetic.json`, `search-success-synthetic.json` — poprawna konfiguracja i wynik.
- `search-empty-synthetic.json` — pusty zakres bez komórek, z `eligible_area_fraction: null` i przyczyną.
- `search-no-data-synthetic.json` — komórki istnieją, ale aktywne wartości są brakujące; wynik mapy jest `null`, nie zero.
- `search-hotspot-synthetic.json`, `pixel-hotspot-synthetic.json`, `map-hotspot-synthetic.json` — pojedynczy mocny piksel pozostaje w rankingu i w maksimum mapy mimo słabego otoczenia.
- `search-distinct-areas-synthetic.json` — osobne pole `area_ranking`, jawny dystans i agregaty mapy niezależne od wybranych reprezentantów.
- `error-dataset-unavailable-synthetic.json` — błąd nie udaje pustego ani zerowego wyniku.
- `hotspot-regression.json` — przypadki syntetyczne dla logiki rankingowej z wcześniejszego planu.
- `health-ready-no-dataset.json` — kształt istniejącej odpowiedzi K-001; API może być gotowe, gdy dataset nie jest gotowy.

## Walidacja

JSON Schema waliduje przypięty `jsonschema==4.26.0` w grupie developerskiej. Z katalogu repo:

```text
uv sync --locked --dev
uv run --locked pytest contracts/tests/test_contracts.py
```

Walidator sprawdza same schematy, fixture'y zgodne z każdym typem payloadu, poprawne i niepoprawne kombinacje trybu oraz semantyczną unikalność `feature_id`. Te kontrole dotyczą kontraktów i przykładów; nie dowodzą, że planowane endpointy lub naukowe dane są już wdrożone.
