# Przekazanie: K-003 — kontrakt API v1 i syntetyczne fixture'y

- Od: Kamil, `codex-kamil-k003-contract`
- Do: Ewelina
- Data i strefa: 2026-11-14, Europe/Warsaw
- Zadanie / PR / commity implementacji: K-003 / [PR #7](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/7) / bazowy `b439941e1a6d33573b5de46654004fe2ab8a51b0`, poprawka geometrii `0f7eb71a6a64b08211ef3df43ac28664f1a2bf95`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-003-contract-v1`
- Czy rezerwacja / rezultat są w origin/main: rezerwacja K-003 (`619dc9a`) jest w `origin/main`; rezultat jest opublikowany na gałęzi i w PR #7, jeszcze nie w `main`.
- Lokalne niewysłane zmiany: brak.
- Stan: poprawka po E-013 opublikowana; czeka na E-015.

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

Walidator JSON Schema to przypięte `jsonschema==4.26.0`. Semantyczne kontrole w `contracts/validation.py` uzupełniają JSON Schema o unikalność `feature_id` i powody wartości `null` w manifeście. Schematy katalogu, mapy i szczegółu pikseli walidują zagnieżdżenie MultiPolygon do pozycji; nie sprawdzają domknięcia pierścieni ani topologii. Negatywna regresja obejmuje błędny typ elementu i długość geograficzną 181 dla każdego z tych trzech payloadów.

## Sprawdzenia

- `uv run --locked pytest contracts/tests/test_contracts.py`: 34 testy zaliczone dla pierwotnego kontraktu. Po poprawce `pytest -q contracts/tests/test_contracts.py` w istniejącym środowisku `.venv-k003-contract`: 40 testów zaliczonych.
- `python tools/check_planning.py`: OK — 107 plików Markdown, 62 JSON, 39 kart i acykliczne zależności.
- Parser YAML odczytał `contracts/openapi.yaml`: 7 ścieżek; wszystkie 9 lokalnych odwołań do schematów istnieje.
- 23 pliki JSON kontraktów i fixture'ów parsują się.
- `git diff --check`: bez błędów.

Próba odtworzenia `uv run --locked pytest` w bieżącym środowisku nie mogła zapisać cache interpretera do katalogu aplikacji; te same testy uruchomiono w istniejącym środowisku K-003. Nie uruchamiano serwera, bo K-003 nie implementuje endpointów. Nie sprawdzano pobierania, pokrycia ani przetwarzania rzeczywistych danych; syntetyczne przykłady nie dowodzą jakości naukowej ani globalnej kompletności.

## Ograniczenia i potrzebne działania

E-013 wskazało, że nieprawidłowe `MultiPolygon.coordinates` mogło przejść przez katalog, mapę i szczegóły piksela. Poprawkę sprawdzająca zagnieżdżenie oraz regresje opublikowano w PR #7 jako `0f7eb71a6a64b08211ef3df43ac28664f1a2bf95`; E-015 w [origin/main](../tasks/E-015.md) prosi Ewelinę o niezależny review dokładnie tego SHA. Proszę też potwierdzić, że pozostałe kształty `SearchRequest`/`SearchResponse`, `PixelDetails`, `ProfileResponse`, `DatasetManifest`, jednostki, zakresy, braki i rozdzielenie rankingu od agregacji pozwalają odtworzyć UI w E-003/E-004.

Po akceptacji PR należy połączyć K-003 do `main`. To nie zmienia ograniczenia, że tylko health jest dziś wdrożony; backend i wyniki na danych rzeczywistych pozostają kolejnymi zadaniami.
