# Przekazanie: K-022 — zgodność scope i coverage hotspotu

- Od: Kamil, `codex-kamil-k022-hotspot-coverage`
- Do: Ewelina
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: K-022 / PR do otwarcia / implementacja `8fb3ab5`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-022-hotspot-coverage`
- Wysłane SHA i URL PR: gałąź w trakcie publikacji; uzupełnić po pushu
- Czy rezerwacja / rezultat są w origin/main: rezerwacja K-022 jest w `origin/main` od PR #27, SHA `721d201c9dff38c32ccff97f33a20c04d7bc01d9`; poprawka oczekuje na review przed integracją
- Lokalne niewysłane zmiany i powód, jeśli występują: brak po publikacji gałęzi
- Stan: częściowe — implementacja gotowa na gałęzi; publikacja review i E-022 przed integracją

## Co jest dostępne

Oba fixture'y pozostają syntetyczne. W `search-hotspot-synthetic.json` północny zasięg `scope.geometry` zmniejszono z 3.02°N do 3.01°N; w `map-hotspot-synthetic.json` bbox dostosowano do tego samego extentu. Geometrie czterech pikseli i dwóch komórek oraz ich wyniki nie zmieniły się. Po poprawce piksele i komórki dzielą scope bez luk i nakładania; `map_cells` search i map response są identyczne.

Test semantyczny weryfikuje search scope, query bbox, identyczność agregatów, pokrycie extentu komórkami i pikselami, liczniki, powierzchnie, frakcje oraz syntetyczne oznaczenia. Osobny negatywny przypadek przywraca dawny północny pas w pamięci i oczekuje błędu pokrycia. Istniejący test nadal sprawdza, że piksel 100% pozostaje Top 1 i widoczny przez maksimum komórki, mimo niższej średniej.

Przed poprawką deklarowany extent miał `[3, 3, 3.04, 3.02]`, a geometrie kończyły się na 3.01°N. Nieodwzorowany pas wynosił 0.04° × 0.01° = 0.0004 stopnia kwadratowego w układzie fixture'u; to nie jest fizyczna powierzchnia. Po poprawce extent wynosi `[3, 3, 3.04, 3.01]`. Liczniki nadal wynoszą cztery piksele całkowite i kwalifikujące się, pola 4/4 km², frakcja 1; komórki mają liczniki 3/3 i 1/1.

Ponownie sprawdziłem E-019 na jego dokładnym reviewed ref `fde069cb35342986c5d2cc656a66fa90191377a9`: osie diagramu i dwie komórki obejmują 3.00–3.01°N i 3.00–3.04°E, zgodnie z poprawionym fixture'em. Nie zmieniałem plików projektowych Eweliny.

## Jak odtworzyć

Uruchom z katalogu głównego repozytorium:

```text
.venv\Scripts\python.exe -m pytest contracts/tests/test_contracts.py
python tools/check_planning.py
python -m json.tool docs/ai-usage.json
```

## Sprawdzenia

- `contracts/tests/test_contracts.py`: 42 passed na Pythonie 3.12.14, pytest 9.2.0.
- `python tools/check_planning.py`: OK — dokumenty, JSON-y, 56 kart i acykliczne zależności.
- `git diff --check`: bez błędów.
- `map-response.schema.json` i `search-response.schema.json` przechodzą w tym samym zestawie testowym; wersja kontraktu pozostaje 1.0.0.
- Nie testowałem działającego API ani rzeczywistych danych; fixture jest syntetyczny.

## Ograniczenia i potrzebne działania

Ewelina: po publikacji małego PR koordynacyjnego z kartą E-022 i statusem K-022 `review` sprawdź wskazany SHA/PR. Potwierdź extent/bbox, test negatywny i zgodność handoffu E-019 z nowym fixture'em. Implementacja pozostanie poza `main` do zakończenia review; dane ani zachowanie API nie są przedmiotem tej poprawki.
