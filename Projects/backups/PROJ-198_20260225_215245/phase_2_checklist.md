# Phase 2: Init Declarations & Guard Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-198 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add missing `__init__` declarations for dynamically-set attributes, then remove the hasattr guards that check for them.

---

## Tasks

### Task 2.1: StrategyScreen — build_queue_screen Init [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [x] Add `self.build_queue_screen = None` in `__init__` (near L110)
- [x] `strategy_event_router.py` L58: Remove `hasattr(...)`. Use `if self.ui.scene.build_queue_screen is not None:`
- [x] `strategy_input_handler.py` L56: Remove `hasattr(...)`. Use `if self.scene.build_queue_screen is not None:`
- [x] `strategy_build_queue_manager.py` L44: Remove `hasattr(...)`. Use `if self._screen.build_queue_screen is not None:`
- [x] `strategy_build_queue_manager.py` L155: Same pattern
- [x] `strategy_build_queue_manager.py` L202: Same pattern
- [x] `screenshot_manager.py` L155: Remove `hasattr(...)`. Use `if scene.build_queue_screen:`
- [x] Verify: tests pass

**Notes:** Also updated `strategy_screen.py` L204 self-reference.

### Task 2.2: Ship — crew_onboard / crew_required Init [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

- [x] Add `self.crew_onboard: int = 0` in `__init__`
- [x] Add `self.crew_required: int = 0` in `__init__`
- [x] `battle_ui_service.py` L205-206: Replace getattr with direct access
- [x] Verify: tests pass

**Notes:** Crew stats now initialized to 0 in Ship.__init__, removed getattr fallbacks.

### Task 2.3: Ship & Projectile — id Attribute [Simple]
**File:** `game/simulation/entities/ship.py`, `game/simulation/entities/projectile.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

- [x] Add `self.id: str = str(id(self))` in `Ship.__init__`
- [x] Add `self.id: str = str(id(self))` in `Projectile.__init__`
- [x] `battle_ui_service.py` L180: Replace `getattr(ship, 'id', id(ship))` with `ship.id`
- [x] `battle_ui_service.py` L264: Replace `getattr(proj, 'id', id(proj))` with `proj.id`
- [x] `battle_panels.py` L71-79: Simplify `_get_ship_id` to use `.id`
- [x] `battle_panels.py` L275-279: Simplify `_get_projectile_id` to use `.id`
- [x] Verify: tests pass

**Notes:** Simplified helper functions to single-line `.id` access. Deleted 4 obsolete tests that tested fallback behavior.

### Task 2.4: ComponentListItem — is_hovered Init [Simple]
**File:** `game/ui/screens/builder/components.py`
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`

- [x] Add `self.is_hovered: bool = False` in `ComponentListItem.__init__`
- [x] `builder/left_panel.py` L352: Replace getattr with `item.is_hovered`
- [x] Verify: tests pass

**Notes:**

### Task 2.5: DesignSelectorWindow — design_rows Init [Simple]
**File:** `game/ui/screens/design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k design --testmon`

- [x] Add `self.design_rows = []` in `__init__` before call to `_refresh_designs()`
- [x] L285: Remove `hasattr(self, 'design_rows')` guard. Keep for-loop body.
- [x] Verify: tests pass

**Notes:**

### Task 2.6: BuilderLeftPanel — _dropdown_expanded Init [Simple]
**File:** `game/ui/screens/builder/left_panel.py`
**Tests:** `pytest tests/unit/ui/screens/builder/ --testmon`

- [x] Add `self._dropdown_expanded: bool = False` in `__init__`
- [x] L214: Replace `getattr(self, '_dropdown_expanded', False)` with `self._dropdown_expanded`
- [x] Verify: tests pass

**Notes:**

### Task 2.7: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All tests pass (12728 passed, 1 skipped)
- [x] No new failures introduced

**Notes:** Deleted 5 obsolete tests that tested getattr fallback behavior that no longer exists:
- TestBattleUIServiceDefensiveFallbacks.test_ship_without_crew_attributes_uses_defaults
- TestShipStatsPanelExtended.test_get_ship_id_fallback_to_name
- TestShipStatsPanelExtended.test_get_ship_id_fallback_to_python_id
- TestSeekerMonitorPanelExtended.test_get_projectile_id_fallback_to_python_id
Updated mock fixtures to include `.id` attribute.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
