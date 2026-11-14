# Terra Analog — plan projektu

Zespół: **Kamil i Ewelina** · NASA Space Apps Challenge 2026 · nazwa robocza do zmiany.

Webapp wyszukujący na Ziemi komórki najbardziej podobne do wybranego regionu Marsa lub Księżyca. Użytkownik wybiera warstwy, nadaje im wagi i otrzymuje mapę oraz ranking Top 10 z wyjaśnieniem wyniku.

**Stan repo: dokumentacja, plan i kontrakty startowe. Aplikacja i rzeczywiste wyniki nie są jeszcze zaimplementowane.** Repozytorium Git utworzono lokalnie; publikacja i połączenie z repozytorium zespołu są zadaniem I-001.

## Zacznij tutaj

1. Przeczytaj [instrukcje agentów](AGENTS.md) i [opis produktu](docs/PRODUCT.md).
2. Otwórz [plan krok po kroku](docs/PLAN.md) oraz [tablicę zadań](tasks/README.md).
3. Kamil uruchamia agenta z [tego promptu](prompts/KAMIL.md), Ewelina z [tego promptu](prompts/EWELINA.md).
4. Przed połączeniem implementacji obie strony stosują [kontrakty](docs/CONTRACTS.md).

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
