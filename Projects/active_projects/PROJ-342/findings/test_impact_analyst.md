# PROJ-342: Test Impact Analysis
Date: 2026-05-04  
Analyst: Claude Code (Search Specialist)  
Status: Complete

## Executive Summary

Refactoring TestLabScreen and TestLabUIController to eliminate self.game coupling will require:
- DELETE ENTIRELY: tests/unit/combat_lab/services/test_test_execution_service.py (20 tests)
- DELETE CLASS: TestHandleRunHeadless and TestHandleRunVisual from two controller test files (8 tests)
- UPDATE: Constructor calls in remaining controller and visual run tests (from 3-arg to 2-arg)
- UPDATE: test_visual_run.py fixture setup and mock_game references (fixture removed, added mock_battle_scene)
- KEEP: 18 controller init/event tests + 17 visual/battle tests, all fixable with fixture changes

Total test count delta:
- Current: 63 tests in scope files
- After: 34 tests (29 tests deleted)
- Net change: -29 tests (all intended deletions)

---

## File-by-File Disposition

### 1. tests/unit/combat_lab/services/test_test_execution_service.py
Status: DELETE ENTIRE FILE (20 tests)

Justification: 
- File tests TestExecutionService, an orphan service deleted when handle_run_headless() and handle_run_visual() methods are removed from TestLabUIController.
- No production code calls TestExecutionService after controller methods are deleted (verified by git grep).
- File is tightly coupled to the deleted service; no tests worth preserving for other purposes.

Tests to remove: 20 tests (TestTestExecutionServiceInit, TestRunVisual, TestRunHeadless)

---

### 2. tests/unit/combat_lab/services/test_controller_execution.py
Status: KEEP 9 tests (DELETE 5 tests)

Summary:
- Total: 14 tests across 4 classes
- Keep: 9 tests (TestGetFilteredScenarios, TestGetShipInfo, TestGetComponentData)
- Delete: 5 tests (TestHandleRunHeadless class, lines 14-205)

#### TestHandleRunHeadless - DELETE ENTIRE CLASS (lines 14-205)
Tests to delete:
- test_handle_run_headless_success
- test_handle_run_headless_failed_test
- test_handle_run_headless_no_test_selected
- test_handle_run_headless_test_not_found
- test_handle_run_headless_with_error
- test_handle_run_headless_progress_callback
- test_handle_run_headless_updates_ui_state
- test_handle_run_headless_adds_to_history

Justification: Tests the deleted handle_run_headless() method and now-orphaned TestExecutionService and TestResultsService.

#### Remaining Classes - KEEP ALL (9 tests)
- TestGetFilteredScenarios::test_get_filtered_scenarios_all
- TestGetFilteredScenarios::test_get_filtered_scenarios_by_category
- TestGetShipInfo::test_get_ship_info_success
- TestGetShipInfo::test_get_ship_info_test_not_found
- TestGetComponentData::test_get_component_data_success
- TestGetComponentData::test_get_component_data_not_found

Required updates:
1. Delete lines 14-205: TestHandleRunHeadless class entirely
2. Lines 225, 254, 275, 293, 311, 325: Change TestLabUIController(mock_game, mock_test_registry, mock_test_history) to TestLabUIController(mock_test_registry, mock_test_history)

---

### 3. tests/unit/combat_lab/services/test_controller_init_events.py
Status: KEEP 8 tests (DELETE 4 tests)

Summary:
- Total: 12 tests across 5 classes
- Keep: 8 tests (init, event handling, category/test clicks)
- Delete: 4 tests (TestHandleRunVisual class)

#### TestHandleRunVisual - DELETE ENTIRE CLASS (lines 134-199)
Tests to delete:
- test_handle_run_visual_success (line 137)
- test_handle_run_visual_no_test_selected (line 155)
- test_handle_run_visual_test_not_found (line 168)
- test_handle_run_visual_execution_failure (line 183)

Justification: Tests the deleted handle_run_visual() method on TestLabUIController.

#### Remaining Classes - KEEP ALL (8 tests)
TestTestLabUIControllerInit (2 tests, lines 11-30):
- test_init (line 14): Will need line 18 assertion removed
- test_init_loads_scenarios (line 26)

TestHistoryLoadedOnInit (3 tests, lines 33-99):
- test_init_loads_history_into_registry (line 36)
- test_init_skips_tests_with_no_history (line 61)
- test_init_loads_failing_test_history (line 77)

TestHandleCategoryClick (2 tests, lines 101-120):
- test_handle_category_click (line 104)
- test_handle_category_click_clears_test (line 112)

TestHandleTestClick (1 test, lines 122-131):
- test_handle_test_click (line 125)

Required updates:
1. Delete lines 134-199: TestHandleRunVisual class entirely
2. Lines 16, 28, 56, 71, 96, 106, 114, 127: Change constructor from 3 args to 2 args
3. Line 18: Delete assertion "assert controller.game is mock_game" (attribute will not exist)

---

### 4. tests/unit/test_lab/test_visual_run.py
Status: KEEP ALL 17 tests (UPDATE FIXTURES & CONSTRUCTOR)

Summary:
- Total: 17 tests across 4 classes
- All tests are valid after refactoring but require fixture/constructor updates
- No tests deleted; all 17 tests remain logically sound

Core issue:
The test helper _create_test_lab_screen() (lines 92-120) constructs mocks assuming TestLabScreen receives a game parameter.

After refactor, TestLabScreen.__init__ signature changes from:
  def __init__(self, game, ...):
