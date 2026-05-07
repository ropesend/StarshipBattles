# Phase 2: Pathfinding shim migration sweep (closes PROJ-372 review MIN-002, partial)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-377 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Objective:** Migrate the pathfinding-shim importers that have no `unittest.mock.patch('game.strategy.data.pathfinding.X')` reaching them, calling `galaxy._pathfinder.X(…)` directly. Defer the test-patched sites with documented rationale. Closes PROJ-372 review MIN-002 partially; the residual scope (test-patched sites + test rewrites) is captured as a successor concern.

**Files (planned):** see manifest.md "Phase 2" row group.
**Test target per Class A site:** `pytest tests/<area> -v` for the area touched, plus the shard suite at the end.
**Sharded suite:** must remain green; pass count unchanged from Phase 1 close (Phase 2 is migration, not new tests).

---

## Reading

- [x] PROJ-377 [design.md](design.md) §"Initial Analysis: per-site migration matrix" — Class A / B / C / D split
- [x] PROJ-377 [findings/initial_review.md](findings/initial_review.md) §"Site-by-site cost matrix"
- [x] `game/strategy/data/pathfinding.py` — full file (104 LOC)
- [x] `game/strategy/services/galaxy_pathfinding_service.py:36-217` — public API: `find_hybrid_path`, `get_system_at_hex`, `find_nearest_system`, `find_path_interstellar`, `find_path_deep_space`, `strip_start_hex`
- [x] PROJ-372 verifier_report.md MIN-002 (revised remediation)

---

## Tasks

### Task 2.1: Verify Class D site #9 (planet_slice.py:66) [Medium]
**File:** `tests/unit/strategy/facade/test_facade_robust_resolution.py`, `game/strategy/facade/slices/planet_slice.py`
**Tests:** `pytest tests/unit/strategy/facade/test_facade_robust_resolution.py -v`

- [x] Read `tests/unit/strategy/facade/test_facade_robust_resolution.py` lines 60-100.
- [x] Confirm whether the patches at lines 73 and 87 are reached when the SUT (the planet slice or the facade) calls `pathfinding.get_system_at_hex` from `planet_slice.py:66`.
- [x] Document the conclusion in PROJ-377 `decisions.md`: either (a) "site #9 reached by the patch — defer" or (b) "site #9 NOT reached by the patch — migrate".
- [x] **Verify:** the conclusion is recorded in decisions.md before any code change to planet_slice.py.

**Notes:**

### Task 2.2: Migrate site #3 — superweapon_order_processor.py [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/integration/strategy/superweapons/ -v` (run any superweapon-tagged tests; if not present, run the broader strategy suite)

- [x] Drop the line `from game.strategy.data.pathfinding import get_system_at_hex` (line 31).
- [x] In each of the ~10 call sites within this file (lines 345, 408, 413, 453, 470, 540, 546, 597, 605, 715 per Phase A grep), change `get_system_at_hex(galaxy, fleet.location)` (or `galaxy, fleet_location`) to `galaxy._pathfinder.get_system_at_hex(fleet.location)`. Mind the `galaxy if galaxy else None` pattern at line 715 — the migration must preserve the None-safety: `galaxy._pathfinder.get_system_at_hex(fleet_location) if galaxy else None`.
- [x] **Verify:** focused superweapon tests pass.
- [x] **Verify:** zero `from game.strategy.data.pathfinding` imports remain in this file (`Grep`).

**Notes:**

### Task 2.3: Migrate sites #10, #11, #12 — strategy_screen.py [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen*.py -v` (if exists; otherwise UI-tagged tests)

