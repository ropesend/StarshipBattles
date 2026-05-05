# PROJ-359: Typed Weapon Execution Contract — Replace String/Class Dispatch

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-359` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-359 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Characterization (golden) tests for current dispatch | Not started | (to be created at /proj-start) |
| 2. AttackRequest / AttackResolution + registry skeleton | Not started | (to be created at /proj-start) |
| 3. Migrate weapon families one at a time | Not started | (to be created at /proj-start) |
| 4. Delete string-class branches + dict carriers | Not started | (to be created at /proj-start) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** 1
**Last Action:** Project scaffolded from realtime-combat tech-debt review finding #4 — largest of the 5 derived projects, intentionally phased.
**Next Action:** Run /claude-proj-start PROJ-359 to expand design + per-phase checklists.
**Blockers:** None

## Overview

Weapon behavior is dispatched by ability class names and dictionary fields
across four systems: weapon firing, targeting, collision, and projectile
hit application. Adding a new weapon family today requires coordinated
edits to all four files, plus telemetry and outcome paths. Simulation
semantics also leak into `game/engine/collision.py` through dictionary
attack carriers.

Introduce a typed `AttackRequest` / `AttackResolution` model and a weapon
family registry; migrate Beam, Projectile, Seeker, and PDC behind that
contract; then delete the legacy string branches.

Source: realtime combat tech-debt review finding #4 (P2 extensibility, largest leverage).

## Goals
- A single `AttackRequest` dataclass replaces dict-shaped attack payloads at the firing→engine boundary
- A weapon family registry routes targeting filters, firing logic, collision/hit application by family, not by string class name
- Adding a new weapon family is one registration call + one family module — no edits to firing/targeting/collision/projectile centrals
- Damage event contracts converge: beam and projectile produce equivalent telemetry shapes
- Final state: zero remaining `comp.has_ability('BeamWeaponAbility')` / `'SeekerWeaponAbility'` string branches in firing or targeting

## Scope
**In:**
- `game/simulation/combat/weapon_firing_system.py`
- `game/simulation/combat/targeting_system.py`
- `game/engine/collision.py` (process_beam_attack and dict carriers)
- `game/simulation/projectile_manager.py` (hit application)
- New `game/simulation/combat/weapon_registry.py` (or co-located with firing system)
- Tests across `tests/unit/simulation/combat/`

**Out:**
- New weapon families (this is a refactor — content-add is separate)
- Strategy spec compiler changes
- AI targeting policy/rule rewrites (handled in PROJ-356 + targeting policy work)
- Visual/UI weapon rendering
- Fleet aura interactions (already covered by PROJ-357)

## Key Files
| Component | File Path |
|-----------|-----------|
| Firing dispatch (string branches) | `game/simulation/combat/weapon_firing_system.py:198,221,236` |
| Targeting (PDC/seeker rules) | `game/simulation/combat/targeting_system.py:123` |
| Collision (beam dict path) | `game/engine/collision.py:68` |
| Projectile hit application | `game/simulation/projectile_manager.py:130` |
| New contract module | `game/simulation/combat/attack_contract.py` (to be created) |
| Weapon family registry | `game/simulation/combat/weapon_registry.py` (to be created) |

## Phasing Notes
Phase 1 locks current behavior with golden tests before any structural change.
Phase 2 introduces the contract behind the existing dispatch (no behavior change).
Phase 3 migrates families one at a time, keeping the legacy branch as a fallback until the last family is moved.
Phase 4 deletes the legacy branches once no caller relies on them.

## Related Documents
- Review report finding #4: `Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md`
- Architecture: `docs/01_ARCHITECTURE.md` § layers (Engine vs Simulation boundary)
- Combat docs: `docs/systems/combat_simulation.md`

## Verification
- [ ] Phase 1 golden tests reproduce current beam/projectile/seeker/PDC damage events bit-for-bit
- [ ] After migration, golden tests still pass
- [ ] A fake `TestWeaponFamily` registers and fires without editing firing/targeting/collision/projectile centrals
- [ ] PDC target restrictions are validated via weapon metadata, not string lookup
- [ ] Zero `comp.has_ability('BeamWeaponAbility' | 'SeekerWeaponAbility' | 'ProjectileWeaponAbility')` string branches remain in firing/targeting
- [ ] `python Tools/test_sharded/test_sharded.py` passes
