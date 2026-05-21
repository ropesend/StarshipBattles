# PROJ-473: Thread per-instance RNG through planet/star generation to enable global random.seed removal (deferred from PROJ-471)

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
| 1. Thread `rng` through generation, then remove the two global `random.seed()` calls | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-20 (scope populated from PROJ-471 deferral)
**Active Phase:** Phase 1
**Last Action:** Project scope populated from the PROJ-471 deferral (ST-04-010 / ST-04-011). PROJ-471 verified that the two global `random.seed()` calls are LOAD-BEARING and cannot be removed until generation accepts an explicit `rng`.
**Next Action:** Begin Phase 1 Task 1.1 — thread an explicit `random.Random` through `StarGenerator` and the planet/atmosphere/naming generation modules.
**Blockers:** None

## Overview
Galaxy generation reproducibility currently relies on a global `random.seed(galaxy_seed)`
call because `StarGenerator`, planet/atmosphere/naming generation, and the placement
strategies' `rng is None` fallbacks use the **bare module-level `random.*`** API. PROJ-471
identified the two global `random.seed()` calls (`game/strategy/engine/game_initializer.py`
and `game/ui/screens/galaxy_test/galaxy_mode.py`) as Pattern #18 global-RNG pollution but
verified that deleting them as-is would silently break seed reproducibility — the global
seed is the only thing wiring determinism into the bare-`random` generation code. This
project threads an explicit per-instance `rng` through that generation path so the global
seed becomes unnecessary, then removes both global `random.seed()` calls.

## Goals
- **Phase 1:** Thread an explicit `rng: random.Random` parameter (defaulting safely) through
  `StarGenerator` and the planet/atmosphere/naming/warp generation modules so all generation
  draws come from the seeded instance RNG that `game_initializer.py` already constructs
  (`rng = random.Random(galaxy_seed)`, line 248). Remove the bare-`random` fallbacks and the
  placement-strategy `rng is None: rng = random.Random()` fallbacks on the generation path.
  Then delete the two global `random.seed()` calls. Prove byte-for-byte (or
  outcome-for-outcome) generation reproducibility for a fixed seed BEFORE and AFTER, and
  prove the global RNG is no longer perturbed by generation.

## Scope
**In:**
- `game/strategy/generation/star_generator.py` (26 bare `random.*` draws — primary)
- `game/strategy/data/planet_gen.py`, `planet_gen_surface.py`, `planet_physics.py`,
  `planet_atmosphere.py`, `naming.py`, `galaxy_warp_generator.py` (bare `random.*` draws)
- `game/strategy/generation/placement_strategies.py` (`rng is None` global fallbacks)
- `game/strategy/engine/game_initializer.py` (remove global `random.seed(galaxy_seed)` at
  ~line 250 once rng is threaded; ST-04-010)
- `game/ui/screens/galaxy_test/galaxy_mode.py` (remove global `random.seed(self.galaxy_seed)`
  at ~line 239 once rng is threaded; ST-04-011)
- The Pattern #18 guard test `tests/unit/quality/test_no_unseeded_random.py` (the strategy
  generation exclusion may be tightened once draws are seeded-instance only).

**Out:**
- Any combat / `ShipCombatEngine` / `battle_setup` RNG (owned by PROJ-471 — already done).
- `density_map.py` instance RNG (already Pattern #18-compliant; PROJ-471 ruled it
  OUT_OF_SCOPE — docstring accuracy only).
- Save-file format changes. Generation output for a fixed seed must remain reproducible;
  the project does NOT intend to change *what* is generated, only *where the randomness
  comes from*.

## Key Files
| Component | File Path |
|-----------|-----------|
| Star generation (primary) | `game/strategy/generation/star_generator.py` |
| Placement strategies (`rng is None` fallback) | `game/strategy/generation/placement_strategies.py` |
| Planet generation | `game/strategy/data/planet_gen.py`, `planet_gen_surface.py`, `planet_physics.py` |
| Planet atmosphere | `game/strategy/data/planet_atmosphere.py` |
| Naming | `game/strategy/data/naming.py` |
| Warp generation | `game/strategy/data/galaxy_warp_generator.py` |
| Galaxy init (seed removal) | `game/strategy/engine/game_initializer.py` |
| Galaxy test tool (seed removal) | `game/ui/screens/galaxy_test/galaxy_mode.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Origin: PROJ-471 `decisions.md` revision entries + `Reviews/results/2026-05-20_082533_state-audit/`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
