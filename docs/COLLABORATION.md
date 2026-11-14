# Współpraca Kamila i Eweliny

## Podział

Kamil odpowiada za wiarygodność danych, metodę i obliczenia. Ewelina odpowiada za czytelność i działanie produktu w przeglądarce oraz pakiet prezentacyjny. Każda osoba przegląda rezultat drugiej: Ewelina sprawdza zrozumiałość wyniku, Kamil sprawdza zgodność prezentowanych twierdzeń z danymi.

To dwie równoległe ścieżki, a nie dwa niezależne produkty. Wspólnym punktem jest kontrakt i fixture. Własność ścieżek wskazuje `AGENTS.md`; każda karta ma dokładniejszy zakres.

## Repozytoria i gałęzie

1. Jedno repo zespołu, dla każdej osoby osobny klon. Domyślna gałąź `main` ma działać po integracji.
2. Nazwy gałęzi: `kamil/K-006-scoring`, `ewelina/E-004-map`, `integration/I-003-acceptance`.
3. Mały PR na jeden spójny zakres. Dołącz ID karty, spełnione kryteria, wynik sprawdzeń i informację o zmianie kontraktu/danych.
4. Pobierz zmiany przed integracją i rozwiązuj konflikty z zachowaniem obu rezultatów. Nie używaj resetu, force-push ani usuwania cudzej pracy jako skrótu.
5. Jeżeli oba agenty pracują w jednym katalogu, nie przełączają samodzielnie gałęzi pod drugim agentem. Zalecane osobne klony; podział plików obowiązuje także w tym samym checkout.

Publikacja repo i adresy kont nie zostały ustalone. I-001 opisuje konfigurację współdzielenia; nie ma jeszcze zdalnego origin ani zadań opublikowanych jako GitHub Issues.

## Kolejka i status

Źródło prawdy to oddzielne pliki `tasks/K-*.md`, `tasks/E-*.md` i `tasks/I-*.md`. Indeks `tasks/README.md` pokazuje kolejność i zależności, nie duplikuje aktualnego statusu.

Dozwolone statusy: `todo`, `in_progress`, `blocked`, `review`, `done`, `cancelled`. Gotowe do podjęcia = wszystkie zależności ukończone, brak innego właściciela aktywnie wykonującego kartę, spełnione warunki startu. Jedna aktywna karta implementacyjna na agenta; niezależne drobne uzupełnienia dokumentacji są dopuszczalne.

Przy rozpoczęciu wpisz `agent`, zaktualizuj `updated` i sekcję przebiegu. Przy `blocked` zapisz konkretny warunek, obejście i zależność; nie zostawiaj samego słowa „blocked”. Przy `done` odhacz kryteria i dodaj dowód sprawdzenia. PR z niedokończonym kodem może mieć `review`, nie `done`.

Karta lokalna nie blokuje równolegle innych klonów. Synchronizuj claim przez repo / ustalony kanał zespołu. W razie kolizji wykonawca o wcześniejszym uzgodnieniu zachowuje zadanie, druga strona bierze inne. Nie zakładaj, że sam plik zapewnia atomową blokadę w całym zespole.

## Jak agent dodaje odkryte zadanie

1. Sprawdź istniejące karty i duplikaty.
2. Utwórz nowy plik z [TEMPLATE](../tasks/TEMPLATE.md): następny wolny ID odpowiedniego toru, np. `K-012.md`, `E-012.md`, `I-007.md`.
3. Wpisz właściciela, priorytet, zależności, pliki, powód odkrycia i testowalne kryteria. Dodaj `discovered_from`, np. ID karty lub konkretne źródło.
4. Dodaj link do sekcji „Odkryte zadania” w indeksie. Indeks jest plikiem wspólnym; przy jednoczesnych zmianach zachowaj obie pozycje.
5. Jeśli nowe zadanie blokuje starą kartę, dopisz zależność i powód. Unikaj cykli.
6. P0 = konieczne do uzgodnionego MVP / prawidłowości / zgłoszenia. P1 = rozszerzenie po MVP. P2 = dalszy rozwój. Pomysł nie staje się P0 tylko dlatego, że jest ciekawy.

Zmiany zakresu mają wpis w `docs/DECISIONS.md`, z powodem i skutkiem. Rozszerzenie wymagające dodatkowych kont, kosztów lub zmiany celu najpierw opisujemy jako propozycję; niezależne P0 są kontynuowane.

## Przekazywanie rezultatów

`handoffs/TEMPLATE.md` → `handoffs/<task-id>-<slug>.md`. Wpis zawiera: co gotowe, commit/PR, jak odtworzyć, wersje kontraktu i danych, sprawdzenia, ograniczenia i czego potrzebuje druga strona.

Wczesne przekazania:

- K-003 → E-003: schema, przykłady sukcesu/pustego wyniku/błędu i hotspotu.
- K-007 → E-006: działające API z regionalnymi danymi, zgodne z fixture.
- K-008 → E-007: globalny zbiór, pokrycie i agregaty maksimum po wyniku łącznym.
- E-006 → K-009: ekran pokazujący wkłady oraz reprodukowalna konfiguracja.
- E-010 → I-005: publiczny pakiet z jasno rozdzielonym stanem wykonanym i planowanym.

Krótki wspólny przegląd po G1, G2 i przed zgłoszeniem. Komunikaty mają identyfikator karty i konkretny problem, nie ogólne „backend gotowy”.