to:
  def __init__(self, screen_width: int, screen_height: int, battle_scene: BattleScreen, scene_callback=None):

Lines to update in _create_test_lab_screen():
- Line 103: screen.game = mock_game -> change to screen.battle_scene = battle_scene
- Line 115: get_engine=lambda: mock_game.battle_scene.engine -> get_engine=lambda: battle_scene.engine

Fixture changes required:
1. Add mock_battle_scene fixture (available from tests.fixtures.battle)
2. Update _create_test_lab_screen() to accept battle_scene parameter
3. Update line 103 and 115 as noted above
4. Update _create_screen_with_real_switch() (line 268) similarly

Assertions using mock_game.battle_scene that need fixture binding update (not logic change):
- mock_game.battle_scene.start_battle.assert_called_once(): 3 sites
- mock_game.battle_scene.engine.ships assignment: 1 site
- mock_game.battle_scene.start_battle.call_args: 3 sites
- mock_game.state checks: 2 sites

These are all resolvable by proper fixture binding.

Classes tested:
- TestVisualRunFlow (7 tests, lines 10-213): KEEP ALL
- TestSceneTransitionCallbacks (7 tests, lines 241-346): KEEP ALL
- TestEndBattleInTestMode (2 tests, lines 349-426): KEEP (tests BattleScreen, not TestLabScreen)
- TestBattleScreenDrawsInTestMode (1 test, line 432): KEEP (tests BattleScreen)
- TestUpdateBattleVisualWithTestMode (1 test, line 503): KEEP (tests BattleScreen)

---

### 5. tests/unit/combat_lab/services/conftest.py
Status: UPDATE (remove mock_game fixture)

Current fixture (lines 59-66):
```python
@pytest.fixture
def mock_game(mock_battle_screen):
    """Mock game object."""
    from unittest.mock import Mock
    game = Mock()
    game.battle_scene = mock_battle_screen
    game.state = None
    return game
```

Disposition:
- REMOVE the mock_game fixture (lines 59-66) after updating controller test constructors
- The fixture is only used to pass game as first arg to TestLabUIController
- Once all tests remove the game arg, this fixture is unused

---

### 6. tests/unit/test_lab/conftest.py
Status: UPDATE (add mock_battle_scene fixture)

Current contents (lines 1-21):
- Only provides PROJ-279 spec-compiler patch

Disposition:
- Add mock_battle_scene fixture to support test_visual_run.py
- Import from tests.fixtures.battle or define locally
- The autouse fixture at lines 14-21 remains unchanged

---

## Summary Table

| File | Current Tests | Deleted | Kept | Required Changes |
|------|:---:|:---:|:---:|---|
| test_test_execution_service.py | 20 | 20 | 0 | DELETE ENTIRE FILE |
| test_controller_execution.py | 14 | 5 | 9 | Delete TestHandleRunHeadless class (lines 14-205). Update 5 constructor calls. |
| test_controller_init_events.py | 12 | 4 | 8 | Delete TestHandleRunVisual class (lines 134-199). Remove 1 assertion. Update 8 constructor calls. |
| test_visual_run.py | 17 | 0 | 17 | Add mock_battle_scene fixture. Update 2 helper methods. |
| conftest.py (services) | -- | -- | -- | Remove mock_game fixture (lines 59-66). |
| conftest.py (test_lab) | -- | -- | -- | Add mock_battle_scene fixture. |

---

## Test Count Delta

Before refactor:
- test_test_execution_service.py: 20 tests
- test_controller_execution.py: 14 tests
- test_controller_init_events.py: 12 tests
- test_visual_run.py: 17 tests
- Total: 63 tests

After refactor:
- test_test_execution_service.py: 0 tests (file deleted)
- test_controller_execution.py: 9 tests (14 minus 5)
- test_controller_init_events.py: 8 tests (12 minus 4)
- test_visual_run.py: 17 tests (no deletions)
- Total: 34 tests

Delta: -29 tests (all intended deletions due to orphaned services and methods)

---

## No Hidden Dependencies Found

Git grep verification completed:
- No other test files construct TestLabUIController with 3-arg signature
- No test files import TestExecutionService or TestResultsService outside service tests
- Fixtures are isolated to test directories

Autouse fixtures:
- Both conftest.py files use _proj279_patch_spec_compiler
- This fixture is independent of the game parameter being removed
- Requires no changes

---

## Risk Assessment

Low risk:
- All deletions are well-scoped to orphaned services and methods
- Remaining tests use only public data-filtering and event-handling interfaces
- Fixture updates are mechanical parameter binding changes

Mitigation:
- Run full test suite after implementation
- Run smoke test of Combat Lab "Run All" functionality

---

## Implementation Checklist

1. [ ] Delete: tests/unit/combat_lab/services/test_test_execution_service.py (entire file)
2. [ ] Update: test_controller_execution.py - delete TestHandleRunHeadless class
3. [ ] Update: test_controller_execution.py - fix 5 constructor calls
4. [ ] Update: test_controller_init_events.py - delete TestHandleRunVisual class
5. [ ] Update: test_controller_init_events.py - fix 8 constructor calls
6. [ ] Update: test_controller_init_events.py - remove assertion at line 18
7. [ ] Update: test_visual_run.py - add mock_battle_scene fixture
8. [ ] Update: test_visual_run.py - fix _create_test_lab_screen() helper
9. [ ] Update: test_visual_run.py - fix _create_screen_with_real_switch() helper
10. [ ] Update: conftest.py (services) - remove mock_game fixture
11. [ ] Update: conftest.py (test_lab) - add mock_battle_scene fixture
