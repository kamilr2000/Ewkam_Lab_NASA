# Ryzyka i reakcje

| Ryzyko | Sygnał | Reakcja / odpowiedzialność |
|---|---|---|
| Zbyt mało czasu na pełny świat | Nie ma G2 po ok. 8 h | Zatrzymać P1, uprościć UI, mierzyć i ewentualnie jawnie zwiększyć rozmiar komórki; Kamil |
| Brak danych / dostęp po zalogowaniu | Nie można odczytać próbki w G1 | Wybrać inny jawny produkt lub regionalny zakres; nie odkładać pobierania na koniec; Kamil |
| Globalne przeszukiwanie zbyt ciężkie | Benchmark przekracza pamięć / czas | Przetwarzanie partiami, cache, kompaktowe tablice; potem nowa jawna wersja siatki; Kamil |
| Średnia chowa dobry piksel | Fixture hotspotu nie przechodzi | Pełny skan przed agregacją, mapa maksimum, ranking pikseli; oboje |
| Pozorny wynik z maksimów innych pikseli | Dwie warstwy tworzą fikcyjny ideał | Agregować dopiero łączny wynik każdego piksela; Kamil |
| Artefakt wygrywa ranking | Pojedynczy peak przy brzegu / nodata | QA i kontrola źródła; izolację pokazać, nie usuwać bez dowodu; Kamil |
| „5 km” oznacza różne skale | Źródło i komórka / okno niespójne | Metadane wsparcia pomiaru, wspólna skala i porównanie rozdzielczości; Kamil |
| Trzy cechy DEM udają pełne środowisko | Prezentacja mówi ogólnie „podobne do Marsa” | Jawny profil topograficzny i ograniczenia; Ewelina |
| Globalna mineralogia niedostępna | Dane regionalne lub różne klasy | Pilotaż z macierzą zgodności; bez globalnego procentu; Kamil |
| Znikają bieguny lub małe wyspy | Domyślna projekcja / maska pomija zakres | Raport zasięgu, odpowiedni widok mapy i kwalifikowalność; oboje |
| Zmiany kontraktu blokują UI | Brak zgodnych fixture'ów | Wersjonowanie, wczesny handoff i test kontraktowy; oboje |
| Wyniki nieodtwarzalne | Zmieniły się źródła / wagi bez wersji | Manifest, hash konfiguracji i zamrożona analiza; Kamil |
| Hosting wymaga logowania / jest niedostępny | Link nie działa w prywatnym oknie | Publiczny build i lokalna instrukcja; statyczny fallback opisany jako ograniczenie; oboje |
| Pakiet jury nie spełnia edycji 2026 | Za długie demo, brak źródeł lub ujawnienia AI | Kontrola S03/S04 w I-005 przed formalnym wysłaniem; Ewelina |

Priorytetem jest działający, uczciwie opisany pionowy przepływ i czas na zgłoszenie. Nowo odkryte ryzyko prowadzi do konkretnej karty; sam dopisek w tej tabeli nie zastępuje działania.
