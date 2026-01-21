# PROJ-03: Fleet Report Window

## Overview
Create a comprehensive Fleet Report window for the strategy layer that displays detailed fleet information, ship listings with filtering/sorting, and individual ship status reports with damage tracking.

## Goals
- Add a "Fleet Report" button that appears when a fleet is selected
- Create a split-panel window similar to Planet List for fleet management
- Display fleet summary statistics (ships, tonnage, movement, supplies, endurance)
- Show filterable/sortable ship list with reorderable columns
- Show detailed ship report with current stats and component damage
- Implement ship serial numbers (unique identifiers per design)

## Scope
**In Scope:**
- Fleet Report button in strategy layer bottom-right detail panel
- Fleet Report Window with three-section layout:
  - Left panel: Fleet summary, management buttons, filters
  - Center panel: Ship list with virtual scrolling
  - Right panel: Ship detail report (Design Workshop-style with damage)
- Ship filtering by: abilities, size class, damage status
- Ship list columns: portrait, unique ID, design, name, movement, damage %
- Sortable and reorderable column headers (matching Planet List pattern)
- Ship serial number system per design
- Component damage display with collapsible/stackable view

**Out of Scope:**
- Fleet combat simulation
- Ship transfer between fleets (separate feature)
- Fleet renaming (could be added later)
- Fleet formation preview

## Current State
**Last Updated:** 2026-01-21
**Current Phase:** Phase 5 Complete - Ready for Phase 6
**Last Agent Action:** Completed Phase 5 (Filters and Column Configuration) - added filter toggle buttons and column visibility toggles to sidebar
**Next Action:** Begin Phase 6 (Polish and Integration) - add screenshot support, resize handling, fleet state changes
**Blockers:** None
**Context for Next Agent:**
- Phase 1 complete: Serial number system (16 tests)
- Phase 2 complete: Basic window functional with 3-panel layout
- Phase 3 complete: Enhanced summary panel (18 tests)
- Phase 4 complete: Ship detail panel with damage display (21 tests)
- Phase 5 complete: Filters and column configuration
  - Added filter toggle buttons in sidebar:
    - Show Damaged (default: on)
    - Show Undamaged (default: on)
    - Show Derelict (default: on)
    - Show Destroyed (default: off)
  - Added column visibility toggles in sidebar:
    - Each column (except icon) has a `[x] Title` / `[ ] Title` toggle button
    - Toggling a column rebuilds headers and row pool
  - Added `update()` method to FleetReportWindow:
    - Handles filter button clicks via `_toggle_filter(filter_id)`
    - Handles column button clicks via `_toggle_column(col_id)`
  - Uses `btn.check_pressed()` pattern from PlanetListWindow
  - Filter logic already existed in fleet_report_filters.py (Phase 3)
  - 243 total strategy tests passing
- Phase 6 needs: Screenshot support (F12), window resize handling, fleet state change refresh
- Manual testing recommended: Toggle filters and columns to verify list updates correctly

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Strategy Screen UI | `game/ui/screens/strategy_screen.py` | `StrategyScreenUI` |
| Strategy Scene | `game/ui/screens/strategy_scene.py` | `StrategyScene` |
| Input Handler | `game/ui/screens/strategy_input_handler.py` | `StrategyInputHandler` |
| Planet List Window | `game/ui/screens/planet_list_window.py` | `PlanetListWindow` |
| Fleet Data Model | `game/strategy/data/fleet.py` | `Fleet` |
| Ship Instance | `game/strategy/data/ship_instance.py` | `ShipInstance` |
| Ship Combat Model | `game/simulation/entities/ship.py` | `Ship` |
| Design Report Panel | `game/ui/panels/design_report_panel.py` | `DesignReportPanel` |
| Stats Config | `ui/builder/stats_config.py` | Stats definitions |
| Stats Display | `ui/builder/right_panel.py` | `BuilderRightPanel`, `StatRow` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Serial numbers: Global unique + per-design serial display | User wants every ship to have a unique numerical ID (never duplicates), plus a human-friendly serial starting at 1 per design. Display format: "DesignName-000001" |
| 2026-01-21 | Fleet summary: Include all stat categories | Combat stats (firepower, HP%, shields), logistics (fuel rate, supply days), and composition (class breakdown, damaged count, abilities) |
| 2026-01-21 | Component damage: Collapsible groups by layer | Group components by layer (Hull, Core, etc.) with expand/collapse. Show damage % per component when expanded |
| 2026-01-21 | Window size: Match Planet List | Same size and proportions as Planet List for UI consistency |

