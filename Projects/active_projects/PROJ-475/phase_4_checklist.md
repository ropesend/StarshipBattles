# Phase 4: Privatize `FacadeSessionState.session`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make the live session UNREACHABLE as a public attribute via
`facade.facade_state.session`, by renaming `FacadeSessionState.session` → `_session`
and giving the facade's own slices a slice-internal read path. The cache holder
stays public. Mechanical but touches `_facade_state` + 7 slice files. DO NOT delete `FacadeSessionState`.

---

## Tasks

### Task 4.1: Pin the closure with a failing test [Simple]
**File:** `tests/unit/strategy/facade/test_facade_indices.py` (or nearest facade-state
test module).
**Tests:** `pytest tests/unit/strategy/facade -k facade_state_session_private`

- [ ] FAILING TEST: `hasattr(facade.facade_state, 'session')` is `False` (the public
      attribute is gone) AND the slice helpers still work
      (`facade.fleets.get(id)`, `facade.systems.all()`, `facade.empires.get(id)`
      return correctly). Confirm it FAILS now (`session` is currently public).

**Notes:**

---

### Task 4.2: Rename `session` → `_session` + internal accessor [Complex]
**Files:** `game/strategy/facade/slices/_facade_state.py` (`__init__` `:65`, helpers
`:108-177`), and every slice reading `_state.session` — **7 slices**:
`system_slice.py`, `planet_slice.py`, `fleet_slice.py`, `event_slice.py`,
`empire_slice.py`, `economy_slice.py` (`:67`, `:119` — post-flesh review B1),
`command_dispatch_slice.py`. Also `grouped_namespaces.py`
`FacadeSessionInfo._session` (already `_session` there — verify).
**Tests:** the Task 4.1 pin + full facade suite

- [ ] In `_facade_state.py`: rename the public `self.session` to `self._session` in
      `__init__` and all internal helpers (`get_fleet_by_id` `:114`, `get_empire_by_id`
      `:119`, `build_planet_index` `:125`, `get_design_catalog_for_empire` `:153`,
      `get_designs_for_empire` `:170`).
- [ ] Provide the slice read path: simplest is a property `def session(self)` that
      RAISES (so external reads fail loudly) is NOT viable since slices read it —
      instead expose an internal name the slices use. Decide between (a) slices read
      `_state._session` directly, or (b) add a deliberately-named internal accessor
      e.g. `_state.live_session()` documented as engine-internal. Record choice in
      decisions.md. Whichever: `facade.facade_state.session` must no longer resolve.
- [ ] Update all `_state.session.<x>` reads across the 7 slice files (incl.
      `economy_slice.py:67,119`) to the chosen internal path. Grep
      `_state\.session` repo-wide to confirm zero stragglers before claiming done.
- [ ] Verify Task 4.1 pin now passes; full facade suite green.

**Notes:** Watch for any test that constructs `FacadeSessionState(session=...)` by
keyword or asserts `.session` — update those test seams (they are test-internal, not
a production read-path leak).

---

### Task 4.3: Confirm the cache boundary is untouched [Simple]
**Tests:** `tests/unit/strategy/engine/test_game_session_projection_boundary.py`

- [ ] Verify the kept-by-design cache-holder pin
      (`TestFacadeCacheHolderIsDocumentedPerformanceBoundary`) is still green — the
      caches (`planet_index`, `all_stars_cache`, `planets_for_empire_cache`,
      `stars_cache_new`, ...) and `invalidate_all` are UNCHANGED; only `session` was renamed.
- [ ] Verify UI cache reads still work: `planet_list_filters.py:60-86` /
      `star_list_filters.py:40-63` read `facade_state.planets_for_empire_cache` /
      `stars_cache_new` — these are NOT `session` and must keep resolving.

**Notes:**

---

### Task 4.4: Tighten the session-read guard for the closure [Simple]
**File:** `tests/static_guards/test_facade_read_path_session_guard.py`
**Tests:** the guard's own positive controls

- [ ] The matcher already recognizes `facade_state.session` (form 3). Add/keep a pin
      asserting no UI file reaches `facade.facade_state.session` (the migration of
      `strategy_build_queue_manager` in 472 1C is already pinned by
      `test_facade_state_session_form_no_longer_present_in_build_queue_manager`).
      Optionally broaden to assert it nowhere resolves now that the attribute is gone.
- [ ] Verify guard suite green.

**Notes:**

---

## Phase Completion Checklist
- [ ] `facade.facade_state.session` no longer resolves; slices use the internal path
- [ ] `FacadeSessionState` and its helpers/caches intact; cache-boundary pin green
- [ ] `python Tools/test_sharded/test_sharded.py` green
- [ ] PROJECT END: confirm both guards green with the migrated allowlist entries
      removed; the only remaining allowlist = the DEFERRED broad-pass-through readers
      + mutator WRITE seams + Category A composition-root self-reads
- [ ] Update status to `Complete`; update plan.md phase table + Current State
