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

Pierwotny pakiet opublikowano w PR #44 pod exact ref `a5dfe3d892235d31938dcdd56bdcc17a66e0f167`. Po review E-024 fingerprint metadanych poprawiono w exact commicie `d3b880cacbbdf339d078a2fbedbe8fd373db7bef`. PR #44 zawiera również późniejsze commity dokumentujące korektę i synchronizujące branch; ocena danych wskazuje jawnie na ten exact commit.

## Korekta po E-024: kod fingerprintu

E-024 wykazała, że fingerprint `feab8cb9a942e6c7e8217f0d27d1a9b1f676d874d8c99ba32b6d4e9c2b81778f` zapisany w trzech manifestach i raporcie nie odpowiadał exact kodowi K-005. Po pobraniu i zweryfikowaniu przypiętych publicznych źródeł (`uv run --locked --group data python pipeline/download_k005_sources.py`) uruchomiono `uv run --locked --group data python pipeline/build_k005_earth_grid.py --force`. Aktualne `_code_fingerprint()` wylicza `56543c206661c3158999fd442f13a3ebc56e695333da8b2ad01b1e19d8d63829`; raport i wszystkie trzy manifesty zapisują zgodnie ten sam hash.

| AOI | Wiersze danych | SHA-256 CSV po rebuildzie | Rozmiar |
|---|---:|---|---:|
| Atacama / Andy | 1 796 | `784ccc0dbebe4e846774ac819809029a31f082cb16931e6bbe882da26c0f570c` | 63 856 B |
| Big Island | 1 854 | `5489e51b4ec4f1a770fe7e7511565de6e5083b4547ebb48d61ada3af0ec4668b` | 64 177 B |
| Himalaje | 1 737 | `30a3dd1d93277a766b9d7d9ddcd8a2c05c9db4df374a4bb310eaac97f143479c` | 61 206 B |

Wszystkie CSV zachowały SHA i rozmiary z poprzedniej publikacji; zmieniły się metadane pochodzenia, czas rebuilda i rzeczywiste czasy przetwarzania zamiast wartości z pominiętych checkpointów. Manifesty przechodzą `contracts/dataset-manifest.schema.json` (Draft 2020-12), a niezależna kontrola potwierdza zgodność fingerprintu, SHA, rozmiaru i liczby wierszy. `uv run --locked --group data python -m pytest pipeline/tests contracts/tests -q` — 45 passed. `python tools/check_planning.py` i `git diff --check origin/main --` przechodzą.

Codex pomagał odtworzyć i zweryfikować metadane pochodzenia; nie utworzył ani nie edytował wartości pomiarowych ani CSV. Właścicielka rejestru, Ewelina, powinna ująć ten metadata-only follow-up w trwającym I-012 przed zamknięciem disclosure. Obecna walidacja nadal obejmuje trzy AOI regionalne; nie wykonano pełnego globu, biegunów ani globalnego rankingu.
