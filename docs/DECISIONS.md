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

Nowy wpis: data, powód, autor/tor, karta, rozważone opcje, wybór, wpływ na zakres/kontrakt/dane, konieczna aktualizacja drugiego toru. Nie zmieniaj starego wpisu tak, by zniknął powód wcześniejszej decyzji; oznacz go jako zastąpiony i wskaż nowy.
