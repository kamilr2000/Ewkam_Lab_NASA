# Metoda podobieństwa i granulacja

Status: specyfikacja projektowa v0.1. Dwa zmierzone profile P0 powstały w K-004; ich tolerancje i wspólna skala nadal wymagają analizy wrażliwości K-009. Progi i parametry poniżej są decyzjami inżynierskimi, nie ustaleniami NASA.

## 1. Co porównujemy

Konfiguracja = ciało niebieskie + konkretny region referencyjny + wersja profilu + wybrane cechy + dodatnie wagi + wersja siatki/danych + tryb wyników. „Mars” bez profilu regionalnego nie definiuje jednego zestawu warunków.

Profil zawiera geometrię regionu we współrzędnych właściwego ciała, statystyki zmierzonych cech, datę/wersję źródła, jednostki, definicję skali i uzasadnienie tolerancji. K-004 przygotował rzeczywiste profile Jezero i księżycowego obszaru 80–90°S. Ich zasięg i ograniczenia są częścią danych profilu, a nie domyślnym twierdzeniem o całej planecie.

## 2. Zmierzone profile K-004

Oba profile używają nominalnej komórki 2 km i kołowego okna cech o fizycznym promieniu 10 km. Każdy raster jest najpierw sprowadzany do siatki analitycznej właściwej dla jego ciała; absolutnych wysokości Marsa i Księżyca nie porównujemy.

| Profil | Geometria celu | Źródło i wsparcie | Pokrycie profilu |
|---|---|---|---:|
| Jezero, Mars | Okrąg 47,52 km średnicy wokół środka 18,41°N, 77,69°E z Gazetteer USGS; to geometryczna obwiednia, nie obrys brzegu krateru | MOLA MEGDR v2, MEGT + MEGC, kafel 44N000HB, 128 px/°. MEGT ma ok. 463 m/piksel na równiku i ok. 439 m E–W na szerokości Jezero | 448 komórek celu; 448/448 z trzema cechami. Średnio 35,4% źródłowych binów MEGC ma bezpośrednie obserwacje; 95,5% komórek 2 km przecina co najmniej jeden taki bin |
| Biegun południowy Księżyca | Sferyczna czapa 80–90°S, określona granicą pokrycia źródła; promień około 304,1 km w stereografii polarnej | NASA PGDA Product 90: LDEM, LDEC, EFFRES i ERR, nominalny posting DEM 80 m. Odległości cech uwzględniają zmianę skali stereografii; komórki odrzuca się, gdy uśredniona efektywna rozdzielczość przekracza 2 km | 72 580 komórek celu; 72 100/72 580 (99,34%) z trzema cechami. Efektywna rozdzielczość po uśrednieniu na komórkę analityczną 2 km: P50 42,49 m, P95 69,76 m |

Referencyjne zakresy to ważone powierzchnią P10–P90 cech komórek w profilu. Tolerancja to jawne, prowizoryczne założenie `1,5 × IQR` (P75−P25) tego samego profilu. Nie jest niepewnością instrumentu, nie pochodzi z dopasowania do znanego ziemskiego analogu i nie jest progiem NASA. K-009 ma sprawdzić zmianę rankingu przy innych tolerancjach i regułach jakości.

| Profil | Cecha | P10–P90 | Tolerancja K-004 |
|---|---|---:|---:|
| Jezero | Nachylenie | 0,377–5,682° | 3,040° |
| Jezero | Nierówność po odjęciu płaszczyzny | 20,658–175,207 m | 151,788 m |
| Jezero | Deniwelacja P95−P05 | 138,334–887,632 m | 630,221 m |
| Księżyc 80–90°S | Nachylenie | 1,281–14,385° | 10,412° |
| Księżyc 80–90°S | Nierówność po odjęciu płaszczyzny | 115,063–452,243 m | 252,451 m |
| Księżyc 80–90°S | Deniwelacja P95−P05 | 572,221–2 959,491 m | 1 947,640 m |

