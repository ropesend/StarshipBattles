# Phase 1: Per-system star + planet pipeline + image registries

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-473 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 0 (root rng + names seeded; Task 0.1 baseline test green)
**Goal mapping:** All tasks serve **G1** (per-system star + planet generation draws from
the seeded rng, incl. the image registries).
**Objective:** Thread the seeded `rng` through `StarGenerator.generate_system_stars`,
`PlanetGenerator.generate_system_bodies` and its leaf helpers, and forward `rng` into the
star/planet image registries — preserving exact draw order (hazard H5). Use the dedicated
`physics_rng` (design.md H7 S4/S5), NOT the placement rng. The Task 0.1 GREEN guard —
class-(a) fields (incl. S9 warp geometry) asserted against the Task 0.0 GOLDEN BASELINE —
must stay green (byte-for-byte equal to current code) throughout; the full-snapshot
expected-RED class-(b) determinism test should shed its `image_id`/`image_rotation`
tolerance this phase (names already shed in P0; S10 warp type/intrinsics shed in P2).

---

## Tasks

### Task 1.1: Thread `rng` through the per-system orchestration loop [Medium]
**File:** `game/strategy/data/galaxy_system_generator.py`
**Symbol/area:** `generate_systems` (`:104-215`) — the per-system loop at `:171-209`
calls `self._star_gen.generate_system_stars(name)` (`:193`) and
`self.generate_planets(galaxy, sys, rng=intrinsic_rng)` (`:197`). Today stars + planet
*physics* get NO rng (only intrinsic-ability rolls get the derived `intrinsic_rng`); they
draw from the module-level `random` separately seeded via `random.seed(galaxy_seed)` at
`game_initializer.py:250` (design.md H7 S4/S5). Thread the dedicated `physics_rng` here.
**Test that must fail first:** add a unit test asserting `generate_systems` with a fixed
seeded rng produces identical star masses/types + planet masses across two runs (fails
until physics is threaded — currently physics draws from global).
**Run:** `pytest tests/unit/strategy/data/test_galaxy_system_generator.py -q`; then
`pytest tests/ --testmon`.

> **STREAM-IDENTITY CONTRACT (design.md H7 — NOT a free choice).** The physics rng MUST be
> the dedicated `physics_rng = random.Random(galaxy_seed)` instance built at the
> composition root (Phase 0 Task 0.3), passed DOWN into `generate_systems`. **Do NOT**
> derive it from the placement `rng`, and **do NOT** reuse the placement `rng` directly:
> the placement rng has already had two `randint` draws pulled at `:163-164` (to seed
> `storm_rng` and `intrinsic_rng`), so deriving/reusing it would change the sequence stars
> and planet physics see and break equivalence. The four streams — placement `rng` (S1),
> `storm_rng` (S2), `intrinsic_rng` (S3), and the new `physics_rng` (S4+S5) — stay
> **distinct**. `physics_rng` reproduces the sequence the global `random.seed(galaxy_seed)`
> produced ONLY because it is seeded with the same `galaxy_seed` and is consumed in the
> same star-then-planet order; preserve that order exactly (hazard H5).

- [ ] Accept the dedicated `physics_rng` parameter in `generate_systems` (passed from the
      composition root; do NOT construct it here, and do NOT derive it from the placement
      `rng`). Keep placement `rng`, `physics_rng`, `intrinsic_rng`, and `storm_rng` as
      **distinct streams** so adding/removing one stream's draws never shifts another (H5).
- [ ] Forward `physics_rng` (one shared instance, star-then-planet order) into
      `generate_system_stars(...)` first, then `generate_system_bodies(...)` (signatures
      extended in Tasks 1.2/1.3). Do NOT split physics into two separate instances.
- [ ] Verify: the new system-generator physics determinism test passes; the Task 0.1 narrow
      GREEN guard stays green; the full-snapshot xfail test now has its image fields
      reproducible (narrow its tolerance — see Tasks 1.2/1.3).

### Task 1.2: Thread `rng` through `StarGenerator` (26 bare draws) [Complex]
**File:** `game/strategy/generation/star_generator.py`
**Symbol/area:** `generate_system_stars` (`:282`) → `_generate_random_stars` (`:410`) /
`generate_from_blueprint` (`:340`); the draw sites are `_generate_mass` (`:69`, `:83`),
`_determine_type_and_radius` (`:109-142`), `_compute_stefan_boltzmann_type`
(`:168-186`), `_roll_star_type` (`:200`), `_generate_spectrum` jitter (`:268`),
`_generate_companions` (`:309`, `:315`, `:319`), age (`:393`, `:440`),
`_generate_mass_constrained` (`:466`, `:471`). Also `_get_image_id` (`:51-58`).
**Test that must fail first:** `pytest tests/ -k star_generator` — add a test that
`generate_system_stars(name, rng=Random(seed))` is identical across two runs incl.
`image_id` (fails until rng threaded + image rng forwarded).
**Run:** `pytest tests/ -k star_generator`; then `pytest tests/ --testmon`.

- [ ] Add a per-call `rng: random.Random` to `generate_system_stars` and thread it down
      through every helper that draws (`_generate_mass`, `_determine_type_and_radius`,
      `_compute_stefan_boltzmann_type`, `_roll_star_type`, `_generate_spectrum`,
      `_generate_companions`, `_generate_mass_constrained`). Replace each bare `random.*`
      with `rng.*`, preserving exact call order (hazard H5).
