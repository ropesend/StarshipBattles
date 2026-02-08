# Phase 1: Empire Resource Pool Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add global resource tracking to Empire class

---

## Tasks

### Task 1.1: Write TDD tests for Empire resources [Simple]
**File:** `tests/unit/strategy/data/test_empire_resources.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_empire_resources.py -v`

- [ ] Create test file with TestEmpireResources class
- [ ] Test: resource_pool initializes as empty dict
- [ ] Test: max_storage initializes as empty dict
- [ ] Test: add_resources() basic - adds to pool
- [ ] Test: add_resources() - respects max_storage, returns overflow
- [ ] Test: add_resources() - no max_storage means unlimited
- [ ] Test: consume_resources() success - deducts and returns True
- [ ] Test: consume_resources() failure - insufficient returns False
- [ ] Test: consume_resources() - partial consumption not allowed
- [ ] Test: has_resources() with single resource type
- [ ] Test: has_resources() with multiple resource types
- [ ] Test: has_resources() returns False if any insufficient
- [ ] Test: get_resource() returns 0 for missing type
- [ ] Test: to_dict() includes resource_pool and max_storage
- [ ] Test: from_dict() restores resource_pool and max_storage
- [ ] Test: from_dict() handles missing fields (old save compatibility)

**Notes:**

---

### Task 1.2: Add resource_pool field to Empire [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_resources.py -v`

- [ ] Add field: `resource_pool: Dict[str, float] = field(default_factory=dict)`
- [ ] Add field: `max_storage: Dict[str, float] = field(default_factory=dict)`
- [ ] Implement `add_resources(resource_type: str, amount: float) -> float`:
  ```python
  def add_resources(self, resource_type: str, amount: float) -> float:
      """Add resources to pool. Returns overflow amount."""
      current = self.resource_pool.get(resource_type, 0.0)
      max_cap = self.max_storage.get(resource_type, float('inf'))
      new_total = current + amount
      if new_total > max_cap:
          self.resource_pool[resource_type] = max_cap
          return new_total - max_cap  # overflow
      self.resource_pool[resource_type] = new_total
      return 0.0
  ```
- [ ] Implement `consume_resources(resource_type: str, amount: float) -> bool`:
  ```python
  def consume_resources(self, resource_type: str, amount: float) -> bool:
      """Consume resources. Returns True if successful."""
      current = self.resource_pool.get(resource_type, 0.0)
      if current >= amount:
          self.resource_pool[resource_type] = current - amount
          return True
      return False
  ```
- [ ] Implement `has_resources(costs: Dict[str, float]) -> bool`:
  ```python
  def has_resources(self, costs: Dict[str, float]) -> bool:
      """Check if empire has all required resources."""
      for resource_type, amount in costs.items():
          if self.resource_pool.get(resource_type, 0.0) < amount:
              return False
      return True
  ```
- [ ] Implement `get_resource(resource_type: str) -> float`:
  ```python
  def get_resource(self, resource_type: str) -> float:
      return self.resource_pool.get(resource_type, 0.0)
  ```

**Notes:**

---

### Task 1.3: Update Empire serialization [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_resources.py tests/integration/strategy/test_empire.py -v`

- [ ] Update `to_dict()` to include new fields:
  ```python
  # Add to existing to_dict():
  'resource_pool': dict(self.resource_pool),
  'max_storage': dict(self.max_storage),
  ```
- [ ] Update `from_dict()` with safe defaults:
  ```python
  # Add to existing from_dict():
  empire.resource_pool = data.get('resource_pool', {})
  empire.max_storage = data.get('max_storage', {})
  ```
- [ ] Verify existing Empire tests still pass

**Notes:**

---

### Task 1.4: Run full test suite [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] All tests pass
- [ ] No serialization regressions
- [ ] Document any issues found

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
