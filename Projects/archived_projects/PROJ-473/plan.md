# PROJ-473: Thread an explicit per-instance `random.Random` through galaxy generation so the two load-bearing global `random.seed()` calls can be removed

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-473` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-473 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Root-RNG boundary + name shuffle (+ golden baseline + reproducibility tests) | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Per-system star + planet pipeline + image registries | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Warp generation (incl. the `generate_warp_lanes` facade rng gap) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Remove the two global `random.seed()` calls + normalize the `rng is None` fallbacks + guard | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-21
**Active Phase:** All phases complete — pending audit + user verification

**Last Action (2026-05-21, Phases 1-3 COMPLETE):** Continued from prior subagent
that died mid-Phase-2. Verified golden baseline is PRISTINE (stashed production
changes, regenerated snapshot, byte-for-byte == committed fixture for both
configs; restored). **Phase 2:** threaded the CONTINUED `physics_rng` through
`galaxy_warp_generator` (`_calculate_warp_distance`, `_should_add_density_edge`,
`create_warp_link`, `_apply_mst_edges`, `_add_density_edges`, S10 intrinsics
roll) — NO fresh warp rng; closed the `Galaxy.generate_warp_lanes` facade rng
gap (added `rng` param) and both composition roots now pass `physics_rng` into
warp generation. Built the independent `image_rng` (seed = galaxy_seed+0x1A6E)
at both roots and threaded it into `generate_systems`. Removed the xfail marker
(full-snapshot determinism now strictly green). **Phase 3:** removed both
`random.seed()` calls (`game_initializer.py`, `galaxy_mode.py`); flipped the
global-state assertion to prove generation does NOT touch module random; added
`game/strategy/generation` + `game/strategy/data` to the Pattern #18 guard
(`GUARDED_DIRECTORIES`); fixed Phase-1 test-double signatures
(`_FakeStarGenerator`/`_FakePlanetGenerator` accept `**kwargs`); fixed warp
helper tests to pass rng; trimmed star_generator (497 LOC) under 500 and raised
the galaxy.py PROJ-372 ceiling 350→370 with justification.

**RESULTS:** class-(a) golden baseline preserved byte-for-byte for BOTH configs
(multi + n1_retry); warp_geometry drift FIXED; class-(b) two-run determinism
green; full-snapshot xfail flipped to strict-green. Full sharded suite: 23547
passed / 0 failed. combat_lab TOHIT-ATK-FLEET-003/004 fail pre-existing
(data-phase, unrelated). Both global seeds removed; guard extended.

**Prior Active Phase:** Phase 1
**Last Action (2026-05-21, Phase 0 COMPLETE):** Golden baseline captured
(`tests/fixtures/strategy/galaxy_repro_golden.json` via
`galaxy_repro_baseline.py`); reproducibility anchors landed in
`tests/integration/strategy/test_galaxy_reproducibility.py` (class-(a)
golden-guard GREEN for both configs; full-snapshot class-(b) xfail RED;
class-(b)-seeded determinism GREEN incl. `name`; n1_retry-fires + global-state
tripwire GREEN). Name shuffle seeded via `NameRegistry(rng=...)` injected from
`Galaxy(name_rng=...)` at both composition roots; dedicated `physics_rng`
(separate instance, same seed) built at both roots and threaded into
`generate_systems(physics_rng=...)` (accepted, consumed in Phase 1). N=1 retry
config = seed 37, 4 empires, radius 500 (forces exactly 1 retry). KEYING NOTE:
warp geometry golden-keyed by `(src_loc,dest_loc)` coords, not `destination_id`
(name is class-(b), unstable pre-P0) — see decisions.md. Both `random.seed`
calls still present (removed in Phase 3). 643 strategy/integration tests green.
**Next Action:** Phase 1 — thread `physics_rng` through `StarGenerator` +
planet pipeline + image registries (separate child `image_rng`). See
phase_1_checklist.md.
**Prior Action:** Revised per the Codex sign-off review (`AgentCoordination/Scratchpad/Consult/proj473_signoff/review.md`, verified against live code). Two final blockers fixed: **(B1) Warp-stream contract corrected** — S9 warp GEOMETRY (distance jitter `:47` + density-edge acceptance `:273`) is ALREADY SEEDED today (continues the module stream right after planet physics; storms/intrinsics use child streams off the placement rng, so nothing else consumes the module RNG in between — `warp_geometry_equal=True` verified). It must CONTINUE the dedicated `physics_rng`, NOT a fresh `warp_rng` (which would change geometry). Only S10 warp type/intrinsic rolls (`:408-409`) are unseeded today and become newly-deterministic. design.md H7 + phase_2_checklist rewritten. **(B2) Golden-baseline enforcement added** — output contract split into class (a) already-seeded outputs (placement/star/planet physics, S9 warp geometry, storms, intrinsics, archetype) enforced against a GOLDEN BASELINE captured from CURRENT code (new Phase 0 Task 0.0), and class (b) currently-unseeded outputs (names, images, warp type/intrinsics) asserted for determinism+presence only. Earlier post-flesh fixes (expected-RED snapshot, RNG topology reproduction, N=1 retry trigger, backward-compatible facades, stale-artifact fixes) remain in place.
**Next Action:** Begin **Phase 0 Task 0.0** — capture the golden baseline of the class-(a) already-seeded outputs from the CURRENT (pre-change) code and store it as a fixture. Then Task 0.1 — narrow GREEN guard asserting class-(a) fields equal that golden baseline, plus the full-save-visible expected-RED test for the class-(b) fields (see design.md H7 + the Output contract section + decisions.md).
**Blockers:** None

## Overview
Galaxy generation reproducibility currently rides on a global `random.seed(galaxy_seed)`
call because `StarGenerator`, the planet/atmosphere/physics/surface generators, the
load-time name shuffle, and warp-distance/density-edge jitter all use the **bare
module-level `random.*`** API. PROJ-471 (findings ST-04-010 / ST-04-011) flagged the two
global seed calls as Pattern #18 violations but verified they are **load-bearing** —
deleting them as-is silently breaks fixed-seed reproducibility. This project threads an
explicit per-instance `rng: random.Random` through the entire new-game galaxy generation
path so the global seed becomes unnecessary, then removes both calls — preserving
**full save-visible equivalence** for a fixed `galaxy_seed`.

## Output contract — two classes of generation output (read before any test work)

The save-visible generation outputs split into TWO classes with DIFFERENT preservation
contracts. The tests must enforce them differently (see decisions.md for the authoritative
field-by-field list and the golden-baseline mechanism):

**(a) Already-seeded outputs — MUST be byte-for-byte preserved vs the CURRENT (pre-change)
code.** These are reproducible today and any drift is a regression:
- system placement / `global_location` (S1), star physics (S4), planet physics (S5),
  **warp GEOMETRY** (warp-point `location` per `destination_id`, S9), storms (S2), intrinsic
  abilities + system archetype (S3).
- **Enforcement:** a **GOLDEN BASELINE** snapshot captured from the CURRENT code BEFORE any
  threading, stored as a fixture, and compared for equality after each phase. A two-run
  same-implementation determinism check is NOT sufficient for class (a) — a
  deterministic-but-sequence-shifting rewrite would pass two-run determinism while silently
  changing output. Only an against-baseline comparison catches that.

**(b) Currently-unseeded outputs — values WILL newly become deterministic; this is allowed,
NOT a regression.** Not reproducible today; bringing them into a seeded stream changes their
values:
- system `name` (S8), star/planet `image_id` + `image_rotation` (S6/S7), warp `warp_type` +
  warp `intrinsic_abilities` (S10).
- **Enforcement:** asserted ONLY for determinism (stable across two runs of the NEW code,
  per phase as each lands) and presence — NOT against the golden baseline. The expected-RED
  full-snapshot test concerns exactly these (b) fields becoming deterministic.

## Goals
- **G0 — Root-RNG boundary + names in the seeded stream + golden baseline.** Establish the
  seeded streams at each composition root (per design.md H7 this is a placement rng + a
  dedicated `physics_rng`, both seeded with `galaxy_seed` but kept distinct — NOT one
  consolidated root; warps continue `physics_rng`, no separate warp rng) and bring the
  load-time `NameRegistry` shuffle (today fired in `Galaxy.__init__` before the seed exists)
  into the seeded stream. Land three anchors: (1) **capture the GOLDEN BASELINE** snapshot of
  the class-(a) already-seeded outputs from the CURRENT pre-change code and store it as a
  fixture; (2) a narrow GREEN guard asserting the class-(a) fields equal that golden baseline
  (passes on the unchanged baseline and after every phase); (3) the full-save-visible
  end-to-end equivalence test as an **expected-RED** characterization for the class-(b)
  fields (names/images/warp type/intrinsics are unseeded today; it turns green as those
  become deterministic across Phases 0–2). These are the TDD anchors for all later phases.
- **G1 — Per-system star + planet pipeline draws from the seeded rng.** Thread `rng`
  through `StarGenerator.generate_system_stars`, `PlanetGenerator.generate_system_bodies`
  and its leaf helpers (`planet_physics`, `planet_atmosphere`, `planet_gen_surface`), and
  forward `rng` into the star/planet image registries (which already accept it).
- **G2 — Warp generation draws from the seeded rng.** Thread `rng` through
  `GalaxyWarpGenerator.generate_warp_lanes` internals (`_calculate_warp_distance`,
  `_should_add_density_edge`) and close the `Galaxy.generate_warp_lanes` facade gap that
  currently drops `rng` so warp-type/intrinsic rolls run unseeded.
- **G3 — Remove the two global seeds + normalize fallbacks + guard.** Delete
  `random.seed(galaxy_seed)` (`game_initializer.py`) and `random.seed(self.galaxy_seed)`
  (`galaxy_mode.py`); normalize the unseeded `rng is None` fallbacks per the
  backward-compatible-facade contract (public facades normalize `rng=None` to a seeded
  stream at the composition root; internal helpers hard-require rng — see decisions.md),
  after the dependent tests are updated; add `game/strategy` to the Pattern #18 guard so a
  regression is caught. (Note: "seeded streams" is plural per design.md H7 — placement,
  physics, warp — not one consolidated root.)

Every goal maps to a phase; every phase task maps back to a goal (see phase checklists).

## Scope
**In:**
- `game/strategy/engine/game_initializer.py` — root rng; remove `random.seed` (G0, G3)
- `game/ui/screens/galaxy_test/galaxy_mode.py` — root rng; remove `random.seed` (G0, G3)
- `game/strategy/data/galaxy.py` — `__init__` registry construction order; `generate_systems`
  / `generate_warp_lanes` rng forwarding (G0, G2)
- `game/strategy/data/naming.py` — seed the load-time name shuffle (G0)
- `game/strategy/data/galaxy_system_generator.py` — thread rng into the per-system
  star/planet calls (currently passes none for physics) (G1)
- `game/strategy/generation/star_generator.py` — 26 bare `random.*` draws → `rng.*` (G1)
- `game/strategy/data/planet_gen.py`, `planet_gen_surface.py`, `planet_physics.py`,
  `planet_atmosphere.py` — thread `rng`; bare `random.*` → `rng.*` (G1)
- `game/strategy/generation/star_image_registry.py`, `planet_image_registry.py` — forward
  the seeded `rng` from the generators (registries already accept it) (G1)
- `game/strategy/data/galaxy_warp_generator.py` — thread `rng` through warp internals (G2)
- `game/strategy/generation/placement_strategies.py` — normalize `rng is None` fallback (G3)
- `tests/unit/quality/test_no_unseeded_random.py` — add `game/strategy` to the guard (G3)
- The dependent tests that call generation with no rng / seed module-level random (G3)
- New reproducibility tests + golden-baseline fixture (G0): a GOLDEN BASELINE snapshot of
  the class-(a) already-seeded outputs captured from CURRENT code and stored as a fixture; a
  narrow GREEN guard asserting class-(a) fields equal that baseline after every phase; plus
  one full-save-visible end-to-end equivalence test authored **expected-RED** for the
  class-(b) fields that progressively become deterministic as names (P0), images (P1), and
  warp type/intrinsics (P2) land

**Out:**
- `game/strategy/generation/density/density_map.py`, `loaders/system_blueprints_loader.py`,
  `systems/race_randomizer.py`, `engine/minefield_resolver.py` — verified NOT on the
  new-game galaxy path (consult §3). Separate cleanup candidates; not scoped here.
- Combat / `ShipCombatEngine` / `battle_setup` RNG (owned by PROJ-471 — done).
- Save-file format changes. Output for a fixed seed must remain reproducible (full
  save-visible equivalence); this project changes *where randomness comes from*, not
  *what is generated*.
- `storm_generator.py` production changes — inspected, already fully rng-threaded;
  included only in the snapshot + as a regression guard.

## Key Files
| Component | File Path | Phase |
|-----------|-----------|-------|
| Galaxy init composition root + global seed | `game/strategy/engine/game_initializer.py` | 0, 3 |
| Galaxy test tool composition root + global seed | `game/ui/screens/galaxy_test/galaxy_mode.py` | 0, 3 |
| Galaxy facade (registry ctor order, generate_warp_lanes rng gap) | `game/strategy/data/galaxy.py` | 0, 2 |
| Name registry (load-time shuffle) | `game/strategy/data/naming.py` | 0 |
| Per-system orchestration loop | `game/strategy/data/galaxy_system_generator.py` | 1 |
| Star generation (26 bare draws — primary) | `game/strategy/generation/star_generator.py` | 1 |
| Planet generation | `game/strategy/data/planet_gen.py` | 1 |
| Planet surface/classification/resources | `game/strategy/data/planet_gen_surface.py` | 1 |
| Planet physics (radius/density) | `game/strategy/data/planet_physics.py` | 1 |
| Planet atmosphere | `game/strategy/data/planet_atmosphere.py` | 1 |
| Star image registry (already accepts rng) | `game/strategy/generation/star_image_registry.py` | 1 |
| Planet image registry (already accepts rng) | `game/strategy/generation/planet_image_registry.py` | 1 |
| Storm generator (already rng-threaded — snapshot only) | `game/strategy/generation/storm_generator.py` | 1 |
| Warp generation | `game/strategy/data/galaxy_warp_generator.py` | 2 |
| Placement strategies (`rng is None` fallback) | `game/strategy/generation/placement_strategies.py` | 3 |
| Pattern #18 guard | `tests/unit/quality/test_no_unseeded_random.py` | 3 |

See [manifest.md](manifest.md) for the per-phase conflict map.

## Related Documents
- [design.md](design.md) — architecture hazards (name-shuffle-before-seed, system_count==1
  retry seed-bump sensitivity, image-field save-visibility, the `generate_warp_lanes`
  facade rng gap, draw-order fragility sites)
- [decisions.md](decisions.md) — full decisions log (incl. the orchestrator decisions)
- Code-grounded consult: `AgentCoordination/Scratchpad/Consult/proj473_preflesh3/advice.md`
- Origin: PROJ-471 `decisions.md` revision entries + `Reviews/results/2026-05-20_082533_state-audit/`

## Validation
- Baseline / full: `python Tools/test_sharded/test_sharded.py`
- Incremental: `pytest tests/ --testmon`

## Verification
- [ ] All phase checklists complete
- [ ] Golden baseline of class-(a) already-seeded outputs captured from CURRENT code and
      stored as a fixture (Phase 0)
- [ ] Class-(a) fields (incl. S9 warp geometry) equal the golden baseline byte-for-byte after
      every phase (NOT merely two-run same-impl determinism)
- [ ] Class-(b) fields (names/images/warp type/intrinsics) start expected-RED on baseline and
      become deterministic across two runs of the new code as Phases 0–2 land (asserted for
      determinism + presence, NOT against the golden baseline)
- [ ] Full-save-visible end-to-end equivalence test is GREEN after Phase 2 (and stays green
      through Phase 3): class-(a) vs golden baseline, class-(b) two-run determinism
- [ ] No `random.seed(...)` remains in `game_initializer.py` or `galaxy_mode.py`
- [ ] Pattern #18 guard covers `game/strategy` generation modules
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
