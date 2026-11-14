# Instrukcje pracy dla agentów

## Kontekst i kolejność czytania

Projekt Kamila i Eweliny: ziemskie analogi regionów Marsa i Księżyca, NASA Space Apps 2026. Zadanie bieżącego etapu: wdrożyć plan opisany w repo. Początkowy commit zawiera przygotowanie, nie gotowy produkt.

Przeczytaj kolejno: `README.md`, `docs/PRODUCT.md`, `docs/METHODOLOGY.md`, `docs/CONTRACTS.md`, `docs/COLLABORATION.md`, swój prompt w `prompts/` i kartę aktualnego zadania. Źródła organizatora są w `docs/sources/`. Kamil i Ewelina pracują na osobnych komputerach; ścieżki w instrukcjach są względne do własnego klonu.

## Wspólne remote — obowiązkowe

Repozytorium zespołu: **https://github.com/kamilr2000/Ewkam_Lab_NASA**, remote `origin`, obecnie prywatne. Obie osoby potrzebują dostępu do zapisu. **Źródłem prawdy jest `origin/main`**, nie lokalny katalog ani niepołączona gałąź. Wszystkie poprawki kodu, dokumentacji, kontraktów i statusów zapisuj w małych commitach i wysyłaj do tego remote. Nie wymieniaj plików ręcznie i nie zakładaj dostępu do komputera drugiej osoby.

**Przed pierwszą zmianą implementacji każdego zadania** utwórz osobny commit `tasks(ID): IN PROGRESS`, zmieniający kartę na `status: in_progress` i zapisujący agenta, datę i gałąź. Najpierw opublikuj rezerwację w `origin/main` i potwierdź jej obecność. Sam push na gałąź roboczą lub otwarty PR nie rezerwuje zadania. Przy chronionym `main` rezerwacja musi najpierw zostać połączona przez mały PR. `in_progress` jest maszynowym zapisem statusu **IN PROGRESS**.

Następnie implementuj na gałęzi zadania; po każdej spójnej poprawce wykonaj commit, synchronizację i skuteczny push. Zwykłe commity/pushe do ustalonego repo są częścią zleconej pracy. Respektuj rzeczywiste wymagania dostępu i zgody środowiska; błąd wysyłki raportuj uczciwie. Wyjątek startowy: utworzenie pustego repo i pierwsze zasilenie w I-001 wymaga lokalnego commita, bo `origin/main` jeszcze nie istnieje. Wyjątek nie dotyczy kolejnych zadań.

**Pull jest obowiązkowy:** na początku sesji, przed wyborem nowego zadania i po połączeniu zmian do `main` aktualizuj własny klon. Na czystym `main` używaj `git pull --ff-only origin main`; na opublikowanej gałęzi roboczej `git pull --no-rebase`, a następnie dołącz aktualne `origin/main` przez merge. Ponawiaj synchronizację przed pushem. Sam `fetch` nie aktualizuje plików w drzewie roboczym. Jeśli masz niezapisane zmiany, najpierw bezpiecznie zachowaj własną pracę; nie nadpisuj jej ślepym pullem/resetem.

## Współpraca i zlecanie drugiemu agentowi

Każdy agent może utworzyć kartę dla drugiego: Kamil tworzy E-* z `owner: ewelina`, Ewelina tworzy K-* z `owner: kamil`; w I-* zawsze wskaż jednego właściciela. Dotyczy to implementacji, pytań o kontrakt, integracji i review. Nową kartę oraz indeks opublikuj w `origin/main`. Nie ustawiaj in_progress za drugiego agenta i nie przejmuj jego aktywnej karty.

Opisuj konkretny rezultat, powód, pliki/kontrakt, kryteria, priorytet oraz opublikowany SHA/PR. Dla przeglądu użyj `tasks/REVIEW_TEMPLATE.md`: `task_type: review`, `review_of`, `review_ref` i warunek startu. Nie dodawaj ocenianego zadania do `depends_on` przeglądu, jeśli czeka ono na review przed done — powodowałoby to blokadę. Producent zapisuje w swojej karcie `review_tasks`; przegląd rusza na opublikowanej wersji, gdy zadanie jest w review, nie dopiero po done.

Regularnie pulluj i czytaj całą kolejkę przypisaną Tobie, w tym nowe zadania dodane przez drugiego agenta. Recenzent publikuje wynik i dowody w remote. Poprawki przypisuje właścicielowi kodu; nie uznaje zmiany za poprawną bez sprawdzenia. Istotne poprawki po przeglądzie wymagają przeglądu zmienionego zakresu. Nie twórz automatycznej nieskończonej kolejki review przeglądów.

### Review ma pierwszeństwo przy wyborze następnego zadania

