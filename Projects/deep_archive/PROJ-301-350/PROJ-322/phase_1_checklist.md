# Phase 1: CAT-4 Duplicate Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-322 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate the 19 verified CAT-4 duplicate tests identified by review `2026-05-02_204633_test-review`.

---

## Tasks

### Task 1.1: Merge beam-weapon binding tests into weapon-ability bindings [Medium]
**File:** `tests/unit/modifiers/test_beam_weapon_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_beam_weapon_bindings.py tests/unit/modifiers/test_weapon_ability_bindings.py`

- [x] Verify `test_weapon_ability_bindings.py` shares compatible fixtures/conftest with `test_beam_weapon_bindings.py`. If not, migrate the shared fixture to parent conftest first.
- [x] S11-CAT4-002: collapse the 3-class structure (lines 1-123) into `test_weapon_ability_bindings.py` as additional parametrized cases or a child class; only the `accuracy_add` binding differs.
- [x] Verify: `pytest tests/unit/modifiers/test_weapon_ability_bindings.py` passes; LOC delta approximately -123

---

### Task 1.2: Remove redundant seeker-weapon recalculate tests [Medium]
**File:** `tests/unit/modifiers/test_seeker_weapon_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_seeker_weapon_bindings.py tests/unit/modifiers/test_weapons_isolation.py`

- [x] S09-CAT4-002: remove the 4 individual recalculate tests at lines 100-193 that duplicate the consolidated coverage in `test_weapons_isolation.py:1011-1026`.
- [x] Verify: `pytest tests/unit/modifiers/test_weapons_isolation.py` passes; LOC delta approximately -94

---

### Task 1.3: Remove deprecated static-method modifier-manager class [Simple]
**File:** `tests/unit/simulation/components/test_modifier_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_manager.py`

- [x] S02-CAT4-001: remove `TestModifierManagerStandalone` (lines 140-177); the deprecated static method wrappers are already covered by instance method tests.
- [x] Verify: `pytest tests/unit/simulation/components/test_modifier_manager.py` passes; LOC delta approximately -38

---

### Task 1.4: De-duplicate ship-derelict status coverage [Simple]
**File:** `tests/unit/simulation/entities/test_ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship.py tests/unit/simulation/test_combat.py`

- [x] S09-CAT4-001: keep the entity-level derelict tests in `test_ship.py` (lines 163-194); remove the duplicated three-step coverage from `tests/unit/simulation/test_combat.py:98-122`.
- [x] Verify: `pytest tests/unit/simulation/entities/test_ship.py tests/unit/simulation/test_combat.py` passes; LOC delta approximately -32

---

### Task 1.5: Move BattleRunner DI helpers into shared conftest [Medium]
**File:** `tests/unit/simulation/test_battle_runner_di.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py tests/unit/simulation/test_battle_runner_di.py`

- [x] S09-CAT4-003: move byte-identical `_make_ship_spec` / `_make_team` helpers (lines 52-100) into `tests/unit/simulation/conftest.py` with class scope; reference from both `test_battle_runner.py` and `test_battle_runner_di.py`.
- [x] Verify: `pytest tests/unit/simulation/test_battle_runner.py tests/unit/simulation/test_battle_runner_di.py` passes; LOC delta approximately -49 (overlaps with HLP-002 in Phase 6 - keep in sync)

---

### Task 1.6: Refactor battle-resolver private-attr asserts to public API [Medium]
**File:** `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py`

- [x] S06-CAT4-001: rewrite `test_mock_resolver_enables_unit_testing` (lines 69-107) to drive the BattleResolver public API and assert on observable engine state instead of `_empires`/`_combats_resolved`/`_fleets_destroyed` private attrs.
- [x] Verify: `pytest tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` passes; LOC delta approximately -39 (overlaps with APC-003-F05 in Phase 5 - keep in sync)

---

### Task 1.7: Parametrize the 6 component-state field-deletion tests [Simple]
**File:** `tests/unit/strategy/data/test_battle_state_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_battle_state_validation.py`

- [x] S08-CAT4-002: collapse the 6 field-deletion tests in `TestComponentStateValidation` (lines 39-101) into a single `@pytest.mark.parametrize('field', [...])` test.
- [x] Verify: `pytest tests/unit/strategy/data/test_battle_state_validation.py` passes; LOC delta approximately -50

---

### Task 1.8: Keep colony-species edge-case tests as distinct [Simple]
**File:** `tests/unit/strategy/data/test_colony_species_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_colony_species_config.py`

