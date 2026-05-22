# Phase 0: Root-RNG boundary + name shuffle (+ baseline reproducibility test)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-473 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Goal mapping:** All tasks here serve **G0** (root-RNG boundary + names in the seeded
stream + the baseline reproducibility anchor).
**Objective:** Establish the seeded streams at each composition root (per design.md H7:
placement rng + dedicated `physics_rng`, both seeded with `galaxy_seed` but kept distinct —
**NOT** one consolidated root; warps continue `physics_rng` in Phase 2, no separate warp
rng), bring the load-time `NameRegistry` shuffle into the seeded stream, and land the
reproducibility anchors: **(0.0) capture a GOLDEN BASELINE of the class-(a) already-seeded
outputs from the CURRENT pre-change code**, (0.1a) a GREEN guard asserting class-(a) fields
(incl. S9 warp geometry) equal that golden baseline, and (0.1b) the full-save-visible
end-to-end determinism test authored **expected-RED** for the class-(b) currently-unseeded
fields (it cannot be green on baseline; it turns green only after Phases 0–2). See
decisions.md "Output contract split" for the authoritative class (a)/(b) field lists.
**Determinism is sacred** — these tests gate every later phase.

---

## Tasks

### Task 0.0: Capture the GOLDEN BASELINE of class-(a) already-seeded outputs from CURRENT code [Medium]
**Files:** new fixture under `tests/fixtures/strategy/` (e.g.
`galaxy_repro_golden_<seed>.json`) + a small capture helper/script (kept under the test tree
or `tests/fixtures/strategy/`).
**Why this is a SEPARATE task and must run FIRST (Codex sign-off Blocker 2):** the previous
Phase 0 / Phase 2 tests were two-run SAME-implementation determinism checks. They prove the
NEW code is reproducible but NOT that it produces the SAME galaxy as the CURRENT code — a
deterministic-but-sequence-shifting rewrite would pass them while silently changing output.
The only thing that catches that is comparing post-change output against a snapshot captured
from the CURRENT (pre-change) code. So capture that snapshot BEFORE any threading work
begins.
**Test that must fail first / be authored first:** N/A for the capture itself (it produces a
fixture); the consuming assertions live in Task 0.1.

- [x] Run `GameInitializer.initialize(config)` on the UNCHANGED baseline with one or more
      fixed `GameConfig`s (at least: a multi-system config, e.g.
      `galaxy_seed=42, system_count=5, galaxy_radius=500`; AND the N=1-multi-empire
      retry-triggering config from Task 0.1) and snapshot ONLY the **class-(a)** already-
      seeded fields (decisions.md "Output contract split"): per-system `global_location`,
      `region_id`, `archetype`, system `intrinsic_abilities`; per-warp-point `location` keyed
      by `destination_id` (**S9 warp GEOMETRY** — already reproducible today,
      `warp_geometry_equal=True`); per-star physics (`mass`, `radius_hexes`, `temperature`,
      `luminosity`, `spectrum`, `star_type`, `color`, `age`) + star `intrinsic_abilities`;
      per-planet physics (`orbit_distance`, `mass`, `radius`, `surface_area`, `density`,
      `surface_gravity`, `surface_pressure`, `surface_temperature`, `atmosphere`,
      `planet_type`, `surface_water`, `tectonic_activity`, `magnetic_field`, `deposits`) +
      planet `intrinsic_abilities`; storms.
- [x] **Exclude the class-(b) fields** from the golden fixture: system `name`, star/planet
      `image_id` + `image_rotation`, warp `warp_type`, warp `intrinsic_abilities` — these are
      unseeded today and would differ run-to-run, so they CANNOT be golden-pinned. (Note: key
      warp geometry by `destination_id`, not by warp-point list index, so name/type drift
      does not perturb the geometry comparison.)
- [x] Store the snapshot as a committed fixture and document the exact config(s) + the field
      list inline in the fixture or its capture helper. This fixture is the immutable "what
      current code generates" reference for class (a).
- [x] Verify: the fixture is captured against the UNCHANGED baseline (no production edits yet)
      and is stable across two captures (sanity check that the class-(a) fields are indeed
      reproducible today, including S9 warp geometry).

