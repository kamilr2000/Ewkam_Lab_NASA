# Przekazanie: K-003 — kontrakt API v1 i syntetyczne fixture'y

- Od: Kamil, `codex-kamil-k003-contract`
- Do: Ewelina
- Data i strefa: 2026-11-14, Europe/Warsaw
- Zadanie / PR / commit implementacji: K-003 / [PR #7](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/7) / `b439941e1a6d33573b5de46654004fe2ab8a51b0`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-003-contract-v1`
- Czy rezerwacja / rezultat są w origin/main: rezerwacja K-003 (`619dc9a`) jest w `origin/main`; rezultat jest opublikowany na gałęzi i w PR #7, jeszcze nie w `main`.
- Lokalne niewysłane zmiany: brak.
- Stan: gotowe do przeglądu.

## Co jest dostępne

Kontrakt `1.0.0` obejmuje OpenAPI i schematy JSON Schema Draft 2020-12 dla katalogu, profilu, manifestu, requestu/wyniku wyszukiwania, szczegółów piksela, agregatów mapy, błędów i istniejącego endpointu health. Zakres wyszukiwania jest jawnie globalny lub regionalny. Ranking pojedynczych pikseli, agregaty komórek mapy i tryb `distinct_areas` mają odrębne kształty. Brak wyniku jest `null` z powodem.

Fixture'y w `contracts/fixtures/` są syntetyczne. Są dostępne przypadki katalogu/profilu/manifestu, sukcesu, pustego zasięgu, braku pomiarów, błędu `DATASET_UNAVAILABLE`, pojedynczego hotspotu, trybu różnych obszarów, szczegółu piksela i mapy. Nie są to pomiary Marsa, Księżyca, Ziemi ani dane NASA/NOAA.

Zaimplementowany jest tylko `GET /api/v1/health` z K-001; pozostałe ścieżki w `contracts/openapi.yaml` są planowanym interfejsem, nie działającym API ani deklaracją dostępności zbiorów. Nie pobierano ani nie przetwarzano rzeczywistych danych naukowych.

## Jak odtworzyć

Z katalogu głównego repozytorium:

```powershell
uv sync --locked --dev
uv run --locked pytest contracts/tests/test_contracts.py
python tools/check_planning.py
```

Walidator JSON Schema to przypięte `jsonschema==4.26.0`. Semantyczne kontrole w `contracts/validation.py` uzupełniają JSON Schema o unikalność `feature_id` i powody wartości `null` w manifeście.

## Sprawdzenia

- `uv run --locked pytest contracts/tests/test_contracts.py`: 34 testy zaliczone.
- `python tools/check_planning.py`: OK — 98 plików Markdown, 59 JSON, 35 kart i acykliczne zależności.
- Parser YAML odczytał `contracts/openapi.yaml`: 7 ścieżek; wszystkie 9 lokalnych odwołań do schematów istnieje.
- 23 pliki JSON kontraktów i fixture'ów parsują się.
- `git diff --check`: bez błędów.

Nie uruchamiano serwera, bo K-003 nie implementuje endpointów. Nie sprawdzano pobierania, pokrycia ani przetwarzania rzeczywistych danych; syntetyczne przykłady nie dowodzą jakości naukowej ani globalnej kompletności.

## Ograniczenia i potrzebne działania

Proszę sprawdzić PR #7 i potwierdzić, że kształt `SearchRequest`/`SearchResponse`, `PixelDetails`, `ProfileResponse`, `DatasetManifest`, jednostki, zakresy, braki i rozdzielenie rankingu od agregacji pozwalają odtworzyć UI w E-003/E-004. Uwagi kontraktowe zapisujemy w PR; niekompatybilna zmiana wymaga nowej wersji.

Po akceptacji PR należy połączyć K-003 do `main`. To nie zmienia ograniczenia, że tylko health jest dziś wdrożony; backend i wyniki na danych rzeczywistych pozostają kolejnymi zadaniami.
