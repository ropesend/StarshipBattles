# PROJ-349: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Starting point for Closeout Sprint 7 - Documentation drift and convention violations from review |
| 2026-05-04 | Sprint 7 partial scope: completed T6.2, T6.7, audit-update (in af0dbd77e) | Given context budget at session-end, focused on high-value low-risk items (broad-catch annotation, doc timestamp, concurrent-commit audit reinforcement). |
| 2026-05-04 | T6.5 declined: LLMUnexpectedError.code stays None per existing design | The class docstring at `game/core/exceptions.py:319-323` explicitly says "code is intentionally None — the wrapped exception is, by definition, outside the categorized LLM-error taxonomy. Callers that need to distinguish 'something unexpected happened' from a specific known LLM failure should use isinstance(err, LLMUnexpectedError)." Adding a taxonomy code would contradict the documented isinstance-discrimination guidance. The review's framing ("consumers branching on err.code see None") is correct as a fact but the design intent is to STEER consumers off `err.code` for this exception type. No change. |
| 2026-05-04 | T6.1, T6.3, T6.4, T6.6, T6.8 deferred to user direction | T6.1 (PlanetaryFacility legacy save compat) requires user sign-off per CLAUDE.md "old saves disposable" intent + master plan caution. T6.3 (ActionExecutionEngine DI fix) requires test-pin updates that may cascade. T6.4 (planet_abilities_controller hardcoded list → registry scan) requires choosing the right registry-scan idiom. T6.6 (strategy load dialog modal tracking) is a wider modal-management refactor. T6.8 (facade `_session` lint enforcement) is a tooling decision. All are non-trivial and the user can prioritize directly. |
| 2026-05-04 | Tier-7 polish (synthesis lines 105-122) deferred | Long list of small test-quality improvements, none Tier-1 or merge-blocking. Better tackled per-area in a focused follow-up project than rushed at session-end. |
