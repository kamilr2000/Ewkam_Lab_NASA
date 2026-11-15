# Validation plan and evidence

Validation is scoped to the exact code, data version, and request that were checked. A unit test does not establish scientific validity, global coverage, browser rendering, deployment, or submission readiness.

## API and data checks

- Validate request and response payloads against the versioned schemas; exercise semantic errors and query-echo mismatches.
- Reproduce source downloads from pinned manifests and verify checksums, versions, units, grid definitions, QA, and provenance.
- Exercise one-feature and multi-feature requests, changed weights, deterministic ties, missing/null values, empty results, and unavailable dataset/scope errors.
- Compare the API Top K with an independent full sort on a bounded check set.
- Preserve isolated hotspots and adjacent winning pixels. Verify map maxima identify an actual pixel and do not combine maxima from different pixels.
- Check regional boundaries, masks, invalid support, and exact analysis-ID consistency across search, map, and details.
- Report regional coverage honestly. Global claims require a completed global dataset and documented coverage/QA evidence.

## Web checks

- Exercise both bodies, all available criteria, changed weights, and a fresh analysis after edits.
- Confirm stale requests cannot replace the latest result and no Live error silently falls back to fixtures.
- Check ranking, pixel selection, details, map, and explanation against the same analysis ID.
- Toggle basemap, cells, and markers independently. Confirm marker visibility survives pixel selection and reruns.
- Inspect visible OSM attribution and behaviour when map tiles are unavailable.
- Check keyboard navigation, focus, labels, contrast, small viewports, and selected-result visibility.

## Demo and submission checks

Use only evidence from an exact, reviewed code/data ref. Distinguish local tests from browser tests and local demos from public deployments. Review every public feature, data, NASA, licence, AI/SI, and result statement against its source. A public URL requires a signed-out access check. The formal submission and attestations are human-only.
