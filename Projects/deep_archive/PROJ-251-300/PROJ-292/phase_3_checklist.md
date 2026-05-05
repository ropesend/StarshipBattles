# Phase 3: H2 + M2 — Pin projector vs engine drain + CachedRaceRegistry invalidation tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-292 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add two integration/unit tests pinning two contracts that currently rely only on docstrings: (H2) the projector's yard-drain matches what `ProductionEngine` actually drains; (M2) `CachedRaceRegistry.invalidate(race_id)` actually causes a re-read of the underlying loader. Optionally (user decision) add an mtime fallback to the registry.

---

## Tasks

### Task 3.1: Write the H2 projector-vs-engine integration test [Complex]
**File:** `tests/integration/strategy/test_projector_drain_matches_engine.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_projector_drain_matches_engine.py -v`

- [x] Read [tests/integration/strategy/test_growth_rate_equivalence.py](tests/integration/strategy/test_growth_rate_equivalence.py) for the test-style pattern. Reuse the same Planet construction helpers if possible.
- [x] Test 1: `test_yard_drain_projection_matches_engine_tick_for_planetary_yard`. Construct a planet with a planetary-yard facility + one queued complex (e.g. cost `{"metals": 1000}`). Set up `economy_config = EconomyConfig(population_consumption={"organics": 0.001})`. Compute the projection: `projector.project(planet)`. Get `projected_drain[r] = -projection[r].yard` for `yard > 0`. Snapshot `pre_stockpile = dict(planet.stockpile)`. Run `ProductionEngine(...).process_construction_tick(tick=1, empires=[empire], galaxy=None)`. Compute `actual_drain[r] = pre_stockpile[r] - planet.stockpile[r]`. Assert `actual_drain * 100 == pytest.approx(projected_drain, rel=0.01)` for every drained resource (per-tick × 100 ticks per turn).
- [x] Test 2: `test_yard_drain_zero_when_queue_empty`. Planet with shipyard but empty queue. Project. Tick. Assert both drain dicts are empty/zero.
- [x] Test 3: `test_multi_queue_drain_aggregates`. Planet with planetary yard + 2 shipyards, each with one queued item. Project. Run one tick. Assert per-resource projected drain == sum of per-queue actual drain * 100.
- [x] Run all three tests — should pass with the current code. (The test is a contract pin, not a bug fix.)

**Notes:** This is the regression-prevention contract for the private-API reach in `_project_yard_drain`. If `_collect_planet_sources` ever refactors, these tests fail loudly.

### Task 3.2: Write the M2 CachedRaceRegistry staleness test [Medium]
**File:** [tests/unit/strategy/systems/test_race_library.py](tests/unit/strategy/systems/test_race_library.py)
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py::TestCachedRaceRegistryStaleness -v`

- [x] Add a new test class `TestCachedRaceRegistryStaleness`.
- [x] Test 1: `test_invalidate_causes_reread`. Mock `RaceLibrary.get_race` to return CONFIG_A on first call, CONFIG_B on second call (use `side_effect = [CONFIG_A, CONFIG_B]`). Construct `CachedRaceRegistry(library)`. Assert `registry.get_race("foo")` returns CONFIG_A. Assert `registry.get_race("foo")` STILL returns CONFIG_A (cached). Call `registry.invalidate("foo")`. Assert `registry.get_race("foo")` returns CONFIG_B.
- [x] Test 2: `test_invalidate_other_race_does_not_affect_cached`. Cache "foo" then "bar". Call `invalidate("foo")` only. Confirm "bar" stays cached (no re-read).
- [x] Test 3: `test_invalidate_all_clears_everything`. Cache 3 races. Call `invalidate()` (no arg). Confirm all 3 re-read on next access.
- [x] Run tests — should pass with the current code. (Pin the contract.)

**Notes:** PROJ-269 audit's "stale lazy cache" pattern is the reason this test is needed. PROJ-287 shipped without this coverage.

### Task 3.3: USER DECISION — mtime fallback for CachedRaceRegistry [User input required]
**File:** [game/strategy/systems/race_library.py](game/strategy/systems/race_library.py)
**Tests:** Conditional based on user's choice

- [x] **STOP and ask the user:** "Should `CachedRaceRegistry` get an optional `auto_refresh_on_mtime: bool = False` kwarg that file-stat-watches each cached race file and refreshes when mtime changes? **Recommend: NO** (keeps PROJ-287's documented contract; no filesystem-stat noise on every read). Recommend opting in only if mod-tooling becomes a real concern."
- [x] If user says NO: skip implementation. Document in decisions.md the user's choice. Move on.
- [x] If user says YES:
  - Add the `auto_refresh_on_mtime: bool = False` kwarg to `__init__`. Store on `self._auto_refresh`.
  - In `get_race`, if `self._auto_refresh and race_id in self._cache`, check `os.path.getmtime(self._library._path_for(race_id))` against a stored cache-write-time. If newer, evict the cache entry and re-read.
  - Add tests verifying the behaviour.

**Notes:**

### Task 3.4: Targeted regression suite [Simple]
**Tests:** `pytest tests/unit/strategy/systems/ tests/integration/strategy/ -q`

- [x] Both suites green.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
