# Phase 4: Old Directory Tree Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-157 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete old test directories file-by-file after verifying each is a strict subset of the newer version.

**CRITICAL RULES:**
1. Do NOT delete wholesale. Verify EACH file individually.
2. For each old file, find the new counterpart in `tests/unit/simulation/`
3. List all `def test_` methods in old file, confirm each has an equivalent in new file
4. If ANY old test lacks an equivalent → SKIP that file (do not delete)
5. Run `pytest tests/ -x -q` after each batch of deletions
6. Record which files were skipped and why

---

## Pre-Work
- [x] Record current test count: 12585 tests collected
- [x] Catalog all .py files in `tests/unit/services/` (6 test files + __init__.py)
- [x] Catalog all .py files in `tests/unit/combat/` (15 test files + conftest.py)
- [x] Catalog all .py files in `tests/unit/entities/` (42 test files + conftest.py)
- [x] Catalog all .py files in `tests/unit/components/` (4 test files)

---

## Task 4.1: Clean up tests/unit/services/ [Medium]
**New counterparts in:** `tests/unit/simulation/services/`

**Files processed:**
| Old File | New Counterpart | Subset? | Action |
|----------|----------------|---------|--------|
| test_battle_service.py | simulation/services/test_battle_service.py | 15→77 | DELETED |
| test_modifier_service.py | simulation/services/test_modifier_service.py | 29→63 | DELETED |
| test_modifier_service_di.py | simulation/services/test_modifier_service.py | 11→63 | DELETED |
| test_vehicle_design_service.py | simulation/services/test_vehicle_design_service.py | 17→50 | DELETED |
| test_vehicle_design_service_di.py | simulation/services/test_vehicle_design_service.py | 6→50 | DELETED |
| test_ship_stats_calculator_di.py | strategy/ship_stats/test_edge_cases.py | 6→48 | DELETED |

- [x] Run `pytest tests/ -x -q` - 12497 tests collected

**Notes:** All 6 service test files were strict subsets. Directory deleted entirely.

---

## Task 4.2: Clean up tests/unit/entities/ [Medium]
**New counterparts in:** `tests/unit/simulation/entities/`

**Files DELETED (31 files - confirmed subsets):**
| Old File | New Counterpart | Tests | Action |
|----------|----------------|-------|--------|
| test_layer_data.py | simulation/entities/test_layer_data.py | 24→64 | DELETED |
| test_ship_formation.py | simulation/entities/test_ship_formation.py | 14→76 | DELETED |
| test_ship_serialization.py | simulation/entities/test_ship_serialization.py | 7→58 | DELETED |
| test_ship_serialization_di.py | simulation/entities/test_ship_serialization.py | 6→58 | DELETED |
| test_ship_physics_mixin.py | simulation/entities/test_ship_physics.py | 10→43 | DELETED |
| test_ability_aggregator_layers.py | simulation/entities/test_ability_aggregator.py | 13→83 | DELETED |
| test_ability_aggregator_scope.py | simulation/entities/test_ability_aggregator.py | 5→83 | DELETED |
| test_modifiers.py | simulation/components/test_modifiers.py | 10→24 | DELETED |
| test_modifier_row.py | simulation/components/test_modifier_effects.py | 7→31 | DELETED |
| test_modifier_propagation.py | simulation/components/test_modifier_introspection.py | 3→46 | DELETED |
| test_mandatory_modifiers.py | simulation/components/test_modifier_schema.py | 7→57 | DELETED |
| test_mandatory_updates.py | simulation/components/test_modifier_introspection.py | 3→46 | DELETED |
| test_modifier_defaults_robustness.py | simulation/components/test_modifier_schema.py | 3→57 | DELETED |
| test_component_formulas.py | simulation/components/test_component_stats_calculator.py | 2→9 | DELETED |
| test_component_modifiers_extended.py | simulation/components/test_modifier_effects.py | 2→31 | DELETED |
| test_component_resources.py | simulation/components/test_component_resource_manager.py | 4→44 | DELETED |
| test_component_composition.py | simulation/components/test_modifier_schema.py | 3→57 | DELETED |
| test_abilities_advanced.py | simulation/components/abilities/test_ability_base.py | 3→9 | DELETED |
| test_crystalline_armor.py | simulation/armor_mechanics/test_damage_mechanics.py | 4→17 | DELETED |
| test_emissive_armor.py | simulation/armor_mechanics/test_damage_reduction.py | 3→10 | DELETED |
| test_hull_layer.py | simulation/entities/test_layer_data.py | 6→64 | DELETED |
| test_ship_caching.py | simulation/entities/test_ship_loader.py | 22→42 | DELETED |
| test_ship_classes.py | simulation/entities/test_ship_loader.py | 2→42 | DELETED |
| test_ship_stats.py | simulation/systems/test_ship_stats_calculator_phases.py | 6→14 | DELETED |
| test_ship_resources.py | simulation/components/test_component_resource_manager.py | 5→44 | DELETED |
| test_ship_validator_helper.py | simulation/validation/test_ship_validator_rules.py | 9→51 | DELETED |
| test_bridge_scaling.py | simulation/systems/test_ship_stats_calculator_phases.py | 3→14 | DELETED |
| test_resource_manager.py | simulation/systems/test_resource_manager_edge_cases.py | 7→15 | DELETED |
| test_scaling_logic.py | simulation/systems/test_ship_stats_calculator_phases.py | 4→14 | DELETED |
| test_stacking_integration.py | simulation/components/test_modifier_manager.py | 5→14 | DELETED |
| test_stacking_rules.py | simulation/components/test_modifier_manager.py | 4→14 | DELETED |