Wartości i źródłowe sumy kontrolne są zapisane w [manifeście wyników K-004](../data/manifests/k004-planetary-profiles.json); przypięte wejścia są w [manifeście plików](../data/manifests/k004-source-files.json). Reprodukcja używa `python pipeline/download_k004_sources.py`, a następnie `python pipeline/profiles/build_profiles.py`. Program sprawdza ręcznie odtworzony zestaw trzech cech w jednym pikselu każdego profilu oraz przejście długości geograficznej przez transformację w obie strony. Oba sprawdzenia przeszły dla bieżących danych.

Ograniczenia źródeł są jawne. MOLA uzupełnia biny bez bezpośrednich obserwacji interpolacją produktu; MEGC pokazuje ten udział i nie maskujemy go jako pomiaru bezpośredniego. Księżycowy profil dotyczy tylko 80–90°S, a nie całego południowego bieguna ani obszaru na północ od pokrycia LDEM. LDEC jest liczbą zwrotów, nie odsetkiem pokrytej powierzchni; posting 80 m nie oznacza efektywnej rozdzielczości 80 m. Cytowania źródeł i ograniczenia licencyjne są w `docs/DATA.md` i manifeście.

Braki w księżycowym profilu wynikają z geometrii i jawnych reguł wsparcia, a nie z braku danych w środku komórek analitycznych: 72 580/72 580 komórek 2 km ma ważną wartość źródłową po bramce jakości EFFRES. Przy krawędzi kafla część kołowych okien 10 km wychodzi poza raster; 480 okien ma wtedy mniej niż 90% ważnych próbek i nie dostarcza nierówności ani deniwelacji. Minimalne wsparcie okna wynosi 56,79%, P01 90,12%, a P05, P50 i P95 100%. Nachylenie nie wymaga całego okna 10 km, ale jego różnica centralna potrzebuje sąsiadów po obu stronach; ta sama krawędź pozbawia ich 96 komórek. Żadna wartość brakująca nie jest zastępowana zerem. Szczegóły są w sekcjach `grid_quality` i `feature_statistics` manifestu K-004. Dla Jezero 448/448 okien i komórek źródłowych są kompletne.

Wszystkie liczby powyżej są statystykami wybranych zmierzonych obszarów. Nie są jeszcze wynikiem rankingu Ziemi, walidacją podobieństwa ani twierdzeniem, że którykolwiek obszar jest jednoznacznym analogiem.

## 3. Trzy różne skale

| Skala | Znaczenie | Zasada |
|---|---|---|
| Efektywna rozdzielczość źródła | Najmniejsza rozpoznawalna struktura w pomiarze | Zagęszczenie rastra nie tworzy nowych obserwacji |
| Komórka analityczna i okno cechy | Obiekt rankingu oraz otoczenie potrzebne do obliczenia cechy | Stałe w danym wydaniu, zapisane w metadanych |
| Komórka wizualizacji | Zbiór wyników wyświetlany po oddaleniu mapy | Nigdy nie jest kandydatem zastępującym piksele |

Pierwotna propozycja P0 w D-007 używała regularnej siatki 60 arc-second, ale traktowała tę samą liczbę stopni długości jako podobną granulację na całej Ziemi. Pomiary K-042 wykazały, że pole komórki spada z 3,419 km² na równiku do 0,302 km² przy 85° i 0,030 km² przy 89,5°. Stałe 21 600 kolumn w każdym wierszu oznaczałoby zatem nadreprezentację obszarów polarnych w rankingu pikseli. D-007 zostało zastąpione rekomendacją fizycznej komórki około 2 km; pełna globalna siatka i jej własność komórek pozostają do sprawdzenia w K-008/K-044.

### Decyzja K-005 dla regionalnego pakietu Ziemi

