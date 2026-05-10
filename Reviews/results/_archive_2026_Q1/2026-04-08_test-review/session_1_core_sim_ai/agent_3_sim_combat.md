# Test Review Report: Simulation Combat, Systems & Services

## Scope
- Source files reviewed: 25 files (2339 statements total)
  - game/simulation/combat/ (7 files, 564 stmts)
  - game/simulation/systems/ (6 files, 693 stmts)
  - game/simulation/services/ (6 files, 460 stmts)
  - game/simulation/managers/ (3 files, 139 stmts)
  - game/simulation/battle_controller.py (254 stmts)
  - game/simulation/battle_state.py (277 stmts)
  - game/simulation/projectile_manager.py (104 stmts)
- Test files reviewed: 50+ files across 12 directories
- Coverage data referenced: yes

## Summary
- Test files reviewed: 53
- Source files reviewed: 25
- Tests flagged for removal: 8 (estimated LOC: 97)
- Tests flagged as happy-path-only: 7
- Source files with inadequate coverage: 3

---

## A. Tests Recommended for Removal

### A1. Duplicate test directory: tests/unit/combat/test_combat.py vs tests/unit/simulation/combat/

- **File:** `tests/unit/simulation/ship_combat_engine/test_combat_ops.py`
- **Test(s):** `TestFireWeapons.test_fire_weapons_returns_empty_when_dead`, `test_fire_weapons_returns_empty_when_derelict`, `test_fire_weapons_returns_empty_when_no_weapons`, `TestDamageApplication.test_take_damage_does_nothing_when_dead`, `test_take_damage_applies_emissive_armor_reduction`, `test_take_damage_emissive_armor_blocks_all_when_damage_less_than_armor`, `test_take_damage_applies_shield_regenerating_armor`, `test_take_damage_shields_absorb_before_layers`
- **Reason:** DUPLICATE_OF:`tests/unit/simulation/combat/test_damage_calculator.py` and `tests/unit/simulation/combat/test_weapon_firing_system.py`
- **Confidence:** HIGH
- **Evidence:** ShipCombatEngine is a thin facade that delegates to DamageCalculator and WeaponFiringSystem. The tests in `test_combat_ops.py` (lines 19-236) test the exact same damage pipeline behaviors (emissive armor, SRA, shields, dead/derelict skip, empty weapons) already covered in `test_damage_calculator.py` (lines 32-288) and `test_weapon_firing_system.py` (lines 39-83). Both test sets use identical mock setups and assert the same outcomes. The facade tests add no incremental coverage since the real logic lives in the delegated classes.
- **Estimated LOC saved:** 210 (keeping only the 2 integration tests at lines 238-258)

### A2. Scaffold-only hasattr tests in test_ship_stats_phase_ordering.py

- **File:** `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py`
- **Test(s):** `TestShipStatsPhaseOrdering.test_ship_stats_calculator_exists`, `test_calculator_has_calculate_method`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Lines 14-22 contain only `assert ShipStatsCalculator is not None` and `assert hasattr(ShipStatsCalculator, 'calculate')`. The comprehensive test file `test_ship_stats_calculator_phases.py` (400+ lines) already exercises the calculator thoroughly including all 5 phases, DI injection, and edge cases.
- **Estimated LOC saved:** 22

### A3. Duplicate hasattr tests in test_ship_stats_calculator_phases.py

- **File:** `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py`
- **Test(s):** `TestPhaseHelperMethods.test_priority_sort_key_exists`, `test_check_mass_limits_exists`, `test_initialize_resources_exists`, `test_get_ability_total_exists`, `test_calculate_ability_totals_exists`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Lines 381-404 contain five tests that only assert `hasattr(calculator, '_method_name')`. These are private method existence checks that were scaffolds from the original extraction. The actual phase tests above them (lines 74-369) already exercise these methods through the public `calculate()` API, providing far stronger coverage.
- **Estimated LOC saved:** 25

### A4. Duplicate mode characteristic tests

