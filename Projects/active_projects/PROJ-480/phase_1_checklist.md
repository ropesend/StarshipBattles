# Phase 1: CAT-9 Simplification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-480 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace ~28 verified CAT-9 simplification findings from review `2026-05-20_210550_test-review`. Each is a repeated boilerplate/import/mock-construction pattern that an in-module helper or fixture can flatten. Smallest, lowest-risk wins first. Reclaim ~600 LOC of repetition.

---

## Tasks

### Task 1.1: test_workshop_screen.py — boilerplate derivative tests
**File:** `tests/unit/ui/screens/test_workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_screen.py`

- [ ] Once Phase 2 of PROJ-478 deletes the CAT-2 cluster (lines 260-331 deleted), the CAT-9 boilerplate derivative disappears. _(coordination note: this finding is mostly subsumed by P0 work; no separate action required if PROJ-478 Phase 2 has run.)_
- [ ] Verify: re-check `pytest tests/unit/ui/screens/test_workshop_screen.py` after PROJ-478 work; LOC delta covered there.

### Task 1.2: test_system_selection_window.py — 6 repeated SystemSelectionWindow constructions
**File:** `tests/unit/ui/screens/test_system_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_system_selection_window.py`

- [ ] Extract `_make_system_selection_window()` helper (or `@pytest.fixture`) for the 6 tests at lines 50-227 that share `Rect(100,100,450,500)` + identical systems list.
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 1.3: test_fleet_menu_items.py — repeated fleet/mapper/galaxy construction
**File:** `tests/unit/ui/screens/test_fleet_menu_items.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_menu_items.py`

- [ ] Extract shared `_make_fleet` / `_make_galaxy` / `_mapper` helpers (currently re-called with the same defaults in TestCapabilityMatrix + TestFMSRows, lines 100-262, 400-615).
- [ ] _(coordination note: also touches HLP-004 in PROJ-479 Phase 6. Keep helpers in this file local unless cross-shard sweep absorbs them.)_
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 1.4: test_physics_constants.py — 3 docstring-substring tests
**File:** `tests/unit/strategy/test_physics_constants.py`
**Tests:** `pytest tests/unit/strategy/test_physics_constants.py`

- [ ] Parametrize the 3 docstring-substring tests (lines 91-108) on `(constant, expected_substring)`.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 1.5: test_save_selection.py — 3 setup_tmpdir wrappers
**File:** `tests/unit/ui/test_save_selection.py`
**Tests:** `pytest tests/unit/ui/test_save_selection.py`

- [ ] Replace the 3 per-class `setup_tmpdir` wrappers (lines 65, 164, 241) with a single module-level autouse fixture. _(coordination note: tied to HLP-005 in PROJ-479 Phase 6; if HLP-005 sweep absorbs this, no separate action required.)_
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 1.6: test_hex_math_core.py — 9 in-method hex_random_cluster imports
**File:** `tests/unit/core/test_hex_math_core.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`

- [ ] Add `import random` at module level (or `from game.core.hex_math import hex_random_cluster`) and remove the 9 in-method import statements at lines 722, 735, 748, 757, 783, 806, 819, 841, 853.
- [ ] Verify: passes; LOC delta ≈ -9.

### Task 1.7: test_colonization_facade.py — 8 in-method MockPlanetType defs
**File:** `tests/unit/strategy/services/test_colonization_facade.py`
**Tests:** `pytest tests/unit/strategy/services/test_colonization_facade.py`

- [ ] Define a single `MockPlanetType(Enum)` at module level; remove the 8 inline definitions inside test methods (lines 71, 377, 438, 488, 571, 625, 724, 787). _(coordination note: tied to HLP-002 in PROJ-479 Phase 6. If the shared `tests/fixtures/colonization_fixtures.py` is created first, import from there.)_
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 1.8: test_build_order_processor.py — local OrderProcessor() ignoring fixture
**File:** `tests/unit/strategy/engine/test_build_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_build_order_processor.py`

