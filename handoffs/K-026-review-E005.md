# K-026 — wynik review E-005

## Zakres i wynik

- Oceniane zadanie: E-005, PR #31.
- Dokładny reviewed ref: `03e94204e8199440046f5dd600b38031b3e53773`.
- Aktualny PR head podczas oceny: `101e9e24a20c5cacb651df89c95df92aa9c0c538`; pliki aplikacji w `apps/web/` nie zmieniły się od reviewed ref.
- Rezerwacja K-026 została opublikowana w `origin/main` przez PR #39 i commit `f2fb8ccc0896ce2d43df434383027da62beaf4b7`.
- Wynik niezależnego review: **REQUEST_CHANGES**. Raport i poprawka P1 zostały opublikowane na [PR #31](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/31).

## Co potwierdzono

- `getAvailableProfileFeatures` wybiera cechy wspólne dla odpowiedzi profilu, jego wpisu w katalogu oraz cech dostępnych w danym trybie; builder requestu przesyła tylko aktywne kryteria.
- `buildSearchRequest` zachowuje `body` i `profile_id` profilu, wysyła jawny globalny scope, surowe dodatnie wagi i tryb pikselowy zgodny z SearchRequest v1.
- UI pokazuje surowe wagi i udziały znormalizowane. Edycja slidera/checkboxa zmienia lokalny stan, anuluje i unieważnia wcześniejsze żądanie oraz czyści poprzedni wynik. Nowe `runSearch` jest uruchamiane wyłącznie przez Run/Retry.
- Synthetic nie udostępnia kontrolek edycji; `runSearch` zwraca zapisany fixture i nie przelicza wyniku po zmianie konfiguracji.
- Testy obejmują jedno/trzy/zero aktywnych kryteriów, niepoprawne wagi, niedostępne cechy, profil Księżyca oraz niezależność metadanych widoczności mapy od requestu.

## Wymagana poprawka P1

W `apps/web/src/App.tsx` (około linii 50 w reviewed ref) dataset wybierany jest pierwszym wpisem z `body === 'earth'` i dostępnością dla trybu. Kod pomija `CatalogDataset.role`, choć katalog rozróżnia `earth_search`, `validation`, `planetary_reference` i `fixture_only`. Jeżeli dostępny dataset walidacyjny wystąpi wcześniej w katalogu, request otrzyma niewłaściwy `dataset_version`; kolejność katalogu nie jest kontraktem.

Właściciel: Ewelina w ramach E-005. Wymagany warunek: wybierać rolę właściwą dla trybu albo jawnie obsłużyć brak/wieloznaczność; dodać test, w którym dostępny dataset `validation` poprzedza `earth_search` i request nadal używa wersji Earth search.

## Sprawdzenia

- `npm test --prefix apps/web` — **35/35 passed** na dokładnym reviewed ref.
- `npm run build --prefix apps/web` — **passed**, TypeScript i build Vite.
- `python tools/check_planning.py` — **OK**, 116 Markdown, 32 JSON, 58 kart, bez cykli, 5 przypadków syntetycznych.
- `git diff 03e94204e8199440046f5dd600b38031b3e53773^1 03e94204e8199440046f5dd600b38031b3e53773 --check` — **passed**.
- Testy korzystają z fixture'ów oznaczonych jako synthetic. API wdraża obecnie tylko health; live catalog/profile/search nie były uruchamiane. Brak wywołania z slidera potwierdzono przez przepływ kodu, nie przez przechwycenie żądania w przeglądarce.

Review K-026 jest zakończony wynikiem REQUEST_CHANGES. PR #31 i E-005 pozostają otwarte do poprawienia roli datasetu i ponownego sprawdzenia; nie oznacza to odbioru globalnego rankingu ani pełnej aplikacji.
