# Phase 1: Battle Loop Hot Path

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-12 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Optimize the main battle loop to reduce per-frame overhead
**Priority:** CRITICAL - 60 FPS target with 60+ ships

---

## Tasks

### Task 1.1: PERF-02 - Fix Spatial Grid Rebuild Pattern [Medium]
**File:** `game/simulation/systems/battle_engine.py:221-228`
**Tests:** `pytest tests/unit/simulation/test_battle_engine.py`

**Issue:** Complete grid destruction + rebuild every frame:
```python
self.grid.clear()
alive_ships = [s for s in self.ships if s.is_alive]  # List allocation
for s in alive_ships:
    self.grid.insert(s)
```
60 fps = 60 grid clears/rebuilds per second.

**Implementation:**
- [ ] Track which objects moved since last frame
- [ ] Only reinsert moved objects (dirty-flag pattern)
- [ ] Skip list comprehension - iterate directly with alive check
- [ ] Consider incremental update instead of full rebuild
- [ ] Benchmark before and after

**Expected Improvement:** 20-30% reduction in update loop time

---

### Task 1.2: PERF-12 - Fix Grid Clear Memory Allocation [Simple]
**File:** `game/engine/spatial.py:11-12`
**Tests:** `pytest tests/unit/engine/test_spatial.py`

**Issue:** `clear()` creates new dict object every time instead of reusing.
```python
def clear(self):
    self.buckets = {}  # New dict object every frame
```

**Implementation:**
- [ ] Change to `self.buckets.clear()` to reuse dict
- [ ] Verify behavior is identical
- [ ] Benchmark memory allocation

**Expected Improvement:** Negligible frame time, but reduces GC pressure

---

### Task 1.3: PERF-01 - Fix Inefficient Type Check [Simple]
**File:** `game/simulation/projectile_manager.py:115`
**Tests:** `pytest tests/unit/simulation/test_projectile_manager.py`

**Issue:** `isinstance(p.target, type(p))` creates runtime type objects.

**Implementation:**
- [ ] Cache projectile class reference
- [ ] Or use duck-typing: check for attributes instead
- [ ] Benchmark with 100+ projectiles

**Expected Improvement:** 5-10% reduction in collision checks

---

### Task 1.4: PERF-08 - Fix Projectile Removal Pattern [Medium]
**File:** `game/simulation/projectile_manager.py:34-135`
**Tests:** `pytest tests/unit/simulation/test_projectile_manager.py`

**Issue:** Uses index-based removal with list comprehension rebuild.
```python
projectiles_to_remove = set()
# ... populate set
self.projectiles = [p for i, p in enumerate(self.projectiles) if i not in projectiles_to_remove]
```

**Implementation:**
- [ ] Consider using `collections.deque` for O(1) removal
- [ ] Or mark for removal and rebuild once per frame (batch)
- [ ] Or use swap-and-pop pattern
- [ ] Benchmark with high projectile counts (100+)

**Expected Improvement:** 5-10% reduction in projectile update overhead

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Profile shows grid operations < 5% of frame time
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