Wersja K-005 używa osobnej, kwadratowej siatki lokalnego UTM o komórce 2 000 × 2 000 m. ETOPO 2022 15″ jest uśredniane powierzchniowo do tej siatki; efektywna skala wyjściowa pozostaje 2 km, choć źródłowy posting wynosi ok. 0,42–0,46 km w badanych szerokościach. Kandydatem jest każda komórka, której środek leży w jawnie podanym bbox AOI. Bufor 12 km służy tylko obliczeniu cech i nie poszerza zakresu kandydatów. `pixel_id` wiąże wersję AOI/siatki z wierszem i kolumną. Pole każdej komórki obliczamy jako powierzchnię ellipsoidalną poligonu jej czterech narożników po transformacji UTM → WGS84; 4 km² w UTM pozostaje powierzchnią nominalną.

### Rekomendacja globalnej siatki z pilota K-042

K-042 sprawdziło cztery kompletne rdzenie kafli 64 × 64 na rzeczywistym modelu NOAA ETOPO 2022 15″ Ice Surface i niezależnej masce GSHHG 2.3.7. Rekomendowany kandydat ma nominalnie 2 000 × 2 000 m, a nie stały krok kątowy. Na szerokościach poniżej 80° wybieramy lokalny UTM; od 80°N stosujemy UPS EPSG:3413, a od 80°S EPSG:3031. Rozmiar komórki w rzucie koryguje się lokalnym współczynnikiem skali, a pole każdej komórki zapisuje z elipsoidalnego pola jej narożników WGS84. Pilot zmierzył medianę pola 4,0003 km² na Hawajach, 3,9991 km² na 82°N i 3,9990 km² na 85°S. Przy 82°N współczynnik UPS wyniósł 0,97460; krok mapy 1 949 m odpowiadał około 2 000 m w terenie.

Rdzeń kafla obejmuje 64 × 64 = 4 096 odrębnych kandydatów (około 128 × 128 km). Siedem komórek kontekstu z każdej strony daje halo 14 km dla kołowego promienia cechy 10 km; halo nie dodaje kandydatów. Każda komórka rdzenia pozostaje w wyniku, także wykluczona z powodu wody, brakującego DEM lub niewystarczającego wsparcia. Źródłowe piksele oceanu są maskowane przez GSHHG przed uśrednianiem ETOPO do komórek; maska środka komórki jest niezależną kontrolą. W oknie 10 km potrzeba co najmniej 73 z 81 próbek (90%). Brak pomiaru zapisuje się jako null z powodem, a ujemna wysokość lądu pozostaje poprawnym pomiarem.

| Próbka | Kandydaci rdzenia | Ląd w środku | Kwalifikujące się | Kontrola |
|---|---:|---:|---:|---|
| Wybrzeże Big Island, UTM 5N | 4 096 | 2 449 | 1 861 | GSHHG odrzuca wodę przed agregacją; punkt oceanu ma prawidłową batymetrię ETOPO −792,71 m, ale nie staje się kandydatem lądowym |
| Depresja Qattara, UTM 35N | 4 096 | 4 096 | 4 096 | 2 424 lądowe komórki poniżej 0 m; minimum −128,45 m |
| Grenlandia 82°N, UPS północny | 4 096 | 4 046 | 3 859 | maska GSHHG i skala metryczna; terenowy punkt kontrolny ETOPO 945,62 m |
| Uziemiona Antarktyda 85°S, UPS południowy | 4 096 | 4 096 | 4 096 | maska GSHHG L6; dwa sąsiednie kafle źródłowe; brak braków DEM w rdzeniu |

Łącznie zachowano 16 384 kandydatów, z czego 13 912 spełniło warunki QA. Odtworzone ręcznie nachylenie, nierówność i deniwelacja w punkcie każdej próbki zgadzały się z pipeline'em. Próbka antimeridianu sprawdziła dane z kafli ETOPO po obu stronach 180° oraz geodezyjną odległość 2 226,39 m między 179,99°E i 179,99°W. To kontrola punktowa, nie pełny kafel rasteryzowany przez południk 180°.