- [x] Site #10 (`calculate_hybrid_path` method, line 436): replace `from game.strategy.data.pathfinding import find_hybrid_path; return find_hybrid_path(self.galaxy, start_hex, end_hex)` with `return self.galaxy._pathfinder.find_hybrid_path(start_hex, end_hex)`.
- [x] Site #11 (`_get_system_at_hex` method, line 441): replace with `return self.galaxy._pathfinder.get_system_at_hex(hex_c)`.
- [x] Site #12 (`_find_nearest_system` method, line 446): replace with `return self.galaxy._pathfinder.find_nearest_system(hex_c)`.
- [x] **Verify:** zero `from game.strategy.data.pathfinding` imports remain in this file.
- [x] **Verify:** focused UI tests pass.

**Notes:**

### Task 2.4: Migrate site #14 — strategy_colonization.py [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_colonization*.py -v` (if exists)

- [x] Site #14 (line 258): replace `from game.strategy.data.pathfinding import get_system_at_hex; return get_system_at_hex(self.scene.galaxy, hex_coord)` with `return self.scene.galaxy._pathfinder.get_system_at_hex(hex_coord)`.
- [x] **Verify:** zero `from game.strategy.data.pathfinding` imports remain in this file.
- [x] **Verify:** focused tests pass.

**Notes:**

### Task 2.5: Migrate site #9 if Task 2.1 confirmed safe [Conditional]
**File:** `game/strategy/facade/slices/planet_slice.py`
**Tests:** `pytest tests/unit/strategy/facade/test_facade_robust_resolution.py -v`

- [x] **Skip this task if Task 2.1 concluded "defer".** Add row to `decisions.md`: "Site #9 deferred per Task 2.1 finding."
- [x] If migrate: replace `from game.strategy.data.pathfinding import get_system_at_hex; system = get_system_at_hex(self._state.session.galaxy, hex_coord, radius=50)` with `system = self._state.session.galaxy._pathfinder.get_system_at_hex(hex_coord, radius=50)`.
- [x] **Verify:** the affected facade tests pass.

**Notes:**

### Task 2.6: Pin the deferred-site list in decisions.md [Simple]
**File:** `Projects/active_projects/PROJ-377/decisions.md`

- [x] Add a row for each Class B + Class C site that is staying with the shim, citing the exact test file/line that pins it. Use the format from PROJ-377 plan.md Phase 2 scope table.
- [x] **Verify:** every of sites #1, #2, #4, #5, #6, #7, #8, #13 has a pinning row (and #9 if Task 2.1 deferred it).

**Notes:**

### Task 2.7: Re-grep production for shim importers; assert count equals deferred-site count [Simple]
**File:** N/A
**Tests:** N/A — verification only

- [x] Run: `Grep` for `from game\.strategy\.data\.pathfinding import|from game\.strategy\.data import pathfinding` under `game/`.
- [x] Expected output: 6 sites + 2 intercept-calculator sites = 8 lines (or 9 if Task 2.5 deferred site #9). Confirm count matches the deferred list.
- [x] **Verify:** count matches; if it doesn't, identify the surprise import (likely a new caller added since the planning grep) and decide migrate-or-defer.

**Notes:**

### Task 2.8: Run sharded suite + golden-fixture round-trip [Medium]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`; `pytest tests/integration/strategy/test_save_round_trip.py -v`

- [x] Sharded green; pass count unchanged from Phase 1 close.
- [x] Both golden-fixture tests still pass (proves the migration didn't change save format).
- [x] **Verify:** zero new failures introduced by migration.

**Notes:**

### Task 2.9: Commit Phase 2 [Simple]
**File:** N/A

- [x] `git add` only the migrated production files + `decisions.md`.
- [x] Commit message: `PROJ-377 phase 2: migrate N pathfinding-shim importers to galaxy._pathfinder direct calls (defer M test-patched sites)` (substitute the actual N and M).
- [x] **Verify:** `git log -1 --stat` shows expected files.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Class A sites migrated; production grep returns only Class B + Class C sites
- [x] Class D site #9 explicitly resolved (migrate or defer)
- [x] decisions.md has a pinning row per deferred site
- [x] Sharded suite green; golden-fixture tests still pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
