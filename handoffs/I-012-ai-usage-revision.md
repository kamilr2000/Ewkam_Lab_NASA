# Przekazanie: I-012 — korekta statusów rejestru AI/SI

- Od: Ewelina, `codex-ewelina-i012-k031-revision`
- Do: Kamil
- Data: 2026-11-15
- Zadanie / PR / exact commit: I-012 / [PR #46](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/46) / `7481397528d190bd4f7be69e925cc43848bcb034`
- Zdalne repo i gałąź: `kamilr2000/Ewkam_Lab_NASA`, `ewelina/I-012-ai-usage-followup`
- Zakres: `docs/AI_USAGE.md`, `docs/ai-usage.json`, statusy i dowody I-012
- Powód: re-review K-031 `REQUEST_CHANGES` dla exact `17dab257e82e7f3f82baf7df77d1483a076a588f` wykrył nieaktualne stany E-004/E-005/E-021 i zbiorczy JSON.

## Korekty

- E-005: K-028 zatwierdziło exact `98be49cac38e6d72245a092e7a59bab7c5599424`; PR #31 nadal jest otwarty i niezintegrowany, więc E-005 ma `review`. Live API pozostaje health-only.
- E-004: K-032 zatwierdziło lazy-load exact `e63ded588f07b9925c54075a31e581d07bfc5fc9`; PR #37 nadal jest otwarty i niezintegrowany, więc E-004 ma `review`. Mapa nie została wizualnie potwierdzona w tym review; build zgłasza asynchroniczny chunk mapy 1,085.35 kB minified, powyżej progu 500 kB.
- E-021: K-030 zakończyło `REQUEST_CHANGES`; żądane 781 px dało `innerWidth=782`. E-021 wróciło do `in_progress`; dokładny pomiar nadal nie istnieje. Ostatnia próba nie uzyskała lokalnego preview, więc nie dodano nowych screenshotów ani metryk.
- E-023: zaakceptowane review K-004 exact `d9ff76f7d5f3cfd18a55b82def271b9cc35030dc`; PR #36 pozostaje otwarty.
- E-024: raport E-024 dla K-005 exact `a5dfe3d892235d31938dcdd56bdcc17a66e0f167` zgłosił P1 `REQUEST_CHANGES` z powodu fingerprintu kodu. Poprawiony rebuild nie zmienił CSV; wymaga osobnego review.
- E-019/E-022: K-020 zgłosiło korektę zakresu/coverage; K-022 opublikowało syntetyczną poprawkę w otwartym PR #28, a E-022 recenzuje exact `8fb3ab5da9117090b430fbe29df76862c6e70cda`.

JSON zachowuje wszystkie 14 istniejących ścieżek syntetycznych, `generated_media: []` i `measurements_generated_by_ai: false`. Nie zmieniono twierdzeń o K-002/K-017 ani ograniczenia, że backend udostępnia tylko health endpoint. Rejestr nie deklaruje NASA endorsement ani wykonanego submission.

## Sprawdzenia

- `python tools/check_planning.py` — OK: 145 Markdown, 32 JSON, 71 kart, acykliczne zależności, 5 przypadków syntetycznych.
- `python -m json.tool docs/ai-usage.json` — poprawny JSON.
- Wszystkie 14 `synthetic_data_paths` wskazuje istniejące pliki.
- `git diff --check` — bez błędów.

To kontrole rejestru i repozytoryjnego planowania, nie re-analiza danych naukowych, wizualny odbiór mapy ani potwierdzenie działania pełnej aplikacji. Proszę o niezależne re-review exact commita `7481397528d190bd4f7be69e925cc43848bcb034` w PR #46 przez K-034. I-012 pozostaje w `review` do odbioru i integracji do `origin/main`.
