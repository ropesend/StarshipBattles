# Test Review Report: Colonization + Superweapons Cross-Domain Dedup

## Scope
- Source files reviewed:
  - `game/simulation/components/abilities/colonize.py` (82 lines)
  - `game/strategy/validation/colonize_validator.py` (143 lines)
  - `game/strategy/engine/order_processor.py` (779 lines)
  - `game/strategy/engine/command_handlers.py` (1062 lines)
  - `game/ui/screens/strategy_colonization.py` (274 lines)
  - `game/simulation/components/abilities/superweapons.py` (115 lines)
  - `game/strategy/validation/superweapon_validator.py` (276 lines)
  - `game/strategy/engine/superweapon_order_processor.py` (797 lines)
  - `game/strategy/engine/superweapon_command_handlers.py` (372 lines)
  - `game/ui/screens/strategy_superweapons.py` (398 lines)
- Test files reviewed:
  - `tests/integration/colonization/test_validation.py` (86 lines)
  - `tests/integration/colonization/test_execution.py` (170 lines)
  - `tests/integration/colonization/test_edge_cases.py` (197 lines)
  - `tests/integration/colonization/test_explicit_orders.py` (104 lines)
  - `tests/integration/colonization/test_planet_specific_colonization.py` (695 lines)
  - `tests/integration/colonization/conftest.py` (143 lines)
  - `tests/unit/strategy/engine/test_process_colonize_validation.py` (428 lines)
  - `tests/unit/strategy/engine/test_process_colonize_cargo.py` (219 lines)
  - `tests/unit/strategy/engine/test_colonize_mission_handler.py` (267 lines)
  - `tests/unit/strategy/engine/test_colonize_population.py` (342 lines)
  - `tests/unit/strategy/engine/test_multi_pod_colonization.py` (141 lines)
  - `tests/unit/strategy/engine/test_population_seeding.py` (154 lines)
  - `tests/unit/strategy/validation/test_colonize_validator.py` (1247 lines)
  - `tests/unit/strategy/engine/test_pod_transfer.py` (192 lines)
  - `tests/unit/strategy/validation/test_transfer_drop_pod.py` (140 lines)
  - `tests/integration/strategy/test_colonize_logic.py` (321 lines)
  - `tests/integration/gameplay_loop/test_commands_colonization.py` (292 lines)
  - `tests/unit/abilities/test_colonize_planet.py` (195 lines)
  - `tests/unit/simulation/components/abilities/test_colonize_harvester.py` (626 lines)
  - `tests/unit/ui/screens/test_strategy_colonization.py` (102 lines)
  - `tests/integration/ui/test_colonization_facade.py` (836 lines)
  - `tests/unit/strategy/engine/test_superweapon_edge_cases.py` (727 lines)
  - `tests/unit/strategy/engine/test_superweapon_order_processor.py` (1212 lines)
  - `tests/unit/strategy/engine/test_superweapon_handler_validation.py` (459 lines)
  - `tests/unit/strategy/engine/test_superweapon_command_handlers.py` (618 lines)
  - `tests/unit/strategy/engine/test_superweapon_stabilizers.py` (77 lines)
  - `tests/unit/strategy/data/test_superweapon_orders.py` (292 lines)
  - `tests/unit/strategy/validation/test_superweapon_validator.py` (650 lines)
  - `tests/unit/simulation/components/abilities/test_superweapons.py` (171 lines)
  - `tests/integration/strategy/test_superweapon_integration.py` (621 lines)
  - `tests/unit/ui/test_superweapon_operations.py` (393 lines)
  - `tests/unit/ui/screens/test_superweapon_input_modes.py` (228 lines)
  - `tests/unit/ui/screens/test_strategy_superweapons.py` (544 lines)
- Coverage data referenced: no

## Summary
- Test files reviewed: 33 (12,889 LOC total)
- Source files reviewed: 10 (4,298 LOC total)
- Tests flagged for removal: 16 (estimated LOC: 740)
- Tests flagged as happy-path-only: 2
- Source files with inadequate coverage: 0

