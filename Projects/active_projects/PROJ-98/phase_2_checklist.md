# Phase 2: Resource Consumption Columns [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-98 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add 10 new columns showing per-resource construction cost data from queue items (5 current consumption rate + 5 total cost) for the 5 planet resources.

**Background:** Queue items (PROJ-75 Phase 4) contain `cost_per_tick: Dict[str, float]` and `total_cost: Dict[str, float]`. Per-turn consumption = `cost_per_tick[resource] * 100` (100 ticks per turn). The 5 resources: Metals, Organics, Vapors, Radioactives, Exotics.

---

## Tasks

### Task 2.1: Add resource formatter functions [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`

- [ ] Add `get_resource_rate_text(source: BuildQueueSource, resource_name: str) -> str`:
  - Empty queue -> "-"
  - First item has no `cost_per_tick` key (legacy) -> "-"
  - `resource_name` not in `cost_per_tick` -> "0"
  - Otherwise: format `cost_per_tick[resource_name] * 100` as comma-separated number (e.g. "1,500")
- [ ] Add `get_resource_total_text(source: BuildQueueSource, resource_name: str) -> str`:
  - Empty queue -> "-"
  - First item has no `total_cost` key (legacy) -> "-"
  - `resource_name` not in `total_cost` -> "0"
  - Otherwise: format with k/M suffixes (>=1M: "1.5M", >=1k: "150k", else plain number)
  - Follow formatting pattern from `planet_list_filters.py:297-308` (`get_resource_str`)

**Notes:**

### Task 2.2: Write formatter tests [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_formatter.py`

- [ ] Add `TestGetResourceRateText` class:
  - `test_empty_queue_returns_dash` - no queue items -> "-"
  - `test_with_cost_per_tick_returns_per_turn_value` - cost_per_tick={"Metals": 15.0} -> "1,500" (15*100)
  - `test_legacy_item_without_cost_per_tick_returns_dash` - item without cost_per_tick key -> "-"
  - `test_resource_not_in_cost_returns_zero` - cost_per_tick={"Metals": 10} queried for "Organics" -> "0"
  - `test_zero_rate_returns_zero` - cost_per_tick={"Metals": 0} -> "0"
- [ ] Add `TestGetResourceTotalText` class:
  - `test_empty_queue_returns_dash` - no queue items -> "-"
  - `test_with_total_cost_returns_formatted` - total_cost={"Metals": 5000} -> "5k"
  - `test_large_value_uses_M_suffix` - total_cost={"Metals": 1500000} -> "1.5M"
  - `test_legacy_item_without_total_cost_returns_dash` - item without total_cost key -> "-"
  - `test_resource_not_in_total_returns_zero` - total_cost={"Metals": 100} queried for "Organics" -> "0"

**Notes:**

### Task 2.3: Add 10 column definitions [Simple]
**File:** `game/ui/screens/empire_build_queue_filter_manager.py` (after line 27)

- [ ] Append 5 rate columns to `DEFAULT_COLUMNS`:
  ```python
  {'id': 'res_metals_rate', 'width': 70, 'title': 'Met/t', 'visible': True},
  {'id': 'res_organics_rate', 'width': 70, 'title': 'Org/t', 'visible': True},
  {'id': 'res_vapors_rate', 'width': 70, 'title': 'Vap/t', 'visible': True},
  {'id': 'res_radioactives_rate', 'width': 70, 'title': 'Rad/t', 'visible': True},
  {'id': 'res_exotics_rate', 'width': 70, 'title': 'Exo/t', 'visible': True},
  ```
- [ ] Append 5 total cost columns:
  ```python
  {'id': 'res_metals_total', 'width': 70, 'title': 'Met Tot', 'visible': True},
  {'id': 'res_organics_total', 'width': 70, 'title': 'Org Tot', 'visible': True},
  {'id': 'res_vapors_total', 'width': 70, 'title': 'Vap Tot', 'visible': True},
  {'id': 'res_radioactives_total', 'width': 70, 'title': 'Rad Tot', 'visible': True},
  {'id': 'res_exotics_total', 'width': 70, 'title': 'Exo Tot', 'visible': True},
  ```

**Notes:**

### Task 2.4: Wire column values in _get_column_value() [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`

- [ ] Add module-level constants (after imports):
  ```python
  RESOURCE_RATE_COLS = {
      'res_metals_rate': 'Metals',
      'res_organics_rate': 'Organics',
      'res_vapors_rate': 'Vapors',
      'res_radioactives_rate': 'Radioactives',
      'res_exotics_rate': 'Exotics',
  }
  RESOURCE_TOTAL_COLS = {
      'res_metals_total': 'Metals',
      'res_organics_total': 'Organics',
      'res_vapors_total': 'Vapors',
      'res_radioactives_total': 'Radioactives',
      'res_exotics_total': 'Exotics',
  }
  ```
- [ ] Import `get_resource_rate_text`, `get_resource_total_text` from formatter module (line 27-34)
- [ ] Extend `_get_column_value()` (line 524) with:
  ```python
  if col_id in RESOURCE_RATE_COLS:
      return get_resource_rate_text(source, RESOURCE_RATE_COLS[col_id])
  if col_id in RESOURCE_TOTAL_COLS:
      return get_resource_total_text(source, RESOURCE_TOTAL_COLS[col_id])
  ```

**Notes:**

### Task 2.5: Update test assertions for new column count [Simple]
**Files:** `tests/unit/ui/screens/test_empire_build_queue_window.py`, `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py`

- [ ] `test_empire_build_queue_window.py` line 411: change `assert len(visible) == 8` to `assert len(visible) == 18`
- [ ] `TestColumnConfiguration.test_expected_column_ids`: add all 10 new IDs to `expected` set
- [ ] `test_empire_build_queue_filter_manager.py` `test_columns_list_populated_with_expected_ids`: add 10 new IDs to expected list
- [ ] `test_empire_build_queue_filter_manager.py` `test_all_columns_visible_by_default`: update count to `len(DEFAULT_COLUMNS)` (18)
- [ ] Add tests in `TestGetColumnValue` for at least 2 resource rate and 2 resource total column IDs

**Notes:**

### Task 2.6: Verify [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_empire_build_queue_filter_manager.py tests/unit/ui/screens/test_empire_build_queue_formatter.py -n 4`

- [ ] All tests pass
- [ ] Verify: no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
