# Test Review Report: Agent 3 — Strategy Services/Validation/Fleet

## Scope
- Source files reviewed: 22 files (5,998 LOC total)
  - `game/strategy/validation/planet_order_validator.py` (149 LOC)
  - `game/strategy/services/fleet_cargo_projector.py` (64 LOC)
  - `game/strategy/systems/race_library.py` (255 LOC)
  - `game/strategy/services/design_validator.py` (197 LOC)
  - `game/strategy/interfaces/engines.py` (613 LOC)
  - `game/strategy/validation/transfer_validator.py` (246 LOC)
  - `game/strategy/services/component_inspector.py` (335 LOC)
  - `game/strategy/services/strategic_ability_scanner.py` (237 LOC)
  - `game/strategy/validation/colonize_validator.py` (143 LOC)
  - `game/strategy/services/modifier_resolver.py` (69 LOC)
  - `game/strategy/services/system_effects_collector.py` (231 LOC)
  - `game/strategy/interfaces/battle_resolver.py` (92 LOC)
  - `game/strategy/services/fleet_navigation_service.py` (681 LOC)
  - `game/strategy/formulas/habitability.py` (316 LOC)
  - `game/strategy/services/action_time_resolver.py` (195 LOC)
  - `game/strategy/data/pathfinding.py` (501 LOC)
  - `game/strategy/systems/race_randomizer.py` (130 LOC)
  - `game/strategy/services/ship_stats_calculator.py` (750 LOC)
  - `game/strategy/services/cargo_transfer_service.py` (300 LOC)
  - `game/strategy/services/area_effect_manager.py` (101 LOC)
  - `game/strategy/services/fleet_speed_calculator.py` (192 LOC)
  - `game/strategy/adapters/simulation_adapter.py` (201 LOC)
- Test files reviewed: 46 files (12,206 LOC total)
- Coverage data referenced: Yes, from `coverage.json` with line-level missing data

## Summary
- Test files reviewed: 46
- Source files reviewed: 22
- Tests flagged for removal: 5 (estimated LOC: 670)
- Tests flagged as happy-path-only: 5
- Source files with inadequate coverage: 5

---

## A. Tests Recommended for Removal

### A1. test_engine_interfaces.py — Interface-only structural tests
- **File:** `tests/unit/strategy/interfaces/test_engine_interfaces.py`
- **Test(s):** `TestIMovementEngineInterface`, `TestIProductionEngineInterface`, `TestIOrderProcessorInterface`, `TestIConflictEngineInterface`, `TestIConsumableEngineInterface`, `TestIPopulationEngineInterface`, `TestIResupplyEngineInterface`, `TestIHarvestingEngineInterface`, `TestConcreteImplementations`, `TestInterfacesModuleExports`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** All 476 lines consist exclusively of: (a) asserting ABCs are importable, (b) asserting ABCs have `__isabstractmethod__` attributes, (c) asserting ABCs cannot be instantiated, (d) creating trivial mock implementations that call `pass`, (e) checking `__all__` exports. No real game logic executes. These tests are entirely structural — they verify Python ABC mechanics (`issubclass(X, ABC)`, `TypeError` on instantiation), not game behavior. The `test_engine_inheritance.py` file (57 LOC) already verifies the concrete engines inherit their interfaces, making most of these redundant.
- **Estimated LOC saved:** 476

### A2. test_simulation_adapter.py — TestSimulationBattleResolverImport class
- **File:** `tests/unit/strategy/adapters/test_simulation_adapter.py`
- **Test(s):** `TestSimulationBattleResolverImport.test_adapter_importable_from_adapters`, `TestSimulationBattleResolverImport.test_adapter_importable_from_adapters_package`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Lines 18-29 only assert that `SimulationBattleResolver is not None` after importing. The subsequent test classes (`TestSimulationBattleResolverImplementation`, `TestSimulationBattleResolverBehavior`) import and use the same class, so any import failure would be caught by those tests. Pure import-success assertions add no value.
- **Estimated LOC saved:** 12

