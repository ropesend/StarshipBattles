# Test Review Report: Agent 2 -- Strategy Engine

## Scope
- Source files reviewed: 30 files in `game/strategy/engine/` (3,893 total statements per coverage data)
- Test files reviewed: 63 test files across `tests/unit/strategy/engine/`, `tests/unit/strategy/turn_engine/`, `tests/unit/strategy/conflict_resolution/`, `tests/unit/strategy/consumable_management_engine/`, `tests/unit/strategy/fleet_movement_engine/`, `tests/unit/strategy/production_engine/`
- Coverage data referenced: yes -- line-level missing coverage from coverage.json for all 30 source files

## Summary
- Test files reviewed: 63
- Source files reviewed: 30
- Tests flagged for removal: 5 (estimated LOC: 85)
- Tests flagged as happy-path-only: 11
- Source files with inadequate coverage: 6

---

## A. Tests Recommended for Removal

### A1. test_commands.py -- TestCommandType class
- **File:** `tests/unit/strategy/engine/test_commands.py`
- **Test(s):** `TestCommandType.test_issue_order_exists`, `TestCommandType.test_enum_is_auto_generated`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** Lines 41-48 assert `hasattr(CommandType, 'ISSUE_ORDER')` and that its `.value` is an `int`. These test Python's `enum.auto()` behavior, not game logic. The enum is a frozen constant; removing these tests loses zero regression coverage.
- **Estimated LOC saved:** 8

### A2. test_commands.py -- redundant field assertions
- **File:** `tests/unit/strategy/engine/test_commands.py`
- **Test(s):** `TestIssueMoveCommand.test_with_origin_hex` (line 119-123), `TestIssueInterceptCommand.test_intercept_self` (line 141-143)
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** `test_with_origin_hex` creates a command with `HexCoord(0,0)` and asserts `== HexCoord(0,0)` -- this tests dataclass field storage with a different value, which is already covered by `test_create_with_target_hex`. `test_intercept_self` asserts `fleet_id == target_fleet_id` when both are 5 -- this documents that the dataclass doesn't validate, but no validation code exists to test. These are marginal but very low value.
- **Estimated LOC saved:** 10

