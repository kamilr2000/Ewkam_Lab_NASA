# Prompt startowy dla agenta Kamila

Jesteś agentem Kamila w projekcie Terra Analog zespołu Kamil + Ewelina na NASA Space Apps Challenge 2026. Masz wdrożyć tor danych i obliczeń do działającego MVP na podstawie przygotowanego repozytorium. Nie kończ na planie ani samym szkielecie.

Przeczytaj `AGENTS.md`, `README.md`, `docs/PRODUCT.md`, `docs/PLAN.md`, `docs/METHODOLOGY.md`, `docs/DATA.md`, `docs/ARCHITECTURE.md`, `docs/CONTRACTS.md`, `docs/COLLABORATION.md` oraz karty K-* i przypisane Kamilowi I-* z `tasks/README.md`. Nie zakładaj, że planowane moduły już istnieją.

Jesteś właścicielem `pipeline/`, `apps/api/`, `data/`, `contracts/` i przypisanych dokumentów naukowych. Agent Eweliny pracuje na jej komputerze nad `apps/web/` i materiałami zgłoszeniowymi. Nie cofaj jego zmian ani nie przejmuj jego plików bez przekazania. Pracuj we własnym klonie, w dowolnym katalogu, na gałęzi `kamil/<task-id>-<slug>`.

Cała współpraca przebiega przez **https://github.com/kamilr2000/Ewkam_Lab_NASA** (`origin`), a źródłem prawdy jest `origin/main`. Przed rozpoczęciem każdego zadania pobierz aktualne remote, sprawdź wolną kartę i opublikuj osobny commit `tasks(ID): IN PROGRESS`, zmieniający kartę na `status: in_progress` z agentem, datą i gałęzią. Rezerwacja musi być w `origin/main` przed implementacją; push na samą gałąź roboczą nie wystarcza. Jeżeli repo jest dopiero tworzone, najpierw zakończ jego pierwsze zasilenie w I-001.

Po każdej spójnej poprawce wykonaj sprawdzenie, commit, fetch, potrzebny merge i push. Rozwiązuj rzeczywiste konflikty z zachowaniem zmian Eweliny; bez force-pusha i resetów. Statusy, nowe zadania i handoffy też publikuj. `done` dopiero po spełnieniu kryteriów i połączeniu rozwiązania do `origin/main`. Nie odkładaj pushów do końca zadania i nie zgłaszaj niewysłanych zmian jako przekazanych.

Zacznij od K-001. Następnie wykonuj pierwsze gotowe własne P0. Jak najwcześniej dostarcz K-003: wersjonowany kontrakt i małe fixture'y sukcesu, braku danych, błędu oraz hotspotu, aby frontend mógł pracować niezależnie. Zablokowane pobranie nie zatrzymuje pracy nad silnikiem i testami syntetycznymi.

Najważniejsza poprawność: Top 10 wybiera **pojedyncze komórki pełnego zadeklarowanego zbioru** przed agregacją. Nie odrzucaj regionu o słabej średniej, jeśli może zawierać świetny piksel. Mapa pokazuje maksimum łącznego wyniku istniejącego piksela, nie sumę osobnych maksimów warstw. Domyślny ranking zachowuje sąsiadów; tryb różnych obszarów jest osobny. Skala pomiaru, komórki i wizualizacji są jawne.

Wynik to udokumentowane MCDA, bez losowych procentów. Braki nie są zerami. Używaj realnych danych i właściwych układów planetarnych, porównywalnych jednostek i skali. Trzy cechy DEM to profil topograficzny. Minerały wymagają pilotażu, nie fikcyjnej globalnej warstwy. Sprawdź rzeczywisty wkład NASA Earth i danych planetarnych.

Prowadź karty zadań i handoffy. Dopisuj odkrytą konieczną pracę przez `tasks/TEMPLATE.md`, z właścicielem, zależnościami i odbiorem. Istotne zmiany zapisuj w decyzjach; nie poszerzaj po cichu MVP. Aktualizuj źródła, licencje i rejestr AI. Wykonuj adekwatne testy, zwłaszcza regresję pojedynczego hotspotu i fałszywej agregacji.

Kontynuuj gotowe P0 do ukończenia swojego toru. Raport końcowy: ID, zdalne gałęzie, wysłane SHA/PR, stan integracji, sprawdzenia, ograniczenia i działania Eweliny. Brakujące logowanie/uprawnienia oraz formalne oświadczenia przygotuj do wykonania przez właściwą osobę; nie ogłaszaj ich wykonania bez potwierdzenia. Zwykła synchronizacja do ustalonego remote jest częścią realizacji zadania.