### A3. test_battle_resolver.py — Import and structural assertion tests
- **File:** `tests/unit/strategy/interfaces/test_battle_resolver.py`
- **Test(s):** `TestBattleResult.test_battle_result_importable`, `TestBattleResult.test_battle_result_is_dataclass`, `TestIBattleResolverInterface.test_ibattle_resolver_importable`, `TestIBattleResolverInterface.test_ibattle_resolver_is_abstract`, `TestIBattleResolverInterface.test_ibattle_resolver_has_resolve_battle_method`, `TestIBattleResolverInterface.test_concrete_implementation_must_implement_resolve_battle`, `TestInterfacesModuleExports.test_battle_resolver_accessible_from_interfaces_package`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** MEDIUM
- **Evidence:** Lines 20-28 assert `BattleResult is not None` and `hasattr(BattleResult, '__dataclass_fields__')`. Lines 76-109 verify ABC properties (importable, is_abstract, has_method, cannot_instantiate, incomplete_raises_TypeError). The BattleResult field tests (lines 31-65) and concrete implementation tests (lines 111-165) do exercise real API contracts and should be KEPT. Only the pure structural tests are scaffold.
- **Estimated LOC saved:** ~55

### A4. test_simulation_adapter.py — TestSimulationBattleResolverImplementation class
- **File:** `tests/unit/strategy/adapters/test_simulation_adapter.py`
- **Test(s):** `TestSimulationBattleResolverImplementation.test_implements_ibattle_resolver`, `TestSimulationBattleResolverImplementation.test_can_instantiate`, `TestSimulationBattleResolverImplementation.test_has_resolve_battle_method`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Lines 37-60: `test_implements_ibattle_resolver` checks `issubclass()`, `test_can_instantiate` checks `resolver is not None`, `test_has_resolve_battle_method` checks `hasattr(resolver, 'resolve_battle')`. The behavioral tests that follow actually call `resolve_battle`, which would fail if any of these conditions were false.
- **Estimated LOC saved:** 24

### A5. test_colonize_validator.py — Heavily redundant tests within the file
- **File:** `tests/unit/strategy/validation/test_colonize_validator.py`
- **Test(s):** Multiple near-duplicate tests across `TestColonizeValidatorColonyPods`, `TestColonizeValidatorAnyPlanetPods`, and `TestColonizeValidatorAdvancedEdgeCases` classes
- **Reason:** DUPLICATE_OF: same-file duplicates
- **Confidence:** HIGH
- **Evidence:** This 1,247-line test file tests 143 LOC of source code (colonize_validator.py) at 86% coverage. The file has extreme internal redundancy:
  - `test_validate_with_drop_pod_succeeds_any_planet_type` (line 414) and `test_validate_accepts_drop_pod` (line 438) and `test_drop_pod_validates` (line 981) and `test_any_planet_with_drop_pod_succeeds` (line 836) all test the same behavior: "fleet with drop pod can colonize planet."
  - `test_validate_allows_no_colony_pod_at_command_time` (line 461), `test_no_drop_pod_succeeds_at_command_time` (line 1003), `test_any_planet_without_drop_pod_succeeds_at_command_time` (line 856) all test: "validation passes without pods because pod check is deferred."
  - `test_validate_allows_overcommitted_pods_at_command_time` (line 538), `test_overcommit_succeeds_at_command_time` (line 951), `test_any_planet_exhausted_pods_fails` (line 878) all test: "overcommitted pods still succeed at command time."
  - `test_count_drop_pods` (line 484) and `test_count_drop_pods_multiple_ships` (line 497) test the same method with identical setup (both assert count == 2 with 2 ships each having 1 pod).
  - Each test class re-creates duplicate fixtures (`mock_component_registry`, `_make_planet`, `_make_ship_with_pod`) that are identical across classes.
  
  The source code's `validate()` method is only 40 lines of straightforward conditionals. The 1,247-line test file is ~8.7x the source, with ~50% of tests being semantic duplicates. Recommend consolidating to ~500 LOC.
