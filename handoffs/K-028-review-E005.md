# K-028 — wynik re-review wyboru roli datasetu E-005

## Zakres i wynik

- Oceniane zadanie: E-005, [PR #31](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/31).
- Dokładny reviewed ref: `98be49cac38e6d72245a092e7a59bab7c5599424` (`fix(E-005): select datasets by role`).
- Head PR podczas review: `1526945b3af6b191f02f44ae529e14757425057c`. Późniejsze zmiany względem reviewed ref dotyczą wyłącznie handoffu i metadanych zadań; zmienione pliki aplikacji i testów są identyczne.
- Rezerwacja K-028 została połączona do `origin/main` przez PR #47, commit `49b651f13d7f322ec40432e97fa245d32ad83326`.
- Wynik: **ACCEPT** poprawki K-026. Approval opublikowano na PR #31 przy bieżącym headzie.

## Co potwierdzono

- `CatalogDatasetRole` w TypeScript ma te same cztery wartości co enum `role` w `contracts/catalog-response.schema.json`.
- `selectDatasetForMode` wybiera dokładnie jeden rekord z `body: earth`, właściwą rolą i availability: Live używa `earth_search`/`available`, a Synthetic `fixture_only`/`synthetic_only`. Kolejność katalogu nie wpływa na wybór.
- Brak dopasowania i wiele dopasowań powodują jawny wyjątek. `makeRequest` jest wywoływane wewnątrz obsługi błędów `runAnalysis`; błąd trafia do stanu `searchError`, a `runSearch` nie jest wywoływane.
- `dataset_version` wybranego rekordu jest przekazywany do SearchRequest. Request zachowuje body i profile ID z profilu, globalny scope, aktywne kryteria, `pixels` i `top_k: 10`.
- Testy sprawdzają katalog Live z dostępnym `validation` przed `earth_search`, brak i wieloznaczność roli oraz wymóg `fixture_only` w Synthetic. Testy operują na kopiach fixture'ów oznaczonych jako syntetyczne.

## Sprawdzenia

- `npm test --prefix apps/web` na exact review ref — **38/38 passed**.
- `npm run build --prefix apps/web` — **passed** (TypeScript i Vite production build).
- `python tools/check_planning.py` — **OK**, 134 Markdown, 32 JSON, 67 kart, graf zależności bez cykli.
- `git diff --check 1c13cffa6f8c310b31a3068496fd88f8eb8a7d0e 98be49cac38e6d72245a092e7a59bab7c5599424` — czysto.

## Ograniczenia i status integracji

- API obecnie udostępnia tylko health. Nie wykonano live catalog/profile/search ani nie potwierdzono zachowania na rzeczywistych pomiarach; regresje ról używają wyłącznie syntetycznych kopii katalogu.
- PR #31 pozostaje otwarty. K-028 akceptuje poprawkę w ocenionym zakresie; E-005 nie jest `done`, dopóki PR z kodem nie zostanie połączony do `origin/main`.
