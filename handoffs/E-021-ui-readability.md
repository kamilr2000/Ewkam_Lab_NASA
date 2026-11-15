# E-021 — Czytelność bazowego UI (w trakcie)

Status: `review` na `origin/main` od commitu `f3288465908d9e9843f76daf56f51aac06ba49c6`. Gałąź: `ewelina/E-021-ui-readability`. Poprawka i bieżące pomiary są opublikowane w PR #35; ostatni potwierdzony head przed dołączeniem świeżego zrzutu to `4c4975eb5fcc45f9c2d4da163c35df3b813d4ee0`. Karta na `main` wskazuje exact ref `d85f717a645d4a23c67831d4d4c1e7ad4b981266`; odświeżę ją po publikacji nowego screenshotu. Poprzednie exact refs oraz historyczne pomiary poniżej nie obejmują tej poprawki.

## Zmiana

W `apps/web/src/styles.css` podniesiono kontrast drobnych podpisów oraz rozmiary kluczowych etykiet, jednostek, objaśnień i stanów z 8–11 px do 9–12 px, także w mobilnych etykietach mapy i stopce. Widok disabled zachowuje wyłączone kontrolki i kursor `not-allowed`; fokus klawiatury pozostaje z jawnym obrysem. Dla podpisów mapy uwzględniono ciemną bazę oraz jaśniejszy gradient i siatkę z CSS.

Źródłowe sprawdzenie CSS w pierwotnym snapshotcie E-021 nie znajdowało deklaracji tekstu poniżej 9 px po uwzględnieniu mobilnych nadpisań.

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

Po synchronizacji E-005 doszły etykiety i opisy w syntetycznym przepływie wyników. Podniesiono je do minimum 9 px, a dwa kolory poniżej 4.5:1 na ich rzeczywistych ciemnych panelach rozjaśniono. Dodatkowe pary sprawdzono ze złożonym tłem wynikającym z CSS; wszystkie mają co najmniej 4.68:1:

| Dodatkowy element | Kolor tekstu / złożone tło | Kontrast |
|---|---|---:|
| Etykieta pola pomocniczego | `#81918a` / `#172122` | 4.97:1 |
| Opis banera danych syntetycznych | `#93a199` / `#202a26` | 5.49:1 |
| Etykiety metryk wyniku | `#84938b` / `#121d1d` | 5.35:1 |
| Identyfikator analizy | `#82918b` / `#121d1d` | 5.23:1 |
| Opis w rankingu | `#84938b` / `#172122` | 5.11:1 |
| Etykiety metadanych piksela | `#7d8d84` / `#172122` | 4.71:1 |
| Tekst źródła cechy | `#82918b` / `#1a2425` | 4.82:1 |
| Znacznik pustego stanu | `#7e8c85` / `#172122` | 4.68:1 |

Sprawdzenie deklaracji fontów w tamtym snapshotcie `styles.css` nie znalazło tekstu poniżej 9 px. Tabela dotyczy tekstu; nie jest audytem kontrastu wszystkich ikon, obramowań i stanów interaktywnych.

## Poprzednie pomiary responsywności i fokusu

Poniższa tabela oraz oględziny opisują wcześniejszy snapshot `a3f8fdeb3fe5845538083e76d359acc35a9abce8`. Nie są dowodem dla bieżącej wersji po późniejszym dodaniu kontrolek kryteriów E-005.

Produkcyjny build Vite obejrzano w Chrome DevTools responsive mode z preview `http://localhost:4173/`. Z konsoli strony odczytano `innerWidth`, `document.documentElement.clientWidth`, `document.documentElement.scrollWidth` i `document.body.scrollWidth`:

| Żądana szerokość | Faktyczny `innerWidth` | `clientWidth` | `scrollWidth` / `body.scrollWidth` |
|---:|---:|---:|---:|
| 320 | 320 | 320 | 320 / 320 |
| 375 | 375 | 375 | 375 / 375 |
| 390 | 390 | 390 | 390 / 390 |
| 780 | 780 | 780 | 780 / 780 |
| 781 | 782 | 782 | 782 / 782 |
| 1150 | 1150 | 1150 | 1150 / 1150 |
| 1151 | 1151 | 1151 | 1151 / 1151 |

