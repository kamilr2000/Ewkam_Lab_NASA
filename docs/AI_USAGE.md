# Użycie AI / SI

Rejestr wspomagania pracy, aktualizowany przez każdy tor. Wymagania organizatora: [S03](sources/03-submission.md). Angielska wersja przeznaczona do publicznego pakietu powstaje w E-010.

## Zapis początkowy — 2026-11-14

- **Autorzy podstawowej idei:** Kamil i Ewelina. Zespół dostarczył pomysł globalnej aplikacji warstwowej z MCDA i Top 10; Kamil doprecyzował potrzebę zachowania pojedynczych dobrze dopasowanych pikseli.
- **Narzędzie:** asystent Codex. Dokładnego identyfikatora wersji modelu nie zapisano.
- **Zakres wspomagania:** analiza wskazanych źródeł, propozycja źródeł i metody, plan projektu, podział pracy, dokumentacja, karty zadań, kontrakt startowy i syntetyczne przypadki regresyjne.
- **Wygenerowane artefakty:** pliki przygotowania w początkowym commicie, w tym narzędzie kontroli dokumentacji. Fixture'y mają `is_synthetic: true` i `ai_assisted: true`; nie stanowią obserwacji Ziemi ani planet. Metadane: [ai-usage.json](ai-usage.json).
- **Stan kontroli:** zweryfikowano treści oficjalnych stron przez narzędzie odczytu; metoda, progi i architektura są propozycją wymagającą walidacji przy implementacji.
- **Media generatywne:** na tym etapie nie wygenerowano zdjęć, filmów ani audio. Nie wygenerowano materiałów zawierających branding NASA.
- **Dane naukowe:** nie pobrano i nie wygenerowano żadnych rzeczywistych pomiarów; dane testowe nie mogą zostać przedstawione jako pomiary.

## Kolejne wpisy

2026-11-14 — Codex pomógł doprecyzować pracę Kamila i Eweliny na osobnych komputerach: zdalne rezerwacje IN PROGRESS, commit/push każdej poprawki, obsługę konfliktów, aktualizację promptów i kontrolę metadanych kart. Na bezpośrednie polecenie Kamila utworzono repo, nadano nazwę Ewkam_Lab_NASA i wysłano zaproszenie write do ewelixa. Kontrole lokalnych dokumentów i syntetycznych przykładów przechodzą; nie jest to walidacja aplikacji.

2026-11-14 — I-007: Codex rozbudował oba prompty do samodzielnych Celów wykonawczych z kryteriami ukończenia, obowiązkowym pullem, rezerwacją przed implementacją, wykrywaniem braków oraz zlecaniem zadań i review drugiemu agentowi. Na wyraźną prośbę Kamila formalny submission oznaczono jako human_only; agenci kończą na gotowym pakiecie do ręcznego zgłoszenia. Zaktualizowano szablon przeglądu i instrukcje tak, by nie tworzyć zależności wymagającej done ocenianego zadania przed jego review.

| Data | Narzędzie / wersja, jeśli znana | Zadanie / pliki | Jak wspomogło pracę | Kontrola człowieka i testy | Oznaczenia w wyniku |
|---|---|---|---|---|---|
| Uzupełnij przy implementacji | | | | | |

Wraz z kodem lub danymi wspomaganymi przez AI dodaj opis i metadane wymagane dla tych materiałów. Jeżeli powstaną media, zastosuj oznaczenia właściwe dla ich typu według S03. Nie utożsamiaj użycia asystenta z wykorzystaniem danych NASA. Przed zgłoszeniem członkowie zespołu potwierdzają opis użycia narzędzi.
