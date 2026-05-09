# Scoring Methodology

The ranking engine is not implemented yet. This document defines the guardrails for V1.9.

## Principles

- Rankings must be deterministic, testable, and reproducible for the same data, preferences, and ranking version.
- LLM output must not determine scores, rank order, category scores, confidence, reason codes, or tradeoffs.
- Missing data should lower confidence or be shown as unknown; it should not be silently treated as zero.
- Score explanations should be generated from structured reason codes and known data.

## Planned V1 Categories

- Academic fit
- Cost fit
- Career fit
- Location fit
- Campus fit
- Admissions realism

## V1.8 Preference Inputs

The frontend onboarding profile now captures user weights for the planned scoring categories above. These weights are stored locally as decimal values from `0.05` to `0.4` per category and are not yet applied to school scores.

The profile also captures intended major, academic interests, affordability constraints, aid importance, career priorities, location preferences, campus preferences, and admissions strategy. V1.9 must define how these inputs become deterministic category scores, reason codes, tradeoffs, confidence, and `ranking_version`.

## Future Updates

When ranking logic is added, document default weights, formulas, missing-data behavior, tie-breaking, reason codes, and the `ranking_version` policy here.
