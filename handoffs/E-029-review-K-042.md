# E-029 — Niezależny review K-042

Data: 2026-11-15  
Oceniany exact ref: `affcd909bf3ac343ecb3a6d96f45b2d40658dbea`  
PR: [#72 — K-042: measured 2 km global grid pilot](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/72)  
Head PR podczas recenzji: `affcd909bf3ac343ecb3a6d96f45b2d40658dbea`  
Wynik: **REQUEST_CHANGES**, jeden P1: pobieranie przypiętych źródeł nie działa w czystym klonie.

## Zastrzeżenie P1

`pipeline/download_k042_sources.py` przekazuje do `download_public_file()` katalog `destination.parent`, ale nie tworzy go. Wspólna funkcja `pipeline/download_k017_assets.py:download_public_file()` przygotowuje nazwę pliku `.part` i otwiera ją do zapisu bez `mkdir`. Katalogi pod `data/raw` są ignorowane przez Git i nie istnieją w czystym klonie. Odtworzenie kończy się przed pobraniem pierwszego pliku błędem `FileNotFoundError` dla:

```text
data/raw/k042/etopo/ETOPO_2022_v1_15s_N00E165_surface.tif.part
```

Prośba w review przypięta do linii wywołania w PR: utworzyć katalog docelowy przed zapisem `.part` (najlepiej we wspólnym helperze) i dodać test regresyjny dla brakującego katalogu. Warunek akceptacji: pobranie, weryfikacja przypiętych SHA-256 i rozpakowanie GSHHG przechodzą z czystego klonu bez ręcznego `mkdir`. Właściciel: Kamil/K-042.

## Wykonane kontrole

Na dokładnym refie PR #72:

| Polecenie | Wynik |
|---|---|
| `.venv\Scripts\python.exe -m pipeline.download_k042_sources --verify-only` przed pobraniem | Oczekiwany brak przypiętego pliku w czystym drzewie źródeł |
| `.venv\Scripts\python.exe -m pipeline.download_k042_sources` przed utworzeniem katalogów | **Błąd P1:** brak katalogu nadrzędnego pliku `.part` |
| `uv run --locked --group data python -m pipeline.download_k042_sources --verify-only` po pobraniu | Wszystkie przypięte źródła zweryfikowane |
| `uv run --locked --group data python -m pipeline.global_grid_pilot --force` po ręcznym utworzeniu brakujących katalogów | Ukończono; pełne cztery rdzenie pilota |
| `uv run --locked --group data --group dev python -m pytest pipeline/tests contracts/tests -q` | 50 passed |
| `python tools/check_planning.py` | OK: 168 Markdown, 42 JSON, 84 task cards, zależności bez cykli, 5 przypadków syntetycznych |
| `git diff --check` | OK; tylko ostrzeżenia o konwersji CRLF/LF |

Pierwszy pełny niezależny przebieg przez `uv` przetworzył 16 384 komórki kandydujące, z których 13 912 spełniało warunki QA. Zmierzone lokalnie: 63,137 s, peak working set 448 479 232 B, skompresowany wynik 705 886 B. Czasy i pamięć różnią się od środowiska autora, więc nie zastępują wartości w opublikowanym raporcie.

## Źródła i sumy

Siedem kafli ETOPO 2022 v1 15″ Ice Surface (NOAA NCEI, DOI `10.25921/fd45-gt74`, CC0-1.0, WGS84, wysokości względem geoidy EGM2008) oraz archiwum GSHHG 2.3.7 (LGPL-3.0-or-later) pobrano i zweryfikowano rozmiarem oraz SHA-256. Katalogi raw utworzono ręcznie wyłącznie po odnotowaniu awarii czystego pobrania.

| Źródło | Bajty | SHA-256 |
|---|---:|---|
| `ETOPO_2022_v1_15s_N00E165_surface.tif` | 11 640 090 | `228580011ba4995553da6c72e2d17af3f55df4ac730dd64a27bfcb26648bf516` |
| `ETOPO_2022_v1_15s_N00W180_surface.tif` | 16 843 500 | `62ac5ab585cff2a6cffd862d63123f187bf03aff81fee0ffc08cadaf2d601fdc` |
| `ETOPO_2022_v1_15s_N30E015_surface.tif` | 33 429 495 | `1ee225cb379eb7c95d446337004f413a2eb270a4682383afb6930270ec04515c` |
| `ETOPO_2022_v1_15s_N30W165_surface.tif` | 22 411 557 | `8265ec91d7db7644d227374afe91d23662203a4eb3fd580626b3f7d3d27dc85c` |
| `ETOPO_2022_v1_15s_N90W045_surface.tif` | 14 851 825 | `d0999cc6b029eae2eb266c607778ac109052d9beb9588d53117e33d637bf92fe` |
| `ETOPO_2022_v1_15s_S75E000_surface.tif` | 22 866 882 | `946c142b64712f789931a3e9c863328343a517a2987f84cadd4c7ddfb75b5f4f` |
| `ETOPO_2022_v1_15s_S75W015_surface.tif` | 23 694 802 | `f3329a47b67dff29382cf1679302bb0db3940b091dba110331615f12b9d736b0` |
| `gshhg-shp-2.3.7.zip` | 149 157 845 | `8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41` |

Oficjalne potwierdzenia: [NOAA NCEI ETOPO 2022 metadata](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Aetopo_2022) oraz [SOEST GSHHG documentation](https://www.soest.hawaii.edu/wessel/gshhs/). Wariant ETOPO to Ice Surface, czyli powierzchnia nad uziemionym lodem; nie jest to bedrock ani miara grubości lodu. Maskowanie używa niezależnego GSHHG, a nie batymetrii jako maski oceanu.

## Odtworzone wyniki

Każdy testowy kafel zawiera 64 × 64 kandydatów. Dla każdego pliku wynikowego weryfikacja rozmiaru i SHA-256 względem manifestu zwróciła `true`.

| Kafel | Kandydaci | Kwalifikujące się | Ręczna kontrola cech |
|---|---:|---:|---|
| Hawaii coast | 4 096 | 1 861 | passed |
| Qattara depression | 4 096 | 4 096 | passed |
| Greenland high north | 4 096 | 3 859 | passed |
| Antarctica grounded | 4 096 | 4 096 | passed |

Wszystkie cztery SHA wyjściowych CSV.GZ zgadzają się z manifestem:

| Wynik | Bajty | SHA-256 |
|---|---:|---|
| `hawaii-coast.csv.gz` | 149 129 | `6a4f1cdee44e749587d6b305aa44cc48310abf6ab433126e9bbde95a8f3394d8` |
| `qattara-depression.csv.gz` | 180 760 | `70e7556bc20a9dc1882e31638eeea21756b5731e80819c011bf138d64b384f81` |
| `greenland-high-north.csv.gz` | 192 928 | `cd7c0700af1f99d52b7d488c749aa419b860ecff98c019213a26875cd2ec887f` |
| `antarctica-grounded.csv.gz` | 183 069 | `d3d5dfafc29c9e2013cd968855c21cd90c3ec58938b07cd1de88f859d5124a5a` |

Kontrole maski oraz próbki wysokości przeszły: mała wyspa/wybrzeże Hawaii, ocean obok Hawaii, depresja Qattara poniżej zera, północna Grenlandia, uziemiona Antarktyda i punkty wodne po obu stronach południka 180°. Qattara pozostała lądem przy `-78.353 m` (EGM2008); oceaniczna próbka Hawaii ma `-792.712 m` batymetrii, ale nie jest kandydatem lądowym. Próbki `179.99°E` i `179.99°W` dzieli 2 226.386 m po geodezyjnym zawinięciu; obie zostały oznaczone jako woda i mają prawidłową próbkę ETOPO.

## Ocena metody i granice

Pilot używa lokalnego UTM według strefy dla szerokości `|lat| < 80°` oraz EPSG:3413/EPSG:3031 dla obszarów polarnych. Raport przechowuje współczynnik skali projekcji i elipsoidalne pola komórek. Okno cech ma promień 10 km, a halo 14 km. Porównanie pokazuje, dlaczego stała siatka 60″ nadmiernie zagęszcza kandydatów względem powierzchni ku biegunom; liczba ~2 km pozostaje geometrycznym przybliżeniem, nie wygenerowaną globalną siatką.

To cztery lokalne rdzenie wraz z kontrolą punktową seam. Kod i raport jawnie deklarują `global_run_performed: false` i `global_ranking_performed: false`; nie ma dowodu pełnego pokrycia ani globalnego optimum. Kontrola 180° nie rasteruje pełnego kafla przecinającego seam, co pozostaje częścią bramki K-044 dotyczącą globalnego przypisania komórek i ciągłości seam.

PR #72 nadal jest otwarty i niepołączony. Podczas kontroli API GitHub wskazywało `mergeable: false`; baza PR to `f86f8a67e5e0c8a2098573dda8641a93f9b9278a`, a `origin/main` zdążył przejść do `0dbfe48eb55f0815dbf10343cf84c271a094d6ea`. Przed integracją autor powinien zsynchronizować gałąź i ponownie sprawdzić mergeability. Review nie zatwierdza integracji K-042 ani nie zamyka pracy nad globalnym przebiegiem.
