# Dane, warstwy i profile

Stan 2026-11-14: zweryfikowano opisy źródeł i zasobów organizatora; **nie pobrano jeszcze produktów naukowych ani nie zmierzono ich kompletności**. Dostępność konkretnego pliku, jego wersję i warunki zatwierdza K-002. Poniższa lista jest propozycją implementacyjną, a nie listą produktów już wykorzystanych.

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
| D02 | [NASA/METI ASTER GDEM v3](https://asterweb.jpl.nasa.gov/gdem.asp): rzeczywiste porównanie cech na wybranych ziemskich wycinkach | Zasięg 83°S–83°N, artefakty, dostęp przez Earthdata. Pobrać co najmniej trzy AOI, sprowadzić do tej samej skali i policzyć rozbieżności z D01. Nie ogłaszać danych ASTER jako pełnego globalnego podkładu. |
| D03 | [LRO LOLA w NASA PDS](https://pds-geosciences.wustl.edu/missions/lro/lola.htm): profil topograficzny Księżyca | Wybierać produkty gridded/polar zgodne z regionem. Zachować etykiety produktu, jednostki i model ciała. |
| D04 | [MGS MOLA MEGDR / Topography Derived](https://pds-geosciences.wustl.edu/missions/mgs/megdr.html): profil topograficzny Marsa | Odczytać topografię, nie surowy promień. PDS wskazuje migrację do PDS4 w 2026 r.; dobrać aktualny produkt i jego etykiety. |
| D05 | [GSHHG przez NOAA](https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html): kandydat na maskę lądu i jezior | LGPL według strony; zachować wersję i wymagane noty albo wybrać sprawdzone zgodne źródło. Nie wyznaczać lądu progiem wysokości 0 m. |

D01 jest produktem NOAA, nie NASA ani agencji partnerskiej Space Apps. Rola danych NASA w rozwiązaniu to D03/D04 w samym wyniku oraz D02 w ilościowej walidacji ziemskich cech. Raport musi pokazywać wykonane obliczenia D02, nie sam link. Jeśli D02 jest niedostępne, K-002 wybiera inne realne NASA Earth dane i aktualizuje plan; nie zaznacza tego wymagania jako spełnione.

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
