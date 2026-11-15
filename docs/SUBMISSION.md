# Pakiet zgłoszeniowy

**Stan na 15 listopada 2026:** przygotowano angielski opis i siedmioslajdowe demo na podstawie lokalnie przetestowanego MVP z PR #96 (E-006, head `c0df63a50f196ef89793ec1345d3c5ca3636d18c`). E-006 pozostaje przekazane do odbioru i nie jest jeszcze w `origin/main`. Pakiet nie twierdzi, że jest to wydanie publiczne.

Agent przygotowuje treść, źródła i demo. Formalne zgłoszenie do NASA Space Apps wykonuje osobiście Kamil albo Ewelina. Agent nie klika Submit for Judging, nie wysyła odpowiedniego żądania API, nie składa oświadczeń ani nie akceptuje regulaminu w imieniu człowieka.

## Gotowe materiały

- [`submission/project-description.md`](../submission/project-description.md) — angielski opis, działanie MVP, przykładowe wyniki, źródła i prawa, narzędzia, ujawnienie AI oraz ograniczenia.
- [`submission/terra-analog-demo.pptx`](../submission/terra-analog-demo.pptx) — dokładnie 7 slajdów z tytułowym, poniżej limitu S03; slajdy i speaker notes przejrzano wizualnie i tekstowo.
- [`submission/README.md`](../submission/README.md) — status pakietu i lista wymaganych czynności człowieka.

## Stan dowodów

Opis przedstawia dwa odtworzone lokalnie przebiegi rzeczywistego API: Jezero/MOLA + regionalny pakiet Atacama–Andes oraz księżycowy biegun południowy/LOLA + Hawaii Big Island. Zapisano identyfikatory profili, wersje pakietów, liczności, konfigurację, metryki, hotspot i `analysis_id`. Użycie NOAA ETOPO jako źródła skanowanych komórek i NASA MOLA/LOLA jako profili referencyjnych jest rozdzielone. NASADEM opisano wyłącznie jako osobną walidację pomiarów ziemskich. Wynik 100% opisano jako zgodność trzech wybranych cech z eksperymentalnymi przedziałami profilu, nie jako habitability, prawdopodobieństwo czy ogólną analogię środowisk.

Globalny zakres zwrócił `SCOPE_UNAVAILABLE`; globalnego rankingu nie wykonano. Wymieniony deck jest lokalnym plikiem, repozytorium pozostaje prywatne, a publiczny deploy i dostęp anonimowy nie są zweryfikowane. PR #96 nie jest zintegrowany w `origin/main`. Strona przewodnika S03 zwróciła HTTP 502 przy bieżącym sprawdzaniu; obowiązujący lokalny snapshot w repo ma datę odczytu 14 listopada 2026. Link i aktualne warunki należy potwierdzić przed wysyłką.

## Kontrola I-005 — status

- [x] Angielski opis i demo są przygotowane; nie przedstawiają P1 ani globalnego skanu jako gotowych funkcji.
- [x] Opisano konkretne realne lokalne przebiegi i odróżniono je od jawnie oznaczonych fixture'ów syntetycznych.
- [x] Dane NASA mają przypisaną rolę: MOLA/LOLA w profilach referencyjnych, NASADEM w odrębnej walidacji.
- [x] Źródła i wersje danych oraz użyte biblioteki są wymienione; brak niezweryfikowanego NASA endorsement.
- [x] Publiczne ujawnienie AI wskazuje pomoc w kodzie, źródłach, tłumaczeniu i prezentacji; nie przypisuje AI pomiarów.
- [x] Demo ma 7 slajdów z tytułowym i nie zawiera generatywnych mediów ani brandingu NASA.
- [x] Ograniczenia, braki, wymiary siatki i charakter eksperymentalnego wyniku są opisane.
- [ ] Publiczny adres projektu/decku i dostęp bez logowania — nie istnieją lub nie zostały zweryfikowane.
- [ ] Kamil potwierdza roszczenia naukowe oraz aktualny status E-006 przed użyciem opisu.
- [ ] Człowiek potwierdza event/team owner, wcześniejszy lokalny pitch, skład i warunki formularza.
- [ ] Człowiek wypełnia formularz, osobiście wysyła zgłoszenie i zachowuje potwierdzenie.

## Wymagane czynności człowieka

1. Potwierdź właściwy event, konto/team owner, członków zespołu i lokalny termin. Snapshot S03 podaje do 15.11.2026 23:59 czasu Local Event, ale wcześniejszy lokalny pitch może mieć inny termin.
2. Po odbiorze i integracji PR #96 wdroż UI/API pod publicznym adresem; publicznie hostuj deck. Otwórz oba linki w oknie bez logowania i sprawdź faktyczną wersję.
3. Kamil sprawdza twierdzenia naukowe, liczby, źródła, prawa i ograniczenia. Uzgodnij publiczne ujawnienie AI z wewnętrznym rejestrem przez przypisane zadania I-012/I-013/E-028.
4. Osobiście wprowadź tekst i publiczne linki do właściwej strony zespołu. Samo zapisanie draftu nie jest zgłoszeniem.
5. Osobiście sprawdź obowiązkowe pola, oświadczenia i regulamin; użyj Submit for Judging, po czym zachowaj URL, czas ze strefą i komunikat powodzenia.

Zobacz [S03 — lokalny snapshot wymagań 2026](sources/03-submission.md), [pakiet angielski](../submission/README.md) oraz [I-006](../tasks/I-006.md). Wysyłka pozostaje `human_only`; agent kończy na sprawdzonym pakiecie do ręcznego użycia.
