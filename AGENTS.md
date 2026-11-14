# Instrukcje pracy dla agentów

## Kontekst i kolejność czytania

Projekt Kamila i Eweliny: ziemskie analogi regionów Marsa i Księżyca, NASA Space Apps 2026. Zadanie bieżącego etapu: wdrożyć plan opisany w repo. Początkowy commit zawiera przygotowanie, nie gotowy produkt.

Przeczytaj kolejno: `README.md`, `docs/PRODUCT.md`, `docs/METHODOLOGY.md`, `docs/CONTRACTS.md`, `docs/COLLABORATION.md`, swój prompt w `prompts/` i kartę aktualnego zadania. Źródła organizatora są w `docs/sources/`.

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

1. Sprawdź aktualną gałąź, zmiany i swoją kolejkę. Nie nadpisuj niezacommitowanej pracy.
2. Wybierz pierwsze gotowe zadanie P0 własnego toru. Przeczytaj jego zależności.
3. Ustaw kartę na `in_progress`, wpisz agenta i zakres. W osobnych klonach zgłoszenie musi zostać zsynchronizowane; lokalna karta nie jest globalną blokadą.
4. Wykonaj kroki i kryteria odbioru, uzupełnij źródła, wyniki sprawdzeń i ograniczenia.
5. Po odkryciu brakującej pracy od razu dodaj kartę według `tasks/TEMPLATE.md`. Nie poszerzaj po cichu MVP.
6. Przekaż rezultat przez PR lub uzgodniony commit oraz `handoffs/`. `done` dopiero po spełnieniu kryteriów; blokada ma konkretny powód i następne działanie.
7. Kontynuuj kolejne gotowe P0. Przy zablokowanej zależności wykonuj niezależne zadania. P1 zaczynaj po działającym pionowym przepływie i ocenie pozostałego czasu.

Zadania wymagające konta, zewnętrznego udostępnienia lub formalnego zgłoszenia przygotuj do wykonania przez człowieka. Nie oznaczaj ich ukończonych na podstawie samej instrukcji. Nie uruchamiaj dodatkowych subagentów bez prośby użytkownika.

## Standard końcowy

W raporcie podaj identyfikatory ukończonych kart, zmienione pliki, wykonane sprawdzenia, ograniczenia, nowo dodane zadania i najbliższy krok drugiego toru. Nie twierdź, że aplikacja działa, jeśli sprawdziłeś tylko dokumenty. Zachowaj źródło prawdy: stan zadania w jego karcie, format danych w kontrakcie, decyzję w `docs/DECISIONS.md`.
