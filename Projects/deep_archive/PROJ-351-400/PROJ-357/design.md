# PROJ-357: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/)
- **Type:** Technical Debt Review
- **Date:** 2026-05-04
- **Report:** [View Full Report](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md)
- **Source finding:** #2 — "Fleet aura providers are not tied to component identity" (P1)

## Initial Analysis

### Bug location
`game/simulation/combat/fleet_aura_manager.py`:
- `_scan_ship` (lines 207-227) — registers an `AuraProvider` per qualifying ability instance, keyed only by `(ship, ability_class_name, value)`. The originating component / ability identity is not stored.
- `_recalculate` (lines 308-327) — for each provider, walks the ship and asks "is there any operational component with a same-class non-self-scope ability?" If yes, treats the provider as still alive and contributes `provider.value` (the originally cached number).

### Failure mode
Ship has two same-class aura components:
- Component A: `ShieldProjection(value=10, scope=fleet)`
- Component B: `ShieldProjection(value=5, scope=fleet)`

`_scan_ship` registers two providers (one with value 10, one with value 5). Disable component A: `_recalculate`'s "any operational same-class ability" check still finds B operational, so BOTH provider entries are treated as live. The team aggregator sees [10, 5] still, even though only [5] should remain.

This is independent of the dirty-flag / fingerprint cache — `_get_provider_fingerprint` recomputes when the operational component count changes, so the recalc *runs*, but the recalc itself is the buggy part.

### Architecture
- Aura semantics centralized in `FleetAuraManager` (PROJ-253 added the cache; PROJ-269/270/271/273 layered external modifiers + ability-stat registry).
- Aggregation is delegated to `_aggregate_ability_groups` in `game/simulation/entities/ability_aggregator.py` — that contract (MAX same group / SUM across groups) must be preserved bit-for-bit.

## Key Patterns to Reuse
- **`KNOWN_EXTERNAL_STAT_KEYS` allow-listing** (`game/simulation/combat/ability_stat_registry.py`) — already wires external modifiers through the same aggregator. The provider-identity fix should preserve this routing.
- **Fingerprint cache invalidation** (`_get_provider_fingerprint`) — keep; consider extending to include per-component-id operational state if the fix needs sharper invalidation.

## Dependencies & Risks
1. **Stacking semantics** — must remain bit-identical for the single-provider case (the existing test corpus locks this). Mitigation: write characterization tests for current single-provider behavior in Phase 1 BEFORE touching production code.
2. **Provider mutation during iteration** — `_recalculate` is the only writer of `_team_bonuses`; safe.
3. **Identity object choice** — Python `id()` of the ability instance is the cheapest stable identity but goes stale across Ship re-materialization. Use the component's stable id + an instance index, or the ability instance reference + a "still in `comp.ability_instances`" check. Decide in Phase 2 based on `_scan_ship` flow.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