## A. Tests Recommended for Removal

### Colonization Duplicates

1. **File:** `tests/unit/strategy/engine/test_process_colonize_cargo.py`
   **Test(s):** `TestProcessColonizeCargo::test_colonize_universal_drop_pod_succeeds` (lines 173-193)
   **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_process_colonize_validation.py::TestProcessColonizeValidation::test_process_colonize_universal_drop_pod_succeeds`
   **Confidence:** HIGH
   **Evidence:** Both tests create a fleet with a CONTINENTAL drop pod at an ICE_DWARF planet and assert `result.colonized is True`. The validation file's version (lines 175-206) and the cargo file's version (lines 173-193) are structurally identical -- same setup, same assertion. The cargo file tests OrderProcessor.process_colonize() with universal pods, as does the validation file.
   **Estimated LOC saved:** 20

2. **File:** `tests/unit/strategy/engine/test_process_colonize_cargo.py`
   **Test(s):** `TestProcessColonizeCargo::test_colonize_any_planet_picks_first_unowned` (lines 195-219)
   **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_process_colonize_validation.py::TestProcessColonizeAnyPlanet::test_any_planet_selects_first_unowned`
   **Confidence:** HIGH
   **Evidence:** Both tests create two planets (CONTINENTAL + ICE_DWARF) at same location, fleet with drop pod, COLONIZE target=None, and assert the first unowned planet (continental) gets colonized. The validation file's version (lines 359-391) and cargo file's version (lines 195-219) verify the exact same behavior of process_colonize().
   **Estimated LOC saved:** 25

