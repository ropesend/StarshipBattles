# Phase 1: Shared `make_galaxy_stub()` fixture + migrate `test_galaxy_cleanup.py`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-378 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):**
- `tests/fixtures/galaxy_fixtures.py` (new — canonical implementation module)
- `tests/unit/strategy/data/conftest.py` (new, optional thin pytest fixture bridge)
- `tests/unit/strategy/data/test_galaxy_cleanup.py` (modified)

**Objective:** Introduce `make_galaxy_stub()` in `tests/fixtures/galaxy_fixtures.py` (the canonical implementation, importable cross-tree per the established `tests.fixtures.*` convention — see `tests/fixtures/README.md`). Optionally add a thin `tests/unit/strategy/data/conftest.py` that delegates a `galaxy_stub` pytest fixture to `make_galaxy_stub()` for ergonomic injection inside this directory. Migrate all three setup fixtures in `test_galaxy_cleanup.py` to use the function; verify all 15 errors resolve to passes with no regression in the rest of the file.

---

## Tasks

### Task 1.1: Add `tests/fixtures/galaxy_fixtures.py` with `make_galaxy_stub()` factory + optional pytest fixture bridge [Simple]
**File:** `tests/fixtures/galaxy_fixtures.py` (new — canonical implementation), `tests/unit/strategy/data/conftest.py` (new, optional thin bridge)
**Tests:** N/A (will be exercised by Task 1.3)

- [ ] Create new file `tests/fixtures/galaxy_fixtures.py` (this is the canonical implementation module, mirroring the established `tests.fixtures.*` convention — see `tests/fixtures/README.md`, `tests/fixtures/ai.py`, `tests/fixtures/battle.py`, `tests/fixtures/common.py`).
- [ ] Add module docstring referencing PROJ-378 and the post-PROJ-372 facade.
- [ ] Implement `make_galaxy_stub(radius: int = 100) -> Galaxy:` per the design doc:
  ```python
  from game.strategy.data.galaxy import Galaxy
  from game.strategy.data.galaxy_state import GalaxyState
  from game.strategy.data.galaxy_entity_registry import GalaxyEntityRegistry
  from game.strategy.data.galaxy_spatial_index import GalaxySpatialIndex


  def make_galaxy_stub(radius: int = 100) -> Galaxy:
      """Construct a minimal post-PROJ-372 Galaxy for unit tests, bypassing __init__'s heavy I/O."""
      galaxy = Galaxy.__new__(Galaxy)
      galaxy._state = GalaxyState(radius=radius)
      galaxy._registry = GalaxyEntityRegistry(galaxy._state)
      galaxy._spatial = GalaxySpatialIndex(galaxy._state)
      return galaxy
  ```
- [ ] Docstring on `make_galaxy_stub` lists which methods are safe to call (anything that delegates to `_registry` / `_spatial` or reads `_state`) and which are NOT (anything calling generators — `generate_systems`, `generate_planets`, `generate_warp_lanes`); for those, use real `Galaxy(radius=...)`.
- [ ] (Optional but recommended) Create `tests/unit/strategy/data/conftest.py` as a thin pytest fixture bridge that delegates to the implementation:
  ```python
  import pytest
  from tests.fixtures.galaxy_fixtures import make_galaxy_stub


  @pytest.fixture
  def galaxy_stub():
      return make_galaxy_stub()
  ```
  This gives unit tests in this directory a one-line fixture-injection API while integration tests import `make_galaxy_stub` directly.
- [ ] Verify: `python -c "from tests.fixtures.galaxy_fixtures import make_galaxy_stub; g = make_galaxy_stub(); assert g.radius == 100; assert g.systems == {}"` succeeds.

**Notes:** [Filled during implementation]

---

### Task 1.2: Migrate `TestGalaxyUnregisterPlanet.galaxy_with_planet` fixture [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_cleanup.py:58-104`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_cleanup.py::TestGalaxyUnregisterPlanet -v`

- [ ] Replace the entire `with patch.object(Galaxy, '__init__', lambda self, radius=100: None):` block at `:62-103` with a `make_galaxy_stub()` call.
- [ ] **Before:**
  ```python
  with patch.object(Galaxy, '__init__', lambda self, radius=100: None):
      galaxy = Galaxy.__new__(Galaxy)
      galaxy.radius = 100
      galaxy.systems = {}
      galaxy.name_map = {}
      galaxy._next_planet_id = 1
      galaxy.planets_by_id = {}
      galaxy._planet_to_system = {}
      galaxy._global_hex_planets = {}
      galaxy._global_hex_zones = {}
      galaxy.fleets_by_id = {}
      galaxy._registry = GalaxyEntityRegistry(galaxy)  # NB: pre-PROJ-372 signature
      # ... (rest of fixture)
  ```
  **After:**
  ```python
  galaxy = make_galaxy_stub()
  # ... (rest of fixture, unchanged: planet creation + state population via galaxy._state.* or via galaxy.register_planet)
  ```