Na każdym faktycznie zmierzonym viewportcie `scrollWidth == clientWidth`; oględziny renderu nie pokazały oczywistego przycięcia poziomego ani nachodzenia etykiet. Przy żądaniu 781 px pole Chrome przyjęło 781, ale strona raportowała 782 px. Ten punkt nie jest dokładnym pomiarem 781 px; 782 px pozostaje po tej samej stronie progu media query 780 px.

Przy 320 px kliknięto selektor „Data source”, zamknięto menu klawiszem Escape i przejście Tab przeniosło fokus na „Fixture scenario” z widocznym obrysem `:focus-visible`. Test wykonano na produkcyjnym preview.

## Ograniczenia

Chrome DevTools nie udostępnił dokładnego `innerWidth` 781 px, więc raport zachowuje rzeczywisty wynik 782 px zamiast deklarować sprawdzenie brakującego piksela. Nie wymuszono osobno nieprzezroczystego, klasycznego paska przewijania; pomiar wykonano przy pasku dostępnym w bieżącej konfiguracji Chrome/Windows. Oględziny oraz pomiar szerokości nie zastępują pełnego audytu dostępności E-008 ani sprawdzenia na fizycznym telefonie.

Podczas podglądu konsola zgłosiła żądanie `favicon.ico` z odpowiedzią 404. Nie wpływa ono na pomiary układu i nie należy do zakresu E-021; wymaga osobnej decyzji o brakującym zasobie.

