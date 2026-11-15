# Kamil work guide

You own the data pipeline, reference profiles, regional and future global processing, scoring API, source evidence, and API schemas. The current task card and AGENTS.md define the active goal and repository workflow.

## Before implementation

- Synchronize with origin/main and read the current task, dependencies, and data contracts.
- Publish the task's IN PROGRESS reservation on origin/main before editing.
- Work on the task's published Kamil branch, keeping commits small and scoped.

## Data and analysis responsibilities

Keep source products, units, versions, licences, grid and feature scales, masks, QA, and coverage explicit. Preserve missing values as null with reasons. Score every eligible cell within the declared scope before map aggregation. Do not discard isolated hotspots or imply a regional result is global. Keep planetary elevation references separate unless a documented transformation makes them comparable.

The API is the single scoring authority. Search, map, and pixel detail must remain tied to the same analysis ID. Synthetic fixtures are useful for tests but must be labelled and must never become a silent fallback for Live failures.

## Handoff and completion

Publish manifests, reproducible commands, exact evidence, checks, and limitations. Coordinate API changes with Ewelina through the versioned contract and reviewable handoffs. Do not mark work done until criteria are met and the change is integrated into origin/main.

Formal NASA Space Apps submission and required attestations are human-only and must be completed personally by Kamil or Ewelina.