Przetwarzanie czterech rdzeni trwało 66,93 s; szczytowy working set procesu wyniósł 447 012 864 B. Zapisane tabele CSV gzip zajęły 705 886 B (2 941 138 B bez kompresji). Są to wyniki lokalnego pilota, nie benchmark całego globu. Geometryczne oszacowanie referencyjne siatki około 2 km to 137 921 962 pozycje przy kroku 60″ północ–południe i około 2 km wschód–zachód; to nie jest wygenerowany ani zatwierdzony globalny grid. Liniowa ekstrapolacja pomiarów kafli daje około 5,7–8,0 dnia i 5,94 GB skompresowanego wyniku, lecz pomija m.in. globalne wybieranie geometrii GSHHG, harmonogram, indeksy, ponowienia i zmienność kompresji.

Odtwarzalny [manifest](../data/manifests/k042-global-grid-pilot.json) przypina wejścia i wyniki SHA-256; [raport](../data/reports/k042-global-grid-pilot.json) podaje środowisko, geometrię, QA, czas, pamięć i ekstrapolację. Surowe rastry i checkpointy nie są śledzone w Git. Pilot nie dowodzi pełnego pokrycia, spójnej własności sąsiednich komórek między strefami UTM/UPS, ciągłości przez antimeridian, globalnego rankingu ani dokładności rozdzielczości DEM. K-008 musi ustalić globalne ID, pojedynczą własność każdej komórki, mozaikę źródłową, pokrycie, brak szczelin i duplikatów oraz prawdziwy koszt pełnego skanu; konkretny test granic siatki jest przekazany w K-044.

Maska GSHHG jest niezależna od wysokości i stosowana już na natywnej siatce źródłowego ETOPO 15″ przed uśrednieniem do 2 km; wartości batymetrii nie mogą domieszać się do lądowej wysokości komórki wybrzeża. Komórka kandydująca jest lądowa według punktu środkowego; `land_fraction_4x` dodatkowo zapisuje przybliżony udział 16 podkomórek. Okno 10 km zawiera 81 środków komórek; dla nierówności i deniwelacji wymagamy co najmniej 73 ważnych pomiarów lądu, a nachylenie wymaga kompletnego sąsiedztwa 3 × 3. Brak lub woda zmniejszają udziały QA, nie wypełniają pomiaru zerem. Zmiana metody maskowania źródła podnosi `model_version` i `grid_version` do v2.

Na DEM obliczamy pola cech na wspólnej skali fizycznej i zapisujemy wartość dla **każdego piksela**. Nie uśredniamy potem cech wielu pikseli do większego heksagonu lub regionu przed scoringiem. Koszyki mapowe oraz opcjonalny indeks przestrzenny służą wyłącznie do wyświetlania i przyspieszania odczytu. Profil planetarny powstaje z próbek o porównywalnym wsparciu przestrzennym, w układzie właściwego ciała. Jeśli źródło lub cecha wymaga większego okna, nowa skala musi zostać jawnie zarejestrowana; nie mieszamy jej bez walidacji z poprzednią wersją.

Okno potrzebne do wyznaczenia nierówności jest częścią definicji tej cechy, a nie średnią wyników rankingu. Dobry piksel może zatem oznaczać dopasowanie lokalnego otoczenia o zadanym promieniu. UI pokazuje to obok wielkości komórki; nie sugeruje niezależnego pomiaru wyłącznie wewnątrz małego piksela.

## 4. Cechy P0

- `slope_deg`: lokalny kąt nachylenia w pikselu; gradient liczony po wygładzeniu / przeskalowaniu DEM do wspólnej efektywnej skali, z odległościami w metrach.
- `roughness_m`: odchylenie standardowe reszt wysokości po odjęciu lokalnej płaszczyzny w oknie fizycznym.
- `relief_m`: różnica P95 i P05 wysokości w tym samym oknie, odporna na pojedynczy ekstremalny pomiar.