### Task 0.1: Reproducibility test anchors — golden-baseline guard (class a) + full-snapshot expected-RED (class b) [Medium]
**Files:** new `tests/integration/strategy/test_galaxy_reproducibility.py`
**Symbol/area:** snapshot anchored on `[sys.to_dict() for sys in galaxy.systems.values()]`
(`game/strategy/data/star_system.py:99-115` already serializes the full nested tree:
stars, planets, warp_points, storms, region_id, archetype, intrinsic_abilities).
**Test that must fail first / be authored first:** the new test itself.
**Run:** `pytest tests/integration/strategy/test_galaxy_reproducibility.py -q`; then
`pytest tests/ --testmon`.

> **CRITICAL — the full snapshot is NOT green on baseline (class-(b) fields only).** Per
> design.md **H7**, the class-(b) fields — names (S8), star/planet `image_id`/`image_rotation`
> (S6/S7), and `warp_type`/warp `intrinsic_abilities` (**S10 only**) — are drawn from
> UNSEEDED streams today, so they differ across two same-seed `initialize()` runs. **Warp
> GEOMETRY (S9: warp-point `location`) is NOT in this set — it is already seeded today and
> is golden-baseline guarded (class (a)).** Verified by a read-only runtime check (review.md
> §1, §3): two `initialize(GameConfig(galaxy_seed=42, system_count=5, galaxy_radius=500))`
> runs produced different system names, star `image_id`s, and warp `warp_type`s, but
> IDENTICAL warp geometry (`warp_geometry_equal=True`). The full-save-visible equality test
> is therefore an **expected-RED** characterization for the class-(b) fields that only turns
> green after Phases 0–2 land. Do NOT try to make it green in Phase 0 and do NOT weaken it.

- [x] **GREEN golden-baseline guard (class-(a) already-seeded fields).** Run
      `GameInitializer.initialize(config)` (the SAME config(s) used to capture the golden
      baseline in Task 0.0) and assert deep equality of the class-(a) fields **against the
      Task 0.0 GOLDEN BASELINE fixture** — NOT merely two same-impl runs (a two-run check
      would pass a deterministic-but-sequence-shifting rewrite; only the golden comparison
      catches output drift — Codex sign-off Blocker 2). Class-(a) fields (H7 S1/S2/S3/S4/S5
      **+ S9**): per-system `global_location`, `region_id`, `archetype`, system
      `intrinsic_abilities`; **per-warp-point `location` keyed by `destination_id` (S9 warp
      GEOMETRY)**; per-star physics (`mass`, `radius_hexes`, `temperature`, `luminosity`,
      `spectrum`, `star_type`, `color`, `age`) + star `intrinsic_abilities`; per-planet
      physics (`orbit_distance`, `mass`, `radius`, `surface_area`, `density`,
      `surface_gravity`, `surface_pressure`, `surface_temperature`, `atmosphere`,
      `planet_type`, `surface_water`, `tectonic_activity`, `magnetic_field`, `deposits`) +
      planet `intrinsic_abilities`; and storms. These MUST equal the golden baseline on the
      unchanged code now and after EVERY phase — that is the contract the threading work must
      preserve. (Do NOT include the class-(b) fields `name`, `image_id`, `image_rotation`,
      `warp_type`, or warp `intrinsic_abilities` in THIS guard — they are unseeded today and
      are NOT golden-pinned.)
