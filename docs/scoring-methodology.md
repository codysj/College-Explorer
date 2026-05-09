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

## Future Updates

When ranking logic is added, document default weights, formulas, missing-data behavior, tie-breaking, reason codes, and the `ranking_version` policy here.