### A3. test_build_order_command_handler.py -- IssueBuildOrderCommand dataclass tests duplicate test_commands.py
- **File:** `tests/unit/strategy/engine/test_build_order_command_handler.py`
- **Test(s):** `TestIssueBuildOrderCommand.test_create_build_order_command`, `test_command_name`, `test_commands_with_same_fleet_are_equal`, `test_commands_with_different_fleet_are_not_equal`
- **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_commands.py:TestCommandBase.test_all_commands_have_type` and `TestCommandEquality`
- **Confidence:** MEDIUM
- **Evidence:** `test_commands.py` line 59-83 already tests that ALL command types have `ISSUE_ORDER` type and tests equality semantics. The build order command is included in that list (line 81 registry has it). The 4 tests in `test_build_order_command_handler.py` lines 18-41 re-test the same dataclass mechanics for this specific command. The handler tests (lines 45+) are unique and should stay.
- **Estimated LOC saved:** 24

### A4. test_planet_energy_cache.py -- test_cached_values_reused_on_unchanged_facilities
- **File:** `tests/unit/strategy/engine/test_planet_energy_cache.py`
- **Test(s):** `TestPlanetEnergyCache.test_cached_values_reused_on_unchanged_facilities`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** MEDIUM
- **Evidence:** Lines 52-63 call `_process_planet` twice then assert the cache dict has `capacity` and `generation` keys. This is identical to what `test_cache_populated_on_first_tick` already verifies (that the cache exists). The test comment says "the scan only runs once" but does not actually verify that -- it would need to instrument or count calls to prove reuse. It tests dict key existence, which is already proven by test at line 42.
- **Estimated LOC saved:** 13

### A5. test_fleet_order_transfer.py -- TestTransferResult
- **File:** `tests/unit/strategy/engine/test_fleet_order_transfer.py`
- **Test(s):** `TestTransferResult.test_transfer_result_has_required_fields`, `test_transfer_result_defaults`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** Lines 369-389 create `TransferResult(success=True, amount_transferred=100, message="OK")` and assert each field equals what was passed in. This tests Python's `@dataclass` mechanics. The dataclass is a frozen 3-field struct with defaults; these tests have zero regression value.
- **Estimated LOC saved:** 20

---

## B. Tests That Are Happy-Path-Only

### B1. test_planet_action_engine.py -- no error path for _initiate_activation on non-INACTIVE state
- **File:** `tests/unit/strategy/engine/test_planet_action_engine.py`
- **Test(s):** `TestPlanetActionEngine` (all tests)
- **What's tested:** Activate from INACTIVE, deactivate from ACTIVE, deactivate from ACTIVATING, destroyed facility cancellation, multiple orders, mixed orders
- **What's missing:** (1) Attempting to activate a component already in ACTIVATING state (line 193-198 in source: warning logged, no state change). (2) Attempting to activate from ACTIVE state. (3) Attempting to deactivate from INACTIVE or DEACTIVATING state (line 281 in source). (4) _resolve_component_key returning None (no matching ability found) -- lines 306-309. (5) _find_target_facility fallback paths (lines 362-371).
- **Source method(s) affected:** `planet_action_engine.py:193-198, 281-284, 306-309, 362-371`
- **Priority:** MEDIUM

### B2. test_planet_energy_engine.py -- missing edge cases for _cancel_all_draining_components
- **File:** `tests/unit/strategy/engine/test_planet_energy_engine.py`
- **Test(s):** `TestPlanetEnergyEngine`, `TestPlanetEnergyEngineEvents`
- **What's tested:** Generation, capping, draining, auto-deactivation, stacking, non-operational facility, no-battery
- **What's missing:** (1) Non-operational facility with active component_states -- should it still drain? Lines 268-270 skip non-operational facilities in `_cancel_all_draining_components`. (2) Multiple active components draining simultaneously, one insufficient -- all should cancel (lines 266-296). (3) Component state entries that are not dicts or lack 'phase' key (line 259-260: defensive check). (4) `get_shield_info` and `get_activatable_ability_info` module-level functions (lines 40-66) have zero test coverage.
- **Source method(s) affected:** `planet_energy_engine.py:40-66, 259-260, 266-296`
- **Priority:** MEDIUM

### B3. test_atmosphere_engine.py -- missing zero gravity / zero surface_area edge case
- **File:** `tests/unit/strategy/engine/test_atmosphere_engine.py`
- **Test(s):** `TestAtmosphereEngine`
- **What's tested:** No target, moves toward target, no overshoot, planet size scaling, stacking, gas reduction, new gas addition, non-operational, no facility, rate calibration
- **What's missing:** (1) Zero `surface_area` or zero `surface_gravity` -- source lines 83-84 early-return without modification (uncovered lines 59, 69, 71, 72, 84). (2) `atmosphere_target` with a gas not present and also reducing another gas simultaneously. (3) Colony with `atmosphere` attribute missing entirely (line 57-58: getattr fallback).
- **Source method(s) affected:** `atmosphere_engine.py:59, 69, 71-72, 84`
- **Priority:** LOW

### B4. test_empire_economy_calculator.py -- no test for _calculate_maintenance_cost
- **File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py`
- **Test(s):** `TestEmpireEconomyCalculator`
- **What's tested:** Empty empire, single colony, net resources, storage, non-operational, multiple, missing quality, placeholder sources, registry fallback, construction expenses
- **What's missing:** (1) Ship/fleet maintenance cost calculation -- source lines 244-249 (uncovered) compute per-ship maintenance from `resource_cost` in design_data. (2) Facilities with `resource_cost` contributing to maintenance expenses. This is the primary missing coverage area at 93.8%.
- **Source method(s) affected:** `empire_economy_calculator.py:244-249`
- **Priority:** MEDIUM

### B5. test_fleet_movement_engine.py -- no test for normal MOVE path calculation
- **File:** `tests/unit/strategy/engine/test_fleet_movement_engine.py`
- **Test(s):** `TestFleetMovementEngineEnvironmentalEffects`, `TestFleetMovementEngineErrorHandling`
- **What's tested:** Storm speed reduction, effective speed calculation, error handling (stranded, warp failures)
- **What's missing:** (1) Normal successful movement (non-storm) with actual hex-to-hex path following -- all movement tests mock `calculate_next_hex`. (2) Fleet movement consuming fuel (lines 117, 257 uncovered). The separate `tests/unit/strategy/fleet_movement_engine/` directory covers more basics, but the fuel consumption path is untested.
- **Source method(s) affected:** `fleet_movement_engine.py:117, 257`
- **Priority:** LOW

