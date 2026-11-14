# Pipeline danych

Właściciel: Kamil; pierwsze zadania K-001, K-002, K-004, K-005, K-008.

Środowisko Python jest zdefiniowane w głównym `pyproject.toml`, a wersje rozwiązanych zależności w `uv.lock`. Narzędzia geodanych obejmują Rasterio do rastrów i pyproj do transformacji układów współrzędnych. Nie pobrano jeszcze produktów naukowych i nie ma tu implementacji pobierania, preprocessingu, ekstrakcji cech ani profili planetarnych.

Kolejne etapy dodadzą odtwarzalne pobieranie małych próbek, kontrolę CRS/QA, cechy w jawnej skali fizycznej oraz wersjonowany pakiet dla API. Źródła, licencje, manifesty i stan faktycznego pokrycia opisuje [DATA](../docs/DATA.md).
