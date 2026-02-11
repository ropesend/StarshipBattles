# Phase 3: Medium Complexity Removals

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Remove backward compatibility code with multiple callers requiring careful migration.

---

## Tasks

### Task 3.1: Remove validation_result() convenience function [Medium] - COMPLETE
**Finding:** LEG-FND-004 (partial) + LEG-FND-001 (partial)
**File:** `game/core/validation.py:168-183`
**Callers:**
- `game/ui/screens/race_validator.py` (8 calls)
- `game/strategy/facade/strategy_session_facade.py` (3 calls)
- `game/strategy/validation/transfer_validator.py` (many calls)
- `game/strategy/validation/colonize_validator.py` (many calls)
- `game/strategy/validation/superweapon_validator.py` (many calls)
- `game/strategy/engine/command_handlers.py` (many calls)
- `game/strategy/engine/superweapon_command_handlers.py` (many calls)
- Multiple test files
**Tests:** `pytest tests/ -n 12` (all 8249 passed)

- [x] In `game/ui/screens/race_validator.py`: replace all `validation_result(is_valid=False, message="...")` calls with `ValidationResult(is_valid=False, errors=["..."])`
- [x] In `game/ui/screens/race_validator.py`: replace all `validation_result(is_valid=True)` calls with `ValidationResult()`
- [x] In `tests/unit/ui/test_race_validator.py:128`: update the test call similarly
- [x] Update imports in race_validator.py: change `from game.core.validation import validation_result` to `from game.core.validation import ValidationResult`
- [x] Update ALL other callers of validation_result() in game/ and tests/
- [x] Delete the `validation_result()` function from `game/core/validation.py` (lines 168-183)
- [x] Update the docstring on ValidationResult class to remove "Pattern 2" references (lines 71-78)
- [x] Verify: `grep -r "validation_result(" game/` returns no hits
- [x] Updated test assertions that expected success messages to check for empty errors instead

**Notes:** Scope was much larger than initially documented - the function was used throughout the strategy layer, not just in race_validator.

---

### Task 3.2: Remove deprecated BattleScreen action flags [Medium] - COMPLETE
**Finding:** LEG-UI1-001, LEG-UI1-010
**File:** `game/ui/screens/battle_screen.py`
**Callers:**
- `game/ui/screens/test_lab/screen.py:457`
- `tests/unit/test_lab/test_visual_run.py`
- `tests/fixtures/battle.py`
- `game/ui/screens/battle_ui.py`
- `test_framework/services/test_execution_service.py`
**Tests:** `pytest tests/unit/test_lab/ tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_extended.py -n 12`

- [x] In `battle_screen.py`: Remove `self.action_return_to_setup = False` and `self.action_return_to_test_lab = False` from `__init__` (lines 109-111)
- [x] In `battle_screen.py`: Remove reset of these flags in `start()` (lines 272-273) and `start_with_controller()` (lines 160-161)
- [x] In `battle_screen.py:_trigger_return_to_setup()`: Remove the `else: self.action_return_to_setup = True` branch (line 502) - keep only the `scene_callback` path
- [x] In `battle_screen.py:_trigger_return_to_test_lab()`: Remove the `else: self.action_return_to_test_lab = True` branch (line 509) - keep only the `scene_callback` path
- [x] Grep all files for `action_return_to_setup` and `action_return_to_test_lab`
- [x] In `test_lab/screen.py:457`: Remove `self.game.battle_scene.action_return_to_test_lab = False` line
- [x] Update any test files that read these flags to use scene_callback pattern instead
- [x] In `game/ui/screens/battle_ui.py`: Changed direct flag set to `_trigger_return_to_test_lab()` call
- [x] In `test_framework/services/test_execution_service.py`: Removed flag reset
- [x] Verify: `grep -r "action_return_to_setup\|action_return_to_test_lab" game/ tests/` returns no hits

**Notes:** Removed 8 lines from battle_screen.py. Updated battle_ui.py to use scene_callback via _trigger_return_to_test_lab(). Removed flag resets from test_lab/screen.py, test_execution_service.py, test_visual_run.py (x2), and fixtures/battle.py.

---

### Task 3.3: Remove BuildQueueScreen legacy single-context mode [Medium] - COMPLETE
**Finding:** LEG-UI1-002
**File:** `game/ui/screens/build_queue_screen.py:106-120, 274-277`
**Callers:** All callers in `game/ui/screens/strategy_screen.py` already provide hex_coord
**Tests:** `pytest tests/integration/ui/build_queue_screen/ -n 12`

