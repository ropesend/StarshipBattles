# Phase 1: Extract Complex Handlers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-201 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract the two highest-complexity branches (status, resources) into dedicated handler methods.

**Expected CC reduction:** ~8-10 points (removing nested conditionals and loop)

---

## Tasks

### Task 1.1: Extract `_format_status` handler [Medium]
**File:** `game/ui/screens/fleet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k status`

- [ ] Add method `_format_status(self, ship: "ShipInstance") -> str` after line 233:
  ```python
  def _format_status(self, ship: "ShipInstance") -> str:
      """Format ship status for display."""
      if not ship.is_alive:
          return "DESTROYED"
      elif ship.is_derelict:
          return "DERELICT"
      elif ship.is_damaged():
          return "DAMAGED"
      else:
          return "OK"
  ```

- [ ] Update `_get_column_value` status branch (lines 156-164) to call handler:
  ```python
  elif col_id == "status":
      return self._format_status(ship)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k status`
- [ ] Verify: All 4 status tests pass

**Notes:** Status priority must be preserved: DESTROYED > DERELICT > DAMAGED > OK

---

### Task 1.2: Extract `_format_resources` handler [Medium]
**File:** `game/ui/screens/fleet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k resources`

- [ ] Add method `_format_resources(self, ship: "ShipInstance") -> str` after `_format_status`:
  ```python
  def _format_resources(self, ship: "ShipInstance") -> str:
      """Format resource percentages for display."""
      parts = []
      resource_abbrevs = [
          (ResourceType.ENERGY, "E"),
          (ResourceType.FUEL, "F"),
          (ResourceType.AMMO, "A"),
      ]
      for res_type, abbrev in resource_abbrevs:
          pct = ship.get_resource_percentage(res_type)
          if pct is not None and pct >= 0:
              parts.append(f"{abbrev}:{int(pct * 100)}")
      return " ".join(parts) if parts else "--"
  ```

- [ ] Update `_get_column_value` resources branch (lines 202-214) to call handler:
  ```python
  elif col_id == "resources":
      return self._format_resources(ship)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_data_source.py -v -k resources`
- [ ] Verify: All 2 resources tests pass

**Notes:** Format must be "E:XX F:XX A:XX" with "--" fallback

---

### Task 1.3: Phase Verification [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v`

- [ ] Run full test file: `pytest tests/unit/ui/screens/test_fleet_data_source.py -v`
- [ ] Verify: All 37+ tests pass
- [ ] Check CC: `radon cc game/ui/screens/fleet_data_source.py -s -a` (should show reduction)

**Notes:** Document CC change in decisions.md

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
