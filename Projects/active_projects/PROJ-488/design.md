# PROJ-488: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`
- **Bundle counts:** Audit verified: 17 (across all sibling projects) | This bundle: 1 verified, 0 uncertain, 0 INFO, 0 deferred
- **Sibling projects:** PROJ-484, PROJ-485, PROJ-486, PROJ-487, PROJ-489, PROJ-490
- **Cluster identity:** mass_earth_alias — single backward-compat alias rebinding
- **Severity breakdown:** 0 CRITICAL, 0 MAJOR, 1 MINOR

## Initial Analysis
`MASS_EARTH = EARTH_MASS  # Backward-compatible alias` at `game/strategy/data/planet_physics.py:24-25` is a literal name-rebinding. `EARTH_MASS` is imported from `game.core.constants`. The alias adds no behavior — it is a name preservation only.

### Architecture
The canonical name is `EARTH_MASS` per `game.core.constants`. All callers can use this name directly without any code change beyond import-line edits and a name-replace.

### Key Patterns to Reuse
- **Single canonical name**: the rule of one canonical symbol per concept — `EARTH_MASS` survives, `MASS_EARTH` does not.

### Dependencies & Risks
1. **Caller volume** — ~25 sites is small; a single PR with a find-and-replace across the listed files should suffice.
2. **Behavioral identity** — Since `MASS_EARTH = EARTH_MASS` is a literal reference assignment (the symbols share the same `float` object in Python's immutable-numeric pool), the behavioral guarantee is trivial.

### Opportunities Discovered
- Could combine with PROJ-490 (stale-comment cleanup) if the user wishes a single "low-risk cleanup" PR. Default bundling kept them separate.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
