# Metoda podobieństwa i granulacja

Status: specyfikacja projektowa v0.1 do walidacji w K-004 i K-009. Progi i parametry startowe poniżej są naszymi decyzjami inżynierskimi, nie ustaleniami NASA.

## 1. Co porównujemy

Konfiguracja = ciało niebieskie + konkretny region referencyjny + wersja profilu + wybrane cechy + dodatnie wagi + wersja siatki/danych + tryb wyników. „Mars” bez profilu regionalnego nie definiuje jednego zestawu warunków.

Profil zawiera geometrię regionu we współrzędnych właściwego ciała, statystyki zmierzonych cech, datę/wersję źródła, jednostki, definicję skali i uzasadnienie tolerancji. Nie wpisujemy teraz fikcyjnych wartości dla Jezero ani południowego bieguna Księżyca.

## 2. Trzy różne skale

| Skala | Znaczenie | Zasada |
|---|---|---|
| Efektywna rozdzielczość źródła | Najmniejsza rozpoznawalna struktura w pomiarze | Zagęszczenie rastra nie tworzy nowych obserwacji |
| Komórka analityczna i okno cechy | Obiekt rankingu oraz otoczenie potrzebne do obliczenia cechy | Stałe w danym wydaniu, zapisane w metadanych |
| Komórka wizualizacji | Zbiór wyników wyświetlany po oddaleniu mapy | Nigdy nie jest kandydatem zastępującym piksele |

Propozycja P0: każdy ważny piksel ziemskiego rastra 60 arc-second jest osobnym kandydatem; ID zawiera wersję siatki, wiersz i kolumnę. Nominalna odległość północ–południe to ok. 1,85 km, a szerokość i powierzchnia zależą od szerokości geograficznej. Zapisujemy `pixel_area_km2`, granice i faktyczne wsparcie pomiaru. Proponowana wspólna efektywna skala DEM to ok. 2 km, a promień okna cech lokalnych 10 km. Konkretne wartości zamraża G1 po pomiarze danych i kosztów.

Na DEM obliczamy pola cech na wspólnej skali fizycznej i zapisujemy wartość dla **każdego piksela**. Nie uśredniamy potem cech wielu pikseli do większego heksagonu lub regionu przed scoringiem. Koszyki mapowe oraz opcjonalny indeks przestrzenny służą wyłącznie do wyświetlania i przyspieszania odczytu. Profil planetarny powstaje z próbek o porównywalnym wsparciu przestrzennym, w układzie właściwego ciała. Jeśli źródło lub cecha wymaga większego okna, nowa skala musi zostać jawnie zarejestrowana; nie mieszamy jej bez walidacji z poprzednią wersją.

Okno potrzebne do wyznaczenia nierówności jest częścią definicji tej cechy, a nie średnią wyników rankingu. Dobry piksel może zatem oznaczać dopasowanie lokalnego otoczenia o zadanym promieniu. UI pokazuje to obok wielkości komórki; nie sugeruje niezależnego pomiaru wyłącznie wewnątrz małego piksela.

## 3. Cechy P0

- `slope_deg`: lokalny kąt nachylenia w pikselu; gradient liczony po wygładzeniu / przeskalowaniu DEM do wspólnej efektywnej skali, z odległościami w metrach.
- `roughness_m`: odchylenie standardowe reszt wysokości po odjęciu lokalnej płaszczyzny w oknie fizycznym.
- `relief_m`: różnica P95 i P05 wysokości w tym samym oknie, odporna na pojedynczy ekstremalny pomiar.

Nie porównujemy wysokości nad ziemskim geoidem z wysokością nad marsjańskim areoidem ani promieniem Księżyca. Powyższe cechy są względne, lecz nadal zależą od skali. DEM lodowej powierzchni i DEM podłoża to różne wielkości. P0 opisuje powierzchnię dostępną do testów, a nie ukryte podłoże.

Wiele cech jednego DEM nie stanowi niezależnych dowodów zgodności. P0 jest modelem topograficznym. Przed dodaniem dziedzin środowiskowych wprowadzamy grupy wag, aby trzy podobne cechy terenu nie zdominowały jednej warstwy temperatury.

## 4. Wynik pojedynczej warstwy

Dla wartości `x`, przedziału referencyjnego `[a, b]` i dodatniej tolerancji `t`:

```text
d = max(a - x, 0, x - b)
s(x) = max(0, 1 - d / t)
```

`s` należy do [0,1]. Wynik jest równy 1 wewnątrz przedziału i maleje liniowo do 0 poza nim. Przedział może wynikać z kwartylów porównywalnych próbek regionu referencyjnego. Tolerancja musi mieć uzasadnienie fizyczne / pomiarowe lub być jawnym założeniem eksperymentalnym. Zapisujemy jej pochodzenie, nie dopasowujemy jej tak, by znany analog automatycznie wygrał.

Warstwy kategoryczne wymagają osobnej, udokumentowanej macierzy zgodności. Nie odejmujemy kodów klas minerałów od siebie. Nowy typ funkcji wymaga wersji modelu i testów.

## 5. MCDA

Dla aktywnego zestawu `A` i wag `w_i > 0`:

```text
alpha_i = w_i / sum(w_j for j in A)
score_pct(p) = 100 * sum(alpha_i * s_i(p) for i in A)
contribution_pct_i(p) = 100 * alpha_i * s_i(p)
```

Składniki sumują się do wyniku. Jedna warstwa daje dokładnie jej wynik. Wagi zerowe wyłączają kryterium; ujemne, niefinitywne i pusta suma są błędem. Wynik liczymy z pełną precyzją; zaokrąglenie tylko przy wyświetleniu.

