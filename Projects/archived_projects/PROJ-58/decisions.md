# PROJ-58: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Eradicate Backward Compatibility Shims |
| 2026-02-06 | ShipCombatMixin: redirect callers to `ship.combat_engine.*` (not inline into Ship) | Clean sheet approach: Ship is a data/component container, not a combat actor. Completes PROJ-12 decomposition intent. More work but architecturally correct. |
| 2026-02-06 | Include `get_default_registries()` migration in scope (Phase 7) | User decision - tackles all backward compat patterns comprehensively. |
| 2026-02-06 | Collision defense fallback: investigate before removing | Non-Ship objects might exist in collision system. Verify `total_defense_score` is always present. |
| 2026-02-06 | Path migration target: `Paths.CONSTANT` class access | Full migration to canonical Paths class, remove all module-level re-exports from `constants.py` and `paths.py`. |
| 2026-02-06 | Exclude proper adapter patterns from scope | `ShipControllableAdapter`, `SimulationBattleResolver`, `DesignLoaderAdapter`, `get_default_registry_provider()` are proper patterns, not shims. |
| 2026-02-06 | 7-phase approach ordered by risk | Phase 1 (zero-risk) → Phase 2 (mechanical imports) → Phase 3 (LayerType imports) → Phase 4 (formation) → Phase 5 (combat mixin) → Phase 6 (battle controller) → Phase 7 (registry DI). |
| 2026-02-06 | Workshop proxy properties have 11 INTERNAL usages | Swarm corrected earlier belief that they had 0 callers. `self.ship`, `self.selected_components`, `self.available_components` are used within workshop_screen.py itself. Must update to `self.viewmodel.*`. |
| 2026-02-06 | Formation delegation has 170+ test callers | Much larger scope than initially estimated. 10 production callers in 2 files + 6 adapter methods + 155+ test usages across 20+ test files. All mechanical replacements. |
| 2026-02-06 | `apply_results_to_fleets()` legacy fallback is BLOCKED | The mode handler's `apply_results()` is incomplete (blocked by PROJ-41). Cannot eradicate this fallback until PROJ-41 completes. Explicitly out of scope. |
| 2026-02-06 | Battle engine legacy controller creation path kept for now | `battle_engine.py` lines 268-272 create controllers internally when not provided. Used by tests and simple scenarios. Removing requires broader refactor of test infrastructure. |
| 2026-02-06 | `_find_pdc_target()` and `_calculate_firing_solution()` are dead code | Zero callers found in entire codebase. Can be deleted with the mixin. |