3. **File:** `tests/unit/strategy/engine/test_process_colonize_cargo.py`
   **Test(s):** `TestProcessColonizeCargo::test_colonize_ship_stays_in_fleet` (lines 134-152), `test_colonize_fleet_not_removed` (lines 154-170)
   **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_colonize_population.py::TestExistingColonizationBehavior::test_colonize_ship_stays_in_fleet`
   **Confidence:** HIGH
   **Evidence:** Both files test that after process_colonize(), the colony ship remains in fleet.ships and the fleet remains in empire.fleets. The population file (lines 313-342) tests this at the same abstraction level (unit test of OrderProcessor.process_colonize). The cargo file's two tests (lines 134-170) split the same assertion into two tests. These are also duplicated by integration tests in test_planet_specific_colonization.py::TestFleetRemovalBehavior.
   **Estimated LOC saved:** 40

4. **File:** `tests/integration/colonization/test_execution.py`
   **Test(s):** `TestColonizationExecution::test_colonize_transfers_ownership` (lines 20-35), `test_colonize_adds_to_colonies` (lines 37-48), `test_colonize_fleet_stays` (lines 50-61)
   **Reason:** DUPLICATE_OF:`tests/integration/gameplay_loop/test_commands_colonization.py::TestColonizationWorkflow::test_colonize_order_claims_planet` and `test_colonize_removes_fleet`
   **Confidence:** MEDIUM
   **Evidence:** test_execution.py lines 20-61 test colonize through turn_engine.process_turn and assert ownership transfer, colony list growth, and fleet persistence. test_commands_colonization.py lines 222-292 tests the identical flow (fleet at planet, issue COLONIZE order, call process_turn, assert planet.owner_id and empire.colonies). The difference is test_execution uses a dedicated colonization conftest while test_commands_colonization uses the gameplay_loop conftest. Both are integration tests of the same turn_engine.process_turn colonization path.
   **Estimated LOC saved:** 45

5. **File:** `tests/integration/colonization/test_validation.py`
   **Test(s):** `TestColonizationValidation::test_validate_colonize_unowned_planet` (line 18), `test_validate_colonize_owned_planet_fails` (line 27), `test_validate_colonize_wrong_location_fails` (line 40), `test_validate_colonize_any_planet` (line 64), `test_validate_colonize_no_fleet_fails` (line 75)
   **Reason:** DUPLICATE_OF:`tests/unit/strategy/validation/test_colonize_validator.py::TestColonizeValidatorBasic` and `TestColonizeValidatorAnyPlanet`
   **Confidence:** HIGH
   **Evidence:** The integration test_validation.py (86 lines) calls turn_engine.validate_colonize_order() which delegates to ColonizeValidator.validate(). The unit test file test_colonize_validator.py tests ColonizeValidator.validate() directly with the same 5 scenarios: unowned planet succeeds (line 82), owned planet fails (line 98), wrong location fails (line 111), any planet success (line 132), no fleet fails (line 73). The integration wrapper adds no additional value because validate_colonize_order is a thin passthrough.
   **Estimated LOC saved:** 86

6. **File:** `tests/integration/strategy/test_colonize_logic.py`
   **Test(s):** `TestColonizePodCargoConsumption::test_colonize_consumes_pod_from_cargo_ship_stays` (lines 222-258), `test_colonize_single_ship_fleet_stays` (lines 260-285), `test_colonize_consumes_one_drop_pod` (lines 287-321)
   **Reason:** DUPLICATE_OF:`tests/integration/colonization/test_planet_specific_colonization.py::TestColonizeWithMatchingPod::test_colonize_with_matching_pod_succeeds` and `TestFleetRemovalBehavior`
   **Confidence:** HIGH
   **Evidence:** test_colonize_logic.py::TestColonizePodCargoConsumption (lines 222-321, ~100 LOC) tests the same behaviors as test_planet_specific_colonization.py: pod consumed from carried_items, both ships stay in fleet, fleet stays in empire. Both call OrderProcessor.process_colonize() directly with MockGalaxy/MockPlanet at the same abstraction level. test_planet_specific_colonization.py has more thorough coverage (matching pods, chain colonization, UI filtering).
   **Estimated LOC saved:** 100

7. **File:** `tests/integration/strategy/test_colonize_logic.py`
   **Test(s):** `test_colonize_specific_success_at_exact_location` (line 111), `test_colonize_any_success_at_location` (line 150), `test_colonize_specific_fail_owned` (line 181), `test_colonize_any_fail_no_candidates` (line 168)
   **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_process_colonize_validation.py` + `tests/unit/strategy/validation/test_colonize_validator.py`
   **Confidence:** MEDIUM
   **Evidence:** These 4 tests (lines 111-195) exercise execute_action_order -> process_colonize, testing the same validations (specific planet success, any planet success, owned planet fails, no candidates) that are already covered in both the unit validation test and the process_colonize unit test. The test_colonize_logic.py file uses nearly identical mock setup (MockGalaxy, MockPlanet, MockSystem).
   **Estimated LOC saved:** 85

8. **File:** `tests/unit/abilities/test_colonize_planet.py`
   **Test(s):** `TestColonizePlanetAbility` (entire class, lines 30-157) and `TestColonizePlanetRegistration` (lines 159-195)
   **Reason:** DUPLICATE_OF:`tests/unit/simulation/components/abilities/test_colonize_harvester.py::TestColonizePlanet`
   **Confidence:** HIGH
   **Evidence:** test_colonize_planet.py::TestColonizePlanetAbility tests: string shorthand (line 62), dict format (line 61), layer is STRATEGIC (line 40), scope is SELF (lines 47, 53), UI rows formatting (lines 80-109), all 11 planet types (line 111), reject invalid scope (line 131), primary value returns 0 (line 140). test_colonize_harvester.py::TestColonizePlanet tests the same: string shorthand (line 39), dict format (line 47), layer is strategic (line 65), scope is self (line 73), UI rows formatting (lines 92-118), all planet types (line 120), reject invalid scope (line 136), primary value returns 0 (line 86). Both import ColonizePlanet directly and test the ability class in isolation. The only unique test in test_colonize_planet.py is `test_colonize_planet_in_all_exports` (line 191), which could be folded into test_colonize_harvester.py.
   **Estimated LOC saved:** 180

