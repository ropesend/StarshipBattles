# Phase 5: Type Annotations & Protocol Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-198 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add type annotations to untyped parameters to enable removing remaining hasattr/getattr guards.

---

## Tasks

### Task 5.1: Battle UI Service — Type Parameters [Medium]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [ ] Add TYPE_CHECKING imports for Ship, Component, Projectile, ICombatShip
- [ ] Type conversion method parameters
- [ ] L170, L176: Replace `hasattr(target, 'name')` with isinstance or typed access
- [ ] L260: Same pattern for projectile target
- [ ] Verify: tests pass

**Notes:**

### Task 5.2: Battle Panels — Scene Typing [Medium]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [ ] Add TYPE_CHECKING import for BattleScreen
- [ ] Type `self.scene` as BattleScreen
- [ ] L38, L49: Remove `getattr(self.scene, 'ui_service', None)` fallback
- [ ] L496-498: Remove `hasattr(self.scene, 'test_mode')` and `hasattr(self.scene, 'is_battle_over')`
- [ ] Verify: tests pass

**Notes:**

### Task 5.3: Screenshot Manager — Scene Typing [Simple]
**File:** `game/ui/services/screenshot_manager.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [ ] Add TYPE_CHECKING import for StrategyScreen
- [ ] Type the scene parameter
- [ ] L149: Remove `hasattr(scene, 'ui')`. Use `if scene.ui:` directly.
- [ ] L161-162: Replace getattr with direct access to `SIDEBAR_WIDTH` / `TOP_BAR_HEIGHT`
- [ ] Verify: tests pass

**Notes:**

### Task 5.4: Strategy Input Handler — Modal Check [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L163: Remove double `hasattr`. Call `self.scene.ui._has_modal_open()` directly.
- [ ] Verify: tests pass

**Notes:**

### Task 5.5: Builder Type Discrimination [Simple]
**Files:** `game/ui/screens/builder/detail_panel.py`, `builder_selection.py`, `workshop_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`

- [ ] `detail_panel.py` L95: Replace `hasattr(selection_data, 'id')` with `isinstance(selection_data, Component)`
- [ ] `builder_selection.py` L22: Replace `hasattr(item, 'id')` with `isinstance(item, Component)`
- [ ] `workshop_viewmodel.py` L166: Replace `hasattr(item, 'id')` with `isinstance(item, Component)`
- [ ] Add Component import (TYPE_CHECKING where needed)
- [ ] Verify: tests pass

**Notes:**

### Task 5.6: Build Queue Screen — Type Validation [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k build_queue --testmon`

- [ ] L177, L183: Replace `hasattr(build_context, 'owner_id'/'name')` with isinstance or typed union
- [ ] L179: Keep `getattr(build_context, 'name', 'unknown')` in error path
- [ ] Verify: tests pass

**Notes:**

### Task 5.7: Strategy Build Queue Manager — queue_sources [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L97: Replace `getattr(self._screen.build_queue_screen, 'queue_sources', [])` with direct access
- [ ] Verify: tests pass

**Notes:**

### Task 5.8: Input Mapper — Event Typing [Simple]
**File:** `game/ui/services/input_mapper.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [ ] L204: Replace `getattr(event, "type", None)` with `event.type`. Type parameter.
- [ ] Verify: tests pass

**Notes:**

### Task 5.9: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All tests pass
- [ ] No new failures introduced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