## Initial Analysis

### Architecture Findings

**Strategy Layer Structure:**
- Main UI in `strategy_screen.py` (847 lines) with 4 main panels
- Detail panel (bottom-right) shows contextual buttons when objects selected
- Fleet selection handled in `strategy_scene.py:291-313`
- Button events routed through `strategy_input_handler.py:56-74`

**Existing Patterns to Follow:**
- `PlanetListWindow` (908 lines) - exact pattern for Fleet Report:
  - Sidebar with filters and column toggles
  - Virtual scrolling with row pool for performance
  - Sortable/reorderable column headers
  - Preset system for saved configurations
- `FleetOrdersWindow` - existing fleet-specific window pattern

**Ship Data Model:**
- `ShipInstance` (strategy layer) tracks: instance_id (UUID), design_id, name, owner_id, current_hp, component_damage dict, resource_levels, is_destroyed, is_derelict, experience, kills, battles_survived
- `Ship` (combat layer) has full component/resource system
- **Gap Found:** No serial number system exists - ships use UUIDs, not human-readable sequential IDs

**Stats Display System:**
- `DesignReportPanel` already exists for reusable ship stats display
- Uses `StatRow` class for label/value/unit rows
- `stats_config.py` has getter functions including `get_resource_current()` for damage states
- Layer status already shows damage percentages

### Key Technical Findings

1. **Serial Numbers Need Implementation:**
   - Currently ships use UUID (`instance_id`)
   - Need to add per-design serial counter (e.g., "Battleship-000001")
   - Could store counter on Empire or globally

2. **Component Damage Already Trackable:**
   - `ShipInstance.component_damage` stores `{component_id: current_hp}`
   - Can calculate damage % per component
   - `get_resource_current()` getter already exists in stats_config.py

3. **Fleet Stats to Calculate:**
   - Total ships: `len(fleet.ships)`
   - Total tonnage: Sum of ship masses from design_data
   - Movement per turn: `fleet.speed` (default 5.0)
   - Supplies: Sum of fuel/energy/ammo from ship_instance.resource_levels
   - Endurance: Needs calculation (total fuel / consumption rate?)

4. **Button Placement:**
   - Existing buttons at `y = rect_detail.height - 50`
   - Buttons are 120px wide x 40px tall
   - Current positions: x=80 (Orders), x=220 (Colonize), x=350 (Build Yard)
   - Fleet Report could go at x=80 alongside Orders when fleet selected

---

## Swarm Findings Summary

### Architecture Analysis

**Recommended File Structure:**
```
game/ui/screens/fleet_report_window.py       # Main window (UIWindow subclass)
game/ui/screens/fleet_report_filters.py      # Filter/sort logic (like planet_list_filters.py)
game/ui/panels/fleet_summary_panel.py        # Fleet stats panel
game/ui/panels/ship_list_panel.py            # Scrollable ship list with row pool
game/ui/panels/ship_detail_panel.py          # Ship detail with damage (wraps DesignReportPanel)
```

**Module Boundaries:**
- `FleetReportWindow` coordinates all panels, manages state
- Panels are self-contained, communicate via callbacks
- Filter logic separated for testability (like `planet_list_filters.py`)

**Data Flow:**
```
Fleet.get_ship_instances() → List[ShipInstance]
    ↓
ShipInstance.design_data['expected_stats'] → max_hp, mass, resources
ShipInstance.current_hp, component_damage, resource_levels → current state
    ↓
FleetReportWindow displays aggregated stats + individual ship details
```

### Key Patterns to Reuse

