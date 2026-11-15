# Przekazanie: E-004 — poprawka warstwy komórek mapy

- Od: Ewelina, `codex-ewelina-e004-map-fix`
- Do: Kamil
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: E-004 / [PR #37](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/37) / `0c4f509752e12893f5dd8203390aa919e578c132`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-004-map-hotspot`
- Wysłane SHA i URL PR: `0c4f509752e12893f5dd8203390aa919e578c132`, https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/37
- Czy rezerwacja / rezultat są w origin/main: rezerwacja E-004 jest w `origin/main`; kod jest w zdalnej gałęzi PR; handoff i status `review` są publikowane w tym commicie koordynacyjnym
- Lokalne niewysłane zmiany i powód, jeśli występują: brak
- Stan: częściowe — poprawki i regresje są gotowe do re-review; ręczna inspekcja wizualna pozostaje do wykonania

## Co jest dostępne

- `AnalysisMap.tsx` przekazuje do MapLibre pole `collection` zwrócone przez `makeCellCollection`, zamiast całego wrappera z `invalidCount`.
- Etykieta mapy wyświetla nazwę zakresu globalnego lub regionalnego także dla liczby komórek.
- `renderData.ts` udostępnia funkcje renderowania GeoJSON, które są pokryte testami bez uruchamiania zewnętrznego basemapu.
- Fixture'y użyte w teście są syntetyczne; nie stanowią danych obserwacyjnych ani dowodu globalnego optimum.

## Jak odtworzyć

Z katalogu repozytorium:

```text
npm test --prefix apps/web
npm run build --prefix apps/web
git diff --check
```

Wersje kryteriów i odpowiedzi pochodzą z fixture'ów kontraktu w `contracts/fixtures/`; zakres zmiany ogranicza się do prezentacji danych mapowych i regresji.

## Sprawdzenia

- `npm test --prefix apps/web`: 30/30 testów zaliczonych.
- `npm run build --prefix apps/web`: typecheck i produkcyjny build Vite zaliczone.
- `git diff --check`: zaliczone.
- `apps/web/tests/map-render-data.test.mjs`: źródło otrzymuje dwa obiekty w FeatureCollection — wynik `100` oraz `null` z `missing_feature_value`; test sprawdza też etykietę globalną i regionalną.
- Ograniczenie: ręczna kontrola widoku w przeglądarce została przerwana, bo Computer Use zgłosił, że polityka URL nie jest obsługiwana dla lokalnej przeglądarki Windows. Nie potwierdzono wizualnie poligonów, legendy ani kompletnego scenariusza polarnego.
- Build sygnalizuje chunk JS 1,350.80 kB minified (375.97 kB gzip); kompilacja i testy przechodzą.

## Ograniczenia i potrzebne działania

Kamil: zarezerwuj i wykonaj K-029 na exact SHA powyżej. W re-review sprawdź wizualnie komórki z wynikiem liczbowym i `null`, etykietę zakresu, legendę, hotspot po oddaleniu oraz zachowanie bez basemapu. Po odbiorze połącz PR #37 do `main`, a następnie zsynchronizuj E-004 do `done`. Nie twierdzimy, że testy syntetyczne sprawdzają działanie live API ani wynik naukowy.