- [x] In `build_queue_screen.py`: Remove the `else` branch at lines 111-120 (the backward compat wrapping with `_legacy` ID)
- [x] Change the `if hex_coord is not None and galaxy is not None and empire is not None:` guard to always execute (remove the if)
- [x] Make `hex_coord`, `galaxy`, and `empire` required parameters (remove Optional, remove None defaults)
- [x] Delete backward compat test alias properties at lines 274-277: `queue_selector_panel`, `queue_selector_scrollable`, `queue_selector_buttons`
- [x] Also delete the sync at line 284: `self.queue_selector_buttons = self._queue_selector.buttons`
- [x] Grep test files for `queue_selector_panel`, `queue_selector_scrollable`, `queue_selector_buttons` and update to use `_queue_selector.panel`, `_queue_selector.scrollable`, `_queue_selector.buttons`
- [x] Verify: all callers in strategy_screen.py provide hex_coord, galaxy, empire

**Notes:** Required parameter validation added at top of __init__. Updated 8 test files with MockGalaxy class and required parameters. Also updated test_add_ship_to_queue_with_shipyard and test_add_ship_fails_without_shipyard tests to work with the new queue source architecture.

---

### Task 3.4: Remove StrategyInputHandler legacy keydown fallback [Medium] - COMPLETE
**Finding:** LEG-UI1-005
**File:** `game/ui/screens/strategy_input_handler.py:102-107, 316-394`
**Tests:** `pytest tests/unit/ui/screens/ -n 12` (515 passed)

- [x] In `_handle_keydown()` (lines 102-107): Remove the `if/else` dispatch - always call `_handle_keydown_mapped(event)`
- [x] If `self._mapper` is None, simply return without handling (no legacy fallback)
- [x] Delete the entire `_handle_keydown_legacy()` method (lines 316-394, ~78 lines of duplicated key checks)
- [x] Update `__init__` to document that `input_mapper` is effectively required for keyboard input
- [x] Remove "backward compat" from the class docstring (line 26)
- [x] Verify: all callers that create StrategyInputHandler provide input_mapper
- [x] Check `StrategyScreen.__init__` always passes `input_mapper` to `StrategyInputHandler`
- [x] Update test_scene_protocol.py to pass input_mapper to StrategyScreen
- [x] Update TestBackwardCompatWithoutMapper → TestNoMapperMeansNoKeyboardInput (tests new behavior)
- [x] Update TestStrategyInputHandlerTransfer to use mapper fixture

**Notes:** Deleted ~78 lines of legacy code. Updated 2 test files. All 8248 tests pass.

---

### Task 3.5: Remove BuilderRightPanel sync methods and DesignReportPanel compat [Simple]
**Finding:** LEG-UI1-008, LEG-UI1-009
**Files:**
- `game/ui/screens/builder/right_panel.py:324-327`
- `game/ui/panels/design_report_panel.py:165-166`
**Tests:** `pytest tests/unit/builder/ -n 12`

- [ ] In `right_panel.py`: Delete `_sync_from_stats_panel()` method (lines 324-327)
- [ ] Grep for callers of `_sync_from_stats_panel` and remove calls
- [ ] In `right_panel.py`: Remove direct `rows_map` and `current_logistics_keys` attributes if only populated by sync method
- [ ] In `design_report_panel.py:165-166`: Remove direct `rows_map` exposure if tests can access via `_stats_panel`
- [ ] Update tests that access `rows_map` directly to go through the panel

**Notes:**

---

### Task 3.6: Remove DesignMetadata legacy mass field [Simple]
**Finding:** LEG-STR-006
**File:** `game/strategy/data/design_metadata.py:90-92`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] In `from_design_file()`: Change line 92 from `mass = expected_stats.get("mass", data.get("mass", 0.0))` to `mass = expected_stats.get("mass", 0.0)`
- [ ] Remove the comment about "top-level (legacy)" on line 90

**Notes:**

---

### Task 3.7: Remove DesignMetadata backward-compatible defaults [Medium]
**Finding:** LEG-STR-011
**File:** `game/strategy/data/design_metadata.py:55-72`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Review `from_dict()`: Many `.get()` calls with defaults are appropriate for optional fields
- [ ] Only tighten required fields: `design_id` and `name` should use `data["design_id"]` and `data["name"]` (fail fast if missing)
- [ ] Keep optional fields with defaults (mass, combat_power, resource_cost, etc.) as they may genuinely be absent
- [ ] Verify: all callers of `DesignMetadata.from_dict()` provide design_id and name

**Notes:**

---

### Task 3.8: Remove RaceConfig legacy "name" field [Simple]
**Finding:** LEG-STR-008
**File:** `game/strategy/data/race_config.py:83`
**Tests:** `pytest tests/unit/strategy/ tests/unit/ui/ -n 12`

- [ ] Grep for `race_config.name` or `.name` usage on RaceConfig objects to verify if `faction_name` is used everywhere
- [ ] If `name` field is unused or only used as `faction_name` fallback, remove it
- [ ] If `name` is actively used, remove only the "legacy" comment
- [ ] Update any callers that still use `.name` to use `.faction_name`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (8164 baseline)
- [ ] No "backward compat" or "_legacy" references in modified files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
