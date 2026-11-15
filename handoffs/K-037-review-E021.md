# K-037 — Re-review E-021 po korekcie kontrolek kryteriów

**Decyzja:** `REQUEST_CHANGES` dla PR #35. Re-review dotyczy exact `review_ref` `874d41ab92290146f0a9f9484a75f5a8f15c30a8`. W chwili sprawdzenia bieżący head PR #35 to `5c180e0a339e9667745d689a4b2ab7fd3284755e`; plik `apps/web/src/styles.css` jest identyczny z wersją w `review_ref`.

## Sprawdzenia exact CSS

- Teksty kontrolek kryteriów mają co najmniej 9 px również w mobilnym nadpisaniu do 390 px: nazwa 10 px, jednostka i stan 9 px, etykieta i znormalizowany udział wagi 9 px. Wyszukiwanie deklaracji `font-size`/`font` poniżej 9 px w exact `styles.css` nie zwróciło wyników.
- Usunięto `.criterion.is-disabled .criterion-copy { opacity: .68; }`. Niezaznaczone kryteria nadal pozostają aktywne przez checkbox; ich tekst nie jest przygaszany przez tę regułę.
- Niezależnie przeliczono pary sRGB metodą względnej luminancji. Wszystkie sprawdzone wartości z handoffu są zgodne:

| Element | Tekst / tło | Kontrast |
|---|---|---:|
| Etykieta wagi | `#899990` / `#172122` | 5.50:1 |
| Znormalizowany udział | `#9eaea3` / `#172122` | 7.08:1 |
| Pomoc pola | `#81918a` / `#172122` | 4.97:1 |
| Opis banera danych syntetycznych | `#93a199` / `#202a26` | 5.49:1 |
| Opis w rankingu | `#84938b` / `#172122` | 5.11:1 |
| Metadane piksela | `#7d8d84` / `#172122` | 4.71:1 |
| Tekst źródła cechy | `#82918b` / `#1a2425` | 4.82:1 |
| Znacznik pustego stanu | `#7e8c85` / `#172122` | 4.68:1 |

## Viewporty

Jawnie zmienione kryterium 780/782 px jest uczciwe i użyteczne: 780 px sprawdza stronę breakpointu `max-width: 780px`, a faktyczne 782 px leży po jego drugiej stronie. Ta para nie dowodzi pomiaru dokładnie przy 781 px; handoff i karta poprawnie zachowują to ograniczenie.

**P1 — właściciel: Ewelina.** Brakuje dowodów z renderu po aktualnej synchronizacji z kontrolkami E-005 i po zmianie ich szerokości/typografii. Wcześniejsze pomiary oraz fokus pochodzą ze starszego snapshotu; bieżące `innerWidth`, `clientWidth`, `scrollWidth`, oględziny przycięć/nakładania i fokus nie są potwierdzone. Przed oznaczeniem E-021 jako `done` zbuduj preview z aktualnego headu, sprawdź faktycznie raportowane szerokości 320/375/390/780/782/1150/1151 px i zapisz dla każdej `innerWidth`, `clientWidth`, `scrollWidth` oraz `body.scrollWidth`. Obejrzyj aktualny widok pod kątem przycięć/nakładania i potwierdź fokus klawiatury przy 320 px; dołącz zrzuty lub równoważny odtwarzalny dowód do handoffu. Następnie poproś o re-review. Nie przedstawiam starszych pomiarów jako wyniku bieżącego CSS.

## Testy i ograniczenia

- Na bieżącym headzie PR #35 `5c180e0a339e9667745d689a4b2ab7fd3284755e`: `npm run test` w `apps/web/` — 38/38; `npm run build` — typecheck i produkcyjny build Vite przechodzą.
- `python tools/check_planning.py` przechodzi: 151 plików Markdown, 32 JSON, 75 kart; `git diff --check` czyste.
- Nie załadowano aktualnego preview w przeglądarce i nie wykonano nowych pomiarów ani oględzin renderu. Wyniki builda i testów nie dowodzą zachowania layoutu.

## Następny krok

PR #35 pozostaje własnością Eweliny. Po dodaniu pomiarów oraz zrzutów z aktualnego renderu poproś o re-review; do tego czasu kryterium responsywności/fokusu pozostaje otwarte i E-021 nie powinno przejść do `done`.