Nie porównujemy wysokości nad ziemskim geoidem z wysokością nad marsjańskim areoidem ani promieniem Księżyca. Powyższe cechy są względne, lecz nadal zależą od skali. DEM lodowej powierzchni i DEM podłoża to różne wielkości. P0 opisuje powierzchnię dostępną do testów, a nie ukryte podłoże.

Wiele cech jednego DEM nie stanowi niezależnych dowodów zgodności. P0 jest modelem topograficznym. Przed dodaniem dziedzin środowiskowych wprowadzamy grupy wag, aby trzy podobne cechy terenu nie zdominowały jednej warstwy temperatury.

## 5. Wynik pojedynczej warstwy

Dla wartości `x`, przedziału referencyjnego `[a, b]` i dodatniej tolerancji `t`:

```text
d = max(a - x, 0, x - b)
s(x) = max(0, 1 - d / t)
```

`s` należy do [0,1]. Wynik jest równy 1 wewnątrz przedziału i maleje liniowo do 0 poza nim. Przedział może wynikać z kwartylów porównywalnych próbek regionu referencyjnego. Tolerancja musi mieć uzasadnienie fizyczne / pomiarowe lub być jawnym założeniem eksperymentalnym. Zapisujemy jej pochodzenie, nie dopasowujemy jej tak, by znany analog automatycznie wygrał.

Warstwy kategoryczne wymagają osobnej, udokumentowanej macierzy zgodności. Nie odejmujemy kodów klas minerałów od siebie. Nowy typ funkcji wymaga wersji modelu i testów.

## 6. MCDA

Dla aktywnego zestawu `A` i wag `w_i > 0`:

```text
alpha_i = w_i / sum(w_j for j in A)
score_pct(p) = 100 * sum(alpha_i * s_i(p) for i in A)
contribution_pct_i(p) = 100 * alpha_i * s_i(p)
```

Składniki sumują się do wyniku. Jedna warstwa daje dokładnie jej wynik. Wagi zerowe wyłączają kryterium; ujemne, niefinitywne i pusta suma są błędem. Wynik liczymy z pełną precyzją; zaokrąglenie tylko przy wyświetleniu.

To model kompensacyjny: dobry wynik w jednej cesze może równoważyć słaby w drugiej. UI pokazuje rozbicie. Ewentualne nieprzekraczalne progi terenowe są osobnymi filtrami, nie ukrytymi wagami. 100% oznacza dopasowanie do przyjętych przedziałów wybranych cech, a nie identyczność środowiska lub pewność naukową.

## 7. Braki i jakość

Domyślnie kwalifikuje się tylko komórka z ważnymi danymi dla **każdej aktywnej cechy**. Wymagany udział ważnych próbek w komórce i oknie startowo 90%; to próg operacyjny podlegający kontroli w G1. W razie braku danych `score_pct = null`, z listą braków i przyczyną. Nie przeliczamy automatycznie wag osobno dla każdego piksela.

`coverage_fraction` = suma wag cech z ważnym pomiarem / suma wag aktywnych. Jest to kompletność, nie prawdopodobieństwo poprawnego wyniku. Jakość obejmuje również źródło, maskę, efektywną rozdzielczość, udział interpolacji oraz diagnostykę artefaktów. Wynik, kompletność i jakość to odrębne pola.

Maska lądu jest niezależna od wysokości: depresje poniżej poziomu morza pozostają lądem. Strefy polarne, małe wyspy i wybrzeża trafiają do raportu kwalifikowalności; brak pokrycia nie może zniknąć z mianownika raportu.

## 8. Dokładny globalny Top 10 pikseli

