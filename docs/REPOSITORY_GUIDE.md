# Repository guide and retention decisions

This guide inventories the tracked repository. Keep a file when it supports building, operating, validating, reproducing, reviewing, or submitting the project. Delete a file only after checking its owner, references, and reproducibility value.

## Top-level inventory

| Path | Keep? | Purpose and retention decision |
|---|---|---|
| .github/ | Yes | Pull-request and repository workflow templates. |
| apps/api/ | Yes | Regional analysis API and its tests. |
| apps/web/ | Yes | User-facing application, map, and UI tests. |
| contracts/ | Yes | Versioned request/response schemas, OpenAPI, fixtures, and contract tests. Synthetic fixtures are required test evidence, not substitutes for Live data. |
| data/ | Yes | Source manifests, checksums, reproducibility reports, and small derived regional packages. Raw inputs remain ignored and must not be committed. |
| design/ | Yes | Interaction-flow documentation. Label intended behaviour when it is not implemented. |
| docs/ | Yes | Product, science, data, collaboration, validation, source, and submission references. |
| handoffs/ | Yes | Durable cross-owner implementation and review evidence; retain historical records. |
| pipeline/ | Yes | Reproducible download, QA, profile, and feature-processing scripts. |
| prompts/ | Yes | Work guides for the two project tracks. Keep them consistent with AGENTS.md and collaboration rules. |
| submission/ | Yes | Current English jury copy and demo artifacts. Retire draft templates only after their replacement is integrated and references are checked. |
| tasks/ | Yes | Shared task queue and review/history records. Keep completed, cancelled, and historical cards. |
| tools/ | Yes | Repository planning and consistency checks. |
| AGENTS.md | Yes | Shared collaboration, ownership, safety, and repository workflow instructions. |
| LICENSE | Yes | Project code licence; it does not replace source-specific data licences. |
| THIRD_PARTY.md | Yes | Software, dataset, and attribution notices. |
| pyproject.toml, uv.lock | Yes | Python project metadata and reproducible dependency lock. |
| apps/web/package.json, package-lock.json | Yes | Web package metadata and reproducible dependency lock. |
| .gitignore, .gitattributes, .python-version | Yes | Generated/raw-data exclusions, consistent text handling, and Python runtime selection. |
| README.md | Yes | English project entry point and accurate scope statement. |

## Candidate cleanup decisions

- Submission template: the obsolete TODO template is removed from the I-014 branch after checking its references. The verified English description and demo remain in E-010 PR #99, awaiting factual review. The default branch may still contain the old template until these changes are integrated; do not present it as finished work.
- Historical Polish task cards and handoffs: retain them as audit evidence. Do not rewrite old review findings or timestamps as though they were authored in English. Current instructions, indexes, active task summaries, and maintained product documentation should be in English.
- Synthetic API fixtures: retain them for contract, empty-data, null, error, and isolated-hotspot regression coverage. Keep their synthetic labels and do not use them as a silent Live fallback.
- Derived regional tables: retain the small, versioned, checksummed packages served by the API. They are required runtime inputs, not disposable build output.
- Raw source downloads and intermediate rasters: keep them outside Git in ignored data directories. Their manifests and reproduction scripts remain tracked.
- Screenshots and review evidence: retain evidence referenced by a handoff or task. Check references before removing unreferenced large artifacts; this inventory does not justify broad deletion.
- AI/SI records and source attributions: retain accurate disclosures required by event guidance and repository rules. Remove incidental tool references from product copy or code comments; the repository scan found no such references in the web source or design.
- Lockfile sponsor metadata and API field names: keep them. Third-party sponsor URLs and fields such as generated_at are dependency/API metadata, not project claims or AI attribution.

## Ownership

Kamil owns the pipeline, API, source data, data documentation, and contract schemas. Ewelina owns the web app, design, and submission materials. Shared instructions, root files, and general documentation belong to the owner of the active integration task. Changes to scientific meaning, units, provenance, or API semantics require review by the relevant owner.

This is a documentation inventory, not a deletion list. Do not remove data, task history, tests, manifests, fixtures, lockfiles, or review evidence solely to reduce repository size.
