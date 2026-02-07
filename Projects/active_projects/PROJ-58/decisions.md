# PROJ-56: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Eradicate Backward Compatibility Shims |
| 2026-02-06 | ShipCombatMixin: redirect callers to `ship.combat_engine.*` (not inline into Ship) | Clean sheet approach: Ship is a data/component container, not a combat actor. This completes the PROJ-12 decomposition intent. More work (7+ callers) but architecturally correct. |
| 2026-02-06 | Include `get_default_registries()` migration in scope (Phase 6) | User decision - tackles all backward compat patterns comprehensively rather than leaving the DI transitional pattern unaddressed. |
| 2026-02-06 | Collision defense fallback: investigate before removing | Non-Ship objects might exist in collision system. Verify `total_defense_score` is always present before removing fallback. |
| 2026-02-06 | Path migration target: `Paths.CONSTANT` class access | Full migration to canonical Paths class access pattern. Remove all module-level re-exports from both `constants.py` and `paths.py`. |
| 2026-02-06 | Exclude proper adapter patterns from scope | `ShipControllableAdapter`, `SimulationBattleResolver`, `DesignLoaderAdapter` are proper architectural adapters, not backward compat shims. `get_default_registry_provider()` is a valid DI mechanism. |
| 2026-02-06 | Deprecated registry global functions already removed | Research confirmed `get_component_registry()`, `get_modifier_registry()`, etc. have zero callers. PROJ-38 migration of globals is complete. Only the timeline comment remains (cleaned up in Phase 1). |
| 2026-02-06 | 6-phase approach ordered by risk | Phase 1 (zero-risk) → Phase 2 (mechanical) → Phase 3 (simple) → Phase 4 (complex) → Phase 5 (medium) → Phase 6 (complex). Allows early validation and builds confidence before risky changes. |
