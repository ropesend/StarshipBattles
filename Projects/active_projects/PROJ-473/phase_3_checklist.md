# Phase 3: Remove the two global `random.seed()` calls + normalize fallbacks + guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-473 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phases 0, 1, 2 (ALL generation draws now come from the seeded rng)
**Goal mapping:** All tasks serve **G3** (remove the two global seeds; normalize the
`rng is None` fallbacks; add the Pattern #18 guard).
**Objective:** Now that no generation code reads global `random` state, delete the two
load-bearing `random.seed()` calls (ST-04-010 / ST-04-011), update the dependent tests so
the `rng is None` fallbacks can be normalized, normalize those fallbacks, and add
`game/strategy` generation dirs to the Pattern #18 guard so a regression is caught.

---

## Tasks

### Task 3.1: Update tests that pin the global-random contract [Medium]
**Files:** `tests/unit/strategy/data/test_planet_gen.py` (`:42-45`),
`tests/integration/strategy/test_planet_gen.py` (`:17-18`),
`tests/integration/strategy/test_galaxy_gen.py`,
`tests/unit/strategy/generation/test_placement_strategies.py` (`:44-45`),
`tests/unit/strategy/data/test_galaxy_system_generator.py` (`:544-549`).
**Symbol/area:** these call generation with no rng or seed module-level `random`, relying
on the fallback / global-state contract (consult §4, §6).
**Caller-cleanup contract (decisions.md 2026-05-21):** public facades stay
backward-compatible (`rng=None` normalized internally to a seeded stream); only internal
leaf helpers hard-require rng. So the broad caller surface that goes through facades
(`test_galaxy_generation_storms.py`, `test_save_round_trip.py`, the two conftests,
`bench_galaxy_planet_star.py`, `test_star_generation.py`, `test_stars.py`,
`test_generation.py`, and `system_mode.py:245-263`) does **NOT** require editing — those
keep working. The five files below DO need editing because they pin the *unseeded fallback*
behavior being normalized at the placement/leaf layer.
**Test that must fail first:** N/A (this task edits tests). Run them before editing to
capture the current pass shape, edit, then confirm green.
**Run:** the five files above with `--testmon`; then `pytest tests/ --testmon`.

- [ ] `test_planet_gen.py` (unit): replace the `random.seed(42)` fixture seeding (`:42-45`)
      with constructing/passing an explicit `random.Random(42)` to the generator calls.
- [ ] `test_planet_gen.py` (integration): pass an explicit seeded rng to
      `galaxy.generate_systems(...)` (`:17-18`).
- [ ] `test_galaxy_gen.py`: pass an explicit seeded rng to `generate_systems(...)`.
- [ ] `test_placement_strategies.py`: pass an explicit seeded rng to `sample_location(...)`
      (`:44-45`).
- [ ] `test_galaxy_system_generator.py`: reconcile the `rng=None` shape test (`:544-549`)
      with the normalized contract — either pass an explicit rng, or assert the new
      explicit-rng requirement, per the Task 3.3 decision.
- [ ] Verify: all five files green with explicit rng; Task 0.1 full-save-visible
      equivalence test (now un-xfailed since Phase 2) stays green.

### Task 3.2: Remove the two global `random.seed()` calls [Medium]
**Files:** `game/strategy/engine/game_initializer.py` (`:248-250`, ST-04-010),
`game/ui/screens/galaxy_test/galaxy_mode.py` (`:239`, ST-04-011).
**Symbol/area:** `random.seed(galaxy_seed)` (`game_initializer.py:250`) and
`random.seed(self.galaxy_seed)` (`galaxy_mode.py:239`).
**Test that must fail first:** flip the Task 0.1 global-perturbation assertion to assert
generation **no longer** perturbs global `random` state (it fails before the seeds are
removed because generation still touched global only if any draw escaped — confirm it
fails first by running it before deletion, then passes after).
**Run:** `pytest tests/integration/strategy/test_galaxy_reproducibility.py -q`;
`pytest tests/ -k "game_initializer or galaxy_mode"`; then `pytest tests/ --testmon`.

- [ ] Delete `random.seed(galaxy_seed)` and its comment (`game_initializer.py:249-250`).
- [ ] Delete `random.seed(self.galaxy_seed)` (`galaxy_mode.py:239`).
- [ ] Update the Task 0.1 companion assertion to now PROVE generation does not touch global
      `random` state (snapshot `random.getstate()` before/after `initialize()` → unchanged).
      **NOTE (necessary but NOT sufficient):** `getstate()` unchanged does NOT prove
      determinism — fresh unseeded `random.Random()` fallbacks would leave global state
      untouched while still producing nondeterministic output. The authoritative proof of
      determinism is the full-save-visible equivalence test (now un-xfailed) staying green.
      Treat `getstate()` only as a coarse "the global seed is gone" tripwire.
- [ ] Verify: the Task 0.1 full-save-visible equivalence test STILL green (same galaxy for
      the same seed — THIS is the real determinism proof); global-state-unchanged assertion
      now green (coarse tripwire only); `pytest tests/ --testmon` green.

### Task 3.3: Normalize the `rng is None` fallbacks [Medium]
**Files:** `game/strategy/generation/placement_strategies.py` (`:90-91`, `:163-164`); and
the internal fallbacks at `galaxy_system_generator.py:265-266`,
`galaxy_warp_generator.py:408-409`, `planet_image_registry.py:76-77`/`:107-108`,
`star_image_registry.py:81-82` (per consult §1.4).
**Symbol/area:** `if rng is None: rng = random.Random()` (unseeded) fallbacks.
**Test that must fail first:** add a test asserting the production composition path always
supplies a concrete rng (e.g. assert `generate_systems` normalizes `rng=None` to a seeded
instance at the single site, or that passing `rng=None` raises / is no longer silently
unseeded — pick per the decision below). Fails before normalization.
**Run:** `pytest tests/ -k "placement or galaxy_system_generator"`; then
`pytest tests/ --testmon`.

- [ ] **DECIDED (decisions.md 2026-05-21): option (b) — backward-compatible facades.** Keep
      public facades (`Galaxy.generate_systems`, `Galaxy.generate_planets`,
      `Galaxy.generate_warp_lanes`, direct `StarGenerator()`/`PlanetGenerator()` use)
      accepting `rng=None` and normalize it internally to a seeded stream at a single
      composition site, rather than an independent UNSEEDED `Random()`. Internal leaf
      helpers (placement strategies, the planet/star free-function draws, the warp internals)
      hard-require a concrete rng. This avoids editing the broad caller surface (see the
      contract note at top of Task 3.1).
- [ ] Apply the normalization to `placement_strategies.py` (`:90-91`, `:163-164`)
      and the internal fallbacks at `galaxy_system_generator.py:265-266`,
      `galaxy_warp_generator.py:408-409`, `planet_image_registry.py:76-77`/`:107-108`,
      `star_image_registry.py:81-82`: replace each `if rng is None: rng = random.Random()`
      (UNSEEDED) on the generation path with either a require-rng assertion (internal
      helpers) or routing through the facade's seeded normalization. Also add an optional
      normalizing `rng` param to `Galaxy.generate_planets` (`galaxy.py:212-214`, currently
      no rng param) so the facade contract is uniform.
- [ ] Verify: no unseeded `Random()` reachable from the seeded generation path; Task 0.1
      green; the five Task 3.1 test files green.

### Task 3.4: Add `game/strategy` generation dirs to the Pattern #18 guard [Simple]
**File:** `tests/unit/quality/test_no_unseeded_random.py` (`:37`).
**Symbol/area:** `GUARDED_DIRECTORIES = ("game/simulation", "game/engine", "game/ai")` —
`game/strategy` is **absent** today (decisions.md correction: this ADDS coverage, it does
not "tighten an exclusion").
**Test that must fail first:** after adding the dirs, run the guard — it will fail on any
remaining bare `random.*` in the now-clean modules (which is the regression-catching
behavior we want). Confirm it goes from fail (if any stragglers) → pass once clean.
**Run:** `pytest tests/unit/quality/test_no_unseeded_random.py -q`; then
`pytest tests/ --testmon`.

- [ ] Add `game/strategy/generation` and `game/strategy/data` to `GUARDED_DIRECTORIES`.
- [ ] If any legitimate tool-only / non-generation bare `random.*` remains in those dirs,
      annotate it with the existing `# noqa: replay-determinism` allowlist marker (`:43`)
      and justify; otherwise the guard should pass clean.
- [ ] Update the stale `# excluded: PROJ-301-304` prose comment (`:32-36`) to reflect that
      strategy generation is now guarded (PROJ-473).
- [ ] Verify: guard passes and would catch a new unseeded `random.*` in the generation
      modules.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] FULL suite green: `python Tools/test_sharded/test_sharded.py`
- [ ] Task 0.1 full-save-visible equivalence test green (the real determinism proof);
      global-state-unchanged assertion green (coarse tripwire only — see Task 3.2 note)
- [ ] No `random.seed(...)` in `game_initializer.py` or `galaxy_mode.py`
- [ ] Pattern #18 guard covers `game/strategy` generation modules
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to mark project ready for audit
