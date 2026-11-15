# Przekazanie: K-047 — wykonalność danych termicznych

- Od: Kamil / `codex-kamil-k047-thermal-preflight`
- Do: Ewelina
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: K-047 / [PR #84](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/84) / exact code ref `fad5b3b9b36043cd93fe5517c67a116fe8d899a4`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-047-thermal-feasibility`
- Baza PR #84: `origin/main` `db23641...`; head po synchronizacji main, przed tą aktualizacją handoffu: `44163689e17c027aed018b77ee9c7e7a4b1b95fc`.
- Wysłane SHA i URL PR: poprawka runnera `fad5b3b9b36043cd93fe5517c67a116fe8d899a4` opublikowana; dokładny bieżący head PR jest w metadanych PR #84.
- Czy rezerwacja / rezultat są w origin/main: rezerwacja K-047 oraz karta E-032 są w `origin/main`; karta K-047 i wynik na gałęzi PR #84 mają `review`, ale kod nie jest jeszcze połączony.
- Lokalne niewysłane zmiany i powód, jeśli występują: wyłącznie znany diff końców linii w `tasks/K-007.md`, wykluczony z commitów K-047.
- Stan: pakiet K-047 jest gotowy do niezależnego review. E-032 w `origin/main` nadal ma stary placeholder `review_ref`; Ewelina musi go odświeżyć do `fad5b3b9b36043cd93fe5517c67a116fe8d899a4` i opublikować własną rezerwację przed rozpoczęciem oceny.

## Co jest dostępne

- `pipeline/experiments/thermal/run_feasibility.py` pobiera brakujące próbki, sprawdza rozmiar i SHA-256 oraz generuje analizę i raport.
- `data/manifests/thermal-feasibility.json` przypina 36 plików źródłowych, trzy maski NASADEM z K-017, zasięg, wersje, jednostki, QA, skale, źródła i warunki użycia. Surowe pliki pozostają poza Gitem w `data/raw/k047` oraz `data/raw/k017`.
- `data/reports/thermal-feasibility.md` przedstawia rzeczywiste pomiary dla pięciu obszarów: trzech AOI Ziemi, profilu Księżyca 80–90°S oraz Jezero.
- `docs/DECISIONS.md` zawiera `D-024`: `NO-GO` dla jednej wspólnej punktowanej warstwy MODIS–Diviner–TES. K-010 pozostaje P1; nie zmieniłem P0, produkcyjnego scoringu, API, kontraktu ani UI.

Najważniejsze wyniki: wsparcie MODIS zależy silnie od AOI i daty; księżycowa nocna próbka ma 828 z 72 580 komórek z co najmniej 80% poprawnych punktów postingowych; bezwładność TES ma przy Jezero posting około 2,8–3,0 km, więc nie przypisuję jej niezależnego wsparcia w komórkach 2 km. Diviner TB3 jest temperaturą jasnościową, a TES wielkością modelowaną; wspólne K nie czyni ich równoważnymi.

## Jak odtworzyć

Gdy przypięte pliki źródłowe są już lokalnie dostępne, na Pythonie 3.12 odtwórz weryfikację i analizę bez pobierania:

```powershell
.venv\Scripts\python.exe pipeline/experiments/thermal/run_feasibility.py --no-download-missing
```

Przy brakujących wejściach użyj `--download-missing`; pobieranie MODIS wymaga lokalnego `EARTHDATA_TOKEN` przez `earthaccess`. Nie zapisuj tokenu do plików projektu ani logów. Diviner i zakresy bajtów PDS są pobierane z URL-i przypiętych w manifeście. `--report` przyjmuje także ścieżkę absolutną poza repozytorium; test regresji sprawdza sposób jej wyświetlania po wygenerowaniu pliku.

## Sprawdzenia

- Bieżący runner zweryfikował wszystkie 39 dostępnych plików (144 901 027 bajtów), dopasowując zapisane rozmiary i SHA-256, oraz ponownie przeliczył trzy AOI Ziemi dla czterech dat dziennych i nocnych, cykl dzień/noc Diviner i próbki MGS TES 25×25 z maską bezpośredniości/interpolacji.
- Wartości bloków `earth`, `moon`, `mars` i fingerprinty manifestów źródłowych są identyczne z poprzednim pomiarem. Manifest zapisuje nowy hash aktualnego runnera: `b5854aa1e93902b110555feb70b6611c37db352cf68b740ee1913ef926cf5f2a`.
- `pipeline/tests/test_thermal_feasibility.py`: 1 passed; `pipeline/tests contracts/tests`: 48 passed. Testy i re-run nie pobierały danych; surowe próbki lokalne miały już poprawne SHA-256.
- Runner raz zakończył kodem 1 po wygenerowaniu raportu, gdy `--report` wskazywał folder tymczasowy poza repozytorium. Poprawiłem wyłącznie wyświetlenie ścieżki i dodałem regresję; powtórzenie z absolutną ścieżką wyjściową zakończyło się kodem 0.
- Osobno pobrano na próbę jeden MODIS przez Earthdata i jeden 25×25 wycinek przez zakres PDS; oba pliki zgodziły się z przypiętym SHA-256 i zostały usunięte po kontroli.
- `python tools/check_planning.py`: 189 Markdown, 43 JSON, 96 kart, zależności acykliczne i pięć syntetycznych przypadków; manifest JSON oraz `git diff --check` przechodzą.
- QA, jednostki, lokalne czasy, skale i model TES sprawdzono w dokumentacji wskazanej przy źródłach manifestu. `NO-GO` jest ograniczone do wymienionych produktów i próbek.

Nie wykonano pełnego pobrania wszystkich próbek w świeżym klonie, globalnej analizy sezonowej ani uruchomienia aplikacji. Próbki nie są klimatologią i nie dowodzą globalnego pokrycia.

## Ograniczenia i potrzebne działania

Ewelina: zaktualizuj kartę E-032 w `origin/main` do exact code ref `fad5b3b9b36043cd93fe5517c67a116fe8d899a4` i bieżącego headu PR #84, a następnie opublikuj osobny commit `tasks(E-032): IN PROGRESS` przed rozpoczęciem review. Niezależnie sprawdź reguły wsparcia, konwersje i fizyczne interpretacje; jeśli Earthdata nie jest skonfigurowana na Twoim komputerze, zapisz ten brak jako ograniczenie i nie proś o token w czacie. Opublikuj werdykt i ewentualne poprawki z priorytetem, właścicielem oraz kryterium akceptacji.

Następna decyzja techniczna dotyczy K-010: `NO-GO` nie uzasadnia uruchomienia wspólnej termicznej funkcji. Osobna cecha temperatury albo bezwładności wymaga własnego, zgodnego zestawu obserwacji i modelu. NASA submission pozostaje działaniem wyłącznie człowieka.
