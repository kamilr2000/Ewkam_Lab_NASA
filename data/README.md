# Dane

Właściciel: Kamil. K-002 pobrał małe próbki ETOPO 2022, LOLA LDEM_4 i MOLA MEGT/MEGC. Metadane, etykiety PDS3/PDS4, rozmiary i SHA-256 są w manifeście próbek. Dane surowe nie są commitowane.

Odtwarzalne pobranie próbek publicznych: uruchom z katalogu repo polecenie `python pipeline/download_samples.py`. Program sprawdza rozmiar i SHA-256, a poprawne pliki już obecne tylko weryfikuje. NASADEM wymaga lokalnego logowania Earthdata i nie jest pobierany przez ten skrypt.

Duże dane w ignorowanych katalogach `raw/`, `intermediate/`, `processed/`, `cache/`. Małe manifesty i raporty pokrycia mogą być wersjonowane. Pobranie gotowego pakietu ma sprawdzać wersję i sumy kontrolne; źródła i ograniczenia opisuje [DATA](../docs/DATA.md).

Jedna wersja danych obejmuje jedną siatkę i skalę. Lokalnych wyników o większej szczegółowości nie dopisujemy do tej samej tabeli jako pozornie porównywalnych kandydatów globalnych.
