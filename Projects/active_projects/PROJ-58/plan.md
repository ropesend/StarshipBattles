# PROJ-56: Eradicate Backward Compatibility Shims

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-56` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-56 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins (Zero-Risk Removals) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Constants & Import Migration | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Formation Delegation Removal | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. ShipCombatMixin Elimination | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. BattleController Compat Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Registry DI Fallback Migration | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-06 18:45
**Active Phase:** Planning
**Last Action:** Deep code review complete, all shims catalogued
**Next Action:** User approval of plan
**Blockers:** None
**Context for Next Agent:** Baseline is 6114 passed, 5 skipped. See design.md for complete shim inventory.

## Overview
Remove all backward compatibility shims from the codebase per the CLAUDE.md policy (lines 136-158). This includes: re-exported constants, delegation properties, facade mixins, proxy properties, fallback code paths, and transitional DI patterns. Target: zero occurrences of "backward compat" in comments.

## Goals
- Remove all 44+ backward compatibility shims
- Update all callers to use the canonical/new API
- Properly separate Ship from combat operations (complete PROJ-12 intent)
- Migrate all DI fallbacks to strict injection
- Remove all "backward compatibility" comments from codebase

## Scope
**In:**
- Path constant re-exports in `constants.py` and `paths.py` (22 import sites)
- LayerType re-export in `component_constants.py` (19 import sites)
- Formation delegation properties in `ship.py` (6 properties)
- ShipCombatMixin facade in `ship_combat.py` (entire file)
- Workshop ViewModel proxy properties in `workshop_screen.py` (3 properties)
- BattleController retreat/escape proxy properties (4 properties + 2 fallback methods)
- Collision defense score fallback in `collision.py` (1 fallback chain - investigate first)
- `get_default_registries()` transitional fallback (18 callers)

**Out:**
- `ShipControllableAdapter` (proper adapter pattern, not a shim)
- `SimulationBattleResolver` (proper layer boundary adapter)
- `DesignLoaderAdapter` (proper layer isolation)
- `get_default_registry_provider()` (proper DI mechanism, not a shim)
- Any structural architecture changes beyond removing shims

## Key Files
| Component | File Path |
|-----------|-----------|
| Ship formation delegation | `game/simulation/entities/ship.py` |
| ShipCombatMixin | `game/simulation/entities/ship_combat.py` |
| ShipCombatEngine | `game/simulation/entities/ship_combat_engine.py` |
| BattleController | `game/simulation/battle_controller.py` |
| Workshop screen | `game/ui/screens/workshop_screen.py` |
| Collision system | `game/engine/collision.py` |
| Path constants | `game/core/paths.py` |
| Core constants | `game/core/constants.py` |
| Component constants | `game/simulation/components/component_constants.py` |
| Registry module | `game/core/registry.py` |
| AI adapter | `game/ai/interfaces/controllable.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | ShipCombatMixin: redirect callers to combat_engine | Clean sheet approach - Ship is data/component host, not a combat actor. Completes PROJ-12 intent. |
| 2026-02-06 | Include get_default_registries() migration in scope | User decision - addresses all backward compat patterns comprehensively |
| 2026-02-06 | Collision fallback: investigate before removing | May have non-Ship objects in collision system; verify first |
| 2026-02-06 | Path migration target: Paths.CONSTANT | Full migration to class access pattern, remove all module-level re-exports |
| 2026-02-06 | Registry DI: NOT a shim pattern | get_default_registries() and get_default_registry_provider() excluded from "shim" label |

---

## Phases

### Phase 1: Quick Wins (Zero-Risk Removals) [Simple]
**Objective:** Remove backward compat code that has zero callers or is already dead code.
**Status:** Not Started

### Phase 2: Constants & Import Migration [Simple]
**Objective:** Migrate all 41 import sites from re-exported constants to canonical locations.
**Status:** Not Started

### Phase 3: Formation Delegation Removal [Simple]
**Objective:** Update AI adapter, remove 6 delegation properties from Ship.
**Status:** Not Started

### Phase 4: ShipCombatMixin Elimination [Complex]
**Objective:** Remove the entire mixin, redirect all callers to ship.combat_engine.
**Status:** Not Started

### Phase 5: BattleController Compat Cleanup [Medium]
**Objective:** Remove proxy properties and dual-path fallback logic.
**Status:** Not Started

### Phase 6: Registry DI Fallback Migration [Complex]
**Objective:** Migrate all 18 get_default_registries() callers to strict DI.
**Status:** Not Started

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 6114 passed, 5 skipped (baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Run `pytest tests/` - full suite passes (no regressions)

### Final Verification
- [ ] Run full test suite: `pytest tests/` (NOT --testmon)
- [ ] `grep -r "backward compat" game/` returns zero results
- [ ] No remaining re-exports marked as "deprecated" or "backward compatibility"
- [ ] All tests passing

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
