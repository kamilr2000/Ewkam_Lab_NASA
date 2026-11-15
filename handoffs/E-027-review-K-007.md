# E-027 — wynik review regionalnego API K-007

- Od: Ewelina / `codex-ewelina-e027-review`
- Do: Kamil
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR: E-027 / K-007 / PR #70
- Exact requested `review_ref`: `cd9caff3fb700cd6683c468b8937d815dcc5a1be`
- Oceniony head PR #70: `4f7e296624b7ea1e9889906c23b3b9fedcb94f4a`
- Gałąź Eweliny: `ewelina/E-027-review-k007-real-api`
- Bieżący `origin/main` po opublikowaniu K-041: `ad829f10e53ec982165ae2d57b9c1101bf208137`
- Decyzja review: APPROVED dla exact `review_ref` i bieżącego headu; GitHub review [#5910789661](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/70#pullrequestreview-5910789661) przypięto do `4f7e296`. PR #70 pozostaje otwarty i nie jest scalony.

## Decyzja

**APPROVED dla zakresu K-007: regionalne API, jego kontrakt v1 oraz przebiegi na rzeczywistych pakietach Atacama/Andes i Hawaii Big Island. Nie znalazłam uwagi P0 ani P1.**

Występuje nieblokująca uwaga P2 dotycząca coercion typów requestu przez domyślną walidację Pydantic. Dodałam dla Kamila kartę [K-041](../tasks/K-041.md), opublikowaną w `origin/main` commitem `ad829f1`. Zależność od K-007 utrzymuje poprawkę poza równoległą zmianą jego API.

Exact `review_ref` jest przodkiem bieżącego headu PR #70. Zmiany po `cd9caff` są synchronizacją kart i dokumentacji z `main`; `git diff --stat cd9caff..4f7e296` nie pokazuje zmian `apps/api/`, kontraktu ani danych. Ocenę uruchomiłam na headzie PR.

## Źródła, wersje i zakres pomiarów

- Profile Marsa i Księżyca mają `is_synthetic: false`. Wersje to odpowiednio `mola128-2km-grid-10km-window-v1` i `lola-pgda-80m-2km-grid-10km-window-v1`. Profile wskazują źródła MOLA MEGDR v2 MEGT/MEGC oraz LOLA PGDA 80 m wraz z warstwami jakości.
- Pakiety Earth są wersjonowane osobno dla Atacama/Andes, Hawaii Big Island i Himalaya; każdy ma własny `dataset_version`, `grid_version` i wspólną wersję modelu `terrain-p0-k005-v2`. Źródła manifestów to NOAA ETOPO 2022 v1 surface elevations i maska lądu/wody GSHHG 2.3.7, z cytowaniami, URL-ami, licencjami oraz SHA-256 wyjść.
- API udostępnia trzy cechy topografii: `slope_deg` (degree), `roughness_m` (meter) i `relief_m` (meter). Jednostki i skale pomiaru profilu oraz manifestów są zgodne. Komórka analityczna Earth ma nominalnie 2 km; cechy roughness/relief używają okna 10 km. Wynik nie porównuje wysokości nad ziemskim geoidem z marsjańskim areoidem ani księżycową sferą odniesienia — porównywane są pochodne terenu.
- Katalog i odpowiedzi jawnie określają porównanie jako regionalne i topograficzne. Nie przedstawiają go jako globalnego optimum, mineralogii, pełnej analogii środowiskowej ani endorsement NASA.

## Odtworzone rzeczywiste przebiegi

Oba requesty użyły trzech cech, wag `1:2:1`, trybu `pixels` i `top_k=10`. Request, SearchResponse i PixelDetailsResponse walidują się względem Draft 2020-12 JSON Schema.

| Profil / pakiet | Komórki | Kwalifikujące się | Wykluczone | Udział kwalifikującej się powierzchni | Najlepszy piksel | Wynik |
|---|---:|---:|---|---:|---|---:|
| Mars Jezero / Atacama–Andes | 1 796 | 1 791 | 5 `failed_quality` | 99,72% | `earth:k005-earth-2km-atacama-andes-v2:r00008:c00009` | 100% |
| Księżycowy profil 80–90°S / Hawaii Big Island | 1 854 | 1 497 | 206 `failed_quality`, 151 `outside_mask` | 80,74% | `earth:k005-earth-2km-hawaii-big-island-v2:r00008:c00020` | 100% |

Liczniki wykluczeń zgadzają się z kategoriami manifestów K-005 (`insufficient_window_support`, `insufficient_slope_support` i `not_land`). `load_registry()` sprawdza rozmiar, SHA-256 i liczbę wierszy pakietów; pełny test integracyjny K-007 używa tych samych rzeczywistych profili i danych.

W obu przebiegach `max_pixel_id` przeglądu mapy wskazał piksel rankingu z maksymalnym wynikiem. Szczegóły zwycięskiego piksela zwróciły ten sam `analysis_id` i `score_pct`. Test paginacji endpointu mapy potwierdza, że kolejne strony pozostają w tej samej analizie.

## Kontrakt i zachowanie API

- Dodatnie wagi są normalizowane raz dla całej konfiguracji. Duplikaty `feature_id` są odrzucane, tryby `pixels` i `distinct_areas` mają osobne odpowiedzi, a brak aktywnej wartości wyklucza piksel bez lokalnego przeliczania wag.
- Ranking ocenia wszystkie piksele przed agregacją kafli. Kafel bez kwalifikujących się pikseli nie otrzymuje wyniku zero; `max_pixel_id` zachowuje tożsamość maksymalnego piksela.
- Globalny request kończy się `SCOPE_UNAVAILABLE` zamiast cichego ograniczenia do trzech regionów. API nie używa fallbacku na fixture przy awarii danych.
- Analiza jest przypięta do konfiguracji i przechowywana w pamięci procesu przez godzinę, do 16 analiz. Wygasłe ID zwraca `ANALYSIS_EXPIRED`, nieznane `NOT_FOUND`; serwis wymaga jednego workera Uvicorn. Ograniczenie jest jawnie opisane w README i handoffie; wdrożenie wieloworkerowe wymaga współdzielonego magazynu.

### P2 — ścisłość typów requestu

Bezpośrednie sprawdzenie modeli wykazało, że `SearchCriterionRequest.model_validate({"feature_id":"slope_deg","weight":"1"})` przyjmuje tekst jako `1.0`, a `SearchRequest.model_validate(..., "top_k":"2")` przyjmuje tekst jako integer. `contracts/search-request.schema.json` wymaga odpowiednio number i integer. Poprawne requesty działają, więc nie blokuje to obecnego MVP. K-041 wymaga walidacji typów bez niejawnej konwersji oraz testów zgodności ze schematem.

## Sprawdzenia

- `.venv\Scripts\python.exe -m pytest -q` na headzie PR #70 — **84 passed in 4.76s**. Domyślny sandbox blokował utworzenie lokalnej pętli asyncio w Windows; suite uruchomiłam poza tym ograniczeniem. Pierwsza próba `uv run` zakończyła się odmową zapisu do cache interpretera, nie błędem testu.
- Dwa requesty regionalne `top_k=10` odtworzono przez aplikację ASGI; oba zwróciły 200 i wyniki powyżej. Requesty i odpowiedzi search/details przeszły walidację JSON Schema.
- `python tools/check_planning.py` na headzie PR #70 — OK: 164 Markdown, 40 JSON, 81 kart, acykliczne zależności, 5 syntetycznych przypadków.
- `git diff --check 23c57b1331cde3eb0a98a644c81f32d4fab9f495 4f7e296624b7ea1e9889906c23b3b9fedcb94f4a` — czysto.
- GitHub workflow lookup dla headu PR #70 nie zwrócił workflow runs.

## Integracja i ograniczenia

PR #70 jest nadal otwarty. Najnowszy odczyt GitHub zwrócił `mergeable: true`, ale baza PR nadal wskazuje `23c57b1`, starszy od aktualnego `origin/main` `ad829f1`. Zgodnie z przepływem repozytorium Kamil powinien zsynchronizować swoją gałąź z aktualnym `main` przed integracją. Nie zmieniałam jego gałęzi ani nie scalałam PR.

Review potwierdza dwie regionalne analizy rzeczywistych danych o nominalnej rozdzielczości komórki 2 km. Nie waliduje globalnego rankingu, wydajności na zbiorze globalnym ani wdrożenia wieloworkerowego.