| Pattern | Source File | Lines | Use For |
|---------|-------------|-------|---------|
| Virtual Scrolling | `planet_list_window.py` | 126-137, 523-649 | Ship list with 100+ ships |
| Column Config | `planet_list_window.py` | 53-75 | Sortable/reorderable columns |
| Filter Panel | `planet_list_window.py` | 184-388 | Damage/status/ability filters |
| Stat Rows | `ui/builder/right_panel.py` | 21-62 | Ship stats display |
| Report Panel | `design_report_panel.py` | 28-102 | Ship detail with portrait |
| Collapsible Sections | `layer_panel.py` | 91-98 | Component damage groups |
| Window Pattern | `fleet_orders_window.py` | 8-59 | UIWindow subclass structure |

### Dependencies Map

**Required Imports for FleetReportWindow:**
```python
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
from ui.builder.stats_config import STATS_CONFIG
from ui.builder.right_panel import StatRow
from game.ui.panels.design_report_panel import DesignReportPanel
```

**Files to Modify:**
- `game/ui/screens/strategy_screen.py` - Add Fleet Report button + window management
- `game/ui/screens/strategy_input_handler.py` - Add button event handler
- `game/strategy/data/ship_instance.py` - Add serial number field
- `game/strategy/data/empire.py` - Add serial counter persistence

### Risks Identified

| Risk | Severity | Mitigation |
|------|----------|------------|
| Ship destroyed while viewing | HIGH | Use weak references + validation before display |
| Fleet disbanded while window open | CRITICAL | Check fleet existence, close window gracefully |
| Turn advancement race condition | HIGH | Version stamping on ShipInstance |
| Large fleets (100+ ships) | MEDIUM-HIGH | Virtual scrolling with row pool pattern |
| Serial counter overflow (100000) | MEDIUM | Use 6-digit limit, warn at 90000 |
| Serial persistence on save/load | HIGH | Add to Empire.to_dict/from_dict |

### Test Requirements

**New Test Files Needed:**
- `tests/unit/strategy/test_fleet_report_window.py`
- `tests/unit/strategy/test_ship_serial_numbering.py`
- `tests/unit/ui/test_fleet_report_ui.py`

**Key Test Scenarios:**
- Fleet stats calculation (total HP, tonnage, damage %)
- Ship filtering by damage status, class, abilities
- Serial number generation and persistence
- Window behavior with empty/destroyed/derelict ships

---

## Phases

### Phase 1: Serial Number System [Medium]
**Objective:** Implement ship serial numbers that persist across saves
**Status:** Complete

#### Task 1.1: Add Serial Number Field to ShipInstance [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_serial_numbering.py`
- [x] Add `serial: Optional[int] = None` field to ShipInstance dataclass (after line 51)
- [x] Update `to_dict()` to include `'serial': self.serial` (line ~295)
- [x] Update `from_dict()` to restore `serial=data.get('serial')` (line ~315)
- [x] Add `get_display_id()` method that returns `f"{design_name}-{serial:06d}"` if serial exists
**Notes:** Added TYPE_CHECKING import for Empire to avoid circular import.

#### Task 1.2: Add Serial Counter to Empire [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/test_ship_serial_numbering.py`
- [x] Add `_design_serial_counters: Dict[str, int] = {}` in `__init__` (after line 20)
- [x] Add method `get_next_serial(design_id: str) -> int` that increments and returns counter
- [x] Update `to_dict()` to include `'_design_serial_counters': self._design_serial_counters` (line ~55)
- [x] Update `from_dict()` to restore counters (line ~85)
**Notes:** Used dict instead of dataclass field since Empire is not a dataclass.

#### Task 1.3: Assign Serial on Ship Construction [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_serial_numbering.py`
- [x] Update `create()` classmethod to accept optional `empire` parameter (line ~55)
- [x] If empire provided, call `empire.get_next_serial(design_id)` and assign to instance
- [x] Update all callers of `ShipInstance.create()` to pass empire when available
**Notes:** Updated `game/strategy/engine/turn_engine.py:213` to pass empire.

