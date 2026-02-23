# Phase 3: Partial File Edits

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Surgically remove dead/duplicate/trivial tests from 4 remaining files (~250 lines removed)
**Priority:** Normal — requires careful editing to avoid breaking kept tests

**Note:** PROJ-157 already completed 4 of 8 tasks (3.1, 3.2, 3.4, 3.6). Only tasks 3.3, 3.5, 3.7, 3.8 remain.

---

## Tasks

### ~~Task 3.1: UI-5 — Remove trivial positivity checks from test_config.py [Simple]~~
**DONE by PROJ-157** — File reduced from 213 → 74 lines. Only relationship/validation tests remain.

- [x] ~~Completed by PROJ-157~~

### ~~Task 3.2: UI-7 — Remove duplicates from test_battle_screen_edge_cases.py [Medium]~~
**DONE by PROJ-157** — File reduced from 408 → 143 lines. Only 6 unique tests remain.

- [x] ~~Completed by PROJ-157~~

### Task 3.3: UI-6 — Remove 3 duplicate tests from test_battle_screen_extended.py [Simple]
**File:** `tests/unit/ui/test_battle_screen_extended.py` (131 → 41 lines)
**Tests:** `pytest tests/unit/ui/test_battle_screen_extended.py -v`

**Keep:** `test_process_beam_attack_logic` (unique beam attack test)

- [x] Remove `test_is_battle_over_victory` (duplicate of test_battle_screen.py)
- [x] Remove `test_update_loop_tick_counter` (duplicate of test_battle_screen_simulation.py)
- [x] Remove `test_headless_mode_initialization` (duplicate of test_battle_screen_simulation.py)
- [x] Clean up any fixtures/imports only used by removed tests (`setup_strategy_manager` fixture, `StrategyManager`, `get_unit_test_data_dir`, etc.)
- [x] Run `pytest tests/unit/ui/test_battle_screen_extended.py -v` — verify beam test passes

**Notes:** Removed 3 duplicate tests and unused fixture/imports. File reduced from 131 → 41 lines.

### ~~Task 3.4: UI-9 — Remove trivial color and font tests [Simple]~~
**DONE by PROJ-157** — File reduced from 141 → 100 lines. `TestBasicColors` and `TestFontConstants` removed.

- [x] ~~Completed by PROJ-157~~

### Task 3.5: UI-11 — Remove TestGameSwitchScene from test_scene_protocol.py [Simple]
**File:** `tests/unit/ui/test_scene_protocol.py` (240 → ~200 lines)
**Tests:** `pytest tests/unit/ui/test_scene_protocol.py -v`

**Keep:** `TestISceneProtocolCompliance` + `TestSceneCallback`

- [x] Remove `TestGameSwitchScene` class (lines 152-192): `test_switch_scene_updates_active_scene`, `test_switch_scene_updates_game_state`. These test Python attribute assignment on MagicMock, not game code.
- [x] Run `pytest tests/unit/ui/test_scene_protocol.py -v` — verify kept tests pass

**Notes:** Removed TestGameSwitchScene class (2 tests). File reduced by ~40 lines.

### ~~Task 3.6: UI-13 — Remove constant positivity checks from test_game_renderer.py [Simple]~~
**DONE by PROJ-157** — File reduced from 397 → 371 lines. Only relationship/semantic tests remain in `TestRenderingConstants`.

- [x] ~~Completed by PROJ-157~~

### Task 3.7: UI-14 — Remove mock-testing classes from test_strategy_detail_formatter.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py` (538 → ~432 lines)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py -v`

- [x] Remove `TestStrategyDetailFormatterWidgetAccessors` class (lines 71-131, 8 tests that assert `_mock_name` values)
- [x] Remove `TestResizeSupport` class (lines 425-468, 3 tests: `test_update_screen_size`, `test_update_graph_rect`, `test_update_graphs`)
- [x] Clean up unused imports if any
- [x] Run `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py -v` — verify remaining tests pass

**Notes:** Removed 11 mock-testing tests (8 widget accessor tests + 3 resize tests). File reduced by ~106 lines.

### Task 3.8: STR-14 — Remove legacy cleanup check from test_production_refactor.py [Simple]
**File:** `tests/unit/strategy/engine/test_production_refactor.py` (134 → 127 lines)
**Tests:** `pytest tests/unit/strategy/engine/test_production_refactor.py -v`

- [x] Remove `test_legacy_cleanup` method (lines 128-133): checks `not hasattr(engine, '_process_base_queue')` etc. One-time refactoring verification, no longer needed.
- [x] Run `pytest tests/unit/strategy/engine/test_production_refactor.py -v` — verify remaining tests pass

**Notes:** Removed legacy cleanup test (1 test). File reduced by 7 lines.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