- **Estimated LOC saved:** ~600 (consolidation target, not full removal)

---

## B. Tests That Are Happy-Path-Only

### B1. test_design_validator.py — Missing layer mass validation tests
- **File:** `tests/unit/strategy/services/test_design_validator.py`
- **Test(s):** `TestDesignValidator` (entire class, 89 LOC)
- **What's tested:** Empty design, missing components, missing crew housing, None input
- **What's missing:** 
  - Layer mass budget validation (`_check_layer_mass`, lines 138-197 — completely untested, accounts for 39 of the 39 missing lines)
  - Life support deficit error path (only crew housing tested)
  - Modifier multiplier effects on crew/mass calculations
  - Designs where vehicle class is not found in registry (line 149-150)
  - Components with formula-based CrewRequired (string `=` prefix, lines 114-116)
- **Source method(s) affected:** `design_validator.py:138-197` (`_check_layer_mass`), `design_validator.py:114-116` (formula CrewRequired)
- **Priority:** HIGH — The entire `_check_layer_mass` method (60 lines, 33% of file) is completely untested. This validates ship designs before build queue insertion; a bug here could allow invalid ships to be queued.

### B2. test_transfer_validator_robustness.py — Minimal transfer validator coverage
- **File:** `tests/unit/strategy/validation/test_transfer_validator_robustness.py`
- **Test(s):** `TestTransferValidatorRobustness` (69 LOC)
- **What's tested:** Fleet at correct/wrong system for planet transfers
- **What's missing:**
  - Fleet-to-fleet transfers (`_validate_fleet_transfer`, lines 120-151)
  - `_validate_load` for passengers: no population, species_id filtering (lines 191-220)
  - `_validate_unload` for passengers: no cargo to unload (lines 238-244)
  - Invalid direction, invalid cargo_type (lines 62-73)
  - Drop pod capacity validation (already covered in `test_transfer_drop_pod.py` but not robustness edge cases)
  - Projected cargo parameter (`projected_cargo` kwarg, used in `_validate_load` and `_validate_unload`)
  - Note: `test_transfer_drop_pod.py` covers drop_pod scenarios well (140 LOC), but general cargo/passenger paths have gaps
- **Source method(s) affected:** `transfer_validator.py:99-118` (fleet-to-fleet), `transfer_validator.py:130-151` (_validate_fleet_transfer), `transfer_validator.py:191-220` (_validate_load passengers)
- **Priority:** MEDIUM — Missing lines are 100-101, 105-106, 118, 130-137, 143-146, 151, 167, 182-183. The fleet-to-fleet transfer path is completely untested.

### B3. test_race_library.py — No error handling tests
- **File:** `tests/unit/strategy/systems/test_race_library.py`
- **Test(s):** All classes (335 LOC)
- **What's tested:** CRUD operations (save, load, list, delete), ID generation, slugify
- **What's missing:**
  - Corrupt JSON file handling (`get_all_races` lines 88-99 — JSONDecodeError, KeyError, PermissionError, OSError, AttributeError, TypeError, ValueError, ValidationException)
  - Error paths in `get_race` (lines 127-138 — same error types)
  - Error paths in `save_race` (lines 170-181 — PermissionError, OSError, ValidationException, AttributeError, KeyError)
  - Error paths in `delete_race` (lines 203-211 — PermissionError, OSError, RuntimeError)
  - `_ensure_folder_exists` error paths (lines 57-62 — PermissionError, OSError)
  - All 56 missing lines are error handling branches — the happy paths are well covered
- **Source method(s) affected:** `race_library.py:57-62,85-99,125-138,154,169-181,203-211`
- **Priority:** LOW — These are all exception-handling branches for filesystem operations. The happy paths work correctly. However, the coverage gap is large (57.6%) because these branches are numerous.

