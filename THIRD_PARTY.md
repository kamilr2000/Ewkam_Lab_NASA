# Materiały zewnętrzne

MIT obejmuje własny kod i dokumentację projektu. Nie zmienia praw do danych NASA, NOAA, ESA, zdjęć, podkładów map ani bibliotek. Nie dodano jeszcze danych naukowych ani zależności aplikacji.

Przy dodaniu materiału dopisz wiersz i zachowaj wymagany tekst licencji/atrybucji. Publiczny dostęp do portalu nie wystarcza do uznania każdego produktu za swobodnie redystrybuowalny.

| Materiał / wersja | Zastosowanie i pliki | Autor / URL | Licencja / warunki i dowód | Atrybucja | Status |
|---|---|---|---|---|---|
| Dokumentacja organizatora | Streszczenia i linki w `docs/sources/` | NASA Space Apps; linki w rejestrze | Odnośniki i własne streszczenia; bez kopii całych stron | Źródła przy streszczeniach | dodano |
| ETOPO 2022 v1, 15″ surface tile S15W075 | Rzeczywista próbka DEM Ziemi; manifest data/manifests/k002-samples.json | NOAA NCEI; DOI 10.25921/fd45-gt74 | CC0-1.0 w metadanych NOAA; dane nie są przeznaczone do nawigacji | Cytuj NOAA NCEI i DOI | próbka pobrana i zweryfikowana; pełny produkt nie pobrany |
| LOLA LDEM_4, PDS dataset V3.0 | Rzeczywista próbka promienia/kształtu Księżyca; PDS3 IMG/LBL i PDS4 XML | NASA PDS Geosciences Node; DOI 10.17189/1520642 | PDS data są public domain; dokumenty PDS mogą mieć odrębne prawa | Cytuj zbiór PDS i DOI | próbka oraz etykiety pobrane i zweryfikowane |
| MOLA MEGT/MEGC 4 px/deg | Rzeczywista próbka topografii Marsa i liczby obserwacji; etykiety PDS3/PDS4 | NASA PDS Geosciences Node; DOI 10.17189/1z1b-kv84 | PDS data są public domain; dokumenty PDS mogą mieć odrębne prawa | Cytuj bundle PDS4 i DOI | próbka, mapa liczności i etykiety pobrane i zweryfikowane |
| NASADEM_HGT v001 | Planowana walidacja ziemskiego DEM NASA i maska SWB z tego produktu | NASA JPL / LP DAAC; DOI 10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001; granula i link zapisane w manifeście próbek | CC0-1.0 według odpowiedzi LP DAAC; Earthdata Login wymagany do pliku | Cytuj NASA JPL, NASADEM v001 i DOI | katalog, DOI i licencja potwierdzone; plik wymaga lokalnych danych logowania |
| GSHHG 2.3.7 | Kandydat na niezależną maskę polygonową lądu i jezior; nie pobrano | NOAA NCEI; strona źródła w docs/DATA.md | GNU LGPL według NOAA; przejrzeć warunki i zachować atrybucję przy pobraniu | Wessel & Smith, DOI 10.1029/96JB00104, oraz GSHHG | kandydat, nie wdrożono |

Źródła warunków ETOPO: [metadane NOAA](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Aetopo_2022); [odpowiedź LP DAAC o licencji NASADEM](https://forum.earthdata.nasa.gov/viewtopic.php?p=18837&t=5421). Dla NASA PDS dane i dokumenty mogą mieć różne warunki; cytuj DOI produktu. Maska lądu, granice i kafle mapy również wymagają osobnego wpisu. Nie oznaczaj całego katalogu danych etykietą MIT.
