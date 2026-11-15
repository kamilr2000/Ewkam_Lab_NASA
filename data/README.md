# Dane

Właściciel: Kamil. K-002 pobrał małe próbki ETOPO 2022, LOLA LDEM_4 i MOLA MEGT/MEGC. K-017 dodał NASADEM HGT/NUM/SWB, porównawcze kafle ETOPO, GSHHG 2.3.7 i gridy geoid PROJ. Metadane, pochodzenie, rozmiary i SHA-256 są w `manifests/`; sprawdzone porównanie zapisuje `reports/k017-validation.json`. Dane surowe nie są commitowane.

Odtwarzalne pobranie próbek publicznych z K-002: `python pipeline/download_samples.py`. Dla K-017 po `uv sync --locked --group data` uruchom `uv run --locked --group data python pipeline/download_k017_assets.py`, a potem `uv run --locked --group data python pipeline/compare_nasadem_etopo.py`. Downloader K-017 korzysta z lokalnej zmiennej `EARTHDATA_TOKEN` do Earthdata Login, sprawdza przypięte rozmiary i SHA-256 oraz nie zapisuje tokenu. Szczegóły są w [instrukcji pipeline](../pipeline/README.md).

Duże dane w ignorowanych katalogach `raw/`, `intermediate/`, `processed/`, `cache/`. Małe manifesty i raporty pokrycia mogą być wersjonowane. Pobranie gotowego pakietu ma sprawdzać wersję i sumy kontrolne; źródła i ograniczenia opisuje [DATA](../docs/DATA.md).

K-005 publikuje trzy małe, skompresowane regionalne tabele komórek (`derived/k005-earth-grid/`) wraz z manifestami SHA-256, więc kolejne etapy API i UI mogą od razu pokazać rzeczywiste dane. Mają łącznie mniej niż 200 kB; zawierają wyłącznie pochodne cechy i QA, nie surowe rastry. Surowe ETOPO/GSHHG oraz checkpointy pozostają ignorowane i można je pobrać oraz odtworzyć według instrukcji w [pipeline README](../pipeline/README.md).

Jedna wersja danych obejmuje jedną siatkę i skalę. Lokalnych wyników o większej szczegółowości nie dopisujemy do tej samej tabeli jako pozornie porównywalnych kandydatów globalnych.
