# Phase 1: Thread `rng` through generation, then remove the two global `random.seed()` calls

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-473 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make galaxy generation draw from an explicit, seeded per-instance `rng` so the
global `random.seed()` calls (ST-04-010 / ST-04-011) become unnecessary, then remove them —
without changing what a fixed seed generates. **Determinism is sacred:** a before/after
reproducibility characterization test gates the seed removal.

---

## Tasks

### Task 1.1: Characterization test — fixed-seed galaxy reproducibility (BASELINE) [Medium]
**File:** `tests/unit/strategy/generation/` (new test)
**Tests:** the new test itself; then `pytest tests/ --testmon`

- [ ] Write a test that generates a galaxy (or invokes `StarGenerator` + planet/naming
      generation) twice with the SAME `galaxy_seed` and asserts the results are identical
      (stars' masses/types, planet attributes, names, warp layout — whatever uniquely
      characterizes the generated output). Confirm it PASSES on current code (this is the
      baseline the threading work must preserve).
- [ ] Add a companion assertion that, with the CURRENT code, generation perturbs the global
      `random` state (snapshot `random.getstate()` before/after) — documents the debt being
      removed.
- [ ] Verify: baseline test green on unchanged code.

### Task 1.2: Thread `rng` through `StarGenerator` [Complex]
**File:** `game/strategy/generation/star_generator.py`
**Tests:** `pytest tests/ -k star_generator`; then `pytest tests/ --testmon`

- [ ] Add an explicit `rng: random.Random` (constructor or per-call) and replace all 26 bare
      `random.*` draws with `rng.*`, preserving exact call order so the seeded sequence is
      unchanged.
- [ ] Verify: the Task 1.1 reproducibility test still passes when the seeded rng is injected.

### Task 1.3: Thread `rng` through planet / atmosphere / naming / warp generation [Complex]
**File:** `game/strategy/data/planet_gen.py`, `planet_gen_surface.py`, `planet_physics.py`, `planet_atmosphere.py`, `naming.py`, `galaxy_warp_generator.py`
**Tests:** `pytest tests/ -k "planet or naming or warp"`; then `pytest tests/ --testmon`

- [ ] Thread an explicit `rng` through each generation entry point; replace bare `random.*`
      with `rng.*`, preserving call order.
- [ ] Verify: reproducibility test still passes.

### Task 1.4: Remove placement-strategy global `rng` fallback [Medium]
**File:** `game/strategy/generation/placement_strategies.py`
**Tests:** `pytest tests/ -k placement`; then `pytest tests/ --testmon`

- [ ] Remove the `if rng is None: rng = random.Random()` unseeded fallbacks on the generation
      path (lines ~90-91, ~163). Require an explicit rng (construct the seeded one at the
      single composition site in `game_initializer` instead).
- [ ] Verify: no generation path silently constructs an unseeded `random.Random()`.

### Task 1.5: Inject seeded rng at composition sites + REMOVE both global `random.seed()` calls [Medium]
**File:** `game/strategy/engine/game_initializer.py`, `game/ui/screens/galaxy_test/galaxy_mode.py`
**Tests:** `pytest tests/unit/quality/test_no_unseeded_random.py`; `pytest tests/ -k "game_initializer or galaxy_mode"`; then `pytest tests/ --testmon`

- [ ] Pass the already-constructed seeded `rng = random.Random(galaxy_seed)` into all
      generation calls.
- [ ] Delete the global `random.seed(galaxy_seed)` in `game_initializer.py` (~line 250,
      ST-04-010) and `random.seed(self.galaxy_seed)` in `galaxy_mode.py` (~line 239,
      ST-04-011).
- [ ] Update the Task 1.1 global-RNG-perturbation assertion to now prove generation no longer
      touches global `random` state.
- [ ] Verify: reproducibility test still passes (same galaxy for the same seed); no global
      `random.seed()` remains in either file; full suite green.

### Task 1.6: Tighten the Pattern #18 guard exclusion [Simple]
**File:** `tests/unit/quality/test_no_unseeded_random.py`
**Tests:** `pytest tests/unit/quality/test_no_unseeded_random.py`; then `pytest tests/ --testmon`

- [ ] Now that strategy generation draws only from a seeded instance rng, tighten / re-scope
      the strategy-generation exclusion so the guard would catch a regression.
- [ ] Verify: guard test passes and no longer blanket-excludes the now-clean generation
      modules.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
