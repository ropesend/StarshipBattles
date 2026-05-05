# PROJ-352 Dependency Map

## 1. Public function callers
**`collect_system_effects`, `collect_sector_effects`, `find_sector_effect`, `aggregate_value_or`:**
- `game/strategy/engine/environmental_hazard_engine.py:114` — `collect_sector_effects` for hazard damage processing.
- `game/strategy/engine/fleet_movement_engine.py:114, 123, 126` — imports `aggregate_value_or` and calls `collect_sector_effects` for strategic speed.
- `game/strategy/engine/conflict_resolution_engine.py:509` — `collect_sector_effects` for battle location resolution.
- `game/ui/panels/system_tree_panel.py:458, 490` — `collect_system_effects` for system-level UI (2 sites).
- `game/ui/panels/system_tree_panel.py:505` — `collect_sector_effects` for sector-level UI.

## 2. Legacy provider fields consumers
Fields emitted by `_legacy_provider_fields()` (lines 476-503): `planet_name`, `planet_id`, `facility_name`, `facility_id`, `component_key`.

UI consumers:
- `game/ui/panels/system_tree_panel.py:9-20` (`_legacy_provider_label` reads `facility_name`, `planet_name`).
- `game/ui/screens/planet_list_window.py` — legacy field access.
- `game/ui/screens/planet_list_sidebar.py`, `game/ui/screens/planet_list_controller.py` — pass-through.
- `game/ui/panels/planet_report_panel.py` — direct field consumption.

These are the blockers for legacy-field removal (Phase 5 of PROJ-352).

## 3. SYSTEM_EFFECT_ABILITIES external imports
None. The dict is internal to `system_effects_collector.py` (used at lines 163, 200, 323). Callers pass ability names as strings.

## 4. make_group_key / make_display_name public consumers
Per FEAT-16 docstring, public APIs:
- `game/ui/screens/planet_list_window.py:37, 77-78` — imports both.
- `game/ui/screens/planet_list_sidebar.py:160` — imports `make_display_name`.
- `game/ui/screens/planet_list_filters.py:29, 121, 145` — imports `make_group_key`.
- `tests/unit/strategy/services/test_system_effects_collector.py:685-716` — coverage.

These must continue to work after refactor (signatures stay; bodies become metadata-driven).

## 5. UI panels rendering effect rows
- `game/ui/panels/system_tree_panel.py` — system/sector effects tree (lines 452-505).
- `game/ui/screens/planet_list_window.py` — per-effect columns.
- `game/ui/screens/planet_list_sidebar.py` — effects filter sidebar.
- `game/ui/screens/planet_list_filters.py` — effect filter manager.

## 6. combat_modifier_collector
**Does NOT reuse system_effects_collector.** It imports `find_abilities_in_scope` from `strategic_ability_scanner.py:18` and implements separate aggregation via `aggregate_multipliers` (line 19). Independent owner-aware scope resolution per PROJ-272.

**Implication:** PROJ-352 should NOT try to unify combat_modifier_collector into the new metadata registry — they share data inputs but have different aggregation models. The new `EffectAbilityMetadata` registry can be consumed by both, but their iteration loops stay separate.

## Summary
6 production callers (3 engines + UI tree panel + 2 helpers); 4+ UI files consume legacy fields; `make_*` functions are actively used in planet list UI; `combat_modifier_collector` is a parallel consumer, not a duplicator.
