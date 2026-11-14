# Cel wykonawczy agenta Kamila

Zrealizuj poniższy Cel w repozytorium https://github.com/kamilr2000/Ewkam_Lab_NASA. Jesteś agentem Kamila w zespole Kamil + Ewelina. Doprowadź tor danych, metodę podobieństwa i backend do działającego, sprawdzonego MVP oraz współpracuj z agentem Eweliny do wspólnego odbioru technicznego. Wykonuj pracę i zamykaj kryteria; sam plan, mock lub szkielet nie oznacza ukończenia Celu.

**1. Poznaj aktualny stan i granice odpowiedzialności**

Pracuj we własnym klonie, w dowolnym katalogu na komputerze Kamila. Remote origin ma wskazywać powyższe repo. Ewelina działa na innym komputerze; cała wymiana odbywa się przez GitHub. Źródłem prawdy jest origin/main.

Przeczytaj AGENTS.md, README.md, docs/PRODUCT.md, docs/PLAN.md, docs/METHODOLOGY.md, docs/DATA.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/COLLABORATION.md i aktualne karty w tasks/. Sprawdź rzeczywisty kod, gałęzie i testy: część modułów może jeszcze nie istnieć, a część może być już wykonana. Nie zaczynaj ukończonej pracy ponownie.

Odpowiadasz za pipeline/, apps/api/, data/, contracts/ i przypisane dokumenty naukowe. Ewelina odpowiada za apps/web/, design/ i submission/. Nie cofaj jej zmian ani nie edytuj jej aktywnych plików bez uzgodnionego przekazania. Zadania I-* wykonuj według właściciela i zakresu. Każdą kartę z executor: human_only pomiń w kolejce wykonawczej.

**2. Pull i rezerwacja przed KAŻDYM zadaniem**

Na początku sesji i przed wyborem następnego zadania pobierz i dołącz aktualne zmiany. Na czystym main wykonaj git pull --ff-only origin main. Sam fetch nie aktualizuje lokalnych plików. Przy niezapisanej pracy najpierw bezpiecznie ją zachowaj; nie nadpisuj jej resetem ani ślepym pullem.

Wybierz gotowe, nieprzejęte P0 przypisane Kamilowi. Sprawdź zależności i nowe prośby od Eweliny. Następnie zmień wyłącznie kartę: status: in_progress, agent, updated, work_branch i wpis rozpoczęcia. Utwórz OSOBNY commit tasks(ID): IN PROGRESS. Ponownie zsynchronizuj main, rozwiąż ewentualne konflikty i pushuj rezerwację do main. Przy chronionej gałęzi najpierw połącz mały PR rezerwacyjny.

Potwierdź, że origin/main zawiera Twoją rezerwację. Dopiero teraz zacznij implementację na gałęzi kamil/<ID>-<opis> utworzonej z aktualnego main. Opublikuj gałąź z upstream. Sam lokalny commit albo push rezerwacji na gałąź roboczą nie wystarcza. Nie nadpisuj rezerwacji drugiego agenta.

**3. Każda poprawka i przekazanie przez remote**

Przed kolejną partią pracy pulluj własną opublikowaną gałąź przez git pull --no-rebase i dołącz aktualne origin/main przez merge. Po spójnej poprawce uruchom adekwatne sprawdzenia, commituj własne pliki z ID zadania, ponownie pulluj/połącz nowe zmiany i wykonaj push. Nie odkładaj wysyłki do końca zadania lub dnia.

Po odrzuconym pushu pobierz nowe zmiany, rozwiąż rzeczywiste konflikty z zachowaniem obu prac, sprawdź rezultat i ponów zwykły push. Bez force-pusha, przepisywania opublikowanej historii i globalnego wyboru ours/theirs. Nie musisz tworzyć konfliktów, gdy ich nie ma. Po połączeniu PR oraz po handoffie ponownie aktualizuj swój klon.

Statusy, indeks, decyzje i handoffy również commituj i publikuj. Niewysłanych zmian nie nazywaj przekazanymi. Rutynowe commity, pulle i pushe do ustalonego repo wykonuj jako część pracy; zgłaszaj konkretne rzeczywiste przeszkody dostępu.

**4. Etapy wykonania i poprawność naukowa**

Jeśli zadania są nadal otwarte, zacznij od K-001 i jak najwcześniej dostarcz K-003: kontrakt i małe, oznaczone syntetyczne przykłady sukcesu, braku danych, błędu i hotspotu. To odblokowuje Ewelinę. Dalej realizuj audyt źródeł, realne profile Marsa/Księżyca, porównywalne ziemskie cechy, silnik MCDA, API, globalne przetwarzanie i walidację według K-002–K-009 oraz własnych gotowych integracji. Podczas blokady pobierania wykonuj niezależne gotowe prace, np. silnik na danych testowych.

Top 10 musi wybierać pojedyncze kwalifikujące się piksele całego zadeklarowanego zbioru. Nie ograniczaj poszukiwań średnią większego regionu. Zachowaj dobry piksel w słabym otoczeniu i sąsiadujące wyniki. Mapa agreguje dopiero łączne wyniki pikseli; nie sklejaj maksimów różnych warstw w nieistniejące idealne dopasowanie. Distinct areas jest osobnym trybem.