#### Task 1.4: Unit Tests for Serial Numbers [Simple]
**File:** `tests/unit/strategy/test_ship_serial_numbering.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_serial_numbering.py`
- [x] Test serial counter increments correctly per design
- [x] Test different designs have independent counters
- [x] Test serial persists through save/load cycle
- [x] Test display ID format "DesignName-000001"
**Notes:** Created 16 tests covering EmpireSerialCounter, ShipInstanceSerial, ShipInstanceDisplayId, and ShipCreationWithEmpire.

---

### Phase 2: Fleet Report Window Foundation [Complex]
**Objective:** Create the basic window structure with ship list
**Status:** Complete

#### Task 2.1: Create FleetReportWindow Class [Medium]
**File:** `game/ui/screens/fleet_report_window.py` (NEW)
**Tests:** Manual - open window from strategy screen
- [x] Create class extending `pygame_gui.elements.UIWindow`
- [x] Initialize with `rect`, `manager`, `fleet`, `on_close_callback`
- [x] Set window title to `f"Fleet Report: {fleet.id}"`
- [x] Create main layout: left sidebar (300px), center list area, right detail panel
- [x] Implement `kill()` to call callback and cleanup
**Notes:** Created comprehensive FleetReportWindow with three-panel layout, basic summary in sidebar, ship list with virtual scrolling, and placeholder detail panel.

#### Task 2.2: Create Ship List Panel with Virtual Scrolling [Complex]
**File:** `game/ui/screens/fleet_report_window.py` (integrated)
**Tests:** Manual - scroll through 50+ ships
- [x] Define columns: icon (50px), serial ID (130px), design (100px), name (120px), HP% (80px), status (100px)
- [x] Implement `_rebuild_row_pool()` for visible rows + buffer
- [x] Implement `_update_visible_rows()` with dirty tracking
- [x] Implement column sorting by clicking headers
- [ ] Implement column reordering with left/right arrow buttons (deferred to Phase 5)
- [x] Ship selection callback structure (placeholder)
**Notes:** Integrated into FleetReportWindow rather than separate file. Column reordering deferred to Phase 5 with other column configuration features.

#### Task 2.3: Add Fleet Report Button to Strategy Screen [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual - select fleet, verify button appears
- [x] Add `self.btn_fleet_report = UIButton(...)` in `__init__` (line ~277)
- [x] Position at `x=210` (next to Orders button), same y and size
- [x] Set `visible=0` initially
- [x] In `show_detailed_report()`, show button when fleet selected (line ~524)
- [x] Add `self.fleet_report_window = None` reference (line ~29)
**Notes:** Button positioned at x=210 to avoid overlap with Orders button at x=80.

#### Task 2.4: Wire Button Event Handler [Simple]
**File:** `game/ui/screens/strategy_screen.py` (integrated with UI)
**Tests:** Manual - click button, window opens
- [x] Add handler in `handle_event()` for btn_fleet_report (line ~727)
- [x] Handler calls `self.open_fleet_report_window(obj)` when fleet selected
**Notes:** Handler integrated into strategy_screen.py rather than separate input_handler.py.

#### Task 2.5: Add Window Open Method to Strategy Scene [Simple]
**File:** `game/ui/screens/strategy_screen.py` (StrategyInterface)
**Tests:** Manual - window opens centered
- [x] Add `open_fleet_report_window(self, fleet)` method
- [x] Create window centered on screen, size 1200x700 (matching PlanetListWindow)
- [x] Store reference in `self.fleet_report_window`
- [x] Add callback `_on_fleet_report_closed()` to clear reference on close
**Notes:** Method added to StrategyInterface class for consistency with open_orders_window pattern.

---

### Phase 3: Fleet Summary Panel [Medium]
**Objective:** Display comprehensive fleet statistics
**Status:** Complete

#### Task 3.1: Create Fleet Summary Panel [Medium]
**File:** `game/ui/screens/fleet_report_window.py` (integrated)
**Tests:** Manual - verify stats display correctly
- [x] Enhanced sidebar with dedicated sections (COMBAT STATUS, LOGISTICS)
- [x] **Combat Stats Section:**
  - Ships (combat capable / total)
  - Average HP %
  - Damaged count
  - Derelict count
