# Przekazanie: E-004 — poprawka warstwy komórek mapy

- Od: Ewelina, `codex-ewelina-e004-map-fix`; follow-up `codex-ewelina-e004-bundle-split`
- Do: Kamil
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commity: E-004 / [PR #37](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/37) / poprawka mapy `0c4f509752e12893f5dd8203390aa919e578c132`, lazy bundle follow-up `e63ded588f07b9925c54075a31e581d07bfc5fc9`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/E-004-map-hotspot`
- Wysłany exact `review_ref` i URL PR: `e63ded588f07b9925c54075a31e581d07bfc5fc9`, https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/37 (bieżący PR head po synchronizacji: `ae0bf5b7a4e58ce9f2d67bb91b15d1829c7c620e`)
- Czy rezerwacja / rezultat są w origin/main: rezerwacja E-004 jest w `origin/main`; kod jest w zdalnej gałęzi PR; handoff i status `review` są publikowane w tym commicie koordynacyjnym
- Lokalne niewysłane zmiany i powód, jeśli występują: brak
- Stan: częściowe — poprawki, regresje i code-splitting są gotowe do review; ręczna inspekcja wizualna pozostaje do wykonania

## Co jest dostępne

- `AnalysisMap.tsx` przekazuje do MapLibre pole `collection` zwrócone przez `makeCellCollection`, zamiast całego wrappera z `invalidCount`.
- Etykieta mapy wyświetla nazwę zakresu globalnego lub regionalnego także dla liczby komórek.
- `renderData.ts` udostępnia funkcje renderowania GeoJSON, które są pokryte testami bez uruchamiania zewnętrznego basemapu.
- Fixture'y użyte w teście są syntetyczne; nie stanowią danych obserwacyjnych ani dowodu globalnego optimum.

## Follow-up wydajnościowy

Build wcześniejszego PR #37 raportował jeden JS chunk 1,350.80 kB minified (375.97 kB gzip). Commit `e63ded588f07b9925c54075a31e581d07bfc5fc9` przenosi `AnalysisMap` i `maplibre-gl/dist/maplibre-gl.css` za dynamiczny import. Aplikacja pokazuje początkowo placeholder; mapowy chunk jest wymagany dopiero po rozpoczęciu analizy. `MapModuleBoundary` zachowuje resztę wyników, jeśli asynchroniczny moduł mapy nie zostanie pobrany.

Po zmianie produkcyjny build zawiera entry JS 268.06 kB (80.15 kB gzip) oraz oddzielny asynchroniczny `AnalysisMap` JS 1,085.35 kB (297.36 kB gzip) i CSS 71.33 kB (10.25 kB gzip). Entry HTML wskazuje tylko entry JS/CSS, bez bezpośredniego odwołania do mapowych plików. Vite nadal ostrzega o chunku mapy przekraczającym 500 kB; ostrzeżenia nie wyciszano. Osobny asset workera ma 519.54 kB i służy MapLibre.

Sprawdzenia dla follow-upu: `npm test --prefix apps/web` — 30/30; `npm run build --prefix apps/web` — typecheck i produkcyjny build zaliczone; `python tools/check_planning.py` — OK; `git diff --check` — bez błędów. Około 80% redukcji dotyczy początkowego JS w porównaniu z poprzednim entry bundle; całkowity kod mapy pozostaje duży i pobiera się, gdy użytkownik rozpoczyna analizę.

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

Kamil: zarezerwuj i wykonaj nowy K-032 na exact SHA `e63ded588f07b9925c54075a31e581d07bfc5fc9`. Poprzednia K-029 wskazuje zastąpiony SHA `0c4f509752e12893f5dd8203390aa919e578c132`; nie przeglądaj jej jako osobnego zakresu. W K-032 sprawdź FeatureCollection, komórki liczbowe/null, etykietę zakresu, nowe entry/map chunks, fallbacki, legendę, hotspot po oddaleniu i zachowanie bez basemapu. Po odbiorze połącz PR #37 do `main`, a następnie zsynchronizuj E-004 do `done`. Nie twierdzimy, że testy syntetyczne sprawdzają działanie live API ani wynik naukowy.