### B6. test_turn_state_snapshot.py -- dump_crash_snapshot completely untested
- **File:** `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py`
- **Test(s):** `TestTurnStateSnapshotCapture`, `TestTurnStateSnapshotRestore`
- **What's tested:** Capture stores turn number, empire dicts, galaxy dict, timestamp, isolation from mutations, serialization failure. Restore resets empires, galaxy, empire count.
- **What's missing:** (1) `dump_crash_snapshot()` method (source lines 102-134) -- writes crash snapshot to disk, handles OSError. Zero test coverage. (2) `restore()` -- fleet re-registration with galaxy (line 92-93) and order reference resolution (line 97-98) are exercised via the real restore but not individually verified.
- **Source method(s) affected:** `turn_state_snapshot.py:102-134 (dump_crash_snapshot), 92-98 (restore fleet/order registration)`
- **Priority:** HIGH -- crash snapshots are a debugging lifeline; untested file I/O could silently fail

### B7. test_order_processor (various) -- fleet-to-fleet transfer untested
- **File:** `tests/unit/strategy/engine/test_fleet_order_transfer.py`
- **Test(s):** `TestProcessTransfer`, `TestTransferValidation`, `TestExecuteLoad`, `TestExecuteUnload`
- **What's tested:** Planet-to-fleet transfers (load/unload passengers, capping, species), validation errors
- **What's missing:** (1) Fleet-to-fleet transfer path (`_execute_fleet_transfer` at lines 366-396) -- completely untested. (2) Resource cargo (non-passenger) load/unload from planet stockpile (lines 447-467, 519-530). (3) Drop pod load/unload from staging yard (`_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard` at lines 532-616). (4) LOAD_POPULATION auto-resolve colony at fleet hex (BUG-70 path, lines 295-307).
- **Source method(s) affected:** `order_processor.py:295-307, 366-396, 447-467, 519-530, 532-616`
- **Priority:** HIGH -- fleet-to-fleet transfers and staging yard operations are production features with zero coverage

### B8. test_colonize_mission_handler.py -- no failure path tests
- **File:** `tests/unit/strategy/engine/test_colonize_mission_handler.py`
- **Test(s):** `TestColonizeMissionHandlerPodValidation`
- **What's tested:** Universal drop pod acceptance, matching pod, exhausted pod at command time, none planet, no pods
- **What's missing:** (1) Fleet not found error. (2) Planet not found error. (3) Pathfinding failure to target_hex. All tests use valid fleet/planet mocks. The handler at `command_handlers.py` lines ~400-450 has validation paths for fleet resolution and pathfinding that are never tested in this file.
- **Source method(s) affected:** `command_handlers.py:400-450 (ColonizeMissionCommandHandler.execute)`
- **Priority:** LOW -- the BaseCommandHandler resolution is tested elsewhere

### B9. test_game_session.py / game_session.py -- process_turn error handling path
- **File:** (no dedicated game_session test file beyond test_game_initializer.py)
- **Test(s):** N/A -- GameSession.process_turn() has test coverage only through turn_engine integration
- **What's tested:** Initialization, fleet lookup, session creation
- **What's missing:** (1) `GameSession.process_turn()` (lines 159-180) -- the EnginePhaseError catch-and-re-raise path. (2) `_create_event_handler()` closure (lines 135-157). (3) `preview_fleet_path()` (line 182+). Coverage is 89.4% but the missing 13 lines include the turn failure path, event handler creation, and several property accessors.
- **Source method(s) affected:** `game_session.py:133, 177-180, 214-215, 229, 304-305, 333-334, 347-348`
- **Priority:** MEDIUM

### B10. test_harvesting_engine.py -- missing registry-based size_mount for harvesters via registry lookup path
- **File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
- **Test(s):** `TestHarvestingEngine`
- **What's tested:** Single/multiple harvesters, depletion, quality scaling, storage, non-operational, registry lookup, per-tick, storage aggregation
- **What's missing:** (1) `_get_total_harvesters_from_facility_component_list` path when component is a string ID and registry returns None (lines 113-115, uncovered). (2) Harvesting when a facility has components with both harvester and non-harvester abilities. (3) Concurrent harvesting of the same resource by harvesters in different facilities on the same planet exceeding planet quantity mid-turn (the depletion test uses a single facility).
- **Source method(s) affected:** `harvesting_engine.py:62, 113-115, 201-204`
- **Priority:** LOW

