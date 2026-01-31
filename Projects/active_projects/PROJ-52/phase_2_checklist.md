# Phase 2: Galaxy Generator Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Integrate density-based placement with existing Galaxy class

---

## Task 2.1: Create Placement Strategy Interface [Simple]
**File:** `game/strategy/generation/placement_strategies.py`
**Tests:** `python -m pytest tests/unit/strategy/generation/test_placement_strategies.py`

- [ ] Define `ISystemPlacementStrategy` protocol with `sample_location(radius, existing_systems, min_dist) -> Optional[HexCoord]`
- [ ] Extract current random logic to `RandomPlacementStrategy` class
- [ ] Implement `DensityBasedPlacementStrategy` using `DensityMap`
- [ ] Both strategies must respect `min_dist` constraint

**Notes:**

---

## Task 2.2: Add Galaxy Type to GameConfig [Simple]
**File:** `game/strategy/engine/game_config.py`
**Tests:** `python -m pytest tests/unit/strategy/engine/test_game_config.py`

- [ ] Add `galaxy_type: str = "random"` field (line ~111)
- [ ] Add `galaxy_seed: Optional[int] = None` field for deterministic generation
- [ ] Add validation in `__post_init__` for valid galaxy types
- [ ] Update `to_dict()` and `from_dict()` methods

**Notes:**

---

## Task 2.3: Modify Galaxy.generate_systems() [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `python -m pytest tests/integration/strategy/test_galaxy_gen.py`

- [ ] Add `placement_strategy: Optional[ISystemPlacementStrategy] = None` parameter (line 198)
- [ ] Default to `RandomPlacementStrategy()` if None
- [ ] Replace random coordinate generation (lines 209-214) with `placement_strategy.sample_location()`
- [ ] Keep existing min_dist validation logic
- [ ] Ensure return type remains `List[StarSystem]`

**Notes:**

---

## Task 2.4: Update GameSession._initialize_galaxy() [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `python -m pytest tests/integration/strategy/test_galaxy_gen.py`

- [ ] Load layout config based on `config.galaxy_type` (line 126)
- [ ] Set `random.seed(config.galaxy_seed)` if provided
- [ ] Create appropriate placement strategy
- [ ] Pass strategy to `galaxy.generate_systems()`
- [ ] Log galaxy type being generated

**Notes:**

---

## Task 2.5: Add Seed Control Throughout Generation [Medium]
**Files:** `galaxy.py`, `stars.py`, `planet_gen.py`
**Tests:** `python -m pytest tests/integration/strategy/test_deterministic_generation.py`

- [ ] Create new test verifying same seed produces identical galaxy
- [ ] Audit all `random.*` calls in generation pipeline
- [ ] Ensure seeding at GameSession level propagates correctly
- [ ] Document seed usage in docstrings

**Notes:**

---

## Task 2.6: Update Existing Tests [Simple]
**Files:** `tests/integration/strategy/test_galaxy_gen.py`, `conftest.py`
**Tests:** Run full test suite

- [ ] Update test fixtures to use explicit placement strategy
- [ ] Add tests for density-based placement
- [ ] Verify existing tests still pass with `RandomPlacementStrategy`
- [ ] Add test for `galaxy_type` in GameConfig

**Notes:**

---

## Phase 2 Verification
- [ ] All unit tests pass: `python -m pytest tests/unit/strategy/generation/`
- [ ] All integration tests pass: `python -m pytest tests/integration/strategy/test_galaxy_gen.py`
- [ ] `galaxy_type="spiral"` generates visibly different layout than "random"
- [ ] Same seed produces identical galaxy
- [ ] All existing tests pass with `RandomPlacementStrategy`
- [ ] Full test suite still passes: `python -m pytest tests/`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

## Handoff Notes
(To be filled when phase completes)
