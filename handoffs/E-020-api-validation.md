# E-020 — follow-up do review adaptera E-003

- Data: 2026-11-15
- Zadanie: E-020, naprawa uwag K-019
- Gałąź: `ewelina/E-020-validate-api-echo`
- Rezerwacja `origin/main`: `cc8ca41` (`tasks(E-020): IN PROGRESS`)
- Commit poprawki: `a4e0925` (`fix(E-020): validate live query echoes`)
- Review snapshot: `b8a5d0c6198944d0b1fbb8af4590ebd5b3c740fd`
- PR: [#20](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/20), otwarty i scalalny z `main`
- Raport pierwotnych obserwacji: [K-019](K-019-review-E-003.md)

## Zmiany

Live odpowiedź search jest porównywana z wysłanym `dataset_version`, ciałem, profilem, typem i ID zakresu, zbiorem kryteriów oraz wagami surowymi i znormalizowanymi, trybem rankingu, `top_k` i dystansem. Kolejność kryteriów w odpowiedzi nie zmienia ich znaczenia; brakujące, dodatkowe, powtórzone lub zmienione kryterium jest odrzucane. Wartość `normalized_weight` jest porównywana z normalizacją wag requestu z tolerancją `1e-9`.

Każda odpowiedź mapy — live i synthetic — musi zawierać echo czterech współrzędnych bbox, poziomu i limitu zgodne z żądaniem. Wcześniejsze sprawdzenia `analysis_id` mapy i `analysis_id`/pixel ID szczegółu pozostają aktywne. Odpowiedzi live nie przechodzą na fixture po błędzie.

## Sprawdzenia

- `npm test` w `apps/web/` — **24/24 zaliczone**. Harness SSR załadowuje adapter przez Vite i używa kontrolowanych odpowiedzi JSON pochodzących z syntetycznych fixture'ów. Obejmuje zgodne search/map/detail, rozbieżności dataset/body/profile/scope/feature/weights/mode/top_k/distance/bbox/level/limit, HTTP 503 bez fallbacku oraz istniejące wiązanie `analysis_id` i pixel ID.
- `npm run build` w `apps/web/` — **zaliczony**: TypeScript `tsc --noEmit` i Vite production build.
- `git diff --check` — bez błędów.
- Środowisko kontroli: Node `v22.13.0`, npm `10.9.2`, Vite `8.3.8`.

## Granice i dalszy odbiór

To są testy adaptera z kontrolowanymi payloadami, nie test połączenia z rzeczywistym serwerem ani test danych planetarnych. Backend projektu nadal implementuje tylko `/api/v1/health`; live search, map i pixel details nie są dostępne w tym PR. Scoring pozostaje po stronie API.

K-021 ma niezależnie sprawdzić wskazany `review_ref` przed scaleniem. Po akceptacji należy scalić PR #20 i dopiero wtedy oznaczyć E-020 oraz E-003 jako `done`.
