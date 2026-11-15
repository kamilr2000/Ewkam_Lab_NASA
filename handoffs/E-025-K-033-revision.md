# Przekazanie: E-025 — poprawki po K-033

- Od: Ewelina, `codex-ewelina-e025-k033-revision`
- Do: Kamil
- Data: 2026-11-15
- Zadanie / PR / exact matrix commit: E-025 / [PR #50](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/50) / `d755352240f003b7609104f500355c14df065251`
- Repozytorium / gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-025-submission-evidence-matrix`
- Zakres: `submission/evidence-matrix.md`; re-review K-033 `REQUEST_CHANGES` dla `e44614187c19eb9f8898115cf4512de2bc9078b9`.

## Zmiany

- Odświeżono stany produktu po E-005: K-028 zaakceptowało exact `98be49cac38e6d72245a092e7a59bab7c5599424`, a PR #31 został scalony do `origin/main` merge commitem `00561365c7d42cd7ffd4083968adb5c386e81aca`. E-005 jest `done`; UI controls są zintegrowane, lecz live API nadal udostępnia tylko health.
- E-004 nadal jest w otwartym PR #37, K-032 zaakceptowało exact `e63ded588f07b9925c54075a31e581d07bfc5fc9`, a render mapy nie został wizualnie potwierdzony. E-021 nadal jest `in_progress`; K-030 zwróciło `REQUEST_CHANGES`, żądane 781 px dało 782 px, a exact punkt pozostaje nierozwiązany.
- AI/SI row rozróżnia zintegrowany rejestr I-011 od korekt w PR #46. K-034 rozpoczęło review exact `7481397528d190bd4f7be69e925cc43848bcb034`; ten snapshot powstał przed merge PR #31 i nadal mówi, że E-005 nie jest zintegrowane. To ograniczenie jawnie zapisano; rejestr wymaga aktualizacji przed użyciem w pakiecie końcowym.
- Dodano pola S03 dla języka; hostowania i rozmiaru obrazów; statusu członków i ograniczeń wieku; zasad AI/SI dla obrazów, wideo, audio, kodu i danych; oraz lokalnego okna Universal Event i wcześniejszego pitchu.
- Zapisano potwierdzone przez Kamila: Team Owner to Kamil, wydarzenie to Universal Event, a oboje członkowie są zarejestrowani i zaakceptowani w tym evencie. Tytuł projektu w rejestracji pozostaje niepotwierdzony. Deadline i strefa wymagają sprawdzenia przez Kamila; nie wywiedziono miejsca zamieszkania ze środowiska.

Macierz pozostaje materiałem wewnętrznym, nie do wysłania jury. Nie dodano publicznego demo, wyników globalnych, endorsement NASA ani potwierdzenia submission. I-006 nadal wymaga osobistego działania Kamila lub Eweliny.

## Sprawdzenia

- `python tools/check_planning.py` — OK: 148 Markdown, 32 JSON, 72 karty, acykliczny graf, 5 syntetycznych przypadków.
- W macierzy 18/18 lokalnych linków wskazuje istniejące pliki; wszystkie 13 wierszy danych mają cztery kolumny.
- `git diff --check` — bez błędów.

Sprawdzenia nie potwierdzają aplikacji, naukowych wyników, event deadline ani publicznej dostępności materiałów. Proszę o niezależny re-review K-035 na exact commit `d755352240f003b7609104f500355c14df065251` w PR #50.
