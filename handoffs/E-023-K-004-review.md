# E-023 — niezależny przegląd profili K-004

**Decyzja: APPROVED dla dokładnego commita `d9ff76f7d5f3cfd18a55b82def271b9cc35030dc` (PR #36).** Nie znalazłam blokującego błędu kodu, danych, kontraktu ani opisu metody. PR pozostaje otwarty; przy ostatnim odczycie GitHub zwracał `mergeable: false`, więc Kamil musi zsynchronizować gałąź z aktualnym `main` i rozwiązać status scalania przed połączeniem. Nie próbowałam scalać cudzego PR.

## Zakres i źródła

Sprawdziłam dokładny snapshot wskazany w `tasks/E-023.md`, czyli gałąź `kamil/K-004-target-profiles` i commit `d9ff76f7d5f3cfd18a55b82def271b9cc35030dc`. Kod i wyniki uruchomiłam z wyodrębnionego snapshotu, bez zmian w plikach należących do Kamila.

Źródła odpowiadają deklarowanym produktom: [NASA PGDA LOLA Product 90](https://pgda.gsfc.nasa.gov/products/90), [PDS MOLA MEGDR](https://pds-geosciences.wustl.edu/missions/mgs/megdr.html) i [USGS Gazetteer — Jezero](https://planetarynames.wr.usgs.gov/Feature/Jezero). Manifest wejściowy zawiera 14 unikalnych plików z adresów HTTPS NASA/PDS; pobieranie potwierdziło rozmiar i SHA-256 wszystkich 14. Manifest wynikowy również zawiera 14 plików, a jego SHA manifestu wejściowego to `0d851a5ba62b637366a8052e5511c0e2c0cfa551d19473dc5a718b8615383824`.

LOLA używa DEM, LDEC, EFFRES i ERR jako osobnych warstw. Posting 80 m nie jest przedstawiany jako efektywna rozdzielczość; LDEC jest liczbą zwrotów, a nie pokryciem powierzchni. Dla MOLA MEGC pozostaje osobną informacją o bezpośrednim wsparciu, a interpolowane przez produkt wartości MEGT nie są przedstawiane jako bezpośrednie obserwacje. Produkt PGDA prosi o cytowanie i podaje DOI; nie dopisano niezadeklarowanego identyfikatora licencji. Cytowania wskazane w pakiecie to [Barker et al. 2023](https://doi.org/10.3847/PSJ/acf3e1), [LOLA PGDA DOI](https://doi.org/10.60903/gsfcpgda-lola-spole) i [MOLA PDS DOI](https://doi.org/10.17189/1z1b-kv84).

## Reprodukcja i kontrole

- `python pipeline/download_k004_sources.py`: pobrano i zweryfikowano rozmiar oraz SHA-256 14/14 przypiętych plików.
- `python pipeline/profiles/build_profiles.py`: udana niezależna reprodukcja. SHA-256 kodu buildera wynosi `dac26c01c156ae9c154f7a2b216e63c36cc852132846259cfe52c1b7e6f72e25`; uruchomienie użyło Python 3.12.14, NumPy 2.5.4, Rasterio 1.5.2, GDAL 3.12.2, pyproj 3.8.0 i PROJ 9.8.1.
- Odtworzone oba pliki `ProfileResponse v1` są semantycznie identyczne z odpowiedziami w ocenianym commicie i przechodzą `contracts/profile-response.schema.json` Draft 2020-12.
- Manifest reprodukcji jest identyczny z opublikowanym po wyłączeniu oczekiwanych pól czasu generacji, rewizji checkoutu i wersji środowiska; SHA kodu i SHA manifestu wejściowego zgadzają się. Rewizja Git w izolowanym uruchomieniu została pominięta, bo snapshot nie ma własnego katalogu `.git`.
- `python tools/check_planning.py`: `OK: 267 Markdown files, 106 JSON files, 61 task cards, acyclic dependencies, 5 synthetic cases.` To sprawdzenie waliduje dokumenty planowania i przykładową arytmetykę, nie działanie aplikacji.
- Wbudowana ręczna ekstrakcja trzech cech i round-trip długości geograficznej przechodzą dla obu profili.

### Geometrie i liczności

- Jezero: geometria ma promień 23 760 m (średnica 47 520 m). Niezależna transformacja środka lokalnej sferycznej AEQD daje 77,69°E, 18,41°N planetocentrycznie; odległość geodezyjna do punktu na obwodzie wynosi 23 760 m. Profil obejmuje 448 komórek 2 km, z trzema cechami w 448/448.
- Księżyc: wejściowy raster LOLA ma siatkę 7 600 × 7 600, posting 80 m, układ south polar stereographic w ramie DE421 i promień sfery 1 737 400 m. Niezależna transformacja krawędzi profilu daje szerokość −80°, zgodnie z granicą obszaru 80–90°S. Z 72 580 komórek trzy cechy są dostępne w 72 100.
- Liczności braków są zgodne z regułą wsparcia okna 90%: nachylenie jest dostępne dla 72 484 komórek (96 braków przy krawędzi rastra), a nierówność i deniwelacja dla 72 100 (480 braków); braki zachowują przyczynę zamiast zera.

### Metoda i ograniczenia

Oba profile używają siatki 2 km i kołowego okna fizycznego 10 km. Nachylenie pochodzi z różnic centralnych z sąsiadami, nierówność ze standardowego odchylenia reszt po odjęciu płaszczyzny LS, a deniwelacja z P95−P05. Statystyki profilu są ważone powierzchnią. Przedział P10–P90 i tolerancja `1.5 × IQR` są jawnie opisane jako prowizoryczna reguła inżynierska do analizy wrażliwości, nie próg NASA ani niepewność instrumentu. Wysokości nad areoidą MOLA i sferą księżycową nie są porównywane; porównywane są pochodne topograficzne.

Przegląd potwierdza ekstrakcję dwóch regionów referencyjnych. Nie waliduje globalnego rankingu ziemskich analogów, działającej aplikacji ani jednoznacznego „najlepszego” analogu. Wyniki nie stanowią endorsementu NASA.
