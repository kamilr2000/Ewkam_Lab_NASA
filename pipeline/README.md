# Pipeline danych

Właściciel: Kamil; zadania K-001, K-002, K-004, K-005, K-008, K-017.

Środowisko Python jest zdefiniowane w głównym `pyproject.toml`, a wersje rozwiązanych zależności w `uv.lock`. Skrypt `download_samples.py` pobiera publiczne próbki z `data/manifests/k002-samples.json` i weryfikuje liczbę bajtów oraz SHA-256. Uruchom z katalogu repo polecenie `python pipeline/download_samples.py`. Surowe dane trafiają do ignorowanego katalogu `data/raw/k002`.

## NASADEM, maska i porównanie K-017

Zainstaluj grupę zależności danych, skonfiguruj lokalnie `EARTHDATA_TOKEN`, a następnie uruchom:

```text
uv sync --locked --group data
uv run --locked --group data python pipeline/download_k017_assets.py
uv run --locked --group data python pipeline/compare_nasadem_etopo.py
```

Downloader korzysta z `earthaccess` przez zmienną środowiskową, nie zapisuje ani nie wyświetla tokenu, pobiera wskazane granule CMR i sprawdza nazwy, zawartość ZIP, wymiary, rozmiary, SHA-256, zakres HGT oraz klasy NUM/SWB. Pobiera też przypięte kafle ETOPO, GSHHG 2.3.7 i gridy PROJ. Archiwa GSHHG są bezpiecznie rozpakowywane do ignorowanego `data/raw/k017`; raw nie trafia do Git. `--nasadem-only` ogranicza downloader do NASADEM. `--record-checksums` zapisuje rozmiary, sumy i obserwowane statystyki warstw do manifestu po sprawdzeniu plików.

`compare_nasadem_etopo.py` transformuje HGT z EGM96 do EGM2008 lokalnymi gridami PROJ, przelicza oba DEM-y do wspólnej siatki lokalnego UTM 2 km, rasteruje niezależną maskę GSHHG oraz porównuje nachylenie, nierówność po odjęciu lokalnej płaszczyzny i P95−P05 w kołowym promieniu 10 km. Raport `data/reports/k017-validation.json` zawiera liczności, różnice masek, histogramy NUM, błędy wysokości i cech oraz cztery testy maski. Wynik obejmuje trzy AOI; nie jest globalnym rankingiem ani globalną walidacją DEM.

Próbki z K-002 oraz wyniki K-017 dowodzą odczytu i pochodzenia wskazanych plików, nie pełnego globalnego przetwarzania. Preprocessing globalnej siatki, raport pokrycia i profile planetarne pozostają kolejnymi zadaniami. Źródła, licencje i ograniczenia opisuje [DATA](../docs/DATA.md) oraz [THIRD_PARTY](../THIRD_PARTY.md).
