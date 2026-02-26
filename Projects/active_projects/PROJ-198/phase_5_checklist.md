# Phase 5: Type Annotations & Protocol Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-198 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add type annotations to untyped parameters to enable removing remaining hasattr/getattr guards.

---

## Tasks

### Task 5.1: Battle UI Service — Type Parameters [Medium]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [x] Add TYPE_CHECKING imports for Ship, Component, Projectile, ICombatShip - Already present
- [x] Type conversion method parameters - Already typed
- [x] L170, L176: Replace `hasattr(target, 'name')` with direct access (target is always Ship)
- [x] L260: Same pattern for projectile target
- [x] Verify: tests pass

**Notes:** Targets are always Ships (ICombatShip protocol), so hasattr removed.

### Task 5.2: Battle Panels — Scene Typing [Medium]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [x] Add TYPE_CHECKING import for BattleScreen - Not needed, using direct access
- [x] Type `self.scene` as BattleScreen - Implicit via usage
- [x] L47: Remove `getattr(self.scene, 'ui_service', None)` fallback → direct access
- [x] L489-491: Remove `hasattr(self.scene, 'test_mode')` and `hasattr(self.scene, 'is_battle_over')`
- [x] Verify: tests pass

**Notes:** BattleScreen always has these attributes. Kept getattr fallback for ships for test mocks.

### Task 5.3: Screenshot Manager — Scene Typing [Simple]
**File:** `game/ui/services/screenshot_manager.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [x] Add TYPE_CHECKING import for StrategyScreen - Not needed
- [x] Type the scene parameter - Implicit
- [x] L149: Remove `hasattr(scene, 'ui')`. Use `if scene.ui:` directly.
- [x] L161-162: Replace getattr with direct access to `SIDEBAR_WIDTH` / `TOP_BAR_HEIGHT`
- [x] Verify: tests pass

**Notes:** StrategyScreen always has these attributes.

### Task 5.4: Strategy Input Handler — Modal Check [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [x] L163-165: Remove double `hasattr`. Call `self.scene.ui._has_modal_open()` directly.
- [x] Verify: tests pass

**Notes:** StrategyScreen.ui always has _has_modal_open method.

### Task 5.5: Builder Type Discrimination [Simple]
**Files:** `game/ui/screens/builder/detail_panel.py`, `builder_selection.py`, `workshop_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`

- [x] `detail_panel.py` L95: Keep `hasattr(selection_data, 'id')` - explicit duck type for test compatibility
- [x] `builder_selection.py` L22: Keep `hasattr(item, 'id')` - wrapped in _is_component_like() helper
- [x] `workshop_viewmodel.py` L166: Keep `hasattr(item, 'id')` - documented duck type for test compatibility
- [x] Verify: tests pass

**Notes:** These are intentional duck type checks because selection logic accepts both real Component instances and mock objects in tests. The selection logic only needs the 'id' attribute. Documented with comments explaining the rationale.

### Task 5.6: Build Queue Screen — Type Validation [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k build_queue --testmon`

- [x] L177, L183: Keep hasattr checks - these are intentional validation of interface contract
- [x] L179: Keep `getattr(build_context, 'name', 'unknown')` in error path
- [x] Verify: tests pass

**Notes:** The hasattr checks here are validation code to ensure callers pass proper objects with required attributes (owner_id, name). This is not duck typing for functionality but interface contract validation. Keeping as-is is correct.

### Task 5.7: Strategy Build Queue Manager — queue_sources [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [x] L97: Already using direct access `self._screen.build_queue_screen.queue_sources`
- [x] Verify: tests pass

**Notes:** No changes needed - already fixed in earlier phase.

### Task 5.8: Input Mapper — Event Typing [Simple]
**File:** `game/ui/services/input_mapper.py`
**Tests:** `pytest tests/unit/ui/services/ --testmon`

- [x] L204: Replace `getattr(event, "type", None)` with `event.type`. Type parameter as `pygame.event.Event`.
- [x] Verify: tests pass

**Notes:** Event is now properly typed as pygame.event.Event.

### Task 5.9: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All tests pass
- [x] No new failures introduced

**Notes:** 12728 passed, 1 skipped

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
