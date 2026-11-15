# E-021 — Czytelność bazowego UI (w trakcie)

Status: `in_progress`. Gałąź: `ewelina/E-021-ui-readability`. Rezerwacja jest w `origin/main` w commicie `35c71be`. Ostatni opublikowany przyrost CSS: `94ba5ea41f505afff3bd063bb6aeff2046a364fa`. Brak PR i `review_ref`; nie jest to jeszcze gotowe do odbioru.

## Zmiana

W `apps/web/src/styles.css` podniesiono kontrast drobnych podpisów oraz rozmiary kluczowych etykiet, jednostek, objaśnień i stanów z 8–11 px do 9–12 px, także w mobilnych etykietach mapy i stopce. Widok disabled zachowuje wyłączone kontrolki i kursor `not-allowed`; fokus klawiatury pozostaje z jawnym obrysem. Dla podpisów mapy uwzględniono ciemną bazę oraz jaśniejszy gradient i siatkę z CSS.

Źródłowe sprawdzenie CSS nie znajduje deklaracji tekstu poniżej 9 px po uwzględnieniu mobilnych nadpisań.

## Dowody

Kontrast policzono ze względnej luminancji sRGB. Dla mapy użyto konserwatywnego composited background `#283835` — jaśniejszego niż przewidywana suma gradientu radialnego i siatki wynikająca z CSS. Wśród 39 sprawdzonych par foreground/background minimum wynosi 4.68:1; pozostałe reprezentatywne pary po poprawce mają 4.77–14.91:1.

| Element | Przed | Po |
|---|---:|---:|
| Stopka, na `#11191a` | 3.79:1 | 5.86:1 |
| Tekst pomocniczy panelu, na `#172122` | 3.80:1 | 4.99:1 |
| Breadcrumb, na `#11191a` | 4.31:1 | 5.41:1 |
| Jednostka, na `#172122` | 4.36:1 | 4.99:1 |
| Podpisy mapy, na konserwatywnym `#283835` | poniżej 4.5:1 | 5.09:1 lub więcej |
| Skala mapy, na `#152021` | 3.67:1 | 6.89:1 |
| Wyłączony selektor, na `#1c2929` | 4.08:1 | 5.71:1 |
| Wyłączony przycisk, na `#344130` | 4.45:1 | 4.77:1 |

Sprawdzono `npm run build` w `apps/web/` — typecheck i produkcyjny build Vite przechodzą. `git diff --check` przechodzi.

## Niezweryfikowane

Nie wykonano jeszcze oględzin renderu, fokusu ani pomiarów `scrollWidth <= clientWidth` dla 320/375/390/780/781/1150/1151 px. Próba otwarcia lokalnego podglądu została przerwana przez kontrolę Computer Use, która nie mogła pewnie ustalić URL; niezależne lokalne żądanie HTTP zostało zablokowane przez uprawnienia gniazda w środowisku. Nie ma zrzutów i nie twierdzimy, że układ w tych szerokościach został sprawdzony. Do zamknięcia E-021 potrzebna jest kontrola layoutu i fokusu w dostępnym, zatwierdzonym podglądzie.

WCAG 2.2 SC 1.4.3 wymaga co najmniej 4.5:1 dla zwykłego tekstu, z wyjątkami opisanymi w kryterium: [W3C WCAG 2.2](https://www.w3.org/TR/2023/REC-WCAG22-20231005/). Te statyczne obliczenia nie zastępują pełnego audytu UI w E-008.
