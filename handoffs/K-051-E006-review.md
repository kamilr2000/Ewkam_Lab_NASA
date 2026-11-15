# K-051 — exact-ref review E-006

Data: 2026-11-15
Decyzja: **APPROVE exact code scope; merge po synchronizacji task-doc conflicts**

## Wersja i scope

- E-006 PR: [#96](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/96)
- Reviewed head: `c0df63a50f196ef89793ec1345d3c5ca3636d18c` (zgodny z `review_ref` i bieżącym PR head).
- PR base: `e1f534888ddb07c8c90c2c8f4c80d15ac662082b`.
- `origin/main` przy kontroli: `a364f40e7261e2ad6f1d4949b98abf949ecceb7b`.
- Compare base → current main: tylko task docs/index (`tasks/E-006.md`, `E-010.md`, `E-034.md`, `E-035.md`, `K-051.md`, `K-052.md`, `K-053.md`, `tasks/README.md`); bez zmian `apps/web`, `apps/api`, `contracts` ani `data` objętych review.
- GitHub oznacza #96 jako open i non-mergeable. To wymaga synchronizacji branchu i rozwiązania dokumentacyjnego konfliktu przed merge, ale nie zmienia ocenionego kodu.

## Kontrole

- Przejrzano wszystkie 10 zmienionych plików. Live region wybiera dokładnie przypięty dataset version, a request i odpowiedź wiążą body/profile, dataset, region/scope, aktywne criteria, result mode i wymagany dystans.
- Live error nie przełącza się po cichu na fixtures. Synthetic mode pozostaje oznaczony.
- Zmiany profilu/body/regionu/kryteriów/trybu czyszczą wynik i unieważniają żądanie w toku. Odpowiedź z poprzedniego `analysis_id` nie staje się nowym wynikiem.
- Ranking pojedynczych pikseli pozostaje odrębny od representative pixels w `distinct_areas`. Dystans jest jawny i walidowany; nie widać filtrowania Top 10 przez średnią obszaru.
- Null measurements są wyświetlane jako niedostępne z powodem, a nie jako zero. UI pokazuje jednostki, skalę, zakres odniesienia, tolerancję, normalized weight i source IDs.
- Ranking, warstwa mapy i szczegóły piksela korzystają z odpowiedzi jednego `analysis_id`; markery Top 10 pozostają osobną listą komórek, niezależnie od agregacji komórek mapy.

## Dowody

- `npm test --prefix apps/web` na exact ref: **47 passed**.
- `npm run build --prefix apps/web` na exact ref: **TypeScript i produkcyjny build passed**. Chunk MapLibre ma 1,085.76 kB po minifikacji; odłożone jako nieblokujący follow-up.
- `.venv\Scripts\python.exe -m pytest apps/api/tests/test_api_contract.py -q` na K-007 API: **7 passed**. Testy odtwarzają profile Mars/Atacama i Moon/Hawaii, regionalny ranking i distinct-area behavior na realnych pakietach.
- Ewelina opisała browser run dla obu profili przez lokalny same-origin proxy w PR #96. Nie powtarzałem tego browser run samodzielnie; osobny origin/CORS pozostaje w K-052.
- Review APPROVE opublikowane na PR #96, review ID `5912486971`, anchored na `c0df63a50f196ef89793ec1345d3c5ca3636d18c`.

## Follow-up przed integracją

Ewelina: zsynchronizuj branch PR #96 z bieżącym `origin/main` i rozwiąż konflikty kart/indeksu, zachowując kod exact-review. Jeśli zmieni się kod `apps/web`, zaktualizuj ref i poproś o re-review. Rozmiar chunku MapLibre jest optymalizacją P1.

Nie zweryfikowano publicznego wdrożenia ani deployment CORS. OSM basemap jest oddzielnym zadaniem E-035. Ta decyzja dotyczy wyłącznie sprawdzonego code scope; nie oznacza merge PR #96 ani ukończenia demo.
