# Phase 2: Treasury Panel

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-99 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the Treasury tab panel that renders production, expenses, and storage sections with resource icon column headers.

---

## Tasks

### Task 2.1: Create EmpireTreasuryPanel class [Medium]
**File:** `game/ui/panels/empire_treasury_panel.py` (NEW)
**Tests:** Manual visual test (rendered in Phase 3 window)

- [x] Create new file `game/ui/panels/empire_treasury_panel.py`
- [x] Import `pygame`, `pygame_gui`, `UIPanel`, `UILabel`, `UIImage`, `UIScrollingContainer`
- [x] Import `PLANET_RESOURCES` from `game.core.constants`
- [x] Import `Paths` from `game.core.paths`
- [x] Define layout constants:
  - `LABEL_COL_WIDTH = 200`
  - `RESOURCE_COL_WIDTH = 100` (adjusted for 5 columns)
  - `ICON_SIZE = 20`
  - `ROW_HEIGHT = 28`
  - `SECTION_GAP = 15`
  - `HEADER_HEIGHT = 35`
- [x] Define `EmpireTreasuryPanel` class:
  - `__init__(self, panel, manager, snapshot, resource_icons)`:
    - `panel`: parent UIPanel container
    - `manager`: pygame_gui.UIManager
    - `snapshot`: EmpireEconomySnapshot
    - `resource_icons`: Dict[str, pygame.Surface] (pre-loaded, 20x20)
  - Store references, call `_build_ui()`
- [x] Implement `_build_ui(self)`:
  - Create UIScrollingContainer inside parent panel (full size minus margins)
  - Track `y_offset` starting at 10
  - Call `_build_resource_header(y_offset)` → renders 5 resource icons + abbreviated names as column headers
  - Call `_build_section("Resource Production Per Turn", rows, y_offset)` with production rows
  - Call `_build_section("Resource Expenses Per Turn", rows, y_offset)` with expense rows
  - Call `_build_section("Treasury", rows, y_offset)` with treasury rows
- [x] Implement `_build_resource_header(self, y)`:
  - For each resource in PLANET_RESOURCES, at x = LABEL_COL_WIDTH + i * RESOURCE_COL_WIDTH:
    - Render UIImage with scaled icon (ICON_SIZE x ICON_SIZE)
    - Render abbreviated label below: Met, Org, Vap, Rad, Exo
  - Return new y_offset (y + HEADER_HEIGHT)
- [x] Implement `_build_section(self, title, rows, y)`:
  - Render section title as bold UILabel (full width)
  - For each `(label, values_dict, is_total)` in rows:
    - Render label in left column
    - Render 5 numeric values aligned to resource columns
    - Total rows use different styling (e.g., separator line above)
  - Return new y_offset
- [x] Implement `_format_value(self, value)`:
  - Return formatted integer string (e.g., "4,591") with comma separators
  - Return "0" for zero values
- [x] Implement `refresh(self, snapshot)`:
  - Clear existing widgets in scroll container
  - Rebuild with new snapshot data

**Notes:** Also added `load_resource_icons()` helper function to load and scale icons.

### Task 2.2: Define treasury section data structure [Simple]
**File:** `game/ui/panels/empire_treasury_panel.py`
**Tests:** Part of Task 2.1

- [x] Production rows list:
  ```
  ("From Colonies", snapshot.colony_production, False)
  ("From Ships", snapshot.ship_production, False)
  ("From Trade", snapshot.trade_production, False)
  ("From Tribute", snapshot.tribute_production, False)
  ("From Remote Mining", snapshot.mining_production, False)
  ("Total", snapshot.total_production, True)
  ```
- [x] Expense rows list:
  ```
  ("Tributes", snapshot.tribute_expenses, False)
  ("Maintenance Costs", snapshot.maintenance_expenses, False)
  ("Construction Queues", snapshot.construction_expenses, False)
  ("Total", snapshot.total_expenses, True)
  ```
- [x] Treasury rows list:
  ```
  ("Net Resources", snapshot.net_resources, False)
  ("Total In Storage", snapshot.current_storage, False)
  ("Maximum Storage", snapshot.max_storage, False)
  ```

**Notes:** Implemented as `_get_production_rows()`, `_get_expense_rows()`, `_get_treasury_rows()` methods.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] File `game/ui/panels/empire_treasury_panel.py` exists and has no syntax errors
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3

## Implementation Notes
- Created 259-line panel with full production/expense/treasury display
- 19 unit tests covering formatting, row structure, panel construction, refresh
- Resource column width adjusted to 100px (vs 120) to fit 5 columns nicely
- Added `RESOURCE_ABBREVIATIONS` dict for column header labels
- Panel uses UIScrollingContainer for overflow support
