# Agent Instructions

These instructions apply to Codex and other LLM coding agents working in this repository.

## Coding Standards

- Read `README.md`, `tasks.md`, `docs/architecture.md`, and the docs relevant to the current task before editing.
- Keep each implementation step small and aligned with the V1/V2/V3 roadmap.
- Prefer typed contracts and explicit validation over ad hoc objects.
- Keep SQL out of route handlers when backend code is added; use repository or service modules.
- Use parameterized SQL only. Never concatenate user input into SQL.
- Treat missing data as unknown, not as zero, unless zero is semantically correct.
- Keep application logic deterministic where user decisions depend on ranking, sorting, filtering, or scoring.

## Validation Commands

Real commands will be added as the apps are implemented. Expected future commands:

```powershell
cd apps/web; pnpm lint; pnpm build
cd apps/api; pytest
pnpm exec playwright test
```

Until those runtimes exist, validate foundation changes with:

```powershell
Get-ChildItem -Recurse -File
```

## Documentation Update Rules

- Update `tasks.md` whenever a roadmap item changes status.
- Update `docs/api-contract.md` in the same change as any endpoint contract.
- Update `docs/data-dictionary.md` in the same change as schema, seed, or data-source changes.
- Update `docs/scoring-methodology.md` in the same change as ranking or explanation logic.
- Update `docs/deployment.md` when infrastructure, environment variables, or deployment steps change.
- Do not claim measured performance, users, uptime, or deployment status unless those facts have been verified.

## LLM Guardrails

- Do not build V2 or V3 features before the required V1 foundation is stable.
- Do not invent college facts, data-source freshness, performance numbers, users, or deployment status.
- Do not present the product as admissions advice, guaranteed ROI, or financial advice.
- Do not store sensitive student details without clear product boundaries and privacy documentation.
- Prefer fixtures, seed data, tests, and typed schemas over mock-only demos.

## Ranking and Generated Text

Keep deterministic ranking separate from LLM-generated text.

- Ranking scores, sort order, category scores, confidence, reason codes, and tradeoffs must come from deterministic code and structured data.
- LLM-generated text may later summarize known deterministic outputs, but it must not create school facts, change scores, decide rankings, or hide missing data.
- Every ranking logic change must update the scoring methodology docs and use a versioned ranking constant once the ranking engine exists.