### B11. test_superweapon_order_processor.py -- some edge case branches uncovered
- **File:** `tests/unit/strategy/engine/test_superweapon_order_processor.py`
- **Test(s):** Multiple test classes covering all superweapon types
- **What's tested:** Extensive coverage at 89.7% -- implode planet, stellerate star, open/close warp point, create dyson sphere, self-destruct
- **What's missing:** (1) Missing validation paths: lines 165-167 (fleet has no ships for warp point), lines 244-246 (no valid warp destination), lines 518-524 (dyson sphere star not found), lines 532-534 (dyson sphere already exists). These are defensive error paths.
- **Source method(s) affected:** `superweapon_order_processor.py:165-167, 244-246, 518-524, 532-534`
- **Priority:** LOW

---

## C. Source Code with Inadequate Coverage

### C1. planet_command_handlers.py -- 17.9% coverage (CRITICAL)
- **Source file:** `game/strategy/engine/planet_command_handlers.py` (78 stmts)
- **Coverage:** 17.9% -- only 14 of 78 statements covered
- **Untested areas:** ALL four handler classes are effectively untested:
  - `IssuePlanetOrderCommandHandler.execute()` (lines 39-97): Planet resolution, ownership check, order type parsing, ACTIVATE_ABILITY validation, DEACTIVATE_ABILITY validation, target dict construction, order queuing
  - `ClearPlanetOrdersCommandHandler.execute()` (lines 104-115): Planet resolution, ownership, clear_orders
  - `DeletePlanetOrderCommandHandler.execute()` (lines 121-136): Planet resolution, ownership, index bounds check, order removal
  - `SetAtmosphereTargetCommandHandler.execute()` (lines 142-157): Planet resolution, ownership, atmosphere target setting
- **Risk:** These handlers are the entry point for all planet order commands from the UI. A regression could silently accept invalid orders or reject valid ones. The 17.9% coverage comes only from imports and class definitions.
- **Priority:** HIGH -- worst coverage in the entire engine package

### C2. turn_state_snapshot.py -- 73.9% coverage
- **Source file:** `game/strategy/engine/turn_state_snapshot.py` (46 stmts)
- **Coverage:** 73.9% -- 12 lines uncovered
- **Untested areas:**
  - `restore()` fleet re-registration loop (line 93) and order reference resolution (line 98) -- tested indirectly but not asserted
  - `dump_crash_snapshot()` (lines 113-134) -- entirely untested, both success and error paths
- **Risk:** Crash snapshots are the primary debugging mechanism for turn failures. If `dump_crash_snapshot` fails silently (e.g., permission error on save_path), debugging production crashes becomes impossible.
- **Priority:** HIGH

### C3. planet_action_engine.py -- 82.9% coverage
- **Source file:** `game/strategy/engine/planet_action_engine.py` (170 stmts)
- **Coverage:** 82.9% -- 29 lines uncovered
- **Untested areas:**
  - `_initiate_activation()` when current phase is not INACTIVE (lines 193-198)
  - `_initiate_deactivation()` when phase is neither ACTIVATING nor ACTIVE (lines 281)
  - `_resolve_component_key()` fallback path (lines 302-309)
  - `_find_target_facility()` fallback paths (lines 363-371): searching by ability name when facility_instance_id not found, and legacy PlanetaryShield fallback
  - `_find_ability_component_id()` (lines 373-382) and `_find_shield_component_id()` legacy wrapper (lines 384-386)
- **Risk:** The fallback paths in `_find_target_facility` could return None unexpectedly, causing NoneType errors in activation/deactivation flows.
- **Priority:** MEDIUM

### C4. planet_energy_engine.py -- 83.6% coverage
- **Source file:** `game/strategy/engine/planet_energy_engine.py` (122 stmts)
- **Coverage:** 83.6% -- 20 lines uncovered
- **Untested areas:**
  - Module-level functions `get_shield_info()` (lines 46-50) and `get_activatable_ability_info()` (lines 62-66) -- used by other modules but never tested directly
  - `_validate_tick_inputs` error path (lines 131-133) -- `ValidationException` when registries is None (tested via `test_engine_validation.py` only for the colony-None case, not the constructor)
  - `_cancel_all_draining_components()` inner loop for multiple facilities (lines 260, 270, 273)
