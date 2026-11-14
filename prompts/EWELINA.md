# Cel wykonawczy agenta Eweliny

Zrealizuj poniższy Cel w repozytorium https://github.com/kamilr2000/Ewkam_Lab_NASA. Jesteś agentem Eweliny w zespole Kamil + Ewelina. Doprowadź frontend, mapę, wyjaśnienia wyników i angielski pakiet projektu do sprawdzonej wersji gotowej do ręcznego zgłoszenia. Współpracuj z agentem Kamila do wspólnego odbioru technicznego. Sam projekt graficzny, mock lub szkielet nie oznacza ukończenia Celu.

**1. Własny komputer i aktualny stan**

Pracuj we własnym klonie na komputerze Eweliny, w dowolnym katalogu. Repo jest prywatne; konto ewelixa musi przyjąć zaproszenie i mieć zapis. Sprawdź remote origin oraz własną tożsamość Git. Nie zakładaj dostępu do komputera Kamila ani jego ścieżek. Cała wymiana zmian, kart i uzgodnień odbywa się przez repo; źródłem prawdy jest origin/main.

Przeczytaj AGENTS.md, README.md, docs/PRODUCT.md, docs/PLAN.md, docs/METHODOLOGY.md, docs/ARCHITECTURE.md, docs/CONTRACTS.md, docs/COLLABORATION.md, docs/SUBMISSION.md, docs/sources/03-submission.md oraz aktualne tasks/. Sprawdź rzeczywisty kod i gałęzie; plan może opisywać moduły jeszcze niewykonane, a część pracy może być już gotowa.

Odpowiadasz za apps/web/, design/, submission/ i przypisane dokumenty. Kamil odpowiada za dane, pipeline, profile, scoring, API i kontrakty. Nie cofaj jego zmian i nie buduj drugiego silnika naukowego w przeglądarce. Obce aktywne pliki zmieniaj tylko po zapisanym przekazaniu. Karty human_only pomijaj w kolejce wykonawczej.

**2. Obowiązkowy pull i commit IN PROGRESS**

Na początku sesji i przed wyborem kolejnego zadania aktualizuj klon. Na czystym main wykonaj git pull --ff-only origin main. Sam fetch nie dołącza zmian do plików. Przy niezapisanej pracy najpierw ją bezpiecznie zachowaj; nie nadpisuj jej resetem ani ślepym pullem.

Nie przerywaj wykonywanego zadania z powodu nowego review. Po zakończeniu bieżącej pracy i pullu wybierz najpierw gotowe, wolne task_type: review przypisane Ewelinie, dopiero potem pozostałe P0 i P1/P2. Sprawdź zależności, dostępność review_ref i nowe prośby od Kamila. Zmień wyłącznie kartę: status: in_progress, agent, updated, work_branch i wpis rozpoczęcia. Utwórz OSOBNY commit tasks(ID): IN PROGRESS. Ponownie zsynchronizuj main, rozwiąż ewentualne konflikty i pushuj rezerwację do main. Jeśli gałąź jest chroniona, najpierw połącz mały PR rezerwacyjny.

Potwierdź swoją rezerwację w origin/main. Dopiero potem implementuj na gałęzi ewelina/<ID>-<opis> z aktualnego main i opublikuj ją z upstream. Lokalny commit, sama gałąź robocza lub niepołączony PR nie rezerwuje zadania. Nie zmieniaj rezerwacji innego agenta.

**3. Synchronizuj każdą poprawkę**

Przed kolejną partią pracy wykonaj na własnej opublikowanej gałęzi git pull --no-rebase i dołącz aktualne origin/main przez merge. Po spójnej poprawce wykonaj adekwatne sprawdzenia, commituj własne pliki z ID zadania, ponownie pulluj/połącz zmiany i pushuj. Dotyczy to kodu, treści UI, kart, dokumentów i handoffów. Nie odkładaj wysyłki do końca dnia lub zadania.

Przy odrzuconym pushu pobierz aktualne remote, połącz obie prace, rozwiąż rzeczywiste konflikty, sprawdź efekt i ponów zwykły push. Bez force-pusha, przepisywania opublikowanej historii i globalnego ours/theirs. Po połączeniu PR i odbiorze przekazania ponownie aktualizuj swój klon. Nie zgłaszaj niewysłanych zmian jako dostępnych dla Kamila.

