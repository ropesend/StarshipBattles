# Phase 1: Replace `_MockGalaxy` fixtures with `GalaxyState`

**Status:** Not Started
**Objective:** Get the broad `tests/unit/strategy/data/ -k galaxy` selector to 0 failures by migrating two test fixtures to the canonical `GalaxyState` field shape.

---

## Tasks

### Task 1.1: Read both test files + the production delegates [Simple]
**File:** see manifest

- [ ] Read `_MockGalaxy` definitions and how they're passed into delegates.
- [ ] Read `game/strategy/data/galaxy_state.py` to learn the canonical `GalaxyState` field names + their types.
- [ ] Read `galaxy_entity_registry.py` and `galaxy_spatial_index.py` to confirm exactly which fields the delegates read.
- [ ] Decide: shared helper (under `tests/fixtures/`) or per-file local stubs? Document in `decisions.md`.

**Notes:**

### Task 1.2: Run failing selector to confirm baseline [Simple]
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_entity_registry.py tests/unit/strategy/data/test_galaxy_spatial_index.py -v`

- [ ] Run the focused command. Expected: ~36 failures with `AttributeError` mentioning `next_planet_id`, `planet_to_system`, `global_hex_planets`, `global_hex_zones`.
- [ ] Confirm at least one failure of each named-attr type so the test plan covers all three field migrations.

**Notes:**

### Task 1.3: Migrate `test_galaxy_entity_registry.py` [Medium]
**File:** `tests/unit/strategy/data/test_galaxy_entity_registry.py`

- [ ] Replace `_MockGalaxy` with either a real `GalaxyState(...)` instance per test or a small `make_state(...)` helper using canonical fields.
- [ ] Update each constructor call site from `GalaxyEntityRegistry(mock_galaxy)` to `GalaxyEntityRegistry(state)`.
- [ ] Confirm the delegate still receives a `GalaxyState` (not a `Galaxy`); read production callers to confirm they pass `galaxy.state`.
- [ ] Run focused tests for the file — should pass.

**Notes:**

### Task 1.4: Migrate `test_galaxy_spatial_index.py` [Medium]
**File:** `tests/unit/strategy/data/test_galaxy_spatial_index.py`

- [ ] Same migration as Task 1.3, applied here.
- [ ] If a shared helper was chosen, factor out at this point.
- [ ] Run focused tests for the file — should pass.

**Notes:**

### Task 1.5: Run the broad selector PROJ-394's checklist asserts [Simple]
**Tests:** `pytest tests/unit/strategy/data/ -k galaxy -q`

- [ ] 0 failures.
- [ ] If new failures appear, triage. They may be unrelated test-isolation flakes — re-run individually.

**Notes:**

### Task 1.6: Cross-check production callers
**Tests:** `rg -n "GalaxyEntityRegistry\(|GalaxySpatialIndex\(" game/`

- [ ] Confirm every production constructor passes `galaxy.state` (or a `GalaxyState`), not `galaxy`.
- [ ] If any production caller is still passing `galaxy`, fix it (this would be a latent bug — note in `decisions.md`).

**Notes:**

### Task 1.7: Closeout
- [ ] Update Phase 1 status to `Complete`
- [ ] Update plan.md Quick Status + Current State
- [ ] Update `Projects/projects_index.md` row for PROJ-403 to `Complete`
- [ ] Validators pass
- [ ] Commit `PROJ-403 phase 1: migrate _MockGalaxy fixtures to GalaxyState`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Status at top of this file is `Complete`
- [ ] plan.md updated
- [ ] `pytest tests/unit/strategy/data/ -k galaxy -q` passes
- [ ] `python Projects/scripts/validate_phase.py PROJ-403 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-403` PASSED
