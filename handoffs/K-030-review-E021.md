# K-030 — Review E-021 czytelności UI

**Decyzja:** `REQUEST_CHANGES` dla PR #35. Review dotyczy exact `review_ref` `a3f8fdeb3fe5845538083e76d359acc35a9abce8`; w chwili sprawdzenia PR #35 miał head `476c7c5992eb4e2b6bdb6b957effdd0788106129`. CSS w tym headzie jest identyczny z CSS pod exact `review_ref`.

## Sprawdzenia

- `npm run build --prefix apps/web` na exact SHA — OK: TypeScript typecheck i produkcyjny build Vite.
- `git diff --check origin/main...origin/ewelina/E-021-ui-readability` — OK.
- Przejrzano każdą deklarację `font-size` i shorthand `font` w `styles.css`, wraz z breakpointami `max-width: 780px` i `max-width: 390px`. Najmniejszy rozmiar tekstu wynosi 9 px; deklaracji poniżej 9 px nie ma.
- Niezależnie przeliczono reprezentatywne pary metodą względnej luminancji sRGB. Wszystkie sprawdzone wartości wynoszą co najmniej 4.68:1. Wymóg 4.5:1 dla zwykłego tekstu wynika z [WCAG 2.2, SC 1.4.3](https://www.w3.org/TR/2023/REC-WCAG22-20231005/#contrast-minimum). Wyłączone kontrolki policzono również na potrzeby zakresu K-030, choć SC 1.4.3 wyłącza tekst nieaktywnych komponentów.

| Przykład z exact CSS | Tekst / tło | Kontrast |
|---|---|---:|
| Pusty znacznik wyniku | `#7e8c85` / `#172122` | 4.68:1 |
| Metadane piksela | `#7d8d84` / `#172122` | 4.71:1 |
| Pomoc pola formularza | `#81918a` / `#172122` | 4.97:1 |
| Współrzędne mapy na konserwatywnym złożonym tle | `#9daa9f` / `#283835` | 5.09:1 |
| Tekst wyłączonego selectora | `#94a39d` / `#1c2929` | 5.71:1 |
| Tekst wyłączonego przycisku | `#a4b09e` / `#344130` | 4.77:1 |
| Opis banera danych syntetycznych na tle złożonym z CSS | `#93a199` / `#202a26` | 5.49:1 |

Złożone tło mapy `#283835` jest jaśniejsze od centrum tła wynikającego z podanych w CSS gradientu i siatki, więc sprawdzenie podpisu mapy jest konserwatywne.

## Viewporty i fokus

Handoff E-021 podaje, że produkcyjny preview nie miał poziomego overflow dla pomiarów: 320, 375, 390, 780, 1150 i 1151 px; przy 320 px Tab przeniósł fokus na `Fixture scenario` z widocznym obrysem. CSS zawiera jawną regułę `:focus-visible`. W tym worktree nie udało się uruchomić lokalnego endpointu Chrome DevTools do niezależnego powtórzenia tych pomiarów, dlatego powyższe wyniki traktuję jako dowody producentki, nie jako własny pomiar przeglądarkowy.

| Żądana szerokość | Faktyczne `innerWidth` w handoffie | Ocena |
|---:|---:|---|
| 320 | 320 | Bez overflow według handoffu |
| 375 | 375 | Bez overflow według handoffu |
| 390 | 390 | Bez overflow według handoffu |
| 780 | 780 | Bez overflow według handoffu |
| 781 | 782 | Brak dokładnego pomiaru 781 px |
| 1150 | 1150 | Bez overflow według handoffu |
| 1151 | 1151 | Bez overflow według handoffu |

Karta E-021 nadal wymaga siedmiu konkretnych szerokości, a jej kryterium viewportu pozostaje niezaznaczone. Pomiar 782 px nie dowodzi zachowania przy 781 px; to punkt po drugiej stronie breakpointu `max-width: 780px`, gdzie pojedynczy piksel może zmienić zawijanie. Właścicielka powinna ustawić CSS viewport dokładnie na 781 px (np. przez `Emulation.setDeviceMetricsOverride` albo `page.setViewportSize`), zapisać `innerWidth`, `clientWidth` i `scrollWidth`, sprawdzić przycięcia/nachodzenie, a następnie uzupełnić handoff. Jeśli viewport 781 px nie jest już wymagany, kryterium trzeba jawnie zmienić w karcie przed oznaczeniem E-021 jako `done`.

Brak wymuszonego klasycznego, nieprzezroczystego scrollbara został jawnie zachowany jako ograniczenie handoffu. Nie przedstawiam tego review jako pełnego audytu dostępności E-008.

## Następny krok

Ewelina: opublikować dokładny pomiar 781 px wraz z potwierdzeniem braku poziomego overflow, przycięć i nakładania albo uzgodnić jawną zmianę kryterium w `origin/main`. Do tego czasu E-021 pozostaje w `review`; K-030 nie zmienia statusu E-021.
