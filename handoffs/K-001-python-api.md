# Przekazanie: K-001 — środowisko Python i readiness API

- Od: Kamil, `codex-kamil-k001-runtime`
- Do: Ewelina
- Data i strefa: 2026-11-14, Europe/Warsaw
- Zadanie / PR / commit: K-001 / [PR #4](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/4) / implementacja `e00bdf16085a04d9836035f659067b9865dcea88`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-001-api-bootstrap`
- Czy rezerwacja / rezultat są w origin/main: rezerwacja K-001 jest w `origin/main`; kod i ten handoff są w opublikowanej gałęzi oraz PR #4, nie w `main`.
- Lokalne niewysłane zmiany: brak.
- Stan: gotowe do przeglądu.

## Co jest dostępne

- Główne `pyproject.toml`, `.python-version` i `uv.lock` przypinają Python 3.12.14 oraz FastAPI 0.162.7, NumPy 2.5.4, Rasterio 1.5.2, pyproj 3.8.0 i Uvicorn 0.54.0.
- `apps/api/main.py` udostępnia `GET /api/v1/health`. Odpowiedź potwierdza gotowość procesu API i jawnie zwraca `dataset_ready: false`, `dataset_version: null`.
- `apps/api/tests/test_health.py` sprawdza tę odpowiedź. `pipeline/tests/README.md` wskazuje miejsce na kolejne testy preprocessingu i silnika.
- Instrukcje uruchomienia są w [apps/api/README.md](../apps/api/README.md), a granice obecnego pipeline w [pipeline/README.md](../pipeline/README.md).

Endpoint nie udostępnia katalogu, profili, scoringu ani wyszukiwania. Nie pobrano danych naukowych i nie zwracamy fikcyjnych wyników.

## Jak odtworzyć

Z katalogu głównego repozytorium:

```powershell
uv python install
uv sync --locked --dev
uv run --locked python -m uvicorn apps.api.main:app --reload
```

W drugim terminalu:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
uv run --locked pytest
```

Wersje, konfiguracja i komendy odpowiadają `uv.lock` oraz `apps/api/README.md`.

## Sprawdzenia

- Świeży tymczasowy virtualenv: `uv sync --locked --dev` z Pythonem 3.12.14 zainstalował wszystkie zależności.
- `uv run --locked pytest`: 1 test zaliczony.
- `uv python install`: potwierdził zainstalowany Python 3.12.14.
- Uruchomiono serwer udokumentowaną komendą `uv run`; `GET /api/v1/health` zwrócił `{"status":"ready","dataset_ready":false,"dataset_version":null}`.
- `python tools/check_planning.py`: OK — 67 plików Markdown, 4 JSON, 31 kart, acykliczne zależności, 5 przypadków syntetycznych.
- `git diff --check`: bez błędów.

Nie sprawdzano pobierania ani przetwarzania rzeczywistych danych, bo nie należy to do K-001.

## Ograniczenia i potrzebne działania

Proszę sprawdzić [PR #4](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/4), zwłaszcza możliwość instalacji Rasterio/pyproj na drugim komputerze oraz zgodność kształtu health endpointu z planowanym kontraktem K-003. Rezerwacja K-001 ma osobną kartę w `origin/main`; status przejdzie do `review` po opublikowaniu karty przeglądu Eweliny. Po akceptacji PR należy połączyć kod do `main`, a dopiero potem oznaczyć K-001 jako `done`.
