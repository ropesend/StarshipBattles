# PROJ-360: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/)
- **Type:** Technical Debt Review
- **Date:** 2026-05-04
- **Report:** [View Full Report](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md)
- **Source finding:** #5 — "Ship stat calculation is a monolithic special-case engine" (P2 maintainability)

## Initial Analysis

### Bug location
`game/simulation/entities/ship_stats.py` — 643 LOC (over the 500 LOC convention per AGENTS.md). `ShipStatsCalculator.calculate()` (line 111) runs many phases mutating `ship` in place and hardcodes ability-name string checks for movement, shields, regeneration, launch capacity, multiplex tracking, armor, command priority, and engine priority.

Adding a new stat or ability class requires editing this single broad file that already owns multiple unrelated concerns.

### Architecture
- The calculator is the single source of truth for derived ship stats; that's correct architecturally.
- The problem is shape, not location: the calculator should be a coordinator that delegates to per-domain contributors, not a god-method.

### Precedents to mirror
- `ABILITY_STAT_REGISTRY` (PROJ-273) — registry replaced hardcoded per-ability mappings spread across compilers.
- `_aggregate_ability_groups` — extracted aggregation as a shared function consumed by `FleetAuraManager` and stat readers.
- The decomposition pattern this project will introduce (per-domain contributors registered into a coordinator) belongs in `docs/02_PATTERNS.md` once it lands.

### Static-analysis context (from review report)
Other complexity hotspots in the same area worth knowing about (NOT in this project's scope but related):
- `combat_endurance.py::calculate_combat_endurance` D(21)
- `ability_aggregator.py::calculate_ability_totals` C(20)
- `ship_design_stats.py::calculate_design_stats` C(20)
- `Ability.get_effective_stat` C(17)

If decomposition surfaces a natural extraction point that would simplify these, surface to user as a follow-up — don't expand scope unilaterally.

## Key Patterns to Reuse
- **Registry pattern** — `ABILITY_STAT_REGISTRY` shape.
- **Two-phase aggregation** — already extracted in `_aggregate_ability_groups`.
- **Golden snapshot tests** — same testing pattern PROJ-359 will establish for weapon dispatch.

## Dependencies & Risks
1. **Mutation-order coupling** — `calculate()` runs phases that depend on each other's intermediate writes to `ship`. The decomposition must preserve order. Mitigation: golden tests first; refactor in mechanical extractions; do not reorder.
2. **PROJ-359 overlap** — some weapon/defense contributors may want to consume the typed `AttackRequest` / `AttackResolution` once it exists. PROJ-360 is scheduled AFTER PROJ-359 for that reason; revisit if PROJ-359 is delayed.
3. **`ship_design_stats.py`** — separate calculator with its own complexity. NOT in scope here; treat as a follow-up project if warranted.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
