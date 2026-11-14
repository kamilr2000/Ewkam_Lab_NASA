# E-003 follow-up: source attribution copy

- Date: 2026-11-15
- Task branch: `ewelina/E-003-api-adapter`
- Code commit: `6ce2492467e3202a15da80e0a732e8ba7491ee92`
- PR: [#16](https://github.com/kamilr2000/Ewkam_Lab_NASA/pull/16)
- Main E-003 review reference: `5e4a82aa4c6527009adcce877ac1d6cb00928445`
- Current published branch head after synchronizing `origin/main`: `7c2e802`

Before K-019 started, a pass over the user-facing copy found a footer statement promising that NASA sources would be cited with every released analysis. That promise was unsupported and could imply a NASA-only source set. The footer now says: “Source IDs appear when provided; full citations are not linked in this prototype.” This describes the current UI and avoids a NASA endorsement or unsupported attribution claim.

The follow-up is one text line in `apps/web/src/App.tsx`; the synthetic fixture disclosure remains unchanged. After the edit, `npm run build` passed and `git diff --check` passed. The task card keeps K-019's original exact `review_ref`; the reviewer should include commit `6ce2492467e3202a15da80e0a732e8ba7491ee92` when accepting the current PR head, or request a scoped follow-up review if that commit is outside the review performed.