- [ ] Update `test_build_order_auto_completes_when_queue_empties` (line 80) and `test_queued_orders_remain_after_build_completion` (line 149) to use the existing `order_processor` fixture at lines 14-17 instead of constructing locally.
- [ ] Verify: passes; LOC delta ≈ -4.

### Task 1.9: test_empire_build_queue_formatter.py — repeated in-method imports
**File:** `tests/unit/ui/screens/test_empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_formatter.py`

- [ ] Move `get_resource_rate_text` and `get_resource_total_text` imports to module level; remove from 5+ method bodies in TestGetResourceRateText and TestGetResourceTotalText (lines 235-270).
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 1.10: test_engine_validation.py — 12 near-identical engine classes
**File:** `tests/unit/strategy/engine/test_engine_validation.py`
**Tests:** `pytest tests/unit/strategy/engine/test_engine_validation.py`

- [ ] Consolidate the 12 engine validation classes (lines 39-319, ~280 LOC, each has `test_valid_empires_pass` + `test_*_raises` with the same `_empire()` / `_fleet()` helpers) into a parametrized superclass or per-engine `@pytest.fixture(params=[...])`.
- [ ] Verify: passes; LOC delta ≈ -180.

### Task 1.11: test_strategy_input_handler_transfer.py — 3 mode-test classes
**File:** `tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`

- [ ] Consolidate the 3 transfer/drop/load mode-test classes (lines 44-275, ~230 LOC) into one parametrized class testing the shared key-sets-mode / left-click-opens-dialog / right-click-cancels / escape-cancels pattern.
- [ ] Verify: passes; LOC delta ≈ -150.

### Task 1.12: test_modifier_utils.py — local _Modifier / _SpecialModifier stubs
**File:** `tests/unit/ui/screens/builder/test_modifier_utils.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_utils.py`

- [ ] _(coordination note: addressed via DUP-006 in PROJ-479 Phase 5 Task 5.5. No separate action required.)_

### Task 1.13: test_fleet_movement_engine/conftest.py — 16-attribute mock_fleet duplicated
**File:** `tests/unit/strategy/fleet_movement_engine/conftest.py`
**Tests:** `pytest tests/unit/strategy/fleet_movement_engine/`

- [ ] Move the 16-attribute `mock_fleet` fixture (lines 21-38) to the canonical conftest if duplicated in `test_fleet_order_transfer.py:21-36`, or extend kwargs to avoid duplication.
- [ ] Verify: passes; LOC delta ≈ -18.

### Task 1.14: test_race_setup_screen.py — repeated inline mock function defs
**File:** `tests/unit/ui/test_race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/test_race_setup_screen.py`

- [ ] Extract shared fixtures for the inline mock function definitions repeated in 4+ tests (lines 155-167, 173-190, 304-309, 345-352).
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 1.15: test_strategy_menu_actions.py — _make_strategy_screen helper
**File:** `tests/unit/ui/screens/test_strategy_menu_actions.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_menu_actions.py`

- [ ] Convert `_make_strategy_screen()` helper at lines 15-40 (used in ~22 tests) to a `@pytest.fixture(scope="function")` to reduce boilerplate calls.
- [ ] Verify: passes; LOC delta ≈ -22.

### Task 1.16: test_weapon_firing_system.py — inline ship construction
**File:** `tests/unit/simulation/combat/test_weapon_firing_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_firing_system.py`

- [ ] Create `_make_ship_mock(**kwargs)` factory with defaults for the 6+ recurring attrs (team_id, position, velocity, angle, total_shots_fired, max_targets, secondary_targets). Replace inline constructions in 15+ tests (lines 100-115+).
- [ ] Verify: passes; LOC delta ≈ -90.

### Task 1.17: test_transfer_dialog.py + test_cargo_quick_dialog.py — real UIManager
**File:** `tests/unit/ui/screens/test_transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_cargo_quick_dialog.py`

- [ ] Switch both files' fixtures (lines 22-23) to `scope="module"` + `MagicMock()` for UIManager (matching the preferred pattern in test_empire_treasury_panel.py).
- [ ] Verify: passes; LOC delta minimal but per-test pygame_gui setup eliminated.

