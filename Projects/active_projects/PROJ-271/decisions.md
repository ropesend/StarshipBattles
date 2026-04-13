# PROJ-271: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

## Locked Architectural Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-12 | Project initialized as Track B successor to PROJ-270 Phase 6 | Deferred per [PROJ-270 decisions.md Decision 1](../PROJ-270/decisions.md) — Track A (multipliers) landed in PROJ-270; Track B (additive + opponent-routed) requires new stat_key + routing infrastructure that would have blown out PROJ-270's scope budget. |
| 2026-04-12 | **Scope: `flat_shield_bonus` + suppressor effects only.** Any other modifier-types surfaced by future audit belong in a successor project, not here. | Time-box the effort; closure criterion is "placeholder stat_key absent from compiler for these two sources". |
| 2026-04-12 | **Precedent for additive stat_key binding:** follow the shape of `ACCURACY_ADD` (existing in `StatKey` enum). Copy the pattern — same `operation=ADD`, same `AbilityStatBinding` wiring shape — to minimize novel architecture. | Reuse proven patterns from the existing accuracy additive system; don't invent new binding mechanics. |
| 2026-04-12 | **Suppressor routing mechanism:** `ModifierStack.per_team[opponent_id]` — same structure used by Track A's team-scoped modifiers, just targeting the opposing team_id. Spec compiler computes which team_id is "opponent" at spec-compile time (not engine runtime). | Keep the simulation layer dumb — routing decisions happen in the compiler where team-identity is known; `FleetAuraManager` just applies whatever arrived in its per_team buckets. |
| 2026-04-12 | **Combat Lab scope: none.** Combat Lab doesn't currently express these modifiers (scenarios are per-weapon math, not per-fleet/per-planet). If Combat Lab wants the new modifier types later, it's a separate request. | Combat Lab tests use per-scenario `ModifierStack.empty()` or build-time modifier entries — they bypass the planet-driven compiler path that needs wiring. |

## Future Decisions

(Record new decisions below as they are made during implementation.)

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |
