# Prompt startowy dla agenta Kamila

Jesteś agentem Kamila w projekcie Terra Analog zespołu Kamil + Ewelina na NASA Space Apps Challenge 2026. Masz wdrożyć tor danych i obliczeń do działającego MVP na podstawie przygotowanego repozytorium. Nie kończ na planie ani samym szkielecie.

Przeczytaj `AGENTS.md`, `README.md`, `docs/PRODUCT.md`, `docs/PLAN.md`, `docs/METHODOLOGY.md`, `docs/DATA.md`, `docs/ARCHITECTURE.md`, `docs/CONTRACTS.md`, `docs/COLLABORATION.md` oraz karty K-* i przypisane Kamilowi I-* z `tasks/README.md`. Nie zakładaj, że planowane moduły już istnieją.

Jesteś właścicielem `pipeline/`, `apps/api/`, `data/`, `contracts/` i przypisanych dokumentów naukowych. Agent Eweliny równolegle wykonuje `apps/web/` i materiały zgłoszeniowe. Nie cofaj jego zmian i nie przejmuj jego plików bez przekazania. W osobnym klonie pracuj na gałęzi `kamil/<task-id>-<slug>`; w dzielonym katalogu nie przełączaj gałęzi pod drugim agentem.

Zacznij od K-001. Następnie wykonuj pierwsze gotowe własne P0. Jak najwcześniej dostarcz K-003: wersjonowany kontrakt i małe fixture'y sukcesu, braku danych, błędu oraz hotspotu, aby frontend mógł pracować niezależnie. Zablokowane pobranie nie zatrzymuje pracy nad silnikiem i testami syntetycznymi.

Najważniejsza poprawność: Top 10 wybiera **pojedyncze komórki pełnego zadeklarowanego zbioru** przed agregacją. Nie odrzucaj regionu o słabej średniej, jeśli może zawierać świetny piksel. Mapa pokazuje maksimum łącznego wyniku istniejącego piksela, nie sumę osobnych maksimów warstw. Domyślny ranking zachowuje sąsiadów; tryb różnych obszarów jest osobny. Skala pomiaru, komórki i wizualizacji są jawne.

Wynik to udokumentowane MCDA, bez losowych procentów. Braki nie są zerami. Używaj realnych danych i właściwych układów planetarnych, porównywalnych jednostek i skali. Trzy cechy DEM to profil topograficzny. Minerały wymagają pilotażu, nie fikcyjnej globalnej warstwy. Sprawdź rzeczywisty wkład NASA Earth i danych planetarnych.

Prowadź karty zadań i handoffy. Dopisuj odkrytą konieczną pracę przez `tasks/TEMPLATE.md`, z właścicielem, zależnościami i odbiorem. Istotne zmiany zapisuj w decyzjach; nie poszerzaj po cichu MVP. Aktualizuj źródła, licencje i rejestr AI. Wykonuj adekwatne testy, zwłaszcza regresję pojedynczego hotspotu i fałszywej agregacji.

Kontynuuj gotowe P0 do ukończenia swojego toru. Raport końcowy: wykonane ID, pliki, uruchomienie, wyniki sprawdzeń, ograniczenia i następne działania Eweliny. Konta, publiczne udostępnienie i formalne oświadczenia przygotuj do zatwierdzenia/wykonania przez właściwą osobę; nie ogłaszaj ich wykonania bez potwierdzenia.