### Superweapon Duplicates

9. **File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
   **Test(s):** `TestImplodePlanetCommandHandler::test_execute_fails_when_fleet_not_found` (line 102), same pattern for Stellerate (line 171), OpenWarp, CloseWarp, CreateDyson, SelfDestruct
   **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_superweapon_edge_cases.py::TestMissionHandlerNotFound`
   **Confidence:** MEDIUM
   **Evidence:** test_superweapon_command_handlers.py tests fleet-not-found for each direct handler (6 tests, ~30 LOC each). test_superweapon_edge_cases.py tests fleet-not-found for each mission handler (5 tests, lines 185-271). These test the same "fleet not found" error path but at two different entry points (direct handler vs mission handler). While the code paths differ slightly, the mock setup and assertions are nearly identical. These are genuinely different code paths, so the recommendation is weaker.
   **Estimated LOC saved:** 0 (genuinely different concerns -- keep both)

10. **File:** `tests/unit/strategy/engine/test_superweapon_handler_validation.py`
    **Test(s):** `TestImplodePlanetCommandHandlerPassesRegistry::test_rejects_fleet_without_destroy_planet_ability` (line 104), and identical pattern for all 5 superweapon types
    **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_superweapon_command_handlers.py::TestImplodePlanetCommandHandler::test_execute_fails_when_validation_fails`
    **Confidence:** HIGH
    **Evidence:** test_superweapon_handler_validation.py has 10 "rejects fleet without ability" tests (2 per superweapon type: direct + mission). test_superweapon_command_handlers.py has the same "validation fails" tests for direct handlers. Both mock SuperweaponValidator.find_ship_with_ability to return None and assert result.is_valid is False with the ability name in the message. The handler_validation file's unique value is only the "passes component_registry" tests (10 tests verifying kwargs). The "rejects" tests (10 tests) are pure duplicates.
    **Estimated LOC saved:** 100

11. **File:** `tests/unit/ui/test_superweapon_operations.py`
    **Test(s):** `TestSuperweaponOperationsInit::test_init_stores_references` (line 65)
    **Reason:** DUPLICATE_OF:`tests/unit/ui/screens/test_strategy_superweapons.py::TestSuperweaponOperationsInit::test_init_stores_references` (line 65)
    **Confidence:** HIGH
    **Evidence:** Both files define a `TestSuperweaponOperationsInit` class with a `test_init_stores_references` test that creates a SuperweaponOperations(scene, facade) and asserts ops.scene is scene and ops.facade is facade. Identical assertion, identical test name, identical class name. test_superweapon_operations.py (line 65-71) and test_strategy_superweapons.py (line 65-71).
    **Estimated LOC saved:** 10

12. **File:** `tests/unit/ui/test_superweapon_operations.py`
    **Test(s):** `TestSuperweaponOperationsInit::test_properties_delegate_to_scene` (approx line 75)
    **Reason:** DUPLICATE_OF:`tests/unit/ui/screens/test_strategy_superweapons.py::TestPropertyAccessors`
    **Confidence:** HIGH
    **Evidence:** Both files test that SuperweaponOperations properties (systems, camera, hex_size, galaxy) delegate to scene attributes. test_superweapon_operations.py and test_strategy_superweapons.py have overlapping property accessor tests. The file at `tests/unit/ui/test_superweapon_operations.py` appears to be an older version that was superseded by the more organized `tests/unit/ui/screens/test_strategy_superweapons.py`.
    **Estimated LOC saved:** 49

**Total estimated LOC for removal: ~740**

## B. Tests That Are Happy-Path-Only

1. **File:** `tests/integration/colonization/test_execution.py`
   **Test(s):** `TestColonizationWithMovement::test_colonize_at_destination_not_start` (line 125)
   **Note:** This test has a conditional `if fleet in empire.fleets and fleet.location != target_loc:` guard that can silently pass without verifying anything if the fleet arrives in 1 turn.

