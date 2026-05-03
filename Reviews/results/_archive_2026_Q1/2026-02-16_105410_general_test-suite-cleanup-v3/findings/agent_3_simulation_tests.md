# Agent 3: Simulation Tests Analysis

## Summary
- **Files analyzed:** 77 test files + 5 utility files + 7 log files + 12 JSON configs
- **Removal candidates found:** 12 items (including scaffold groups)
- **HIGH confidence:** 5 items (old framework scaffold + 1 trivial test)
- **MEDIUM confidence:** 5 items (scaffold utilities + inline math tests + potential duplicates)
- **LOW confidence:** 3 items (borderline trivial tests, stale filename)

### Lines Removable (Estimated)
- HIGH confidence: ~1,152 lines of code + ~19 data files (logs + configs)
- MEDIUM confidence: ~1,508 lines of code
- LOW confidence: ~256 lines of code (but recommend rename, not removal)
- **Total HIGH+MEDIUM removable: ~2,660 lines + 19 data files**

---

## HIGH Confidence Removal Candidates

### 1. Old Component Test Framework (Scaffold Group)
These 5 files form a cohesive old testing framework that has been **superseded by `simulation_tests/` scenarios and pytest**. They are not pytest test files. They should all be removed together.

#### run_component_tests.py (~506 lines)
- **Location:** `tests/unit/simulation/run_component_tests.py`
- **Assessment:** Custom test runner that loads JSON configs, runs simulations, and parses logs. Uses pygame directly. Not discovered by pytest.
- **Confidence:** HIGH

#### update_test_ships.py (~58 lines)
- **Location:** `tests/unit/simulation/update_test_ships.py`
- **Assessment:** Development utility script to update test ship JSON files with recalculated stats. Uses pygame directly. Not a test.
- **Confidence:** HIGH

#### output/logs/ directory (7 .log files)
- **Location:** `tests/unit/simulation/output/logs/`
- **Assessment:** Generated log output files from the old component test runner.
- **Confidence:** HIGH

#### test_configs/ directory (12 .json files)
- **Location:** `tests/unit/simulation/test_configs/`
- **Assessment:** JSON configuration files for the old component test runner.
- **Confidence:** HIGH

### 2. Trivially Obvious Test File

#### test_ship_stats_phase_ordering.py (22 lines)
- **Location:** `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py`
- **Assessment:** Only 2 tests: one checks a class can be imported (`assert ShipStatsCalculator is not None`), and one checks `hasattr(ShipStatsCalculator, 'calculate')`. These are trivially obvious import/existence checks that provide no regression value. The actual phase ordering is tested by `test_ship_stats_calculator_phases.py` (375 lines) in the same directory.
- **Confidence:** HIGH

---

## MEDIUM Confidence Removal Candidates

### 3. Old Framework Utilities (Remove with Scaffold Group)

#### component_logger.py (~279 lines)
- **Location:** `tests/unit/simulation/component_logger.py`
- **Assessment:** Test logging infrastructure with `TEST_LOGGING_ENABLED = False` by default. Used only by `run_component_tests.py`. Part of the superseded component testing framework.
- **Confidence:** MEDIUM (remove with scaffold group)

#### component_sim_tools.py (~157 lines)
- **Location:** `tests/unit/simulation/component_sim_tools.py`
- **Assessment:** Helper to create test ship JSON files for the older component testing framework.
- **Confidence:** MEDIUM (remove with scaffold group)

#### log_parser.py (~361 lines)
- **Location:** `tests/unit/simulation/log_parser.py`
- **Assessment:** Parses log files from component_logger. Only used by run_component_tests.py.
- **Confidence:** MEDIUM (remove with scaffold group)

### 4. Inline Math Formula Tests

#### test_physics_formulas.py (~731 lines)
- **Location:** `tests/unit/simulation/test_physics_formulas.py`
- **Assessment:** Tests physics formula boundary conditions (zero mass, overflow, NaN, etc.). However, **these tests don't test actual game code paths** -- they test raw mathematical expressions inline (e.g. `max_speed = (thrust * K_SPEED) / mass`). The actual game physics is in `ship_stats.py` and `ship_physics.py`, which have their own tests in `test_ship_physics.py` (585 lines) and `test_ship_stats_calculator_phases.py` (375 lines). These are essentially math sanity tests disconnected from the real implementation.
- **Confidence:** MEDIUM

### 5. Potential Duplicated Test Coverage (Post-PROJ-118 Extraction)

#### ship_combat_engine/ vs combat/ duplication
- **Files involved:**
  - `ship_combat_engine/test_creation_and_lead.py` (100 lines) - Tests `ShipCombatEngine.solve_lead()`
  - `ship_combat_engine/test_targeting.py` (152 lines) - Tests `ShipCombatEngine.select_target()` and `calculate_firing_solution()`
  - `combat/test_targeting_system.py` (913 lines) - Tests `TargetingSystem.solve_lead()`, `select_target()`, `calculate_firing_solution()`
