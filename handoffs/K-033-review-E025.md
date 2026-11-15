# K-033 — Review macierzy dowodów E-025

**Decyzja:** `REQUEST_CHANGES` dla PR #50; GitHub review `5910087329`. Oceniony exact `review_ref`: `e44614187c19eb9f8898115cf4512de2bc9078b9`. Bieżący head PR podczas review: `6c1bb7c8282bec5291f124312c716d047d4dd15e`; `submission/evidence-matrix.md` jest w nim identyczny z ocenionym refem.

## Sprawdzenia

- `python tools/check_planning.py` — OK: 143 Markdown, 32 JSON, 71 kart, bez cykli, 5 syntetycznych przypadków. To waliduje lokalny `origin/main`, nie działanie produktu.
- `git diff --check fd2a9f5a71e9d039e3e7c538621d7f42e24f23bf e44614187c19eb9f8898115cf4512de2bc9078b9` — czysto.
- Kontrola linków względnych w macierzy exact ref — 13/13 istnieje; linki zewnętrzne pominięto w tym sprawdzeniu.
- Porównałem każdą sekcję `docs/sources/03-submission.md` z polami macierzy, `docs/SUBMISSION.md` i szablonem `submission/project-template.md`.
- PR #50 jest otwarty, head `6c1bb7c...`, baza PR to `fd2a9f5...`, podczas gdy aktualny `origin/main` to `8b17e17...`. Macierz nie została odświeżona od `review_ref`.

## Ustalenia wymagające poprawy

### P1 — nieaktualne stany review i produktu (wiersze 9 i 14)

Macierz mówi, że K-028 i K-031 czekają na review, a E-004/E-005/E-021 są w tym samym stanie. Aktualne dowody w `origin/main`:

| Obszar | Aktualny stan | Korekta w macierzy |
|---|---|---|
| E-005 / K-028 | K-028 jest `done`, zaakceptował exact `98be49cac38e6d72245a092e7a59bab7c5599424` (GitHub review `5909896192`); PR #31 pozostaje otwarty i kod nie jest zintegrowany | Review zaakceptowane; integracja nadal oczekuje |
| E-021 / K-030 | K-030 jest `done` z `REQUEST_CHANGES` (`5909971282`); E-021 jest `in_progress`; wymagane 781 px dało `innerWidth=782` | Zapisać wynik i aktywną poprawkę, nie „review pending” |
| E-004 / K-032 | K-032 zaakceptował exact `e63ded588f07b9925c54075a31e581d07bfc5fc9` (review `5910052573`); PR #37 pozostaje otwarty i nie jest zintegrowany | Review zaakceptowane; status PR/integracji nadal otwarty |
| I-012 / K-031 | K-031 jest `done` z `REQUEST_CHANGES` (`5910015378`); PR #46 i I-012 pozostają otwarte / `review` | Zmienić „review pending” na wynik zmian wymagających poprawy; nie oznaczać disclosure jako kompletnego |

E-023 i E-024 oraz ograniczenia K-004/K-005 są zgodne ze źródłowymi kartami. K-007/K-008 nie są ukończone. E-004 lazy-map nadal wymaga wpisu I-013, który oczekuje na integrację I-012.

### P1 — niepełne mapowanie wymagań S03 (wiersze 7, 10, 14 i bramki wydania)

Macierz prawidłowo wymienia limity demo: film do 30 sekund albo prezentacja do 7 slajdów z tytułowymi. Pomija jednak kilka konkretnych warunków z lokalnego S03, przez co nie pokrywa w pełni wymagań dla każdego pola:

- **Język:** treści formularza i materiałów po angielsku; film może mieć inną mowę, jeśli ma angielskie napisy.
- **Dostęp i format plików:** publiczne linki bez logowania są wspomniane, ale brakuje reguły hostowania dokumentów/filmów zewnętrznie oraz limitu bezpośrednio dodawanych obrazów JPG/PNG/GIF do 10 MB.
- **Osoby:** brak statusu dla członków zaakceptowanych w tym samym evencie oraz reguły, by materiały nie pokazywały rozpoznawalnych osób niepełnoletnich. Kamil potwierdził w bieżącej rozmowie, że zespół i oboje członkowie są zarejestrowani/zaakceptowani, Team Ownerem jest Kamil, a wydarzeniem jest Universal Event; projektowy tytuł rejestracyjny nadal nie został potwierdzony. Nie pytaj ponownie o znaną rejestrację — zapisz potwierdzone fakty i pozostaw tylko rzeczywiście nieznany tytuł.
- **AI/SI:** obecny opis wspomina o rejestrze i braku AI-generated measurements, lecz nie mapuje etykiet/znaków wodnych dla generowanych obrazów i wideo, oznaczania audio, wymaganych opisów/metadanych kodu i danych ani zakazu generowania brandingu NASA. Dla aktualnego stanu bez mediów można zapisać „brak”, ale reguły muszą pozostać jawne dla przyszłego pakietu.
- **Okno i event:** S03 wiąże Universal Event z miejscem zamieszkania Team Ownera i dopuszcza wcześniejszy lokalny pitch. Dodaj pole do potwierdzenia terminu/strefy przez Kamila jako Team Ownera; nie wyciągaj miejsca zamieszkania z ustawień środowiska.

Dla każdego nowego stanu dopisz dowód, bezpieczną granicę twierdzenia, brakujący dowód i konkretnego właściciela. Wiersze Summary/problem (8) oraz Demo/project URL (10) nie wskazują jasno, kto odpowiada za przygotowanie brakującej treści i linków; przypisz Ewelinę dla materiałów/E-010 i Kamila dla potwierdzeń naukowych/danych.

## Elementy potwierdzone

- Dokument jest jawnie oznaczony jako wewnętrzny, nie do uploadu; `docs/SUBMISSION.md` i macierz zachowują human-only I-006.
- Wiersze wyników i ograniczeń nie twierdzą, że istnieje realny globalny Top 10, gotowy publiczny demo lub działające live search; fixture'y są rozróżnione od odkryć.
- Role NASADEM (regionalna walidacja), ETOPO (NOAA), LOLA/MOLA (NASA PDS) i GSHHG (maska lądu) są rozdzielone. K-017 nie jest wyolbrzymiany do globalnego rankingu.

## Następny krok

Ewelina: zsynchronizować PR #50 z najnowszym `origin/main`, poprawić wiersze ze statusami oraz brakujące wymagania/odpowiedzialności, zachowując wewnętrzny charakter macierzy. Opublikować nowy exact SHA w PR #50 i poprosić o re-review K-033. E-025 nie powinno przejść do `done` do poprawy i integracji. Formalnego submission nie wykonywano.