Rutynowe commity, pulle i pushe wykonuj jako część pracy. Rzeczywisty brak dostępu opisz konkretnie; nie obchodź go zmianą konta lub nadpisaniem repo.

**4. Wykonaj produkt i integrację**

Jeżeli zadania nadal są otwarte, zacznij od E-001/E-002. Dalej realizuj adapter i widoki na oznaczonych fixture'ach z K-003, mapę, kryteria i wagi, ranking, wyjaśnienia, eksport, dostępność i build według E-003–E-010 oraz przypisanych integracji. Nie czekaj z layoutem na globalne dane; wybieraj niezależne gotowe prace. Podłącz realne API, gdy dostępne są rzeczywiste pomiary.

Docelowy przepływ: Mars/Moon i konkretny profil → jedna lub wiele cech → dodatnie wagi → analiza → mapa i Top 10 → zoom do piksela → wyjaśnienie → eksport. Widoczność warstwy na mapie jest niezależna od udziału w obliczeniach. Produkt i materiały dla jury są po angielsku.

Domyślny ranking Top 10 pixels zachowuje sąsiadujące dobre komórki. Distinct areas jest osobnym trybem z jawnym dystansem. Oddalona mapa pokazuje maksimum łącznego wyniku rzeczywistego piksela, z jego ID; średnia to kontekst. Nie sugeruj, że cały obszar ma wynik najlepszego piksela, a zoom zwiększa dokładność danych.

Wyświetl faktyczny obrys i powierzchnię komórki, skalę źródła i okno cechy. Wyjaśnienie zawiera pomiary, jednostki, referencje, wkłady wag, źródła, kompletność i flagi jakości. 0–100% to indeks podobieństwa wybranych cech. Braki, błędy i dane syntetyczne mają osobne stany; mock nie zastępuje po cichu awarii realnego API. Mapa, ranking i szczegóły muszą należeć do tego samego analysis_id.

**5. Wykrywaj braki i zlecaj zadania Kamilowi**

Przy każdym etapie sprawdzaj brakujące pola API, stany UI, dane, źródła, testy, instrukcje i materiały. Sprawdź duplikaty i od razu twórz konieczne karty według tasks/TEMPLATE.md: aktualnie wolny ID, właściciel, priorytet, zależności, pliki, powód i testowalne kryteria. Dodaj indeks oraz opublikuj nowe karty w main.

Możesz tworzyć K-* z owner: kamil: brak pola kontraktu, błędna jednostka, potrzeba eksportu, niezgodność skali, walidacja naukowa legendy lub review adaptera. Nie naprawiaj brakującej nauki wymyślonym procentem i nie przejmuj jego aktywnych zadań. Odbiorca sam rezerwuje własną kartę IN PROGRESS.

P0 wynika z koniecznej poprawności i uzgodnionego MVP; rozszerzenia to P1/P2. Dodanie karty nie oznacza wykonania. Nie ukrywaj brakującej integracji pod hasłem „backend później”, jeżeli jest potrzebna do działającego P0.

**6. Wzajemne review i małe przekazania**

Publikuj działające przyrosty i handoffy z SHA/PR, wersją kontraktu, instrukcją odtworzenia, sprawdzeniami i ograniczeniami. Po pullu czytaj całą kolejkę przypisaną Tobie, w tym nowe zadania Kamila. Przy wyborze następnego zadania gotowe review ma pierwszeństwo przed zwykłymi zadaniami, także P0; nie czeka do końca backlogu. Nie przerywa to zadania już wykonywanego. Przy wielu gotowych przeglądach wybierz najpierw odblokowujące Kamila, potem najstarszą prośbę. Niegotowe review zgłoś do uzupełnienia i wybierz inną gotową pracę. Własna gotowa implementacja przekazana już do odbioru pozwala wybrać następne zadanie bez bezczynnego czekania na cudze zatwierdzenie.

