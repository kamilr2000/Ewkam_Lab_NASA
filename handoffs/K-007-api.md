# Przekazanie K-007 — regionalne API na rzeczywistych danych

- Od: Kamil / Codex
- Do: Ewelina
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: K-007, PR #70
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-007-api-first-real-run`
- Wysłany SHA implementacji: `7b55cb8e813160e5f1c92d91170a3604252d541b`
- Czy rezerwacja jest w `origin/main`: tak; implementacja pozostaje w PR, status K-007 będzie przekazany do review osobnym wpisem w `origin/main`.
- Stan: działający regionalny etap MVP, gotowy do niezależnego review; nie jest to globalne wyszukiwanie.

## Co jest dostępne

API udostępnia:

- `GET /api/v1/health`, `/catalog`, `/catalog/profiles/{profile_id}` oraz `/catalog/datasets/{dataset_version}/manifest`.
- `POST /api/v1/search` z wyborem profilu Marsa lub Księżyca, jednego z trzech pakietów Earth search, aktywnych kryteriów, dodatnich wag i trybu `pixels` albo `distinct_areas`.
- `GET /api/v1/analyses/{analysis_id}/pixels/{pixel_id}` oraz `GET /api/v1/analyses/{analysis_id}/map` dla tej samej zamrożonej analizy.

Warstwy P0 to nachylenie (`slope_deg`, stopnie), lokalna nierówność (`roughness_m`, metry) i lokalna deniwelacja (`relief_m`, metry). Są to trzy miary topografii, nie trzy niezależne dziedziny ani mineralogia. Serwer używa istniejącego silnika K-006, sprawdza rozmiar i SHA-256 spakowanych plików K-005 i nie zmienia wag zależnie od braków.

W katalogu są profile `mars-jezero-mola128-v1` oraz `moon-south-polar-80s-lola80-v1` i regionalne wersje `k005-earth-2km-atacama-andes-v2`, `k005-earth-2km-hawaii-big-island-v2`, `k005-earth-2km-himalaya-v2`. Wersja jest jawna; odpowiedź zawiera `analysis_id`, wersje i rzeczywisty scope. Globalne żądanie zwraca `SCOPE_UNAVAILABLE` zamiast wyników regionalnych.

## Rzeczywiste przebiegi

Przebiegi użyły trzech aktywnych cech ze wagami `1, 2, 1`, trybu `pixels` i pełnego skanu wskazanego regionalnego pakietu. Wynik 100% oznacza, że każda aktywna miara mieści się w swoim przedziale referencyjnym według zadeklarowanych tolerancji; nie oznacza ogólnej równoważności środowiska ani przydatności lokalizacji.

| Profil | Pakiet Earth | Komórki | Kwalifikujące się | Wykluczone | Najlepszy piksel | Wynik |
|---|---|---:|---:|---|---|---:|
| Mars, Jezero | Atacama/Andes | 1 796 | 1 791 | 5 `failed_quality` | `earth:k005-earth-2km-atacama-andes-v2:r00008:c00009` | 100% |
| Księżyc, biegun południowy | Hawaii Big Island | 1 854 | 1 497 | 206 `failed_quality`, 151 `outside_mask` | `earth:k005-earth-2km-hawaii-big-island-v2:r00008:c00020` | 100% |

Testy integracyjne wysyłają żądania przez aplikację FastAPI z rzeczywistymi profilami i danymi dla obu ciał. Dodatkowy test potwierdza wyszukiwanie z jedną aktywną cechą i normalizację jej wagi. Mapa poziomu 8 oraz endpoint mapy korzystają z wyników tych samych pikseli; szczegóły zwycięskiego piksela mają identyczny wynik i `analysis_id`.

## Jak odtworzyć

Z katalogu repozytorium:

```powershell
uv sync --locked --dev
uv run --locked python -m uvicorn apps.api.main:app --reload
```

Serwer działa domyślnie pod `http://127.0.0.1:8000`; `/docs` pokazuje operacje API. Przykład zapytania dla profilu Marsa:

```powershell
$request = @{
  contract_version = '1.0.0'
  body = 'mars'
  profile_id = 'mars-jezero-mola128-v1'
  dataset_version = 'k005-earth-2km-atacama-andes-v2'
  scope = @{ type = 'regional'; region_id = 'atacama-andes' }
  criteria = @(
    @{ feature_id = 'slope_deg'; weight = 1 },
    @{ feature_id = 'roughness_m'; weight = 2 },
    @{ feature_id = 'relief_m'; weight = 1 }
  )
  result_mode = 'pixels'
  top_k = 10
} | ConvertTo-Json -Depth 8

$result = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/v1/search' -ContentType 'application/json' -Body $request
$result.ranking[0]
```

Dla pierwszego przebiegu Księżyca zmień `body` na `moon`, `profile_id` na `moon-south-polar-80s-lola80-v1`, `dataset_version` na `k005-earth-2km-hawaii-big-island-v2`, a `scope.region_id` na `hawaii-big-island`. Nie zmieniaj payloadu na `global`, bo taki zbiór nie jest jeszcze opublikowany.

Po utworzeniu analizy szczegóły pobiera się z jej `analysis_id` i `pixel_id`; mapa przyjmuje `bbox=west,south,east,north`, `level` jako zoom XYZ 0–30, opcjonalne `limit` i zwracany `cursor`. Mapa grupuje wspólne wyniki pikseli; maksimum wskazuje `max_pixel_id`, a średnia jest ważona powierzchnią.

## Sprawdzenia

- `.venv\Scripts\python.exe -m pytest -q` — 84 passed.
- `python tools/check_planning.py` — OK: 161 Markdown, 40 JSON, 79 kart, acykliczne zależności i 5 syntetycznych przypadków.
- `git diff --check` — bez błędów.
- Wersje lokalne: Python 3.12.14, FastAPI 0.162.7, NumPy 2.5.4, pyproj 3.8.0.

Testy kontraktu walidują odpowiedzi przez JSON Schema v1 i pokrywają oba profile, katalog/manifest, ranking, jedną cechę, `distinct_areas`, paginację mapy, zgodność szczegółów, duplikat cechy, brak/wartość null odległości oraz odrzucenie scope global. Kontrola planu nie jest testem aplikacji; rzeczywiste dane użyte w przebiegach pochodzą z opublikowanych pakietów K-005.

## Ograniczenia i potrzebne działania

- Trzy regionalne zbiory topografii mają nominalną komórkę analityczną ok. 2 km. Wynik nie dowodzi globalnego optimum; następny główny krok techniczny to K-008: globalne dane, pokrycie, wydajność i agregaty.
- Porównanie nie obejmuje mineralogii, lodu, temperatury ani dowodów życia. Nie przewiduje też przydatności miejsca do budowy bazy.
- Zamrożone analizy są przechowywane lokalnie przez godzinę, maksymalnie 16; restart je unieważnia. Obecne API wymaga jednego workera Uvicorn. Wdrożenie wieloprocesowe wymaga wspólnego magazynu analiz.
- Zgłoszenie NASA i oświadczenia pozostają wyłącznie dla człowieka; ta implementacja niczego nie wysyła.
- Ewelina: sprawdź exact head PR #70 i kontrakt/mapę/detale dla realnych danych. Rejestr AI/SI nadal mówi, że backend ma tylko health; utworzę osobne zadanie dla Eweliny, zależne od integracji K-007 i kolejki ujawnień.
