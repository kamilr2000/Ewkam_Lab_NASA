# Handoff I-012 — poprawki po K-036

- Od: Ewelina, `codex-ewelina-i012-k036-correction`
- Do: Kamil
- Data: 2026-11-15
- Zadanie / PR: I-012 / [PR #46](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46)
- Poprzedni exact disclosure ref: `0f9bc969eb9b988ea5b2ad67240e3364c0ec3924`
- Poprzedni head PR oceniony przez K-036: `32e027ce222670d52e96815e39fff3f4c3cdf64e`
- Wynik K-036: `REQUEST_CHANGES`, review `5910234096`; źródłowy raport: [K-036](K-036-review-I-012.md)

## Zmiany

- Poprawiono otwierające twierdzenie o oznaczeniach fixture'ów. Centralne `synthetic_data_paths` obejmuje wszystkie 14 plików; top-level `is_synthetic: true` występuje w 12/14, a top-level `ai_assisted: true` w 1/14. Dwoma ścieżkami bez top-level `is_synthetic` są `health-ready-no-dataset.json` i `search-request-synthetic.json`; jedyny top-level `ai_assisted: true` ma `hotspot-regression.json`. Brak flagi per-file nie zmienia centralnego rejestru.
- Dodano ujawnienie pracy K-004: Codex pomógł przypiąć 14 publicznych wejść NASA PDS/PGDA, przygotować downloader/builder oraz dokumentację. E-023 zatwierdziła exact `d9ff76f7d5f3cfd18a55b82def271b9cc35030dc`, a PR #36 scalono do `origin/main` jako `4301744bddab0bfc56b6dc8c7908d4f8849df890`. Kod obliczył wartości z oryginalnych rastrów; AI nie wygenerowało ani nie edytowało pomiarów. Manifests: `data/manifests/k004-source-files.json` i `data/manifests/k004-planetary-profiles.json`.
- Odświeżono statusy w rejestrze: E-005 jest `done`; PR #37 jest scalony jako `f316db24d183bbbe2a9de05307fcb5b8fa446503`, lecz E-004 pozostaje `review` bez wizualnego potwierdzenia mapy. E-021 ma `review`, a K-037 przegląda poprawkę; poprzednie 782 px pochodzi z wcześniejszego snapshotu, więc aktualnego renderu nie uznajemy za sprawdzony. K-005 pozostaje `review` z otwartym PR #44 i P1 dla exact fingerprintu. I-012 jest ponownie `in_progress` po K-036.
- Zbiorczy JSON zachowuje `generated_media: []`, `measurements_generated_by_ai: false`, 14 centralnych ścieżek oraz health-only API. Dodano manifesty źródeł i wyników profili K-004.

## Sprawdzenia

Sprawdzenia: `python tools/check_planning.py` — OK (155 Markdown, 36 JSON, 75 kart, zależności acykliczne, 5 przypadków syntetycznych); `python -m json.tool docs/ai-usage.json` — poprawny JSON; 14/14 centralnych ścieżek istnieje, z 12/14 top-level `is_synthetic: true` i 1/14 `ai_assisted: true`; `git diff --check` — bez błędów treści (Git zgłasza jedynie normalizację CRLF/LF w JSON).

Nie zmieniano plików `contracts/fixtures/`, które należą do Kamila. Nie uruchamiano aplikacji ani ponownej analizy naukowej; w tym zadaniu poprawiono dokumentację disclosure. Nie wykonano formalnego submission NASA.