- [x] S08-CAT4-003 (NEEDS_REWORK): KEEP the 5 `TestLastFoodRatioAggregation` tests (lines 76-118); they cover distinct MIN-aggregation edge cases (single-resource pass-through, multi-resource min, zero-collapses, all-ones, empty-dict-returns-1). Add a brief docstring/note to each making the edge case explicit. _(verification adjusted from review's "Parametrize the 5 duplicate tests" - see verification_report.md)_
- [x] Add a one-line docstring to each of the 5 tests naming its specific edge case:
   1. single-resource pass-through
   2. multi-resource MIN aggregation
   3. zero-collapses-to-zero
   4. all-ones-yields-one
   5. empty-dict-defaults-to-1
- [x] Verify: `pytest tests/unit/strategy/data/test_colony_species_config.py` passes; LOC delta approximately 0 (documentation only)

---

### Task 1.9: Parametrize Planet/Fleet construction-queue paused tests [Medium]
**File:** `tests/unit/strategy/data/test_construction_queue_paused_persistence.py`
**Tests:** `pytest tests/unit/strategy/data/test_construction_queue_paused_persistence.py`

- [x] S04-CAT4-001: collapse `TestPlanetConstructionQueuePausedPersistence` and the Fleet variant (lines 34-100) into a parametrized fixture-factory over Planet/Fleet entity types; the four method shapes (default, set True, set False, legacy save) become parametrized cases.
- [x] Verify: `pytest tests/unit/strategy/data/test_construction_queue_paused_persistence.py` passes; LOC delta approximately -35

---

### Task 1.10: Parametrize event-validation missing-key tests [Simple]
**File:** `tests/unit/strategy/data/test_event_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_event_validation.py`

- [x] S08-CAT4-001: collapse the 5 `test_missing_*_raises_persistence_exception` tests (lines 26-69) into a single `@pytest.mark.parametrize('field', [...])` test.
- [x] Verify: `pytest tests/unit/strategy/data/test_event_validation.py` passes; LOC delta approximately -34

---

### Task 1.11: Replace hardcoded policy lists with registry-driven test [Medium]
**File:** `tests/unit/strategy/data/test_group_policies.py`
**Tests:** `pytest tests/unit/strategy/data/test_group_policies.py`

- [x] S06-CAT4-002: replace the 3 hardcoded-policy-list tests (lines 31-71) with a single data-driven test that loads policies from the registry and asserts structural invariants; adding a new policy should not require updating any test list.
- [x] Verify: `pytest tests/unit/strategy/data/test_group_policies.py` passes; LOC delta approximately -30

---

### Task 1.12: Use registry public API instead of `_handlers` private dict [Simple]
**File:** `tests/unit/strategy/engine/test_build_order_command_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_build_order_command_handler.py`

- [x] S06-CAT4-003: rewrite the 2 tests at lines 183-203 to use `registry.get_handler(command_name)` (or equivalent public surface) instead of indexing `registry._handlers`.
- [x] Verify: `pytest tests/unit/strategy/engine/test_build_order_command_handler.py` passes; LOC delta approximately -10 (overlaps with APC-003-F06 in Phase 5 - keep in sync)

---

### Task 1.13: Parametrize / merge superweapon fleet-not-found duplication [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/engine/test_superweapon_edge_cases.py`

- [x] S03-CAT4-001: parametrize or merge the duplicated `_get_fleet_by_id.return_value=None` test pattern at lines 105-118 with the 5 fleet-not-found tests already present in `test_superweapon_edge_cases.py`.
- [x] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/engine/test_superweapon_edge_cases.py` passes; LOC delta approximately -14 (overlaps with DUP-001/DUP-002 in Phase 6 - keep in sync)

---

### Task 1.14: Consolidate superweapon edge-case duplicates [Complex]
**File:** `tests/unit/strategy/engine/test_superweapon_edge_cases.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_edge_cases.py`

- [x] S03-CAT4-002: parametrize the 5 mission-handler fleet-not-found tests (lines 188-274) - structurally identical.
- [x] S03-CAT4-003: consolidate order-processor error-case overlap (lines 281-508) - keep handler-level tests for input validation, processor-level for orchestration; remove duplicated mock-setup/assertion patterns.
- [x] Verify: `pytest tests/unit/strategy/engine/test_superweapon_edge_cases.py` passes; LOC delta approximately -315

---

### Task 1.15: Module-level make_ship_with_yard fixture [Simple]
**File:** `tests/unit/strategy/fleet/test_space_yard.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_space_yard.py`

- [x] S09-CAT4-004: collapse the two identical `make_ship_with_yard` fixtures (lines 91-123 and 195-226) into a single module-level fixture referenced from both classes.
- [x] Verify: `pytest tests/unit/strategy/fleet/test_space_yard.py` passes; LOC delta approximately -32 (overlaps with HLP-003 in Phase 6 - keep in sync)

---

### Task 1.16: Document overlap and keep both projection-edge-case tests [Simple]
**File:** `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_service_edge_cases.py tests/unit/strategy/fleet_navigation/test_projection.py`

- [x] S10-CAT4-001: keep `TestProjectPathAsDicts` (lines 432-465); the structural overlap with `test_projection.py:146-169` is minimal and the logical coverage is distinct. Add a one-line note to the class docstring stating the overlap is intentional.
- [x] Verify: `pytest tests/unit/strategy/fleet_navigation/test_service_edge_cases.py` passes; LOC delta approximately 0 (documentation only)

---

### Task 1.17: Extract shared `setup_mocks` for battle-panels-extended [Medium]
**File:** `tests/unit/ui/screens/test_battle_panels_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_panels_extended.py`

- [x] S11-CAT4-001: extract the 3 copy-pasted `setup_mocks` blocks (lines 39-66, 225-247, 402-424) into a single shared module-scoped fixture/helper.
- [x] Verify: `pytest tests/unit/ui/screens/test_battle_panels_extended.py` passes; LOC delta approximately -55

---

### Task 1.18: Merge warp-hotkey mode-activation tests [Medium]
**File:** `tests/unit/ui/screens/test_warp_hotkey.py`
**Tests:** `pytest tests/unit/ui/screens/test_warp_hotkey.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`

- [x] S05-CAT4-001: merge the 4 mode-activation tests in `TestWarpHotkeyModeActivation` (lines 46-102) into `test_strategy_input_handler_hotkeys.py` (W/M, fleet-None, capability-fail, ESC); retain `TestWarpHotkeyViaRealMapper` and `TestWarpClickDispatching` in the original file.
- [x] Verify: `pytest tests/unit/ui/screens/test_warp_hotkey.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` passes; LOC delta approximately -45

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