- [x] **Logistics Section:**
  - Total Tonnage
  - Fleet Speed
  - Fuel Level (current/max, percentage)
  - Energy Level (current/max, percentage)
**Notes:** Integrated directly into FleetReportWindow sidebar rather than separate panel. Stats use calculate_fleet_stats() function.

#### Task 3.2: Create Fleet Stats Calculator [Simple]
**File:** `game/ui/screens/fleet_report_filters.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_fleet_report_filters.py`
- [x] Create `calculate_fleet_stats(ships) -> Dict` function
- [x] Calculate: ship_count, combat_capable_count, total_tonnage, avg_hp_percent
- [x] Calculate: total_fuel, max_fuel, total_energy, max_energy
- [x] Calculate: damaged_count, derelict_count
- [x] Create `filter_ships(ships, filter_state)` function
- [x] Create `sort_ships(ships, sort_column, descending)` function
**Notes:** Created 18 unit tests covering all stats calculation and filtering logic.

#### Task 3.3: Integrate Summary Panel into Window [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual - summary displays in window
- [x] Update _update_summary() to use calculate_fleet_stats()
- [x] Update _apply_filters() to use filter_ships()
- [x] Update _apply_sort() to use sort_ships()
- [x] Summary displays in left sidebar, 300px wide
**Notes:** Full integration complete. Summary auto-updates when refresh_list() is called.

---

### Phase 4: Ship Detail Panel with Damage [Medium]
**Objective:** Show selected ship details with component damage breakdown
**Status:** Complete

#### Task 4.1: Create Ship Detail Panel Wrapper [Medium]
**File:** `game/ui/panels/ship_detail_panel.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_detail_panel.py` (21 tests)
- [x] Create `ShipDetailPanel` class (standalone, not wrapping DesignReportPanel)
- [x] Add method `update_ship(ship_instance: ShipInstance)`
- [x] Display current HP/resources vs max (not just max)
- [x] Add status display (OK/DAMAGED/DERELICT/DESTROYED)
- [x] Added helper methods to ShipInstance: get_status_text(), get_hp_display(), get_resource_display()
**Notes:** Created standalone panel rather than wrapping DesignReportPanel for simpler implementation. Added 21 unit tests.

#### Task 4.2: Add Collapsible Component Damage Section [Complex]
**File:** `game/ui/panels/ship_detail_panel.py`
**Tests:** `pytest tests/unit/strategy/test_ship_detail_panel.py::TestShipInstanceLayerInfo`
- [x] Add component damage section below main stats
- [x] Group components by layer (HULL, CORE, INNER, OUTER, ARMOR)
- [x] Each layer header is clickable button to expand/collapse
- [x] Collapsed: show layer name + damage count + "▶"
- [x] Expanded: show each component with name and HP
- [x] Color coding: get_damage_color() returns Green/Yellow/Red/Gray
- [x] Track expanded state in `expanded_layers: Dict[str, bool]`
**Notes:** Added get_components_by_layer() and get_damaged_components_by_layer() to ShipInstance for layer grouping.

#### Task 4.3: Integrate Detail Panel into Window [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual - click ship in list, detail updates
- [x] Import and create `ShipDetailPanel` in right section
- [x] Position: right side, fills detail_panel container
- [x] Added row click handling via _handle_row_click() to select ships
- [x] Show placeholder "Select a ship" when no selection
- [x] Forward events to ShipDetailPanel for layer toggle buttons
**Notes:** Integration complete. Row clicks select ships and update detail panel.

---

### Phase 5: Filters and Column Configuration [Medium]
**Objective:** Add filtering and column customization
**Status:** Complete

#### Task 5.1: Create Filter Panel [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual - filters update ship list
- [x] Add filter section to left sidebar (below summary)
- [x] **Status Filters (toggle buttons):**
  - [Damaged] / Damaged toggle (default on)
  - [Undamaged] / Undamaged toggle (default on)
  - [Derelict] / Derelict toggle (default on)
  - [Destroyed] / Destroyed toggle (default off)
