# Privacy And Evaluation Limitations

V2.8 analytics are designed for product feedback and ranking evaluation in a local/demo environment. They are not a production observability, consent, or data-governance system.

## Privacy-Safe Logging

Analytics events are typed and sanitized before storage.

Allowed examples:

- Event name and timestamp.
- School id for school-level actions.
- Enabled filter keys.
- Result count, rank position, fit score, confidence score, reason codes, and ranking version.
- Normalized category weights.
- Report version and decision confidence label.

Disallowed examples:

- Raw search text.
- Visit notes, unresolved concerns, parent notes, or student notes.
- Aid offers, scholarships, estimated yearly cost, or loan amounts.
- Email addresses or authentication identifiers beyond the existing demo `user_id`.
- Free-form preference narratives such as intended major text or home-state input.

## Evaluation Caveats

Ranking evaluation metrics are descriptive, not causal.

- High-fit schools being saved more often can indicate ranking alignment, but it can also reflect users already preferring those schools.
- Compare rates by rank position can be affected by the UI layout, demo scripts, and local browser state.
- Reason-code frequency can show explanation coverage, but it does not prove that users trusted or understood an explanation.
- Confidence distributions reflect available source data. Missing public-data fields can bias confidence downward.
- Prestige, selectivity, and name recognition may influence user saves or finalists independently of deterministic fit scores.

## V3 Requirements

Before production analytics, the platform needs authenticated ownership, retention windows, deletion/export controls, consent language, access control for internal dashboards, rate limiting, and audit logging.
