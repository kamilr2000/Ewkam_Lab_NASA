---
id: E-012
owner: ewelina
reviewer: kamil
priority: P0
task_type: review
queue_priority: review_first
unblocks_other_agent: true
status: todo
depends_on: []
review_of: K-006
review_ref: pending
agent: unassigned
work_branch: unassigned
updated: 2026-11-14
discovered_from: requesting-task-or-pr
---

# TASK-ID — Review a specific change and ref

This is a template. Assign the next available ID and the receiver as owner. Kamil creates E-* cards for Ewelina; Ewelina creates K-* cards for Kamil.

When choosing the next task, ready reviews come before ordinary P0/P1/P2 work, but never interrupt work already in progress. Among ready reviews, prefer those that unblock the other agent, then the oldest request. Set unblocks_other_agent only when accurate. Older review cards keep review priority even if they lack queue_priority.

Goal: inspect the requested change and publish a result with evidence.

Scope: list the files, contract, and criteria to inspect. Publish the reviewer report in handoffs/ or the PR. Fixes remain with the code owner unless a separate handoff is agreed.

## Start conditions

The implementation is in review and review_ref points to an available published SHA/PR. If it is missing, request an updated handoff; do not wait idly. Do not require the reviewed task to be done and do not put it in depends_on. review_of records the review relationship, not a completion dependency.

## Steps

1. Finish current work. Before selecting the next task, synchronize, check review readiness and priority, verify the exact ref, and publish your own IN PROGRESS reservation.
2. Check the specified criteria, integration, and relevant edge cases; do not review only the author's description.
3. Publish the exact SHA, what was inspected, results, gaps, and ACCEPT or REQUEST CHANGES.
4. For defects, create or update a specific task for the code owner. Recheck significant fixes without creating an endless chain of review requests.

## Acceptance criteria

- [ ] The report is published and names the exact reviewed version.
- [ ] Results are supported by relevant checks and reproducible evidence.
- [ ] Findings state priority, owner, and a testable correction condition.
- [ ] The author can find the report in the task card or PR.

## Progress and evidence

Record the agent, date, branch, checked SHA, pushed commit/PR, and report location. Completing a review finishes the review task; it does not automatically accept the implementation.