- [ ] Remove the local `from game.strategy.data.galaxy_entity_registry import GalaxyEntityRegistry` import inside the fixture (no longer needed; the stub wires it).
- [ ] Update the manual registration block at `:94-102` — keep the inline mutations against `galaxy._state.*` or `galaxy._registry.register_planet(...)`. (The current code mutates the un-prefixed dicts; verify all six mutations land on `galaxy._state.*` correctly via property forwarders.)
- [ ] Drop the now-unused `from unittest.mock import ... patch` import if no other test uses it (check the file's other imports first).
- [ ] Verify: `pytest tests/unit/strategy/data/test_galaxy_cleanup.py::TestGalaxyUnregisterPlanet -v` shows 5 passed, 0 errors.

**Notes:** [Filled during implementation]

---

### Task 1.3: Migrate `TestGalaxyRemoveWarpLink.galaxy_with_warp_link` fixture [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_cleanup.py:163-190`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_cleanup.py::TestGalaxyRemoveWarpLink -v`

- [ ] Replace the `with patch.object(...)` block at `:166-188` with `galaxy = make_galaxy_stub()`.
- [ ] Reset/replace the inline state population — `galaxy.systems[system_a.global_location] = system_a` works through the property forwarder, but for clarity and to mirror the production wiring, prefer `galaxy._state.systems[...] = ...` inside test setup.
- [ ] Note: `Galaxy.remove_warp_link` at `galaxy.py:209-232` reads `self._state.name_map` and `self._state.global_hex_warp_points` directly — no service delegation. Stub provides this via `_state`. No additional wiring needed.
- [ ] Verify: `pytest tests/unit/strategy/data/test_galaxy_cleanup.py::TestGalaxyRemoveWarpLink -v` shows 4 passed, 0 errors.

**Notes:** [Filled during implementation]

---

### Task 1.4: Migrate `TestGalaxyGetAllFleetsInSystem.galaxy_with_fleets` fixture [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_cleanup.py:245-294`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_cleanup.py::TestGalaxyGetAllFleetsInSystem -v`

- [ ] Replace the `with patch.object(...)` block at `:248-273` with `galaxy = make_galaxy_stub()`.
- [ ] Note: `Galaxy.get_all_fleets_in_system` at `galaxy.py:238-240` delegates to `self._spatial.get_all_fleets_in_system(...)` — stub wires `_spatial` (Task 1.1). No additional wiring needed.
- [ ] State population: `galaxy.systems[...] = ...` and `galaxy.name_map[...] = ...` route through property forwarders correctly (read-modify on the forwarded dict). Inline writes work; the test's existing logic doesn't need restructuring.
- [ ] Verify: `pytest tests/unit/strategy/data/test_galaxy_cleanup.py::TestGalaxyGetAllFleetsInSystem -v` shows 6 passed, 0 errors.

**Notes:** [Filled during implementation]

---

### Task 1.5: Run full target test file and confirm no regressions [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_cleanup.py` (full)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_cleanup.py -v`

- [ ] Run the full file; expect **18 passed, 0 errors** (was 3 passed, 15 errors; 18 tests collected total).
- [ ] Spot-check: the `TestDysonSpherePlanetType` class at `:13-52` is unchanged (tests the enum, not Galaxy state) — ensure its 3 tests still pass.
- [ ] Run an adjacent unit test to verify no global-state pollution: `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_state.py -v` — expect all-pass.
- [ ] Confirm: `Grep` for `patch.object(Galaxy,` in `tests/unit/strategy/data/test_galaxy_cleanup.py` returns zero matches.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] `pytest tests/unit/strategy/data/test_galaxy_cleanup.py -v` reports 18 passed, 0 errors.
- [ ] `python -c "import ast, pathlib; src = pathlib.Path('tests/unit/strategy/data/test_galaxy_cleanup.py').read_text(); assert 'patch.object(Galaxy' not in src; assert 'Galaxy.__new__' not in src"` succeeds.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 2.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-378 1` per 03c.
