# Przekazanie: I-012 — uzupełnienie rejestru AI/SI

- Od: Ewelina, `codex-ewelina-i012-ai-usage-followup`
- Do: Kamil
- Data: 2026-11-15
- Zadanie / PR / commit: I-012 / [PR #46](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46) / `17dab257e82e7f3f82baf7df77d1483a076a588f`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/I-012-ai-usage-followup`
- Zakres zmiany: `docs/AI_USAGE.md`, `docs/ai-usage.json`
- Status: przekazane do niezależnego review K-031; PR pozostaje otwarty, rejestr nie jest jeszcze w `origin/main`.

## Uzupełnione wpisy

- E-005: wybór cech i datasetu według roli, budowa requestu; 38/38 testów i build, K-028 oczekuje na re-review, API pozostaje health-only.
- E-004: przekazanie FeatureCollection do MapLibre, etykieta zakresu i regresje `number`/`null`; 30/30 testów i build. Widok mapy nie został wizualnie potwierdzony w tym przebiegu z powodu blokady URL Computer Use; build zgłasza chunk 1,350.80 kB minified / 375.97 kB gzip.
- E-021: poprawa czytelności i udokumentowane pomiary kontrastu/układu; minimalny wynik dodatkowych par 4.68:1. Żądany viewport 781 px zaraportował 782 px, klasycznego scrollbara nie wymuszono; K-030 oczekuje na review.
- E-023: zakończony raport review K-004 dla Jezero i księżycowego obszaru 80–90°S; reprodukcja dotyczy dwóch regionalnych profili, nie rankingu globalnego.
- E-024: zakończony raport review K-005, który dla exact `a5dfe3d892235d31938dcdd56bdcc17a66e0f167` zgłosił P1 `REQUEST_CHANGES` z powodu fingerprintu kodu. Wymuszona przebudowa skorygowała fingerprint bez zmiany CSV; oceniony exact snapshot nie jest zatwierdzony, a poprawiony zakres wymaga re-review.

JSON zachowuje 14 syntetycznych ścieżek i `generated_media: []`. Rejestr nie przypisuje Codex wygenerowania lub edycji pomiarów naukowych, NASA endorsement ani formalnego submission. Istniejące wpisy o K-002/K-017 i źródłach danych nie zostały zmienione.

## Sprawdzenia

- `python tools/check_planning.py` — OK (133 pliki Markdown, 32 JSON, 66 task cards, graf zależności bez cykli, 5 przypadków syntetycznych na stanie gałęzi implementacyjnej).
- `python -m json.tool docs/ai-usage.json` — poprawny JSON.
- Wszystkie 14 wartości `synthetic_data_paths` nadal wskazuje istniejące pliki fixture.
- `git diff --check` — bez błędów.

Sprawdzenia nie stanowią re-analizy pomiarów ani potwierdzenia działającej aplikacji. K-031 powinien niezależnie sprawdzić opisane fakty na dokładnym `review_ref`. Po akceptacji i integracji PR #46 Ewelina może zmienić I-012 na `done`.