WCAG 2.2 SC 1.4.3 wymaga co najmniej 4.5:1 dla zwykłego tekstu, z wyjątkami opisanymi w kryterium: [W3C WCAG 2.2](https://www.w3.org/TR/2023/REC-WCAG22-20231005/). Te statyczne obliczenia nie zastępują pełnego audytu UI w E-008.

## Follow-up po K-037 i synchronizacji aktualnej mapy — stan historyczny

2026-11-15: Rezerwację follow-upu opublikowano na `origin/main`. PR #35 zsynchronizowano z aktualnym main; konflikt CSS rozwiązano, zachowując style MapLibre z E-004, kontrolki E-005 i poprawki czytelności E-021. Nowe etykiety mapy o rozmiarze 7–8 px podniesiono do 9 px, również w mobilnych nadpisaniach. Skan deklaracji `font`/`font-size` w `apps/web/src/styles.css` zwraca zero tekstów poniżej 9 px.

Dla nowych etykiet MapLibre obliczono kontrast z luminancji sRGB po złożeniu przezroczystych warstw CSS z bazowym tłem mapy. Reprezentatywne pary:

| Element | Tekst / złożone tło | Kontrast |
|---|---|---:|
| Kontekst mapy | `#a8b89a` / `#111b1c` | 8.34:1 |
| Etykieta stanu pustej mapy | `#b6cb8d` / `#121d1d` | 9.77:1 |
| Tytuł legendy | `#dce5d8` / `#101a1b` | 13.70:1 |
| Opisy rampy | `#c0ccc2` / `#0d1516` | 11.14:1 |
| Klucze legendy | `#b5c0b8` / `#101a1b` | 9.44:1 |
| Stopka mapy | `#a0ada5` / `#0d1516` | 7.94:1 |
| Etykieta inspectora | `#b6cb8d` / `#131e1e` | 9.67:1 |
| Tekst szczegółu inspectora | `#d6ed85` / `#131e1e` | 13.24:1 |
| Status mapy | `#b7c5ba` / `#131f1f` | 9.42:1 |
| Ostrzeżenie mapy | `#e4b5a7` / `#131f1f` | 9.22:1 |
| Tag kontraktu | `#9aaba0` / `#172122` | 6.82:1 |
| Numer znacznika rankingu | `#f3f5e9` / `#172625` | 14.21:1 |

`npm test --prefix apps/web` — 40/40; `npm run build --prefix apps/web` — typecheck i build produkcyjny przechodzą. Vite nadal ostrzega, że asynchroniczny chunk mapy ma 1,085.35 kB minified. `python tools/check_planning.py` — OK (156 Markdown, 36 JSON, 77 kart, 5 synthetic cases). Build i statyczne obliczenia nie dowodzą zachowania layoutu.

Próba otwarcia lokalnego preview została zatrzymana przez politykę URL przed załadowaniem strony. Nie ma świeżych `innerWidth`/`clientWidth`/`scrollWidth`/`body.scrollWidth`, zrzutów, oględzin przycięć ani sprawdzenia fokusu po tej synchronizacji. Historyczna tabela wyżej pochodzi ze starszego snapshotu; nie stanowi dowodu dla aktualnego PR. K-039 ma przeprowadzić re-review dopiero po opublikowaniu tych renderowych dowodów.

## Follow-up po K-030 i synchronizacji

2026-11-15: Po rezerwacji poprawki ponownie zbudowano produkcyjny frontend — typecheck i build przechodzą. Próba otwarcia lokalnego preview w Chrome została zatrzymana przez politykę URL Computer Use, zanim strona się załadowała. Nie uzyskano nowego screenshotu ani pomiaru `innerWidth`, `clientWidth` lub `scrollWidth`; wynik 781 px z `handoffs/e014-viewport-metrics.json` pochodzi z wcześniejszej wersji CSS i nie jest używany jako dowód dla aktualnego review.

2026-11-15: Gałąź zsynchronizowano z `origin/main` w merge commicie `2e61fb1`. Konflikt CSS rozwiązano, zachowując czytelniejsze etykiety E-021 oraz reguły kontrolek dodane przez E-005. `npm test --prefix apps/web` przechodzi (38/38), `npm run build --prefix apps/web` przechodzi (typecheck i produkcyjny build), `git diff --check` przechodzi.

Przegląd CSS po scaleniu ujawnił nowe teksty kontrolek E-005 o rozmiarze 8 px, a w widoku do 390 px 7 px. Podniesiono je do 9 px i powiększono kolumny etykiet, aby zrobić miejsce na czytelniejszy tekst. Usunięto też `opacity: .68` z wierszy niezaznaczonych kryteriów: checkbox nadal jest aktywny, a przygaszenie jednostki `#82918b` do około `#606d69` obniżało kontrast z `#172122` do 3.05:1. Bez przygaszenia etykieta wagi `#899990` ma 5.50:1, a udział wagi `#9eaea3` ma 7.08:1 na tle panelu `#172122`. Po poprawce wyszukiwanie deklaracji CSS/TSX nie znajduje tekstu poniżej 9 px.

K-030 odnotowało, że żądany viewport 781 px dał `innerWidth=782`, `clientWidth=782`, `scrollWidth=782` i `body.scrollWidth=782`. W CSS breakpointem jest `max-width: 780px`; 782 px leży po jego drugiej stronie. Proponowana zmiana kryterium zastępuje nieosiągalny dokładny pomiar 781 px faktycznie raportowanym 782 px oraz jawnie zachowuje ograniczenie, że 781 px nie zmierzono. K-037 ma ocenić zasadność tej zmiany. Nie deklarujemy braku overflow ani widocznego fokusu dla aktualnego commitu: wcześniejsze oględziny tabeli powyżej dotyczą starszego snapshotu, a bieżący podgląd został zablokowany przed załadowaniem przez Computer Use. Poszerzone kolumny etykiet również nie mają jeszcze potwierdzenia w aktualnym renderze.

## Synchronizacja z aktualnym main — stan przed powtórnym renderem, uzupełniony poniżej

Gałąź PR #35 została zaktualizowana z `origin/main` `5273ca1008aa87c339fb6ef864d80ffe307c893c` w merge commicie `99c15f908d064149645802ee37e82db966ad0b9e`. Po synchronizacji `npm test --prefix apps/web` — 40/40; `npm run build --prefix apps/web` — typecheck i produkcyjny Vite build przechodzą. Vite nadal ostrzega o asynchronicznym chunku mapy 1,085.35 kB. `python tools/check_planning.py` — OK (161 Markdown, 40 JSON, 79 kart, 5 synthetic cases), a `git diff --check origin/main...HEAD` — czysto.

Nie powstał nowy renderowy dowód. Lokalny podgląd wcześniej zablokowała polityka URL; nie ma świeżych pomiarów siedmiu szerokości, inspekcji przycięć/nakładania, testu fokusu przy 320 px ani screenshotów. Historyczna tabela responsywności pozostaje dowodem wyłącznie dla starszego snapshotu. K-039 nie powinno rozpoczynać review, dopóki te P1 nie zostaną uzupełnione.

## Bieżący production preview — poprawka lokalna, 2026-11-15

Po buildzie z lokalnego commitu `c26663ca64153399f75f3e518efc6b6607c25799` uruchomiono Vite production preview pod `http://127.0.0.1:4180/`. Oględziny wykonano w Chrome responsive mode przy wysokości 900 CSS px. Widok używa `Synthetic fixture demo` i scenariusza `Isolated hotspot`; API nie było wywoływane, a wyniki są syntetyczne i regionalne.

W przeglądarce z widocznym 15-pikselowym gutterem paska przewijania `clientWidth` jest o 15 px mniejsze od `innerWidth`. We wszystkich punktach `scrollWidth == clientWidth` i `body.scrollWidth == clientWidth`, więc nie ma poziomego overflow.

| Żądane i faktyczne `innerWidth` | `clientWidth` | `scrollWidth` | `body.scrollWidth` |
|---:|---:|---:|---:|
| 320 | 305 | 305 | 305 |
| 375 | 360 | 360 | 360 |
| 390 | 375 | 375 | 375 |
| 780 | 765 | 765 | 765 |
| 782 | 767 | 767 | 767 |
| 1150 | 1135 | 1135 | 1135 |
| 1151 | 1136 | 1136 | 1136 |

Poprawka zmienia górny margines `.field-help` z `-3px` na `3px`. Oględziny geometrii przed/po pokazują odstęp między selektorem scenariusza a jego objaśnieniem: przy 320/375/390/780 px zwiększył się z 6 do 12 px; przy 782/1150/1151 px z nachodzenia o 3 px do odstępu 3 px. Na każdym z siedmiu viewportów po poprawce nie zaobserwowano przycięć ani nakładania tekstu.

Przy 320 px fokus klawiatury sprawdzono sekwencją Tab z pola „Data source” do „Fixture scenario”. `:focus-visible` był aktywny; obrys był widoczny i miał kolor `#d6ed85` (reguła CSS: `2px solid`; przeglądarka raportowała obliczoną szerokość 1.6 px).

Odtworzenie pomiaru w konsoli DevTools: ustaw responsive viewport na każdą szerokość z tabeli i wykonaj:

```js
(() => {
  const root = document.documentElement;
  const help = document.querySelector('.field-help');
  const select = document.querySelector('#demo-scenario');
  return {
    innerWidth,
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    scenarioHelpGap: help && select
      ? Math.round((help.getBoundingClientRect().top - select.getBoundingClientRect().bottom) * 100) / 100
      : null,
  };
})()
```

Przy 320 px fokus można odtworzyć klawiaturą: kliknąć „Data source”, zamknąć menu przez Escape, nacisnąć Tab i sprawdzić `document.activeElement.matches(':focus-visible')` oraz `getComputedStyle(document.activeElement).outlineColor`.

Świeży pełnostronicowy zrzut przy 320 px po poprawce zapisano w [E-021-320px-2026-11-15-postfix.png](screenshots/E-021-320px-2026-11-15-postfix.png); pokazuje fixture `Isolated hotspot` i dodatni odstęp pod selektorem. Trzy wcześniejsze pliki PNG bez sufiksu `postfix` są ze snapshotu `99a016e` i scenariusza `Successful ranking`, więc nie są dowodem dla poprawionego renderu. Pozostałe sześć szerokości obejrzano na żywo; ich pomiary i odtwarzalna procedura są w tabeli oraz JSON, bez osobnych świeżych zrzutów.

Po zmianie CSS: `npm test --prefix apps/web` — 40/40; `npm run build --prefix apps/web` — typecheck i produkcyjny build przechodzą; `python tools/check_planning.py` — OK (180 Markdown, 41 JSON, 93 karty, 5 synthetic cases); `git diff --check` — czysto. Vite nadal ostrzega o asynchronicznym chunku mapy o rozmiarze 1,085.35 kB minified. Statyczny skan 107 deklaracji `font`/`font-size` wykrył 106 jawnych wartości px, minimum 9 px i zero tekstów poniżej 9 px. Poprawka dotyczy wyłącznie odstępu, więc wcześniejsze 39 sprawdzonych par kontrastu (minimum 4.68:1) nie zmieniają się. Nie testowano fizycznego telefonu ani nie wymuszano klasycznego scrollbara.

Commit CSS `c26663ca64153399f75f3e518efc6b6607c25799` oraz pomiary zostały opublikowane w PR #35. Status `review` opublikowano na `origin/main` jako `f3288465908d9e9843f76daf56f51aac06ba49c6`; merge do PR opublikowano w `4c4975eb5fcc45f9c2d4da163c35df3b813d4ee0`. Świeży zrzut 320 px jest dołączany w kolejnym commicie, po czym zaktualizuję exact `review_ref`. Pierwsza próba `git ls-remote` nie rozwiązała `github.com`, ale późniejsza synchronizacja i push zadziałały.
