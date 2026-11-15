# K-039 — Re-review E-021 po poprawce odstępu

Data: 2026-11-15
Wynik: **RECOMMEND APPROVE** dla zakresu czytelności UI i responsywnego renderu E-021 na sprawdzonym refie. Nie oznacza to integracji ani statusu `done`.

## Sprawdzone refy

- Exact evidence ref E-021: `bff33641cf44906ad3ad8fbe073e55cc6e3ccf42`.
- Aktualny head PR #35: `a2087b0fde4bd2968cffcc34ab956839f7492c3b`.
- Aktualny `origin/main`: `18803b793019069f87ce1fd2d51ebd78d24831e4`; jest przodkiem gałęzi PR.
- GitHub raportuje PR jako otwarty i `mergeable=true`.
- Karta E-021 na `origin/main` ma `status: review` i wskazuje exact evidence ref `bff3364...`.

Poprzednia rekomendacja K-039 dotyczyła wyłącznie starszego renderu `Successful ranking`; została wycofana po odkryciu nakładania tekstu helpera z selektorem przy szerokim layoucie. Obecny wynik ocenia poprawkę CSS oraz render `Isolated hotspot` z opublikowanym zrzutem i pomiarami.

## Wyniki renderu

Render pochodzi z lokalnego Vite production preview na commitcie CSS `c26663ca64153399f75f3e518efc6b6607c25799`. Użyto syntetycznego fixture `Isolated hotspot`, bez wywołania live API. Przykład jest regionalny, syntetyczny i nie przedstawia rankingu planetarnych danych.

| Żądane i faktyczne `innerWidth` | `clientWidth` | `scrollWidth` | `body.scrollWidth` | Odstęp selector–helper po poprawce |
|---:|---:|---:|---:|---:|
| 320 | 305 | 305 | 305 | 12 px |
| 375 | 360 | 360 | 360 | 12 px |
| 390 | 375 | 375 | 375 | 12 px |
| 780 | 765 | 765 | 765 | 12 px |
| 782 | 767 | 767 | 767 | 3 px |
| 1150 | 1135 | 1135 | 1135 | 3 px |
| 1151 | 1136 | 1136 | 1136 | 3 px |

Chrome miał widoczny 15-pikselowy gutter scrollbara, dlatego `clientWidth` jest o 15 px mniejszy od `innerWidth`. We wszystkich punktach `scrollWidth == clientWidth == body.scrollWidth`, czyli poziomego overflow nie ma.

Przed poprawką odstęp wynosił 6 px przy 320/375/390/780 i `-3 px` przy 782/1150/1151; szeroki układ nachodził helperem na selector o 3 px. E-021 zmieniło `.field-help` margin z `-3px` na `3px`. Po poprawce dodatni odstęp i brak nakładania były widoczne we wszystkich siedmiu oglądanych szerokościach.

Przy 320 px klawiaturowy Tab z „Data source” do „Fixture scenario” pokazał aktywne `:focus-visible`. Obrys był widoczny i miał kolor `#d6ed85`; reguła CSS to `2px solid`, a przeglądarka raportowała obliczoną szerokość 1.6 px.

Świeży pełnostronicowy zrzut 320 px po poprawce: [E-021-320px-2026-11-15-postfix.png](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/E-021-ui-readability/handoffs/screenshots/E-021-320px-2026-11-15-postfix.png). Zrzut pokazuje ten sam fixture i dodatni odstęp. Pozostałe sześć szerokości obejrzano na żywo, a ich wymiary i geometryczny odstęp są w tabeli oraz [JSON z procedurą odtworzenia](https://github.com/kamilr2000/Ewkam_Lab_NASA/blob/ewelina/E-021-ui-readability/handoffs/e021-viewport-metrics-2026-11-15.json). Nie zapisano osobnych świeżych PNG dla tych sześciu szerokości; stare screenshoty ze scenariusza `Successful ranking` są jawnie oznaczone w handoffie jako historyczne.

## Statyczne sprawdzenia i build

- Skan CSS/TS/TSX: 107 deklaracji `font`/`font-size`, 106 z jawnym px, minimum 9 px, zero tekstów poniżej 9 px.
- Wcześniejsze 39 sprawdzonych par foreground/background z luminancji sRGB pozostają niezmienione przez fix odstępu; minimum to 4.68:1.
- `npm test --prefix apps/web` — 40/40.
- `npm run build --prefix apps/web` — typecheck i produkcyjny build przechodzą; Vite ostrzega o async map chunku 1,085.35 kB minified.
- `python tools/check_planning.py` — OK (182 Markdown, 40 JSON, 94 task cards, 5 synthetic cases).
- JSON pomiarów z exact PR branch parsuje się poprawnie i zawiera siedem szerokości; `git diff --check` przechodzi.

## Dispozycja i ograniczenia

Nie ma otwartego P1 w zakresie CSS czytelności i zbadanych szerokości. Odtwarzalne pomiary dokumentują wszystkie siedem szerokości; świeży PNG jest dla viewportu 320 px, a pozostałe sześć mają live visual inspection i powtarzalną procedurę DevTools. To spełnia warunek alternatywnego odtwarzalnego dowodu w E-021, ale nie należy twierdzić, że zapisano screenshoty dla wszystkich viewportów.

Nie testowano fizycznego telefonu ani nie wymuszano klasycznego, nieoverlayowego scrollbara. To nie jest pełny audyt dostępności E-008. Testy, build i syntetyczny fixture nie dowodzą jakości danych planetarnych.

Formalna akcja GitHub `APPROVE` została odrzucona, ponieważ połączone konto jest autorem PR #35. Wynik oraz korekta poprzedniej rekomendacji są opublikowane w komentarzu [K-039 na PR #35](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/35#issuecomment-6895059234). E-021 pozostaje `review` do integracji i akceptacji przez właściciela; karta K-039 należy do Kamila i nie jest edytowana w tym raporcie.
