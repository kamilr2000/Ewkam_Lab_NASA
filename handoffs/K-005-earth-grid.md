# K-005 — regionalne pakiety siatki Ziemi

## Zakres i odtwarzanie

Pakiety obejmują jawne AOI Atacama/Andy, Big Island na Hawajach i Himalaje. Każdy AOI ma niezależną siatkę lokalnego UTM 2 km. Najpierw GSHHG maskuje oceaniczne piksele na natywnej siatce ETOPO 15″, aby batymetria nie zaniżała lądowej średniej przy wybrzeżu; potem wysokości wyłącznie lądowych próbek są uśredniane do siatki 2 km. Maska docelowa nadal niezależnie rozstrzyga lądowy środek kandydata, a 4× udział podkomórek opisuje przybliżenie udziału lądu w komórce. Kandydatami są środki komórek w bbox AOI, a bufor służy wyłącznie obliczeniu cech z oknem 10 km. Zmienione pomiary używają wersji siatki/modelu v2.

Na czystym środowisku z zależnościami zablokowanymi przez `uv.lock` odtworzenie wygląda tak:

```text
uv run --locked --group data python pipeline/download_k005_sources.py
uv run --locked --group data python pipeline/build_k005_earth_grid.py
```

Downloader pobiera tylko publiczne wejścia i weryfikuje je względem rozmiaru oraz SHA-256 zapisanych w K-017. Token Earthdata nie jest wymagany. Duże dane wejściowe i checkpointy są ignorowane przez Git, ale trzy małe, skompresowane tabele wynikowych komórek (łącznie mniej niż 200 kB) są śledzone w `data/derived/k005-earth-grid/`, aby następny etap API i UI mógł skorzystać z nich bez ponownego przetwarzania. Manifesty i podsumowanie QA również są śledzone. Uruchomienie buildera ponownie weryfikuje checkpointy; `--force` przelicza je. Można wybrać AOI przez `--aoi <nazwa>`.

## Wynik z danych lokalnych

| AOI | Komórki kandydujące | Lądowe środki | Kwalifikujące się | Przyczyna wykluczenia | Suma powierzchni komórek |
|---|---:|---:|---:|---|---:|
| Atacama / Andy | 1 796 | 1 796 | 1 791 | 5 zbyt małe wsparcie okna 10 km | 7 189,193164 km² |
| Big Island | 1 854 | 1 703 | 1 497 | 151 woda, 62 niekompletne sąsiedztwo nachylenia, 144 słabe wsparcie okna | 7 409,230122 km² |
| Himalaje | 1 737 | 1 737 | 1 737 | brak | 6 953,058955 km² |

Powierzchnia pojedynczej komórki jest obliczona geodezyjnie z narożników po transformacji UTM do WGS84; 4 km² to nominalne pole płaszczyzny UTM. Po zastosowaniu maski źródłowej 134 z 1 854 środków Big Island nie miały żadnej lądowej próbki ETOPO i pozostały nodata; 151 wodnych środków odrzucono przez niezależną docelową maskę GSHHG. Wartości cech w tych pakietach są pomiarami topografii, nie punktacją analogów ani rankingiem.

Ręcznie przeliczono co najmniej jedną komórkę dla każdego AOI; maksymalna różnica cech w stosunku do funkcji pipeline wyniosła 6,17e-6 dla Atacama/Andów, 1,42e-5 dla Big Island i 5,29e-6 dla Himalajów. Jednostki: nachylenie w stopniach, lokalna nierówność po odjęciu dopasowanej płaszczyzny w metrach, deniwelacja P95−P05 w metrach. Okno ma promień 10 km; brakujące próbki pozostają brakami. Dla Qattary K-005 odwołuje się do wcześniej zweryfikowanego dowodu z K-017: NASADEM −80 m względem EGM96, przy zgodnych klasach lądu SWB/GSHHG. Pakiet K-005 nie przetwarza ponownie NASADEM.

## Skala i ograniczenia

Siatka 60″ ma 233 280 000 komórek globalnych. Model float32 ETOPO i maski źródłowej wylicza 933 120 000 B dla docelowego DEM, 6 065 280 000 B dla pełnego stanu komórek oraz 208 094 400 B dla partii 64 wierszy z halo przed buforami GDAL/PROJ i geometrii. To rachunek pamięci bez zmierzonego szczytowego RSS ani czasu globalnego przebiegu. K-005 nie buduje globalnego rastra, nie bada biegunów i nie twierdzi o globalnym optimum ani globalnym Top 10. Siatki lokalnej UTM nie należy mieszać z siatką przyszłego rankingu globalnego.

## Sprawdzenia

- Pięć testów jednostkowych pokrywa budżet 60″, siatkę UTM/pole geodezyjne, ręczny wzór cech, brak wypełniania nodata zerem i wykluczanie batymetrii z lądowego resamplingu.
- Testy pełnego pipeline, planera i kontraktów oraz kontrola dokumentacji są zapisywane w karcie K-005 po uruchomieniu przed publikacją.
- Builder został uruchomiony ponownie bez `--force`; trzy zweryfikowane checkpointy zostały pominięte.
- Manifesty są walidowane przez JSON Schema i kontrolę semantyczną; SHA-256 danych wynikowych i liczniki CSV zgadzają się z manifestami.

Commit/PR i dokładny SHA wdrożenia zostaną dopisane po publikacji implementacji.
