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

## Responsywność i fokus

Produkcyjny build Vite oglądano w Chrome DevTools responsive mode pod lokalnym preview na `http://127.0.0.1:4174/`. Pomiar z poziomu strony zwracał identyczne `innerWidth`, `documentElement.clientWidth`, `documentElement.scrollWidth` i `body.scrollWidth` dla:

| Żądana szerokość | Faktyczna szerokość viewportu | `scrollWidth` / `clientWidth` |
|---:|---:|---:|
| 320 | 320 | 320 / 320 |
| 375 | 375 | 375 / 375 |
| 390 | 390 | 390 / 390 |
| 780 | 780 | 780 / 780 |
| 781 | 782 | 782 / 782 |
| 1150 | 1150 | 1150 / 1150 |
| 1151 | 1151 | 1151 / 1151 |

Przy 781 px emulator Chrome zaokrąglił rozmiar viewportu do 782 px, dlatego punktu 781 px nie uznajemy za dokładnie zweryfikowany. Zrzut w szerokości 320 px pokazał układ mobilny bez oczywistego poziomego przycięcia lub nachodzenia tekstu. Dla pozostałych szerokości nie zapisano zrzutów ani pełnego przeglądu wizualnego. Nie wymuszono wariantu klasycznego paska przewijania.

W CSS pozostaje `:focus-visible` z obrysem `2px solid var(--accent)` i offsetem 3 px. Próba przejścia klawiaturą w przeglądarce nie potwierdziła, że fokus dotarł do elementu strony; widoczny fokus nie jest więc jeszcze zweryfikowany. Przy kolejnej próbie należy użyć preview, w którym można dokładnie ustawić viewport 781 px i skierować klawiaturę do treści strony.

## Ograniczenia

Pomiary overflow pochodzą z produkcyjnego renderu, ale same w sobie nie wykrywają każdego rodzaju obcięcia tekstu ani nakładania elementów. Automatyzacja przeglądarki została przerwana przy otwieraniu nowej karty, gdy nie mogła jednoznacznie ustalić bieżącego URL; dlatego fokus i pełny przegląd wizualny pozostają otwarte. Do odbioru E-021 trzeba powtórzyć punkt 781 px, obejrzeć layout w każdej zadanej szerokości, sprawdzić wariant z klasycznym paskiem przewijania i udokumentować widoczny fokus klawiatury.

WCAG 2.2 SC 1.4.3 wymaga co najmniej 4.5:1 dla zwykłego tekstu, z wyjątkami opisanymi w kryterium: [W3C WCAG 2.2](https://www.w3.org/TR/2023/REC-WCAG22-20231005/). Te statyczne obliczenia nie zastępują pełnego audytu UI w E-008.