2. **File:** `tests/integration/colonization/test_edge_cases.py`
   **Test(s):** `TestColonizationEdgeCases::test_colonize_two_empires_race` (line 37)
   **Note:** This test asserts `owner_count <= 1` which means it passes even if neither empire colonized (both destroyed in combat or nothing happened). A stronger test would assert exactly one owner or exactly zero with a documented reason.

## C. Source Code with Inadequate Coverage
(N/A for dedup agent)

## D. Cross-Domain Observations

1. **Massive colonization helper duplication across files.** The `make_colony_ship()` helper function is defined independently in 7 different test files with nearly identical implementations: `test_process_colonize_validation.py` (line 84), `test_process_colonize_cargo.py` (line 47), `test_colonize_mission_handler.py` (line 17), `test_planet_specific_colonization.py` (line 104), `test_colonize_logic.py` (line 65), `test_commands_colonization.py` (line 18), and `integration/colonization/conftest.py` (line 41). These should be consolidated into a shared fixture.

2. **MockGalaxy/MockSystem/MockPlanet duplication.** The same mock classes are defined in at least 5 different test files for colonization alone. A shared conftest with these mocks would eliminate ~200 lines of duplicated setup code.

3. **test_superweapon_operations.py appears to be a superseded file.** The file at `tests/unit/ui/test_superweapon_operations.py` (393 lines) tests `SuperweaponOperations` at a less organized level than `tests/unit/ui/screens/test_strategy_superweapons.py` (544 lines). The screens/ version has the same tests plus additional coverage. The older file should be evaluated for full removal.

4. **No cross-domain overlap between colonization and superweapon tests.** These two feature domains are cleanly separated with no test files testing both features simultaneously.

## E. Dedup Map

### Behavior: "Colonization transfers planet ownership to empire"
- **Test locations:**
  - `tests/integration/colonization/test_execution.py:TestColonizationExecution:test_colonize_transfers_ownership` (via turn_engine.process_turn)
  - `tests/integration/gameplay_loop/test_commands_colonization.py:TestColonizationWorkflow:test_colonize_order_claims_planet` (via turn_engine.process_turn)
  - `tests/integration/strategy/test_colonize_logic.py:test_colonize_specific_success_at_exact_location` (via OrderProcessor.execute_action_order)
  - `tests/integration/colonization/test_planet_specific_colonization.py:TestColonizeWithMatchingPod:test_colonize_with_matching_pod_succeeds` (via OrderProcessor.process_colonize)
  - `tests/unit/strategy/engine/test_process_colonize_validation.py:TestProcessColonizeValidation:test_process_colonize_correct_pod_type_succeeds` (via OrderProcessor.process_colonize)
  - `tests/unit/strategy/engine/test_colonize_population.py:TestExistingColonizationBehavior:test_colonize_still_assigns_ownership` (via OrderProcessor.process_colonize)
- **Recommendation:** Keep `test_process_colonize_validation.py` (unit, direct OrderProcessor test), `test_planet_specific_colonization.py` (integration, pod-type-specific), and `test_commands_colonization.py` (gameplay loop integration). Remove `test_execution.py::test_colonize_transfers_ownership`, `test_colonize_logic.py::test_colonize_specific_success_at_exact_location`, and `test_colonize_population.py::test_colonize_still_assigns_ownership`.

