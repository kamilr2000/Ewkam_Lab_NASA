# Repository instructions

## Project and source of truth

Terra Analog is a Kamil/Ewelina project for the NASA Space Apps Challenge 2026. The current product is a regional terrain-comparison MVP; global Earth search is not available.

Read, in order, the root README, docs/PRODUCT.md, docs/METHODOLOGY.md, docs/CONTRACTS.md, docs/COLLABORATION.md, your work guide under prompts/, and the current task card. Organizer source snapshots are in docs/sources/.

The shared private repository is https://github.com/kamilr2000/Ewkam_Lab_NASA. The source of truth is origin/main. Do not assume access to the other person's machine or local paths. Routine synchronization, commits, and pushes are part of assigned work.

## Task reservation and delivery

Before implementing a task, publish a separate reservation commit to origin/main. Update only that task card with status in_progress, agent, date, branch, and a start entry. Use the commit title tasks(ID): IN PROGRESS. Confirm the reservation is present in origin/main before implementation. A branch-only push or open pull request does not reserve a task.

Implement on ewelina/ID-description or kamil/ID-description based on current main. On a clean main, use fast-forward-only pull. On a published task branch, pull without rebasing and merge current origin/main. Preserve unrelated work. Never force-push, reset away another person's changes, or make broad ours/theirs conflict resolutions.

After each coherent change: inspect it, run relevant checks, commit only owned files, synchronize, resolve real conflicts, and push. Report an unsuccessful push with its local commit SHA; do not describe unpublished work as delivered. Mark a task done only when its criteria and evidence are complete and the implementation is integrated into origin/main.

At the end of current work, synchronize and review the full queue. Ready reviews assigned to you take priority over other work; a review never interrupts an implementation or review already in progress. Review only the requested scope and exact published ref. Report blockers separately from cosmetic follow-ups. Do not create endless review-of-review chains.

## Ownership

| Area | Owner |
|---|---|
| pipeline/, apps/api/, data/, contracts/*.json, contracts/fixtures/ | Kamil |
| apps/web/, design/, submission/ | Ewelina |
| docs/DATA.md, docs/METHODOLOGY.md | Kamil; Ewelina may propose edits for owner review |
| docs/SUBMISSION.md | Ewelina; Kamil checks scientific claims |
| Shared docs and root files | Owner of the active integration task |
| tasks/ID.md | Owner recorded in that task |

The cross-repository inventory and language cleanup task I-014 is explicitly assigned to Ewelina and reviewed by Kamil. Do not use it to change scientific values, API behaviour, data provenance, or another owner's active implementation without review.

## Product and data invariants

1. A global Top 10 requires scoring every eligible cell in the declared grid before display aggregation. Never prune an area by its mean before checking its pixels.
2. Preserve isolated hotspots. Pixel ranking and distinct-area ranking are separate modes with explicit parameters.
3. Missing data remain null with reasons; they are not zero or a favourable score. Compare candidates on the same active criteria.
4. Keep map, ranking, and details tied to one analysis ID. Do not silently replace stale or failed Live results with synthetic fixtures.
5. Label all synthetic data visibly. Do not present them as NASADEM, Live output, or a global scan.
6. Report units, measurement scale, source, version, and quality. Do not compare absolute heights across incompatible planetary vertical references.
7. Lithology is not mineralogy. NDVI is not a measure of life on Mars.
8. OSM is a basemap, not an analysis layer. Preserve attribution and usage-policy requirements.
9. Do not invent data, licenses, precision, NASA endorsement, or submission confirmations.

## Formal submission is human-only

Only Kamil or Ewelina may submit the NASA project, make required attestations, or accept terms. Agents prepare a complete, evidence-backed package and checklist; they must not click Submit for Judging or send an equivalent API request. Task I-006 has executor human_only. An open I-006 does not block an otherwise complete agent objective.

Keep accurate, required AI/SI assistance disclosures and source/licence records. Remove incidental product or code-comment references that are not useful, but do not erase factual use records.

## Final report

Report task IDs, remote branch, pushed SHA and pull-request URL, merge state, checks actually run, evidence, limitations, unpublished commits, and the next human or cross-owner action. Never claim the application, browser, public deployment, or submission works unless that exact outcome was checked.
