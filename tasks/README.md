# Tablica zadań

Każda karta poniżej jest osobnym plikiem Markdown ze stanem, właścicielem, zależnościami, krokami i kryteriami odbioru. **Status czytaj z karty** — ten indeks pokazuje kolejność, bez drugiej kopii statusów.

P0: konieczne do uzgodnionego MVP lub zgłoszenia. P1: rozszerzenie po P0. P2: dalszy rozwój. Początkowo wszystkie 28 kart mają `todo`; 25 kart P0 i 3 karty P1. Liczby opisują stan startowy, nie bieżący postęp.

Zasady: [COLLABORATION](../docs/COLLABORATION.md). Nowa karta: [TEMPLATE](TEMPLATE.md). Kolejność wynika z zależności, nie tylko numeru. K-003 należy przekazać jak najwcześniej; UI może do tego czasu robić własny szkielet i UX.

**Dwa komputery, jedno remote:** [kamilr2000/Ewkam_Lab_NASA](https://github.com/kamilr2000/Ewkam_Lab_NASA). Przed każdym zadaniem pobierz `origin/main`, opublikuj tam osobny commit **IN PROGRESS** (`status: in_progress`) i potwierdź rezerwację. Następnie każdą poprawkę commituj i wysyłaj na zdalną gałąź; statusy i nowe karty również muszą być opublikowane. `done` dopiero po połączeniu rozwiązania do `origin/main`. Lokalny commit lub push rezerwacji wyłącznie na gałąź roboczą nie wystarcza.

**Kolejność po zakończeniu bieżącego zadania i pullu: gotowe review → pozostałe P0 → P1/P2.** Review nie przerywa już wykonywanego zadania, ale nie czeka na koniec zwykłego backlogu. Przy kilku gotowych przeglądach najpierw odblokowujące drugą osobę, potem najstarsze prośby. Karta bez dostępnego kodu/warunków startu nie blokuje wyboru innej gotowej pracy.

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
| [E-008](E-008.md) | P0 | Ewelina | E-006, E-021 | Sprawdź UX, telefon i dostępność |
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
| [I-006](I-006.md) | P0 | Kamil lub Ewelina osobiście | I-005 | Ręczny submission — human_only, poza Celami agentów |

## Odkryte zadania

Agenci mogą samodzielnie dodać konieczną pracę według szablonu. Dopisz tutaj ID, link, właściciela i powód. Nowe P0 musi wynikać z uzgodnionego MVP, poprawności lub obowiązkowego zgłoszenia. Nie usuwaj istniejących kart; zastąpione oznacz jako `cancelled` z uzasadnieniem i aktualizacją zależności.

- [I-007 — Szczegółowe cele agentów i ręczny submission](I-007.md), Kamil, P0: doprecyzowanie na prośbę Kamila; bez implementacji aplikacji.
- [I-008 — Pierwszeństwo gotowych review](I-008.md), Kamil, P0: przeglądy przed zwykłym backlogiem przy wyborze następnego zadania, bez przerywania rozpoczętej pracy.
- [K-012 — Review web scaffold E-001](K-012.md), Kamil, P0: sprawdzenie opublikowanego szkieletu React/Vite i dowodów builda przed połączeniem PR #3.
- [E-012 — Review bootstrapu API K-001](E-012.md), Ewelina, P0: sprawdzenie środowiska Python, API gotowości i odtwarzalności K-001 przed połączeniem PR #4.
- [K-013 — Review poprawki zakresu topografii E-001](K-013.md), Kamil, P1: potwierdzenie poprawki P1 K-012 w dokładnie wskazanym headzie PR #3.
- [I-009 — Zapisz użycie AI przy E-001](I-009.md), Ewelina, P0: brakujący wpis wspólnego rejestru AI, zależny od odbioru E-001.
- [K-014 — Review przepływu informacji E-002](K-014.md), Kamil, P0: przegląd przepływu UX, skali informacji i layoutu E-002 na PR #5.
- [K-015 — Review rejestru AI E-001](K-015.md), Kamil, P0: sprawdzenie faktograficzne ujawnienia użycia Codex przy web scaffoldzie w PR #6.
- [E-014 — Napraw widok mobilny E-002](E-014.md), Ewelina, P0: usuń ucinanie interfejsu przy 320–390 px wykryte w K-014; wymagany odbiór przed integracją E-002.
- [E-015 — Review poprawki geometrii K-003](E-015.md), Ewelina, P0: potwierdź walidację zagnieżdżenia MultiPolygon i regresję po uwadze E-013 w PR #7.
- [E-013 — Review kontraktu API v1 K-003](E-013.md), Ewelina, P0: sprawdzenie kontraktu, syntetycznych fixture'ów i zgodności z adapterem UI w PR #7.
- [K-016 — Re-review poprawki widoku mobilnego E-002](K-016.md), Kamil, P0: sprawdzenie poprawki E-014 oraz dowodów w aktualnym headzie PR #5.
- [E-016 — Review audytu źródeł i próbek K-002](E-016.md), Ewelina, P0: sprawdzenie metadanych, sum i odtwarzalnego pobrania z PR #8.
- [K-017 — Pozyskaj NASADEM i wybierz niezależną maskę lądu](K-017.md), Kamil, P0: pobranie NASADEM po lokalnym logowaniu i weryfikacja maski przed walidacją Earth DEM.
- [K-018 — Re-review overflowu mobilnego przy klasycznym pasku](K-018.md), Kamil, P0: ponowne sprawdzenie E-014 wobec `clientWidth` na dokładnym nowym headzie PR #5.
- [I-010 — Uzupełnij rejestr AI dla E-002, E-014 i E-016](I-010.md), Ewelina, P0: uzupełnienie wymaganej deklaracji Codex dla UI, poprawki mobilnej i review próbek.
- [I-011 — Uaktualnij rejestr użycia AI/SI](I-011.md), Ewelina, P0: uzupełnienie udokumentowanych prac po I-010 oraz aktualizacja stanu rzeczywistych próbek NASADEM.
- [E-017 — Niezależny review NASADEM i maski lądu](E-017.md), Ewelina, P0: sprawdzenie opublikowanego K-017, jego źródeł, porównania i ograniczeń w PR #12.
- [K-019 — Review adaptera API i widoków fixture E-003](K-019.md), Kamil, P0: sprawdzenie kontraktu, trybu syntetycznego, braku fallbacku i spójności `analysis_id` w PR #16.
- [E-018 — Review silnika MCDA i rankingu pikseli K-006](E-018.md), Ewelina, P0: niezależne sprawdzenie punktacji, braków, deterministycznego Top K i selekcji różnych obszarów w PR #15.
- [E-019 — Mapowy design handoff z hotspotem syntetycznym](E-019.md), Ewelina, P1: udokumentowanie legendy, projekcji i interakcji dla przyszłego E-004, z diagramem opartym wyłącznie na fixture'u.
- [K-020 — Review map design handoff E-019](K-020.md), Kamil, P1: sprawdzenie semantyki agregatu, hotspotu, legendy i syntetycznych wartości w PR #18.
- [E-020 — Odrzucaj odpowiedzi API niespójne z żądaniem](E-020.md), Ewelina, P0: walidacja datasetu i echo query search oraz parametrów bbox/level/limit mapy.
- [K-021 — Re-review adaptera API po poprawce E-020](K-021.md), Kamil, P0: sprawdzenie dokładnego headu PR #20 i regresji po uwagach K-019.
- [K-022 — Uzgodnij zakres fixture'u hotspotu z coverage mapy](K-022.md), Kamil, P0: napraw zgodność geometrii scope/bbox, komórek i liczników coverage wykrytą w K-020.
- [E-022 — Review poprawki zakresu i coverage hotspotu K-022](E-022.md), Ewelina, P0: niezależnie sprawdź geometrię scope/mapy/pikseli, coverage i test regresji na exact ref w PR #28.
- [K-023 — Review aktualizacji rejestru AI/SI I-011](K-023.md), Kamil, P0: sprawdź aktualność disclosure, źródła K-017 i rozróżnienie syntetycznych fixture'ów w PR #22.
- [K-024 — Re-review wiązania top-level scope w E-020](K-024.md), Kamil, P0: sprawdź poprawkę scope po P0 findingu K-021 w PR #20.
- [K-025 — Re-review poprawki rejestru AI/SI I-011](K-025.md), Kamil, P0: potwierdź aktualny stan K-017/E-017, integrację E-003/E-020 i syntetyczne fixture'y w PR #22.
- [K-026 — Review wyboru cech i wag E-005](K-026.md), Kamil, P0: potwierdź dostępność kryteriów, konfigurację 1–3 cech, wagi i request globalny w PR #31.
- [K-027 — Review interaktywnej mapy hotspotów E-004](K-027.md), Kamil, P0: sprawdź renderowanie, hotspot, legendę, geometrię brzegową i zachowanie bez podkładu w PR #37.
- [K-028 — Re-review wyboru roli datasetu po poprawce E-005](K-028.md), Kamil, P0: potwierdź `earth_search`/`fixture_only`, brak wieloznaczności i regresję na katalogu z `validation` przed właściwym datasetem w PR #31.
- [K-029 — Re-review renderowania komórek mapy E-004](K-029.md), Kamil, P0: potwierdź FeatureCollection zamiast wrappera, komórki liczbowe/null i etykietę zakresu na dokładnym SHA w PR #37.
- [K-030 — Review kontrastu i czytelności UI E-021](K-030.md), Kamil, P0: niezależnie sprawdź kontrast, fonty, pomiary viewportów i fokus na exact CSS SHA w PR #35.
- [E-021 — Popraw kontrast i czytelność bazowego UI](E-021.md), Ewelina, P0: popraw niewystarczający kontrast drobnych tekstów szkieletu i zachowaj układ telefonu przed pełnym audytem E-008.
- [E-023 — Review rzeczywistych profili K-004](E-023.md), Ewelina, P0: niezależnie odtwórz źródła i profile Jezero/księżycowego bieguna, geometrię, braki, schemę i ograniczenia w PR #36.
- [E-024 — Review siatki i cech regionalnych K-005](E-024.md), Ewelina, P0: niezależnie odtwórz publiczne źródła, maskowanie batymetrii, cechy, QA, checkpointy i trzy realne pakiety w PR #44.
- [E-026 — Re-review metadanych fingerprintu K-005](E-026.md), Ewelina, P0: potwierdź fingerprint kodu w raporcie i trzech manifestach oraz niezmienione SHA regionalnych CSV po poprawce P1 E-024 w PR #44.
- [I-012 — Uzupełnij rejestr AI/SI o późniejsze prace web i review](I-012.md), Ewelina, P0: dodaj źródłowo poparte wpisy dla E-004/E-005/E-021/E-023/E-024 oraz zachowaj ograniczenia i statusy.
- [K-031 — Review uzupełnienia rejestru AI/SI I-012](K-031.md), Kamil, P0: zweryfikuj exact ref disclosure, statusy, ograniczenia, linki i zachowanie syntetycznych ścieżek w PR #46.
- [K-032 — Re-review ładowania mapy E-004](K-032.md), Kamil, P0: sprawdź renderowanie, no-data, fallbacki i lazy bundle MapLibre na nowym exact SHA w PR #37.
- [E-025 — Zmapuj twierdzenia submission na dowody](E-025.md), Ewelina, P1: przygotuj wewnętrzną angielską macierz faktów, stanu funkcji i brakujących dowodów dla E-010.
- [K-033 — Review wewnętrznej macierzy dowodów E-025](K-033.md), Kamil, P1: zweryfikuj pola S03, aktualne statusy repo i granice twierdzeń na exact SHA w PR #50.
- [K-034 — Re-review korekty rejestru AI/SI I-012](K-034.md), Kamil, P0: potwierdź aktualne statusy, exact refy, ograniczenia i ścieżki syntetyczne po poprawkach K-031 w PR #46.
- [K-035 — Re-review macierzy dowodów E-025 po K-033](K-035.md), Kamil, P1: potwierdź pełne pokrycie S03, aktualne statusy po integracji E-005 i granice bezpiecznych twierdzeń w PR #50.
- [K-036 — Re-review I-012 po integracji E-005](K-036.md), Kamil, P0: potwierdź nowy exact status E-005, health-only API i pozostałe ograniczenia w PR #46.
- [K-037 — Re-review czytelności E-021 po korekcie widoku kryteriów](K-037.md), Kamil, P0: sprawdź minimum 9 px, kontrast, interaktywny stan niezaznaczonych kryteriów i jawne ograniczenia pomiaru 781/782 px w PR #35.
- [K-038 — Re-review korekty rejestru AI/SI po K-036](K-038.md), Kamil, P0: potwierdź rozkład flag fixture'ów, źródła K-004 oraz aktualne statusy E-004/E-021 i poprawność disclosure w PR #46.
- [I-013 — Ujawnij lazy-load mapy E-004 w rejestrze AI/SI](I-013.md), Ewelina, P0: dopisz źródłowo poparte użycie Codex przy follow-upie `e63ded5`, po integracji I-012.

Każdy agent może dodać zadanie drugiemu: Kamil tworzy E-*, Ewelina K-*, z właścicielem odbiorcy. Dla przeglądów użyj [REVIEW_TEMPLATE](REVIEW_TEMPLATE.md). Review wskazuje review_of oraz opublikowane review_ref; nie wymaga done ocenianej pracy. I-006 jest zadaniem wyłącznie dla człowieka — agent przygotowuje pakiet i pomija je przy wyborze zadań wykonawczych.

Następne wolne numery po dodaniu tych kart: K-039, E-027, I-014; sprawdź aktualne pliki przed nadaniem numeru w równoległym klonie.

## Sprawdzanie dokumentacji

`python tools/check_planning.py` z katalogu głównego repo sprawdza lokalne linki Markdown, JSON, metadane kart, zależności i cykle oraz zgodność oczekiwań syntetycznych fixture'ów z opisaną funkcją. To kontrola przygotowania repo, a nie test istniejącej aplikacji.
