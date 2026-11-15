# Decision log

This log records decisions and their rationale. Older task cards and handoffs retain their original evidence and timestamps.

| ID | Decision | Status / rationale |
|---|---|---|
| D-001 | The product vision includes a map, Mars/Moon choice, criteria, weights, and a Top 10. | Product goal; the integrated Earth search remains regional, not global. |
| D-002 | The default ranking unit is an individual analysis cell; adjacent results remain separate. | Preserves individual hotspots. |
| D-003 | A zoomed-out display uses the maximum score of a real pixel; a mean is context only. | Map aggregation occurs after combined pixel scoring. |
| D-004 | Distinct-area results are a separate mode from pixel Top 10. | Exposes spatial diversity without changing the default pixel ranking. |
| D-005 | A backend performs analysis; the full dataset is not sent to the browser. | Keeps one scoring implementation and bounds client workload. |
| D-006 | The selected stack is Python/FastAPI and React/TypeScript/Vite/MapLibre. | Implementation choice; no specific hosting provider is required. |
| D-007 | A 60-arc-second grid, roughly 2 km effective scale, and 10 km feature neighbourhood were initial global design proposals. | These are not evidence of a completed global scan. K-005 instead provides three regional UTM 2 km packages. |
| D-008 | P0 uses three topographic features; other domains are deferred. | Keeps the delivered scope explicit and bounded. |
| D-009 | A cell missing an active feature is excluded from ranking. | Candidates must be compared on the same active criteria. |
| D-010 | Mineralogy requires a separate comparability pilot. | The project does not claim an existing global mineral layer. |
| D-011 | Kamil owns data/API; Ewelina owns UI/demo. | Default organizational split; task owners remain authoritative. |
| D-012 | MIT applies to project code and documentation; third-party materials keep their terms. | Review rights before redistribution. |
| D-013 | The initial documentation-language plan was Polish operations and English public materials. | Superseded by I-014: maintained repository descriptions and guides are being standardized in English. Historical evidence is retained. |
| D-014 | Do not aggregate multiple pixels into a larger ranking candidate before scoring. | Superseded the initial H3-area proposal to preserve pixel-level measurements; requires adequate scan capacity. |
| D-015 | The shared remote is kamilr2000/Ewkam_Lab_NASA. | Separate computers exchange work through origin; publish task reservation on main before implementation. |
| D-016 | The repository remains private. | Changing visibility requires a separate owner decision. |
| D-017 | The repository is named Ewkam_Lab_NASA; Ewelina's GitHub account is ewelixa. | Keep access and origin instructions current. |
| D-018 | Formal submission is human-only. | Only Kamil or Ewelina may submit or make required attestations. |
| D-019 | Each agent synchronizes its own clone and may create a task for the other. | Review cards identify exact refs and must not deadlock on the reviewed task's done status. |
| D-020 | Finish current work before selecting a ready review; reviews outrank other tasks after synchronization. | Prefer reviews that unblock the other owner, then the oldest ready request. |
| D-021 | K-005's regional cell grid is 2 km UTM; the 60-arc-second budget is a model, not a global run. | Regional and planned-global products must not be mixed. |
| D-022 | Small, compressed K-005 tables are versioned derived runtime inputs; raw/intermediate rasters stay local. | Manifests preserve provenance and checksums. |
| D-023 | Apply GSHHG source masking before ETOPO is averaged into K-005 coastal cells. | Prevents ocean bathymetry from contaminating land elevations; the change is recorded in v2 and its tests. |

Add new decisions with date, owner, rationale, considered options, and impact on scope/contracts/data. Supersede an old entry explicitly rather than rewriting it to erase its original context.
