# Przekazanie: K-047 — wykonalność danych termicznych

- Od: Kamil / `codex-kamil-k047-thermal-preflight`
- Do: Ewelina
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: K-047 / [PR #84](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/84) / implementacja `062c433`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-047-thermal-feasibility`
- Wysłane SHA i URL PR: commit `062c433` opublikowany; exact finalny PR head jest dostępny w PR #84 i zostanie przypięty do E-032 przed startem review.
- Czy rezerwacja / rezultat są w origin/main: rezerwacja K-047 oraz karta E-032 są w `origin/main`; wynik K-047 jest na gałęzi PR #84 i nie został jeszcze połączony.
- Lokalne niewysłane zmiany i powód, jeśli występują: brak.
- Stan: gotowe do niezależnego review; K-047 ma status `review`, a E-032 oczekuje na odświeżenie exact `review_ref`.

## Co jest dostępne

- `pipeline/experiments/thermal/run_feasibility.py` pobiera brakujące próbki, sprawdza rozmiar i SHA-256 oraz generuje analizę i raport.
- `data/manifests/thermal-feasibility.json` przypina 36 plików źródłowych, trzy maski NASADEM z K-017, zasięg, wersje, jednostki, QA, skale, źródła i warunki użycia. Surowe pliki pozostają poza Gitem w `data/raw/k047` oraz `data/raw/k017`.
- `data/reports/thermal-feasibility.md` przedstawia rzeczywiste pomiary dla pięciu obszarów: trzech AOI Ziemi, profilu Księżyca 80–90°S oraz Jezero.
- `docs/DECISIONS.md` zawiera `D-024`: `NO-GO` dla jednej wspólnej punktowanej warstwy MODIS–Diviner–TES. K-010 pozostaje P1; nie zmieniłem P0, produkcyjnego scoringu, API, kontraktu ani UI.

Najważniejsze wyniki: wsparcie MODIS zależy silnie od AOI i daty; księżycowa nocna próbka ma 828 z 72 580 komórek z co najmniej 80% poprawnych punktów postingowych; bezwładność TES ma przy Jezero posting około 2,8–3,0 km, więc nie przypisuję jej niezależnego wsparcia w komórkach 2 km. Diviner TB3 jest temperaturą jasnościową, a TES wielkością modelowaną; wspólne K nie czyni ich równoważnymi.

## Jak odtworzyć

W klonie z Pythonem 3.12:

```powershell
uv run --locked --group data python pipeline/experiments/thermal/run_feasibility.py --download-missing
```

Pobranie brakujących MODIS wymaga lokalnego `EARTHDATA_TOKEN`, używanego przez `earthaccess`. Nie zapisuj go do plików projektu ani logów. Publiczne Diviner i zakresy bajtów PDS są pobierane z adresów w manifeście. Wynik bieżącego uruchomienia: 39 plików, 144 901 027 bajtów, wszystkie rozmiary i SHA-256 zgodne.

## Sprawdzenia

- Runner przeliczył trzy AOI Ziemi dla czterech dat dziennych i nocnych, księżycowy dzień/nocny cykl Diviner oraz próbki MGS TES 25×25 z maską bezpośredniości/interpolacji.
- Osobno pobrano na próbę jeden MODIS przez Earthdata i jeden 25×25 wycinek przez zakres PDS; oba pliki zgodziły się z przypiętym SHA-256 i zostały usunięte po kontroli.
- `python tools/check_planning.py` przeszedł; JSON manifestu jest poprawny; `git diff --check` przeszedł.
- QA, jednostki, lokalne czasy, skale i model TES sprawdzono w dokumentacji wskazanej przy źródłach manifestu. `NO-GO` jest ograniczone do wymienionych produktów i próbek.

Nie wykonano pełnego pobrania wszystkich próbek w świeżym klonie, globalnej analizy sezonowej ani uruchomienia aplikacji. Próbki nie są klimatologią i nie dowodzą globalnego pokrycia.

## Ograniczenia i potrzebne działania

Ewelina: wykonaj E-032 na exact headzie PR #84 po opublikowaniu jego SHA w `review_ref`. Niezależnie sprawdź reguły wsparcia, konwersje i fizyczne interpretacje; jeśli Earthdata nie jest skonfigurowana na Twoim komputerze, zapisz ten brak jako ograniczenie i nie proś o token w czacie. Opublikuj werdykt i ewentualne poprawki z priorytetem, właścicielem oraz kryterium akceptacji.

Następna decyzja techniczna dotyczy K-010: `NO-GO` nie uzasadnia uruchomienia wspólnej termicznej funkcji. Osobna cecha temperatury albo bezwładności wymaga własnego, zgodnego zestawu obserwacji i modelu. NASA submission pozostaje działaniem wyłącznie człowieka.
