# Phase 2: Simple Shim Removals

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove simple backward compatibility shims with few callers. Each task affects 1-3 callers.

---

## Tasks

### Task 2.1: Remove deprecated GameSession parameters [Simple]
**Finding:** LEG-STR-003
**File:** `game/strategy/engine/game_session.py:61-84`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -n 12`

- [ ] Remove `galaxy_radius` and `system_count` parameters from `__init__` signature (line 61)
- [ ] Delete the deprecation warning blocks (lines 66-84): the `if galaxy_radius is not None` and `if system_count is not None` blocks
- [ ] Remove `import warnings` if no longer needed
- [ ] Grep for callers: `GameSession(.*galaxy_radius|GameSession(.*system_count`
- [ ] Update any callers to use `GameConfig(galaxy_radius=..., system_count=...)` instead
- [ ] Update test callers similarly
- [ ] Verify: no DeprecationWarning in test output for GameSession

**Notes:**

---

### Task 2.2: Remove hasattr() defensive checks for Fleet properties [Simple]
**Finding:** LEG-STR-004
**Files:**
- `game/strategy/services/fleet_navigation_service.py:94`
- `game/strategy/data/pathfinding.py:178, 317`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -n 12`

- [ ] In `fleet_navigation_service.py:94` (NavigationState.from_fleet): change `fleet.can_use_warp() if hasattr(fleet, 'can_use_warp') else True` to `fleet.can_use_warp()`
- [ ] In `pathfinding.py:178`: change `if fleet is not None and hasattr(fleet, 'can_use_warp')` to `if fleet is not None`
- [ ] In `pathfinding.py:317`: change `chaser.can_use_warp() if hasattr(chaser, 'can_use_warp') else True` to `chaser.can_use_warp()`

**Notes:**

---

### Task 2.3: Remove hasattr() for Facility.construction_queue [Simple]
**Finding:** LEG-STR-005
**File:** `game/strategy/engine/production_engine.py:120`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Change `if hasattr(facility, 'construction_queue') and facility.construction_queue:` to `if facility.construction_queue:`

**Notes:**

---

### Task 2.4: Remove deprecated base_path parameter from ShipThemeManager [Simple]
**Finding:** LEG-UI2-004
**File:** `game/ui/assets/ship_theme_manager.py:94, 100-101`
**Tests:** `pytest tests/unit/ui/ tests/unit/entities/test_ship_theme_logic.py -n 12`

- [ ] Remove `base_path=None` parameter from `initialize()` signature (line 94)
- [ ] Delete line 101: `self.base_path = base_path`
- [ ] Delete `self.base_path = None` from `__init__` (line 64)
- [ ] Grep for callers: `\.initialize\(.*base_path` and update any that pass base_path
- [ ] Verify: all callers in `game/app.py`, `game/ui/screens/workshop_screen.py` etc.

**Notes:**

---

### Task 2.5: Remove deprecated turn_engine property from StrategyScreen [Simple]
**Finding:** LEG-UI2-005
**File:** `game/ui/screens/strategy_screen.py:139-148`
**Tests:** `pytest tests/unit/ui/screens/ -n 12`

- [ ] Delete the `turn_engine` property (lines 139-148)
- [ ] Grep for callers of `strategy_screen.turn_engine` or `self.turn_engine` within strategy_screen
- [ ] Note: `_show_scuttle_notifications` (line 344) accesses `self.session.turn_engine` directly, NOT through the deprecated property - this is fine
- [ ] Grep callers in `game/ui/screens/strategy_detail_formatter.py` and migrate to facade methods
- [ ] Update any remaining callers to use `self.session.turn_engine` or facade methods

**Notes:**

---

### Task 2.6: Remove WorkshopViewModel.selected_component alias [Simple]
**Finding:** LEG-UI1-006
**File:** `game/ui/screens/workshop_viewmodel.py:124-127`
**Tests:** `pytest tests/unit/workshop/ tests/unit/builder/ -n 12`

- [ ] Delete the `selected_component` property (lines 124-127)
- [ ] Grep callers: `selected_component` in game/ui/screens/builder/ and game/ui/screens/workshop_
- [ ] Rename all callers to use `primary_selection` instead
- [ ] Callers found in: `builder/main.py`, `builder/schematic_view.py`, `builder/state_manager.py`, `workshop_event_router.py`, `workshop_screen.py`, `workshop_data_reloader.py`, `builder/interaction_controller.py`
- [ ] Update each file's usage

**Notes:**

---

### Task 2.7: Remove deprecated action flag in StrategyScreen.on_design_click [Simple]
**Finding:** LEG-UI2-002
**File:** `game/ui/screens/strategy_screen.py:633-636`
**Tests:** `pytest tests/unit/ui/screens/ -n 12`

- [ ] Delete the `else` branch (lines 633-636): the fallback setting `workshop_context_data` and `action_open_design = True`
- [ ] Grep for `action_open_design` to find any reader (game/ui/screens/strategy_event_router.py, tests)
- [ ] Remove `self.action_open_design = False` from `__init__` (line 104) if no readers remain
- [ ] Update any tests that check `action_open_design`

**Notes:**

---

### Task 2.8: Rename legacy_components.py to modifier_editor.py [Simple]
**Finding:** LEG-UI1-007, LEG-UI2-008
**File:** `game/ui/screens/builder/legacy_components.py`
**Tests:** `pytest tests/unit/builder/ -n 12`

- [ ] Rename file from `legacy_components.py` to `modifier_editor.py`
- [ ] Update import in `game/ui/screens/builder/main.py:45`: change `from game.ui.screens.builder.legacy_components import` to `from game.ui.screens.builder.modifier_editor import`
- [ ] Grep for any other imports of `legacy_components`
- [ ] Update any test imports

**Notes:**

---

### Task 2.9: Remove misleading "backward compatibility" comments [Simple]
**Finding:** LEG-STR-010, LEG-STR-013, LEG-STR-014, LEG-STR-012
**Files:**
- `game/strategy/engine/game_session.py:108` - "Convenience references for backward compatibility"
- `game/strategy/data/classification_config.py:16,20` - "ensure backward compatibility if JSON loading fails"
- `game/strategy/facade/strategy_session_facade.py:432-436` - "legacy behavior"
- `game/strategy/data/empire.py:155-158` - "backwards compatibility"
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] In game_session.py:108: Change comment to "Convenience references for common empires"
- [ ] In classification_config.py:16,20: Change comment to "Default values if JSON loading fails"
- [ ] In strategy_session_facade.py:432-436: Change "legacy behavior" to "Defensive fallback - returns empty dict to prevent UI crash during initialization"
- [ ] In empire.py:155-158: Change "backwards compatibility" to "Optional visual identity fields"

**Notes:**

---

### Task 2.10: Remove migration guide documentation from fleet_navigation_service [Simple]
**Finding:** LEG-STR-009
**File:** `game/strategy/services/fleet_navigation_service.py:9-53`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Delete the "Migration Guide" block from the module docstring (lines 9-53)
- [ ] Keep only the first paragraph of the docstring (lines 1-7) and the architecture section (lines 44-53)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (8164 baseline)
- [ ] No DeprecationWarnings for GameSession or turn_engine in test output
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
