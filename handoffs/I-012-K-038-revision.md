# I-012 — korekta po K-038

Data: 2026-11-15

Właścicielka: Ewelina

Źródłowy review: K-038 `REQUEST_CHANGES`, review `5910427350`, exact source `ca1645d21f432810009b81ed23a9e2cab8afd662`, oceniony head PR #46 `03f6dbda23812df66a0bb5cd7359b7c606fa8324`.

## Korekty disclosure

- E-021: karta ma `in_progress`, a PR #35 head `c9c4a43caf26aea60d8811d3b49fdd56b4d7d797`. K-037 pozostawiło P1 dla aktualnych pomiarów 320/375/390/780/782/1150/1151 px, inspekcji przycięć/nakładania, fokusu 320 px oraz zrzutów lub odtwarzalnego dowodu. Historyczne 782 px nie dowodzi bieżącego renderu. PR #35 było zsynchronizowane do `2e56c5c`, lecz main później przesunął się do `4261b3f`; PR obecnie raportuje `mergeable: false`.
- K-005: status to `review`. E-026 zatwierdziło poprawiony metadata ref `d3b880cacbbdf339d078a2fbedbe8fd373db7bef` (review `5910439313`); PR #44 head `3a07fc27fdad44472bcf61b1bc1347ae5b02fff6` pozostaje otwarty i niezintegrowany oraz wymaga synchronizacji. Fingerprint i zachowane CSV zostały niezależnie sprawdzone. Opis PR nadal twierdzi, że build użył ponownie checkpointów, podczas gdy poprawiony handoff dokumentuje wymuszone `--force`; jest to nieblokujące P2.
- E-019: E-022 opublikowało APPROVED dla syntetycznego zakresu w raporcie PR #34; raport PR #34 i implementacyjny PR #28 pozostają otwarte, więc E-019 nie jest oznaczone jako zintegrowane.
- I-012: po K-038 `REQUEST_CHANGES` karta wróciła do `in_progress`; rezerwację `tasks(I-012/K-040): IN PROGRESS` potwierdzono w `origin/main` w `4261b3f3bbc25dd033c4ed6cdcae9549526b7963`. Nowe zadanie K-040 sprawdzi disclosure po korekcie.

## Zachowane granice

Centralny JSON nadal ma 14 syntetycznych ścieżek; top-level `is_synthetic: true` występuje w 12/14, a `ai_assisted: true` w 1/14. Brak per-file flagi nie usuwa fixture'u z centralnego wykazu. Nie zmieniono fixture'ów ani danych pomiarowych. `generated_media` pozostaje puste, `measurements_generated_by_ai` jest `false`, a backend nadal udostępnia tylko `GET /api/v1/health`. To disclosure i kontrola kart, nie walidacja aplikacji, wizualny odbiór mapy, globalny ranking ani formalne zgłoszenie.

## Sprawdzenie i przekazanie

Treść korekty jest dostępna pod exact commitem `0785708a8fee9504ae74339ff4d572c69570a3d9` w PR #46. `python tools/check_planning.py` — OK (163 Markdown, 36 JSON, 79 kart); `python -m json.tool docs/ai-usage.json` — poprawny; audyt fixture'ów — 14/14 ścieżek istnieje, flagi top-level 12/14 i 1/14; `git diff --check` — czysto.

I-012 pozostaje otwarte do czasu akceptacji exact refu przez K-040 i integracji disclosure. K-040 porówna `0785708a8fee9504ae74339ff4d572c69570a3d9` z bieżącym headem PR #46 po aktualizacji statusu karty i synchronizacji z main.