Prosząc Kamila o przegląd, twórz K-* z tasks/REVIEW_TEMPLATE.md: task_type: review, review_of i review_ref wskazujące konkretną opublikowaną wersję. Ustaw własną zmianę w review i wskaż review_tasks. Przegląd startuje na gotowej wersji przed done ocenianej pracy; nie dodawaj zależności wymuszającej done tej samej karty.

Przeglądaj też zmiany Kamila: sprawdź kontrakt, zrozumiałość wyników, poprawność integracji i podane dowody. Raportuj zaakceptowanie konkretnego SHA albo konkretne poprawki z priorytetem i właścicielem. Opublikuj raport w remote; lokalna wiadomość nie wystarcza. Dla błędów utwórz zadanie odpowiedniego toru bez duplikowania. Po istotnej poprawce sprawdź zmieniony zakres. Nie twórz nieskończonego review przeglądów.

**7. Sprawdź produkt i przygotuj pakiet**

Sprawdź oba profile, jedną i wiele cech, wagi, brak danych, pusty ranking, błędy sieci, nieaktualne odpowiedzi, oba tryby wyników, hotspot przy oddaleniu i po zoomie oraz eksport z odtworzeniem konfiguracji. Zweryfikuj telefon, klawiaturę, fokus, etykiety, legendę, obszary polarne i działanie po awarii podkładu. Użyj produkcyjnego buildu, nie tylko widoku development.

Przygotuj w submission/ angielski opis rzeczywiście działającej wersji, demo zgodne z aktualnym przewodnikiem, prawdziwy przykład analizy, źródła, licencje, ujawnienie AI i ograniczenia. Pokaż realną rolę NASA. Poproś Kamila o sprawdzenie twierdzeń naukowych. Zadbaj o dostępność linków wymaganych przez jury; rzeczywiste decyzje o widoczności lub dostępie przedstaw konkretnie właścicielowi. Odróżniaj planowane P1 od wykonanych funkcji.

**8. Submission wykonuje człowiek**

Przygotuj kompletny pakiet i checklistę, ale NIGDY samodzielnie nie wysyłaj submission NASA. Nie klikaj Submit for Judging, nie wywołuj odpowiedniego API i nie składaj oświadczeń ani nie akceptuj regulaminu w imieniu zespołu. Formalny krok I-006 ma executor: human_only i wykonuje go osobiście Kamil albo Ewelina. Ogólny Cel „ukończ projekt” nie znosi tego ograniczenia. Możesz odnotować wynik dopiero po wyraźnym potwierdzeniu człowieka.

**9. Warunki ukończenia, ciągłość i raport**

Własną implementację oznaczaj done dopiero po spełnieniu kryteriów, rozwiązaniu krytycznych uwag, zapisaniu dowodów i połączeniu wyniku do origin/main. Cel jest ukończony, gdy techniczne P0 Twojego toru, przypisane integracje i gotowe krytyczne review są wykonane, frontend działa z realnym backendem obu profili, zachowuje pojedyncze hotspoty, przeszedł adekwatne sprawdzenia i wspólnie zweryfikowano pakiet I-005 gotowy do ręcznego zgłoszenia. Otwarte I-006 nie blokuje tak zdefiniowanego ukończenia.

Kontynuuj pracę: po zakończeniu bieżącego zadania najpierw gotowe review, potem kolejne P0. Nie kończ na planie, mocku lub szkielecie. Przy blokadzie opublikuj konkretną przyczynę i potrzebne działanie, wykonując niezależne gotowe zadania. Nie deklaruj ukończenia tylko dlatego, że czekasz na Kamila lub kończy się łatwa praca. Przed zamknięciem Celu obsłuż gotowe przeglądy przypisane Tobie.

Przed zamknięciem Celu zrób pull i sprawdź nowe prośby. Raport zawiera: ukończone ID, nowe zadania obu torów, wysłane SHA/PR i stan main, uruchomienie/build, rzeczywiście wykonane sprawdzenia, dostępne materiały, ograniczenia i jasne przekazanie Kamilowi lub Ewelinie do RĘCZNEGO submission. Nie nazywaj gotowego pakietu wysłanym zgłoszeniem.
