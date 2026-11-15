# K-031 — Review rejestru AI/SI I-012

**Decyzja:** `REQUEST_CHANGES` dla PR #46. Oceniony exact `review_ref`: `17dab257e82e7f3f82baf7df77d1483a076a588f`. Bieżący head PR #46 to `2b6fe1e6cdd19edcde8fd40e460b6b533edc9c3f`; pliki rejestru w tym headzie są identyczne z exact `review_ref`.

## Sprawdzenia

- `python -m json.tool docs/ai-usage.json` na exact ref — JSON jest poprawny.
- `synthetic_data_paths` zawiera dokładnie 14 pozycji; każda ścieżka istnieje w drzewie exact ref.
- Dwa względne linki z Markdown prowadzą do istniejących plików w exact ref.
- `python tools/check_planning.py` — OK: 141 Markdown, 32 JSON, 71 kart, brak cykli zależności, 5 syntetycznych przypadków.
- `git diff --check origin/main...origin/ewelina/I-012-ai-usage-followup` — czysto.
- Na aktualnym `origin/main` backend ma tylko `GET /api/v1/health`; nie ma endpointów katalogu/profili/search.
- Rejestr ustala `generated_media: []` i `measurements_generated_by_ai: false`, wskazuje manifesty rzeczywistych próbek i nie przypisuje AI autorstwa pomiarów. Nie znaleziono twierdzenia o NASA endorsement ani o wykonanym submission. Przypadek `design/map-hotspot-concept.svg` jest opisany jako syntetyczny schemat, nie wygenerowane media.

## Zgodność wpisów z bieżącymi kartami i handoffami

| Wpis | Stan w rejestrze I-012 | Stan źródłowy | Ocena |
|---|---|---|---|
| E-005 | K-028 czeka na re-review | K-028 jest `done` i zaakceptował exact `98be49cac38e6d72245a092e7a59bab7c5599424`; E-005 nadal `review`, PR #31 jest otwarty i niezintegrowany | Nieaktualny status. Zmień na „review zaakceptowane, integracja PR #31 nadal oczekuje”. |
| E-021 | K-030 czeka na review | K-030 jest `done` i opublikował `REQUEST_CHANGES`; E-021 jest ponownie `in_progress`. Żądane 781 px nadal dało 782 px i wymaga dokładnego pomiaru albo jawnej zmiany kryterium | Nieaktualny status. Zachowaj ograniczenie 781/782 px i zapisz wynik K-030 oraz stan poprawki. |
| E-004 | K-029 czeka na re-review po K-027 | E-004 ma nowy exact ref `e63ded588f07b9925c54075a31e581d07bfc5fc9`; K-032 jest kolejką `todo` do jego review. K-032 zastępuje stary ref K-029 (`0c4f509...`). Oględziny mapy nadal nie zostały potwierdzone wizualnie | Nieaktualny status i ref. Wskaż K-032 oraz exact `e63ded...`; zachowaj ograniczenie wizualne i health-only API. |
| E-023 | Zatwierdzone review K-004, exact `d9ff76f...` | E-023 jest `done` i zatwierdziło ten exact ref; PR #36 pozostaje otwarty | Zgodne. |
| E-024 | P1 `REQUEST_CHANGES` dla fingerprintu K-005; poprawiony fingerprint nie zatwierdza starego snapshotu | E-024 jest `done`; K-005 i PR #44 pozostają `review`/otwarte, a dokładny snapshot `a5dfe3d...` nie został zaakceptowany | Zgodne. |

Wpisy E-005/E-021/E-004 w Markdown oraz zbiorcze pole `review_status` w JSON zachowują stan sprzed późniejszych review i zmian kart. Proszę uaktualnić je wspólnie, pozostawiając poprawne ograniczenia: dane E-004 są testowe i mapa nie została tu wizualnie potwierdzona; backend obsługuje tylko health; E-021 nie ma dokładnego pomiaru 781 px; E-024 P1 nie jest akceptacją K-005.

## Poprawki wymagane przed ponownym odbiorem

Ewelina: zaktualizować `docs/AI_USAGE.md`, `docs/ai-usage.json` oraz kartę I-012 do obecnych statusów i exact refów, następnie zsynchronizować gałąź z najnowszym `origin/main`, opublikować nowy SHA i poprosić o re-review. PR #46 jest obecnie otwarty, ma head `2b6fe1e...` i `mergeable: false`; nie należy oznaczać I-012 jako `done` przed poprawionym disclosure i jego integracją.
