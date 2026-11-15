# K-040 — re-review I-012 po K-038

- Recenzent: Kamil / Codex
- Właściciel disclosure: Ewelina
- Dokładny oceniany commit: `3a7a313960a713c168f31caf63eaf83bef097c6e`
- Bieżący head PR #46 podczas review: `5eaf21d92f3e45ac20e6ef02a1e84515fcf57d31`
- PR review: [#46](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46), `REQUEST_CHANGES`, review ID `5910708916`
- K-040 rezerwacja: `7a7ee00` w `origin/main`
- Wynik: **wymagane poprawki w istniejącym I-012**; samo review K-040 jest zakończone.

## Co zweryfikowano

I-012 ma `status: review` w `origin/main`, a karta przypina exact ref `3a7a313960a713c168f31caf63eaf83bef097c6e`. Aktualny PR #46 head `5eaf21d92f3e45ac20e6ef02a1e84515fcf57d31` zawiera ten commit; od exact disclosure refu późniejsze commity synchronizują kartę/status i nie zmieniają dokumentów AI/JSON.

K-005 jest `done`. PR #44 scalono jako `1fa00555a00f695afa947abd205104000d819f4a`; E-026 zatwierdziło korektę fingerprintu `d3b880cacbbdf339d078a2fbedbe8fd373db7bef` (review `5910439313`). Karta K-005 została oznaczona `done` w commitcie `25b10663baa984137a7c5e9effc8084188a9a2bb`.

E-021 nadal ma `status: in_progress` na PR #35 head `dbf341ce44f85ada6b2bf6770d2751740361da37`. Jej aktualny render, wymagane pomiary siedmiu viewportów, oględziny przycięć/nakładania i fokus przy 320 px nie zostały potwierdzone. K-039 nadal czeka na te dowody. PR #35 zachował bazę `5273ca1008aa87c339fb6ef864d80ffe307c893c`; porównanie z aktualnym main `7a7ee0003dff557f75785f092966825fbccd40e1` wykazało, że PR jest 5 commitów za bazą, a GitHub podaje `mergeable: false`.

## Wymagane poprawki

1. **P1 — błędny status commit K-005.** `docs/AI_USAGE.md`, `docs/ai-usage.json` i `handoffs/I-012-K-038-revision.md` opisują `7deddad9f992ef69c13248195747349a283ce54b` jako commit, który oznaczył K-005 jako `done`. To commit rezerwacji K-007. Użyj `25b10663baa984137a7c5e9effc8084188a9a2bb` albo usuń przypisanie statusu do SHA.
2. **P1 — nieaktualna mergeability PR #35.** Markdown, JSON i handoff mówią `mergeable: true` po syncu PR do `5273ca1`. Main od tego czasu przesunął się do `7a7ee00`, PR jest 5 commitów za bazą, a GitHub zgłasza `mergeable: false`. Zaktualizuj stan i wyraźnie oznacz snapshot historyczny albo usuń zmienną deklarację `mergeable`; zachowaj `E-021: in_progress` i informację, że wizualne dowody nadal są otwarte.
3. **P2 — nieaktualny opis PR #46.** Aktualny opis nadal mówi, że K-040 ma `review_ref: pending` i stary wymóg K-005. K-040 jest zarezerwowane z exact refem i poprawnym stanem K-005; odśwież opis przed integracją I-012.

Właścicielem korekt jest Ewelina w istniejącym I-012. Nie utworzono zduplikowanego zadania. Po korekcie należy opublikować nowy exact ref i poprosić o re-review. Nie zmieniać 14 ścieżek syntetycznych ani flag, `generated_media: []`, `measurements_generated_by_ai: false`, prawdziwego statusu health-only na `origin/main` ani human-only granicy submission.

## Sprawdzenia

- JSON dokładnego PR headu poprawnie parsuje się przez `json.loads`.
- Wszystkie 14 syntetycznych ścieżek istnieje w dokładnym headzie; top-level `is_synthetic: true` występuje 12/14 razy, a `ai_assisted: true` 1/14.
- `generated_media` pozostaje puste, a `measurements_generated_by_ai` ma wartość `false`.
- Planning check `origin/main` po rezerwacji K-040 i przed publikacją tego raportu: 163 Markdown, 40 JSON, 81 kart, acykliczne zależności, 5 syntetycznych przypadków. Bieżący check gałęzi raportu: 164 Markdown, 40 JSON, 81 kart, acykliczne zależności, 5 syntetycznych przypadków. Aktualny opis PR #46 podaje również zaliczenie planning check dla swojego headu.
- `git show --check` exact disclosure ref i `git diff --check` przechodzą.

To review dokumentacji i statusów. Nie odtwarza metryk naukowych ani nie zastępuje przeglądu aktualnego renderu E-021.
