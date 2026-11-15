# API

Właściciel: Kamil; K-001, K-006, K-007, K-008.

## Uruchomienie lokalne

Wymagane: `uv`. Z katalogu głównego repozytorium:

```powershell
uv python install
uv sync --locked --dev
uv run --locked python -m uvicorn apps.api.main:app --reload
```

Serwer deweloperski nasłuchuje domyślnie na `http://127.0.0.1:8000`. Interaktywny opis tras jest pod `/docs`; zamrożony kontrakt v1 znajduje się w [CONTRACTS](../../docs/CONTRACTS.md) i `contracts/openapi.yaml`.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/catalog
```

### Live web na osobnym originie

API dopuszcza domyślnie tylko `http://localhost:5173` i `http://127.0.0.1:5173`, czyli lokalne originy Vite. Dla innej konfiguracji ustaw `TERRA_ANALOG_CORS_ORIGINS` na rozdzieloną przecinkami listę dokładnych originów aplikacji web (schemat i host z opcjonalnym portem, bez ścieżki); wildcardy, cookies i credentials są wyłączone. Niezdefiniowana zmienna zachowuje domyślne originy lokalne, a jawnie pusta lista wyłącza dostęp CORS.

Uruchom API w pierwszym terminalu:

```powershell
uv run --locked python -m uvicorn apps.api.main:app --reload
```

W drugim terminalu, w katalogu `apps/web`, wskaż API i uruchom Vite:

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

Jeśli web jest wdrożony pod innym adresem, ustaw `TERRA_ANALOG_CORS_ORIGINS` po stronie API na dokładny origin web, np. `https://demo.example`; po stronie web ustaw `VITE_API_BASE_URL` na origin API. Nie umieszczaj ścieżki ani końcowego ukośnika w żadnej z tych wartości. CORS jest ograniczeniem dostępu z przeglądarki i nie uwierzytelnia API.

Health sprawdza rozmiar i SHA-256 trzech śledzonych pakietów K-005. Zwraca `dataset_ready: true`, gdy lokalne dane przechodzą kontrolę. `dataset_version` pozostaje `null`, ponieważ istnieją trzy niezależne, niemieszane wersje regionalne.

## Obsługiwane dane i zakres

API udostępnia profile `mars-jezero-mola128-v1` oraz `moon-south-polar-80s-lola80-v1`, a także rzeczywiste pakiety Earth search `k005-earth-2km-atacama-andes-v2`, `k005-earth-2km-hawaii-big-island-v2` i `k005-earth-2km-himalaya-v2`. Katalog zwraca aktualne regiony, źródła, wersje, ostrzeżenia i ograniczenia.

`POST /api/v1/search` wykonuje pełny ranking komórek jednego wybranego regionu, zapisuje konfigurację w `analysis_id`, zwraca ranking pikseli albo osobny ranking `distinct_areas` oraz kafle mapy poziomu 8. Profile Marsa i Księżyca porównują te same trzy cechy topograficzne. Braki są wykluczane dla aktywnych cech; wagi nie są lokalnie przeliczane.

Globalny zakres nie ma jeszcze pakietu Earth search. Żądanie `{"type":"global"}` zwraca `SCOPE_UNAVAILABLE`; serwer nigdy nie ogranicza go po cichu do dostępnych regionów. Wynik regionalny nie jest globalnym optimum ani NASA endorsement.

Endpoint mapy przyjmuje `bbox=west,south,east,north`, `level` 0–30, opcjonalne `limit` i `cursor`. `level` oznacza zoom kafli XYZ Web Mercator. Średnia kafla jest ważona powierzchnią, a `max_pixel_id` wskazuje konkretny piksel z tym wynikiem. Kafle przecinające bbox mogą obejmować także komórki poza granicą bbox, jeśli należą do tego samego kafla.

Analizy są przechowywane w pamięci procesu przez godzinę, maksymalnie 16 naraz; po restarcie serwera identyfikatory analiz nie są odtwarzane. Ten etap MVP wymaga jednego workera Uvicorn: wiele workerów nie współdzieli `analysis_id`, więc żądania szczegółów i mapy mogą trafić do procesu bez zapisanej analizy. Wdrożenie wieloprocesowe wymaga wspólnego trwałego magazynu analiz. K-008 odpowiada za globalne przetwarzanie, pełne pokrycie, pomiary skali i mapowe agregaty dla globalnego zbioru.

Testowana konfiguracja: Python 3.12.14, FastAPI 0.162.7, NumPy 2.5.4, Rasterio 1.5.2, pyproj 3.8.0 i Uvicorn 0.54.0. Wersje zależności są przypięte w głównym `pyproject.toml` i `uv.lock`.
