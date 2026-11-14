---
id: K-012
owner: kamil
reviewer: ewelina
priority: P0
task_type: implementation
status: todo
depends_on: []
agent: unassigned
work_branch: unassigned
updated: 2026-11-14
discovered_from: TASK-ID-or-source
---

# TASK-ID — krótki konkretny tytuł

Cel: obserwowalny rezultat i powód, dla którego praca jest potrzebna.

Zakres: dokładne pliki/moduły oraz ewentualne potrzebne przekazanie między torami.

## Kroki

1. Konkretne działanie.
2. Konkretne działanie.
3. Sprawdzenie i dokumentacja.

## Kryteria odbioru

- [ ] Testowalny warunek.
- [ ] Warunek obejmujący problem brzegowy.
- [ ] Źródła/kontrakt/handoff zaktualizowane, jeśli potrzebne.

## Sprawdzenie

Jak potwierdzisz działanie; nie kopiuj automatycznie komend, których repo jeszcze nie ma.

## Przebieg i dowody

Przed implementacją opublikuj osobny commit `tasks(ID): IN PROGRESS` w `origin/main`, ustawiający `status: in_progress`, agenta, datę i gałąź. Potwierdź zdalną rezerwację. Każdą poprawkę commituj i wysyłaj; synchronizuj remote i rozwiązuj rzeczywiste konflikty. Data, agent, kroki, sprawdzenia, wysłane SHA/URL PR i ograniczenia. `done` dopiero po odbiorze i integracji do `origin/main`. Przy blokadzie: warunek, zależność, niewysłane zmiany i następne działanie.

## Powód dodania / wpływ

Co odkryto w zadaniu lub źródle, co blokuje, dlaczego P0/P1/P2. Dodaj link do indeksu i zależności w zablokowanych kartach. Sprawdź cykle. Nie wymyślaj nowych P0 bez związku z MVP.

Możesz utworzyć tę kartę dla drugiego agenta: prefix i owner należą do odbiorcy, który sam rezerwuje zadanie. Dla review użyj REVIEW_TEMPLATE.md i wskaż review_of/review_ref zamiast zależności od done ocenianej pracy. Dla własnej implementacji wymagającej odbioru możesz dodać review_tasks z ID przeglądu.
