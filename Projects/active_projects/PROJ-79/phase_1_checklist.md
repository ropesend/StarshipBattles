# Phase 1: Rename + Build Yards List Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-79 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rename "Build Queues" to "Build Yards", add build_rate and planet_id to BuildQueueSource, widen selector panel, improve selection indication, show build rate per yard.

---

## Tasks

### Task 1.1: Add `build_rate` and `planet_id` fields to BuildQueueSource [Medium]
**File:** `game/strategy/data/build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Add `from typing import Optional` import (if not present)
- [ ] Add `build_rate: float = 2000.0` field to `BuildQueueSource` dataclass (after line 39)
- [ ] Add `planet_id: Optional[int] = None` field to `BuildQueueSource` dataclass
- [ ] Add helper function `_get_facility_build_rate(facility) -> float`:
  ```python
  def _get_facility_build_rate(facility) -> float:
      """Extract build rate from a shipyard facility's design_data.
      Shipyards build at 3000 units/turn * construction_speed_bonus."""
      for layer_data in facility.design_data.get("layers", {}).values():
          if not isinstance(layer_data, list):
              continue
          for comp in layer_data:
              if isinstance(comp, dict):
                  abilities = comp.get("abilities", {})
                  shipyard_data = abilities.get("SpaceShipyard", {})
                  if isinstance(shipyard_data, dict):
                      bonus = shipyard_data.get("construction_speed_bonus", 1.0)
                      return 3000.0 * bonus
      return 3000.0  # Default shipyard rate
  ```
- [ ] In `collect_build_queues_at_hex()`:
  - Base queue (line 95-103): Add `build_rate=2000.0`, `planet_id=planet.id`
  - Shipyard facility (line 110-118): Add `build_rate=_get_facility_build_rate(facility)`, `planet_id=planet.id`
  - Fleet yard (line 126-134): Add `build_rate=3000.0`, `planet_id=None`
- [ ] In `collect_all_build_queues_for_empire()`:
  - Base queue (line 159-167): Add `build_rate=2000.0`, `planet_id=planet.id`
  - Shipyard facility (line 174-182): Add `build_rate=_get_facility_build_rate(facility)`, `planet_id=planet.id`
  - Fleet yard (line 188-196): Add `build_rate=3000.0`, `planet_id=None`
- [ ] Verify: All callers of BuildQueueSource constructor compile without error

**Notes:**

### Task 1.2: Rename display names [Simple]
**File:** `game/strategy/data/build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] In `collect_build_queues_at_hex()`:
  - Line 97: Change `f"{planet.name} - Base"` to `f"{planet.name} - Planetary Yard"`
  - Line 128: Change `f"{fleet.name} - Space Yard"` to `f"{fleet.name} - Shipyard"`
  - (Shipyard facility name `f"{planet.name} - Shipyard {shipyard_index}"` already correct)
- [ ] In `collect_all_build_queues_for_empire()`:
  - Line 160: Change `f"{planet.name} - Base"` to `f"{planet.name} - Planetary Yard"`
  - Line 191: Change `f"{fleet.name} - Space Yard"` to `f"{fleet.name} - Shipyard"`
- [ ] Verify: No hardcoded "Base" display names remain for build queues

**Notes:**

### Task 1.3: Rename header and widen queue selector panel [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual test - open build queue screen

- [ ] Line 258: Change `"<b>Build Queues</b>"` to `"<b>Build Yards</b>"`
- [ ] Line 246: Change `panel_width = 200` to `panel_width = 280`
- [ ] Line 284: Change `row_width = 180` to `row_width = 260`
- [ ] Line 422: Update `panel_left` calculation - change `200` (queue selector width) to `280`:
  - From: `panel_left = 10 + 480 + 10 + 200 + 10  # = 710`
  - To: `panel_left = 10 + 480 + 10 + 280 + 10  # = 790`
- [ ] Verify: Build queue panel and queue selector don't overlap

**Notes:**

### Task 1.4: Show build rate and improve selection indication [Medium]
**File:** `game/ui/screens/build_queue_screen.py`, `_refresh_queue_selector()` (line 275)
**Tests:** Manual test - open build queue screen, click different queues

- [ ] Change `row_height = 45` (line 283) to `row_height = 55`
- [ ] Change button label format (line 292):
  - From: `label_text = f"{source.display_name} ({item_count})"`
  - To: Include build rate and selection prefix:
    ```python
    prefix = "> " if is_selected else "  "
    label_text = f"{prefix}{source.display_name}\n{item_count} items | {int(source.build_rate)}/turn"
    ```
- [ ] Verify: Selected queue shows `"> "` prefix, build rate is visible

**Notes:**

### Task 1.5: Update tests for renames and new fields [Medium]
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py tests/integration/ui/`

- [ ] Update display name expectations in existing tests (change "Base" to "Planetary Yard", "Space Yard" to "Shipyard")
- [ ] Add test: `test_build_queue_source_has_build_rate` - verify field exists, defaults to 2000.0
- [ ] Add test: `test_collect_queues_sets_shipyard_build_rate` - mock facility with SpaceShipyard ability, verify build_rate = 3000.0
- [ ] Add test: `test_collect_queues_sets_planet_id` - verify planet-based sources have planet_id, fleet-based have None
- [ ] Run: `pytest tests/ --testmon` to verify no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Manual test: Build queue screen opens, shows "Build Yards" header, "Planetary Yard" / "Shipyard" labels, build rates visible
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
