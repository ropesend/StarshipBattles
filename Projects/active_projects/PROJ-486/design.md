# PROJ-486: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`
- **Bundle counts:** Audit verified: 17 (across all sibling projects) | This bundle: 1 verified, 0 uncertain, 0 INFO, 0 deferred
- **Sibling projects:** PROJ-484, PROJ-485, PROJ-487, PROJ-488, PROJ-489, PROJ-490
- **Cluster identity:** battle_load_state — single dead method removal
- **Severity breakdown:** 0 CRITICAL, 1 MAJOR, 0 MINOR

## Initial Analysis
`BattleController.load_state` at `game/simulation/battle_controller.py:612-698` is ~87 LOC of dead code. The audit's verifier confirmed 0 production callers; the inline note at line 613 ("`load_state` has zero production callers (grep-verified)") corroborates. Independent re-verification by this skill confirmed 0 production callers BUT discovered 4 test callers the audit's verifier missed:

- `tests/unit/simulation/battle_controller/test_state.py:90`
- `tests/unit/simulation/battle_controller/test_state.py:128`
- `tests/unit/simulation/battle_controller/test_state.py:245`
- `tests/unit/simulation/battle_controller/test_state.py:268`

### Architecture
The method exists as the inverse of `save_state` for symmetry. If `save_state` is the canonical serialization output for replay capture or external diagnostics, that contract should be preserved on `save_state`'s docstring (and tested by exercising `save_state` directly, not by round-tripping through `load_state`).

### Key Patterns to Reuse
- **Save/restore symmetry without dead code**: if a test wants to verify "this state can be re-emitted identically after a serialization round-trip," it can do so without `load_state` by constructing a fresh `BattleController` and asserting on `save_state`'s output keys/shape.

### Dependencies & Risks
1. **Test rewrites** — 4 test callers may need substantive rewrites if they currently rely on `load_state` to assert restore semantics. If a test cannot be cleanly migrated to a `save_state`-only assertion, retire it (record the rationale in the phase checklist Notes).
2. **`save_state` survival** — Out of scope for this project. If `save_state` itself turns out to be dead, log a new discovered-issue via `/claude-di-log` and surface it separately.

### Opportunities Discovered
- ~87 LOC dead-code deletion in a single method.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
