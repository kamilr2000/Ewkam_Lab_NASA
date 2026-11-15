# Risks and responses

| Risk | Signal | Response / owner |
|---|---|---|
| Insufficient time for global processing | No evidence of a complete global run | Defer P1 work; keep the regional scope explicit. Kamil owns data and processing. |
| Source access or authentication failure | Required sample cannot be downloaded | Select a documented alternative or restrict scope; do not postpone acquisition checks. Kamil. |
| Processing exceeds memory or time budget | Benchmarks exceed the measured budget | Process in batches; any coarser grid requires a new, explicit dataset version. Kamil. |
| Mean aggregation hides a hotspot | Isolated-hotspot fixture fails | Score pixels before aggregation; preserve the pixel maximum and ID. Both owners. |
| A map combines maxima from different pixels | Layer maxima imply a candidate that does not exist | Aggregate each pixel's combined score, then aggregate map display cells. Kamil. |
| Source artifact wins the ranking | Peak occurs at a boundary or invalid-data edge | Check source and QA; show isolation rather than silently dropping the candidate. Kamil. |
| Nominal resolution is mistaken for effective support | Source grid, analysis cell, and feature window differ | Expose each scale and compare resolution explicitly. Kamil. |
| Terrain-only score is described as whole-environment similarity | Copy says a place is generally “like Mars” | Name the profile and topographic criteria; state limitations. Ewelina. |
| Planetary mineral layers cannot be compared | Coverage or class definitions differ | Run a small documented pilot first; do not publish a global mineral percentage. Kamil. |
| Polar areas or small islands disappear | Projection, mask, or source extent excludes them | Report coverage and eligibility; use an appropriate map view. Both owners. |
| API contract changes break the UI | Fixtures and adapter disagree | Version contracts and publish handoffs early. Both owners. |
| Results cannot be reproduced | Source files or weights changed without a version | Keep source manifests, configuration, hashes, and immutable analysis identity. Kamil. |
| Hosting requires login or is unavailable | Link fails in a signed-out browser | Verify actual public access; label a local/static demo as limited. Both owners. |
| Jury package violates current rules | Demo length, citations, or disclosure is incomplete | Re-check current S03/S04 before the human submits. Ewelina. |

The priority is a working, accurately described regional flow and enough time for the team to submit. Adding a risk to this table does not replace an owner-assigned task.
