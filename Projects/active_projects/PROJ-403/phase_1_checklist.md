# Phase 1: Replace `_MockGalaxy` fixtures with `GalaxyState`

**Status:** Complete
**Objective:** Get the broad `tests/unit/strategy/data/ -k galaxy` selector to 0 failures by migrating two test fixtures to the canonical `GalaxyState` field shape.

---

## Tasks

### Task 1.1: Read both test files + the production delegates [Simple]
**File:** see manifest

- [x] Read `_MockGalaxy` definitions and how they're passed into delegates.
- [x] Read `game/strategy/data/galaxy_state.py` to learn the canonical `GalaxyState` field names + their types.
- [x] Read `galaxy_entity_registry.py` and `galaxy_spatial_index.py` to confirm exactly which fields the delegates read.
- [x] Decide: shared helper (under `tests/fixtures/`) or per-file local stubs? Document in `decisions.md`.

**Notes:** Decided on Option A (real `GalaxyState(radius=10)` per file, no shared helper) — fixture is one line and per-file scope keeps each test file self-contained. See `decisions.md`.

### Task 1.2: Run failing selector to confirm baseline [Simple]
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_entity_registry.py tests/unit/strategy/data/test_galaxy_spatial_index.py -v`

- [x] Run the focused command. Expected: ~36 failures with `AttributeError` mentioning `next_planet_id`, `planet_to_system`, `global_hex_planets`, `global_hex_zones`.
- [x] Confirm at least one failure of each named-attr type so the test plan covers all three field migrations.

**Notes:** Confirmed baseline: **36 failed, 21 passed** with AttributeError on `global_hex_planets`, `next_planet_id`, `planet_to_system`, etc.

### Task 1.3: Migrate `test_galaxy_entity_registry.py` [Medium]
**File:** `tests/unit/strategy/data/test_galaxy_entity_registry.py`

- [x] Replace `_MockGalaxy` with either a real `GalaxyState(...)` instance per test or a small `make_state(...)` helper using canonical fields.
- [x] Update each constructor call site from `GalaxyEntityRegistry(mock_galaxy)` to `GalaxyEntityRegistry(state)`.
- [x] Confirm the delegate still receives a `GalaxyState` (not a `Galaxy`); read production callers to confirm they pass `galaxy.state`.
- [x] Run focused tests for the file — should pass.

**Notes:** Deleted `_MockGalaxy` class. Renamed `galaxy` fixture to `state`, returns `GalaxyState(radius=10)`. Updated all in-test field reads from `galaxy._next_planet_id` etc. → `state.next_planet_id` etc. (and `galaxy.planets_by_id` → `state.planets_by_id`, `galaxy.fleets_by_id` → `state.fleets_by_id`). 30/30 file-scope tests pass.

### Task 1.4: Migrate `test_galaxy_spatial_index.py` [Medium]
**File:** `tests/unit/strategy/data/test_galaxy_spatial_index.py`

- [x] Same migration as Task 1.3, applied here.
- [x] If a shared helper was chosen, factor out at this point.
- [x] Run focused tests for the file — should pass.

**Notes:** Same migration. Deleted `_MockGalaxy`, renamed fixture, updated all `galaxy._global_hex_planets` → `state.global_hex_planets`, etc. (including `_global_hex_warp_points` → `global_hex_warp_points`). 27/27 file-scope tests pass.

### Task 1.5: Run the broad selector PROJ-394's checklist asserts [Simple]
**Tests:** `pytest tests/unit/strategy/data/ -k galaxy -q`

- [x] 0 failures.
- [x] If new failures appear, triage. They may be unrelated test-isolation flakes — re-run individually.

**Notes:** **192 passed, 0 failed.**

### Task 1.6: Cross-check production callers
**Tests:** `rg -n "GalaxyEntityRegistry\(|GalaxySpatialIndex\(" game/`

- [x] Confirm every production constructor passes `galaxy.state` (or a `GalaxyState`), not `galaxy`.
- [x] If any production caller is still passing `galaxy`, fix it (this would be a latent bug — note in `decisions.md`).

**Notes:** Two hits, both in `game/strategy/data/galaxy.py:63-64`, both pass `self._state`. Production is clean — no fixes needed.

### Task 1.7: Closeout
- [x] Update Phase 1 status to `Complete`
- [x] Update plan.md Quick Status + Current State
- [x] Update `Projects/projects_index.md` row for PROJ-403 to `Complete`
- [x] Validators pass
- [x] Commit `PROJ-403 phase 1: migrate _MockGalaxy fixtures to GalaxyState`

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] `pytest tests/unit/strategy/data/ -k galaxy -q` passes
- [x] `python Projects/scripts/validate_phase.py PROJ-403 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-403` PASSED
