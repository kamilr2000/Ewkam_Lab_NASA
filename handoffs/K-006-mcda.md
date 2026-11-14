# Handoff K-006 — scoring i ranking pikseli

- Od: Kamil, `codex-kamil-k006-mcda`
- Do: Ewelina / K-007 i K-008
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR: K-006 / [PR #15](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/15)
- Repozytorium i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-006-mcda-ranking`
- Rezerwacja: `c04425e262460792a07678c95d8cfd2b41f44de4` jest w `origin/main`.
- Implementacja: `5ade37c9bc987a3cfb1087b334dd650c81630dad`; zsynchronizowany head PR przed handoffem: `8516281373145547bbf46949b74a3e497e73f9be`.
- Rezultat: opublikowany w PR #15, oczekuje na E-018; jeszcze nie scalony do `main`.

## Co implementuje silnik

- `FeatureCriterion` zawiera identyfikator cechy, wagę, przedział referencyjny, dodatnią tolerancję, jednostkę, skalę pomiaru i źródła profilu.
- `ScoringBatch` przyjmuje identyfikatory pikseli oraz kolumnowe tablice wartości, jawne maski ważności, metadane jednostek/źródeł, flagi QA, współrzędne WGS84 i wzajemnie rozłączne maski wykluczeń z powodami.
- `score_batch` liczy liniowe podobieństwo przedziałowe i zwraca `NaN`/brak wyniku dla niekwalifikujących się wierszy. `NaN` nie jest zamieniane na zero; punkt wymaga wartości dla każdej aktywnej cechy.
- `rank_pixel_batches` skanuje wszystkie przekazane wiersze w partiach, zlicza wykluczenia i utrzymuje Top K. Wynik jest sortowany po niezaokrąglonym score malejąco, a następnie po `pixel_id` rosnąco. Maksymalny Top K wynosi 10.
- Wkład każdej cechy wynosi `100 × normalized_weight × similarity_fraction`; suma wkładów jest wynikiem procentowym. Jednostki i skale muszą być zgodne dokładnie; moduł nie wykonuje konwersji jednostek.
- Skale `ratio` i `interval` używają metody liniowej. `ordinal`/`nominal` są odrzucane, bo wymagają osobnej, uzasadnionej funkcji podobieństwa.
- `select_distinct_areas` jest oddzielnym trybem. Używa odległości geodezyjnej WGS84 i czyta kandydatów dalej niż pixel Top K, aż wybierze żądaną liczbę różnych reprezentantów albo wyczerpie strumień.

## Uruchomienie i dowody

Z głównego katalogu repo:

```powershell
uv sync --locked --dev
uv run --locked pytest apps/api/tests/test_scoring.py contracts/tests/test_contracts.py
python tools/check_planning.py
```

Na scalonym środowisku Python 3.12.14 suite scoringu i kontraktu przeszło: 71 testów w 1,24 s. Kontrola planu przeszła (95 Markdown, 30 JSON, 45 kart, brak cykli, 5 przypadków syntetycznych), `git diff --check` bez błędów. Testy odtwarzają wszystkie pięć przypadków z `contracts/fixtures/hotspot-regression.json`, m.in. izolowany hotspot, rozdzielone maksima cech, braki, wagi i remisy; porównują ranking partiami z niezależnym pełnym sortowaniem.

Eksploracyjny mikrobenchmark na danych **syntetycznych**: 200 000 pikseli, trzy cechy, 171 464 kwalifikujące się i 28 536 wykluczonych, 0,092 s (~2,16 mln pikseli/s) w lokalnym środowisku. Nie zapisano parametrów sprzętu ani pomiaru pamięci; to nie dowodzi globalnego czasu ani kompletności zbioru.

Pełne `pytest -q` lokalnie zawisło w istniejącym teście endpointu health podczas żądania ASGI i zostało przerwane po ponad minucie. Nie uznajemy pełnego zestawu za zaliczony. K-001 ma wcześniejsze odrębne dowody uruchomienia health; ten problem środowiska warto sprawdzić ponownie w CI lub wspieranym środowisku.

## Kontrakt dla następnych zadań i ograniczenia

- Dane wejściowe muszą pochodzić z pełnego, zadeklarowanego zakresu oraz stabilnej wersji siatki. Silnik zlicza wszystkie przekazane wiersze, ale sam nie dowodzi, że iterator pokrył cały świat ani że nie powtórzył ID pomiędzy partiami. K-005/K-008 odpowiadają za kompletność pakietu i zakresu.
- `rank_pixel_batches` zwraca pixel Top K. Nie wolno użyć tej listy jako źródła `distinct_areas`. `select_distinct_areas` wymaga pełnego strumienia wszystkich kwalifikujących się pikseli, już posortowanego po niezaokrąglonym wyniku i ID. K-008 musi dostarczyć skalowalny sort zewnętrzny/strumień dla rzeczywistego globalnego zbioru.
- Moduł nie tworzy obrysów ani powierzchni pikseli, agregatów mapy, profili planetarnych ani endpointów HTTP. K-007 łączy wynik z geometrią i zamrożoną analizą; K-008 dodaje globalny zakres, agregaty mapy, cache, ograniczone odczyty i testy skanowania.
- Wartości w PR są wyłącznie syntetyczne. Nie wykonano tu jeszcze scoringu na realnych profilach Marsa/Księżyca ani na siatce Ziemi.