- [x] **Expected-RED full-snapshot determinism test (class-(b) fields).** Author a deep-
      equality test across TWO same-seed runs of the CURRENT code on the COMPLETE `to_dict()`
      snapshot — this is what is RED on baseline, because the class-(b) fields (`name`,
      `image_id`, `image_rotation`, `warp_type`, warp `intrinsic_abilities`) are unseeded
      today and differ run-to-run. Mark it `@pytest.mark.xfail(reason="PROJ-473 expected-RED
      until Phases 0–2 make names/images/warp-type+intrinsics deterministic", strict=True)`
      with a clear comment pointing at design.md H7. **Scope note (Codex sign-off Blocker 2):**
      the class-(a) already-seeded fields — including **S9 warp-point `location` geometry** —
      are NOT what makes this test RED; they are guarded by the Task 0.0 golden baseline from
      the start. This xfail concerns ONLY the class-(b) fields becoming deterministic. The
      snapshot itself MUST still include the full tree (per decisions.md "FULL save-visible
      equivalence"): per-system `name`, `global_location`, `region_id`, `archetype`,
      `intrinsic_abilities`, warp points (`destination_id`/`location`/`warp_type`/
      `intrinsic_abilities`); per-star `name`, `mass`, `radius_hexes`, `temperature`,
      `luminosity`, `spectrum`, `star_type`, `color`, `age`, `location`, `image_id`,
      `intrinsic_abilities`; per-planet `name`, `location`, `orbit_distance`, `mass`,
      `radius`, `surface_area`, `density`, `surface_gravity`, `surface_pressure`,
      `surface_temperature`, `atmosphere`, `planet_type`, `surface_water`,
      `tectonic_activity`, `magnetic_field`, `deposits`, `image_id`, `image_rotation`,
      `intrinsic_abilities`; and storms. As each phase makes the corresponding class-(b)
      field deterministic, remove it from the xfail tolerance (P0: `name`; P1: `image_id`/
      `image_rotation`; P2: `warp_type` + warp `intrinsic_abilities` [S10]); when Phase 2
      completes, drop `xfail` and the test must pass strictly as a two-run determinism check.
      (The class-(a)/S9 fields are simultaneously asserted against the golden baseline by the
      guard above, every phase.)
- [x] **Do NOT** reuse the golden-save image skiplist (`_build_galaxy_fixture.py:53-59`):
      `image_id`/`image_rotation` are part of the full equality (after P1), not normalized
      away.
- [x] **N=1 retry case — must actually trigger a retry (hazard H2).** A bare "N=1 with ≥2
      empires" config does NOT guarantee the seed-bump branch runs (retry only fires when
      `len(lone.planets) < num_empires`, `game_initializer.py:333`; seed bumped via
      `replace(config, galaxy_seed=config.galaxy_seed + attempt)`, `:86-91`). Either (a)
      pick a `galaxy_seed`/`system_count=1`/empire-count combo KNOWN to force at least one
      retry and pin it, OR (b) instrument the run (e.g. capture the planet-shortage log at
      `game_initializer.py:118-121`, or assert via a spy on the retry path) and assert that
      `attempt > 0` was reached. A draw-count shift that flips retry outcome must be caught,
      not masked by a config that succeeds on attempt 0 in both runs. Capture this config's
      class-(a) output in the Task 0.0 golden baseline too, and assert the golden-baseline
      guard against it (physics + S9 geometry) so a retry-flipping draw shift is a real
      baseline regression; extend it into the full snapshot's class-(b) determinism checks as
      those fields go green.
- [x] **Global-state companion assertion (necessary but NOT sufficient — see note below).**
      Snapshot `random.getstate()` before and after `initialize()` and assert generation
      perturbs global `random` state today (this assertion FLIPS in Phase 3). **Caveat:**
      this is a weak proxy. Fresh unseeded `random.Random()` fallbacks (S6/S7/S10 at
      `star_image_registry.py:81-82`, `planet_image_registry.py:76-77`/`:107-108`,
      `galaxy_warp_generator.py:408-409`) do NOT touch module-level state, so this assertion
      can pass while determinism is still broken. The REAL proof of determinism is the
      full-save-visible equivalence test going green — not `getstate()`. Treat `getstate()`
      only as a coarse "did the global seed get removed" tripwire for Phase 3.
- [x] Verify: **the golden-baseline guard passes on the unchanged baseline** (class-(a)
      fields incl. S9 warp geometry equal the Task 0.0 golden fixture, incl. the N=1 retry
      case); the full-snapshot class-(b) determinism test is **xfail (expected-RED)** on
      baseline; the global-perturbation assertion passes (debt present). Record the baseline
      state in Current State.

