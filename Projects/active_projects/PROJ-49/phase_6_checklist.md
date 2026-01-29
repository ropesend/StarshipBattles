# Phase 6: O(n^2) Targeting Optimization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce targeting evaluation complexity by caching expensive checks

---

## Tasks

### Task 6.1: Cache Component Availability Per Ship [Medium]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/test_target_evaluator.py`

- [ ] Add optional `ship_capabilities_cache` parameter to `evaluate()`:
  ```python
  @staticmethod
  def evaluate(
      ship,
      candidate,
      rules,
      distance_cache: Dict = None,
      ship_capabilities_cache: Dict = None
  ) -> float:
  ```
- [ ] Define capabilities cache structure:
  ```python
  # Cache structure:
  # {
  #     ship_id: {
  #         'has_weapons': bool,
  #         'weapon_components': List[Component],
  #         'has_pdc': bool,
  #         'pdc_components': List[Component],
  #     }
  # }
  ```
- [ ] Update `has_weapons` rule evaluation to use cache:
  ```python
  if r_type == 'has_weapons':
      if ship_capabilities_cache and candidate.id in ship_capabilities_cache:
          has_wpns = ship_capabilities_cache[candidate.id]['has_weapons']
      else:
          has_wpns = any(candidate.get_components_by_ability('WeaponAbility', operational_only=True))
  ```
- [ ] Update `pdc_arc` rule evaluation to use cached weapon list
- [ ] Run targeting tests

**Notes:** [Filled during implementation]

---

### Task 6.2: Batch Target Scoring with Pre-computed Data [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai.py tests/unit/ai/test_ai_controller_interface.py`

- [ ] Create helper to build capabilities cache for all ships:
  ```python
  def _build_capabilities_cache(self, ships: List['Ship']) -> Dict:
      """Pre-compute expensive capability checks for all ships."""
      cache = {}
      for ship in ships:
          weapons = ship.get_components_by_ability('WeaponAbility', operational_only=True)
          pdc_weapons = [w for w in weapons if w.has_ability('PDCAbility')]
          cache[ship.id] = {
              'has_weapons': len(weapons) > 0,
              'weapon_components': weapons,
              'has_pdc': len(pdc_weapons) > 0,
              'pdc_components': pdc_weapons,
          }
      return cache
  ```
- [ ] Update `_score_and_sort_enemies()` to use batch computation:
  ```python
  def _score_and_sort_enemies(self, enemies, rules):
      # Pre-compute all shared data
      ship_pos = self.ship.position
      distances = {e: ship_pos.distance_to(e.position) for e in enemies}
      capabilities = self._build_capabilities_cache(enemies)

      scored_enemies = []
      for e in enemies:
          score = TargetEvaluator.evaluate(
              self.ship, e, rules,
              distance_cache=distances,
              ship_capabilities_cache=capabilities
          )
          if score > -float('inf'):
              scored_enemies.append((score, e))

      scored_enemies.sort(key=lambda x: x[0], reverse=True)
      return [e for _, e in scored_enemies]
  ```
- [ ] Run AI controller tests
- [ ] Run integration combat tests to verify targeting behavior unchanged

**Notes:** This builds on Task 2.3 (distance cache). Ensure both caches are used together.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/`
- [ ] Run performance profiler: `python tests/unit/performance/profile_simulation.py`
- [ ] Compare profile results to baseline (document improvement)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
