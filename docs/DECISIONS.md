# Rejestr decyzji

Decyzje startowe z 2026-11-14. Parametry zależne od danych są propozycją do G1; wymagania użytkownika obowiązują od razu.

| ID | Decyzja | Status i uzasadnienie |
|---|---|---|
| D-001 | Globalna mapa, wybór Mars/Moon, warstwy, wagi, Top 10 | Wymaganie Kamila i Eweliny |
| D-002 | Jednostka domyślnego rankingu to pojedyncza komórka; zachowujemy sąsiadujące wyniki | Wymaganie Kamila doprecyzowane w rozmowie; unikamy utraty hotspotów przez średnią obszaru |
| D-003 | Mapa oddalona: maksimum wyniku z rzeczywistego piksela; średnia jako kontekst | Przyjęte w planie; agregacja po wyniku łącznym |
| D-004 | Drugi tryb „różne obszary” nie zmienia domyślnego Top 10 pikseli | Przyjęte; pozwala zobaczyć różnorodność lokalizacji |
| D-005 | Backend pełnego skanu zamiast pełnego zbioru w przeglądarce | Przyjęte w planie po doprecyzowaniu granulacji; wymaga benchmarku |
| D-006 | Python/FastAPI + React/TypeScript/Vite/MapLibre | Proponowany stos; bez obowiązku używania konkretnego hostingu |
| D-007 | Raster analityczny 60 arc-second, skala efektywna ~2 km, lokalny promień 10 km | Propozycja do G1; jeden piksel rastra to jeden kandydat; koszyki mapowe nie zastępują pikseli |
| D-008 | P0: trzy topograficzne cechy; dodatkowe dziedziny P1 | Przyjęte ograniczenie weekendowego MVP, nie redukcja docelowej wizji |
| D-009 | Brak dowolnej aktywnej cechy wyklucza piksel | Przyjęte; wyniki muszą odnosić się do tych samych kryteriów |
| D-010 | Mineralogia przechodzi oddzielny pilotaż porównywalności | Przyjęte; nie obiecujemy istniejącej globalnej warstwy |
| D-011 | Kamil: dane/API; Ewelina: UI/demo | Domyślny podział organizacyjny do ewentualnej zamiany przez zespół |
| D-012 | MIT dla własnego kodu/docs; cudze materiały z osobnymi warunkami | Domyślna licencja repo; kontrola przed publikacją |
| D-013 | Wewnętrzne instrukcje PL, produkt i pakiet jury EN | Przyjęte; pełna kontrola publicznie linkowanych materiałów w I-005 |
| D-014 | Nie łączymy cech kilku pikseli w większy kandydat przed scoringiem | Przyjęte po przeglądzie granulacji; pierwotną roboczą propozycję większych komórek H3 zastąpił raster zachowujący osobne pomiary. Wymaga większego budżetu skanu, dlatego benchmark jest bramką. |
| D-015 | Dwa komputery, całe przekazywanie przez `origin` repo `kamilr2000/Ewkam_Lab_NASA` | Wymaganie Kamila z 2026-11-14; zastępuje wariant wspólnego katalogu. Osobny commit IN PROGRESS musi znaleźć się w `origin/main` przed implementacją. Każda poprawka ma commit i push; konflikty rozwiązujemy przy synchronizacji z zachowaniem obu prac. |
| D-016 | Repo prywatne; pierwsza wysyłka przyjęta po weryfikacji adresu i zakresu | Repo istnieje od 2026-11-14. Po początkowych odmowach potwierdzono własność konta, prywatność i przygotowany zakres 70 plików tekstowych, po czym wysłano historię do wskazanego repo. Zmiana widoczności wymaga osobnej decyzji właściciela. |
| D-017 | Nazwa repo `Ewkam_Lab_NASA`, współpracowniczka `ewelixa` | Bezpośrednia instrukcja Kamila z 2026-11-14. Repo przemianowano, origin i instrukcje zaktualizowano, a zaproszenie z uprawnieniem write wysłano do wskazanego konta. Przyjęcie zaproszenia następuje na koncie Eweliny. |
| D-018 | Submission wykonuje wyłącznie Kamil albo Ewelina osobiście | Bezpośrednia instrukcja Kamila z 2026-11-14. I-006 ma executor: human_only; agenci przygotowują wszystko do ręcznego zgłoszenia i nie wysyłają formularza/API ani nie składają oświadczeń. Otwarte I-006 nie blokuje ukończenia ich technicznych Celów. |
| D-019 | Cele obejmują pull, dwukierunkowe zlecenia i review | Doprecyzowanie Kamila z 2026-11-14. Każdy agent aktualizuje własny klon, może tworzyć karty dla drugiego i obsługuje przeglądy odblokowujące współpracę. Review używa review_of/review_ref i nie czeka na done ocenianej karty. |
| D-020 | Gotowe review pierwsze przy wyborze następnego zadania, bez przerywania bieżącego | Doprecyzowanie Kamila z 2026-11-14. Najpierw agent kończy wykonywaną pracę, potem po pullu wybiera gotowe review przed zwykłym backlogiem, także P0. Przy wielu przeglądach pierwszeństwo mają odblokowujące drugą osobę, następnie najstarsze prośby. Brak dostępnego kodu nie blokuje całej kolejki. |
| D-021 | Regionalny pakiet K-005 jest osobnym produktem analitycznym o rozdzielczości UTM 2 km; budżet 60″ jest na razie rachunkiem, nie globalnym przebiegiem | Przyjęte w K-005 po zmierzeniu skali i kosztu trzech realnych AOI. Lokalna siatka kwadratowa upraszcza poprawne liczenie odległości i pola, a jej identyfikatory nie mieszają się z planowaną globalną siatką. Zachowanie tej granicy zapobiega przedstawianiu małych wycinków ani arytmetycznego budżetu jako globalnego pokrycia lub rankingu. |
| D-022 | Trzy skompresowane tabele komórek K-005 są wersjonowanymi pochodnymi; źródłowe i pośrednie rastry pozostają lokalne | Przyjęte dla ciągłości technicznej K-005→K-007 oraz gotowego pokazu rzeczywistych wyników. Około 190 kB pomiarów, QA i stabilnych ID pozwala reviewerowi i UI od razu odczytać komórki; manifesty zachowują źródła i sumy. Surowe ETOPO/GSHHG i checkpointy są duże i nadal odtwarzalne ze źródeł. |
| D-023 | Zanim ETOPO jest uśredniane do komórek K-005, wyklucz z wejścia próbki oceaniczne według GSHHG na siatce źródłowej | Przyjęte po przeglądzie brzegu Big Island: ETOPO zawiera batymetrię jako ważną wysokość, więc sama maska środka komórki docelowej nie zapobiega domieszce głębokości do wybrzeża. Maskowanie źródłowe i docelowe ma osobne role; zmiana podnosi wersje modelu/siatki do v2. Test z komórką mieszającą 100 m lądu i −100 m oceanu musi zwrócić wyłącznie 100 m. |

Nowy wpis: data, powód, autor/tor, karta, rozważone opcje, wybór, wpływ na zakres/kontrakt/dane, konieczna aktualizacja drugiego toru. Nie zmieniaj starego wpisu tak, by zniknął powód wcześniejszej decyzji; oznacz go jako zastąpiony i wskaż nowy.