To model kompensacyjny: dobry wynik w jednej cesze może równoważyć słaby w drugiej. UI pokazuje rozbicie. Ewentualne nieprzekraczalne progi terenowe są osobnymi filtrami, nie ukrytymi wagami. 100% oznacza dopasowanie do przyjętych przedziałów wybranych cech, a nie identyczność środowiska lub pewność naukową.

## 6. Braki i jakość

Domyślnie kwalifikuje się tylko komórka z ważnymi danymi dla **każdej aktywnej cechy**. Wymagany udział ważnych próbek w komórce i oknie startowo 90%; to próg operacyjny podlegający kontroli w G1. W razie braku danych `score_pct = null`, z listą braków i przyczyną. Nie przeliczamy automatycznie wag osobno dla każdego piksela.

`coverage_fraction` = suma wag cech z ważnym pomiarem / suma wag aktywnych. Jest to kompletność, nie prawdopodobieństwo poprawnego wyniku. Jakość obejmuje również źródło, maskę, efektywną rozdzielczość, udział interpolacji oraz diagnostykę artefaktów. Wynik, kompletność i jakość to odrębne pola.

Maska lądu jest niezależna od wysokości: depresje poniżej poziomu morza pozostają lądem. Strefy polarne, małe wyspy i wybrzeża trafiają do raportu kwalifikowalności; brak pokrycia nie może zniknąć z mianownika raportu.

## 7. Dokładny globalny Top 10 pikseli

1. Zamroź wersję danych i konfigurację. Ustal wszystkie komórki w deklarowanym globalnym uniwersum.
2. W partiach oblicz wynik **każdej** komórki spełniającej te same reguły QA; zachowuj liczności odrzuceń.
3. Utrzymuj globalne Top K, porządkując po niezaokrąglonym wyniku malejąco, potem `pixel_id` rosnąco przy remisie.
4. Zwróć do 10 wyników, faktyczny rozmiar komórek, obrysy, wkłady cech i liczbę przebadanych komórek. Mniej niż 10 ważnych wyników oznacza krótszą listę.
5. Sąsiedztwo nie usuwa wyniku. Dziesięć dobrych pikseli w jednym kraterze może zająć wszystkie pozycje.

Przeszukiwanie tylko regionów o najlepszej średniej jest niedopuszczalne. Jeśli optymalizujemy przez bloki, odcięcie wymaga **udowodnionej górnej granicy** wyniku dla aktualnych wag; P0 stosuje pełny skan. Suma maksimów poszczególnych cech może być górną granicą bloku, ale nie jest wynikiem rzeczywistego piksela — maksima mogły wypaść w różnych miejscach.

## 8. Mapa, która nie chowa hotspotu

Agregacja następuje po obliczeniu wszystkich wyników dla aktualnych wag. Komórka mapy przechowuje `max_score_pct`, `mean_score_pct`, `max_pixel_id`, liczbę ważnych i wszystkich pikseli. Domyślny kolor odpowiada maksimum. Tooltip wyjaśnia, że to najlepszy piksel w koszyku, nie jednorodny wynik całego obszaru.

Nie wolno składać nowego wyniku z osobnych map maksymalnych warstw. Dla dwóch różnych pikseli — jeden dobry w A, drugi w B — taka operacja stworzyłaby nieistniejące idealne dopasowanie.

Przy powiększeniu pobieramy właściwe komórki i geometrie, a Top 10 zawsze ma własne markery. Pojedynczy hotspot może zostać oznaczony jako izolowany; sprawdzamy QA, sąsiednie pomiary i źródło. Nie wygładzamy go i nie usuwamy tylko z powodu izolacji.

## 9. Oddzielny ranking obszarów

Tryb `distinct_areas` wybiera najlepszy piksel, następnie kolejne najlepsze co najmniej `min_distance_km` od już wybranych reprezentantów. Proponowana wartość startowa: 25 km, jawnie edytowalna. Dystans jest geodezyjny na Ziemi, nie liczony w stopniach. Reprezentant ma wynik najlepszego piksela, nie średnią obszaru. UI mówi, że to heurystyka różnorodności przestrzennej.

Algorytm musi przeglądać dalszych kandydatów aż do 10 reprezentantów albo wyczerpania zbioru — nie wystarczy pogrupować wyłącznie pierwszych 10 pikseli. Granice grup nie są administracyjnymi granicami regionów.

## 10. Rozdzielczość, stabilność i kontrola wyniku

- Porównujemy co najmniej dwa poziomy siatki na tym samym obszarze, wskazując jak zmienia się Top 10. Najpierw liczymy drobne wyniki, później ich średnie i maksima do raportu.
- Top 10 fine oraz coarse pozostają osobnymi wynikami. Wysokiej rozdzielczości analiza wybranych AOI nie jest globalnym rankingiem fine.
- Walidacja obejmuje izolowany dobry piksel w słabym regionie, remisy, brak danych, bieguny i południk 180°.
- Analiza wrażliwości: zmiana wag ±20%, tolerancji i reguł QA; pokazujemy czy zwycięzca jest stabilny. Nie nazywamy takiej stabilności przedziałem ufności.
- Benchmarki analogów służą do sprawdzenia sensowności w odpowiednim wymiarze, nie do gwarantowania im pierwszych miejsc.

Przypadki syntetyczne do testów: [hotspot-regression.json](../contracts/fixtures/hotspot-regression.json). Pozostałe kryteria odbioru: [VALIDATION](VALIDATION.md).
