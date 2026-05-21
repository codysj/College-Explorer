# Screenshots and Demo Assets

No committed product screenshots or GIFs exist yet. Do not add fake screenshots, mock browser frames, or generated product captures. Every asset in this folder should come from the real running app.

Recommended future folder shape:

```text
docs/assets/screenshots/
docs/assets/gifs/
```

## V1.13 Capture Checklist

| Asset | Route / source | Status | Notes |
| --- | --- | --- | --- |
| Landing page screenshot | `/` | Placeholder | Show the product framing and primary calls to action. |
| Onboarding screenshot or GIF | `/onboarding` | Placeholder | Capture preference steps, completion state, and search handoff. |
| Search screenshot | `/search` | Placeholder | Capture filters, result cards, sorting, save/compare controls, and compare tray. |
| Ranked search evidence | `POST /rankings` and future ranked UI | Placeholder | Ranking API exists; frontend search does not yet call it. Do not imply ranked cards until wired. |
| School profile screenshot | `/schools/1` | Placeholder | Capture profile sections, missing-data handling, and local actions. |
| Saved schools dashboard screenshot | `/dashboard` | Placeholder | Capture grouped statuses and local persistence behavior. |
| Compare workflow screenshot or GIF | `/compare` | Placeholder | Capture 2-5 selected schools, metric comparison, category winners, tradeoffs, and cost/value calculator. |
| Decision cost/value screenshot or GIF | `/decision` | Placeholder | Capture accepted-school offers, calculator assumptions, debt scenarios, and uncertainty warnings. |

## GIF Checklist

- Onboarding to search handoff.
- Search filters and compare tray selection.
- School profile save/compare interaction.
- Compare workspace with multiple schools.
- Cost/value calculator edits in compare or decision workflow.
- Future V2 semantic search once implemented.

## Capture Rules

- Use the real app running against seeded local data.
- Keep browser state intentional; clear unrelated localStorage before capture if needed.
- Do not crop out missing-data labels or V1 limitations.
- Do not show generated or unofficial college facts as real facts.
- Do not include real student data.

## Current Product Notes

- Search result cards are backed by `GET /schools/search`.
- Deterministic ranking is implemented through `POST /rankings`, but the frontend search route does not yet call it.
- Onboarding stores a typed preference profile in browser `localStorage`.
- Saved schools and comparison selections are browser-local until authenticated persistence is added.
- Similar-school discovery, decision reports, and cost/value calculations belong to V2.
