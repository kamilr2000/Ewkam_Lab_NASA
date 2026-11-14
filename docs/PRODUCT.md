# Produkt i zakres

## Pytanie użytkownika

„Gdzie na Ziemi znajdę teren najbardziej zbliżony do wybranego regionu Marsa lub Księżyca, biorąc pod uwagę wskazane przeze mnie właściwości?”

Odbiorcy: osoby szukające terenów do testów łazików, instrumentów i procedur, edukatorzy oraz uczestnicy badań analogowych. Aplikacja służy do screeningu kandydatów do dalszej weryfikacji.

## Przepływ MVP

1. Wybierz **Mars / Moon** i konkretny profil referencyjny. Start: region Jezero oraz region południowego bieguna Księżyca; granice i wartości wyznacza K-004 z danych.
2. Włącz od jednej do wszystkich dostępnych dla profilu warstw. Wybierz jedną warstwę, aby uzyskać wynik wyłącznie dla niej.
3. Ustaw dodatnie wagi lub pozostaw równe. Widoczność warstwy na mapie jest osobnym ustawieniem od uwzględnienia jej w obliczeniach.
4. Uruchom analizę globalną. Backend ocenia wszystkie kwalifikujące się komórki w aktualnej wersji siatki, niezależnie od widoku mapy.
5. Zobacz mapę i **Top 10 pixels**. Wyniki mogą sąsiadować. Kliknięcie powiększa mapę do konkretnej komórki i pokazuje jej rzeczywisty obrys.
6. Otwórz wyjaśnienie: wynik każdej warstwy, wkład w sumę, pomiar, jednostka, zakres referencyjny, jakość, źródło i ograniczenia analogii.
7. Opcjonalnie przełącz na **Distinct areas** z jawnym promieniem grupowania; oryginalny ranking nadal jest dostępny.
8. Skopiuj konfigurację / pobierz wynik, aby odtworzyć analizę.

## Warstwy proponowane przez nas

| Warstwa | Wersja | Znaczenie i warunek uruchomienia |
|---|---|---|
| Nachylenie powierzchni | P0 | Kąt ze wspólnie przeskalowanego DEM, dystanse w metrach |
| Lokalna nierówność | P0 | Odchylenie wysokości po odjęciu lokalnej płaszczyzny; stałe okno w km |
| Lokalna deniwelacja | P0 | P95–P05 wysokości w takim samym oknie; informuje o rzeźbie |
| Roślinność / odsłonięcie gruntu | P1 | NASA MODIS NDVI z QA; ziemski filtr/proxy warunków testowych, bez fikcyjnego planetarnego NDVI |
| Temperatura powierzchni i amplituda | P1 | Porównywalne statystyki LST / Diviner / danych Marsa; nie mieszać temperatury powietrza i gruntu |
| Litologia / mineralogia | P1, ważne rozszerzenie | Najpierw mały dowód porównywalności na wspólnej ontologii; pokrycie może być regionalne |
| Suchość, lód, pył, jaskinie | P2 | Osobne źródła, skale i profile procesów; nie włączać pustych warstw do wyniku |

Trzy warstwy P0 opisują **jedną dziedzinę: topografię** i są ze sobą powiązane. UI oraz prezentacja muszą to mówić. Nie przedstawiamy ich jako pełnego porównania środowiska. Po ukończeniu P0 następny priorytet to dziedzina o niezależnej informacji, wybrana na podstawie audytu danych.

## Granulacja jako wymaganie produktu

Piksel = najmniejsza komórka aktualnej **siatki analitycznej**; nie piksel ekranu, zdjęcia ani dowolnie dokładny punkt. Startowa propozycja to piksele rastra ETOPO 60 arc-second, ok. 1,85 km w kierunku północ–południe; szerokość wschód–zachód i powierzchnia maleją z szerokością geograficzną. Siatka i fizyczna skala porównania zostają zatwierdzone po benchmarku G1. Nie łączymy najpierw wielu takich pikseli w większy kandydat rankingowy.

Światowy zasięg nie oznacza, że rozpoznajemy każdy mały obiekt. Aplikacja pokazuje wersję siatki, powierzchnię konkretnej komórki i efektywną rozdzielczość źródła. Nie wykryjemy hotspotu mniejszego niż wspierana skala pomiaru. Zwiększenie zoomu nie zwiększa dokładności danych. Jeżeli ograniczenia wymuszą grubszy raster, wydanie jawnie podaje utraconą szczegółowość; nie obiecuje zachowania hotspotów drobniejszej siatki.

## Kryteria gotowego MVP

- Oba ciała niebieskie mają co najmniej jeden realny, udokumentowany profil.
- Działa wybór 1–3 cech, wagi, mapa, oba widoki wyników, wyjaśnienia i eksport.
- Top 10 jest dokładne **w obrębie opublikowanej siatki i kwalifikujących się danych**, również dla jednego dobrego piksela w słabym regionie.
- Wyszukiwanie obejmuje globalny zbiór, z jawną maską i raportem pokrycia wszystkich kontynentów oraz obszarów polarnych. Braki są widoczne, nie interpolowane dla lepszego wyglądu.
- NASA dane Ziemi i planet mają rzeczywistą rolę opisaną w wynikach / walidacji, a nie tylko link na stronie.
- Publiczne materiały po angielsku, zgodność źródeł, testy i demo według przewodnika zgłoszenia.

## Świadomie poza P0

Konta i płatności, dowolne profile definiowane przez użytkownika, trening ML, fotorealistyczny glob 3D, pełne archiwum surowych obrazów online, globalna mineralogia wysokiej rozdzielczości oraz rekomendowanie realnych miejsc budowy baz. P1 może wejść dopiero bez ryzyka dla działającego P0.
