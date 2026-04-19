# Phase 2: C3 — Retrofit Happiness/PopulationEngine to consume IRaceRegistry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-291 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate the silent multi-species fallback in `HappinessEngine._get_race_config` and `PopulationEngine._get_race_config`. Both engines accept an optional `race_registry: Optional[IRaceRegistry] = None` kwarg and resolve `pop.race_id` correctly via the registry. Reverses PROJ-287/decisions.md line 16 deferral.

---

## Tasks

### Task 2.1: Read the PROJ-285 reference pattern [Simple]
**File:** [game/strategy/engine/harvesting_engine.py](game/strategy/engine/harvesting_engine.py), [game/strategy/engine/production_engine.py](game/strategy/engine/production_engine.py)
**Tests:** None (read-only orientation)

- [x] Open `harvesting_engine.py` — locate the `__init__(..., race_registry=None)` kwarg, the `_get_habitability_mult` helper that returns 1.0 when registry is None, and the `set_current_turn` plumbing.
- [x] Open `production_engine.py` — same review.
- [x] Open [game/strategy/engine/turn_engine.py](game/strategy/engine/turn_engine.py) and grep for `HarvestingEngine(` + `ProductionEngine(`. Note exactly how the registry is resolved at construction time (likely `self._race_registry` set somewhere in `TurnEngine.__init__` from the session).
- [x] Document the resolution path in your task notes — Phase 2 Tasks 2.4 + 2.5 mirror it for the new engines.

**Notes:** This is orientation, not implementation. Copy the SHAPE of the optional-kwarg + None-fallback pattern; don't invent a new shape.

### Task 2.2: Write failing multi-species tests for HappinessEngine [Medium]
**File:** `tests/unit/strategy/engine/test_happiness_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py::TestMultiSpeciesViaRegistry -v`

- [x] Add a new test class `TestMultiSpeciesViaRegistry` at the end of the file.
- [x] Build a stub `IRaceRegistry` (use `MagicMock(spec=IRaceRegistry)` or a simple `_StubRegistry` matching the pattern already used in `tests/unit/strategy/services/test_planet_economy_projector.py`).
- [x] Test 1: `test_two_species_use_their_own_base_happiness`. Create an empire with `race_config = humans (base_happiness=0.5)`. Create a colony with TWO populations: humans (count=1000) AND voidari (count=500). Stub registry returns `humans` for `"human"` and `voidari (base_happiness=0.8)` for `"voidari"`. Construct `HappinessEngine(race_registry=stub_registry)`. Run `process_happiness([empire])`. Assert:
  - `humans_pop.happiness ≈ 0.5 * food_ratio * habitability_for_humans`
  - `voidari_pop.happiness ≈ 0.8 * food_ratio * habitability_for_voidari`
  - The two values are DIFFERENT (proves the registry resolved each species separately).
