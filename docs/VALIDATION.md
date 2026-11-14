# Testy i odbiór

To plan wymaganych sprawdzeń przyszłej implementacji. Na etapie przygotowania repo sprawdzamy dokumenty i fixture'y, nie deklarujemy przejścia testów aplikacji.

## Silnik i dane — Kamil

| Przypadek | Oczekiwany wynik |
|---|---|
| Jedna cecha, pomiar w referencji | 100%, wkład równy wynikowi |
| Pomiar poza referencją o połowę tolerancji | 50%; na granicy tolerancji 0% |
| Zmiana wag, np. 1:3 | Ręcznie policzona suma zgadza się; wkłady sumują się do wyniku |
| Mnożenie wszystkich wag przez tę samą liczbę | Bez zmiany wyniku |
| Waga ujemna, puste kryteria, duplikat lub nieznane ID | Jawny błąd, bez częściowego wyniku |
| Brak aktywnej cechy | Komórka wykluczona, wynik null, powód zapisany |
| Równe wyniki | Stały porządek po `pixel_id`; bez sortowania zaokrąglonych wartości |
| Pełne sortowanie kontra skan blokami | Identyczne Top K na reprezentatywnej próbce |
| Wszystkie dane nieważne | Pusty ranking i raport, bez „najlepszego 0%” |
| Nachylenie i lokalne okno | Metry, właściwy model ciała i skala, kontrola brzegu rastra |
| Maska lądu | Depresja lądowa zachowana; ocean nie staje się suchym analogiem |
| Bieguny / 180° / granice rastra | Prawidłowe geometrie, brak pominięcia lub duplikatu |

## Granulacja — obowiązkowy test akceptacyjny

Fixture [hotspot-regression.json](../contracts/fixtures/hotspot-regression.json) jest w całości syntetyczny i nie opisuje realnego miejsca.

1. Słaby obszar zawiera jeden piksel z wynikiem 100%; wszystkie pozostałe są znacznie słabsze. Ten piksel wygrywa globalny ranking i jest widoczny jako maksimum po oddaleniu.
2. Dwa najlepsze piksele sąsiadują — oba pozostają w `pixels`, a tryb obszarów stosuje swój jawny dystans.
3. Dla dwóch warstw ich maksima leżą w różnych pikselach. Wynik mapowego maksimum jest maksimum **łącznych wyników**, a nie sumą maksimów cech.
4. Zmiana zoomu i agregacji mapy nie zmienia Top 10 tej samej analizy.
5. `distinct_areas` znajduje dalszych reprezentantów nawet wtedy, gdy pierwsze 10 pikseli należy do jednego skupiska.
6. Pojedynczy artefakt QA nie otrzymuje wyniku; prawidłowy izolowany piksel nie znika przez wygładzanie.
7. Porównanie dwóch rozdzielczości zawiera metadane i jawnie pokazuje utratę małych hotspotów przy grubszym pomiarze; nie obiecuje precyzji poniżej źródła.

## Weryfikacja naukowa — K-009

- Ręczne odtworzenie co najmniej trzech wyników na opublikowanym profilu.
- Znane analogi i kontrprzykłady, z uzasadnieniem odpowiedniego wymiaru. Analogia geologiczna nie musi wygrywać modelu topografii.
- Co najmniej trzy rzeczywiste ziemskie AOI porównane na NASA Earth DEM i globalnym podkładzie, po ujednoliceniu skali.
- Przegląd dziesięciu najwyższych wyników pod kątem maski, granic kafli, lodu, braków i źródła; badamy zarówno skupiska, jak i izolowane hotspoty.
- Wrażliwość na wagi ±20%, tolerancje, QA i skalę. Nie traktujemy jednego rankingu jako prawdy terenowej.
- Zapisanie nieoczekiwanego kandydata jako hipotezy, z dowodami i listą dalszych pomiarów. Nie ma gwarancji odkrycia wcześniej nieznanego analogu.

## UI i integracja — Ewelina

Scenariusze dla Marsa i Księżyca: jedna warstwa; trzy warstwy; zmienione wagi; brak aktywnych warstw; zero ważnych komórek; wybór i zoom do piksela; oba tryby rankingu; powrót do pierwotnej konfiguracji; eksport i ponowne odczytanie.

Mapa i szczegóły używają tego samego `analysis_id`. Powolna odpowiedź starego zapytania nie nadpisuje nowego. Nieudane API nie pokazuje syntetycznych danych bez oznaczenia. Awaria podkładu pozostawia czytelny ranking.

Sprawdzenie klawiatury, etykiet pól, kontrastu, opisu legendy i alternatywnego widoku wyników poza kolorem. Sprawdzenie telefonu i nawigacji do obszarów polarnych. Suwaki nie wysyłają pełnego globalnego zapytania dla każdego piksela przeciągnięcia — przycisk lub debounce.

## Dowody odbioru

Karta zadania podaje wykonane polecenie/test, rezultat i warunki. Raport I-003 zawiera wersje, sprzęt, pokrycie, czas, pamięć, wyniki regresji i znane ograniczenia. Screenshot sam nie potwierdza prawidłowości obliczeń. Nie wymagamy osobnych testów dla kosmetycznej zmiany dokumentu.
