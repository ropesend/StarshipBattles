# Phase 5: Strategy Support Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add unit tests for strategy support modules: detail formatters, superweapon operations, window/panel managers, and planet list components.
**Findings covered:** TCG-UI1-013, TCG-UI1-014, TCG-UI1-015, TCG-UI1-016
**Estimated tests:** ~80-100

---

## Task 5.1: Strategy Detail Formatters [Medium]
**Finding:** TCG-UI1-013
**Source:** `game/ui/screens/strategy_detail_fmt.py` (367 lines), `game/ui/screens/strategy_detail_formatter.py` (414 lines)
**Tests:** `tests/unit/ui/screens/test_strategy_detail_fmt.py` (NEW), `tests/unit/ui/screens/test_strategy_detail_formatter.py` (NEW)
**Mocks:** Mock star, planet, fleet, warp_point objects with required attributes

### strategy_detail_fmt.py (pure formatting functions):

- [ ] Create `tests/unit/ui/screens/test_strategy_detail_fmt.py`

**format_spectrum_html():**
- [ ] Test with mock star having all spectrum values -> returns HTML with all 9 bands
- [ ] Test spectrum values use scientific notation (`.2e` format)

**format_atmosphere_raw():**
- [ ] Test with planet having atmosphere dict -> returns formatted HTML
- [ ] Test with planet having empty atmosphere -> handles gracefully

**get_label_for_object():**
- [ ] Test with star system object -> returns system name
- [ ] Test with star object -> returns star name
- [ ] Test with planet object -> returns planet name
- [ ] Test with fleet object -> returns fleet id/name
- [ ] Test with warp point object -> returns warp point label
- [ ] Test with unknown object type -> returns fallback string

**format_fleet_info():**
- [ ] Test with fleet having ships -> returns ship count and fleet stats
- [ ] Test with fleet having no ships -> handles gracefully
- [ ] Test with fleet having movement orders -> shows order type

### strategy_detail_formatter.py (StrategyDetailFormatter class):

- [ ] Create `tests/unit/ui/screens/test_strategy_detail_formatter.py`
- [ ] Test initialization stores references correctly
- [ ] Test `show_detail()` dispatches to correct format function based on object type
- [ ] Test `show_detail()` with planet updates planet report panel
- [ ] Test `show_detail()` with star shows spectrum graph
- [ ] Test `show_detail()` with fleet shows fleet info
- [ ] Test `show_detail()` with None clears detail panel
- [ ] Test `_compute_production_rate()` with planet having production complexes
- [ ] Test `_compute_production_rate()` with planet having no complexes -> returns 0

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py tests/unit/ui/screens/test_strategy_detail_formatter.py -v`

**Notes:** `strategy_detail_fmt.py` has pure functions - easiest to test. `StrategyDetailFormatter` wraps these with UI state; use bypass-init pattern.

---

## Task 5.2: Superweapon Operations [Medium]
**Finding:** TCG-UI1-014
**Source:** `game/ui/screens/strategy_superweapons.py` (410 lines)
**Tests:** `tests/unit/ui/screens/test_strategy_superweapons.py` (NEW) + existing `test_superweapon_input_modes.py`
**Mocks:** Mock scene, mock facade; mock command classes

- [ ] Create `tests/unit/ui/screens/test_strategy_superweapons.py`

**Initialization:**
- [ ] Test `__init__` stores scene and facade references
- [ ] Test property accessors (`systems`, `camera`) delegate to scene

**Planet Imploder workflow:**
- [ ] Test target selection validates target is a planet
- [ ] Test command dispatch creates QueueImplodePlanetMissionCommand
- [ ] Test invalid target (non-planet) is rejected

**Stellerator workflow:**
- [ ] Test target selection validates target is a star
- [ ] Test command dispatch creates QueueStellerateStarMissionCommand

**Warp Point operations:**
- [ ] Test open warp point creates QueueOpenWarpPointMissionCommand
- [ ] Test close warp point creates QueueCloseWarpPointMissionCommand

**Dyson Sphere:**
- [ ] Test command creates QueueCreateDysonSphereMissionCommand

**Self-Destruct:**
- [ ] Test self-destruct creates IssueSelfDestructCommand with correct fleet

**Error handling:**
- [ ] Test operation with no fleet selected -> no command dispatched
- [ ] Test operation with invalid hex coordinates -> graceful failure

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_superweapons.py tests/unit/ui/screens/test_superweapon_input_modes.py -v`

