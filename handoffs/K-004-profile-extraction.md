# K-004 — handoff ekstrakcji profili planetarnych

## Zakres

Profil Jezero z MOLA MEGDR v2, 128 px/° oraz profil południowej czapy Księżyca 80–90°S z NASA PGDA LOLA Product 90. Obliczenia używają nominalnej siatki 2 km, kołowego okna cech o promieniu fizycznym 10 km i trzech cech P0: nachylenia, nierówności po odjęciu płaszczyzny oraz deniwelacji P95−P05. Nie porównują bezwzględnych wysokości między ciałami.

## Dane i reprodukcja

- `data/manifests/k004-source-files.json` przypina 14 rastrów i etykiet źródłowych rozmiarem, SHA-256, URL-em i datą pobrania.
- Pobieranie: `python pipeline/download_k004_sources.py`.
- Ekstrakcja: `python pipeline/profiles/build_profiles.py`.
- Surowe rastry pozostają w ignorowanym `data/raw/k004`; downloader nie potrzebuje Earthdata Login.
- Wyniki: `pipeline/profiles/mars-jezero-v1.json`, `pipeline/profiles/moon-south-polar-80s-v1.json` oraz `data/manifests/k004-planetary-profiles.json`.

## Wyniki i jakość

- Jezero: 448 komórek celu; 448 ma wszystkie trzy cechy. Z binów MEGC w obszarze 35,40% ma bezpośrednie obserwacje, a 95,54% komórek 2 km przecina co najmniej jeden bezpośrednio mierzony bin. Pozostałe MEGT zawiera interpolowaną topografię produktu.
- Księżyc 80–90°S: 72 580 komórek celu i 72 100 (99,34%) z trzema cechami. Każda komórka ma ważną zagregowaną wartość DEM po bramce jakości EFFRES. W 480 oknach wsparcie jest niższe niż 90%, więc nierówność i deniwelacja są niedostępne; nachylenie nie ma wymaganych sąsiadów różnicy centralnej w 96 komórkach przy krawędzi kafla. Powód i liczności braków są rozpisane w manifeście. Minimum wsparcia okna to 56,79%, P01 90,12%, a P05/P50/P95 100%.
- P50/P95 efektywnej rozdzielczości i wysokości błędu po uśrednieniu warstw do komórki analitycznej są jawnie nazwane w manifeście. Nie opisują natywnych próbek rastra 80 m.
- Tolerancje to wynikowo niezależne, prowizoryczne założenie 1,5×IQR danego profilu; nie są niepewnością instrumentu ani progiem NASA. Sąsiednie komórki są przestrzennie zależne z powodu nakładających się okien.

## Weryfikacja

- Downloader ponownie zweryfikował istniejące 14/14 plików manifestu.
- Builder odtworzył oba profile z lokalnych rastrów. Ręczna ekstrakcja trzech cech w jednym punkcie oraz kontrola przejścia długości geograficznej przez transformację w obie strony przeszły dla każdego profilu.
- Obie odpowiedzi `ProfileResponse v1` przeszły walidację JSON Schema; asercje manifeście potwierdziły liczbę komórek i rozkład braków na krawędzi LOLA.
- `python tools/check_planning.py` zgłosił OK dla dokumentacji i metadanych planu. `git diff --check` i kompilacja składni Pythona przeszły.
- Te kontrole potwierdzają ekstrakcję dwóch zmierzonych obszarów. Nie potwierdzają globalnego rankingu Ziemi, działania pełnego demo ani jednoznaczności analogów.

Szczegółowa metoda, źródła, DOI, wartości i ograniczenia są w `docs/METHODOLOGY.md`, `docs/DATA.md`, `THIRD_PARTY.md` oraz manifeście wyników. Dokładną gałąź i reviewed SHA wskazują K-004 i E-023 po publikacji PR.

## Przekazanie disclosure K-004 do Eweliny

Gałąź K-004 zawierała wpis K-004 w `docs/AI_USAGE.md` i źródłowe manifesty profili w `docs/ai-usage.json`. Przy synchronizacji z najnowszym `origin/main` wystąpił konflikt w tych plikach należących do bieżącego toru I-012. Aby zachować wersję disclosure z main bez nadpisywania aktywnej pracy Eweliny, wpis K-004 został odłożony do aktualizacji przez Ewelinę po integracji profili. Proszę uwzględnić w rejestrze: Codex pomógł przypiąć 14 publicznych plików NASA PDS/PGDA, przygotować downloader i builder profili Jezero oraz księżycowej czapy 80–90°S; wartości obliczył kod z oryginalnych rastrów, AI ich nie wygenerowało ani nie edytowało; E-023 zaakceptowała exact `d9ff76f7d5f3cfd18a55b82def271b9cc35030dc`; wyniki dotyczą dwóch profili regionalnych, nie globalnego rankingu ani zwalidowanego analogu.

Do JSON metadanych należą `data/manifests/k004-source-files.json` i `data/manifests/k004-planetary-profiles.json`. Uaktualnij stan PR #36 i integracji na chwilę wpisu. Właścicielka ścieżek `docs/AI_USAGE.md` / `docs/ai-usage.json`: Ewelina w I-012; nie zmieniałem tych plików w tym PR poza zachowaniem wersji z `origin/main` podczas scalania.
