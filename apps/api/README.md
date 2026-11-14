# API

Właściciel: Kamil; K-001, K-006, K-007, K-008.

## Uruchomienie lokalne

Wymagane: `uv`. Z katalogu głównego repozytorium:

```powershell
uv python install
uv sync --locked --dev
uv run --locked python -m uvicorn apps.api.main:app --reload
```

Serwer deweloperski nasłuchuje domyślnie na `http://127.0.0.1:8000`. Gotowość procesu można sprawdzić przez `GET /api/v1/health`; interaktywny opis OpenAPI jest pod `/docs`.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
uv run --locked pytest
```

`/api/v1/health` potwierdza wyłącznie gotowość API. Zwraca `dataset_ready: false` i `dataset_version: null`, dopóki nie zostanie przygotowany rzeczywisty pakiet danych. Endpoint nie uruchamia analizy i nie zwraca wyników syntetycznych.

Testowana konfiguracja: Python 3.12.10, FastAPI 0.162.7, NumPy 2.5.4, Rasterio 1.5.2, pyproj 3.8.0 i Uvicorn 0.54.0. Pełne wersje zależności bezpośrednich i pośrednich są przypięte w `uv.lock`.

## Zakres

To jest punkt startowy FastAPI. K-003 zamrozi kontrakt odpowiedzi, K-006 doda silnik podobieństwa, a K-007 wyszukiwanie na rzeczywistych danych. Specyfikacja: [CONTRACTS](../../docs/CONTRACTS.md). Konfiguracja Pythona i przypięte zależności są w głównym `pyproject.toml` i `uv.lock`.