---

## Task 5.3: Planet List Components [Medium]
**Finding:** TCG-UI1-015
**Source:** `game/ui/screens/planet_list_*.py` (5 files, ~1700 lines)
**Tests:** `tests/unit/ui/screens/test_planet_list_filters.py` (existing, extend) + `tests/unit/ui/screens/test_planet_list_window.py` (NEW)
**Mocks:** Mock galaxy, planets, empire; mock pygame_gui manager

Existing tests cover: basic filter logic. Missing:

**Planet list window:**
- [ ] Create `tests/unit/ui/screens/test_planet_list_window.py` (or extend if exists)
- [ ] Test window initialization with galaxy data and empire
- [ ] Test planet list populates with correct planets for empire
- [ ] Test column sorting (by name, by population, by production)
- [ ] Test filter application narrows planet list
- [ ] Test filter combination (multiple filters active)

**Column management:**
- [ ] Test column configuration (visible/hidden columns)
- [ ] Test column sorting toggle (ascending/descending)
- [ ] Test column width calculation

**Preset system:**
- [ ] Test preset save stores current filter/column state
- [ ] Test preset load restores filter/column state
- [ ] Test preset with no saved presets -> returns empty list

**Filter edge cases:**
- [ ] Test filter with no matching planets -> shows empty list
- [ ] Test filter with all planets matching -> shows full list
- [ ] Test filter reset clears all active filters

- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_list_filters.py tests/unit/ui/screens/test_planet_list_window.py -v`

---

## Task 5.4: Window and Panel Managers [Medium]
**Finding:** TCG-UI1-016
**Source:** `game/ui/screens/strategy_window_manager.py` (460 lines), `game/ui/screens/strategy_panel_manager.py` (476 lines)
**Tests:** `tests/unit/ui/screens/test_strategy_window_manager.py` (NEW), `tests/unit/ui/screens/test_strategy_panel_manager.py` (NEW)
**Mocks:** Mock pygame_gui manager, mock window classes, mock scene

### StrategyWindowManager:

- [ ] Create `tests/unit/ui/screens/test_strategy_window_manager.py`
- [ ] Test initialization sets all window refs to None
- [ ] Test `open_planet_list()` creates PlanetListWindow and stores reference
- [ ] Test `open_planet_list()` when already open -> no-op or closes/reopens
- [ ] Test `close_planet_list()` destroys window and sets ref to None
- [ ] Test `open_fleet_report()` creates FleetReportWindow
- [ ] Test `open_build_queue_list()` creates BuildQueueListWindow
- [ ] Test `open_event_log()` creates EventLogWindow
- [ ] Test window close callback clears window reference
- [ ] Test opening multiple windows simultaneously

### StrategyPanelManager:

- [ ] Create `tests/unit/ui/screens/test_strategy_panel_manager.py`
- [ ] Test initialization creates panel layout
- [ ] Test `handle_resize()` recalculates panel positions
- [ ] Test panel creation with different screen sizes
- [ ] Test widget reference storage (StrategyWidgets dataclass)
- [ ] Test system tree panel creation
- [ ] Test detail panel creation

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_window_manager.py tests/unit/ui/screens/test_strategy_panel_manager.py -v`

**Notes:** Window manager methods typically create pygame_gui windows. Mock the window classes and verify they're instantiated with correct parameters.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests passing
- [ ] No regressions: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
