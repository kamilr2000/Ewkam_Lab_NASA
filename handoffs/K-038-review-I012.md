# K-038 — wynik re-review disclosure I-012

- Od: Kamil, `codex-kamil-k038-review-i012`
- Do: Ewelina
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: K-038 / I-012 / PR #46; exact source `ca1645d21f432810009b81ed23a9e2cab8afd662`, oceniony head `03f6dbda23812df66a0bb5cd7359b7c606fa8324`
- Zdalne repo i gałąź: `origin`, `kamil/K-038-review-I012`
- Wysłane SHA i URL PR: raport K-038 w commicie `083ba6e574e52bba697f94b0cc7a107e742d4e5c`, [integracyjny PR #68](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/68); wynik review: [PR #46, review #5910427350](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46#pullrequestreview-5910427350).
- Rezerwacja w `origin/main`: potwierdzona; `tasks(K-038): IN PROGRESS` — `2e56c5c9733ffde666955e62ee77448f0883c7fc`.
- Lokalne niewysłane zmiany: brak po wysłaniu końcowego headu PR #68.
- Stan: `REQUEST_CHANGES` dla I-012; K-038 spełnia kryteria przeglądu po publikacji raportu.

## Co jest dostępne

Sprawdziłem dokładny ref `ca1645d21f432810009b81ed23a9e2cab8afd662` i bieżący w chwili review head PR #46 `03f6dbda23812df66a0bb5cd7359b7c606fa8324`. Source ref jest przodkiem headu. PR zawiera zsynchronizowaną kartę I-012 ze statusem `review`; oba dokumenty zachowują tę wartość.

Centralna lista w `docs/ai-usage.json` ma 14 unikalnych ścieżek; wszystkie są dostępne w tree każdego z tych refów. Z plików odczytałem 12/14 top-level `is_synthetic: true` i 1/14 `ai_assisted: true`. Dwa pliki bez top-level `is_synthetic` to `contracts/fixtures/health-ready-no-dataset.json` oraz `contracts/fixtures/search-request-synthetic.json`; jedynym plikiem z `ai_assisted: true` jest `contracts/fixtures/hotspot-regression.json`. Centralny wykaz pozostaje autorytatywny. `generated_media` jest puste, a `measurements_generated_by_ai` ma wartość `false`.

Pozostałe twierdzenia porównałem z kartami, review i stanem PR:

- E-005: `done`, K-028 zatwierdziło exact `98be49cac38e6d72245a092e7a59bab7c5599424`, PR #31 jest scalony jako `00561365c7d42cd7ffd4083968adb5c386e81aca`. W kodzie API jedyna trasa to `GET /api/v1/health`; była to inspekcja źródeł, nie test uruchomionej usługi.
- E-004: `review`; PR #37 scalono jako `f316db24d183bbbe2a9de05307fcb5b8fa446503`, K-032 zaakceptowało exact lazy-load ref `e63ded588f07b9925c54075a31e581d07bfc5fc9`. Bieżący render mapy, czytelność poligonów/legendy i pełny widok polarny nie mają potwierdzenia wizualnego.
- E-023: zakończone review K-004 dla `d9ff76f7d5f3cfd18a55b82def271b9cc35030dc`; PR #36 jest scalony jako `4301744bddab0bfc56b6dc8c7908d4f8849df890`. Raport opisuje profile regionalne, nie nową serię pomiarów AI.
- E-024: historyczny `REQUEST_CHANGES` dla K-005 exact `a5dfe3d892235d31938dcdd56bdcc17a66e0f167`; raport review sam nie jest nowymi danymi.
- E-021: K-037 zgłosiło P1 dla świeżych metryk viewportów, oględzin przycięć/nakładania, fokusu przy 320 px i zrzutów. Najnowszy w chwili review PR #35 head to `c9c4a43caf26aea60d8811d3b49fdd56b4d7d797`; jego karta mówi `in_progress`, CSS branch jest już zsynchronizowany z main, lecz renderowe dowody nadal nie ma. K-039 pozostaje `todo`.
- K-005: obecnie `review`, exact poprawka `d3b880cacbbdf339d078a2fbedbe8fd373db7bef`; kodowy fingerprint w raporcie i trzech manifestach to `56543c206661c3158999fd442f13a3ebc56e695333da8b2ad01b1e19d8d63829`. PR #44 jest otwarty. Po opublikowaniu mojego review E-026 zostało zarezerwowane i ma `in_progress` w `origin/main` `8fe4576a513ca4d2f273dc40532ef6bd1cb34bee`; przed tą aktualizacją miało `todo`. K-005 nie ma jeszcze wyniku E-026.

### Wymagane poprawki — P1

1. `docs/AI_USAGE.md`, `docs/ai-usage.json`, bieżący handoff K-036 oraz opis PR #46 nadal mówią, że K-005 jest `in_progress` i że poprawka fingerprintu dopiero czeka na wdrożenie. To już nie odpowiada `origin/main`: poprawka jest opublikowana, K-005 ma `review`, a E-026 sprawdza ją obecnie. Opisz stan po poprawce i oczekujący wynik niezależnego review; nie przedstawiaj K-005 jako zaakceptowanego.
2. Te same bieżące disclosure mówią, że E-021 pozostaje w `review` i PR #35 wymaga synchronizacji. Karta E-021 ma `in_progress`, a head PR #35 `c9c4a43...` zawiera synchronizację i rozwiązanie konfliktu CSS. Nadal otwarte są tylko renderowe dowody wymagane przez K-037; zachowaj je jako ograniczenie.
3. PR #46 ma bazowy SHA `f956079ee01f1e54e457e195957fed5f441b1ac9`, starszy od aktualnego `origin/main` `8fe4576a513ca4d2f273dc40532ef6bd1cb34bee`. GitHub raportuje go jako otwarty i mergeable, ale przed integracją zsynchronizuj branch, zachowując rezerwację K-038 i publikując nowy exact ref.

Wynik `REQUEST_CHANGES` wraz z dwoma komentarzami liniowymi opublikowałem na exact headzie `03f6dbda23812df66a0bb5cd7359b7c606fa8324` w [PR #46](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46#pullrequestreview-5910427350). Raport nie wymaga ponownej oceny samego K-038. Właścicielka I-012 może poprawić disclosure na tej samej karcie; po zmianie należy ocenić zmienione twierdzenia na nowym exact refie.

## Jak odtworzyć

1. Pobierz `ewelina/I-012-ai-usage-followup` i sprawdź, że `ca1645d...` jest przodkiem headu PR #46 `03f6dbd...`.
2. Z `docs/ai-usage.json` na każdym refie odczytaj 14 `synthetic_data_paths`; parsuj każdy fixture jako JSON i zlicz wyłącznie top-level wartości równe `true`.
3. W tym samym tree wykonaj `python tools/check_planning.py`, `python -m json.tool docs/ai-usage.json` oraz `git diff --check f956079ee01f1e54e457e195957fed5f441b1ac9 03f6dbda23812df66a0bb5cd7359b7c606fa8324`.
4. Porównaj statusy na aktualnym `origin/main`: I-012, K-005, E-021, E-004, E-005, E-023, E-024 i E-026. Integracje PR potwierdź na kartach i w GitHub.

## Sprawdzenia

- Dokładne source/head i historia PR #46: potwierdzone; source jest przodkiem headu.
- Zrzut tree PR #46 do tymczasowego katalogu: `python tools/check_planning.py` — OK, 156 Markdown, 36 JSON, 76 kart, acyclic dependencies, 5 synthetic cases.
- `python -m json.tool docs/ai-usage.json` na tree PR #46 — poprawny JSON.
- Fixture audit na obu refach — 14/14 unikalnych ścieżek istnieje; liczniki flag 12/14 i 1/14.
- `git diff --check` PR #46 względem jego bazowego SHA — czysto.
- API — sprawdzono deklaracje tras w źródle; nie uruchamiano usługi. Nie sprawdzano wizualnie webapp ani rankingu danych.

## Ograniczenia i potrzebne działania

- Ewelina: popraw bieżące statusy/warunki K-005 i E-021 w obu rejestrach, bieżącym handoffie oraz opisie PR #46; zsynchronizuj branch z `origin/main` i opublikuj nowy exact ref.
- E-026 prowadzi niezależny review K-005 na exact `d3b880...`; K-005 pozostaje `review` do wyniku E-026 i integracji.
- E-021 pozostaje bez świeżych metryk/render evidence i potwierdzenia fokusu; K-039 jest niegotowe, dopóki E-021 nie opublikuje tych materiałów i nie ustawi `review`.
- Nie wykonano analizy pomiarów, testu działającego API, wizualnego odbioru mapy ani formalnego submission NASA. Nie znaleziono twierdzeń o wygenerowanych pomiarach, wygenerowanych mediach, endorsement ani wysłanym zgłoszeniu.
