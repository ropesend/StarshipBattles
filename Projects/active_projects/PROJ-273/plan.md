# PROJ-273: Shared Ability Stat Key Registry

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-273` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-273 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create registry module + unit tests (TDD) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate Battle Setup compiler | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Strategy compiler | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Glob-driven coverage test | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Runtime unknown-stat_key warning | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** Planning (ready to start Phase 1)
**Last Action:** Project created with full plan, derived from combat system review
**Next Action:** Begin Phase 1 — create registry module and failing unit tests
**Blockers:** None
**Context for Next Agent:** This project unblocks PROJ-275 (N-team combat). Can be executed in parallel with PROJ-274. Core insight: `_ABILITY_TO_STAT_KEY` at `game/ui/screens/battle_setup/spec_compiler.py:70-74` and the hardcoded `stat_key=...` calls in `game/strategy/combat/spec_compiler.py:353,385,400,412,444` are emitting the same three mappings independently. No test enforces consistency. Registry consolidates them.

## Overview

Eliminate duplicate ability→stat_key mapping between Battle Setup and Strategy spec compilers. Introduce a single registry module that both compilers (and any future caller) import from, plus a glob-driven guard test so new `qs_*_complex.json` designs are automatically covered. Add a runtime warning in `FleetAuraManager` when an unknown stat_key appears in the modifier stack (today silently ignored).

## Goals

- One canonical mapping of ability class name → (stat_key, operation, value_field).
- Both spec compilers emit `ModifierEntry` through a shared helper, not via hand-rolled hardcoded functions.
- Test that iterates every `data/designs/qs_*_complex.json` and asserts no placeholder entries / no unknown abilities.
- Unknown stat_keys emit a runtime WARNING in `FleetAuraManager` (currently silently ignored).

## Scope

**In:**
- New module: `game/simulation/combat/ability_stat_registry.py`
- Refactor `_ABILITY_TO_STAT_KEY` out of `game/ui/screens/battle_setup/spec_compiler.py` (lines 70-74)
- Refactor `_entries_from_environmental_effects` + `_entries_from_fleet_combat_modifiers` in `game/strategy/combat/spec_compiler.py` (lines 336-412) to use the shared helper
- New auto-coverage test: `tests/unit/simulation/combat/test_ability_stat_registry.py`
- Runtime warning in `game/simulation/combat/fleet_aura_manager.py::_apply_bonuses`
- Docs: `docs/systems/combat_simulation.md`, `docs/systems/strategy_layer.md`, `docs/02_PATTERNS.md`

**Out:**
- Adding new abilities to the registry (content work, not a refactor)
- Changing stat_key semantics (composition order in `ship_stats.py`)
- Changes to `_route_team_for_scope` signature (that lands in PROJ-275)

## Key Files

| Component | File Path |
|-----------|-----------|
| New registry module | `game/simulation/combat/ability_stat_registry.py` |
| Battle Setup compiler | `game/ui/screens/battle_setup/spec_compiler.py` |
| Strategy compiler | `game/strategy/combat/spec_compiler.py` |
| Fleet aura manager | `game/simulation/combat/fleet_aura_manager.py` |
| New guard test | `tests/unit/simulation/combat/test_ability_stat_registry.py` |
| Existing guard | `tests/unit/simulation/test_unified_entry_guard.py` |
| Docs | `docs/systems/combat_simulation.md`, `docs/systems/strategy_layer.md`, `docs/02_PATTERNS.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest

## Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/unit/simulation/combat/test_ability_stat_registry.py` passes
- [ ] Glob-driven test covers every `data/designs/qs_*_complex.json`
- [ ] Full suite: `python Tools/test_sharded/test_sharded.py` — 14727+ passing, no regressions
- [ ] Manual: launch Battle Setup with a shield-booster complex, verify aura labels still appear on battle HUD
- [ ] Audit passed
- [ ] User verified
