# I-012 — korekta po K-038

> Historyczny snapshot sprzed K-040 i świeżego render review E-021. Bieżący stan oraz poprawki po K-040 są w [handoffie I-012/K-040](I-012-K-040-revision.md).

Data: 2026-11-15

Właścicielka: Ewelina

Źródłowy review: K-038 `REQUEST_CHANGES`, review `5910427350`, exact source `ca1645d21f432810009b81ed23a9e2cab8afd662`, oceniony head PR #46 `03f6dbda23812df66a0bb5cd7359b7c606fa8324`.

## Korekty disclosure

- E-021: karta ma `in_progress`, a PR #35 head `dbf341ce44f85ada6b2bf6770d2751740361da37`. K-037 pozostawiło P1 dla aktualnych pomiarów 320/375/390/780/782/1150/1151 px, inspekcji przycięć/nakładania, fokusu 320 px oraz zrzutów lub odtwarzalnego dowodu. Historyczne 782 px nie dowodzi bieżącego renderu. PR #35 bazuje teraz na `origin/main` `5273ca1008aa87c339fb6ef864d80ffe307c893c` i GitHub zgłasza `mergeable: true`; po tej synchronizacji testy 40/40 i build/typecheck przechodzą, ale nowych dowodów renderu nadal brak.
- K-005: PR #44 scalono jako `1fa00555a00f695afa947abd205104000d819f4a`, a karta w `origin/main` ma teraz `status: done` (commit statusu `25b10663baa984137a7c5e9effc8084188a9a2bb`). E-026 zatwierdziło metadata correction ref `d3b880cacbbdf339d078a2fbedbe8fd373db7bef` (review `5910439313`), a PR opisuje wymuszony rebuild `--force`. Disclosure opisuje zarówno integrację, jak i bieżący status karty.
- E-019: E-022 opublikowało APPROVED dla syntetycznego zakresu w raporcie PR #34; raport PR #34 i implementacyjny PR #28 pozostają otwarte, więc E-019 nie jest oznaczone jako zintegrowane.
- I-012: po K-038 `REQUEST_CHANGES` karta wróciła do `in_progress`; rezerwację `tasks(I-012/K-040): IN PROGRESS` potwierdzono w `origin/main` w `4261b3f3bbc25dd033c4ed6cdcae9549526b7963`. Nowe zadanie K-040 sprawdzi disclosure po korekcie.

## Zachowane granice

Centralny JSON nadal ma 14 syntetycznych ścieżek; top-level `is_synthetic: true` występuje w 12/14, a `ai_assisted: true` w 1/14. Brak per-file flagi nie usuwa fixture'u z centralnego wykazu. Nie zmieniono fixture'ów ani danych pomiarowych. `generated_media` pozostaje puste, `measurements_generated_by_ai` jest `false`, a backend nadal udostępnia tylko `GET /api/v1/health`. To disclosure i kontrola kart, nie walidacja aplikacji, wizualny odbiór mapy, globalny ranking ani formalne zgłoszenie.

## Sprawdzenie i przekazanie

Treść poprzedniego snapshotu jest pod exact commitem `69963e0d42cbed78aba16af9a16c30711f06d127` w PR #46. Po synchronizacji E-021 do headu `dbf341ce44f85ada6b2bf6770d2751740361da37` i main `5273ca1008aa87c339fb6ef864d80ffe307c893c` disclosure ponownie zarezerwowano do korekty osobnym commitem `383d55f26e932da1ee72d5d801a9bd56c4c6581f`. Karta K-040 nadal ma `review_ref: pending` i stary punkt o K-005; Kamil powinien odświeżyć własną kartę przed review. Kontrole nowej korekty przeszły: planning check (164 Markdown, 40 JSON, 79 kart, 5 synthetic cases), JSON parse, fixture audit (14/14 paths, 12/14 `is_synthetic`, 1/14 `ai_assisted`) i `git diff --check`.

I-012 pozostaje otwarte do czasu akceptacji nowego exact refu przez K-040 i integracji disclosure. K-040 porówna opublikowany correction ref z bieżącym headem PR #46 po aktualizacji własnego `review_ref` i warunku startu.
