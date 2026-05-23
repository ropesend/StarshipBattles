# PROJ-473 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Conflict map (which phase touches which file)

Phases are sequential (0 → 1 → 2 → 3); there is no intra-project parallelism planned, so
the only "conflicts" are files touched by more than one phase (noted in the rightmost
column). A file touched in an earlier phase and again later must be re-validated by the
later phase's reproducibility run.

| File | P0 | P1 | P2 | P3 | Type | Notes |
|------|----|----|----|----|------|-------|
| `game/strategy/engine/game_initializer.py` | ✎ | | ✎ | ✎ | Production | P0: build placement rng + dedicated `physics_rng` / pass into name+system path. **P2: pass the CONTINUED `physics_rng` (NOT a fresh warp rng) into `Galaxy.generate_warp_lanes(...)` (`:271`) — Task 2.2; S9 warp geometry already continues the module stream today so it must continue `physics_rng` (sign-off Blocker 1).** P3: delete `random.seed(galaxy_seed)` (`:250`, ST-04-010). **Multi-phase.** |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | ✎ | | ✎ | ✎ | Production | P0: seeded streams (placement + physics_rng). **P2: pass the CONTINUED `physics_rng` (NOT a fresh warp rng) into `generate_warp_lanes(...)` (`:287`) — Task 2.2.** P3: delete `random.seed(self.galaxy_seed)` (`:239`, ST-04-011). **Multi-phase.** |
| `game/strategy/data/galaxy.py` | ✎ | | ✎ | ✎ | Production | P0: registry construction order / rng for `NameRegistry`; thread physics_rng through `generate_systems`. P2: add `rng` param to the `generate_warp_lanes` facade (`:256-266`) + forward it. P3: add optional normalizing `rng` to `generate_planets` facade (`:212-214`) for uniform backward-compatible contract. **Multi-phase.** |
| `game/strategy/data/naming.py` | ✎ | | | | Production | P0: seed the load-time `random.shuffle` (`:42`) — constructor-inject rng or deferred seeded shuffle. |
| `game/strategy/data/galaxy_system_generator.py` | | ✎ | | | Production | P1: thread rng into `generate_system_stars`/`generate_system_bodies` calls (`:193`, `:71`); preserve the existing distinct sub-streams (`:158-169`). |
| `game/strategy/generation/star_generator.py` | | ✎ | | | Production | P1: 26 bare `random.*` → `rng.*` (physics_rng); `_get_image_id` forwards a SEPARATE seeded `image_rng` (child of physics_rng) to the registry — NOT physics_rng directly (else S9 geometry shifts off the golden baseline; design.md H7 S6/S7). |
| `game/strategy/data/planet_gen.py` | | ✎ | | | Production | P1: thread physics_rng through `generate_system_bodies` → orbital slots, moons, mass, `_create_single_planet`; forward the separate `image_rng` (not physics_rng) to the image registry. |
| `game/strategy/data/planet_gen_surface.py` | | ✎ | | | Production | P1: per-call rng on `generate_surface_flags`, `determine_planet_type`, `generate_resources`. |
| `game/strategy/data/planet_physics.py` | | ✎ | | | Production | P1: per-call rng on `calculate_radius_density_from_mass`. |
| `game/strategy/data/planet_atmosphere.py` | | ✎ | | | Production | P1: per-call rng on `generate_atmosphere` → `_calculate_base_pressure`, `_distribute_gas_composition`. |
| `game/strategy/generation/star_image_registry.py` | | ✎ | | | Production | P1: callers forward rng (signature already accepts it); no logic change expected. |
| `game/strategy/generation/planet_image_registry.py` | | ✎ | | | Production | P1: callers forward rng (signature already accepts it); no logic change expected. |
| `game/strategy/generation/storm_generator.py` | | (read) | | | Production | Already fully rng-threaded — **no change**. Included in snapshot + regression guard only. |
| `game/strategy/data/galaxy_warp_generator.py` | | | ✎ | | Production | P2: thread the CONTINUED `physics_rng` through `_calculate_warp_distance` (`:47`, S9 geometry — already seeded, preserve byte-for-byte), `_should_add_density_edge` (`:273`, S9 geometry), `create_warp_link`; ensure `generate_warp_lanes` rng reaches them + the S10 intrinsics roll (`:351-352`, `:394-420`; replace unseeded `Random()` fallback at `:408-409`). No fresh warp rng (sign-off Blocker 1). |
| `game/strategy/generation/placement_strategies.py` | | | | ✎ | Production | P3: normalize `if rng is None: rng = random.Random()` (`:90-91`, `:163-164`) once callers/tests pass explicit rng. |
| `tests/unit/quality/test_no_unseeded_random.py` | | | | ✎ | Test | P3: ADD `game/strategy/generation` + `game/strategy/data` to `GUARDED_DIRECTORIES` (`:37`). |
| `tests/fixtures/strategy/galaxy_repro_golden_*.json` (new) + capture helper | ✎ | (read) | (read) | (read) | Test fixture | **P0 Task 0.0:** GOLDEN BASELINE of the class-(a) already-seeded outputs (placement/star/planet physics, **S9 warp geometry**, storms, intrinsics, archetype) captured from the CURRENT pre-change code. Immutable reference compared against after every phase (Codex sign-off Blocker 2). Does NOT include class-(b) fields (names/images/warp_type/warp intrinsics — unseeded today). |
| `tests/integration/strategy/test_galaxy_reproducibility.py` (new) | ✎ | ✎ | ✎ | ✎ | Test | P0 Task 0.1: GREEN guard asserting class-(a) fields (incl. S9 geometry) == the Task 0.0 GOLDEN BASELINE (not two-run same-impl) + full-save-visible **expected-RED (xfail)** two-run determinism test for the class-(b) currently-unseeded fields. xfail tolerance narrows each phase: P0 drops `name`, P1 drops `image_id`/`image_rotation`, P2 drops `xfail` entirely (S10 `warp_type`/intrinsics now deterministic → strict pass), P3 keeps it green. Class-(a)/S9 stays golden-guarded every phase. |
| `tests/unit/strategy/data/test_planet_gen.py` | | | | ✎ | Test | P3: stop seeding module-level `random` (`:42-45`); pass explicit rng. |
| `tests/integration/strategy/test_planet_gen.py` | | | | ✎ | Test | P3: pass explicit rng to `generate_systems` (`:17-18`). |
| `tests/integration/strategy/test_galaxy_gen.py` | | | | ✎ | Test | P3: pass explicit rng to `generate_systems`. |
| `tests/unit/strategy/generation/test_placement_strategies.py` | | | | ✎ | Test | P3: pass explicit rng to `sample_location` (`:44-45`). |
| `tests/unit/strategy/data/test_galaxy_system_generator.py` | | | | ✎ | Test | P3: reconcile the `rng=None` shape test (`:544-549`) with the normalized contract. |

Legend: ✎ = file edited in that phase; (read) = read-only / snapshot inclusion;
(green) = expected to remain green without edit.

## Out of scope (not in this manifest)
`game/strategy/generation/density/density_map.py`, `loaders/system_blueprints_loader.py`,
`systems/race_randomizer.py`, `engine/minefield_resolver.py` — off the new-game galaxy
path; separate cleanup candidates.