- [x] Test 2: `test_unknown_race_id_skipped_gracefully`. Same setup but registry returns None for `"voidari"`. Assert `humans_pop.happiness` updates correctly AND `voidari_pop.happiness` is unchanged from its pre-call value. No exception raised.
- [x] Test 3: `test_legacy_path_still_works_when_registry_is_none`. Construct `HappinessEngine()` (no kwarg). Same colony. Assert `humans_pop.happiness` updates correctly (matches the empire's primary race) AND `voidari_pop.happiness` stays at default (skipped because the legacy path returns None for non-primary species). This pins the new tightened legacy fallback (Decision 2026-04-18 in decisions.md).
- [x] Run the tests. Confirm Tests 1 + 2 FAIL with the current code (current code returns the wrong race_config for voidari, so it grows using human base_happiness). Test 3 will partially pass for humans but fail for voidari (the unconditional return at line 95 returns the wrong race; voidari gets a happiness update with the WRONG base value).

**Notes:** Use the same Stub pattern PROJ-287 / PROJ-288 used. Don't add the runtime-checkable Protocol assertion — the duck-typed call-through works.

### Task 2.3: Write failing multi-species tests for PopulationEngine [Medium]
**File:** `tests/unit/strategy/engine/test_population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py::TestMultiSpeciesViaRegistry -v`

- [x] Add a new test class `TestMultiSpeciesViaRegistry`.
- [x] Mirror the 3 tests from Task 2.2 but for population growth instead of happiness:
  - Test 1: each species grows at its OWN `base_reproduction_rate * cfg.last_food_ratio * (1 - P/K_eff) * happiness`. Use distinct base_reproduction_rates (humans 0.03, voidari 0.05) so the deltas are visibly different.
  - Test 2: unknown race gracefully skipped (count unchanged).
  - Test 3: legacy path (no registry) skips non-primary species.
- [x] Run the tests. Confirm they FAIL with the current code.

**Notes:** Reuse the equivalence-test patterns from `tests/integration/strategy/test_growth_rate_equivalence.py` for setup style — that file already constructs Planets with a tunable `surface_area` for `max_population` control.

### Task 2.4: Implement HappinessEngine retrofit [Medium]
**File:** `game/strategy/engine/happiness_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py -v`

- [x] Update `HappinessEngine.__init__` to accept `race_registry: Optional['IRaceRegistry'] = None`. Store on `self._race_registry`. Mirror PROJ-285 pattern.
- [x] Add `TYPE_CHECKING` import for `IRaceRegistry` from `game.core.protocols`.
- [x] Rewrite `_get_race_config` to consult the registry first, fall back to legacy single-race resolver, return None on mismatch (instead of returning the wrong race). Per design.md § C3 fix shape:
  ```python
  def _get_race_config(self, race_id: str, empire: 'Empire') -> Optional['RaceConfig']:
      # PROJ-291 C3: registry resolves multi-species correctly when wired
      if self._race_registry is not None:
          race_config = self._race_registry.get_race(race_id)
          if race_config is not None:
              return race_config
      # Legacy single-race fallback (preserves pre-PROJ-291 tests)
      race_config = empire.race_config
      if race_config is None:
          return None
      if race_config.race_id == race_id:
          return race_config
      return None  # PROJ-291 C3: stop returning the wrong race silently
  ```
- [x] Run Task 2.2's test class — Tests 1 + 2 + 3 should all pass now.
- [x] Run the full file — existing tests still pass.

**Notes:** Inline comment markers `# PROJ-291 C3` make the change grep-able.

### Task 2.5: Implement PopulationEngine retrofit [Medium]
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py -v`

- [x] Same pattern as Task 2.4 — accept `race_registry`, rewrite `_get_race_config` to consult registry first + return None on legacy mismatch.
- [x] Run Task 2.3's test class — all green.
- [x] Run the full file — existing tests still pass. NOTE: pre-existing tests that constructed mock empires with single-species colonies will continue to work because the legacy path still returns `empire.race_config` when the species matches.

**Notes:**

### Task 2.6: Wire the registry through TurnEngine [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py -v` + `pytest tests/integration/strategy/test_demographics_loop.py -v`

- [x] Find where `HappinessEngine()` and `PopulationEngine()` are constructed (grep `HappinessEngine(` + `PopulationEngine(` in the file).
- [x] Mirror the resolution path PROJ-285 already uses for `HarvestingEngine(race_registry=...)` / `ProductionEngine(race_registry=...)`. Pass the same `self._race_registry` (or whatever attribute holds it).
- [x] If TurnEngine's `__init__` doesn't yet hold `_race_registry`, follow the PROJ-285 wiring back to its source (likely `session.facade.get_race_registry()` resolved during turn-engine construction or lazy-init).
- [x] Run `tests/integration/strategy/test_demographics_loop.py` — confirms multi-species end-to-end via the post-tick pipeline.
- [x] Run `tests/integration/strategy/test_growth_rate_equivalence.py` — ensures the projected_growth_rate equivalence pin still holds (PROJ-288's matrix).

**Notes:** If you discover the resolution path requires a session/facade restructure, STOP and add a Phase 2 Task 2.7 to do it cleanly. Don't bandaid.

### Task 2.7: Run targeted suite [Simple]
**Tests:** `pytest tests/unit/strategy/engine/ tests/integration/strategy/ -q`

- [x] Engine + integration suite green.
- [x] No regressions in any neighbouring file.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