- [ ] Make `_get_image_id` accept and forward an image rng to
      `StarImageRegistry.get_random_image(star_type, rng=...)` (`:58`). **DRAW-ORDER HAZARD
      (design.md H7 S6/S7):** images are on a fresh unseeded `Random()` today, so they are
      NOT in the module/physics stream. Forwarding `physics_rng` itself would insert image
      draws into the physics sequence and shift S9 warp geometry off its golden baseline.
      Use a SEPARATE seeded image stream (a child `image_rng` derived once from `physics_rng`
      up front, mirroring how storms/intrinsics derive from the placement rng) so the
      physics sequence — and S9 — is untouched. Confirm the golden-baseline guard (incl. S9)
      stays green after this change.
- [ ] Verify: star-generation determinism test (incl. `image_id`) passes; the Task 0.1
      golden-baseline guard stays green (class-(a) incl. S9 geometry unchanged); star
      `image_id` is now reproducible in the full snapshot (narrow the xfail tolerance to drop
      star `image_id`).

### Task 1.3: Thread `rng` through planet generation + leaf helpers [Complex]
**Files:** `game/strategy/data/planet_gen.py`, `planet_gen_surface.py`,
`planet_physics.py`, `planet_atmosphere.py`
**Symbol/area:**
- `planet_gen.py`: `generate_system_bodies` (`:44`) → `_generate_orbital_slots`
  (`:121`, `:123`, `:132`, `:156`, `:160`, `:165`, `:170`, `:176`), `_generate_mass_constrained`
  (`:235`, `:240`), `_generate_moons` (`:266`), `_generate_moon_mass` (`:327`),
  `_create_single_planet` (`:397-398` image registry calls).
- `planet_physics.py`: `calculate_radius_density_from_mass` (`:60`, `:62`, `:64`).
- `planet_atmosphere.py`: `generate_atmosphere` → `_calculate_base_pressure` (`:91`),
  `_distribute_gas_composition` (`:125`, `:138`).
- `planet_gen_surface.py`: `generate_surface_flags` (`:55-65`), `determine_planet_type`
  (`:101`), `generate_resources` (`:199`, `:217`).
**Test that must fail first:** `pytest tests/ -k planet` — add a test that
`generate_system_bodies(name, stars, rng=Random(seed))` is identical across two runs incl.
`image_id`/`image_rotation`, `deposits`, `atmosphere` (fails until threaded).
**Run:** `pytest tests/ -k "planet or atmosphere"`; then `pytest tests/ --testmon`.

- [ ] Add a per-call `rng` to `generate_system_bodies` and thread it through orbital
      slots, moons, mass, `_create_single_planet`, and the four leaf helpers (which are
      module-level free functions → per-call `rng` parameter, per consult §2). Replace bare
      `random.*` with `rng.*`, preserving order (hazards H5; moon `while` loop and
      atmosphere gas loop are data-dependent — do not reorder).
- [ ] In `_create_single_planet`, forward the **separate seeded image stream** (the same
      `image_rng` introduced in Task 1.2 — NOT `physics_rng` directly) to
      `PlanetImageRegistry.get_random_image(p_type, rng=...)` (`:397`) and
      `get_random_rotation(rng=...)` (`:398`). Putting planet image/rotation draws on
      `physics_rng` would shift the physics sequence and break S9's golden baseline
      (design.md H7 S6/S7 draw-order hazard).
- [ ] Verify: planet-generation determinism test (incl. image fields, deposits,
      atmosphere) passes; the Task 0.1 narrow GREEN guard stays green; planet `image_id`/
      `image_rotation` are now reproducible in the full snapshot (narrow the xfail tolerance
      so that after Task 1.2+1.3 all image fields are dropped from the xfail set).

### Task 1.4: Confirm image registries + storm generator deterministic on the seeded path [Simple]
**Files:** `game/strategy/generation/star_image_registry.py`,
`planet_image_registry.py`, `storm_generator.py`
**Symbol/area:** registries already accept `rng` (`star_image_registry.py:70`,
`planet_image_registry.py:65`, `:98`); `storm_generator.py` already uses the passed `rng`
for every draw. No production logic change expected — this task is a guard.
**Test that must fail first:** N/A as a new production failure — instead add/extend a test
asserting that with a fixed seeded rng the image basenames + rotations + storm fields are
stable across runs (should already pass for storms; passes for images once Tasks 1.2/1.3
forward rng).
**Run:** `pytest tests/ -k "image_registry or storm"`; then `pytest tests/ --testmon`.

- [ ] Confirm no bare `random.*` remains *reachable from the seeded generation path* in the
      two image registries (the `if rng is None: rng = random.Random()` fallbacks are
      normalized in Phase 3; here just confirm the seeded path forwards rng).
- [ ] Confirm `storm_generator.py` needs **no change** (already rng-threaded); leave as-is.
- [ ] Verify: image + storm determinism tests pass; the Task 0.1 narrow GREEN guard stays
      green; with names (P0) + images (P1) now reproducible, the full-snapshot xfail test
      should fail ONLY on warp fields (`warp_type`, warp `intrinsic_abilities`) — those drop
      in Phase 2.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` green; Task 0.1 golden-baseline guard still green (class-(a)
      incl. S9 geometry == golden fixture); full-snapshot xfail test now fails only on the
      S10 warp type/intrinsic fields (names + images now reproducible)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
