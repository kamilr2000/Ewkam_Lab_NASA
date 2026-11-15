# Shared task index

Each task has its own Markdown card containing its owner, status, dependencies, scope, acceptance criteria, and evidence. **The card is the source of truth for status.** This index is for navigation and does not duplicate current status values.

Priority: P0 is required for the agreed MVP or submission; P1 is an extension after P0; P2 is further development. Read [collaboration rules](../docs/COLLABORATION.md) and the relevant task template before creating work.

## Shared workflow

The shared repository is [kamilr2000/Ewkam_Lab_NASA](https://github.com/kamilr2000/Ewkam_Lab_NASA). Before implementing a task, synchronize with origin/main and publish a separate IN PROGRESS reservation commit to main. Work on the task branch, synchronize and push each coherent change, and mark work done only after its acceptance evidence is complete and the implementation is integrated into origin/main.

Finish current work before choosing a next task. After synchronization, choose a ready review assigned to you first, then other ready P0, followed by P1/P2. Do not wait on an unavailable review ref. Formal submission is human-only.

## Kamil — data, pipeline, API, and contracts

Early implementation cards: [K-001](K-001.md) · [K-002](K-002.md) · [K-003](K-003.md) · [K-004](K-004.md) · [K-005](K-005.md) · [K-006](K-006.md) · [K-007](K-007.md) · [K-008](K-008.md) · [K-009](K-009.md) · [K-010](K-010.md) · [K-011](K-011.md)

Reviews, validation, and integration cards: [K-012](K-012.md) · [K-013](K-013.md) · [K-014](K-014.md) · [K-015](K-015.md) · [K-016](K-016.md) · [K-017](K-017.md) · [K-018](K-018.md) · [K-019](K-019.md) · [K-020](K-020.md) · [K-021](K-021.md) · [K-022](K-022.md) · [K-023](K-023.md) · [K-024](K-024.md) · [K-025](K-025.md) · [K-026](K-026.md) · [K-027](K-027.md) · [K-028](K-028.md) · [K-029](K-029.md) · [K-030](K-030.md) · [K-031](K-031.md) · [K-032](K-032.md) · [K-033](K-033.md) · [K-034](K-034.md) · [K-035](K-035.md) · [K-036](K-036.md) · [K-037](K-037.md) · [K-038](K-038.md) · [K-039](K-039.md) · [K-040](K-040.md) · [K-041](K-041.md) · [K-042](K-042.md) · [K-043](K-043.md) · [K-044](K-044.md) · [K-045](K-045.md) · [K-046](K-046.md) · [K-047](K-047.md) · [K-048](K-048.md) · [K-049](K-049.md) · [K-050](K-050.md) · [K-051](K-051.md) · [K-052](K-052.md) · [K-053](K-053.md) · [K-054](K-054.md) · [K-055](K-055.md)

## Ewelina — web app, map, design, and submission

Product foundation: [E-001](E-001.md) · [E-002](E-002.md) · [E-003](E-003.md) · [E-004](E-004.md) · [E-005](E-005.md) · [E-006](E-006.md) · [E-007](E-007.md) · [E-008](E-008.md) · [E-009](E-009.md) · [E-010](E-010.md) · [E-011](E-011.md)

Reviews and later implementation cards: [E-012](E-012.md) · [E-013](E-013.md) · [E-014](E-014.md) · [E-015](E-015.md) · [E-016](E-016.md) · [E-017](E-017.md) · [E-018](E-018.md) · [E-019](E-019.md) · [E-020](E-020.md) · [E-021](E-021.md) · [E-022](E-022.md) · [E-023](E-023.md) · [E-024](E-024.md) · [E-025](E-025.md) · [E-026](E-026.md) · [E-027](E-027.md) · [E-028](E-028.md) · [E-029](E-029.md) · [E-030](E-030.md) · [E-031](E-031.md) · [E-032](E-032.md) · [E-033](E-033.md) · [E-034](E-034.md) · [E-035](E-035.md) · [E-036](E-036.md)

## Integration and repository-wide work

[I-001](I-001.md) · [I-002](I-002.md) · [I-003](I-003.md) · [I-004](I-004.md) · [I-005](I-005.md) · [I-006](I-006.md) · [I-007](I-007.md) · [I-008](I-008.md) · [I-009](I-009.md) · [I-010](I-010.md) · [I-011](I-011.md) · [I-012](I-012.md) · [I-013](I-013.md) · [I-014](I-014.md)

Current focus: E-035 is complete after the post-fix K-055 browser check. E-036 is cancelled as a duplicate; its fix is in E-035. E-010's English jury package remains in open PR #99 pending its assigned factual review. I-014 is the active repository inventory and English-documentation cleanup.

The next available IDs are K-056, E-037, and I-015. Check the repository before assigning any number because both owners work in parallel.

## Templates and checks

Use [TEMPLATE.md](TEMPLATE.md) for implementation tasks and [REVIEW_TEMPLATE.md](REVIEW_TEMPLATE.md) for reviews. From the repository root, `python tools/check_planning.py` checks local Markdown links, JSON, task metadata, dependencies, cycles, and synthetic fixture expectations.