- **Risk:** `get_shield_info` and `get_activatable_ability_info` are public API used by PlanetActionEngine and UI code. Silent breakage would cascade.
- **Priority:** MEDIUM

### C5. order_processor.py -- 85.0% coverage
- **Source file:** `game/strategy/engine/order_processor.py` (334 stmts)
- **Coverage:** 85.0% -- 50 lines uncovered
- **Untested areas:**
  - `_execute_fleet_merge()` event logging when event_bus is present (line 100)
  - Fleet-to-fleet transfer resolution: search through `galaxy.empires` and `empire.fleets` (lines 308-326)
  - `_execute_fleet_transfer()` (lines 379-396) -- zero test coverage
  - `_execute_load()` for resource cargo (non-passenger, non-drop_pod) path (lines 447-467)
  - `_execute_unload()` for resource cargo path (lines 519-530)
  - `_load_pod_from_staging_yard()` and `_unload_pod_to_staging_yard()` (lines 532-616)
  - BUG-70 auto-resolve colony for LOAD_POPULATION (lines 295-307)
  - Colonize "Any" planet path (lines 200-207)
- **Risk:** Fleet-to-fleet transfers and staging yard operations are production features with zero test coverage. Resource cargo transfers (metals, fuel, etc.) between fleet and colony are also untested.
- **Priority:** HIGH

### C6. command_handlers.py -- 90.6% coverage
- **Source file:** `game/strategy/engine/command_handlers.py` (449 stmts)
- **Coverage:** 90.6% -- 42 lines uncovered
- **Untested areas:**
  - `TransferCommandHandler.execute()` -- validation failure on invalid direction (line 558), missing target (fleet-to-fleet path lines 585-614)
  - `WarpCommandHandler.execute()` -- warp point validation, auto-move prefix, destination resolution (lines 625-648) -- partially tested via separate warp tests
  - `SelfDestructCommandHandler.execute()` validation paths (lines 870-879, 882-884, 905-910)
  - `create_default_registry()` -- handler registration for planet command handlers (line 936, 969)
- **Risk:** The warp command handler and self-destruct handler have validation branches that could pass invalid data through to game state.
- **Priority:** MEDIUM

---

## D. Cross-Domain Observations

1. **planet_command_handlers.py at 17.9% is the single worst coverage file in the engine.** It handles four distinct planet order commands (issue, clear, delete, set atmosphere target) that are critical for the strategy layer UI interaction. This should be prioritized as a standalone test-writing task.

2. **Fleet-to-fleet transfers (`_execute_fleet_transfer`) have zero test coverage** in order_processor.py. This is a production feature (transferring cargo between two fleets at the same location) that could silently break. The `test_fleet_order_transfer.py` file only tests planet-to-fleet transfers.

3. **Staging yard pod operations (`_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard`) have zero test coverage.** These are called from `_execute_load`/`_execute_unload` when `cargo_type == "drop_pod"`. The `test_pod_transfer.py` file exists but uses a different testing approach (integration-style through command handlers) that may not exercise these internal methods.

4. **`dump_crash_snapshot` in turn_state_snapshot.py is completely untested.** This method writes debugging data to disk when a turn fails. It has error handling (OSError catch) that has never been exercised. Since this is the primary debugging tool for production turn failures, it should have at least basic tests for both success and error paths.

5. **Module-level helper functions `get_shield_info()` and `get_activatable_ability_info()` in planet_energy_engine.py** are imported by other modules (planet_action_engine.py uses `get_shield_info` at line 24) but have zero direct test coverage. If these functions break, the failure would cascade to planet action processing.

6. **test_commands.py** is thorough (411 lines) but approximately 30% of its tests verify dataclass field storage which is guaranteed by Python. The remaining 70% testing command equality, command types, and API contracts is valuable. A selective cleanup could save ~30 lines without losing any real regression coverage.

7. **test_engine_validation.py is exemplary**: 14 engine validation tests across 313 lines, each testing both the valid-input and invalid-input paths. This pattern should be replicated for planet_command_handlers.py.
