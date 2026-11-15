# Delivery plan and current status

This plan separates the implemented regional MVP from work that would be needed for a broader product. Task status and ownership live in the [task index](../tasks/README.md) and individual task cards.

## Delivered regional MVP

The integrated application includes versioned Mars Jezero and lunar south-polar profiles, three real regional Earth terrain packages, three topographic criteria, weighted pixel ranking, a distinct-area mode, an explanatory result view, and an OSM map with independent visibility controls. The K-055 live browser check recorded real regional API examples and post-fix map-toggle/rerun behaviour.

The project has not completed a global Earth scan. Global search is explicitly unavailable. The interface and submission description must continue to call the current scope regional.

## Remaining technical work

- Complete scientific review of the selected profiles, regional inputs, score/tolerance sensitivity, and quality boundaries.
- Extend criteria only after establishing source comparability, units, scales, coverage, quality rules, and provenance.
- Design and verify a global dataset and processing method before claiming global coverage or global Top 10.
- Provide shared durable analysis storage before deploying the API with multiple workers.
- Complete production deployment, browser access, and public-link verification before claiming public availability.

These items are plans, not capabilities of the integrated regional MVP. P1 layers remain deferred until their data are justified and the P0 scope is complete.

## Submission readiness

The English jury description and seven-slide demo are prepared in open PR #99, awaiting its assigned factual review. The repository is private; no public project/demo URL or anonymous access check is available in the recorded evidence. A team member must confirm current event rules, publish and verify public materials, and personally submit the form. See [submission guidance](SUBMISSION.md) and the [S03 source snapshot](sources/03-submission.md).
