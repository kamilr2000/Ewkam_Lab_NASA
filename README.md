# Terra Analog — plan projektu

Zespół: **Kamil i Ewelina** · NASA Space Apps Challenge 2026 · nazwa robocza do zmiany.

Webapp wyszukujący na Ziemi komórki najbardziej podobne do wybranego regionu Marsa lub Księżyca. Użytkownik wybiera warstwy, nadaje im wagi i otrzymuje mapę oraz ranking Top 10 z wyjaśnieniem wyniku.

**Stan repo: dokumentacja, plan i kontrakty startowe. Aplikacja i rzeczywiste wyniki nie są jeszcze zaimplementowane.** Wspólne prywatne repo: **[kamilr2000/Ewkam_Lab_NASA](https://github.com/kamilr2000/Ewkam_Lab_NASA)**. Remote to `origin`; I-001 potwierdza pierwszą wysyłkę i dostęp obu osób.

## Zacznij tutaj

1. Kamil i Ewelina klonują wspólne repo na swoich komputerach do dowolnych katalogów i sprawdzają dostęp do zapisu.
2. Pobierz aktualne `origin/main`, przeczytaj [instrukcje agentów](AGENTS.md), [zasady synchronizacji](docs/COLLABORATION.md) i [opis produktu](docs/PRODUCT.md).
3. Otwórz [plan krok po kroku](docs/PLAN.md) oraz [tablicę zadań](tasks/README.md).
4. Kamil uruchamia agenta z [tego promptu](prompts/KAMIL.md), Ewelina z [tego promptu](prompts/EWELINA.md).
5. Przed implementacją każdego zadania opublikuj osobny commit **IN PROGRESS** w `origin/main`. Każdą poprawkę zapisuj commitem i od razu wysyłaj na zdalną gałąź zadania. Konflikty rozwiązuj przy synchronizacji z zachowaniem obu prac.
6. Obie strony stosują [kontrakty](docs/CONTRACTS.md); zakończone zadania i ich rozwiązania muszą być dostępne w `origin/main`.

Prompty są pełnymi **Celami wykonawczymi**: zawierają warunki ukończenia, pętlę pull/commit/push i zasady dopisywania zadań także dla drugiego agenta. Do przeglądów służy [szablon review](tasks/REVIEW_TEMPLATE.md).

**Agenci przygotowują projekt i pakiet zgłoszeniowy. Submission wykonuje osobiście Kamil albo Ewelina; karta I-006 ma executor: human_only i nie jest zadaniem do samodzielnego wykonania przez agenta.**

## Najważniejsze decyzje

- **Top 10 dotyczy pojedynczych komórek**, a nie średnich regionów. Sąsiadujące dobre piksele mogą zajmować wiele miejsc w domyślnym rankingu.
- Mapa przy oddaleniu pokazuje maksimum wyniku z komórek, zachowując identyfikator najlepszego piksela. Średnia może być pokazana dodatkowo.
- Dodatkowy ranking różnych obszarów grupuje wyniki; nie zastępuje rankingu pikseli.
- Wynik 0–100% to zdefiniowany indeks podobieństwa wybranych cech, nie prawdopodobieństwo i nie potwierdzenie przydatności miejsca do budowy bazy.
- MVP: globalny screening topografii; początkowo trzy mierzalne cechy terenu. Kolejne dziedziny, w tym minerały, mają osobne bramki dostępności i porównywalności danych.
- Ziemski analog ma ograniczenia fizyczne. Profil dotyczy wskazanego regionu i skali pomiaru, nie całej planety.

## Dokumentacja

| Potrzeba | Plik |
|---|---|
| Cel, funkcje, warstwy, zakres MVP | [PRODUCT](docs/PRODUCT.md) |
| Etapy, zależności, harmonogram | [PLAN](docs/PLAN.md) |
| Wynik, MCDA i granulacja | [METHODOLOGY](docs/METHODOLOGY.md) |
| Dobór źródeł i ograniczenia danych | [DATA](docs/DATA.md) |
| Budowa aplikacji i wydajność | [ARCHITECTURE](docs/ARCHITECTURE.md) |
| Formaty i komunikacja frontend–backend | [CONTRACTS](docs/CONTRACTS.md) |
| Podział pracy i dodawanie zadań | [COLLABORATION](docs/COLLABORATION.md) |
| Testy i odbiór | [VALIDATION](docs/VALIDATION.md) |
| Zgłoszenie i materiały dla jury | [SUBMISSION](docs/SUBMISSION.md) |
| Linki organizatora i ich streszczenia | [sources](docs/sources/README.md) |
| Ryzyka, decyzje, użycie AI, licencje | [RISKS](docs/RISKS.md), [DECISIONS](docs/DECISIONS.md), [AI_USAGE](docs/AI_USAGE.md), [THIRD_PARTY](THIRD_PARTY.md) |

## Podział odpowiedzialności

| Kamil | Ewelina | Integracja |
|---|---|---|
| Dane, preprocessing, profile planetarne, model podobieństwa, backend | Interfejs, mapa, warstwy, ranking, dostępność, materiały zgłoszeniowe | Wzajemny przegląd, wspólne demo i odbiór |

To podział organizacyjny, nie założenie o Waszym doświadczeniu. Można zamienić role, aktualizując właścicieli zadań i instrukcje obu agentów.

## Co można uruchomić teraz

Obecnie można czytać dokumentację, przeglądać zadania i uruchomić kontrolę przygotowania: `python tools/check_planning.py` z katalogu repo. Komendy instalacji, testów i uruchomienia aplikacji dodają agenci w K-001 i E-001 po faktycznym utworzeniu projektów. Nie ma jeszcze działającego demo ani pobranych danych naukowych.

Dokumentacja operacyjna jest po polsku. Interfejs i publiczny pakiet zgłoszeniowy powstają po angielsku. Kod własny i dokumentacja: [MIT](LICENSE); dane oraz cudze materiały zachowują własne warunki.
