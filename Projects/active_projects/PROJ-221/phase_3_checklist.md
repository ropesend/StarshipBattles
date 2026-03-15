# Phase 3: Build Queue Data Source & Column Definitions [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create ITableDataSource implementation and column definitions for per-planet build queue

---

## Tasks

### Task 3.1: Define build queue columns [Simple]
**File:** `game/ui/screens/build_queue_queue_data_source.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_queue_data_source.py`

- [x] Create new file `game/ui/screens/build_queue_queue_data_source.py`
- [x] Define `BUILD_QUEUE_COLUMNS` constant — list of column dicts following the standard pattern:
  ```python
  BUILD_QUEUE_COLUMNS = [
      {"id": "order",     "title": "#",     "width": 35,  "visible": True},
      {"id": "portrait",  "title": "",      "width": 50,  "visible": True, "type": "image"},
      {"id": "item",      "title": "Item",  "width": 200, "visible": True},
      {"id": "turns",     "title": "Turns", "width": 60,  "visible": True},
      {"id": "met_rate",  "title": "Met/t", "width": 65,  "visible": True},
      {"id": "org_rate",  "title": "Org/t", "width": 65,  "visible": True},
      {"id": "vap_rate",  "title": "Vap/t", "width": 65,  "visible": True},
      {"id": "rad_rate",  "title": "Rad/t", "width": 65,  "visible": True},
      {"id": "exo_rate",  "title": "Exo/t", "width": 65,  "visible": True},
      {"id": "met_rem",   "title": "Met",   "width": 65,  "visible": True},
      {"id": "org_rem",   "title": "Org",   "width": 65,  "visible": True},
      {"id": "vap_rem",   "title": "Vap",   "width": 65,  "visible": True},
      {"id": "rad_rem",   "title": "Rad",   "width": 65,  "visible": True},
      {"id": "exo_rem",   "title": "Exo",   "width": 65,  "visible": True},
  ]
  ```
- [x] Verify column IDs are unique, all have required fields (id, title, width, visible)
- [x] Column widths should sum to a reasonable total for the available panel width (~600-900px)

**Notes:** Column widths may need tuning during Phase 4 when we see them rendered. The `title` field is used by `TableHeader` as `label` fallback if no `label` key exists.

### Task 3.2: Implement BuildQueueQueueDataSource [Medium]
**File:** `game/ui/screens/build_queue_queue_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_queue_data_source.py`

- [x] Create class `BuildQueueQueueDataSource(ITableDataSource)`
- [x] Constructor takes: `columns: List[Dict]`, `portrait_loader: BuildQueuePortraitLoader`, `build_rate: Dict[str, float]`
- [x] Add `_queue: List[Dict]` field — reference to the active construction queue
- [x] Add `set_queue(queue: List[Dict], build_rate: Dict[str, float])` method to update the active queue and rate
- [x] Implement `get_row_count() -> int` — return `len(self._queue)`
- [x] Implement `get_columns() -> List[Dict]` — return deep copy of column defs
- [x] Implement `get_cell_value(row_index: int, column_id: str) -> str`
- [x] Implement `get_cell_image(row_index: int, column_id: str) -> Optional[Surface]`
- [x] Import `calculate_per_turn_spend` from `build_queue_helpers`

**Notes:** Maps PLANET_RESOURCES order (Metals, Organics, Vapors, Radioactives, Exotics) to column IDs (met_rate/met_rem, org_rate/org_rem, etc.)

### Task 3.3: Write tests for BuildQueueQueueDataSource [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_queue_data_source.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_queue_data_source.py`

- [x] Create test file
- [x] Add fixture: sample queue items with `design_id`, `type`, `turns_remaining`, `total_cost`, `resources_consumed`
- [x] Add fixture: sample build_rate dict
- [x] Add fixture: mock portrait_loader
- [x] Test `get_row_count()` — returns len of queue
- [x] Test `get_row_count()` with empty queue — returns 0
- [x] Test `get_cell_value(0, "order")` — returns "1"
- [x] Test `get_cell_value(2, "order")` — returns "3"
- [x] Test `get_cell_value(0, "item")` — returns "DesignName (ship)"
- [x] Test `get_cell_value(0, "turns")` — returns formatted turns
- [x] Test `get_cell_value(0, "met_rate")` — returns per-turn spend for Metals
- [x] Test `get_cell_value(0, "met_rem")` — returns remaining cost for Metals
- [x] Test `get_cell_image(0, "portrait")` — returns surface from portrait loader
- [x] Test `get_cell_image(0, "item")` — returns None (not an image column)
- [x] Test `get_columns()` — returns deep copy, modifying copy doesn't affect source
- [x] Test `set_queue()` — updates queue and rate, affects subsequent calls
- [x] Run all tests pass (20 passed)

**Notes:**

### Task 3.4: Run regression tests [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Run `pytest tests/ --testmon` — pending full run
- [x] Verify existing build queue tests still pass: `pytest tests/unit/ui/screens/test_build_queue_screen.py` — 39 passed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
