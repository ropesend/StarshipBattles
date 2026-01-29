# Phase 5: Spatial Grid Optimization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce spatial grid rebuild overhead (research first, implement if beneficial)

---

## Tasks

### Task 5.1: Research Incremental Grid Updates [Medium]
**File:** `game/simulation/systems/battle_engine.py:349-356`, `game/engine/spatial.py`
**Tests:** Research only - no code changes

- [ ] Read current grid implementation in `game/engine/spatial.py`:
  - Understand bucket structure
  - Understand clear() and insert() methods
  - Check if objects track their current cell
- [ ] Analyze battle_engine.py grid usage (lines 349-356):
  - Count how often grid is cleared per tick
  - Estimate percentage of objects that actually move cells
- [ ] Determine if incremental updates are feasible:
  - Can we track which objects moved significantly?
  - Can we only re-bucket objects that changed cells?
  - What's the overhead of tracking vs full rebuild?
- [ ] Profile current grid performance:
  ```python
  # Run: python tests/unit/performance/profile_simulation.py
  # Look for spatial.py methods in output
  ```
- [ ] Document findings in design.md under "## Phase 5 Research Findings"
- [ ] Make go/no-go decision for Task 5.2

**Notes:** If research shows incremental updates aren't worth the complexity, skip Task 5.2 and mark phase complete.

---

### Task 5.2: Implement Incremental Grid Updates [Complex]
**File:** `game/engine/spatial.py`, `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/engine/ tests/unit/combat/test_battle_engine_core.py`

> **PREREQUISITE:** Only implement if Task 5.1 research shows clear benefit

- [ ] Add position tracking to SpatialGrid:
  ```python
  def __init__(self, cell_size=...):
      self.buckets = {}
      self.object_cells = {}  # Track current cell for each object
  ```
- [ ] Add method to get cell for position:
  ```python
  def _get_cell(self, pos) -> Tuple[int, int]:
      return (int(pos.x // self.cell_size), int(pos.y // self.cell_size))
  ```
- [ ] Add incremental update method:
  ```python
  def update_object(self, obj, new_pos) -> None:
      """Update object position, only re-bucket if cell changed."""
      new_cell = self._get_cell(new_pos)
      old_cell = self.object_cells.get(id(obj))

      if old_cell == new_cell:
          return  # No change needed

      # Remove from old cell
      if old_cell and old_cell in self.buckets:
          self.buckets[old_cell].discard(obj)

      # Add to new cell
      if new_cell not in self.buckets:
          self.buckets[new_cell] = set()
      self.buckets[new_cell].add(obj)
      self.object_cells[id(obj)] = new_cell
  ```
- [ ] Update battle_engine.py to use incremental updates:
  ```python
  # Instead of clear() + insert all:
  for s in alive_ships:
      self.grid.update_object(s, s.position)
  for p in self.projectiles:
      if p.is_alive:
          self.grid.update_object(p, p.position)
  ```
- [ ] Add fallback to full rebuild if too many objects moved (configurable threshold)
- [ ] Run battle engine and combat tests
- [ ] Re-run performance profile to measure improvement

**Notes:** This is a complex change. Test thoroughly for edge cases: objects crossing multiple cells, objects being removed, new objects being added.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked (or Task 5.2 skipped with justification)
- [ ] Research findings documented in design.md
- [ ] Run full test suite: `pytest tests/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
