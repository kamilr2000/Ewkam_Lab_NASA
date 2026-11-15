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

Propozycja P0: każdy ważny piksel ziemskiego rastra 60 arc-second jest osobnym kandydatem; ID zawiera wersję siatki, wiersz i kolumnę. Nominalna odległość północ–południe to ok. 1,85 km, a szerokość i powierzchnia zależą od szerokości geograficznej. Zapisujemy `pixel_area_km2`, granice i faktyczne wsparcie pomiaru. Proponowana wspólna efektywna skala DEM to ok. 2 km, a promień okna cech lokalnych 10 km. Konkretne wartości zamraża G1 po pomiarze danych i kosztów.

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
