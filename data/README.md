# Dane

Właściciel: Kamil. K-002 pobrał małe próbki ETOPO 2022, LOLA LDEM_4 i MOLA MEGT/MEGC. K-017 dodał NASADEM HGT/NUM/SWB, porównawcze kafle ETOPO, GSHHG 2.3.7 i gridy geoid PROJ. K-004 dodał profil Jezero z MOLA 128 px/° oraz profil księżycowej czapy 80–90°S z LOLA PGDA 80 m. Metadane, pochodzenie, rozmiary i SHA-256 są w `manifests/`; raporty K-017 i K-004 zapisują sprawdzenia i ograniczenia. Dane surowe nie są commitowane.

Odtwarzalne pobranie próbek publicznych z K-002: `python pipeline/download_samples.py`. Dla K-017 po `uv sync --locked --group data` uruchom `uv run --locked --group data python pipeline/download_k017_assets.py`, a potem `uv run --locked --group data python pipeline/compare_nasadem_etopo.py`. Dla K-004 uruchom `python pipeline/download_k004_sources.py`, a następnie `python pipeline/profiles/build_profiles.py`; downloader pobiera publiczne pliki bez EARTHDATA_TOKEN, sprawdza przypięte rozmiary/SHA-256, a builder dodatkowo odrzuca źródła różne od wersji w lockfile. Szczegóły są w [instrukcji pipeline](../pipeline/README.md).

Duże dane w ignorowanych katalogach `raw/`, `intermediate/`, `processed/`, `cache/`. Małe manifesty i raporty pokrycia mogą być wersjonowane. Pobranie gotowego pakietu ma sprawdzać wersję i sumy kontrolne; źródła i ograniczenia opisuje [DATA](../docs/DATA.md).

K-005 publikuje trzy małe, skompresowane regionalne tabele komórek (`derived/k005-earth-grid/`) wraz z manifestami SHA-256, więc kolejne etapy API i UI mogą od razu pokazać rzeczywiste dane. Mają łącznie mniej niż 200 kB; zawierają wyłącznie pochodne cechy i QA, nie surowe rastry. Surowe ETOPO/GSHHG oraz checkpointy pozostają ignorowane i można je pobrać oraz odtworzyć według instrukcji w [pipeline README](../pipeline/README.md).

Jedna wersja danych obejmuje jedną siatkę i skalę. Lokalnych wyników o większej szczegółowości nie dopisujemy do tej samej tabeli jako pozornie porównywalnych kandydatów globalnych.
