# Pipeline danych

Właściciel: Kamil; zadania K-001, K-002, K-004, K-005, K-008.

Środowisko Python jest zdefiniowane w głównym `pyproject.toml`, a wersje rozwiązanych zależności w `uv.lock`. Skrypt `download_samples.py` używa biblioteki standardowej, aby pobrać publiczne próbki z `data/manifests/k002-samples.json` i weryfikuje liczbę bajtów oraz SHA-256. Uruchom z katalogu repo polecenie `python pipeline/download_samples.py`. Surowe dane trafiają do ignorowanego katalogu `data/raw/k002`.

Próbki dowodzą odczytu i pochodzenia pojedynczych plików, nie pełnego globalnego przetwarzania. NASADEM wymaga uwierzytelnienia Earthdata i obecnie nie ma lokalnej próbki. Preprocessing, kontrola pokrycia, ekstrakcja cech i profile planetarne pozostają kolejnymi zadaniami. Źródła, licencje i ograniczenia opisuje [DATA](../docs/DATA.md).
