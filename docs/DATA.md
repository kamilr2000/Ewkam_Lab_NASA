# Dane, warstwy i profile

Stan 2026-11-14: K-002 pobrał i poprawnie odczytał próbki ETOPO, LOLA i MOLA. K-017 dodał cztery rzeczywiste kafle NASADEM HGT/NUM/SWB oraz niezależny produkt GSHHG 2.3.7; rozmiary i SHA-256 zapisano w `data/manifests/k017-earth-validation.json`. Trzy nakładające się AOI porównano z ETOPO na siatce 2 km po transformacji NASADEM z EGM96 do EGM2008. Wynik jest walidacją wybranych próbek, nie dowodem globalnej dokładności ani gotową globalną warstwą aplikacji. Surowe pliki pozostają w ignorowanym `data/raw/`.

## 1. Kolejność pozyskiwania

1. Mały fragment każdego ciała → poprawny odczyt jednostek, CRS i maski.
2. Realne profile planetarne oraz mały ziemski wycinek → pierwszy przepływ API–UI.
3. Globalne cechy Ziemi w partiach → raport pokrycia.
4. Niezależny sprawdzian wybranych wycinków na NASA Earth DEM.
5. Dopiero potem dodatkowa dziedzina danych.

## 2. Produkty P0 i kontrola NASA Earth

