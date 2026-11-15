# Przekazanie: K-027 — Review interaktywnej mapy E-004

- Od: Kamil / `codex-kamil-k027-review`
- Do: Ewelina
- Data i strefa: 2026-11-15, Europe/Warsaw
- Zadanie / PR / commit: K-027 / E-004 PR #37 / dokładnie `fa32bc6ee0a6ffa5dbc178fd13dc417c2928a480`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`; review gałąź `kamil/K-027-review-e004`; kod `ewelina/E-004-map-hotspot`
- Wysłane SHA i URL raportu: `48bc7070ae58054b827688add0f788eae19d4ce4` / PR #42
- Wysłany wynik review: PR #37, review `5908868712`, `REQUEST_CHANGES`
- Rezerwacja w `origin/main`: tak, PR #41, merge `98885f4aaae83935c08b50b50b0da12a84198ac1`
- Lokalne niewysłane zmiany: brak po publikacji
- Stan: wymagane poprawki przed akceptacją E-004

## Co jest dostępne

Review obejmuje exact head PR #37. PR pozostaje otwarty na `fa32bc6ee0a6ffa5dbc178fd13dc417c2928a480`; wynik `REQUEST_CHANGES` jest opublikowany bezpośrednio przy tym SHA.

W syntetycznym fixture izolowanego hotspotu przeglądarka pokazała cztery pozycje rankingu i cztery markery. Najwyższy pojedynczy piksel zachował wynik 100%; trzy kolejne wyniki to 60%, 20% i 20%. Średnia 46.67% jest opisana jako kontekst komórki, a nie wynik piksela. Po wybraniu Top 1 i oddaleniu jego szczegóły oraz cztery markery nadal były obecne. Są to wyłącznie dane testowe i regionalny przykład, nie pomiary ani ranking globalny.

**Mapa nie rysuje wypełnień komórek.** W pliku `apps/web/src/map/AnalysisMap.tsx` helper `makeCellCollection()` zwraca obiekt `{ collection, invalidCount }`, lecz linia 341 przekazuje cały obiekt do `GeoJSONSource.setData()`. W exact fixture nagłówek i podsumowanie zgłaszają dwie komórki mapy, ale zapytanie warstwy `analysis-cells-fill` w przeglądarce zwróciło zero renderowanych cech. Wypełnienia z wynikiem i neutralne komórki null są niewidoczne; widoczne pozostają markery i dane rankingu. Poprawka: przekazać sam `collection.collection` albo rozdzielić GeoJSON od diagnostyki i dodać test warstwy dla wyniku oraz null.

Drugi błąd zakresu: nagłówek mapy stale dodaje tekst `GLOBAL DISPLAY CELLS`. Dla syntetycznego zakresu regionalnego widać `REGIONAL ANALYSIS · 2 GLOBAL DISPLAY CELLS`, choć opis wyniku wyjaśnia, że przykład nie jest globalnym rankingiem. Ewelina powinna uzależnić ten tekst od `scope.type` albo użyć neutralnego `DISPLAY CELLS IN SCOPE`.

Legenda prezentuje stały zakres 0–100, osobny neutralny symbol `null` i symbol Top 10. Etykieta oraz ostrzeżenia oznaczają fixture jako syntetyczny; scenariusz bez danych pokazuje 0/2 kwalifikujących się pikseli i zachowuje null. Mapa nie korzysta z zewnętrznych kafli ani podkładu, a UI jawnie komunikuje brak zewnętrznej zależności kaflowej. Identyfikatory źródeł pojawiają się w szczegółach pomiaru; prototyp nie podaje pełnych linków bibliograficznych przy wyniku.

## Jak odtworzyć

W dokładnym checkoutcie `fa32bc6ee0a6ffa5dbc178fd13dc417c2928a480`:

1. `npm ci --prefix apps/web`
2. `npm run dev --prefix apps/web -- --host 127.0.0.1`
3. W panelu po lewej wybierz `Synthetic fixture demo`, scenariusz `Isolated hotspot` i uruchom analizę.
4. Potwierdź cztery rankingi/markery i średnią 46.67% jako kontekst, potem wybierz Top 1 i oddal widok.
5. Uruchom scenariusz `No eligible measurements`; UI zachowuje 0/2 eligible i null, ale komórka null nie jest namalowana na mapie.

Weryfikacja wykonana w Chromium 157 na lokalnym buildzie exact SHA.

## Sprawdzenia

- `npm run build --prefix apps/web` — typecheck i build Vite przeszły; bundler ostrzegł, że główny chunk JavaScript ma 1.35 MB po minifikacji.
- `npm test --prefix apps/web` — 28/28 testów przeszło.
- `git diff --check fa32bc6ee0a6ffa5dbc178fd13dc417c2928a480^ fa32bc6ee0a6ffa5dbc178fd13dc417c2928a480` — czysty.
- Własne asercje dla geometrii: poligon przez ±180° dzieli się na dwie części, bounds wynoszą 179°–181°, szerokość/długość geograficzna pozostają w prawidłowym zakresie, a polarne bounds kończą się bezpiecznie na 89.5°.
- W kodzie sprawdzono, że zoom mapy zmienia bbox, lecz rankingowe `pixels` nadal pochodzi z odpowiedzi analizy; limit pobierania mapy to maksymalnie 1000 komórek, a dwa bbox przy antimeridianie dostają najwyżej po 500.
- Ręcznie obejrzano zrzuty mapy przed i po wyborze/oddaleniu oraz fixture braku danych. Direct runtime query warstwy fill potwierdził brak renderowanych komórek w exact SHA.

## Ograniczenia i potrzebne działania

1. Ewelina: popraw P1 z payloadem `setData()` i dodaj regresję potwierdzającą obecność komórek z wynikiem oraz komórek null w źródle/warstwie.
2. Ewelina: popraw P1 etykiety scope i dodaj sprawdzenie, że regionalny wynik nie jest opisywany jako globalny.
3. Live endpoint mapy, jego rzeczywiste odpowiedzi bbox i faktyczna awaria usługi nie zostały uruchomione; backend w obecnej integracji nie udostępnia działającego wyszukiwania/mapy. Oceniono kontraktowe fixture'y i kod limitowania.
4. Nie było polarnego fixture'u do screenshotu. Wykonano niezależne asercje geometryczne, a ograniczenie projekcji/map.fitBounds sprawdzono w kodzie; nie deklarujemy pełnej wizualnej walidacji polarnej.
5. K-027 jest zakończone jako review z poprawkami; E-004 pozostaje w statusie `review`. Raport nie oznacza akceptacji ani ukończenia globalnego rankingu lub live API.