**Nie przerywaj bieżącego zadania z powodu nowego review.** Najpierw dokończ wykonywaną pracę i opublikuj jej wynik. Następnie zrób pull i wybierz: (1) gotowe zadanie `task_type: review` przypisane Tobie, (2) inne gotowe P0, (3) P1/P2. Gotowe review wyprzedza zwykłe zadania także wtedy, gdy w kolejce jest dwadzieścia P0; nie odkładaj go do końca backlogu.

Gotowe review wymaga spełnionych warunków startu, dostępnego `review_ref` i braku rezerwacji innego agenta. Jeśli kilka przeglądów jest gotowych, najpierw wybierz odblokowujące drugiego agenta, a w tej samej grupie najstarszą opublikowaną prośbę. Przy niedostępnym kodzie zgłoś brak i wybierz inną gotową kartę; nie czekaj bezczynnie. Sam `status: review` na karcie producenta nie jest zadaniem przeglądu dla recenzenta.

Pierwszeństwo wynika z `task_type: review`, także dla starszych kart bez `queue_priority`. Szablon zapisuje `queue_priority: review_first`; to kolejność obsługi, niezależna od merytorycznego P0/P1/P2. Recenzent nadal publikuje własny commit IN PROGRESS przed rozpoczęciem. Gotowa implementacja przekazana już do odbioru nie wymaga bezczynnego oczekiwania na cudze zatwierdzenie — przy wyborze kolejnej pracy stosuj tę kolejność. Nie przełączaj się natomiast w środku trwającej implementacji lub przeglądu.

## Formalny submission — wyłącznie człowiek

**Agenci nigdy samodzielnie nie wysyłają zgłoszenia NASA. I-006 ma executor: human_only.** Przygotujcie kompletny projekt, materiały, treści, demo, źródła i checklistę dla Kamila lub Eweliny. Nie klikajcie Submit for Judging, nie wysyłajcie równoważnego żądania API, nie składajcie oświadczeń i nie akceptujcie regulaminu w ich imieniu. Ogólny cel „ukończ projekt” nie znosi tego ograniczenia.

Submission wykonuje osobiście Kamil albo Ewelina. Po wyraźnym potwierdzeniu przez tę osobę agent może odnotować dowód i status w karcie, ale nie może sam wykonać wysyłki. Cel agenta kończy się na gotowym, sprawdzonym pakiecie do ręcznego zgłoszenia; otwarte I-006 nie blokuje ukończenia tak zdefiniowanego celu.

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
2. Po zakończeniu bieżącej pracy i pullu wybierz najpierw gotowe review przypisane Tobie, potem pozostałe P0, następnie P1/P2. Nie przerywaj rozpoczętego zadania. Sprawdź aktualne zależności i warunki startu w `origin/main`; lokalna gałąź drugiej osoby nie wystarcza.
3. Opublikuj osobny commit **IN PROGRESS** w `origin/main` i potwierdź rezerwację przed implementacją. Jeśli kartę zajął ktoś inny, nie nadpisuj jego rezerwacji.
4. Utwórz gałąź zadania z aktualnego `main`. Po każdej spójnej poprawce: sprawdzenie → commit → fetch → merge potrzebnych zmian i rozwiązanie konfliktów → sprawdzenie → push.
5. Nowe karty, zmiany statusów i uzgodnienia publikuj w remote. Nie zostawiaj ustaleń tylko w rozmowie lub na lokalnym dysku.
6. Opublikuj `review`, przekaż wynik przez zdalny PR/handoff, a po odbiorze połącz implementację do `main`. `done` publikuj dopiero po spełnieniu kryteriów i obecności rozwiązania w `origin/main`.
7. Po odrzuconym pushu ponownie pobierz remote i zachowaj obie prace. Bez force-pusha, masowego „ours/theirs” i resetu usuwającego cudze zmiany. Rozwiązuj konflikty, gdy wystąpią; nie trzeba ich tworzyć przy każdym commicie.
8. Kontynuuj gotowe P0 po synchronizacji. Gdy remote jest niedostępne, zabezpiecz pracę, napraw dostęp i raportuj niewysłane SHA; nie nazywaj ich przekazanymi ani zadania zarezerwowanym.

Logowanie, nadanie brakujących uprawnień i formalne oświadczenia mogą wymagać udziału człowieka. Przygotuj konkretne działanie i wskaż brakującą informację; nie oznaczaj go ukończonego na podstawie samej instrukcji. Commit/push do ustalonego remote jest normalnym krokiem realizacji zadania. Nie uruchamiaj dodatkowych subagentów bez prośby użytkownika.

## Standard końcowy

W raporcie podaj ID kart, zdalną gałąź, wysłane SHA / URL PR, stan połączenia do `main`, sprawdzenia, ograniczenia i kolejny krok drugiego toru. Wymień commity niewysłane z powodu blokady. Nie twierdź, że aplikacja działa, jeśli sprawdziłeś tylko dokumenty. Źródła prawdy: karta w `origin/main`, kontrakt i rejestr decyzji.
