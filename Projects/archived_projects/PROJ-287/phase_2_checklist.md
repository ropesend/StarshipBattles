# Phase 2: Facade exposure + cache invalidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-287 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `StrategySessionFacade.get_race_registry()` lazy-init method. Wire race-save invalidation so the cache stays correct when a user edits a race.

---

## Tasks

### Task 2.1: Write failing tests for facade accessor [Simple]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

- [x] Test: `facade.get_race_registry()` returns an `IRaceRegistry` instance.
- [x] Test: two calls return the SAME instance (lazy-init, cached).
- [x] Test: two different facades return DIFFERENT instances (per-session scope).

**Notes:** Added `TestRaceRegistryAccessor` class at end of `test_strategy_session_facade.py`.

### Task 2.2: Add `get_race_registry` to facade [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

- [x] Add method with lazy-init pattern (see design.md § Facade exposure).
- [x] Store the instance on `self._race_registry` so subsequent calls return the cached one.

**Notes:** Uses inline import of `CachedRaceRegistry` + `RaceLibrary` inside the accessor to keep the facade's top-level import surface narrow (consistent with other command-dispatch helpers that late-import their command classes). `IRaceRegistry` added to the existing `TYPE_CHECKING` block as the return annotation.

### Task 2.3: Wire race-save invalidation [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [x] Find the race-save handler (likely `_on_overwrite_save` / `_on_save_as_new`).
- [x] After successful `race_library.save_race(race)`, call `self.facade.get_race_registry().invalidate(race.race_id)`.
- [x] Add a test: mock the facade's registry; save a race; assert `invalidate(race_id)` was called.

**Notes:** The single save funnel is `_do_save()` — both `_on_overwrite_save` and `_on_save_as_new` call through it, so invalidation is wired at that single chokepoint. Since `RaceSetupScreen` is launched pre-game today (no live session / facade), I added an optional `race_registry: Optional[IRaceRegistry] = None` kwarg to `__init__`. When `None` (current call sites in `app.py::start_race_setup` and `new_game_setup_screen.py`), `_do_save` simply skips invalidation — no behaviour change pre-game. When a future mid-game invocation passes `facade.get_race_registry()`, the cache is kept coherent automatically. Three new tests in `TestRaceRegistryInvalidationOnSave`: successful save invalidates, failed save does not invalidate, no-registry save still works. Updated `_make_race_setup_screen` helper to seed `screen.race_registry = None` so existing tests using the bypass-init pattern don't regress.

### Task 2.4: Verify end-to-end [Simple]
**Tests:** `pytest tests/unit/strategy/facade/ tests/unit/ui/screens/test_race_setup_screen.py tests/unit/strategy/systems/test_race_library.py`

- [x] All three test suites green.
- [x] Spot-check: facade returns a cached registry, race save invalidates one entry.

**Notes:** Combined run: 286/286 pass in 4.65s.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3: resident_species)
