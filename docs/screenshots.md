# Screenshots

No committed product screenshots exist yet.

## Implemented UI Capture Targets

- Landing page at `/`.
- Onboarding flow at `/onboarding`, including profile completeness and weight sliders.
- Search UI at `/search`, including filters, sort dropdown, active chips, result cards, pagination, local save/compare actions, compare tray, and empty/error/loading states.
- Saved schools dashboard at `/dashboard`, including grouped statuses, quick status updates, removal, and empty states.
- Comparison workspace at `/compare`, including top summary cards, responsive metrics table, category winners, deterministic tradeoff summary, and fewer-than-two-schools states.

Search result cards are backed by `GET /schools/search`. Onboarding stores preferences locally and passes supported search filters forward. Saved schools and compare selections are local browser state until authentication and backend persistence are added. Ranking reason and tradeoff copy appears only when the backend returns those fields; current profile comparison summaries are deterministic and do not use generated text.

## Planned Capture Checklist

- Landing page
- Onboarding quiz
- Search filters and result cards
- School profile with fit breakdown
- Comparison workspace
- Saved schools dashboard
- Sticky compare tray
- Semantic search after V2
- Decision report after V2
- Architecture diagram and performance chart after measurements exist

Screenshots should only be added when the underlying feature is implemented and representative of the real product state.
