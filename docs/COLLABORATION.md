# Współpraca dwóch komputerów przez remote

## Podział

Kamil odpowiada za wiarygodność danych, metodę i obliczenia. Ewelina odpowiada za czytelność i działanie produktu w przeglądarce oraz pakiet prezentacyjny. Każda osoba przegląda rezultat drugiej: Ewelina sprawdza zrozumiałość wyniku, Kamil sprawdza zgodność prezentowanych twierdzeń z danymi.

To dwie równoległe ścieżki, a nie dwa niezależne produkty. Wspólnym punktem jest kontrakt i fixture. Własność ścieżek wskazuje `AGENTS.md`; każda karta ma dokładniejszy zakres.

## Repozytorium i gałęzie

Repo: **[kamilr2000/Ewkam_Lab_NASA](https://github.com/kamilr2000/Ewkam_Lab_NASA)**, remote `origin`, wspólna gałąź `main`. Jest prywatne. Konto Kamila: `kamilr2000`; konto Eweliny: `ewelixa`. Wysłano zaproszenie dla `ewelixa` z uprawnieniem **write**; Ewelina musi je zaakceptować, zanim uzyska zapis. Każda osoba używa własnej tożsamości Git przy tworzeniu commitów.

Kamil i Ewelina mają osobne klony na swoich komputerach, w dowolnych katalogach. Instrukcje nie zakładają wspólnego dysku ani tej samej ścieżki. Po zaakceptowaniu zaproszenia Ewelina klonuje `https://github.com/kamilr2000/Ewkam_Lab_NASA.git`.

`origin/main` jest źródłem prawdy dla rezerwacji, zależności i zakończonych zadań. Zdalne gałęzie pokazują implementację w toku. Wszystkie poprawki, karty, kontrakty i handoffy przechodzą przez remote. Lokalny commit lub plik nie jest przekazaniem drugiej osobie.

Nazwy gałęzi: `kamil/K-006-scoring`, `ewelina/E-004-map`, `integration/I-003-acceptance`. Implementacja trafia do `main` przez mały PR, z ID karty i wynikami sprawdzeń. Zmiany koordynacyjne na `main` ograniczamy do kart, indeksu i niezbędnych ustaleń. Widoczności repo nie zmieniamy automatycznie; udostępnienie jury wymaga osobnego przygotowania.

## Obowiązkowy commit IN PROGRESS przed zadaniem

1. Uporządkuj własne zmiany bez ich usuwania, przejdź do `main`, wykonaj `git fetch origin` i zaktualizuj lokalny `main` względem `origin/main`.
2. Sprawdź zdalną kartę i ukończone zależności. Wybierz własne, wolne P0.
3. Zmień tylko kartę: `status: in_progress`, `agent`, `updated`, planowana `work_branch` i wpis rozpoczęcia.
4. Utwórz osobny commit, np. `tasks(K-006): IN PROGRESS`.
5. Ponownie pobierz `origin`. Po przesunięciu `main` połącz zmiany, sprawdź rezerwację i rozwiąż konflikty. Jeżeli tę samą kartę wcześniej zajął inny agent, zachowaj jego rezerwację i wybierz inną kartę.
6. Wyślij rezerwację do `main` zwykłym pushem. Jeżeli `main` jest chronione, doprowadź do połączenia małego PR zawierającego rezerwację.
7. Potwierdź, że aktualne `origin/main` zawiera Twojego agenta i `in_progress`. Dopiero wtedy rozpocznij implementację.

Wartość `in_progress` oznacza status **IN PROGRESS**. Push samej gałęzi zadania ani niepołączony PR nie rezerwuje karty. Pierwszeństwo ma rezerwacja przyjęta do `origin/main`, nie wcześniejszy lokalny czas commita.

Przykład dla K-006; wykonuj komendy pojedynczo, sprawdzając rezultat:

```text
git switch main
git fetch origin
git merge --ff-only origin/main
# Sprawdź i edytuj tasks/K-006.md.
git add -- tasks/K-006.md
git commit -m "tasks(K-006): IN PROGRESS"
git fetch origin
# Sprawdź, czy ktoś nie zajął tej samej karty, i połącz nowe zmiany.
git merge origin/main
git push origin main
git fetch origin
git show origin/main:tasks/K-006.md
```

Przy błędzie zatrzymaj ten ciąg i rozwiąż przyczynę. Odmowa fast-forward wymaga kontroli historii i połączenia obu prac, nie resetu. Wyjątek: w I-001 samo utworzenie pustego repo wymaga lokalnego commita startowego; trafia on do pierwszego pushu, bo wcześniej `origin/main` nie istnieje. Kolejne zadania nie mają tego wyjątku.

## Każda poprawka kończy się pushem

Po opublikowaniu rezerwacji utwórz gałąź zadania z aktualnego `main` i opublikuj ją przez `git push -u origin HEAD`.

1. Przed kolejną partią pobierz remote i połącz potrzebne zmiany z `origin/main` oraz zdalnej wersji własnej gałęzi.
2. Wykonaj małą poprawkę, sprawdź ją i zrób commit zawierający ID zadania. Dotyczy to także dokumentacji, fixture'ów, kart i kontraktów.
3. Przed wysłaniem ponownie pobierz remote. Jeśli doszły zmiany, połącz je, rozwiąż rzeczywiste konflikty i sprawdź rezultat.
4. Od razu wyślij nowe commity zwykłym pushem na zdalną gałąź. Nie odkładaj synchronizacji do końca dnia lub zadania. Potwierdź powodzenie przed kolejną partią.

Częściowy kod może być w gałęzi i draft PR. Nie może udawać gotowego rozwiązania w `main`. Konflikty nie występują automatycznie przy każdym commicie; obowiązkowa jest synchronizacja i rozwiązanie tych, które faktycznie powstaną.

Przy odrzuconym pushu: fetch → przegląd zmian → merge właściwej gałęzi → rozwiązanie konfliktów z zachowaniem obu prac → odpowiednie kontrole → push. Bez force-pusha, przepisywania opublikowanej historii, resetu usuwającego pracę oraz globalnego wyboru `ours`/`theirs`. Przy sprzecznym znaczeniu kontraktu zapisz pytanie w karcie lub komentarzu PR zamiast zgadywać.

Jeżeli remote jest niedostępne, zabezpiecz lokalne zmiany, napraw dostęp i zgłoś niewysłane SHA. Nie rozpoczynaj nowego zadania na podstawie lokalnej rezerwacji i nie nazywaj niewysłanego commita przekazanym.

## Kolejka i status

Źródło prawdy to oddzielne pliki `tasks/K-*.md`, `tasks/E-*.md` i `tasks/I-*.md`. Indeks `tasks/README.md` pokazuje kolejność i zależności, nie duplikuje aktualnego statusu.

Dozwolone statusy: `todo`, `in_progress`, `blocked`, `review`, `done`, `cancelled`. Gotowe do podjęcia = wszystkie zależności ukończone, brak innego właściciela aktywnie wykonującego kartę, spełnione warunki startu. Jedna aktywna karta implementacyjna na agenta; niezależne drobne uzupełnienia dokumentacji są dopuszczalne.

Każda zmiana statusu ma commit i skuteczny push do `main`, ewentualnie przez połączony mały PR. `review` oznacza wynik opublikowany na zdalnej gałęzi / w PR, gotowy do odbioru. `done` publikuj dopiero po spełnieniu kryteriów i połączeniu rozwiązania do `origin/main`. Przy `blocked` zapisz konkretny warunek, obejście i zależność. Przy `done` odhacz kryteria i dodaj dowód sprawdzenia.

Statusy koordynacyjne zmieniaj na aktualnym `main`. Jeśli gałąź robocza zawiera starszą kartę, przy integracji zachowaj aktualny zdalny stan i faktyczny etap pracy. Zależność jest gotowa dla drugiego komputera dopiero po pobraniu opublikowanego rozwiązania i statusu. Wiadomość „gotowe” bez dostępnego commita nie wystarcza.

## Jak agent dodaje odkryte zadanie

1. Sprawdź istniejące karty i duplikaty.
2. Utwórz nowy plik z [TEMPLATE](../tasks/TEMPLATE.md): następny wolny ID odpowiedniego toru, np. `K-012.md`, `E-012.md`, `I-007.md`.
3. Wpisz właściciela, priorytet, zależności, pliki, powód odkrycia i testowalne kryteria. Dodaj `discovered_from`, np. ID karty lub konkretne źródło.
4. Dodaj link do sekcji „Odkryte zadania” w indeksie. Indeks jest plikiem wspólnym; przy jednoczesnych zmianach zachowaj obie pozycje.
5. Jeśli nowe zadanie blokuje starą kartę, dopisz zależność i powód. Unikaj cykli.
6. Opublikuj nową kartę i indeks w `main` jako zmianę koordynacyjną. Przy kolizji ID zachowaj obie karty, nadając różne numery i poprawiając odnośniki. Przed wykonaniem nowego zadania zrób osobną rezerwację IN PROGRESS.
7. P0 = konieczne do uzgodnionego MVP / prawidłowości / zgłoszenia. P1 = rozszerzenie po MVP. P2 = dalszy rozwój. Pomysł nie staje się P0 tylko dlatego, że jest ciekawy.

Zmiany zakresu mają wpis w `docs/DECISIONS.md`, z powodem i skutkiem. Rozszerzenie wymagające dodatkowych kont, kosztów lub zmiany celu najpierw opisujemy jako propozycję; niezależne P0 są kontynuowane.

## Przekazywanie rezultatów

`handoffs/TEMPLATE.md` → `handoffs/<task-id>-<slug>.md`. Wpis zawiera: co gotowe, zdalną gałąź/URL PR, wysłane SHA, stan połączenia do `main`, jak odtworzyć, wersje kontraktu i danych, sprawdzenia, ograniczenia i czego potrzebuje druga strona. Opublikuj handoff w remote; plik tylko na własnym dysku nie jest przekazaniem.

Wczesne przekazania:

- K-003 → E-003: schema, przykłady sukcesu/pustego wyniku/błędu i hotspotu.
- K-007 → E-006: działające API z regionalnymi danymi, zgodne z fixture.
- K-008 → E-007: globalny zbiór, pokrycie i agregaty maksimum po wyniku łącznym.
- E-006 → K-009: ekran pokazujący wkłady oraz reprodukowalna konfiguracja.
- E-010 → I-005: publiczny pakiet z jasno rozdzielonym stanem wykonanym i planowanym.

Krótki wspólny przegląd po G1, G2 i przed zgłoszeniem. Komunikaty mają identyfikator karty i konkretny zdalny rezultat. Repo utworzono 2026-11-14 jako prywatne i opublikowano początkowe przygotowanie oraz poprawki przez main (30b19ff). Zaproszenie write dla ewelixa oczekuje na przyjęcie; potem Ewelina potwierdza zapis ze swojego komputera. Bieżące potwierdzenia są w I-001.