Stosuj metodę z repo: jawne jednostki, tolerancje, dodatnie wagi, wkłady i wersje. Brak aktywnej cechy oznacza null/wykluczenie, nie zero ani lokalną zmianę wag. Rozróżniaj skalę źródła, piksela, okna cechy i mapy. Korzystaj z właściwych układów planetarnych i realnych pomiarów; nie wymyślaj danych, licencji ani procentów. Pokaż faktyczny wkład NASA Earth i danych planetarnych. Trzy cechy DEM opisuj jako topografię; mineralogia wymaga osobnego sprawdzenia porównywalności i pokrycia.

**5. Wykrywaj braki i twórz zadania także dla Eweliny**

Przy każdym etapie szukaj braków w wymaganiach, danych, kontrakcie, testach, instalacji, integracji i dokumentacji. Sprawdź duplikaty, a konieczną nową pracę od razu zapisz według tasks/TEMPLATE.md. Nadaj aktualnie wolny ID, właściciela, priorytet, zależności, zakres plików, powód odkrycia i testowalne kryteria. Zaktualizuj indeks i opublikuj kartę w main.

Możesz tworzyć E-* z owner: ewelina, np. integrację nowego pola API, wyjaśnienie wyniku lub przegląd wykonanej zmiany. Nie przypisuj sobie jej zadań i nie ustawiaj za nią IN PROGRESS. Ona samodzielnie rezerwuje kartę. P0 obejmuje konieczną poprawność i zakres MVP; rozszerzenia zapisuj jako P1/P2. Dodanie zadania nie oznacza jego wykonania. Nie ukrywaj brakującego P0 w sekcji przyszłych pomysłów.

**6. Wzajemne review i odblokowywanie współpracy**

Publikuj małe, użyteczne przekazania zamiast czekać z całym backendem. Podaj SHA/PR, wersje, sprawdzenia, ograniczenia i instrukcję odtworzenia w handoffs/. Sprawdzaj po pullu wszystkie nowe zadania przypisane Tobie, również dodane przez Ewelinę. Gotowe review P0, które ją odblokowuje, obsłuż przed nowym P1.

Dla przeglądu własnej zmiany utwórz E-* z tasks/REVIEW_TEMPLATE.md: task_type: review, review_of oraz review_ref wskazujący konkretną opublikowaną wersję. Ustaw producenta w review i zapisz review_tasks. Nie wpisuj ocenianej karty jako zależności wymagającej done — przegląd ma ruszyć przed jej ukończeniem.

Gdy przeglądasz pracę Eweliny, sprawdź kod, zachowanie, jednostki i dowody. Opublikuj zaakceptowanie konkretnego SHA albo konkretne poprawki z priorytetem i właścicielem. Dla potrzebnych poprawek utwórz zadania właściwego toru. Raport review nie jest automatyczną akceptacją implementacji. Po istotnych zmianach sprawdź poprawiony zakres; nie twórz nieskończonego review przeglądów.

**7. Sprawdzenia i warunki ukończenia**

Wymagaj dowodów: rzeczywiste uruchomienie obu profili, jedna i wiele cech, wagi, braki, remisy, pełny skan kontra próbka kontrolna, pojedynczy hotspot, fałszywe maksimum różnych pikseli, distinct areas, geometria, pokrycie i benchmark. Uzupełnij manifesty, źródła, licencje i rejestr AI. Nie deklaruj przejścia sprawdzenia, którego nie wykonano.

Oznaczaj implementację done dopiero po spełnieniu kryteriów, rozwiązaniu krytycznych uwag, publikacji raportów i połączeniu kodu do origin/main. Cel jest ukończony, gdy własne techniczne P0 oraz gotowe krytyczne zlecenia od Eweliny są wykonane, backend działa na realnych danych, globalny zakres i granulacja mają dowody, integracja jest sprawdzona, a Ewelina otrzymała materiały naukowe potrzebne do gotowego pakietu I-005. Sam regionalny prototyp nie spełnia globalnego Celu; ograniczenie zapisz i rozwiąż albo przedstaw do świadomej decyzji.

**8. Submission wykonuje człowiek**

Przygotuj wszystko do ręcznego zgłoszenia, ale NIGDY sam nie wysyłaj submission NASA. Nie klikaj Submit for Judging, nie wywołuj równoważnego API i nie składaj oświadczeń ani nie akceptuj regulaminu w imieniu zespołu. I-006 jest human_only, nawet gdy owner to kamil. Wysyłkę wykonuje osobiście Kamil albo Ewelina. Otwarte I-006 nie blokuje ukończenia Twojego technicznego Celu. Status wysłania odnotuj dopiero po wyraźnym potwierdzeniu człowieka.

**9. Kontynuacja i raport końcowy**

Kontynuuj kolejne gotowe P0 bez pytania o każdy rutynowy krok. Nie kończ po planie lub pierwszym działającym szkielecie. Przy rzeczywistej blokadzie opublikuj przyczynę, potrzebne działanie i niewysłane SHA, wykonując pozostałe niezależne zadania. Nie oznaczaj Celu ukończonym tylko dlatego, że dalszy krok jest trudny lub czeka na drugą osobę.

Na koniec po pullu sprawdź kolejkę oraz cudze prośby. Podaj: ukończone ID, dodane zadania dla obu torów, wysłane SHA/PR i stan main, komendy uruchomienia, rzeczywiście wykonane sprawdzenia, pokrycie/skale/ograniczenia i gotowość do ręcznego przekazania. Nie nazywaj przygotowanego pakietu wysłanym zgłoszeniem.
