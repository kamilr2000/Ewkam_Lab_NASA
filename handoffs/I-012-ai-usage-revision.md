# Przekazanie: I-012 — aktualizacja disclosure po scaleniu E-005

- Od: Ewelina, `codex-ewelina-i012-k034-correction`
- Do: Kamil
- Data: 2026-11-15
- Zadanie / PR / exact commit rejestru: I-012 / [PR #46](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46) / `0f9bc969eb9b988ea5b2ad67240e3364c0ec3924`
- Repozytorium / gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/I-012-ai-usage-followup`
- Poprzedni review: K-034 zgłosiło `REQUEST_CHANGES` dla exact `7481397528d190bd4f7be69e925cc43848bcb034` po scaleniu PR #31.

## Korekta

- E-005: K-028 zaakceptowało exact code ref `98be49cac38e6d72245a092e7a59bab7c5599424`; PR #31 scalono do `origin/main` merge commitem `00561365c7d42cd7ffd4083968adb5c386e81aca`, a karta E-005 ma `done`.
- `docs/AI_USAGE.md` i `docs/ai-usage.json` teraz podają ten stan oraz zachowują ograniczenie, że API udostępnia tylko `GET /api/v1/health`; live catalog/profile/search nie zostały przetestowane na rzeczywistych danych.
- Zachowano statusy i ograniczenia E-004, E-021, E-023/E-024 oraz E-019/E-022. Rejestr nadal ma 14 syntetycznych ścieżek, `generated_media: []` i `measurements_generated_by_ai: false`.
- Nie zmieniono twierdzeń ani manifestów K-002/K-017. Rejestr nie przypisuje Codex pomiarów, endorsement NASA ani wykonanego submission.

K-034 ustaliło, że poprzedni exact snapshot był historycznie poprawny przy utworzeniu, lecz PR #31 zintegrowano później. Korekta aktualizuje ten nowy stan; PR #46 nadal jest otwarty, a I-012 pozostaje `in_progress` do re-review i integracji.

## Sprawdzenia

- `python tools/check_planning.py` — OK: 149 Markdown, 32 JSON, 73 task cards, acykliczne zależności, 5 syntetycznych przypadków.
- `python -m json.tool docs/ai-usage.json` — poprawny JSON.
- 14/14 `synthetic_data_paths` wskazuje istniejące pliki; `generated_media` puste; `measurements_generated_by_ai` ma wartość `false`.
- `git diff --check` — bez błędów.

To kontrola disclosure i repozytoryjnego planowania, nie re-analiza naukowa ani potwierdzenie działania pełnej aplikacji. Proszę o nowe niezależne review exact `0f9bc969eb9b988ea5b2ad67240e3364c0ec3924` po publikacji K-036 w PR #46.
