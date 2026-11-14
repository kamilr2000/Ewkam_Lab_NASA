# Instrukcje pracy dla agentów

## Kontekst i kolejność czytania

Projekt Kamila i Eweliny: ziemskie analogi regionów Marsa i Księżyca, NASA Space Apps 2026. Zadanie bieżącego etapu: wdrożyć plan opisany w repo. Początkowy commit zawiera przygotowanie, nie gotowy produkt.

Przeczytaj kolejno: `README.md`, `docs/PRODUCT.md`, `docs/METHODOLOGY.md`, `docs/CONTRACTS.md`, `docs/COLLABORATION.md`, swój prompt w `prompts/` i kartę aktualnego zadania. Źródła organizatora są w `docs/sources/`. Kamil i Ewelina pracują na osobnych komputerach; ścieżki w instrukcjach są względne do własnego klonu.

## Wspólne remote — obowiązkowe

Repozytorium zespołu: **https://github.com/kamilr2000/Ewkam_Lab_NASA**, remote `origin`, obecnie prywatne. Obie osoby potrzebują dostępu do zapisu. **Źródłem prawdy jest `origin/main`**, nie lokalny katalog ani niepołączona gałąź. Wszystkie poprawki kodu, dokumentacji, kontraktów i statusów zapisuj w małych commitach i wysyłaj do tego remote. Nie wymieniaj plików ręcznie i nie zakładaj dostępu do komputera drugiej osoby.

**Przed pierwszą zmianą implementacji każdego zadania** utwórz osobny commit `tasks(ID): IN PROGRESS`, zmieniający kartę na `status: in_progress` i zapisujący agenta, datę i gałąź. Najpierw opublikuj rezerwację w `origin/main` i potwierdź jej obecność. Sam push na gałąź roboczą lub otwarty PR nie rezerwuje zadania. Przy chronionym `main` rezerwacja musi najpierw zostać połączona przez mały PR. `in_progress` jest maszynowym zapisem statusu **IN PROGRESS**.

Następnie implementuj na gałęzi zadania; po każdej spójnej poprawce wykonaj commit, synchronizację i skuteczny push. Zwykłe commity/pushe do ustalonego repo są częścią zleconej pracy. Respektuj rzeczywiste wymagania dostępu i zgody środowiska; błąd wysyłki raportuj uczciwie. Wyjątek startowy: utworzenie pustego repo i pierwsze zasilenie w I-001 wymaga lokalnego commita, bo `origin/main` jeszcze nie istnieje. Wyjątek nie dotyczy kolejnych zadań.

## Najważniejsze wymagania

1. Oceniaj każdą kwalifikującą się komórkę w zadeklarowanej siatce; globalny Top 10 powstaje przed agregacją do wyświetlania.
2. Nigdy nie odrzucaj obszaru na podstawie średniej przed sprawdzeniem jego pikseli. Lokalne doprecyzowanie wybranych obszarów nie dowodzi globalnego optimum w wyższej rozdzielczości.
3. Zachowaj pojedyncze hotspoty. Ranking pikseli i ranking różnych obszarów mają różne nazwy i jawne parametry.
4. Brak danych oznacza `null` i powód; nie oznacza zera ani dobrego dopasowania. Porównuj komórki na tym samym zestawie aktywnych kryteriów.
5. Nie wymyślaj danych, licencji, wyników, precyzji, NASA endorsement ani potwierdzeń zgłoszenia. Dane testowe zawsze oznaczaj jako syntetyczne.
6. Metryki mają jednostki, skalę pomiaru, źródła i wersje. Nie porównuj wysokości nad różnymi planetarnymi zerami. Pochodne DEM licz z odległościami w metrach i modelem właściwego ciała niebieskiego.
7. Nie nazywaj litologii mineralogią ani NDVI miarą życia na Marsie. Warstwy pośrednie oznaczaj jako proxy.
8. Stosuj wymagania zgłoszenia z `docs/sources/03-submission.md`; dokumentuj użycie AI w `docs/AI_USAGE.md`.

## Własność

| Obszar | Właściciel |
|---|---|
| `pipeline/`, `apps/api/`, `data/`, `contracts/*.json`, `contracts/fixtures/` | Kamil |
| `apps/web/`, `submission/`, `design/` | Ewelina |
| `docs/DATA.md`, `docs/METHODOLOGY.md` | Kamil; Ewelina zgłasza uwagi |
| `docs/SUBMISSION.md` | Ewelina; Kamil sprawdza twierdzenia naukowe |
| `README.md`, `AGENTS.md`, inne wspólne docs, `.github/`, pliki główne | Właściciel aktualnego zadania I-*; domyślny integrator Kamil |
| `tasks/<id>.md` | Jedyny właściciel danej karty; każdy agent może utworzyć nową kartę |

Nie jesteś sam w repozytorium. Nie cofaj cudzych zmian. Nie edytuj pliku drugiej ścieżki bez uzgodnionego przekazania; utwórz zadanie lub wpis w `handoffs/`. Nie buduj drugiego silnika scoringu w przeglądarce.

## Pętla wykonania

1. Sprawdź własny klon, `origin`, gałąź i zmiany; pobierz aktualne remote. Nie nadpisuj niezacommitowanej pracy.
2. Wybierz gotowe P0 z aktualnych kart w `origin/main`. Zależności muszą być tam ukończone; lokalna gałąź drugiej osoby nie wystarcza.
3. Opublikuj osobny commit **IN PROGRESS** w `origin/main` i potwierdź rezerwację przed implementacją. Jeśli kartę zajął ktoś inny, nie nadpisuj jego rezerwacji.
4. Utwórz gałąź zadania z aktualnego `main`. Po każdej spójnej poprawce: sprawdzenie → commit → fetch → merge potrzebnych zmian i rozwiązanie konfliktów → sprawdzenie → push.
5. Nowe karty, zmiany statusów i uzgodnienia publikuj w remote. Nie zostawiaj ustaleń tylko w rozmowie lub na lokalnym dysku.
6. Opublikuj `review`, przekaż wynik przez zdalny PR/handoff, a po odbiorze połącz implementację do `main`. `done` publikuj dopiero po spełnieniu kryteriów i obecności rozwiązania w `origin/main`.
7. Po odrzuconym pushu ponownie pobierz remote i zachowaj obie prace. Bez force-pusha, masowego „ours/theirs” i resetu usuwającego cudze zmiany. Rozwiązuj konflikty, gdy wystąpią; nie trzeba ich tworzyć przy każdym commicie.
8. Kontynuuj gotowe P0 po synchronizacji. Gdy remote jest niedostępne, zabezpiecz pracę, napraw dostęp i raportuj niewysłane SHA; nie nazywaj ich przekazanymi ani zadania zarezerwowanym.

Logowanie, nadanie brakujących uprawnień i formalne oświadczenia mogą wymagać udziału człowieka. Przygotuj konkretne działanie i wskaż brakującą informację; nie oznaczaj go ukończonego na podstawie samej instrukcji. Commit/push do ustalonego remote jest normalnym krokiem realizacji zadania. Nie uruchamiaj dodatkowych subagentów bez prośby użytkownika.

## Standard końcowy

W raporcie podaj ID kart, zdalną gałąź, wysłane SHA / URL PR, stan połączenia do `main`, sprawdzenia, ograniczenia i kolejny krok drugiego toru. Wymień commity niewysłane z powodu blokady. Nie twierdź, że aplikacja działa, jeśli sprawdziłeś tylko dokumenty. Źródła prawdy: karta w `origin/main`, kontrakt i rejestr decyzji.
