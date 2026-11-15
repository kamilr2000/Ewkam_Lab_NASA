# Przekazanie: E-005 — wybór cech i wag

- Od: Ewelina, `codex-ewelina-e005-controls`
- Do: Kamil
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: E-005 / [PR #31](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/31) / review ref `03e94204e8199440046f5dd600b38031b3e53773`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-005-controls`
- Wysłane SHA i URL PR: `03e94204e8199440046f5dd600b38031b3e53773`, PR #31
- Czy rezerwacja / rezultat są w origin/main: rezerwacja E-005 `eea4b525e870a1926685b713602fd1364b82a7bf` jest w `origin/main`; implementacja czeka na review w PR
- Lokalne niewysłane zmiany i powód, jeśli występują: brak
- Stan: częściowe — kod UI i budowa requestu są gotowe do review; integracja z rzeczywistym API nie jest dostępna

## Co jest dostępne

- `apps/web/src/controls/criteria.ts` ogranicza cechy do przecięcia profilu i katalogu z dostępnością dla bieżącego trybu, przechowuje stan włączenia i dodatnie wagi oraz odrzuca pusty albo niepoprawny zestaw.
- `apps/web/src/controls/CriteriaControls.tsx` pokazuje checkboxy, suwaki, surową wagę i jej znormalizowany udział.
- `apps/web/src/App.tsx` tworzy globalny request Earth z aktywnymi cechami, zachowuje `body` i `profile_id`, czyści poprzedni wynik po zmianie konfiguracji i wywołuje analizę wyłącznie po kliknięciu przycisku.
- Kontrolki edycji są w trybie Live API. Synthetic demo zachowuje gotowe scenariusze tylko do odczytu, bo ich odpowiedzi nie przeliczają zmienionych wag.
- Testy używają kopii fixture'ów oznaczonych synthetic; nie zawierają rzeczywistych pomiarów.

## Jak odtworzyć

Z katalogu repo:

```powershell
npm test --prefix apps/web
npm run build --prefix apps/web
python tools/check_planning.py
git diff --check
```

## Sprawdzenia

- `npm test --prefix apps/web` — 35 testów przechodzi, w tym 1/3/0 aktywnych cech, niepoprawne wagi, brak dostępności cechy, zachowanie body/profile ID Marsa i Księżyca oraz niezależność metadanych widoczności od requestu.
- `npm run build --prefix apps/web` — TypeScript i produkcyjny build Vite przechodzą.
- `python tools/check_planning.py` — OK; `git diff --check` — OK.
- Nie wykonano przeglądarkowego przepływu z live catalog/search: K-001 udostępnia obecnie wyłącznie `/api/v1/health`.

## Ograniczenia i potrzebne działania

- Proszę sprawdzić PR #31 na dokładnym `review_ref` powyżej, zwłaszcza semantykę globalnego scope, filtrowanie dostępnych cech, normalizację wag oraz ręczne uruchamianie analizy.
- E-004 nie udostępnia jeszcze mapowych przełączników widoczności. W tym zakresie potwierdzono, że serializer kryteriów nie odczytuje metadanych widoczności; interakcję UI trzeba potwierdzić po integracji mapy.
- Rzeczywiste profile i możliwość wysłania requestu live można sprawdzić dopiero po wdrożeniu endpointów katalogu/profilu/search. Nie twierdzę, że aplikacja lub naukowy ranking działa na danych rzeczywistych.
- Przed `done` wymagane są review Kamila i połączenie rozwiązania do `origin/main`.