### Behavior: "Colony ship/fleet stays after colonization (Phase 2 reusable ships)"
- **Test locations:**
  - `tests/integration/colonization/test_execution.py:TestColonizationExecution:test_colonize_fleet_stays`
  - `tests/integration/colonization/test_planet_specific_colonization.py:TestFleetRemovalBehavior:test_last_ship_colonization_fleet_stays`
  - `tests/integration/colonization/test_planet_specific_colonization.py:TestFleetRemovalBehavior:test_partial_fleet_colonization_preserves_fleet`
  - `tests/integration/strategy/test_colonize_logic.py:TestColonizePodCargoConsumption:test_colonize_consumes_pod_from_cargo_ship_stays`
  - `tests/integration/strategy/test_colonize_logic.py:TestColonizePodCargoConsumption:test_colonize_single_ship_fleet_stays`
  - `tests/unit/strategy/engine/test_process_colonize_cargo.py:TestProcessColonizeCargo:test_colonize_ship_stays_in_fleet`
  - `tests/unit/strategy/engine/test_process_colonize_cargo.py:TestProcessColonizeCargo:test_colonize_fleet_not_removed`
  - `tests/unit/strategy/engine/test_colonize_population.py:TestExistingColonizationBehavior:test_colonize_ship_stays_in_fleet`
  - `tests/integration/gameplay_loop/test_commands_colonization.py:TestColonizationWorkflow:test_colonize_removes_fleet` (verifies fleet count unchanged)
- **Recommendation:** Keep `test_planet_specific_colonization.py::TestFleetRemovalBehavior` (most thorough, single-ship and multi-ship variants). Remove the 7 other duplicates.

### Behavior: "Universal drop pod succeeds on any planet type"
- **Test locations:**
  - `tests/unit/strategy/engine/test_process_colonize_validation.py:TestProcessColonizeValidation:test_process_colonize_universal_drop_pod_succeeds`
  - `tests/unit/strategy/engine/test_process_colonize_cargo.py:TestProcessColonizeCargo:test_colonize_universal_drop_pod_succeeds`
  - `tests/unit/strategy/engine/test_colonize_mission_handler.py:TestColonizeMissionHandlerPodValidation:test_mission_accepts_universal_drop_pod`
- **Recommendation:** Keep `test_process_colonize_validation.py` (tests OrderProcessor directly) and `test_colonize_mission_handler.py` (tests mission handler layer). Remove `test_process_colonize_cargo.py::test_colonize_universal_drop_pod_succeeds`.

### Behavior: "Any planet colonization picks first unowned planet"
- **Test locations:**
  - `tests/unit/strategy/engine/test_process_colonize_validation.py:TestProcessColonizeAnyPlanet:test_any_planet_selects_first_unowned`
  - `tests/unit/strategy/engine/test_process_colonize_cargo.py:TestProcessColonizeCargo:test_colonize_any_planet_picks_first_unowned`
  - `tests/integration/strategy/test_colonize_logic.py:test_colonize_any_success_at_location`
  - `tests/integration/colonization/test_validation.py:TestColonizationValidation:test_validate_colonize_any_planet`
  - `tests/unit/strategy/validation/test_colonize_validator.py:TestColonizeValidatorAnyPlanet:test_validate_any_planet_success`
- **Recommendation:** Keep `test_process_colonize_validation.py` (execution-level unit) and `test_colonize_validator.py` (validation-level unit). Remove the other 3.

### Behavior: "Colonize validation: unowned planet succeeds, owned fails, wrong location fails, no fleet fails"
- **Test locations:**
  - `tests/integration/colonization/test_validation.py:TestColonizationValidation` (5 tests, via turn_engine.validate_colonize_order)
  - `tests/unit/strategy/validation/test_colonize_validator.py:TestColonizeValidatorBasic` (3 tests, via ColonizeValidator.validate directly)
  - `tests/unit/strategy/validation/test_colonize_validator.py:TestColonizeValidatorAnyPlanet` (3 tests)
- **Recommendation:** Keep `test_colonize_validator.py` (direct unit test of the validator). Remove `tests/integration/colonization/test_validation.py` entirely (thin passthrough adds no value).

### Behavior: "ColonizePlanet ability class: string/dict init, layer, scope, UI rows, all planet types"
- **Test locations:**
  - `tests/unit/abilities/test_colonize_planet.py:TestColonizePlanetAbility` (14 tests)
  - `tests/unit/simulation/components/abilities/test_colonize_harvester.py:TestColonizePlanet` (13 tests)