- **Assessment:** The `combat/` directory contains the extracted standalone classes from PROJ-118. The `ship_combat_engine/` tests test the old per-ship wrapper that now delegates to these extracted classes. The tests cover the **same logic** (solve_lead, select_target, calculate_firing_solution) via two different APIs. The `combat/` tests are more thorough (913 lines vs 252 lines combined). The `ship_combat_engine/` versions could be removed if the wrapper is just delegating.
- **Confidence:** MEDIUM - Needs verification that ShipCombatEngine purely delegates to TargetingSystem/WeaponFiringSystem

---

## LOW Confidence Removal Candidates

### 6. Borderline Trivial Tests

#### test_battle_config.py (~147 lines)
- **Location:** `tests/unit/simulation/test_battle_config.py`
- **Assessment:** Tests enum string values (`assert BattleMode.MANUAL.value == "manual"`) and dataclass defaults. Tests Python's own Enum behavior rather than game logic. Also partially duplicated by `battle_controller/test_config.py`.
- **Confidence:** LOW - Provides enum regression guard

#### test_physics_constants.py (~109 lines)
- **Location:** `tests/unit/simulation/test_physics_constants.py`
- **Assessment:** Partially trivial. Tests like `isinstance(K_SPEED, int)` and `K_SPEED > 0` are trivially obvious. The formula verification tests have some value.
- **Confidence:** LOW - Partially trivial

### 7. Stale Filename

#### test_layer_restriction_rule_refactor.py (~204 lines)
- **Location:** `tests/unit/simulation/test_layer_restriction_rule_refactor.py`
- **Assessment:** The file name includes "refactor" suggesting it was written during a refactoring task. The tests themselves are valid unit tests for `LayerRestrictionDefinitionRule`. Should be renamed to `test_layer_restriction_rule.py` or merged with `validation/test_ship_validator_rules.py`.
- **Confidence:** LOW - Rename recommendation, not removal

---

## KEEP - All Other Files (No Action Needed)

### Root-Level Test Files
| File | Lines | Assessment |
|------|-------|------------|
| test_battle_state_serialization.py | 1414 | Thorough serialization round-trip tests |
| test_component_decoupling.py | 234 | Context injection tests (PROJ-29) |
| test_formula_exceptions.py | 174 | Exception handling in formula system |
| test_projectile_manager.py | 1554 | ProjectileManager lifecycle tests |

### battle_controller/ (7 test files + conftest)
| File | Lines | Assessment |
|------|-------|------------|
| test_config.py | ~200 | BattleConfig tests (partial overlap with root test_battle_config.py) |
| test_configure.py | ~300 | BattleController.configure() tests |
| test_lifecycle.py | ~250 | Start/stop lifecycle tests |
| test_retreat_flow.py | ~350 | Retreat mechanics |
| test_start.py | ~300 | BattleController.start() |
| test_update.py | ~400 | BattleController.update() |
| test_utilities.py | ~321 | Factory functions and helpers |

### components/ (7 test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_ability_manager.py | 157 | AbilityManager god class extraction tests |
| test_component_health_manager.py | 386 | ComponentHealthManager damage/health tests |
| test_component_resource_manager.py | 640 | ComponentResourceManager resource tests |
| test_modifier_effects.py | 336 | ModifierEffect dataclass and evaluator tests |
| test_modifier_introspection.py | 694 | ModifierIntrospection tooltip/UI display tests |
| test_modifier_schema.py | 355 | V2 format validation function tests |
| test_modifiers.py | 276 | _apply_effect_to_dict, stat multiplier tests |

### components/abilities/ (8 test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_ability_base.py | 863 | Ability base class tests (some borderline trivial sections but overall valuable) |
| test_colonize_harvester.py | 590 | ColonizePlanet, ResourceHarvester, etc. |
| test_crew_abilities.py | 551 | CrewCapacity, LifeSupport, CrewRequired |
| test_defense_integration.py | 517 | Defense abilities integration tests |
| test_defense_isolation.py | 625 | Defense abilities isolation tests |
| test_resource_consumption.py | 1041 | ResourceConsumption, Storage, Generation |
| test_weapons_integration.py | 628 | Weapon abilities integration tests |
| test_weapons_isolation.py | 1062 | Weapon abilities isolation tests |

### combat/ (4 test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_battle_mode_handlers.py | 330 | BattleModeHandler strategy pattern tests |
| test_damage_calculator.py | 1159 | DamageCalculator thorough damage pipeline tests |
| test_targeting_system.py | 913 | TargetingSystem lead calc, selection, firing solutions |
| test_weapon_firing_system.py | 1293 | WeaponFiringSystem comprehensive weapon firing tests |

