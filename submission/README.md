# Terra Analog — jury package status

The English project copy and seven-slide demo are prepared from the tested local MVP evidence. They describe the implementation at E-006 PR #96, exact head `c0df63a50f196ef89793ec1345d3c5ca3636d18c`. E-006 has been handed off for acceptance; that branch is not yet integrated into `origin/main` in this package snapshot.

## Files prepared

- [`project-description.md`](project-description.md): English submission narrative, examples, source and software citations, rights notes, AI disclosure, and limitations.
- [`terra-analog-demo.pptx`](terra-analog-demo.pptx): exactly seven slides including title, within the S03 maximum. Speaker notes contain source citations and run context. The local PowerPoint file is **not** a public link.

## Confirmed evidence and limits

The tested examples are real API responses from NOAA ETOPO-derived regional packages paired with NASA MOLA and LOLA reference profiles. They are not synthetic fixtures. The description identifies each package version, regional denominator, selected measurement values, analysis ID, and distinct-area spacing. Global scope returns `SCOPE_UNAVAILABLE`; no global ranking is claimed. NASADEM is mentioned only for a separate Earth-data validation role. No NASA endorsement is claimed.

The UI/API checks were made against a local build and local API, with a same-origin proxy because the API did not provide browser CORS in that setup. There is no public deployment or anonymous public URL available as of 15 November 2026. A team member must deploy/host the demo and verify the link without signing in before submission. No public-link test has been passed.

The local S03 snapshot allows one presentation of at most seven slides, including the title slide, or a video of at most 30 seconds. This package uses only the seven-slide presentation format. The official guide page returned HTTP 502 during this preparation; its current online content was not re-verified. Confirm the event/team owner, local pitch deadline, required fields, member eligibility, and live submission rules in the team account.

## Human-only actions still required

1. Confirm the official Space Apps event/team account and registered member details.
2. Deploy the tested E-006 branch (after the team accepts/integrates it), host this deck externally, and verify both links in a signed-out browser.
3. Confirm citations, registered team facts, and disclosure statements; update the internal AI register via its owner-assigned follow-up task.
4. Enter the English content and links into the correct project form; a saved draft is not a submission.
5. Personally review the required declarations and terms, use **Submit for Judging**, and retain the success confirmation, URL, and local timestamp.

Only Kamil or Ewelina may perform the formal submission. An agent must not click the submission control, submit an equivalent API request, make attestations, or accept terms on a person’s behalf. A prepared local pack or deployment is not proof of a submitted project. See [`docs/SUBMISSION.md`](../docs/SUBMISSION.md) and the local [S03 snapshot](../docs/sources/03-submission.md).
