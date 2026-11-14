---
id: E-012
owner: ewelina
reviewer: kamil
priority: P0
task_type: review
queue_priority: review_first
unblocks_other_agent: true
status: todo
depends_on: []
review_of: K-006
review_ref: pending
agent: unassigned
work_branch: unassigned
updated: 2026-11-14
discovered_from: requesting-task-or-pr
---

# TASK-ID — Przegląd konkretnego zakresu i wersji

To szablon; nadaj aktualny wolny ID i właściciela odbiorcy. Kamil tworzy E-* dla Eweliny, Ewelina K-* dla Kamila.

Pierwszeństwo przy wyborze następnego zadania: gotowe review przed zwykłymi P0/P1/P2, ale bez przerywania aktualnie wykonywanej pracy. Przy kilku przeglądach najpierw te odblokowujące drugiego agenta, następnie najstarsze prośby. Ustaw unblocks_other_agent zgodnie ze stanem faktycznym. Sam brak queue_priority w starszej karcie review nie odbiera jej pierwszeństwa.

Cel: Sprawdzić wskazaną zmianę i opublikować ocenę z dowodami.

Zakres: Czytane pliki / kontrakt / kryteria. Raport recenzenta w handoffs/ lub PR. Poprawki kodu należą do jego właściciela, chyba że odrębnie uzgodniono przekazanie.

## Warunek startu

Oceniane zadanie jest w review, a review_ref wskazuje dostępny w remote konkretny SHA/PR. W przypadku braku wersji zgłoś potrzebę przekazania. Nie czekaj na done ocenianego zadania i nie dodawaj go do depends_on; review_of jest relacją przeglądu, nie zależnością ukończenia.

## Kroki

1. Dokończ bieżące zadanie. Przy wyborze następnego zrób pull, sprawdź gotowość review i jego pierwszeństwo; zweryfikuj wersję i opublikuj własny commit IN PROGRESS przed przeglądem.
2. Sprawdź konkretne kryteria, integrację i adekwatne przypadki brzegowe; nie oceniaj wyłącznie opisu autora.
3. Opublikuj raport: sprawdzony SHA, co sprawdzono, wyniki, braki i zaakceptowano / wymagane poprawki.
4. Dla błędów dodaj konkretne zadanie właścicielowi kodu lub wskaż istniejącą kartę, bez duplikacji. Po istotnych poprawkach skontroluj zmieniony zakres.

## Kryteria odbioru przeglądu

- [ ] Raport dotyczy jawnie wskazanej wersji i jest dostępny w remote.
- [ ] Wynik poparto sprawdzeniami i odtwarzalnymi dowodami.
- [ ] Uwagi mają priorytet, właściciela i warunek akceptacji poprawki.
- [ ] Autor ocenianej zmiany otrzymał odnośnik przez kartę / PR w remote.

## Przebieg i dowody

Wpisz agenta, datę, work_branch, sprawdzony SHA, wysłane commity/PR i raport. Ukończenie review oznacza ukończenie przeglądu, nie automatyczne zaakceptowanie implementacji. Nie twórz automatycznie nieskończonego review przeglądów.
