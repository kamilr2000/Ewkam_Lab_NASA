# Collaboration and Git workflow

Kamil and Ewelina work in separate clones and exchange work through the shared private repository. The remote main branch is the source of truth.

## Before starting a task

1. Synchronize the local clone with origin/main without discarding uncommitted work.
2. Read the task card, dependencies, owner, exact review references, and start conditions.
3. Publish a separate IN PROGRESS reservation commit on main. Update the task status, agent, date, branch, and progress note. Confirm that commit is visible on origin/main.
4. Create the task branch from the current main and publish it.

Do not reserve a task owned or actively held by the other person. Creating a card or pushing a feature branch does not reserve it.

## Working and synchronizing

Use small, reviewable commits. After each coherent change, run the relevant checks, commit only the files in scope, synchronize with the latest main, resolve actual conflicts while preserving both changes, and push. Do not force-push or use a reset that discards another person's work.

On main, pull with fast-forward only. On a published work branch, pull without rebasing, then merge current origin/main. A fetch alone does not update the working tree. If an existing change is unrelated, preserve it and exclude it from the commit.

If a push fails, fetch again, integrate both changes, review the result, and retry a normal push. Report any local commit that cannot be published; do not call it handed off.

## Queue and review

Finish work already in progress before choosing the next task. Then synchronize and choose a ready review assigned to you, followed by other ready P0 work and then P1/P2. A review request must identify the exact published ref and satisfy its start conditions. A review does not wait for the implementation card to reach done if its reviewed version is already ready. Do not review an unpublished or unavailable ref.

Review only the requested and changed scope. Block on wrong dataset/scope, silent fixture fallback, incorrect null handling, lost hotspot, broken primary flow, or misleading units. Record cosmetic suggestions as follow-ups. Publish review evidence; a chat message alone is not a review record. Significant fixes need review of the corrected scope.

## Task ownership and handoffs

Kamil owns data, pipeline, API, scientific methods, and contract schemas. Ewelina owns the web app, map, design, and submission package. Shared documentation belongs to the active integration-task owner. For work across ownership boundaries, use an explicit task or handoff and require the relevant owner's review. Do not build a second scoring engine in the browser.

New cards use tasks/TEMPLATE.md. A review card uses tasks/REVIEW_TEMPLATE.md and records review_of, review_ref, and exact start conditions. Do not make a review depend on the reviewed card being done when that would create a deadlock.

## Submission

Only Kamil or Ewelina may complete the formal NASA Space Apps submission. Agents may prepare and verify the package but must not submit it or make attestations. See docs/SUBMISSION.md and task I-006.
