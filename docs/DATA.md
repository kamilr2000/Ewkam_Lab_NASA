# Dane, warstwy i profile

Stan 2026-11-14: K-002 pobrał i poprawnie odczytał małe rzeczywiste próbki ETOPO, LOLA i MOLA. Ich pochodzenie, etykiety, rozmiary i SHA-256 zapisano w manifeście próbek w data/manifests/k002-samples.json; odtwarzalne pobranie uruchamia pipeline/download_samples.py. To próbki techniczne, nie gotowe warstwy aplikacji ani dowód globalnego pokrycia. NASADEM jest widoczny w katalogu, ale wymaga lokalnego logowania Earthdata; bez uwierzytelnienia nie pobrano pomiarów.

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
| D02 | [NASA/METI ASTER GDEM v3](https://asterweb.jpl.nasa.gov/gdem.asp) lub NASADEM: niezależna walidacja ziemskich cech | Do kolejnego sprawdzenia wybrano NASADEM HGT v001 (DOI 10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001, CC0-1.0). CMR potwierdza granule, ale plik LP DAAC wymaga Earthdata Login; próbki nie pobrano. Porównać w co najmniej trzech AOI po wspólnym przeskalowaniu i jawnie rozdzielić EGM96 od EGM2008. NASADEM SWB może dostarczyć maskę lądu/wody tylko w zasięgu SRTM, bez obszarów polarnych. |
| D03 | [LRO LOLA w NASA PDS](https://pds-geosciences.wustl.edu/missions/lro/lola.htm): profil Księżyca; pobrano LDEM_4 i etykiety PDS3/PDS4 | Globalny produkt 4 piksele/stopień przechowuje promień względem sfery odniesienia (DN × 0,5 m + 1 737 400 m); topografia względem geoidy wymaga odjęcia promienia geoidy. Nie porównywać surowych wysokości między ciałami. |
| D04 | [MGS MOLA MEGDR / Topography Derived](https://pds-geosciences.wustl.edu/missions/mgs/megdr.html): profil Marsa; pobrano globalny MEGT 4 px/deg oraz MEGC | Używaj utrzymywanego bundle PDS4 z 2026 r. MEGT jest topografią względem areoidy MOLA GMM-3; MEGC zawiera liczbę obserwacji. Produkt interpoluje nieobserwowane komórki — zachowuj MEGC i oznaczaj zerową liczbę obserwacji jako brak bezpośredniego pomiaru. |
| D05 | [GSHHG przez NOAA](https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html): kandydat na globalną maskę lądu i jezior | NOAA wskazuje wersję 2.3.7, WGS84 i LGPL. Kandydat nie został pobrany ani wdrożony. Nie wyznaczać lądu progiem wysokości 0 m. |

D01 jest produktem NOAA, nie NASA ani agencji partnerskiej Space Apps. Próbki D03/D04 są rzeczywistymi produktami NASA PDS, ale nie zastępują niezależnej walidacji cech Ziemi przez dane NASA Earth. Rola NASA Earth w obliczeniach pozostaje otwarta do czasu pobrania i porównania NASADEM lub uzgodnionego zamiennika.

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
