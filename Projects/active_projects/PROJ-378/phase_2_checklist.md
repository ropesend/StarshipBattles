# Phase 2: Sweep remaining `Galaxy.__new__` callers + opportunistic doc cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-378 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Add import at file top: `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`.
- [ ] Replace each `galaxy = Galaxy.__new__(Galaxy); galaxy._next_fleet_id = 1` pair with `galaxy = make_galaxy_stub()`. Specifically:
  - [ ] `:11-12` (`test_fleet_id_sequential`)
  - [ ] `:19-20` (`test_fleet_id_starts_at_1`)
  - [ ] `:26-27` (`test_fleet_id_persists_across_save`)
  - [ ] `:37-38` (`test_fleet_id_persists_across_save`, second instance — `galaxy2`)
  - [ ] `:45-46` (`test_multiple_empires_share_single_counter`)
- [ ] **Note:** `make_galaxy_stub()` initialises `next_fleet_id` to 1 by default (per `GalaxyState`'s field default at `galaxy_state.py:65`). The explicit `galaxy._next_fleet_id = 1` lines become redundant; remove them.
- [ ] **Note:** `test_fleet_id_persists_across_save` at `:24-41` simulates round-trip via `saved_counter = galaxy._next_fleet_id` then constructs `galaxy2`; preserve this semantics — set `galaxy2._state.next_fleet_id = saved_counter` after `make_galaxy_stub()`.
- [ ] Drop `from game.strategy.data.galaxy import Galaxy` if no other reference remains in the file (check first).
- [ ] Verify: `pytest tests/integration/strategy/test_empire.py -v` shows all 5 (or however many parametrize to) tests passing.

**Notes:** [Filled during implementation]

---

### Task 2.2: Migrate `tests/integration/strategy/test_fleet_registration_lifecycle.py` (1 inline factory) [Simple]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py:63-80`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py -v`

- [ ] Add import: `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`.
- [ ] Replace the inline factory body at `:74-80`:
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
- [ ] **Note:** `gal.warp_points = []` is a test-specific attribute set on the instance dict (not part of `GalaxyState`). Preserve it — some tests in this file expect the attribute. Do NOT move it into the stub factory.
- [ ] Drop the now-unused imports inside the fixture: `from game.strategy.data.galaxy_entity_registry import ...`, `from game.strategy.data.galaxy_spatial_index import ...`, `from game.strategy.data.galaxy_state import ...` (verify none are used elsewhere in the file before removing).
- [ ] Verify: `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py -v` reports the same pass count as before the migration (no regressions).

**Notes:** [Filled during implementation]

---

### Task 2.3: Verify zero remaining legacy-pattern call sites [Simple]
**File:** `tests/` (full)
**Tests:** Grep audit + sharded suite

- [ ] Run `Grep` (or `python Projects/scripts/audit_grep.py` if available): pattern `Galaxy\.__new__\(Galaxy\)`, glob `tests/`. Expect **zero matches**.
- [ ] Run `Grep`: pattern `patch\.object\(Galaxy,\s*['\"]__init__['\"]`, glob `tests/`. Expect **zero matches**.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — expect baseline + 15 (the 15 setup errors converted to passes); zero new failures.
- [ ] Confirm `make_galaxy_stub()` is the only shared "minimal galaxy" factory; no duplicate factories drift back in (Grep `def make_galaxy_stub`, glob `tests/` — expect exactly one definition).

**Notes:** [Filled during implementation]

---

### Task 2.4 (OPTIONAL): Document the pattern in `docs/02_PATTERNS.md` [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** None (doc-only)

- [ ] Add a short section (~10 lines) titled "Minimal Galaxy stub for unit tests (post-PROJ-372)".
- [ ] Reference `tests/fixtures/galaxy_fixtures.py::make_galaxy_stub` as the canonical implementation; mention the optional thin `tests/unit/strategy/data/conftest.py` bridge for unit-test fixture injection.
- [ ] State the rule: tests exercising methods that only read `GalaxyState` or delegate to `_registry` / `_spatial` use the stub; tests calling generators construct a real `Galaxy(radius=...)`.
- [ ] Update the doc's `> **Last verified:**` blockquote (per docs/03_CONVENTIONS.md §9).
- [ ] **If skipped:** add a note in `decisions.md` that the doc update is deferred (Q4-style follow-up).

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked (Task 2.4 may be skipped).
- [ ] Grep `Galaxy.__new__(Galaxy)` in `tests/` — zero matches.
- [ ] Grep `patch.object(Galaxy, '__init__'` in `tests/` — zero matches.
- [ ] Sharded suite green; pass count = baseline + 15.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to "All phases complete; ready for audit / user verification."
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-378 2` per 03c.