- **File:** `tests/unit/simulation/combat/test_battle_mode_handlers.py`
- **Test(s):** `TestModeCharacteristics` class (4 tests, lines 260-293)
- **Reason:** DUPLICATE_OF: individual handler test classes above them
- **Confidence:** MEDIUM
- **Evidence:** Lines 260-293 retest the exact same boolean returns already verified per-handler in `TestManualBattleModeHandler` (lines 77-89), `TestTestBattleModeHandler` (lines 116-131), `TestStrategyBattleModeHandler` (lines 154-168), and `TestHypotheticalBattleModeHandler` (lines 192-206). Each "characteristics" test is a 4-assertion copy of what the individual classes test with 1 assertion each. The individual tests provide better failure isolation.
- **Estimated LOC saved:** 34

### A5. Duplicate interface-existence tests in test_battle_mode_handlers.py

- **File:** `tests/unit/simulation/combat/test_battle_mode_handlers.py`
- **Test(s):** `TestBattleModeHandlerInterface.test_has_configure_method`, `test_has_can_retreat_method`, `test_has_can_reinforce_method`, `test_has_apply_results_method`, `test_has_should_clone_ships_method`, `test_has_is_headless_default_method`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** MEDIUM
- **Evidence:** Lines 38-61 are `hasattr` checks on abstract methods. The concrete handler tests (lines 63-255) instantiate all four handlers and call every method, which inherently proves the methods exist. The `test_is_abstract_class` and `test_cannot_instantiate_directly` tests (lines 29-36) are legitimate API contract guards and should be kept.
- **Estimated LOC saved:** 16

---

## B. Tests That Are Happy-Path-Only

### B1. DamageCalculator missing event-bus emission tests

- **File:** `tests/unit/simulation/combat/test_damage_calculator.py`
- **Test(s):** All tests in `TestEmissiveArmorReduction`, `TestShieldAbsorption`, `TestLayerDamage`, `TestShieldRegeneratingArmorAbsorption`
- **What's tested:** Damage pipeline arithmetic (shield values, HP changes, layer traversal)
- **What's missing:** No test passes an event_bus to `apply_damage()`. The source (lines 93-100, 111-117, 130-136, 211-229) emits SHIELD_HIT, ARMOR_ABSORBED, COMPONENT_HIT, COMPONENT_DESTROYED, and SHIP_DERELICT events. These event emission paths are completely untested at the unit level. Missing lines 94, 112, 131, 212-213, 222 from coverage.
- **Source method(s) affected:** `game/simulation/combat/damage_calculator.py:93-100,111-117,130-136,211-229`
- **Priority:** HIGH (event bus is used for UI combat log and visual effects)

### B2. FleetAuraManager missing edge cases

- **File:** `tests/unit/simulation/combat/test_fleet_aura_cache.py` and `test_fleet_aura_register.py`
- **Test(s):** All fleet aura tests
- **What's tested:** Basic caching, registration, bonus propagation for attack/defense
- **What's missing:** (1) `get_active_bonuses()` method at line 256-285 is untested -- no test calls it. (2) External modifiers from BattleConfig (team_modifiers, global_modifiers) at lines 77-92 are untested. (3) Dead provider cleanup during `_recalculate()` at lines 186-205 (operational component check loop) is partially tested but the component-destruction-removes-aura path is not. (4) The `_get_provider_fingerprint()` method at lines 155-169 has untested branches for dead provider ships. These account for most of the 31 missing lines.
- **Source method(s) affected:** `game/simulation/combat/fleet_aura_manager.py:77-92,155-169,186-205,256-285`
- **Priority:** HIGH (79.3% coverage, significant untested functionality)

### B3. BattleEngine.update() tick processing missing phase ordering

- **File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
- **Test(s):** All tests in tick processing module
- **What's tested:** Tick counter increments, basic ship update calls, early returns
- **What's missing:** The test file does not verify the actual ordering of system updates (AI update -> ship update -> weapon firing -> collision -> aura update). Missing lines include 124-127 (start method error handling), 193 (projectile cleanup edge case), 298 (beam attack processing edge case), 362 (tick phase integration), 393-416 (various update loop branches). Tests only mock external dependencies without verifying call ordering.
- **Source method(s) affected:** `game/simulation/systems/battle_engine.py:124-127,193,298,362,393-416`
- **Priority:** MEDIUM

### B4. ResourceManager missing set_regen_rate and set_max_value when resource absent

