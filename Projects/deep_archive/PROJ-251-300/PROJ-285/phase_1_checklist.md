# Phase 1: `planet_habitability_multiplier` helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-285 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add the population-weighted habitability helper with per-turn caching. No wiring yet — helper is a pure function + cache lives on `Planet`.

---

## Tasks

### Task 1.1: Add `planet_habitability_multiplier` helper [Medium]
**File:** `game/strategy/formulas/colony_output.py` (NEW)
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`

- [x] Define:
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
- [x] Import `score_planet_for_race` from `habitability.py`.
- [x] Helper is a pure function — no side effects. Caching lives at the call site, not here.

**Notes:** Deviated slightly from the plan's sketch: species with a missing / unknown `race_id` (registry returns None) or a registry that raises are EXCLUDED from BOTH numerator and denominator, not scored as 0. A colony of 700 known-race + 300 unknown-race reads as 100% known-race rather than dragging the multiplier down 30% via a 0-score imputation. This keeps save-load mismatches (known save data, missing race file) from silently destroying an empire's economy. Documented in the helper's module docstring. Defensive `getattr(planet, "populations", None) or []` handles malformed planet objects. `try/except Exception` around `race_registry.get_race` so a corrupt registry doesn't blow up the pipeline — the species is skipped and a debug log is emitted.

### Task 1.2: Per-turn cache on `Planet` [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_habitability_cache.py`

- [x] Add non-serialized field `_cached_habitability_multiplier: Optional[float] = field(default=None, init=False, repr=False)` and `_cached_multiplier_turn: int = field(default=-1, init=False, repr=False)`.
- [x] Add helper `get_cached_habitability_multiplier(self, race_registry, turn: int) -> float`:
  ```python
  if self._cached_multiplier_turn != turn:
      self._cached_habitability_multiplier = planet_habitability_multiplier(self, race_registry)
      self._cached_multiplier_turn = turn
  return self._cached_habitability_multiplier
  ```
- [x] Cache MUST NOT serialize — exclude from `to_dict` / `from_dict`.

**Notes:** Both cache fields also carry `compare=False` so a warmed-up cache on one `Planet` and an unwarmed cache on an equivalent one still compare equal (Planet equality is identity-by-name+location+orbit, per `__eq__`). `get_cached_habitability_multiplier` late-imports `planet_habitability_multiplier` from `colony_output` — avoids any circular-import risk now that `colony_output.py` imports nothing from `planet.py` but could in the future. Also matters for tests: `monkeypatch.setattr(colony_output_mod, "planet_habitability_multiplier", fake)` is the one patch point that works because of the late import. `to_dict` already emits only explicit keys; the cache fields (being `init=False`) were never round-tripped — verified by the round-trip tests.

### Task 1.3: Helper unit tests [Medium]
**File:** `tests/unit/strategy/formulas/test_colony_output.py` (NEW)
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`

- [x] Test uncolonized planet -> 1.0.
- [x] Test single-species planet at ideal habitability -> ≈ 0.95 (uses real formula).
- [x] Test single-species on hostile planet -> low (<0.3).
- [x] Test weighted average: 70% pop at hab=1.0, 30% pop at hab=0.2 -> multiplier = `0.7*1.0 + 0.3*0.2 = 0.76`.
- [x] Test zero-count pops excluded from weight.
- [x] Test missing race_config (`race_registry.get_race(id)` returns None) -> species skipped, multiplier based on remaining.

**Notes:** 11 tests total (exceeds the 6-checkbox spec). Added `TestResilience` class covering the `planet` without `populations` attribute and a registry whose `get_race` raises — both must NOT propagate. The 70/30 weighted math test uses a `monkeypatch` on `score_planet_for_race` for arithmetic precision; a parallel test uses two real-but-identical races to verify the helper integrates with the real formula without hardcoding registry-weight-dependent expected values.

### Task 1.4: Cache unit tests [Simple]
**File:** `tests/unit/strategy/data/test_planet_habitability_cache.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_planet_habitability_cache.py`

- [x] Test `get_cached_habitability_multiplier(reg, turn=5)` stores value; subsequent call at same turn returns cached value without recomputation (spy on `planet_habitability_multiplier` to count calls).
- [x] Test call with `turn=6` recomputes.
- [x] Test `to_dict` / `from_dict` does NOT round-trip the cache.

**Notes:** 7 tests. Test file named `test_planet_habitability_cache.py` not `test_planet.py` per the project's concern-based test splitting convention (there's already `test_planet_stockpile.py`, `test_planet_species_configs.py`, etc.). All monkey-patches target `game.strategy.formulas.colony_output.planet_habitability_multiplier` because the `Planet.get_cached_habitability_multiplier` method late-imports from there — patching at the planet module name does NOT work (attribute doesn't exist there, and `raising=False` silently makes it a no-op). Added a bonus test pinning the equality-ignores-cache property (cache fields `compare=False`).

### Task 1.5: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Helper exists; nothing calls it yet; full suite green.

**Notes:** 14944 total / 14942 passed / 2 failed. Both failures are pre-existing sharded-runner flakes: `test_copy_designs_without_themes_preserves_original` (theme_id pollution — persistent since PROJ-283) + `test_colony_owner_id_matches_empire` (passes in isolation; confirmed manually — same test-pollution class as the PROJ-284 flakes listed in the handoff). Net Phase 1 new tests: 18 (11 colony_output + 7 planet cache).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
