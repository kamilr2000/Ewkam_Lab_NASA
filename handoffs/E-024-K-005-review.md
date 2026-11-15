# E-024 — wynik przeglądu K-005

Data: 2026-11-15
Reviewed commit: `a5dfe3d892235d31938dcdd56bdcc17a66e0f167`
PR: [#44](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/44)
Wynik: **REQUEST_CHANGES** — jedno P1 dotyczące metadanych pochodzenia danych.

## Zakres i odtwarzalne sprawdzenia

Przegląd dotyczy dokładnego `review_ref` z PR #44. W izolowanym katalogu odtworzyłam źródła oraz budowę regionalnych pakietów poleceniami z karty:

```powershell
uv run --locked --group data python pipeline/download_k005_sources.py
uv run --locked --group data python pipeline/build_k005_earth_grid.py --force
uv run --locked --group data python -m pytest pipeline/tests contracts/tests -q
uv run --locked --group data python tools/check_planning.py
```

Wyniki: downloader sprawdził rozmiar i SHA-256 wszystkich plików; builder zakończył trzy pakiety; `pytest` — **45 passed**; `check_planning.py` — **OK**, zależności bez cykli, pięć przypadków syntetycznych. Check planowania ocenia dokumentację i przykładową arytmetykę, nie działanie aplikacji.

## Źródła i odtwarzalność

- ETOPO 2022 v1, rozdzielczość 15″, powierzchnia z pionowym odniesieniem EGM2008, CC0-1.0, DOI `10.25921/fd45-gt74`; [metadane NCEI](https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ngdc.mgg.dem%3Aetopo_2022/html).
- GSHHG 2.3.7, licencja LGPL-3.0-or-later; [oficjalna strona GSHHG](https://www.soest.hawaii.edu/pwessel/gshhg/), DOI `10.5281/zenodo.7007502`.
- Zweryfikowane artefakty źródłowe: `ETOPO_2022_v1_15s_N30W165_surface.tif` — 22 411 557 B, SHA-256 `8265ec91d7db7644d227374afe91d23662203a4eb3fd580626b3f7d3d27dc85c`; `ETOPO_2022_v1_15s_N30E075_surface.tif` — 30 871 200 B, `cbb763175d331ed0222da35f357d3837aa8218aeda72e586974ef2a53f9027d4`; `ETOPO_2022_v1_15s_S15W075_surface.tif` — 30 004 071 B, `1872b57145c8d18ebd44cf6d08de601bd34c067dc5a780038b0754398444eaf9`; `gshhg-shp-2.3.7.zip` — 149 157 845 B, `8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41`.
- Wartości DEM pochodzą z pobranych plików ETOPO, a geometrie z GSHHG; pipeline nie tworzy pomiarów przez AI.

## Wyniki naukowe i techniczne

- Maska GSHHG jest rasteryzowana na natywnej siatce ETOPO i stosowana przed uśrednianiem. Oddzielna maska lądu na siatce docelowej i estymacja `land_fraction_4x` z 4× próbkowania centrów subkomórek zachowują rozróżnienie między maską centrum a przybliżonym udziałem lądu. Test mieszanej komórki `+100 m` lądu i `−100 m` oceanu zwraca `+100 m`, bez domieszki batymetrii.
- Dane wejściowe ETOPO mają nodata, a brakujące próbki pozostają nieważne. Okna cech są kołowe, o promieniu 10 km; mają 81 próbek przy siatce 2 km i wymagają co najmniej 73. Gradient i okna są w metrach. Nierówność to odchylenie standardowe reszt po dopasowaniu płaszczyzny, a relief to P95−P05. Braki i niekwalifikowane komórki nie są wypełniane zerami.
- Każdy AOI używa własnej lokalnej strefy UTM: Atacama/Andy EPSG:32719, Big Island EPSG:32605, Himalaje EPSG:32645. Powierzchnie komórek są wyliczane geodezyjnie z narożników na elipsoidzie WGS84. Nie mieszają się siatki między AOI.
- Odtworzone CSV są bajtowo identyczne z plikami wskazanego commita. Liczby kandydatów / kwalifikujących się komórek: Atacama 1 796 / 1 791; Big Island 1 854 / 1 497; Himalaje 1 737 / 1 737. SHA-256 CSV: Atacama `784ccc0dbebe4e846774ac819809029a31f082cb16931e6bbe882da26c0f570c`; Big Island `5489e51b4ec4f1a770fe7e7511565de6e5083b4547ebb48d61ada3af0ec4668b`; Himalaje `30a3dd1d93277a766b9d7d9ddcd8a2c05c9db4df374a4bb310eaac97f143479c`.
- Sprawdzono unikalność i stabilny format ID, liczności, kwalifikację, powody braków, zakresy centrów, manifesty względem JSON Schema 2020-12 i walidację semantyczną, a także SHA/rozmiar i zasięgi w manifestach.
- Niezależne obliczenie trzech ręcznych komórek z rastrem źródłowym, maskami i promieniem użytym przez builder dało 81 próbek w każdym oknie. Maksymalna różnica od raportu i CSV była mniejsza niż `0.00002`: Atacama — nachylenie 5.164046°, nierówność 192.678488 m, relief 689.403320 m; Big Island — 5.864032°, 268.396041 m, 1517.441650 m; Himalaje — 2.052802°, 143.855982 m, 781.523926 m.
- Jawny budżet 60″ jest arytmetycznym modelem, nie wykonanym globalnym przetwarzaniem: 233 280 000 komórek; 6 065 280 000 B pełnego stanu kandydata; 208 094 400 B modelowanej pamięci roboczej dla wsadowego przetwarzania wraz z maską źródłową i halo. Pipeline nie publikuje globalnego rastra ani rankingu; obszary polarne pozostają poza walidacją.

## Wymagana poprawka — P1, właściciel: Kamil

W manifeście raportu i trzech manifestach zbiorów z reviewed commit zapisano fingerprint kodu `feab8cb9a942e6c7e8217f0d27d1a9b1f676d874d8c99ba32b6d4e9c2b81778f`. Funkcja `_code_fingerprint()` uruchomiona na dokładnym kodzie z tego commita wylicza `56543c206661c3158999fd442f13a3ebc56e695333da8b2ad01b1e19d8d63829`. To oznacza, że opublikowane metadane nie identyfikują kodu, który buduje przypięte CSV.

Potwierdziłam, że ponowne `build_k005_earth_grid.py --force` zapisuje fingerprint zgodny z kodem i pozostawia trzy CSV bajtowo identyczne. Różnica `resumed_from_checkpoint` wynika z trybu wymuszonej przebudowy i sama nie jest błędem.

Warunek odbioru: opublikować zaktualizowane raport i trzy manifesty, w których fingerprint odpowiada exact kodowi; zachować dotychczasowe SHA CSV lub opisać każdą zmianę; ponownie przejść walidację manifestów i wymagane testy. Nowy commit wymaga przeglądu zmienionego zakresu. Nie zatwierdzać obecnych metadanych jako kompletnego pochodzenia danych.

PR #44 pozostawał otwarty i GitHub zgłaszał `mergeable: false` w czasie przeglądu. Niczego nie łączyłam. Po poprawce autor powinien zsynchronizować gałąź z aktualnym `main` i dopiero wtedy przekazać nowy SHA do ponownego review.