| ID | Źródło i rola | Ograniczenie / działanie |
|---|---|---|
| D01 | [NOAA ETOPO 2022](https://www.ncei.noaa.gov/products/etopo-global-relief-model): globalna rzeźba powierzchni Ziemi | Rozważyć wariant Ice Surface 60 arc-second dla screeningu; angularny piksel nie ma stałego rozmiaru w metrach. Nie używać Bedrock jako terenu po powierzchni lodu. |
| D02 | [NASA/METI ASTER GDEM v3](https://asterweb.jpl.nasa.gov/gdem.asp) lub NASADEM: kontrola ziemskich cech na drugim produkcie DEM | NASADEM HGT v001 (DOI 10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001, CC0-1.0) pobrano dla Atacamy, Hawajów, Himalajów i testu Qattary. Trzy AOI porównano z ETOPO po wspólnej siatce i transformacji EGM96→EGM2008. `NUM` zachowuje pochodzenie komórek. `SWB` opisuje ląd/wodę tylko w zasięgu SRTM i nie obejmuje biegunów. Wyników z trzech AOI nie uogólniamy na cały glob. |
| D03 | [LRO LOLA w NASA PDS](https://pds-geosciences.wustl.edu/missions/lro/lola.htm): profil Księżyca; pobrano LDEM_4 i etykiety PDS3/PDS4 | Globalny produkt 4 piksele/stopień przechowuje promień względem sfery odniesienia (DN × 0,5 m + 1 737 400 m); topografia względem geoidy wymaga odjęcia promienia geoidy. Nie porównywać surowych wysokości między ciałami. |
| D04 | [MGS MOLA MEGDR / Topography Derived](https://pds-geosciences.wustl.edu/missions/mgs/megdr.html): profil Marsa; pobrano globalny MEGT 4 px/deg oraz MEGC | Używaj utrzymywanego bundle PDS4 z 2026 r. MEGT jest topografią względem areoidy MOLA GMM-3; MEGC zawiera liczbę obserwacji. Produkt interpoluje nieobserwowane komórki — zachowuj MEGC i oznaczaj zerową liczbę obserwacji jako brak bezpośredniego pomiaru. |
| D05 | [GSHHG 2.3.7](https://www.soest.hawaii.edu/wessel/gshhg/): wybrana globalna maska lądu, wysp, jezior i uziemionej Antarktydy | Pobrano pełną rozdzielczość, WGS84, LGPL-3.0-or-later. Maska nie zależy od wysokości DEM: L1/L3 oznaczają ląd, L2/L4 wodę, L5 pomijamy, a L6 wybieramy dla uziemionej Antarktydy. Szczegóły i sumy są w manifeście K-017. |

D01 jest produktem NOAA, nie NASA ani agencji partnerskiej Space Apps. NASADEM wnosi rzeczywisty produkt NASA Earth do kontroli ziemskich pomiarów i maski w zasięgu SRTM. D03/D04 są rzeczywistymi produktami NASA PDS dla profili planetarnych. Żadne z tych użyć nie oznacza poparcia projektu przez NASA.

### Dowody porównania K-017

Odtworzenie: `python pipeline/download_k017_assets.py`, następnie `python pipeline/compare_nasadem_etopo.py`. Szczegółowe sumy, histogramy klas `NUM`, wersje bibliotek i metryki zapisuje `data/reports/k017-validation.json`.

| AOI | Kwalifikujące się wspólne komórki lądu | Zgodność GSHHG/SWB | MAE wysokości po transformacji | MAE nachylenia | MAE nierówności | MAE deniwelacji |
|---|---:|---:|---:|---:|---:|---:|
| Atacama / Andes | 1 793 | 1 793/1 796; 3 różnice | 3,64 m | 0,077° | 2,44 m | 6,72 m |
| Hawaii, Big Island | 1 703 | 1 853/1 854; 1 różnica | 5,24 m | 0,062° | 1,26 m | 6,68 m |
| Himalaya | 1 731 | 1 731/1 737; 6 różnic | 7,43 m | 0,164° | 4,92 m | 14,12 m |

Siatka ma komórkę 2 000 m w lokalnym UTM. `slope_deg` liczono po gradientach w metrach; `roughness_m` to odchylenie reszt od lokalnej płaszczyzny; `relief_m` to P95−P05. Dwie ostatnie cechy używają kołowego promienia 10 km i wymagają co najmniej 70% ważnych próbek. Dla każdej cechy oba DEM-y używają tych samych komórek GSHHG land ∩ NASADEM SWB land ∩ ważne wysokości. MAE opisuje różnicę produktów w tych AOI, nie niepewność ani błąd globalny. Różnice masek: 10 z 5 387 komórek (99,81% zgodności w ocenionych AOI); GSHHG pozostaje maską wybraną, a rozbieżności SWB są jawnie raportowane.

NASADEM ma 3 601 × 3 601 próbek na kafel, HGT to big-endian int16 w metrach względem geoidy EGM96, NUM i SWB to bajty. Przewodnik NASADEM nie deklaruje fill/no-data dla tych trzech warstw; kontrola czterech kafli nie znalazła HGT poza zakresem −32 767…32 767 ani nieznanych klas SWB/NUM. NUM zachowujemy, bo kafel może łączyć SRTM, PRISM, GDEM, inne źródła i interpolację.

Wysokości NASADEM przeliczono do EGM2008 za pomocą operacji PROJ z lokalnymi siatkami NGA `us_nga_egm96_15.tif` i `us_nga_egm08_25.tif`; ETOPO już opisuje EGM2008. Dokładną definicję, deklarowaną przez PROJ dokładność operacji 1,113 m oraz sumy siatek podaje manifest. Ta wartość jest metadanymi transformacji, nie wynikiem empirycznej walidacji.

Kontrola maski przeszła cztery przypadki: punkt lądu Big Island (SWB land), ocean na zachód od wyspy (SWB water), Qattara jako ląd przy NASADEM HGT −80 m względem EGM96 oraz punkt uziemionej Antarktydy jako L6. GSHHG został pobrany i użyty lokalnie; kod umożliwia rasteryzację wybranego obszaru. K-017 nie buduje pełnego globalnego rastra maski. NASADEM/SWB nie pokrywa obszarów polarnych, a małe wyspy mogą być nierozpoznawalne po przejściu na komórki analityczne 2 km.

### Regionalne komórki K-005

Odtworzenie: `uv run --locked --group data python pipeline/download_k005_sources.py`, następnie `uv run --locked --group data python pipeline/build_k005_earth_grid.py`. Pobieranie potrzebuje tylko publicznych plików NOAA ETOPO 2022 v1 15″ i GSHHG 2.3.7; nie wymaga Earthdata tokenu. Surowe wejścia i checkpointy pozostają lokalnie w ignorowanych `data/raw/` i `data/processed/`. Trzy małe CSV gzip z komórkami są śledzone w `data/derived/k005-earth-grid/`; ich SHA-256 są zapisane w wersjonowanych manifestach, a zbiorczy raport w `data/reports/k005-earth-grid.json`.

Każdy wiersz CSV jest pojedynczą komórką analityczną: stabilny ID wersji/wiersza/kolumny, środek WGS84, ellipsoidalne pole komórki z narożników UTM, udział maski lądu z 16 próbek, trzy cechy, udziały ważnych próbek i jawna przyczyna wykluczenia. Komórki wybieramy regułą środka w bbox; bufor metryczny nie dodaje kandydatów. GSHHG usuwa próbki oceaniczne ETOPO na natywnej siatce 15″ przed uśrednianiem lądowych wysokości do 2 km w lokalnym UTM; docelowa maska lądu pozostaje niezależną kontrolą. Nachylenie wymaga 9/9 ważnych sąsiadów; nierówność i deniwelacja wymagają co najmniej 73/81 ważnych próbek lądu w kołowym oknie 10 km. Brak DEM pozostaje pustym polem, nigdy zerem. W Atacamie i Himalajach środki kandydatów miały ważną wysokość; na Big Island 134 z 1 854 środków nie miały żadnej lądowej próbki źródłowej, a 151 środków odrzucono jako wodne według docelowej maski.

| AOI i bbox [W, S, E, N] | Komórki | Środek lądu | Kwalifikujące się | Wykluczenia | Mediana nachylenia | Mediana nierówności | Mediana deniwelacji |
|---|---:|---:|---:|---|---:|---:|---:|
| Atacama / Andes `[-68.9, -24.9, -68.1, -24.1]` | 1 796 | 1 796 | 1 791 | 5: za mało próbek w oknie | 3,40° | 161,68 m | 858,89 m |
| Hawaii, Big Island `[-155.9, 19.1, -155.1, 19.9]` | 1 854 | 1 703 | 1 497 | 151: woda; 62: sąsiedztwo nachylenia; 144: okno cechy | 4,63° | 118,99 m | 1 311,74 m |
| Himalaya `[86.1, 28.1, 86.9, 28.9]` | 1 737 | 1 737 | 1 737 | 0 | 4,58° | 197,48 m | 913,72 m |

To są rozkłady pomiarów topografii na trzech regionalnych wycinkach, nie podobieństwa do Jezero ani południowego bieguna Księżyca i nie ranking analogów. ETOPO 15″ ma nominalny posting ok. 0,42–0,46 km w tych szerokościach; resampling nie oznacza, że źródło rozpoznaje obiekty 2-kilometrowe równie dokładnie wszędzie. Komórki wodne nie są kandydatami; próbki batymetryczne są wykluczane z uśredniania już na źródłowej siatce GSHHG/ETOPO.

Globalny budżet siatki komórkowej 60″ wyliczono z wymiarów 21 600 × 10 800: 233 280 000 komórek, 933 120 000 B dla float32 DEM, 2 799 360 000 B dla trzech float32 cech i 6 065 280 000 B dla modelowanego pełnego stanu komórek. Model partii 64 wierszy z 7 wierszami halo potrzebuje około 208,1 MB tablic roboczych oraz okna źródłowego float32 i maski GSHHG 15″, przed buforami GDAL, PROJ i geometrii. To rachunek kosztu pamięci dla formatu używanego przez ETOPO, nie uruchomiony globalny raster ani pomiar szczytowego RSS lub czasu całego globu. Pełna siatka, bieguny i globalne pokrycie nadal wymagają osobnej bramki.

### Dowody próbek z K-002

| Produkt | Odczyt próbki | Układ / rozdzielczość | Kontrola jakości |
|---|---|---|---|
| ETOPO 2022 v1, kafel S15W075 | Rasterio: min −8 997 m, max 6 806.7788 m, średnia 262.3150 m, odch. std. 2 989.1015 m | 3 600 × 3 600, 15″; WGS84 + EGM2008, EPSG:9518, metry, nodata −99999 | 30 004 071 B; SHA-256 w manifeście; NOAA podaje, że wartość nodata nie występuje w siatce ETOPO. |
| LOLA LDEM_4 | 1 036 800 wartości int16; surowe DN −17 757…21 008; pierwsze próbki −239, −245, −236 | 1 440 × 720, 4 px/deg; prosta cylindryczna, DE421 mean-Earth/polar-axis; 0,5 m/DN | 2 073 600 B; etykieta określa próbkę jako mapę promienia. Nie ustawiono niezadeklarowanego nodata. |
| MOLA MEGT90N000CB + MEGC90N000CB | topografia −8 068…21 134 m; liczność obserwacji 0…2 611; pierwsze wartości −1 971 m i liczność 1 | 1 440 × 720, 4 px/deg (0,25°); IAU2000 Mars, planetocentryczny; MEGT względem areoidy GMM-3 | Każdy plik 2 073 600 B. MEGC identyfikuje komórki bez bezpośrednich obserwacji; PDS4 XML zawiera poprawiony geotransform. |

Pliki wejściowe i etykiety PDS3/PDS4 mają rozmiary, URL-e i SHA-256 w manifeście. Downloader weryfikuje rozmiar i SHA-256; surowe dane pozostają poza Gitem.

[Metadane ETOPO](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Aetopo_2022) podają CC0-1.0. Warunki konkretnej wersji oraz dokumentację pochodzenia zapisujemy wraz z cytowaniem DOI w manifeście. [SLDEM2015](https://pgda.gsfc.nasa.gov/products/54) może pomóc przy niższych szerokościach Księżyca, ale obejmuje ±60°, więc nie zastępuje polarnego LOLA.

## 3. Proponowane rozszerzenia

| Warstwa | Źródła do oceny | Wymaganie naukowe |
|---|---|---|
| Odsłonięcie gruntu / mało roślinności | NASA MODIS MOD13C2, portal [Earthdata](https://search.earthdata.nasa.gov/); [instrukcja MOD13](https://lpdaac.usgs.gov/documents/103/MOD13_User_Guide_V6.pdf) | Wybrać obecną kolekcję i okres, QA, chmury, śnieg i wodę. To ziemski proxy/filtr; nie nadajemy Marsowi NDVI = 0 jako pomiaru. |
| Temperatura powierzchni | NASA MODIS LST przez Earthdata; [LRO Diviner](https://www.diviner.ucla.edu/data); produkty Marsa w PDS | Porównać te same statystyki powierzchni i adekwatne warunki obserwacji. Tolerancje nie mogą ukrywać skrajnych różnic środowiska. |
| Mineralogia / materiały | Ziemia: ASTER/EMIT przez Earthdata; Mars: [CRISM](https://pds-geosciences.wustl.edu/missions/mro/crism.htm); Księżyc: M³ przez PDS | Zweryfikować zasięg, produkty mineralne, wspólne klasy i pewność detekcji. Sam obraz RGB lub mapka litologii nie daje ilościowego udziału minerałów. |
| Śnieg / lód, suchość, pył | Earthdata, JAXA G-Portal, Sentinel / Copernicus i planetarny PDS z oficjalnego katalogu zasobów | W osobnych zadaniach wskazać konkretny produkt, skalę, daty, licencję i interpretację procesu. |

Portale z challenge’u są punktem startu; nie oznaczają gwarancji globalności ani natychmiastowego dostępu do wszystkich plików. RADARSAT i Sentinel nie są potrzebne do pierwszego przepływu topografii — nie dodajemy integracji bez wyraźnej korzyści.

## 4. Bramka dla minerałów

1. Wybierz jeden profil Marsa lub Księżyca i dwa ziemskie AOI ze sprawdzonymi obserwacjami.
2. Sprawdź, czy produkty opisują ten sam typ informacji: identyfikację klasy, względną intensywność pasma czy oszacowanie udziału.
3. Zdefiniuj słownik mineralny i macierz zgodności z uzasadnieniem. Basalt jako litologia nie oznacza automatycznie identycznego składu minerałów.
4. Uwzględnij brak ekspozycji pod roślinnością, atmosferę, geometrię pomiaru, rozdzielczość i niepewność.
5. Opublikuj zakres pokrycia. Jeżeli pomiar jest regionalny, analizę ogranicz do wspólnego pokrycia i nazwij ją regionalną; reszta świata ma `no_data`.

Wynik pilotażu może uzasadnić P1 albo zamknięcie eksperymentu bez aktywowania warstwy. Nie publikujemy fikcyjnej globalnej mineralogii.

## 5. Pipeline

Pozyskanie z metadanymi → kontrola sum → odczyt QA/nodata → normalizacja jednostek i układu → wspólna efektywna skala → cechy w fizycznych oknach → komórki analityczne → kontrola pokrycia → manifest i publikacja.

- Reprojekcje planetarne mają właściwy promień/ellipsoidę, konwencję długości i szerokości. Nigdy nie przypisuj Marsowi EPSG:4326.
- Długości 0–360 i −180–180 są jawnie przeliczane; rejon przecinający południk 180° ma osobny test.
- Polarne dane i mapy wymagają osobnej kontroli geometrii; Web Mercator nie pokazuje samych biegunów, więc UI musi umożliwić ich oglądanie odpowiednią projekcją / widokiem.
- Pobrania i preprocessing mają checkpointy i idempotentne polecenia. Surowych wielkich rastrów nie commitujemy.
- Kontrolne AOI analogów dobieramy z literatury do danego wymiaru; NASA brief wymienia Atacamę, Haughton i Death Valley jako kontekst, nie jako etykiety zwycięzców każdego profilu.

## 6. Manifest każdego wykorzystanego zbioru

Wymagane: `dataset_id`, wersja produktu i kolekcji, provider, URL/DOI i cytowanie, `accessed_at`, licencja i URL warunków, rola w projekcie, lista plików i SHA-256, zasięg i okres, CRS/model ciała, jednostki, skala efektywna, maski i QA, kroki przetworzenia i parametry, wersja kodu, ograniczenia, oznaczenie ewentualnych danych syntetycznych.

Manifest wydania dodatkowo: `dataset_version`, `grid_version`, `model_version`, `profile_version`, rozdzielczość i geometria siatki analitycznej, dokładny obszar i reguła kwalifikowania lądu, liczności wszystkich i ważnych komórek, pokrycie wagowe powierzchnią oraz powody braków. Pustych metadanych nie wypełniamy domysłami.
