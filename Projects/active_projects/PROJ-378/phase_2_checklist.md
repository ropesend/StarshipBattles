# Phase 2: Sweep remaining `Galaxy.__new__` callers + opportunistic doc cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-378 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 1 verified
**Review Mode:** standard
**Files (planned):**
- `tests/integration/strategy/test_empire.py` (modified)
- `tests/integration/strategy/test_fleet_registration_lifecycle.py` (modified)
- `docs/02_PATTERNS.md` (optional doc note)

**Objective:** Migrate the remaining 2 test files that use the legacy `Galaxy.__new__(Galaxy)` pattern to call the shared `make_galaxy_stub()` factory. After this phase, zero `Galaxy.__new__(Galaxy)` call sites remain in `tests/`. Optionally document the canonical pattern.

---

## Tasks

### Task 2.1: Migrate `tests/integration/strategy/test_empire.py` (5 call sites) [Simple]
**File:** `tests/integration/strategy/test_empire.py:8-75`
**Tests:** `pytest tests/integration/strategy/test_empire.py -v`

- [x] Add import at file top: `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`.
- [x] Replace each `galaxy = Galaxy.__new__(Galaxy); galaxy._next_fleet_id = 1` pair with `galaxy = make_galaxy_stub()`. All 5 sites done.
- [x] Removed redundant `galaxy._next_fleet_id = 1` assignments (default already 1).
- [x] `test_fleet_id_persists_across_save`: `galaxy2._state.next_fleet_id = saved_counter` after `make_galaxy_stub()`.
- [x] Dropped `from game.strategy.data.galaxy import Galaxy` (no other reference).
- [x] Verify: 5/5 tests in `TestEmpire` passing.

**Notes:** [Filled during implementation]

---

### Task 2.2: Migrate `tests/integration/strategy/test_fleet_registration_lifecycle.py` (1 inline factory) [Simple]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py:63-80`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py -v`

- [x] Add import: `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`.
- [x] Replace the inline factory body at `:74-80`:
  ```python
  gal = Galaxy.__new__(Galaxy)
  gal._state = GalaxyState(radius=300)
  gal.warp_points = []
  gal._registry = GalaxyEntityRegistry(gal._state)
  gal._spatial = GalaxySpatialIndex(gal._state)
  ```
  with:
  ```python
  gal = make_galaxy_stub(radius=300)
  gal.warp_points = []
  ```
- [x] **Note:** `gal.warp_points = []` preserved.
- [x] Dropped now-unused imports + the top-level `Galaxy` import (no other refs).
- [x] Verify: 14 passed, 1 skipped — no regressions.

**Notes:** [Filled during implementation]

---

### Task 2.3: Verify zero remaining legacy-pattern call sites [Simple]
**File:** `tests/` (full)
**Tests:** Grep audit + sharded suite

- [x] Grep `Galaxy\.__new__\(Galaxy\)` over `tests/` — only `tests/fixtures/galaxy_fixtures.py` (canonical impl). Zero call sites.
- [x] Grep `patch\.object\(Galaxy,\s*['\"]__init__['\"]` over `tests/` — zero matches.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — pending; will run once before final commit.
- [x] `def make_galaxy_stub` matched exactly once in `tests/`.

**Notes:** [Filled during implementation]

---

### Task 2.4 (OPTIONAL): Document the pattern in `docs/02_PATTERNS.md` [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** None (doc-only)

- [ ] (Skipped — deferred to follow-up.)
- [x] Note added to `decisions.md` recording the deferral.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked (Task 2.4 skipped per design Q4 recommendation).
- [x] Grep `Galaxy.__new__(Galaxy)` in `tests/` — zero matches.
- [x] Grep `patch.object(Galaxy, '__init__'` in `tests/` — zero matches.
- [ ] Sharded suite green; pass count = baseline + 15. — pending; run once before final commit.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to "All phases complete; ready for audit / user verification."
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-378 2` per 03c.