- **File:** `tests/unit/simulation/systems/test_resource_manager_edge_cases.py`
- **Test(s):** All resource manager edge case tests
- **What's tested:** Consume, regen, storage registration, set_value, modify_value, reset_stats
- **What's missing:** `set_regen_rate()` when resource does not exist (line 198-200: `if res:` branch for None). `set_max_value()` when resource does not exist (line 190-192: creates new via register_storage). `modify_value()` when resource does not exist (line 178: `if res:` branch for None). These are the 10 missing lines.
- **Source method(s) affected:** `game/simulation/systems/resource_manager.py:190-192,194,198-200`
- **Priority:** LOW (edge cases unlikely to cause production bugs)

### B5. VehicleDesignService missing error path coverage

- **File:** `tests/unit/simulation/services/test_vehicle_design_service.py`
- **Test(s):** All tests in `TestAddComponent`, `TestRemoveComponent`, `TestChangeClass`
- **What's tested:** Success paths, invalid inputs, basic error reporting
- **What's missing:** Missing coverage for lines 129-132 (add_component exception handling when Ship.add_component raises), 201-202 (add_component_bulk partial failure internal handling), 242 (get_layer_info defensive coding), 381 (validate_design internal validation exception path). The test for `add_component_to_full_layer` (line 917) has a weak assertion `assert added_count > 0 or True` that always passes.
- **Source method(s) affected:** `game/simulation/services/vehicle_design_service.py:129-132,201-202,242,381`
- **Priority:** MEDIUM

### B6. BattleController missing headless/pause integration

- **File:** `tests/unit/simulation/battle_controller/` (all files)
- **Test(s):** Various test classes across the directory
- **What's tested:** Config creation, mode handlers, retreat, reinforcements, basic execution
- **What's missing:** Missing coverage for lines 168-169 (headless mode toggle during battle), 180 (pause state edge case), 390-393 (apply_results exception handling), 438 (state query when no mode handler), 514-516 (get_battle_results edge cases), 551 (cleanup edge case).
- **Source method(s) affected:** `game/simulation/battle_controller.py:168-169,180,390-393,438,514-516,551`
- **Priority:** LOW

### B7. SimulationDesignLoader missing load_ship_from_design_data error paths

- **File:** `tests/unit/simulation/services/test_simulation_design_loader.py`
- **Test(s):** `TestSimulationDesignLoader` class
- **What's tested:** Success paths for loading from data and file, file-not-found, invalid JSON
- **What's missing:** The source has two catch blocks at lines 82-85 (data validation errors) and 86-89 (unexpected errors) in `load_ship_from_design_data` that return None on failure. No test exercises these paths. Similarly, `load_ship_from_file` line 129-132 (data validation after successful JSON parse) and line 133-136 (OSError) are untested. These account for the 14 missing lines (69.6% coverage).
- **Source method(s) affected:** `game/simulation/services/design_loader.py:82-89,119-136`
- **Priority:** MEDIUM (error handling in design loading could mask broken designs)

---

## C. Source Code with Inadequate Coverage

### C1. game/simulation/battle_state.py (277 stmts, 75.5%)

- **Coverage:** 75.5% -- 68 missing lines
- **Untested areas:**
  - `ShipState.from_ship()` (lines 273-325): Never called in tests. This captures live Ship objects to serializable state. All tests use `from_dict()` instead.
  - `ShipState.to_ship()` (lines 327-419): The registry-dependent ship reconstruction path is partially tested but component damage restoration (lines 388-404) and resource restoration (lines 408-411) are not.
  - `ProjectileState.from_projectile()` (lines 490-531): Never called in tests.
  - `ProjectileState.to_projectile()` (lines 533-572): Never called in tests.
  - `BattleState.capture_from_engine()` (lines 652-714): Never called in tests. This is the primary capture method used during save/load.
  - `BattleResults.from_dict()` (lines 772-791): Never called in tests.
  - Various query methods (`get_ships_by_team`, `get_alive_ships`, `get_surviving_ships`, `get_escaped_ships`, `get_destroyed_ships`, `get_team_survivors`, `get_team_losses`): Several appear untested.
- **Risk:** Save/load could silently corrupt battle state. Strategy layer integration depends on `capture_from_engine()` and `BattleResults` working correctly. These are serialization boundary methods that are critical for game persistence.
- **Priority:** HIGH

### C2. game/simulation/combat/fleet_aura_manager.py (150 stmts, 79.3%)

