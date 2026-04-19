# Phase 2: Facade exposure + cache invalidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-287 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `StrategySessionFacade.get_race_registry()` lazy-init method. Wire race-save invalidation so the cache stays correct when a user edits a race.

---

## Tasks

### Task 2.1: Write failing tests for facade accessor [Simple]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

- [ ] Test: `facade.get_race_registry()` returns an `IRaceRegistry` instance.
- [ ] Test: two calls return the SAME instance (lazy-init, cached).
- [ ] Test: two different facades return DIFFERENT instances (per-session scope).

**Notes:**

### Task 2.2: Add `get_race_registry` to facade [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

- [ ] Add method with lazy-init pattern (see design.md § Facade exposure).
- [ ] Store the instance on `self._race_registry` so subsequent calls return the cached one.

**Notes:**

### Task 2.3: Wire race-save invalidation [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [ ] Find the race-save handler (likely `_on_overwrite_save` / `_on_save_as_new`).
- [ ] After successful `race_library.save_race(race)`, call `self.facade.get_race_registry().invalidate(race.race_id)`.
- [ ] Add a test: mock the facade's registry; save a race; assert `invalidate(race_id)` was called.

**Notes:**

### Task 2.4: Verify end-to-end [Simple]
**Tests:** `pytest tests/unit/strategy/facade/ tests/unit/ui/screens/test_race_setup_screen.py tests/unit/strategy/systems/test_race_library.py`

- [ ] All three test suites green.
- [ ] Spot-check: facade returns a cached registry, race save invalidates one entry.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3: resident_species)
