# Użycie AI / SI

Rejestr wspomagania pracy, aktualizowany przez każdy tor. Wymagania organizatora: [S03](sources/03-submission.md). Angielska wersja przeznaczona do publicznego pakietu powstaje w E-010.

## Zapis początkowy — 2026-11-14

- **Autorzy podstawowej idei:** Kamil i Ewelina. Zespół dostarczył pomysł globalnej aplikacji warstwowej z MCDA i Top 10; Kamil doprecyzował potrzebę zachowania pojedynczych dobrze dopasowanych pikseli.
- **Narzędzie:** asystent Codex. Dokładnego identyfikatora wersji modelu nie zapisano.
- **Zakres wspomagania:** analiza wskazanych źródeł, propozycja źródeł i metody, plan projektu, podział pracy, dokumentacja, karty zadań, kontrakt startowy i syntetyczne przypadki regresyjne.
- **Wygenerowane artefakty:** pliki przygotowania w początkowym commicie, w tym narzędzie kontroli dokumentacji. Fixture'y mają `is_synthetic: true` i `ai_assisted: true`; nie stanowią obserwacji Ziemi ani planet. Metadane: [ai-usage.json](ai-usage.json).
- **Stan kontroli:** oficjalne metadane źródeł sprawdzono, a rzeczywiste pliki próbek Ziemi/LOLA/MOLA pobrano bezpośrednio z NOAA i NASA PDS, po czym zweryfikowano etykiety, odczyt i sumy SHA-256. Asystent pomógł przygotować manifest, instrukcję pobrania i streszczenie ograniczeń; AI nie wygenerowało ani nie zmieniło pomiarów. NASADEM nie został pobrany z powodu wymaganego uwierzytelnienia Earthdata. Metoda, progi i architektura nadal wymagają walidacji przy implementacji.
- **Media generatywne:** na tym etapie nie wygenerowano zdjęć, filmów ani audio. Nie wygenerowano materiałów zawierających branding NASA.
- **Dane naukowe:** pobrano rzeczywiste próbki ETOPO 2022, LOLA LDEM_4 i MOLA MEGT/MEGC; surowe pliki są ignorowane przez Git, a ich pochodzenie i SHA-256 są w data/manifests/k002-samples.json. Nie wygenerowano pomiarów ani danych syntetycznych do tych próbek.

## Kolejne wpisy

2026-11-14 — Codex pomógł doprecyzować pracę Kamila i Eweliny na osobnych komputerach: zdalne rezerwacje IN PROGRESS, commit/push każdej poprawki, obsługę konfliktów, aktualizację promptów i kontrolę metadanych kart. Na bezpośrednie polecenie Kamila utworzono repo, nadano nazwę Ewkam_Lab_NASA i wysłano zaproszenie write do ewelixa. Kontrole lokalnych dokumentów i syntetycznych przykładów przechodzą; nie jest to walidacja aplikacji.

2026-11-14 — I-007: Codex rozbudował oba prompty do samodzielnych Celów wykonawczych z kryteriami ukończenia, obowiązkowym pullem, rezerwacją przed implementacją, wykrywaniem braków oraz zlecaniem zadań i review drugiemu agentowi. Na wyraźną prośbę Kamila formalny submission oznaczono jako human_only; agenci kończą na gotowym pakiecie do ręcznego zgłoszenia. Zaktualizowano szablon przeglądu i instrukcje tak, by nie tworzyć zależności wymagającej done ocenianego zadania przed jego review.

2026-11-14 — I-008: Codex doprecyzował pierwszeństwo gotowych review przy wyborze następnego zadania, także przed zwykłymi P0, bez przerywania już wykonywanej pracy. Zaktualizowano oba Cele, instrukcje i szablon przeglądu; sprawdzenia dotyczą dokumentacji, nie działania aplikacji.

2026-11-14 — K-002: Codex sprawdził oficjalne metadane NOAA ETOPO oraz NASA PDS LOLA/MOLA, pobrał próbki z oficjalnych serwerów i przygotował manifest oraz mały downloader sprawdzający rozmiar i SHA-256. Pomiary i etykiety pochodzą z archiwów; asystent nie wygenerował ani nie edytował danych. NASADEM pozostał niedostępny bez logowania Earthdata; dokładny stan i ograniczenia zapisano w manifeście.

| Data | Narzędzie / wersja, jeśli znana | Zadanie / pliki | Jak wspomogło pracę | Kontrola człowieka i testy | Oznaczenia w wyniku |
|---|---|---|---|---|---|
| 2026-11-14 | OpenAI Codex (wersja nieustalona) | K-001: `pyproject.toml`, API FastAPI, test gotowości i instrukcje środowiska | Utworzył szkielet backendu i konfigurację zależności. | Zainstalowano `uv.lock` w nowym `.venv` na Pythonie 3.12.14; `pytest` zakończył się `1 passed`; lokalny endpoint zwrócił stan gotowości i jawny brak danych. Przegląd człowieka pozostaje wymagany. | Nie wygenerowano danych ani pomiarów naukowych. |
| 2026-11-14 | OpenAI Codex (wersja nieustalona) | E-001: scaffold w `apps/web/` — m.in. `src/App.tsx`, `src/main.tsx`, `src/styles.css`, `package.json`, `package-lock.json`, `README.md` | Przygotował szkielet React/TypeScript/Vite, responsywny pusty widok oraz tekst ograniczający zakres MVP do powiązanych miar topografii po uwadze K-012. | Kamil w review K-012 wskazał potrzebę doprecyzowania zakresu; Codex wprowadził poprawkę. `npm run build --prefix apps/web` (TypeScript i Vite) przeszło po poprawce. Follow-up K-013 oczekuje na niezależny review; nie przypisujemy mu jeszcze akceptacji. | Nie wytworzono pomiarów, profili, wyników ani potwierdzenia NASA endorsement. Dane i API nie są podłączone; AI wspomogło kod i treść interfejsu. |

Wraz z kodem lub danymi wspomaganymi przez AI dodaj opis i metadane wymagane dla tych materiałów. Jeżeli powstaną media, zastosuj oznaczenia właściwe dla ich typu według S03. Nie utożsamiaj użycia asystenta z wykorzystaniem danych NASA. Przed zgłoszeniem członkowie zespołu potwierdzają opis użycia narzędzi.