- [ ] **Class Filter (multi-select buttons):** - Deferred to future enhancement
- [ ] **Ability Filter (dropdown):** - Deferred to future enhancement
- [x] Wire filters via `_toggle_filter()` which calls `refresh_list()`
**Notes:** Implemented status filters using UIButton toggle pattern. Class/ability filters deferred.

#### Task 5.2: Implement Filter Logic [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_report_filters.py` (18 tests)
- [x] Create `filter_ships(ships, filter_state) -> List[ShipInstance]` function
- [x] Filter by damage status (damaged, undamaged, derelict, destroyed)
- [x] Create `sort_ships(ships, sort_column, descending) -> List[ShipInstance]` function
**Notes:** Completed in Phase 3. Filter logic already tested and working.

#### Task 5.3: Add Column Visibility Toggles [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual - toggle columns, list updates
- [x] Add "COLUMNS" section to sidebar (below filters)
- [x] Add toggle button for each column: `[x] Column Name` / `[ ] Column Name`
- [x] Wire toggles via `_toggle_column()` which calls `_rebuild_headers()`, `_rebuild_row_pool()`, `refresh_list()`
- [ ] Persist column state - Deferred (no preset system in fleet report yet)
**Notes:** Column toggles implemented. State persistence deferred to Phase 6 or future enhancement.

---

### Phase 6: Polish and Integration [Simple]
**Objective:** Final touches and full integration
**Status:** Not Started

#### Task 6.1: Add Screenshot Support [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual - press F12, screenshot saved
- [ ] Handle F12/F11 key press for screenshot
- [ ] Show toast notification "Screenshot saved!"
- [ ] Follow `planet_list_window.py:679-701` pattern
**Notes:**

#### Task 6.2: Add Window Resize Handling [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual - resize window, layout adjusts
- [ ] Override `on_window_resize()` or handle in `update()`
- [ ] Recalculate panel widths proportionally
- [ ] Rebuild row pool if list width changes
**Notes:**

#### Task 6.3: Handle Fleet State Changes [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual - battle damages ships, window updates
- [ ] Add `refresh()` method to update all panels from current fleet state
- [ ] Validate fleet still exists before refresh
- [ ] Handle case where selected ship was destroyed
- [ ] Consider periodic auto-refresh or event-based refresh
**Notes:**

#### Task 6.4: Final Integration Testing [Simple]
**Tests:** Manual - full feature walkthrough
- [ ] Test with empty fleet
- [ ] Test with fleet containing only destroyed ships
- [ ] Test with 100+ ships (performance)
- [ ] Test serial numbers persist across save/load
- [ ] Test all filters and sorts work correctly
- [ ] Test window coexists with Fleet Orders Window
**Notes:**

---

## Verification Checklist

### After Each Phase
- [ ] Run `pytest tests/unit/` - all tests pass
- [ ] Manual test: open Fleet Report window from strategy screen
- [ ] Manual test: no crashes when selecting ships/fleets
- [ ] Verify no new linting errors introduced

### Final Verification
- [ ] Open Fleet Report with fresh fleet (no damage) - displays correctly
- [ ] Open Fleet Report after battle (damaged ships) - damage shows correctly
- [ ] Serial numbers display as "DesignName-000001" format
- [ ] Filters work: can filter by damage status, class, abilities
- [ ] Sorting works: all columns sort correctly
- [ ] Column reordering works: arrow buttons move columns
- [ ] Ship detail panel shows current HP/resources (not just max)
- [ ] Component damage collapsible sections work
- [ ] Window resize maintains usable layout
- [ ] Save/load preserves serial numbers
- [ ] Run full test suite: `pytest`

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off (Serial Numbers)
- [ ] All Phase 2 tasks checked off (Window Foundation)
- [ ] All Phase 3 tasks checked off (Fleet Summary)
- [ ] All Phase 4 tasks checked off (Ship Detail)
- [ ] All Phase 5 tasks checked off (Filters)
- [ ] All Phase 6 tasks checked off (Polish)
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
