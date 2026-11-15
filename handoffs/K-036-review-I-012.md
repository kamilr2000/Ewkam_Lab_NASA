# Przekazanie: K-036 — re-review rejestru AI/SI I-012

- Od: Kamil, `codex-kamil-k036-review-i012`
- Do: Ewelina, właścicielka I-012
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / exact disclosure commit: K-036 / [PR #46](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46) / `0f9bc969eb9b988ea5b2ad67240e3364c0ec3924`
- Oceniony aktualny head PR #46: `32e027ce222670d52e96815e39fff3f4c3cdf64e` (otwarty, niezintegrowany)
- Zdalne repo i gałąź pracy: `kamilr2000/Ewkam_Lab_NASA`, `kamil/K-036-review-I012`
- Rezerwacja: PR #62, squash `fa46438c60ff80ef70b1586d08621669101ca56c`.
- Wynik: `REQUEST_CHANGES` na PR #46, GitHub review `5910234096`.
- Publikacja raportu i zamknięcia K-036: PR do `main` z gałęzi pracy K-036.

## Zakres i dowody

Sprawdziłem exact commit `0f9bc969eb9b988ea5b2ad67240e3364c0ec3924` oraz bieżący head PR #46. Exact commit zmienia tylko `docs/AI_USAGE.md` i `docs/ai-usage.json`. Na bieżącym headzie pliki disclosure pozostają bez zmian, natomiast karta I-012 jest w `review` i zaktualizowany handoff nadal mówi, że I-012 pozostaje `in_progress`.

E-005 jest opisane poprawnie: K-028 zaakceptowało exact code ref `98be49cac38e6d72245a092e7a59bab7c5599424`, PR #31 scalono jako `00561365c7d42cd7ffd4083968adb5c386e81aca`, a E-005 ma `done`. W `apps/api` jedyną trasą pozostaje GET `/api/v1/health`; disclosure nie twierdzi, że live catalog/profile/search działa na danych rzeczywistych.

Pozostałe sprawdzone stany zgadzają się z bieżącymi kartami i PR: E-004 jest `review` i PR #37 otwarty bez wizualnego potwierdzenia; E-021 jest `in_progress`, PR #35 otwarty, a dokładne 781 px niezweryfikowane; E-023 jest zakończonym review, lecz PR #36 nadal otwarty; E-024 jest zakończonym raportem review dla K-005 ze zgłoszonym P1, a PR #44 pozostaje otwarty i exact K-005 nie jest zaakceptowany; E-019 jest `review`, E-022 `in_progress`, PR #28 otwarty.

## Wymagane poprawki

1. **P1 — właściciel Ewelina, karta I-012:** na bieżącym headzie `tasks/I-012.md` ma `status: review`, lecz `docs/ai-usage.json` i `handoffs/I-012-ai-usage-revision.md` mówią, że I-012 nadal jest `in_progress`. Dokładny snapshot `0f9bc96` był historycznie w stanie `in_progress`, ale obecny PR head zawiera już status `review`. Uaktualnij bieżące sformułowania albo jawnie oznacz je jako opis historycznego snapshotu i opublikuj nowy exact ref.
2. **P1 — właściciel Ewelina dla disclosure; Kamil dla ewentualnych zmian w `contracts/fixtures/`:** wstęp `docs/AI_USAGE.md` stwierdza, że fixture'y mają zarówno `is_synthetic: true`, jak i `ai_assisted: true`. W exact tree wszystkie 14 wpisów `synthetic_data_paths` istnieje, ale tylko 12 plików ma na poziomie głównym JSON `is_synthetic: true`, a tylko 1 ma na tym poziomie `ai_assisted: true`. Flaga `is_synthetic` nie występuje w `contracts/fixtures/health-ready-no-dataset.json` ani `contracts/fixtures/search-request-synthetic.json`. Popraw disclosure, aby odpowiadał rzeczywistym metadanym plików i nie sugerował nieobecnych per-file flag; zachowaj centralną listę 14 syntetycznych ścieżek. Jeśli potrzebne są dodatkowe metadane w fixture'ach, uzgodnij zmianę z Kamilem jako właścicielem `contracts/fixtures/`.

Nie stwierdziłem błędu w twierdzeniu, że `generated_media` jest puste, `measurements_generated_by_ai` ma wartość `false`, a manifest wymienia 14 syntetycznych ścieżek. Nie zmieniano manifestów ani raportów K-002/K-017; exact diff obejmuje tylko dwa disclosure files. Nie wykonano ponownej analizy naukowej ani uruchomienia aplikacji.

## Sprawdzenia

- `python tools/check_planning.py` w archiwum exact tree — OK: 148 Markdown, 32 JSON, 73 karty, acykliczne zależności, 5 przypadków syntetycznych.
- `python -m json.tool docs/ai-usage.json` na exact tree — poprawny JSON.
- 14/14 ścieżek z `synthetic_data_paths` istnieje w exact tree.
- Inspekcja pól na poziomie głównym exact fixtures: `is_synthetic: true` w 12/14 plików, `ai_assisted: true` w 1/14 plików.
- `git diff --check 0f9bc96^ 0f9bc96` — czysty; exact commit modyfikuje wyłącznie `docs/AI_USAGE.md` i `docs/ai-usage.json`.
- Karta I-012 i handoff na PR headzie sprawdzone względem current disclosure; sprawdzono źródłowe karty i stany PR #31/#35/#36/#37/#44/#28.

Review dotyczy disclosure i kart. Nie potwierdza działania pełnej aplikacji, globalnego rastra ani rankingu, nie odtwarza pomiarów i nie wykonuje formalnego submission NASA.
