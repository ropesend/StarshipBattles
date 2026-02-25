# Phase 4: Resource Accessor Method

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-194 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add a typed `get_resource_stat()` method to Ship, then replace dynamic `getattr(ship, f'{res}{suffix}')` patterns in stats_config.py with calls to this method. This is the structural change needed for C#/C++/Rust portability.

---

## Tasks

### Task 4.1: Add get_resource_stat() method to Ship [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

Add a typed accessor method that replaces the dynamic `f'{res}{attr_suffix}'` pattern:
- [ ] Add method to Ship class:
  ```python
  def get_resource_stat(self, resource_name: str, stat_type: str) -> float:
      """Get a resource-related stat by name and type.

      Args:
          resource_name: Resource name (e.g., 'fuel', 'ammo', 'energy')
          stat_type: Stat suffix (e.g., 'consumption', 'endurance', 'recharge',
                     'potential_consumption', 'net', 'max_usage')

      Returns:
          The stat value, or 0.0 if not applicable.
      """
      attr_name = f'{resource_name}_{stat_type}'
      return getattr(self, attr_name, 0.0)
  ```
- [ ] Write unit test for get_resource_stat() covering fuel_consumption, ammo_endurance, energy_recharge, etc.
- [ ] Verify: Run tests

**Notes:** This is a transitional method — it still uses getattr internally but provides a typed public API. In a future C#/Rust port, the internals would become a dict lookup or match statement. The key benefit is that callers no longer do dynamic attribute construction.

---

### Task 4.2: stats_config.py — Replace dynamic resource getattr patterns [Medium]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/ --testmon`

Replace `hasattr(ship, f'{res}{attr_suffix}')` / `getattr(ship, f'{res}{attr_suffix}', 0)` patterns:
- [ ] Lines 176-177: `if hasattr(ship, attr_name): val = getattr(ship, attr_name, 0)` → `val = ship.get_resource_stat(res, stat_type)` (need to refactor surrounding code to pass resource name + stat type separately)
- [ ] Lines 221-222: `if attr and hasattr(ship, attr): return getattr(ship, attr, 0)` → use `ship.get_resource_stat()`
- [ ] Line 232: `return getattr(ship, attr, 0)` → use `ship.get_resource_stat()`
- [ ] Lines 406-407: `if hasattr(ship, f'{res}{attr_suffix}'): val = getattr(...)` → `val = ship.get_resource_stat(res, attr_suffix.lstrip('_'))`
- [ ] Verify: Run tests

**Notes:** The `_discover_resources()` function (line 398) builds attr names like `f'{res}{attr_suffix}'` where attr_suffix includes leading underscore (e.g., `_consumption`). The accessor method uses `f'{resource_name}_{stat_type}'` so callers need to strip the leading underscore or adjust the suffix format. Check the exact format at each call site.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
