# Phase 1: `planet_habitability_multiplier` helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-285 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add the population-weighted habitability helper with per-turn caching. No wiring yet — helper is a pure function + cache lives on `Planet`.

---

## Tasks

### Task 1.1: Add `planet_habitability_multiplier` helper [Medium]
**File:** `game/strategy/formulas/colony_output.py` (NEW)
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`

- [ ] Define:
  ```python
  def planet_habitability_multiplier(
      planet: "Planet",
      race_registry,  # RaceLibrary or equivalent
  ) -> float:
      """Population-weighted mean habitability across species on the planet.

      Uncolonized planets (no populations) return 1.0.
      """
      populations = getattr(planet, "populations", [])
      total_pop = sum(pop.count for pop in populations if pop.count > 0)
      if total_pop <= 0:
          return 1.0

      weighted_sum = 0.0
      for pop in populations:
          if pop.count <= 0:
              continue
          race_config = race_registry.get_race(pop.race_id)
          if race_config is None:
              continue
          habitability = score_planet_for_race(planet, race_config)
          weighted_sum += pop.count * habitability

      return weighted_sum / total_pop if total_pop else 1.0
  ```
- [ ] Import `score_planet_for_race` from `habitability.py`.
- [ ] Helper is a pure function — no side effects. Caching lives at the call site, not here.

### Task 1.2: Per-turn cache on `Planet` [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet.py`

- [ ] Add non-serialized field `_cached_habitability_multiplier: Optional[float] = field(default=None, init=False, repr=False)` and `_cached_multiplier_turn: int = field(default=-1, init=False, repr=False)`.
- [ ] Add helper `get_cached_habitability_multiplier(self, race_registry, turn: int) -> float`:
  ```python
  if self._cached_multiplier_turn != turn:
      self._cached_habitability_multiplier = planet_habitability_multiplier(self, race_registry)
      self._cached_multiplier_turn = turn
  return self._cached_habitability_multiplier
  ```
- [ ] Cache MUST NOT serialize — exclude from `to_dict` / `from_dict`.

### Task 1.3: Helper unit tests [Medium]
**File:** `tests/unit/strategy/formulas/test_colony_output.py` (NEW)
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`

- [ ] Test uncolonized planet -> 1.0.
- [ ] Test single-species planet at ideal habitability -> ≈ 0.95 (uses real formula).
- [ ] Test single-species on hostile planet -> low (<0.3).
- [ ] Test weighted average: 70% pop at hab=1.0, 30% pop at hab=0.2 -> multiplier = `0.7*1.0 + 0.3*0.2 = 0.76`.
- [ ] Test zero-count pops excluded from weight.
- [ ] Test missing race_config (`race_registry.get_race(id)` returns None) -> species skipped, multiplier based on remaining.

### Task 1.4: Cache unit tests [Simple]
**File:** `tests/unit/strategy/data/test_planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet.py`

- [ ] Test `get_cached_habitability_multiplier(reg, turn=5)` stores value; subsequent call at same turn returns cached value without recomputation (spy on `planet_habitability_multiplier` to count calls).
- [ ] Test call with `turn=6` recomputes.
- [ ] Test `to_dict` / `from_dict` does NOT round-trip the cache.

### Task 1.5: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Helper exists; nothing calls it yet; full suite green.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