### B4. test_strategic_ability_scanner.py — Missing inactive component tests
- **File:** `tests/unit/strategy/services/test_strategic_ability_scanner.py`
- **Test(s):** All classes (266 LOC)
- **What's tested:** Finding abilities at planet/scope, aggregate multipliers
- **What's missing:**
  - Component-level activation state filtering (lines 215-237 — `is_component_active` checks in component iteration)
  - Abilities with missing `scope` field (line 158)
  - Design data with string component references instead of dicts (lines 182, 184, 186)
  - `find_abilities_at_planet` with `component_states` parameter exercised (line 166)
- **Source method(s) affected:** `strategic_ability_scanner.py:158,166,182-186,215-237`
- **Priority:** MEDIUM — The activation state filtering logic ensures inactive facility components don't contribute abilities; untested paths could cause phantom ability effects.

### B5. test_action_time_resolver.py — Missing ACTIVATE/DEACTIVATE ability tests
- **File:** `tests/unit/strategy/services/test_action_time_resolver.py`
- **Test(s):** All classes (282 LOC)
- **What's tested:** COLONIZE, superweapons, TRANSFER, MOVE, defaults, multiple ships
- **What's missing:**
  - `ACTIVATE_ABILITY` and `DEACTIVATE_ABILITY` order types (lines 83-92 — reads `activation_time`/`deactivation_time` from facility components)
  - Planet-scoped orders (`PLANET_ACTION_ORDER_TYPES` path, lines 104-108)
  - `_find_planet_ability_time` method (called for planet action orders)
  - Missing lines 89, 106, 162, 171 correspond to these untested branches
- **Source method(s) affected:** `action_time_resolver.py:83-92,104-108,162,171`
- **Priority:** MEDIUM — Planet ability activation/deactivation timing is untested; incorrect timing could cause abilities to take wrong number of turns.

---

## C. Source Code with Inadequate Coverage

### C1. planet_order_validator.py — 15.0% coverage (68 of 80 statements missing)
- **Source file:** `game/strategy/validation/planet_order_validator.py` (149 LOC)
- **Coverage:** 15.0% — Critically low. Only lines 12-15 (imports/module-level) and possibly the function signature hit.
- **Untested areas:**
  - `validate_activate_ability` (lines 37-77) — ENTIRELY untested. Validates facility existence, operational status, ability presence, component-key activation state, and order queue conflicts.
  - `validate_deactivate_ability` (lines 91-127) — ENTIRELY untested. Mirror of activate with deactivation-specific checks.
  - `_facility_has_ability` (lines 136-149) — ENTIRELY untested. Helper to check if a facility design has a specific ability.
- **Risk:** HIGH — This is the single point of validation for planet ability orders. Without tests, any refactoring could silently break planet facility activation/deactivation order validation, allowing invalid orders to be queued.
- **Priority:** HIGH — 0% method coverage on a validator class that guards planet order queuing.

### C2. fleet_cargo_projector.py — 42.3% coverage (15 of 26 statements missing)
- **Source file:** `game/strategy/services/fleet_cargo_projector.py` (64 LOC)
- **Coverage:** 42.3% — The `get_projected_cargo` method body (lines 42-61) is entirely untested.
- **Untested areas:**
  - The entire order-walking loop (lines 41-61) that projects cargo after queued orders
  - Load direction projection (line 54-57)
  - Unload direction projection (lines 58-61)
  - Handling of 0-amount (fill to capacity / unload all)
  - Non-matching cargo type filtering (lines 47-49)
  - Non-dict `params` filtering (line 44-45)
- **Risk:** HIGH — This is used by the TransferValidator to determine if a fleet will have enough cargo space after earlier queued orders execute. A bug here means the UI might allow queueing impossible transfer chains.
- **Priority:** HIGH — Zero tests for the core projection logic.

### C3. race_library.py — 57.6% coverage (56 of 132 statements missing)
- **Source file:** `game/strategy/systems/race_library.py` (255 LOC)
- **Coverage:** 57.6% — All error handling branches untested (see B3 above).
- **Untested areas:** All exception handling in `get_all_races`, `get_race`, `save_race`, `delete_race`, `_ensure_folder_exists`. Missing lines: 57-62, 85-99, 125-138, 154, 169-181, 203-211, 252.
- **Risk:** LOW — The untested code is entirely exception handling for filesystem errors. Happy paths are well tested. In practice, these branches only fire on disk failures.
- **Priority:** LOW