### entities/ (8 test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_ability_aggregator.py | 1134 | Ability aggregation with stacking rules |
| test_combat_endurance.py | 911 | Combat endurance calculations |
| test_layer_data.py | 632 | LayerData dataclass tests |
| test_projectile.py | 727 | Projectile entity tests |
| test_ship_formation.py | 1018 | ShipFormation tests |
| test_ship_loader.py | 810 | Vehicle class loading tests |
| test_ship_physics.py | 585 | ShipPhysicsMixin physics tests |
| test_ship_serialization.py | 859 | ShipSerializer round-trip tests |

### managers/ (2 test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_battle_state_manager.py | 225 | BattleStateManager capture/restore tests |
| test_retreat_manager.py | 427 | RetreatManager retreat/escape tests |

### projectile_guidance/ (2 test files + conftest)
| File | Lines | Assessment |
|------|-------|------------|
| test_guidance_behavior.py | 434 | Turn direction commitment, lead calculation |
| test_guidance_core.py | 319 | Guidance activation, turn rate limiting |

### services/ (5 test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_battle_service.py | 985 | BattleService abstraction layer tests |
| test_modifier_service.py | 916 | ModifierService allowance/restriction tests |
| test_registry_loader.py | 245 | Registry reload function tests |
| test_simulation_design_loader.py | 216 | SimulationDesignLoader ship creation tests |
| test_vehicle_design_service.py | 1053 | VehicleDesignService validation tests |

### ship_combat_engine/ (4 test files + conftest)
| File | Lines | Assessment |
|------|-------|------------|
| test_combat_ops.py | 251 | ShipCombatEngine fire_weapons/take_damage |
| test_cooldowns.py | 889 | Shield regen, repair rate, energy cooldowns |
| test_creation_and_lead.py | 100 | **See MEDIUM candidate #5** (potential duplicate of combat/) |
| test_targeting.py | 152 | **See MEDIUM candidate #5** (potential duplicate of combat/) |

### systems/ (5 remaining test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_battle_end_conditions.py | 187 | BattleEndCondition/BattleEndMode tests |
| test_battle_engine_end_conditions.py | 314 | BattleEngine.is_battle_over() tests |
| test_battle_engine_tick.py | 1275 | BattleEngine.update() tick processing |
| test_battle_logger.py | 313 | BattleLogger toggleable logger tests |
| test_resource_manager_edge_cases.py | 181 | ResourceState/ResourceRegistry edge cases |
| test_ship_stats_calculator_phases.py | 375 | ShipStatsCalculator phase extraction tests |
| test_tech_preset_loader.py | 596 | TechPresetLoader validation tests |

### validation/ (2 test files)
| File | Lines | Assessment |
|------|-------|------------|
| test_base_rule.py | 266 | ValidationRule template method pattern |
| test_ship_validator_rules.py | 753 | All ship validation rule logic tests |

### Other Utility Files (KEEP)
| File | Lines | Assessment |
|------|-------|------------|
| mocks/mock_ai_controller.py | 79 | Still used by test_battle_engine_tick.py - KEEP |

---

## Checks Performed

### Skip/Xfail Markers
- **Result:** NONE found. No `@pytest.mark.skip` or `@pytest.mark.xfail` decorators exist anywhere in `tests/unit/simulation/`.

### Dead Code (Import Failures)
- **Result:** All imports in all test files resolve to valid modules. No dead code tests found.

### Over-Mocked Tests
- **Result:** Most tests use mocking appropriately. The `combat/` and `ship_combat_engine/` tests are heavily mocked but this is expected for isolating combat logic from ship internals. No cases of mocks hiding bugs were identified.

---

## Recommendations

### Priority 1 (Quick Wins - HIGH Confidence)
1. **Delete the old component test framework**: Remove `run_component_tests.py`, `update_test_ships.py`, `output/logs/` (7 files), `test_configs/` (12 files). This removes 564 lines of dead code and 19 data files that serve no purpose since the `simulation_tests/` framework replaced them.
2. **Delete `test_ship_stats_phase_ordering.py`**: 22 lines of trivially obvious import/existence checks. The actual phase tests live in `test_ship_stats_calculator_phases.py`.

### Priority 2 (Recommended - MEDIUM Confidence)
3. **Delete old framework utilities**: Remove `component_logger.py`, `component_sim_tools.py`, `log_parser.py` (797 lines). These are only used by `run_component_tests.py` which should already be deleted.
4. **Evaluate `test_physics_formulas.py`**: 731 lines testing inline math rather than game code. Consider removing or replacing with tests that call actual game functions.
5. **Evaluate `ship_combat_engine/test_creation_and_lead.py` and `test_targeting.py`**: Check if `ShipCombatEngine` purely delegates to `TargetingSystem`/`WeaponFiringSystem`. If so, the 252 lines in these files duplicate the 913-line test suite in `combat/test_targeting_system.py`.

### Priority 3 (Optional Cleanup - LOW Confidence)
6. **Rename `test_layer_restriction_rule_refactor.py`** to remove stale "refactor" suffix.
7. **Review `test_battle_config.py` and `test_physics_constants.py`** for borderline trivial tests that could be pruned.