### Task 1.18: test_list_data_source_base.py — multi-branch single test
**File:** `tests/unit/ui/utils/test_list_data_source_base.py`
**Tests:** `pytest tests/unit/ui/utils/test_list_data_source_base.py`

- [ ] Split `test_get_cell_value_supports_func_attr_nested_attr_and_format` (lines 57-64) into 4 parametrized tests: computed, direct_attr, formatted_attr, nested_attr. Improves failure isolation.
- [ ] Verify: passes; LOC delta ≈ +5 (split is wider but more diagnostic).

### Task 1.19: test_basic_paths.py — find_path_deep_space duplicated helpers
**File:** `tests/unit/strategy/pathfinding/test_basic_paths.py`
**Tests:** `pytest tests/unit/strategy/pathfinding/`

- [ ] Move `find_path_deep_space` and `find_path_interstellar` (lines 12-30, also in `test_edge_cases.py`) to `tests/unit/strategy/pathfinding/conftest.py`; import in both files.
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 1.20: test_naming.py — module-level loop test
**File:** `tests/unit/strategy/utility/test_naming.py`
**Tests:** `pytest tests/unit/strategy/utility/test_naming.py`

- [ ] _(CAT-12 finding S14-F005 was REJECTED — 5-line loop is straightforward; do not change.)_

### Task 1.21: test_damage_calculator.py — mock_ship factory unused
**File:** `tests/unit/simulation/combat/test_damage_calculator.py`
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator.py`

- [ ] Use the existing `mock_ship` factory at lines 357-370 in the later test classes (lines 831+); currently those classes construct ship via inline MagicMock instead.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 1.22: test_battle_panels_extended.py — inline duplicate of helper
**File:** `tests/unit/ui/test_battle_panels_extended.py`
**Tests:** `pytest tests/unit/ui/test_battle_panels_extended.py`

- [ ] _(coordination note: addressed via DUP-002 in PROJ-479 Phase 5 Task 5.2. No separate action required.)_

### Task 1.23: test_harvesting_engine.py — staticmethod _make_engine declared 3×
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Remove the 3 `_make_engine = staticmethod(_make_engine)` declarations at lines 157, 524, 842 — call the module-level `_make_engine()` directly in test methods.
- [ ] Verify: passes; LOC delta ≈ -3.

### Task 1.24: test_battle_spec.py — 4 _minimal_* helpers
**File:** `tests/unit/simulation/test_battle_spec.py`
**Tests:** `pytest tests/unit/simulation/test_battle_spec.py`

- [ ] _(verification: VERIFIED but flagged as acceptable per advisory rule — helpers are well-factored factories. No remediation indicated.)_
- [ ] No action required.

### Task 1.25: test_save_load_ops.py + others — setup_tmpdir 5× duplication
**File:** `tests/unit/strategy/save_game_service/test_save_load_ops.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/`

- [ ] _(coordination note: addressed via HLP-005 in PROJ-479 Phase 6 Task 6.5. No separate action required here.)_

### Task 1.26: test_superweapons.py — `.items()` parametrize variant
**File:** `tests/unit/strategy/engine/test_superweapons.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapons.py`

- [ ] Normalize the lone `.items()` parametrization at line 113 to match the 9 `.keys()` peers — or document why this one diverges.
- [ ] Verify: passes; LOC delta ≈ 0 (semantic alignment only).

### Task 1.27: test_planet_specific_colonization.py — duplicate 'colony_pod' dict keys
**File:** `tests/unit/strategy/engine/test_planet_specific_colonization.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_specific_colonization.py`

- [ ] Remove the 2 duplicate `'colony_pod'` dict entries at lines 174, 178 (line 183 is the surviving entry per dict-last-wins semantics).
- [ ] Verify: passes; LOC delta ≈ -2.

### Task 1.28: test_action_execution_engine.py — for-loop with assertions
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py`

- [ ] Parametrize `test_speed_1_fleet_acts_every_100_ticks` (lines 76-96) on `tick` ∈ [1, 20, 50, 99] for per-tick failure isolation.
- [ ] Verify: passes; LOC delta ≈ +5.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2 — CAT-8 Needless Complexity)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
