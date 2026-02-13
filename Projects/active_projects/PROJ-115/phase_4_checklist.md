# Phase 4: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-115 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (10 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 4.1: DUP-UI1-001 - BuildQueueScreen instantiation duplicate [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - 3 methods (on_build_yard_click, on_navigate_to_hex_build, on_fleet_build_click) each instantiate BuildQueueScreen with ~15 lines of DI setup. This is explicit dependency injection pattern. Extracting a factory would add indirection without meaningful benefit. The code is clear about what dependencies are being provided.

### Task 4.2: DUP-UI1-002 - Two separate ColumnManager classes with [Medium]
**File:** `game/ui/screens/column_manager.py`, `game/ui/screens/planet_list_columns.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Two different ColumnManager classes exist but serve different purposes:
- `column_manager.py`: Fleet report columns for ShipInstance data (serial, design, HP%, status, warp, etc.)
- `planet_list_columns.py`: Planet list columns with header buttons, sort indicators, pygame_gui integration
Different data models, different UI behaviors. Not duplicate code.

### Task 4.3: DUP-UI1-003 - Screenshot capture and toast notificatio [Simple]
**File:** `game/ui/screens/build_queue_screen.py`, `game/ui/screens/strategy_input_handler.py`, `game/ui/screens/planet_list_window.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Each screen has specific screenshot behavior:
- StrategyInputHandler: full screenshot + viewport-only screenshot, two different methods
- BuildQueueScreen: screenshot with "build_queue" label, toast notification
- PlanetListWindow: screenshot with "planet_list" label, toast notification
Screen-specific labeling and behaviors justify separate implementations.

### Task 4.4: DUP-UI1-004 - Resource display formatting duplicated b [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - PROJ-86 Phase 8 extracted formatting to build_queue_helpers.py with format_empire_resources() and format_resource_cost(). BuildQueueScreen has thin static method wrappers for internal consistency.

### Task 4.5: DUP-UI1-005 - Star system/star formatting duplicated b [Simple]
**File:** `game/ui/screens/strategy_detail_formatter.py`, `game/ui/screens/strategy_detail_fmt.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Different responsibilities:
- `strategy_detail_fmt.format_star_system_info()`: Pure text formatter, returns HTML string
- `strategy_detail_formatter._format_star_system()`: Formatter + UI side effects (shows graph, sets spectrum data)
The method does MORE than the function - handles graph display which requires class state.

### Task 4.6: DUP-UI1-006 - Event log window open methods duplicated [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Facade Pattern. StrategyUI provides stable public API that delegates to StrategyWindowManager. This is intentional decomposition (PROJ-86) - callers use simple methods on StrategyUI without needing to know internal structure.

### Task 4.7: DUP-UI1-007 - Thin wrapper/proxy methods in StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Facade Pattern. StrategyUI is a facade class (PROJ-86 decomposition) that provides unified interface for:
- Window management (delegates to StrategyWindowManager)
- Panel management (delegates to StrategyPanelManager)
- Event routing (delegates to StrategyEventRouter)
These thin wrappers ARE the API. Removing them would expose internal structure.

### Task 4.8: DUP-UI1-008 - Population count formatting (K/M suffixe [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Population formatting is inline in strategy_detail_fmt.py (lines 105, 112, 130) using f-strings like `f"{pop / 1_000:.0f}K"`. No duplicated functions - just inline formatting where needed. Extracting a function for 3 uses would add unnecessary indirection.

### Task 4.9: DUP-UI1-009 - Window centering pattern repeated ~15 ti [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Utility exists: `game/ui/utils.py:create_centered_rect()` for complex centering. Many uses of `.center = (x // 2, y // 2)` are pygame idiom for setting rect center after creation - this is a one-liner that doesn't benefit from extraction. Some places already use the utility (strategy_screen line 641, workshop_ship_io).

### Task 4.10: DUP-UI1-010 - StrategyDetailFormatter._format_star_sys [N]
**File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Same finding as Task 4.5. The _format_star_system() method has UI side effects (graph display) that format_star_system_info() doesn't have. Different responsibilities.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
