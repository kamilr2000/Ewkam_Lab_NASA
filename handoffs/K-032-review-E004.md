# K-032 — Review lazy-load mapy E-004

**Decyzja:** `APPROVE` dla PR #37; GitHub review `5910052573`. Dokładnie oceniony `review_ref`: `e63ded588f07b9925c54075a31e581d07bfc5fc9`. Bieżący head PR podczas review: `9b7cdae02985c4e24a1e7c523a32d1fd1090aa8b`. Pliki web w zakresie K-032 są identyczne między tym headem a `review_ref`; po exact ref branch PR zawiera tylko merge commity i koordynacyjne pliki dokumentacji.

## Wyniki

- Początkowy `index.html` wskazuje tylko entry JS i CSS. Entry JS nie zawiera pakietu MapLibre; ma jedno dynamiczne `import()`. Początkowy stan `App` pokazuje placeholder i nie renderuje `AnalysisMap`. Dynamiczny moduł jest renderowany dopiero, gdy analiza ruszy, pojawi się odpowiedź albo błąd wyszukiwania.
- `AnalysisMap.tsx` importuje zarówno `maplibre-gl`, jak i `maplibre-gl.css` wewnątrz dynamicznego modułu. Produkcyjny build emituje oddzielne zasoby JS i CSS mapy oraz asset workera; nie są podłączone bezpośrednio w początkowym HTML.
- `MapModuleBoundary` i `Suspense` otaczają wyłącznie mapę. Nieudane pobranie modułu daje jawny komunikat „map unavailable” z przeładowaniem aplikacji. Ranking, podsumowanie i szczegóły piksela są rodzeństwem mapy i pozostają w renderze. Błąd inicjalizacji WebGL oraz błąd odświeżenia viewportu są pokazywane wewnątrz mapy; brak błędnego przełączenia do fixture.
- Komórki nadal trafiają do MapLibre jako `FeatureCollection`. Istniejący test sprawdza wynik `100`, `null` i `missing_feature_value`; oddzielny test potwierdza nazwy zakresu globalnego i regionalnego. Kod barwi komórkę `null` neutralnie, pokazuje osobne rankowane markery pikseli, a średnią komórki opisuje jako kontekst. Zaznaczenie markera wybiera pojedynczy piksel i przybliża jego geometrię.
- Styl MapLibre zawiera własne tło, siatkę geograficzną i warstwy GeoJSON. Nie korzysta z zewnętrznego basemapu ani kafli licencjonowanych przez dostawcę.

## Sprawdzenia

Wykonano na exact `review_ref` przy Node `v22.18.0`:

| Sprawdzenie / zasób | Wynik |
|---|---|
| `npm test --prefix apps/web` | 30/30 testów zaliczonych |
| `npm run build --prefix apps/web` | TypeScript i Vite build zaliczone |
| Entry JS | 268.06 kB; 80.15 kB gzip |
| Entry CSS | 21.36 kB; 5.58 kB gzip |
| Asynchroniczny `AnalysisMap` JS | 1,085.35 kB; 297.36 kB gzip |
| Asynchroniczny CSS mapy | 71.33 kB; 10.25 kB gzip |
| Asset workera MapLibre | 519.54 kB |

Vite nadal ostrzega, że chunk mapy przekracza 500 kB po minifikacji. Lazy-load przenosi pobieranie za rozpoczęcie analizy, ale nie zmniejsza całkowitego rozmiaru kodu mapy; ostrzeżenia nie wyciszano.

`git show --check e63ded588f07b9925c54075a31e581d07bfc5fc9` nie zgłasza whitespace w samym follow-up commicie. `git diff --check 26e004b9bc269021565f0bd8596ca18d8a11e213 e63ded588f07b9925c54075a31e581d07bfc5fc9` zgłasza dodatkowe puste linie na końcu `apps/web/src/map/AnalysisMap.tsx` (437) oraz `apps/web/src/map/geometry.ts` (176) w szerszym diffie PR. To kosmetyczne sprzątanie wcześniejszego zakresu mapy, nie regresja w lazy-loadzie; nie blokuje akceptacji.

## Ograniczenia i integracja

- Nie uzyskano wizualnego potwierdzenia aktualnego renderu po poprawce. Lokalny preview był uruchomiony, ale żądanie do `127.0.0.1:4173` zostało odrzucone przez uprawnienia połączeń środowiska; Chrome headless nie zwrócił użytecznego zrzutu. Build i źródła nie są przedstawiane jako test wizualny. Poprzednie K-027 potwierdziło starszy render, zanim naprawiono `FeatureCollection` i etykietę; nie zastępuje to oględzin tego SHA.
- Nie uruchomiono live API, nie testowano rzeczywistych danych ani naukowego rankingu. Wartości `100` i `null` pochodzą z syntetycznych fixture'ów.
- PR #37 pozostaje otwarty, head `9b7cdae...`, a GitHub raportuje `mergeable: false`; jego `base_sha` jest `26e004b...`, starszy niż bieżący `origin/main`. Przed integracją Ewelina musi zsynchronizować gałąź i rozwiązać konflikt koordynacyjnych kart, zachowując K-032 jako `in_progress` oraz K-029 jako `cancelled`. Połączenie review do main nie oznacza, że PR #37 lub E-004 są już zintegrowane.
