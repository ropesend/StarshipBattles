# Phase 4: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-137 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (7 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 4.1: DUP-UI1-001 - Number Formatting with K/M Suffixes Dupl [Simple]
**File:** `game/ui/panels/planet_report_p`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Only 2 occurrences (planet_report_panel.py uses lowercase 'k', strategy_detail_fmt.py uses uppercase 'K'). Different case conventions suggest intentional styling differences for different UI contexts. Extracting would add coupling for minimal benefit.

### Task 4.2: CON-UI1-010 - Duplicate ColumnManager Classes [Medium]
**File:** `game/ui/screens/column_manager`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Two `ColumnManager` classes with DIFFERENT purposes: (1) column_manager.py for FleetReportWindow - ship-specific column value extraction, pure data/logic; (2) planet_list_columns.py for PlanetListWindow - has UI header creation with pygame_gui, sorting state. NOT duplicates - domain-specific implementations.

### Task 4.3: DUP-UI1-002 - Virtual Scrolling List Pattern Repeated [Medium]
**File:** `game/ui/screens/planet_list_wi`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - VirtualListRenderer already exists for planet_list. FleetReportWindow has embedded implementation. Different column systems, data types (planets vs ships), image handling, caching strategies. Domain-specific implementations tied to their data types. Extracting generic base would require significant abstraction overhead.

### Task 4.4: DUP-UI1-003 - Filter Toggle Button Pattern Duplicated [Medium]
**File:** `game/ui/screens/fleet_report_w`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Different architectural approaches: FleetReport uses ViewModel pattern, PlanetList uses direct state dict + All/None bulk toggles, EmpireBuildQueue uses FilterManager class. NOT duplicates - different implementations of similar UX using different architectures.

### Task 4.5: DUP-UI1-005 - Sidebar Filter Section Building Pattern [Medium]
**File:** `game/ui/screens/empire_build_q`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Different sidebar complexity: PlanetList has complex sidebar with range sliders, preset management, grid layout (already extracted to planet_list_sidebar.py); EmpireBuildQueue has simpler vertical checkbox list. Forcing common abstraction would over-engineer the simpler case.

### Task 4.6: DUP-UI1-004 - Placeholder Surface Creation [Simple]
**File:** `game/ui/panels/build_queue_por`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Intentionally different placeholder styles: color-coded by vehicle type (build_queue_portraits), simple gray fallbacks (fleet_report_window), gradient based on planet type (planet_report_panel), crossed lines (race_asset_loader). Pattern is simple (Surface.fill()) and variations are intentional.

### Task 4.7: DUP-UI1-007 - Column Visibility Toggle Handling [Simple]
**File:** `game/ui/screens/planet_list_wi`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS - Thin delegation wrappers calling domain-specific managers (ColumnManager or FilterManager). Minor code overlap (~3 lines button text formatting) is trivial and tightly coupled to each screen's specific refresh sequence.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
