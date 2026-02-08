# Phase 2: PlanetaryFacility Resource Tracking

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add fuel storage tracking to planetary facilities

---

## Tasks

### Task 2.1: Add resource_levels field to PlanetaryFacility [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/ -k facility`

- [ ] Import `field` from dataclasses if not already imported
- [ ] Add new field to PlanetaryFacility dataclass (after line ~31):
  ```python
  resource_levels: Dict[str, float] = field(default_factory=dict)
  ```
- [ ] Verify: Dataclass still instantiates correctly

**Notes:**

---

### Task 2.2: Update serialization for resource_levels [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/integration/save_load/`

- [ ] Find `to_dict()` method in PlanetaryFacility (or add if missing)
- [ ] Add `resource_levels` to the dict output
- [ ] Find `from_dict()` method (or add if missing)
- [ ] Add `resource_levels` restoration from dict
- [ ] Verify: Save/load cycle preserves facility fuel levels

**Notes:**

---

### Task 2.3: Add facility resource helper methods [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/ -k facility`

- [ ] Add `get_fuel_storage(self) -> float`:
  ```python
  def get_fuel_storage(self) -> float:
      """Get current fuel level in this facility."""
      return self.resource_levels.get('fuel', 0.0)
  ```

- [ ] Add `get_max_fuel_storage(self, registries) -> float`:
  ```python
  def get_max_fuel_storage(self, registries) -> float:
      """Calculate max fuel capacity from design_data components."""
      total = 0.0
      for layer_data in self.design_data.get("layers", {}).values():
          if not isinstance(layer_data, list):
              continue
          for comp in layer_data:
              comp_id = comp.get("id") if isinstance(comp, dict) else comp
              comp_def = registries.components.get(comp_id)
              if not comp_def:
                  continue
              abilities = getattr(comp_def, 'abilities', {}) or {}
              for storage in (abilities.get('ResourceStorage') or []):
                  if isinstance(storage, dict) and storage.get('resource') == 'fuel':
                      total += storage.get('amount', 0)
      return total
  ```

- [ ] Add `add_fuel(self, amount, registries) -> float`:
  ```python
  def add_fuel(self, amount: float, registries) -> float:
      """Add fuel up to max capacity. Returns overflow."""
      max_storage = self.get_max_fuel_storage(registries)
      current = self.get_fuel_storage()
      space = max_storage - current
      added = min(amount, space)
      self.resource_levels['fuel'] = current + added
      return amount - added  # overflow
  ```

- [ ] Add `withdraw_fuel(self, amount) -> float`:
  ```python
  def withdraw_fuel(self, amount: float) -> float:
      """Withdraw fuel. Returns actual amount withdrawn."""
      current = self.get_fuel_storage()
      withdrawn = min(amount, current)
      self.resource_levels['fuel'] = current - withdrawn
      return withdrawn
  ```

- [ ] Verify: All methods work correctly with tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
