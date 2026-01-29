# Phase 2: Simple Performance Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Quick performance wins with minimal risk

---

## Tasks

### Task 2.1: Fix Projectile List Reconstruction [Simple]
**File:** `game/simulation/projectile_manager.py:137-138`
**Tests:** `pytest tests/unit/combat/test_projectile_manager.py`

- [ ] Replace list comprehension rebuild with in-place mark-and-sweep:
  ```python
  # Current (line 138):
  self.projectiles = [p for i, p in enumerate(self.projectiles) if i not in projectiles_to_remove]

  # Change to:
  if projectiles_to_remove:
      write_idx = 0
      for read_idx, p in enumerate(self.projectiles):
          if read_idx not in projectiles_to_remove:
              self.projectiles[write_idx] = p
              write_idx += 1
      del self.projectiles[write_idx:]
  ```
- [ ] Run projectile manager tests
- [ ] Run integration combat tests: `pytest tests/integration/test_fleet_combat.py`

**Notes:** [Filled during implementation]

---

### Task 2.2: Build Ability Index at Instantiation [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py tests/unit/refactor/`

- [ ] Add `_ability_index: Dict[str, List[Ability]] = {}` to Component.__init__ (around line 100)
- [ ] Build index in `_instantiate_abilities()` after creating ability_instances:
  ```python
  # After ability_instances is populated:
  self._ability_index = {}
  for ab in self.ability_instances:
      ab_name = ab.__class__.__name__
      if ab_name not in self._ability_index:
          self._ability_index[ab_name] = []
      self._ability_index[ab_name].append(ab)
  ```
- [ ] Update `get_abilities()` (lines 182-209) to use index with polymorphic fallback:
  ```python
  def get_abilities(self, ability_name: str):
      # Fast path: direct index lookup
      if ability_name in self._ability_index:
          return list(self._ability_index[ability_name])  # Return copy

      # Fallback: polymorphic check for subclasses
      from game.simulation.components.abilities import ABILITY_REGISTRY
      target_class = ABILITY_REGISTRY.get(ability_name)
      if target_class and isinstance(target_class, type):
          return [ab for ab in self.ability_instances if isinstance(ab, target_class)]

      return []
  ```
- [ ] Run component tests (169+ files affected - run full suite)
- [ ] Verify no behavior changes in ability lookups

**Notes:** Critical change - must maintain backward compatibility

---

### Task 2.3: Pre-calculate Distances for Targeting [Simple]
**File:** `game/ai/target_evaluator.py`, `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_target_evaluator.py tests/unit/ai/test_ai.py`

- [ ] Add `distance_cache` optional parameter to `TargetEvaluator.evaluate()`:
  ```python
  @staticmethod
  def evaluate(ship, candidate, rules, distance_cache: Dict = None) -> float:
  ```
- [ ] In `controller.py:_score_and_sort_enemies()` (around line 124), pre-calculate distances:
  ```python
  def _score_and_sort_enemies(self, enemies, rules):
      ship_pos = self.ship.position
      distances = {e: ship_pos.distance_to(e.position) for e in enemies}

      scored_enemies = []
      for e in enemies:
          score = TargetEvaluator.evaluate(self.ship, e, rules, distance_cache=distances)
          # ... rest unchanged
  ```
- [ ] Update distance-based rules in target_evaluator.py to use cache if available:
  ```python
  # In evaluate():
  if r_type in ('nearest', 'farthest', 'distance'):
      if distance_cache and candidate in distance_cache:
          dist = distance_cache[candidate]
      else:
          dist = _get_position(ship).distance_to(candidate.position)
  ```
- [ ] Run AI targeting tests

**Notes:** [Filled during implementation]

---

### Task 2.4: Use Shallow Copies Where Safe [Simple]
**File:** `game/simulation/components/component.py:91, 134`
**Tests:** `pytest tests/unit/entities/test_component*.py`

- [ ] Analyze line 91 `self.data = copy.deepcopy(data)`:
  - Check what fields in `data` are actually mutated after copy
  - If only top-level values mutate, use `data.copy()` for dict
  - Keep deepcopy for nested mutable structures (abilities, modifiers)
- [ ] Analyze line 134 `self.base_abilities = copy.deepcopy(self.abilities)`:
  - Determine if abilities dict values are mutated
  - If values are immutable, use `.copy()` instead
- [ ] Run component tests to verify no mutation side effects
- [ ] Document which copies were changed and why

**Notes:** Analyze before changing - some deepcopies may be necessary. Err on the side of caution.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