### C4. design_validator.py — 67.2% coverage (39 of 119 statements missing)
- **Source file:** `game/strategy/services/design_validator.py` (197 LOC)
- **Coverage:** 67.2% — The entire `_check_layer_mass` method (lines 138-197) is untested.
- **Untested areas:**
  - `_check_layer_mass` (lines 138-197): Validates component mass per layer against vehicle class limits. Handles both dict and object class definitions, list and dict layer formats, modifier multipliers for mass.
  - Line 31: `add_warning` method (called but only from `_check_layer_mass`)
  - Line 94: Early return when `comp_def` is None inside `_check_crew_and_life_support`
- **Risk:** MEDIUM — Mass budget validation prevents over-mass designs from entering build queues. Without tests, a ship design exceeding layer mass limits could be accepted silently.
- **Priority:** HIGH — A design validator with 33% of its validation logic untested is a significant gap.

### C5. component_inspector.py — 82.5% coverage (18 of 103 statements missing)
- **Source file:** `game/strategy/services/component_inspector.py` (335 LOC)
- **Coverage:** 82.5% — Missing lines: 73-78 (dict component with registry lookup), 89-91 (_get_component_registry with dict registries), 106, 125, 127, 167, 299, 330-333.
- **Untested areas:**
  - `extract_abilities_from_component` fallback paths: string component entries, dict components requiring registry lookup
  - `_get_component_registry` dict-input branch (line 89-90)
  - Several helper functions at lines 299, 330-333
- **Risk:** LOW — Most usage goes through the primary paths which are tested.
- **Priority:** LOW

---

## D. Cross-Domain Observations

### D1. Colonize validator test-to-source ratio (8.7:1) warrants consolidation
The `test_colonize_validator.py` (1,247 lines) tests `colonize_validator.py` (143 lines) at an 8.7:1 ratio. This is significantly higher than any other validator in the codebase. The colonize validator's `validate()` method was simplified in "Phase 3" to defer pod checks to execution time, making many tests semantically identical (all asserting `is_valid is True` for variations of "fleet can colonize planet"). Each of the 3 later test classes re-creates its own nearly identical fixture methods. A consolidation pass could reduce this to ~500 lines with no loss of coverage or regression protection. The redundancy is an active maintenance burden — anyone modifying colonize validation must update ~30 tests that all assert the same thing.

### D2. Interface tests overlap with engine inheritance tests
`test_engine_interfaces.py` (476 LOC) and `test_engine_inheritance.py` (57 LOC) both verify interface contracts. The inheritance file does the job more efficiently: it checks that all 12 concrete engines are `issubclass` of their interface ABCs, which implicitly proves the ABCs exist, are importable, and define abstract methods. The interface file's tests are entirely redundant with this plus the behavioral tests in the engine test files. This affects the Session 2 engine domain as well.

### D3. Planet order validator is a critical gap affecting UI tests
The `PlanetOrderValidator` at 15% coverage is called from UI-layer planet interaction screens. If any Session 3 (UI) agent finds planet ability activation/deactivation tests, they likely mock this validator. The lack of unit tests on the validator itself means the actual validation logic is only exercised through integration paths (if any exist). This is a cross-cutting risk.

### D4. FleetCargoProjector at 42% coverage affects transfer validation chain
`FleetCargoProjector.get_projected_cargo()` is called by the transfer validation system to project future cargo state. The `TransferValidator._validate_load` accepts a `projected_cargo` parameter (tested in `test_transfer_drop_pod.py`), but the projector that computes that value is itself untested. This means the full transfer-order-chaining feature (queue load + unload in sequence) has no unit test coverage on the projection side. Any agent reviewing the transfer or order-chaining systems should note this gap.
