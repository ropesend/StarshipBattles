# Phase 4: Strategy Screen Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Wire the Star List Window into the strategy screen via button, event routing, and window management.

---

## Tasks

### Task 4.1: Add `btn_stars` to Top Bar [Simple]
**File:** `game/ui/screens/strategy_panel_manager.py`

- [x] Add `btn_stars: Any = None` to StrategyWidgets dataclass
- [x] Insert "Stars" button after "Planets" (index 1)
- [x] Shift all subsequent button indices right by 1

### Task 4.2: Wire `btn_stars` in StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`

- [x] Add `self.btn_stars = widgets.btn_stars`
- [x] Add `open_star_list()` delegation method

### Task 4.3: Add `open_star_list()` to StrategyWindowManager [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`

- [x] Import StarListWindow
- [x] Add `self.star_list_window = None`
- [x] Add `open_star_list()`, `_on_star_list_closed()`, `_on_star_navigate()`

### Task 4.4: Route `btn_stars` in Event Router [Simple]
**File:** `game/ui/screens/strategy_event_router.py`

- [x] Route btn_stars click to `ui.open_star_list()`
- [x] Add `wm.star_list_window` to `has_modal_open()`
- [x] Add star_list_window case to `_handle_window_close()`
- [x] Add to `_is_blocking_ui_element_at()` blocking_windows list

**Notes:** Also fixed 6 test files that mock StrategyUI/WindowManager to include `star_list_window = None` and `btn_stars = MagicMock()`.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Full test suite passes: 13900 passed, 0 failed
- [x] Update status to Complete
