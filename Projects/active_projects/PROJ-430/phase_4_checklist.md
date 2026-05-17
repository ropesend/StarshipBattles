# Phase 4: Migrate tests off legacy cache seams

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `game/strategy/facade/slices/_facade_state.py` (add `seed_*` helpers)
- `tests/unit/strategy/facade/test_colony_demographic_view.py` (rewrite seeding)
- `tests/unit/strategy/facade/test_facade_indices.py` (rewrite `hasattr` to behavioral assertion)
- `tests/unit/strategy/facade/test_strategy_session_facade.py` (survey for incidental legacy-alias use)

**Objective:** Provide a public test-seeding seam on `FacadeSessionState` and migrate the 3 cache-forwarder-pinning test files onto it. After this phase, no test writes to `facade._planet_index` / `facade._race_registry` / etc. — clearing the way for Phase 5's root-cause deletion.

---

## Tasks

### Task 4.1: Add `seed_*` helpers to `FacadeSessionState` [Medium]
**File:** `game/strategy/facade/slices/_facade_state.py`
**Tests:** new unit tests for the helpers (Task 4.4)

- [ ] Add `seed_planet_index(self, mapping: dict[int, Planet]) -> None` — populates the underlying planet-index cache. Docstring explicitly states "test-only seam; production code populates the index via the slice's own caching path."
- [ ] Add `seed_race_registry(self, registry: RaceRegistry) -> None` — sets the race registry. Same docstring intent.
- [ ] Add equivalents for `_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`, `_fleets_by_hex_turn` **only if** the existing 3 test files (or any test surfaced in Task 4.3) write to them. Don't add unused helpers.
- [ ] Method names use the `seed_` prefix so the test-only intent is obvious at the call site.
- [ ] **Preferred alternative for `seed_race_registry`:** if the race registry can be passed through the slice/economy constructor at facade-init time as DI (no refactor sprawl), do that instead and skip the `seed_race_registry` helper. Record the decision (helper vs. constructor DI) in `decisions.md`.
- [ ] Each new public method has a type annotation per project convention (CLAUDE.md "Key Conventions").

**Notes:** [Filled during implementation. Per the TD-08 plan: "the `seed_*` helper makes the test-only intent explicit."]

### Task 4.2: Rewrite `test_colony_demographic_view.py` to use the new seam [Medium]
**File:** `tests/unit/strategy/facade/test_colony_demographic_view.py`
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py -q`

- [ ] In `_facade_for(...)` (lines 82-103), replace:
  - `facade._planet_index = {planet.id: planet}` (line 95) -> `facade.facade_state.seed_planet_index({planet.id: planet})`
  - `facade._race_registry = race_registry` (line 98) -> `facade.facade_state.seed_race_registry(race_registry)` *or* the constructor-DI alternative from Task 4.1.
- [ ] At line 125, `facade._planet_index = {}` -> `facade.facade_state.seed_planet_index({})`.
- [ ] **Behavioral assertions on `get_colony_demographic_view` return value must stay unchanged.** Diff before/after — no `assert` lines dropped.
- [ ] Run the test:
  ```
  pytest tests/unit/strategy/facade/test_colony_demographic_view.py -q
  ```
  Expected: green.

**Notes:** [Filled during implementation. Per the TD-08 plan: "the behavioral assertions stay intact; only the *seeding mechanism* changes." Per AGENTS.md: don't silently relax coverage.]

### Task 4.3: Rewrite `test_facade_indices.py` `hasattr` to behavioral assertion [Simple]
**File:** `tests/unit/strategy/facade/test_facade_indices.py`
**Tests:** `pytest tests/unit/strategy/facade/test_facade_indices.py -q`

- [ ] At line 46, replace:
  - `assert hasattr(facade, '_planet_index')` -> `assert facade.planets.get(42) is facade.planets.get(42)` (cached identity — the *behavior* the original assertion was approximating via implementation detail).
- [ ] Adapt the surrounding test setup so the planet ID used is one that exists in the fixture. If no planet exists with the ID, seed one via `facade.facade_state.seed_planet_index(...)` from Task 4.1.
- [ ] Run the test, confirm green.

**Notes:** [Filled during implementation. Per the TD-08 plan: "assert *behavior* (second call returns the same object) instead of *implementation* (the index field exists)."]

### Task 4.4: Survey `test_strategy_session_facade.py` for incidental legacy use [Simple]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py -q`

- [ ] Grep within the file for legacy alias calls, top-level `dispatch_*` calls, top-level `get_*` calls, and direct cache-attr writes:
  ```
  rg -n "facade\.(_resolve_economy_config|dispatch_|get_fleet|get_planet|_planet_index|_race_registry|_all_stars_cache|_fleets_by_hex_cache)" tests/unit/strategy/facade/test_strategy_session_facade.py
  ```
- [ ] Migrate each occurrence to the grouped surface (or to the `seed_*` helper, for cache writes).
- [ ] Run the test, confirm green.

**Notes:** [Filled during implementation]

### Task 4.5: Repo-wide sweep for any remaining legacy cache writes [Simple]
**Files:** none initially (discovery)
**Tests:** none

- [ ] Run a repo-wide grep for direct cache-attr writes on the facade:
  ```
  rg -n "facade\.(_planet_index|_all_stars_cache|_fleets_by_hex_cache|_race_registry|_all_stars_cache_turn|_fleets_by_hex_turn)" tests/ game/
  ```
  Expected: zero hits outside `_facade_state.py` (where the underlying field lives) and the `seed_*` helpers themselves. Any remaining test or production hit must be migrated.
- [ ] Run a repo-wide grep for the legacy alias:
  ```
  rg -n "_resolve_economy_config" tests/ game/
  ```
  Expected: zero hits outside `strategy_session_facade.py` (the alias method body — gone in Phase 5) and `economy_slice.py:75` (the warning-log fallback — handled per TD-02 coupling note in Phase 5).
- [ ] Record any unexpected hits in `findings/phase_4_residual_legacy_callers.md` and migrate before completing the phase.

**Notes:** [Filled during implementation. Per the TD-08 plan: "Sweep for any other test file that still writes to a legacy cache attr."]

### Task 4.6: Verify the focused facade suite is fully green except the Phase-5-anchored assertions [Simple]
**Files:** none (verification)
**Tests:** focused facade suite

- [ ] Run:
  ```
  pytest tests/unit/strategy/facade -q
  ```
- [ ] Expected: green except for two Phase-1 contract assertions (`test_no_legacy_flat_methods`, `test_legacy_cache_attrs_removed`). All other tests — including the rewritten `test_colony_demographic_view.py` and `test_facade_indices.py` — pass.

**Notes:** [Filled during implementation. After this phase, the only remaining red is the assertions that anchor Phase 5's deletion. Phase 5 flips them green by removing the legacy surface.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `FacadeSessionState` exposes the necessary `seed_*` helpers (or the equivalent constructor DI)
- [ ] `test_colony_demographic_view.py` migrated; behavioral assertions intact
- [ ] `test_facade_indices.py` `hasattr` rewritten to behavioral assertion
- [ ] `test_strategy_session_facade.py` surveyed; any incidental legacy use migrated
- [ ] Repo-wide sweep shows zero unexpected legacy cache writes or `_resolve_economy_config` callers
- [ ] Focused facade suite green except the two Phase-1 contract assertions deliberately anchored for Phase 5
- [ ] `python Projects/scripts/validate_phase.py PROJ-430 4` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
