# Phase 4: Privatize `FacadeSessionState.session`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] FAILING TEST: `hasattr(facade.facade_state, 'session')` is `False` (the public
      attribute is gone) AND the slice helpers still work
      (`facade.fleets.get(id)`, `facade.systems.all()`, `facade.empires.get(id)`
      return correctly). Confirm it FAILS now (`session` is currently public).

**Notes:** Added `TestFacadeStateSessionPrivate` (3 cases) to `test_facade_indices.py`:
`hasattr(facade_state,'session')` is False, `facade_state._session is session`,
slices still function. Confirmed RED before the rename.

---

### Task 4.2: Rename `session` → `_session` + internal accessor [Complex]
**Files:** `game/strategy/facade/slices/_facade_state.py` (`__init__` `:65`, helpers
`:108-177`), and every slice reading `_state.session` — **7 slices**:
`system_slice.py`, `planet_slice.py`, `fleet_slice.py`, `event_slice.py`,
`empire_slice.py`, `economy_slice.py` (`:67`, `:119` — post-flesh review B1),
`command_dispatch_slice.py`. Also `grouped_namespaces.py`
`FacadeSessionInfo._session` (already `_session` there — verify).
**Tests:** the Task 4.1 pin + full facade suite

- [x] In `_facade_state.py`: rename the public `self.session` to `self._session` in
      `__init__` and all internal helpers (`get_fleet_by_id`, `get_empire_by_id`,
      `build_planet_index`, `get_design_catalog_for_empire`, `get_designs_for_empire`).
      Constructor KEYWORD stays `session` (test-internal construction seam).
- [x] Provide the slice read path: chose **(a) slices read `_state._session` directly**
      (simplest, most honest, no extra accessor). Recorded in decisions.md.
      `facade.facade_state.session` no longer resolves.
- [x] Update all `_state.session.<x>` reads across the 7 slice files (incl.
      `economy_slice.py:67,119`) to `_state._session`. Grepped `state\.session`
      repo-wide: zero non-comment stragglers in `game/`.
- [x] Verify Task 4.1 pin now passes; full facade suite green.

**Notes:** 7 slices migrated: command_dispatch, event, empire, economy, system,
planet, fleet (incl. both dot-`.session.` and `getattr(state.session,...)` forms).
**Found a missed external reader during Phase 4:** `workshop_ship_io.py:84` read
`getattr(facade_state, "session", None).services...` (string-getattr, AST-guard-missed)
— migrated to the public `facade_state.get_design_catalog_for_empire(empire_id)`
accessor. Test seams updated: 4 slice-test fake states (`session=`→`_session=`),
`test_builder_io_integration.py` (`.session.services` write → `.get_design_catalog_for_empire`),
`test_build_queue_screen_lifecycle.py` `_MockSession` (added mirrored `_session` property). Watch for any test that constructs `FacadeSessionState(session=...)` by
keyword or asserts `.session` — update those test seams (they are test-internal, not
a production read-path leak).

---

### Task 4.3: Confirm the cache boundary is untouched [Simple]
**Tests:** `tests/unit/strategy/engine/test_game_session_projection_boundary.py`

- [x] Verify the kept-by-design cache-holder pin
      (`TestFacadeCacheHolderIsDocumentedPerformanceBoundary`) is still green — the
      caches and `invalidate_all` are UNCHANGED; only `session` was renamed.
- [x] Verify UI cache reads still work: `planet_list_filters` / `star_list_filters`
      read `facade_state.planets_for_empire_cache` / `stars_cache_new` — NOT `session`;
      they keep resolving (full UI suite GREEN).

**Notes:** Cache-boundary pin green; only the `session`→`_session` attribute renamed,
caches untouched.

---

### Task 4.4: Tighten the session-read guard for the closure [Simple]
**File:** `tests/static_guards/test_facade_read_path_session_guard.py`
**Tests:** the guard's own positive controls

- [x] The matcher already recognizes `facade_state.session` (form 3). Added a runtime
      pin `test_facade_state_session_attribute_is_privatized` asserting
      `hasattr(FacadeSessionState(...), "session")` is False and `_session` still holds
      the live session — this catches the getattr-by-name form the AST scan misses
      (exactly the workshop_ship_io leak found in Phase 4). Kept the existing
      build-queue-manager negative-control pin.
- [x] Verify guard suite green.

**Notes:** Both guards GREEN.

---

## Phase Completion Checklist
- [x] `facade.facade_state.session` no longer resolves; slices use `_state._session`
- [x] `FacadeSessionState` and its helpers/caches intact; cache-boundary pin green
- [x] `python Tools/test_sharded/test_sharded.py` green
- [x] PROJECT END: both guards green; remaining session-read allowlist = the DEFERRED
      broad-pass-through readers (`_session.galaxy/empires/systems`) + the `__extract__`
      getter (deferred 477) + Category B mutator WRITE seams + Category A
      composition-root self-reads (`_session.active_empire`/`_session.human_player_ids`)
- [x] Update status to `Complete`; update plan.md phase table + Current State
