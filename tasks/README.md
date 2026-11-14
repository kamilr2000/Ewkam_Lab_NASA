# Tablica zadań

Każda karta poniżej jest osobnym plikiem Markdown ze stanem, właścicielem, zależnościami, krokami i kryteriami odbioru. **Status czytaj z karty** — ten indeks pokazuje kolejność, bez drugiej kopii statusów.

P0: konieczne do uzgodnionego MVP lub zgłoszenia. P1: rozszerzenie po P0. P2: dalszy rozwój. Początkowo wszystkie 28 kart mają `todo`; 25 kart P0 i 3 karty P1. Liczby opisują stan startowy, nie bieżący postęp.

Zasady: [COLLABORATION](../docs/COLLABORATION.md). Nowa karta: [TEMPLATE](TEMPLATE.md). Kolejność wynika z zależności, nie tylko numeru. K-003 należy przekazać jak najwcześniej; UI może do tego czasu robić własny szkielet i UX.

## Tor Kamila — dane i obliczenia

| Karta | Priorytet | Właściciel | Zależności | Cel |
|---|---|---|---|---|
| [K-001](K-001.md) | P0 | Kamil | — | Uruchom środowisko danych i backendu |
| [K-002](K-002.md) | P0 | Kamil | K-001 | Sprawdź źródła, prawa i małe próbki trzech ciał |
| [K-003](K-003.md) | P0 | Kamil | K-001 | Zamroź kontrakt v1 i przekaż fixture'y Ewelinie |
| [K-004](K-004.md) | P0 | Kamil | K-002, K-003 | Wyznacz realne profile Marsa i Księżyca |
| [K-005](K-005.md) | P0 | Kamil | K-002, K-003 | Zbuduj siatkę i cechy rzeczywistego ziemskiego wycinka |
| [K-006](K-006.md) | P0 | Kamil | K-003 | Zaimplementuj MCDA i pełny ranking komórek |
| [K-007](K-007.md) | P0 | Kamil | K-003, K-004, K-005, K-006 | Udostępnij API i pierwszy realny przebieg |
| [K-008](K-008.md) | P0 | Kamil | K-004, K-005, K-006, K-007 | Przelicz globalny zbiór i agregaty mapy |
| [K-009](K-009.md) | P0 | Kamil | K-004, K-008 | Zweryfikuj naukę, skalę i prawdziwe hotspoty |
| [K-010](K-010.md) | P1 | Kamil | K-009 | Dodaj jedną niezależną dziedzinę danych |
| [K-011](K-011.md) | P1 | Kamil | K-002, K-009 | Sprawdź pilotaż mineralogii |

## Tor Eweliny — produkt i prezentacja

| Karta | Priorytet | Właściciel | Zależności | Cel |
|---|---|---|---|---|
| [E-001](E-001.md) | P0 | Ewelina | — | Utwórz sprawdzony szkielet aplikacji webowej |
| [E-002](E-002.md) | P0 | Ewelina | E-001 | Zaprojektuj przepływ i skalę informacji |
| [E-003](E-003.md) | P0 | Ewelina | E-002, K-003 | Zbuduj adapter API i widoki na fixture'ach |
| [E-004](E-004.md) | P0 | Ewelina | E-003 | Dodaj mapę zachowującą pojedyncze hotspoty |
| [E-005](E-005.md) | P0 | Ewelina | E-003 | Dodaj wybór celu, warstw i wag |
| [E-006](E-006.md) | P0 | Ewelina | E-004, E-005, K-007 | Połącz ranking pikseli, obszary i wyjaśnienia |
| [E-007](E-007.md) | P0 | Ewelina | E-006, K-008 | Dodaj odtwarzanie i eksport analizy |
| [E-008](E-008.md) | P0 | Ewelina | E-006 | Sprawdź UX, telefon i dostępność |
| [E-009](E-009.md) | P0 | Ewelina | E-007, E-008 | Przygotuj build web do wspólnego wydania |
| [E-010](E-010.md) | P0 | Ewelina | E-006 | Przygotuj angielski pakiet i demo dla jury |
| [E-011](E-011.md) | P1 | Ewelina | E-009, K-010 | Podłącz zatwierdzoną warstwę P1 |

## Integracja i zgłoszenie

| Karta | Priorytet | Właściciel | Zależności | Cel |
|---|---|---|---|---|
| [I-001](I-001.md) | P0 | Kamil | — | Udostępnij repo i potwierdź warunki zespołu |
| [I-002](I-002.md) | P0 | Ewelina | K-004, K-005, K-007, E-006 | Odbierz pierwszy pionowy przepływ |
| [I-003](I-003.md) | P0 | Kamil | K-008, K-009, E-007, E-008 | Odbierz globalność, hotspoty i granulację |
| [I-004](I-004.md) | P0 | Kamil | I-002, K-008, E-009 | Przygotuj i sprawdź wspólne wydanie |
| [I-005](I-005.md) | P0 | Ewelina | I-003, I-004, E-010 | Sprawdź zgodność zgłoszenia z finalnym produktem |
| [I-006](I-006.md) | P0 | Kamil | I-005 | Wyślij projekt i zachowaj potwierdzenie |

## Odkryte zadania

Agenci mogą samodzielnie dodać konieczną pracę według szablonu. Dopisz tutaj ID, link, właściciela i powód. Nowe P0 musi wynikać z uzgodnionego MVP, poprawności lub obowiązkowego zgłoszenia. Nie usuwaj istniejących kart; zastąpione oznacz jako `cancelled` z uzasadnieniem i aktualizacją zależności.

Na starcie brak dodatkowych kart. Następne wolne numery: K-012, E-012, I-007; sprawdź aktualne pliki przed nadaniem numeru w równoległym klonie.

## Sprawdzanie dokumentacji

`python tools/check_planning.py` z katalogu głównego repo sprawdza lokalne linki Markdown, JSON, metadane kart, zależności i cykle oraz zgodność oczekiwań syntetycznych fixture'ów z opisaną funkcją. To kontrola przygotowania repo, a nie test istniejącej aplikacji.
