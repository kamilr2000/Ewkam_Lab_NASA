# Przekazanie: K-019 — review adaptera E-003

- Od: Kamil / `codex-kamil-k019-review`
- Do: Ewelina
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: K-019; [PR #16](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/16)
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-003-api-adapter`
- Wysłane SHA i URL PR: review dotyczy przypiętego `5becdea0f37e7757853acdf7614d5e19a90e433f`; raport trafia do `origin/main` przez PR dokumentacyjny/koordynacyjny.
- Czy rezerwacja / rezultat są w `origin/main`: rezerwacja K-019 jest w `origin/main`; raport i wynik review publikowane razem z tym przekazaniem.
- Lokalne niewysłane zmiany i powód, jeśli występują: brak.
- Stan: wymaga poprawek.

## Co jest dostępne

Adapter v1 rozdziela `synthetic` i `live`, widocznie opisuje fixture'y, nie przełącza się na fixture po błędzie live i nie liczy wyniku w przeglądarce. Odpowiedzi mapy i piksela są sprawdzane względem żądanego `analysis_id` i ID piksela; `RequestEpoch` oraz abort kontrolują spóźnione wyszukiwanie. Scenariusze syntetyczne: sukces, pusty zakres, brak danych, hotspot, distinct areas i `DATASET_UNAVAILABLE`.

Oceniony snapshot to dokładny head `5becdea0f37e7757853acdf7614d5e19a90e433f`. PR zawiera też `6ce2492` (usunęło nieuzasadnioną obietnicę pełnych cytowań) i synchronizację z main. W samym repo backend implementuje obecnie tylko `/api/v1/health`; pozostałe ścieżki są zamrożonym kontraktem i nie dowodzą dostępności rzeczywistych obliczeń.

## Wynik review — wymagane poprawki

1. **P0 — odpowiedź search może dotyczyć innego żądania.** `parseSearch` w `apps/web/src/api/client.ts` porównuje tylko `profile_id`, `body` i `result_mode`. W odtwarzalnym wywołaniu live request oczekiwał `synthetic-earth-v1`, scope regional i `slope_deg`/`roughness_m`; odpowiedź z `unexpected-dataset`, scope global i cechą `wrong-feature` została zaakceptowana. Weryfikuj także `dataset_version`, scope, criteria i wagi, `top_k` oraz `min_distance_km`; niezgodność ma dawać jawny `ApiError`.
2. **P0 — odpowiedź mapy może dotyczyć innego bbox.** `getAnalysisMap` sprawdza `bbox`, `level` i `limit` tylko w trybie synthetic. W live odpowiedź z pasującym `analysis_id`, ale bbox `[-180,-90,180,90]` zamiast żądanego `[1,2,3,4]`, została zaakceptowana. Sprawdzaj echo parametrów w obu trybach.

Oba przypadki mogą przypisać wynik naukowy do niezamówionego datasetu lub obszaru. Zadanie poprawek: [E-020](../tasks/E-020.md), przypisane Ewelinie. Po zmianie potrzebne jest nowe review dokładnego SHA zmienionego zakresu.

## Jak odtworzyć

W `apps/web/`:

```text
npm run build
```

Test ad hoc załadował `apps/web/src/api/client.ts` przez Vite SSR i podstawił kontrolowane odpowiedzi `fetch`; nie został zapisany jako test repozytorium. Wszystkie pięć fixture'ów wyszukiwania zwróciło `is_synthetic: true`; `dataset-unavailable` odrzucił się jako HTTP 503. Kontrolowane niezgodne odpowiedzi live search i map zostały zaakceptowane, co odtwarza uwagi powyżej. E-020 wymaga dodania stałych testów regresji.

## Sprawdzenia

- `npm run build` — zaliczony: `tsc --noEmit` oraz Vite production build; Node `v22.18.0`, npm `10.4.0`, Vite `8.3.8`.
- Vite SSR adapter scenarios — pięć syntetycznych wyników przyjętych; fixture błędu odrzucony jako 503.
- Wstrzyknięta live odpowiedź z innym datasetem, scope i feature — **błędnie zaakceptowana**.
- Wstrzyknięta live odpowiedź mapy z niezamówionym bbox — **błędnie zaakceptowana**.
- Analiza statyczna potwierdziła brak wywołań scoringu po stronie React i kontrolę `analysis_id` w funkcjach map/detail.
- Pełny manualny widok w przeglądarce nie został niezależnie odtworzony; opisuję to jako ograniczenie review, nie jako przejście UI.

## Ograniczenia i potrzebne działania

Ewelina: zarezerwuj i wykonaj E-020, dodaj testy odpowiedzi zgodnych i rozbieżnych, opublikuj poprawkę i kartę review dla nowego SHA. Mapa nadal jest podsumowaniem odpowiedzi, bez renderera i podkładu; live API poza health oraz Moon profile pozostają niezaimplementowane. Nic w tym review nie potwierdza działających wyników NASA.