- **Recommendation:** Keep `test_colonize_harvester.py::TestColonizePlanet` (more thorough, includes action_time tests and edge cases like empty dict, non-dict data). Remove `test_colonize_planet.py` and fold its unique `test_colonize_planet_in_all_exports` into test_colonize_harvester.py.

### Behavior: "Drop pod consumed from carried_items during colonization"
- **Test locations:**
  - `tests/unit/strategy/engine/test_process_colonize_cargo.py:TestProcessColonizeCargo:test_colonize_consumes_drop_pod`
  - `tests/integration/colonization/test_planet_specific_colonization.py:TestColonizeWithMatchingPod:test_colonize_with_matching_pod_succeeds` (asserts drop_pods == 0)
  - `tests/integration/strategy/test_colonize_logic.py:TestColonizePodCargoConsumption:test_colonize_consumes_one_drop_pod`
  - `tests/unit/strategy/engine/test_colonize_population.py:TestExistingColonizationBehavior:test_colonize_ship_stays_in_fleet` (asserts drop_pods == 0)
- **Recommendation:** Keep `test_process_colonize_cargo.py::test_colonize_consumes_drop_pod` (focused unit test) and `test_colonize_logic.py::test_colonize_consumes_one_drop_pod` (tests consuming exactly one of two pods). Remove the other 2.

### Behavior: "SuperweaponOperations init stores scene/facade references"
- **Test locations:**
  - `tests/unit/ui/test_superweapon_operations.py:TestSuperweaponOperationsInit:test_init_stores_references`
  - `tests/unit/ui/screens/test_strategy_superweapons.py:TestSuperweaponOperationsInit:test_init_stores_references`
- **Recommendation:** Keep `tests/unit/ui/screens/test_strategy_superweapons.py` (more comprehensive file). Evaluate removing entire `tests/unit/ui/test_superweapon_operations.py` if all its tests are covered by the screens/ version.

### Behavior: "Superweapon command handler rejects fleet without required ability"
- **Test locations:**
  - `tests/unit/strategy/engine/test_superweapon_command_handlers.py` (6 direct handler tests)
  - `tests/unit/strategy/engine/test_superweapon_handler_validation.py` (10 "rejects" tests -- 5 direct + 5 mission)
- **Recommendation:** The handler_validation file's "rejects" tests for direct handlers (5 tests) duplicate the command_handlers file's "validation fails" tests. Keep command_handlers file (original, tests order creation too). Keep handler_validation file's mission handler rejection tests (5 tests) and "passes component_registry" tests (10 tests) as genuinely unique. Remove the 5 direct handler "rejects" tests from handler_validation.

### Superweapon Tests: No Duplicates Found (Genuinely Different Concerns)
The following superweapon test files test cleanly separated concerns with no meaningful overlap:
- `test_superweapon_orders.py` -- Data layer: OrderType enum values, FleetOrder serialization/deserialization, command dataclass structure
- `test_superweapon_validator.py` -- Validation layer: SuperweaponValidator static methods
- `test_superweapon_command_handlers.py` -- Handler layer: command handler wiring, order creation
- `test_superweapon_handler_validation.py` -- Handler layer: component_registry passthrough (except for "rejects" duplication noted above)
- `test_superweapon_order_processor.py` -- Execution layer: SuperweaponOrderProcessor methods
- `test_superweapon_edge_cases.py` -- Execution layer: error paths, mission move helper, colony removal
- `test_superweapon_stabilizers.py` -- Execution layer: stabilizer check unification
- `test_superweapons.py` (abilities) -- Simulation layer: ability class instantiation, layer/scope
- `test_superweapon_integration.py` -- End-to-end: full workflows through real objects
- `test_superweapon_input_modes.py` -- UI layer: input mode transitions
- `test_strategy_superweapons.py` -- UI layer: SuperweaponOperations command dispatch
