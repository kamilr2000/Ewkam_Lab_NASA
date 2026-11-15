# E-026 — Re-review fingerprintu K-005

Data: 2026-11-15

Wynik: **APPROVED** dla korekty fingerprintu i zachowanych danych regionalnych.

Reviewed exact metadata commit: `d3b880cacbbdf339d078a2fbedbe8fd373db7bef`

Current PR #44 head podczas review: `3a07fc27fdad44472bcf61b1bc1347ae5b02fff6`

Opublikowana recenzja: [PR #44](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/44), review ID `5910439313`.

## Sprawdzone dowody

- Na exact `d3b880c` niezależne wywołanie `_code_fingerprint()` zwróciło `56543c206661c3158999fd442f13a3ebc56e695333da8b2ad01b1e19d8d63829`. Ten sam fingerprint występuje w raporcie i w `processing.code_version` wszystkich trzech manifestów.
- Trzy manifesty przechodzą `contracts/dataset-manifest.schema.json` w Draft 2020-12. Raport, manifesty i manifest źródeł K-017 zgadzają się co do przypiętych rozmiarów/SHA wejść, ścieżek/rozmiarów/SHA wyjść, liczności, czasu przetworzenia i flagi `is_synthetic: false`.
- Każdy plik CSV gzip został niezależnie sprawdzony względem manifestu: rozmiar, SHA-256 i liczba rekordów. Wartości wyjściowe są identyczne z poprzednim odbiorem E-024:

| AOI | Bajty | Wiersze / kwalifikujące się | SHA-256 |
|---|---:|---:|---|
| Atacama / Andes | 63,856 | 1,796 / 1,791 | `784ccc0dbebe4e846774ac819809029a31f082cb16931e6bbe882da26c0f570c` |
| Big Island | 64,177 | 1,854 / 1,497 | `5489e51b4ec4f1a770fe7e7511565de6e5083b4547ebb48d61ada3af0ec4668b` |
| Himalaya | 61,206 | 1,737 / 1,737 | `30a3dd1d93277a766b9d7d9ddcd8a2c05c9db4df374a4bb310eaac97f143479c` |

- Porównanie `a5dfe3d..d3b880c` nie wykazało zmian w `pipeline/` ani `data/derived/`; zmieniono tylko trzy manifesty i raport. Bieżący head PR #44 po `d3b880c` nie zmienia ponownie buildera, raportu, manifestów ani CSV. Zmiany wyników nie powstały w ramach korekty fingerprintu.
- `uv run --locked --group data python -m pytest pipeline/tests contracts/tests -q` — 45 passed na exact `d3b880c`.
- `python tools/check_planning.py` — OK na exact `d3b880c` (155 Markdown, 40 JSON, 75 kart) i na bieżącym headzie PR (158 Markdown, 40 JSON, 78 kart); bez cykli, 5 przypadków syntetycznych.

## Rebuild, pochodzenie i ograniczenia

Raport ma końcowy czas `2026-11-15T10:58:32Z`; trzy manifesty zapisują odpowiednio `10:57:40Z`, `10:58:03Z` i `10:58:32Z`, zgodnie z `processing.processed_at`. Czasy pakietów to 19.44 s, 23.47 s i 28.65 s, a każdy ma `resumed_from_checkpoint: false`. Jest to spójne z odnotowanym przez właściciela przebiegiem `--force`; nie mierzyłam tych czasów ponownie.

Pliki surowe ETOPO/GSHHG nie są obecne w tym klonie. Nie uruchamiałam ponownego pobrania ani pełnej przebudowy; niezależnie porównałam deklarowane rozmiary i SHA wejść z przypiętym manifestem K-017 oraz obecne wyjścia z poprzednim, niezależnie odtworzonym wynikiem E-024. E-024 wcześniej sprawdziła publiczne źródła i bajtową zgodność wyjść. Nie zweryfikowałam ponownie bieżących bajtów źródeł ani czasu ściennego nowego przebiegu.

Kod przelicza cechy deterministycznie z ETOPO i GSHHG; korekta dotyczy wyłącznie metadanych. Nie powstały nowe pomiary wygenerowane przez AI. To trzy pomiary regionalne, nie globalne pokrycie/ranking; obszary polarne nie są zwalidowane.

## Drobne działania przed integracją PR #44

Nieblokujący P2: opis PR #44 nadal mówi, że builder użył ponownie zweryfikowanych checkpointów, natomiast poprawiony handoff dokumentuje wymuszony rebuild `--force`. Należy ujednolicić opis PR z aktualnym handoffem. Podczas review GitHub zgłaszał PR jako niegotowy do merge i wskazywał starszą bazę `b9f4df4`; gałąź należy zsynchronizować z aktualnym `origin/main` przed integracją. Recenzja akceptuje exact dane i fingerprint, nie scala PR #44 za właściciela.