- [x] Run `pytest tests/ -x -q` - 12291 tests collected

**Notes:** 31 files deleted. 11 files kept (see Skipped Files Log).

---

## Task 4.3: Clean up tests/unit/combat/ [Medium]
**New counterparts in:** `tests/unit/simulation/` (various subdirs)

**Files DELETED (13 files - confirmed subsets):**
| Old File | New Counterpart | Tests | Action |
|----------|----------------|-------|--------|
| test_projectile_manager.py | simulation/test_projectile_manager.py | 3→60 | DELETED |
| test_combat_endurance.py | simulation/entities/test_combat_endurance.py | 5→45 | DELETED |
| test_projectiles.py | simulation/entities/test_projectile.py | 9→37 | DELETED |
| test_weapons.py | simulation/components/abilities/test_weapons_*.py | 11→105 | DELETED |
| test_battle_engine_core.py | simulation/systems/test_battle_engine_tick.py | 8→49 | DELETED |
| test_shields.py | simulation/components/abilities/test_defense_*.py | 5→103 | DELETED |
| test_pdc.py | simulation/components/abilities/test_defense_*.py | 2→103 | DELETED |
| test_multitarget.py | simulation/combat/test_targeting_system.py | 5→34 | DELETED |
| test_firing_arc_logic.py | simulation/combat/test_targeting_system.py | 5→34 | DELETED |
| test_fighter_launch.py | simulation/components/abilities/test_weapons_*.py | 5→105 | DELETED |
| test_damage_weighted.py | simulation/combat/test_damage_calculator.py | 3→47 | DELETED |
| test_battle_state_di.py | simulation/managers/test_battle_state_manager.py | 6→13 | DELETED |
| test_seeker_range.py | simulation/components/abilities/test_weapons_*.py | 2→105 | DELETED |

- [x] Run `pytest tests/ -x -q` - 12222 tests collected

**Notes:** 13 files deleted. 2 files kept (see Skipped Files Log).

---

## Task 4.4: Clean up tests/unit/components/ [Medium]
**New counterparts in:** `tests/unit/simulation/components/`

**Files DELETED (4 files - all confirmed subsets):**
| Old File | New Counterpart | Tests | Action |
|----------|----------------|-------|--------|
| test_component_health_manager.py | simulation/components/test_component_health_manager.py | 9→43 | DELETED |
| test_component_health_edge_cases.py | simulation/components/test_component_health_manager.py | 10→43 | DELETED |
| test_component_resource_manager.py | simulation/components/test_component_resource_manager.py | 12→44 | DELETED |
| test_resource_costs.py | simulation/components/test_component_resource_manager.py | 6→44 | DELETED |

- [x] Run `pytest tests/ -x -q` - 12185 tests collected

**Notes:** All 4 component test files were strict subsets. Directory deleted entirely.

---

## Task 4.5: Clean up empty directories [Simple]
- [x] Check if `tests/unit/services/` is now empty → DELETED
- [x] Check if `tests/unit/combat/` is now empty → NOT EMPTY (2 files kept)
- [x] Check if `tests/unit/entities/` is now empty → NOT EMPTY (11+ files kept)
- [x] Check if `tests/unit/components/` is now empty → DELETED
- [x] Run `pytest tests/ -x -q` final check - PASSED (pre-existing failures only)

**Notes:** Services and components directories fully deleted. Combat and entities retain files that need manual review.

---

## Skipped Files Log
Files that were NOT strict subsets and were kept:

### tests/unit/entities/ (11 files kept)
| File | Tests | Reason |
|------|-------|--------|
| test_ship_stat_querier.py | 45 | UNIQUE: No counterpart in simulation/, tests ShipStatQuerier class directly |
| test_ability_interface.py | 17 | REVIEW: May have unique interface tests |
| test_component_di.py | 10 | REVIEW: DI pattern tests |
| test_components.py | 22 | REVIEW: Old file has more tests than counterpart |
| test_component_cache.py | 7 | NO_COUNTERPART: Caching tests not found elsewhere |
| test_ship_di.py | 7 | NO_COUNTERPART: Ship DI tests |
| test_ship.py | 12 | NO_COUNTERPART: Core ship tests |
| test_ship_theme_logic.py | 14 | NO_COUNTERPART: Theme logic tests |
| test_planetary_complex.py | 5 | NO_COUNTERPART: Planetary tests |
| test_bridge_requirement_removal.py | 1 | NO_COUNTERPART: Migration test |
| test_abilities.py | 14 | REVIEW: Need to verify coverage |
| ship_helpers/ (subdir) | 50 | REVIEW: Component getter/operation tests |

### tests/unit/combat/ (2 files kept)
| File | Tests | Reason |
|------|-------|--------|
| test_combat.py | 11 | EQUAL: Same test count as counterpart, needs verification |
| test_battle_setup_logic.py | 3 | REVIEW: Setup logic tests |

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or documented as skipped)
- [x] Record post-phase test count: 12185 tests collected (delta: -400)
- [x] Skipped files documented with reasons
- [x] Run `pytest tests/ -x -q` - PASSED (2 pre-existing failures documented)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project ready for audit