- **Coverage:** 79.3% -- 31 missing lines
- **Untested areas:**
  - `get_active_bonuses()` (lines 256-285): UI display method completely untested.
  - External modifier loading from BattleConfig (lines 77-92): Config-driven team and global modifiers never tested.
  - Provider operational check in `_recalculate()` (lines 192-205): The loop that checks if the specific aura-providing component is still operational is only partially exercised.
  - `_get_provider_fingerprint()` death/derelict branches (lines 161-169).
- **Risk:** Fleet aura bonuses could be displayed incorrectly in the UI. External battle conditions (e.g., terrain modifiers, weather effects) would be silently ignored if the config loading code had bugs. Component-destruction-removes-aura behavior could regress.
- **Priority:** HIGH

### C3. game/simulation/services/design_loader.py (46 stmts, 69.6%)

- **Coverage:** 69.6% -- 14 missing lines
- **Untested areas:**
  - `load_ship_from_design_data()` error branches (lines 82-89): Both exception catch blocks return None on failure but are never triggered in tests.
  - `load_ship_from_file()` error branches (lines 119-120 for None return from `load_ship_from_design_data`, lines 129-132 for data validation errors after successful JSON parse, lines 133-136 for OSError).
- **Risk:** Invalid ship designs loaded from disk would silently return None instead of providing meaningful errors. Users could have corrupted design files that never surface as errors.
- **Priority:** MEDIUM

---

## D. Cross-Domain Observations

### D1. tests/unit/combat/ is NOT a superseded directory

Despite the naming similarity, `tests/unit/combat/` contains tests for different concerns than `tests/unit/simulation/combat/`:
- `test_combat.py`: Integration tests using real Ship objects with fresh_registries (real damage pipeline with actual components).
- `test_battle_setup_logic.py`: BattleScreen UI integration tests (SpatialGrid, AI controller setup). These belong in the UI domain session.

**Recommendation:** `test_battle_setup_logic.py` should be moved to `tests/unit/ui/` since it tests `game.ui.screens.battle_screen.BattleScreen`. It was likely placed here before the reorganization.

### D2. tests/unit/systems/ is NOT a superseded directory

`tests/unit/systems/` contains tests for cross-cutting systems (physics, formulas, event bus, spatial grid, persistence, layer restrictions) that are NOT duplicated in `tests/unit/simulation/systems/`. These directories cover different source modules:
- `tests/unit/systems/`: `game.engine.physics`, `game.simulation.formula_system`, `game.ui.screens.builder.event_bus`, `game.ui.services.ship_io`
- `tests/unit/simulation/systems/`: `game.simulation.systems.*`

**No removal recommended.** However, `tests/unit/systems/test_event_bus.py` tests `game.ui.screens.builder.event_bus.EventBus` and should be flagged for the UI session (session 3) as it belongs in `tests/unit/ui/`.

### D3. Physics constants tests verify specific magic numbers

`tests/unit/systems/test_physics.py` line 316-323 asserts `K_SPEED == 25`, `K_THRUST == 2500`, `K_TURN == 25000`. While these look like TRIVIAL_CONSTANT tests, the comment says "documentation check" and these constants are used in formulas throughout the simulation. Changing them would break game balance. These are legitimate regression guards per the "tests validating invariants between related values" keep criterion.

### D4. ShipCombatEngine duplicate concern

The duplicate tests between `tests/unit/simulation/ship_combat_engine/test_combat_ops.py` and `tests/unit/simulation/combat/test_damage_calculator.py` / `test_weapon_firing_system.py` exist because ShipCombatEngine is a facade that was decomposed in PROJ-44. The facade tests should either be removed (if the facade is truly thin) or reduced to verify delegation only (i.e., "calling facade.take_damage calls DamageCalculator.apply_damage with correct args").

### D5. Regression test file is well-maintained

`tests/regression/test_deprecated_code_removed.py` is a valuable regression guard that counts singleton usage across the codebase and verifies deprecated patterns stay removed. It should be kept and maintained as the codebase evolves.

### D6. Combat Lab test files are well-structured

The `tests/unit/combat_lab/` directory contains focused scenario tests for the simulation test framework. These are functional tests that verify the test infrastructure itself works correctly (position tracking, weapon stats collection, resource scenarios, etc.). No issues found.
