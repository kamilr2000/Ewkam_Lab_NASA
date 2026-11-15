# Ewelina work guide

You own the web application, map, interaction design, and submission materials. The current task card and AGENTS.md define the active goal and repository workflow.

## Before implementation

- Synchronize with origin/main and read the current task and dependencies.
- Publish the task's IN PROGRESS reservation on origin/main before editing.
- Work on the task's published Ewelina branch, keeping commits small and scoped.

## Product responsibilities

Connect the user interface to the versioned API contract. The API owns scoring. Keep selection of criteria and weights separate from map-layer visibility. Preserve the same analysis ID across the map, ranking, and pixel explanation. Clear stale results on a changed request and never silently replace a failed Live response with fixture data.

The current Earth scope is regional. Keep Live and synthetic modes visibly distinct. Preserve individual hotspots, explain measurement units and scale, and keep OSM attribution visible. Do not claim global coverage, satellite imagery, public deployment, or NASA endorsement without direct evidence.

Coordinate scientific wording, data versions, source claims, and API semantics with Kamil. Own the English project copy and demo, but keep them factual and within the current submission guide.

## Handoff and completion

Publish each coherent change with its checks, exact SHA, branch or pull request, and limitations. Do not mark the task done until its acceptance criteria are met and the change is integrated into origin/main. Formal submission is human-only and may be performed only by Kamil or Ewelina.