### Task 0.2: Seed the load-time name shuffle (NameRegistry) [Medium]
**File:** `game/strategy/data/naming.py` (and `game/strategy/data/galaxy.py:44` ctor site)
**Symbol/area:** `NameRegistry.load_data` → `random.shuffle(self.available_names)`
(`naming.py:42`); construction in `Galaxy.__init__` (`galaxy.py:44`).
**Test that must fail first:** add a focused unit test in
`tests/unit/strategy/data/test_naming.py` asserting that two `NameRegistry` instances
built with the SAME injected `random.Random(seed)` produce the same `available_names`
order (fails before threading because the shuffle uses module-level `random`).
**Run:** `pytest tests/ -k naming`; then `pytest tests/ --testmon`.

- [x] Constructor-inject `rng: random.Random | None` into `NameRegistry` (or add a
      deferred seeded shuffle step) so the shuffle draws from the seeded stream rather than
      bare `random.shuffle`. Per consult §2, constructor injection is the cleaner fit since
      the random op happens at load time, not at `get_system_name()`.
- [x] Resolve the ordering hazard (H1): the rng must exist when `NameRegistry` shuffles.
      Either (a) `Galaxy.__init__` accepts/builds the rng before constructing the registry,
      or (b) the shuffle is deferred to a post-seed call invoked from the composition root.
      Document the chosen shape in a code comment + note in Current State.
- [x] Verify: the new naming determinism test passes; Task 0.1 baseline equality still
      passes.

### Task 0.3: Establish the seeded root rng at both composition roots [Medium]
**Files:** `game/strategy/engine/game_initializer.py`, `game/ui/screens/galaxy_test/galaxy_mode.py`,
`game/strategy/data/galaxy.py`
**Symbol/area:** `_initialize_galaxy` already builds the placement `rng =
random.Random(galaxy_seed)` (`game_initializer.py:248`) and `galaxy_mode.generate` builds
one (`:261` area); the gap is that names + star/planet physics + warps don't receive a
seeded stream yet. Per design.md H7, do NOT route physics through the placement rng (it has
already had two `randint` draws pulled for storm/intrinsic streams at
`galaxy_system_generator.py:163-164`). Establish, alongside the placement rng, a dedicated
`physics_rng = random.Random(galaxy_seed)` (separate instance, same seed) reserved for the
Phase 1 star/planet pipeline, and wire the seeded name shuffle (Task 0.2). Leave a comment
documenting that Phase 2 will CONTINUE this same `physics_rng` into warp geometry (S9) and
warp type/intrinsics (S10) — NOT a fresh warp rng (sign-off Blocker 1).
**Test that must fail first:** extend the Task 0.1 test (or add a sibling) asserting that
the name order in the generated galaxy is reproducible for a fixed seed — fails until the
root rng feeds the registry.
**Run:** `pytest tests/ -k "game_initializer or galaxy_mode or naming"`; then
`pytest tests/ --testmon`.

- [x] In `game_initializer._initialize_galaxy`, ensure the seeded stream is the source for
      the name shuffle (via the Task 0.2 mechanism), and construct the dedicated
      `physics_rng = random.Random(galaxy_seed)` (separate from the placement rng) reserved
      for Phase 1 — **do not** delete `random.seed(galaxy_seed)` yet (that is Phase 3;
      star/planet/warp still read global until their phases land).
- [x] Mirror the same wiring in `galaxy_mode.generate` (`:226-289`).
- [x] Keep the `Galaxy` facade signature changes minimal and forward-compatible with the
      Phase 1/2 rng-threading (note the intended `generate_systems` physics-rng flow and that
      `generate_warp_lanes` will receive the SAME continued `physics_rng` in P2 — not a fresh
      warp rng — in a comment so later phases slot in cleanly).
- [x] Verify: name-order reproducibility holds for a fixed seed (the `name` portion of the
      full-snapshot class-(b) xfail test should now PASS — narrow the xfail tolerance to drop
      `name`); the golden-baseline guard (class-(a), incl. S9 geometry) still passes; no
      global `random.seed` removed yet.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Task 0.0 golden baseline fixture captured from the unchanged code and committed
- [x] `pytest tests/ --testmon` green; Task 0.1 golden-baseline guard passes (class-(a) incl.
      S9 geometry == golden fixture); the full-snapshot class-(b) test is still xfail BUT
      names are now reproducible (its `name`-field tolerance dropped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
