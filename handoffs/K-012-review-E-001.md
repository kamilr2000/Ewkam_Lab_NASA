# K-012 — Review E-001 / PR #3

- Data przeglądu: 2026-11-14
- Reviewer: `codex-kamil-k012-review`
- Gałąź zadania: `kamil/K-012-review-e001`
- Sprawdzony commit: `1add6d4a40226806fd9de30492163f153597279e`
- PR: https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/3
- Wynik: wymagane poprawki przed integracją — jedno P1 dotyczące widocznego zakresu interpretacji kryteriów.

## Sprawdzenia

- Zarchiwizowano dokładny head PR do czystego katalogu tymczasowego i uruchomiono `npm ci` przy Node 22.18.0 / npm 10.4.0. Instalacja dodała 49 pakietów, audyt objął 50 pakietów i zgłosił 0 podatności.
- `npm run build` zakończył typecheck i produkcyjny build Vite 8.3.8 bez błędów.
- Serwer deweloperski z `npm run dev -- --host 127.0.0.1 --port 5181 --strictPort` wystartował. `/`, `/src/main.tsx` oraz `/src/styles.css` zwróciły HTTP 200.
- Wizualnie sprawdzono desktop 1365×900 oraz tablet 682×900. Przy 682 px panel sterowania i wyniki układają się pionowo, etykiety mapy nie nachodzą na siebie.
- Emulacja rzeczywistego CSS viewportu w Chrome dla 390, 375 i 320 px potwierdziła brak poziomego przewijania: `clientWidth` i `scrollWidth` były równe dla każdej szerokości. Nie sprawdzano fizycznego urządzenia ani czytnika ekranu.
- Zweryfikowano osiem bezpośrednich zależności i licencje z zainstalowanych metadanych pakietów; zgadzają się z tabelą `THIRD_PARTY.md`. Wszystkie 100 wpisów pakietów w lockfile ma metadane licencji.
- `git diff --check` dla PR względem `origin/main` zakończył się powodzeniem.

## Wynik merytoryczny

Szkielet wyraźnie pokazuje brak połączenia z API, brak aktywnego zbioru, niedostępne warstwy i brak wyników. Kontrolki są wyłączone. Nie ma podkładu mapowego, danych pomiarowych ani obliczeń klienta. Skala indeksu 0–100% jest zgodna z `docs/CONTRACTS.md`. Instalacja, zależności, responsywny układ na sprawdzonych szerokościach i build są odtwarzalne.

### P1 — doprecyzować, że trzy kryteria P0 opisują powiązaną topografię

- Właściciel: Ewelina / E-001.
- Miejsce: panel `TERRAIN CRITERIA` i etykiety `CORE` w `apps/web/src/App.tsx`.
- Powód: `docs/PRODUCT.md` wymaga, by UI mówił, że trzy warstwy P0 należą do jednej dziedziny — topografii — i są ze sobą powiązane. Ekran prezentuje je jako trzy kryteria `CORE`, a obecna uwaga mówi tylko o indeksie podobieństwa terenu i habitability. Użytkownik nie dostaje jawnej informacji, że nie są to trzy niezależne wymiary środowiska.
- Warunek akceptacji: widoczny tekst obok listy kryteriów nazywa je powiązanymi miarami topografii i wyjaśnia, że wynik nie jest pełną oceną środowiska; analogiczny zakres pozostaje widoczny przy przyszłym wyjaśnieniu wyników.

## Ograniczenia

Nie sprawdzano połączenia z działającym API ani wyników analizy, bo E-001 celowo udostępnia wyłącznie szkielet. Nie wykonano pełnego testu czytnikiem ekranu ani na fizycznym telefonie. Ręczna kontrola była wizualna; heurystyczny skaner dostępności miał fałszywe alarmy dla semantycznego elementu `<main>` i `role="status"` w JSX.
