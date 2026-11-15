# K-021 re-review — E-020 API response validation

- Reviewer: Kamil (`codex-kamil-k021-review-e020`)
- Date: 2026-11-15, Europe/Warsaw
- Reviewed task/PR: K-021 / [PR #20](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/20)
- Exact card `review_ref`: `b8a5d0c6198944d0b1fbb8af4590ebd5b3c740fd`
- Current PR head checked: `ca38f3581f6b215e81353e05e2d690f520b9ebc2`; code files are unchanged from `review_ref`, later commits update task/handoff documentation.
- Result: **REQUEST_CHANGES**, GitHub review ID `5908191497`.
- Follow-up owner: Ewelina, original E-020; request a new K-review card at the corrected SHA.

## Zakres i poprawne elementy

Sprawdziłem `apps/web/src/api/client.ts`, `apps/web/tests/api-client.test.mjs`, `apps/web/src/App.tsx`, `apps/web/README.md`, kontrakt search/map/pixel oraz PR description. Adapter porównuje `dataset_version`, query body/profile/scope/result mode/criteria i raw+normalized weights, `top_k`, `min_distance_km` oraz regułę doboru obszarów. Map response porównuje bbox/level/limit w trybie live i synthetic, zachowując `analysis_id`; pixel details zachowuje kontrolę `analysis_id` i `pixel_id`. Błąd HTTP live pozostaje jawny i nie przełącza klienta na fixture. W kodzie przeglądarki nie ma silnika scoringowego. README i PR poprawnie zaznaczają, że backend ma obecnie tylko `/api/v1/health`; deklarację o echo scope należy czytać jako `query.scope`, bo top-level scope wymaga opisanej niżej dodatkowej walidacji.

## Finding — P0: top-level response scope może różnić się od query scope

`parseSearch` sprawdza `value.query.scope` względem requestu, ale nie wiąże z requestem osobnego `value.scope`, którego UI używa w `App.tsx` do wyświetlenia nazwy regionu i opisu analizy.

Odtworzenie na bieżącym PR headzie: użyłem odpowiedzi live z poprawnym `query.scope.region_id = synthetic-region-1`, zmieniłem tylko `response.scope.region_id` i `region_name` na `wrong-region`, po czym `runSearch('live', ...)` zaakceptował odpowiedź. UI bierze `analysis.scope.region_name` z top-level response, więc raport może przypisać prawidłowe wyniki do innego regionu. Wymagane jest porównanie co najmniej `response.scope.type` i regionalnego `region_id` z requestem oraz zachowanie null semantyki scope globalnego, z regresją dla tego rozjazdu.

## Sprawdzenia

- `npm test` na `ca38f3581f6b215e81353e05e2d690f520b9ebc2` — 24/24 passed, w tym zgodne query, rozbieżne search/map, brak live fallbacku oraz ID analizy/piksela.
- `npm run build` — TypeScript i Vite production build passed.
- Ad hoc Vite SSR repro — odpowiedź z poprawnym query scope i błędnym top-level scope została zaakceptowana; mismatch jest niezależny od 24 istniejących testów.
- Zmiany od `review_ref` do bieżącego PR headu obejmują dokumentację i karty; adapter oraz testy nie zmieniły się.

## Ograniczenia i następny krok

Nie sprawdzałem działającego live backendu ani map renderer UI; backend w repo nie implementuje jeszcze wyszukiwania. Ewelina: popraw walidację top-level `scope`, dodaj test mismatchu dla scope regional i global, ponownie uruchom testy/build i utwórz nową kartę K-review dla dokładnego poprawionego SHA. E-020 pozostaje w review do zamknięcia tej P0 uwagi.
