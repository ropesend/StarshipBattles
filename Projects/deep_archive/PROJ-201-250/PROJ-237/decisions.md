# PROJ-237: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-29 | Project initialized | Starting point for Planetary Shield, Energy System & Planet Orders Framework |
| 2026-03-29 | Per-planet energy pool (not per-facility) | Simpler, more intuitive. All facilities share one planet-wide pool. Generators add, shield drains. |
| 2026-03-29 | Strategy-only shield; combat abilities are placeholders | Planets don't currently participate in combat. Full combat integration is future work. |
| 2026-03-29 | Auto-deactivate shield when energy hits zero | Simple, predictable. Player must reactivate manually once energy is restored. |
| 2026-03-29 | Timed shield activation/deactivation (ticks from JSON) | Adds strategic depth. Can span multiple turns (>100 ticks). Foundation for future planet order types. |
| 2026-03-29 | Separate PlanetOrderType enum from OrderType | Planet orders operate on different entities with different semantics. Clean type safety. |
| 2026-03-29 | Planet orders queue on Planet dataclass | Mirrors Fleet.orders pattern. Planet is the commanded entity. |
| 2026-03-29 | component_states dict on PlanetaryFacility | Flexible state tracking for any toggleable component without modifying read-only design data. |
| 2026-03-29 | Recalculate energy capacity/generation each tick | Handles mid-turn facility destruction gracefully (like HarvestingEngine.recalculate_storage()). |
| 2026-03-29 | Planets act every tick (no speed concept) | Unlike fleets, planets don't have speed. action_time directly equals number of ticks. |
| 2026-03-29 | Energy phase after fuel gen (0c1), planet actions after fleet actions (1.6) | Energy must be generated before consumed. Planet actions are strategic like fleet actions. |