1. Zamroź wersję danych i konfigurację. Ustal wszystkie komórki w deklarowanym globalnym uniwersum.
2. W partiach oblicz wynik **każdej** komórki spełniającej te same reguły QA; zachowuj liczności odrzuceń.
3. Utrzymuj globalne Top K, porządkując po niezaokrąglonym wyniku malejąco, potem `pixel_id` rosnąco przy remisie.
4. Zwróć do 10 wyników, faktyczny rozmiar komórek, obrysy, wkłady cech i liczbę przebadanych komórek. Mniej niż 10 ważnych wyników oznacza krótszą listę.
5. Sąsiedztwo nie usuwa wyniku. Dziesięć dobrych pikseli w jednym kraterze może zająć wszystkie pozycje.

Przeszukiwanie tylko regionów o najlepszej średniej jest niedopuszczalne. Jeśli optymalizujemy przez bloki, odcięcie wymaga **udowodnionej górnej granicy** wyniku dla aktualnych wag; P0 stosuje pełny skan. Suma maksimów poszczególnych cech może być górną granicą bloku, ale nie jest wynikiem rzeczywistego piksela — maksima mogły wypaść w różnych miejscach.

## 9. Mapa, która nie chowa hotspotu

Agregacja następuje po obliczeniu wszystkich wyników dla aktualnych wag. Komórka mapy przechowuje `max_score_pct`, `mean_score_pct`, `max_pixel_id`, liczbę ważnych i wszystkich pikseli. Domyślny kolor odpowiada maksimum. Tooltip wyjaśnia, że to najlepszy piksel w koszyku, nie jednorodny wynik całego obszaru.

Nie wolno składać nowego wyniku z osobnych map maksymalnych warstw. Dla dwóch różnych pikseli — jeden dobry w A, drugi w B — taka operacja stworzyłaby nieistniejące idealne dopasowanie.

Przy powiększeniu pobieramy właściwe komórki i geometrie, a Top 10 zawsze ma własne markery. Pojedynczy hotspot może zostać oznaczony jako izolowany; sprawdzamy QA, sąsiednie pomiary i źródło. Nie wygładzamy go i nie usuwamy tylko z powodu izolacji.

## 10. Oddzielny ranking obszarów

Tryb `distinct_areas` wybiera najlepszy piksel, następnie kolejne najlepsze co najmniej `min_distance_km` od już wybranych reprezentantów. Proponowana wartość startowa: 25 km, jawnie edytowalna. Dystans jest geodezyjny na Ziemi, nie liczony w stopniach. Reprezentant ma wynik najlepszego piksela, nie średnią obszaru. UI mówi, że to heurystyka różnorodności przestrzennej.

Algorytm musi przeglądać dalszych kandydatów aż do 10 reprezentantów albo wyczerpania zbioru — nie wystarczy pogrupować wyłącznie pierwszych 10 pikseli. Granice grup nie są administracyjnymi granicami regionów.

## 11. Rozdzielczość, stabilność i kontrola wyniku

- Porównujemy co najmniej dwa poziomy siatki na tym samym obszarze, wskazując jak zmienia się Top 10. Najpierw liczymy drobne wyniki, później ich średnie i maksima do raportu.
- Top 10 fine oraz coarse pozostają osobnymi wynikami. Wysokiej rozdzielczości analiza wybranych AOI nie jest globalnym rankingiem fine.
- Walidacja obejmuje izolowany dobry piksel w słabym regionie, remisy, brak danych, bieguny i południk 180°.
- Analiza wrażliwości: zmiana wag ±20%, tolerancji i reguł QA; pokazujemy czy zwycięzca jest stabilny. Nie nazywamy takiej stabilności przedziałem ufności.
- Benchmarki analogów służą do sprawdzenia sensowności w odpowiednim wymiarze, nie do gwarantowania im pierwszych miejsc.

Przypadki syntetyczne do testów: [hotspot-regression.json](../contracts/fixtures/hotspot-regression.json). Pozostałe kryteria odbioru: [VALIDATION](VALIDATION.md).
