# PROJ-58: Eradicate Backward Compatibility Shims

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-58` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-58 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins (Zero-Risk Removals) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Path Constant Import Migration | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. LayerType Import Migration | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Formation Delegation Removal | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. ShipCombatMixin Elimination | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. BattleController & Collision Cleanup | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Registry DI Fallback Migration | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-06
**Active Phase:** All phases complete
**Last Action:** Phase 7 complete. Removed RegistryManager backward-compat fallback chains from TurnEngine, ShipInstance, WorkshopContext, and ShipFactory. Fixed root conftest to call set_default_registries() after hydration. Updated registry.py docstrings. 6246 passed.
**Next Action:** Final verification and audit
**Blockers:** None
**Context for Next Agent:** All 7 phases complete. 6246 passed, 0 failed. Ready for final audit.

## Overview
Remove all backward compatibility shims from the codebase per the CLAUDE.md policy (lines 136-158). Includes: re-exported constants, delegation properties, facade mixins, proxy properties, fallback code paths, and transitional DI patterns.

## Goals
- Remove all backward compatibility shims from active code
- Update all callers to use the canonical/new API
- Properly separate Ship from combat operations (complete PROJ-12 intent)
- Migrate production DI fallbacks to strict injection

## Scope
**In:** Workshop proxies, dead mixin methods, stale comments, path re-exports (23 sites), WIDTH/HEIGHT (2 sites), LayerType re-export (24 legacy sites), formation delegation (170+ callers), ShipCombatMixin (50+ callers), BattleController proxies (tests only), retreat/reinforcement OR-fallback, collision hasattr fallback, `get_default_registries()` (6 prod callers)

**Out:** `apply_results_to_fleets()` (blocked by PROJ-41), BattleEngine legacy controller creation, `DefaultRegistryProvider`, `ValidationResult` dual construction, `ComponentRef` converters, `GameSession` convenience aliases

## Key Files
| Component | File Path |
|-----------|-----------|
| Ship formation delegation | `game/simulation/entities/ship.py` |
| ShipCombatMixin | `game/simulation/entities/ship_combat.py` |
| ShipCombatEngine | `game/simulation/entities/ship_combat_engine.py` |
| BattleController | `game/simulation/battle_controller.py` |
| Workshop screen | `game/ui/screens/workshop_screen.py` |
| Collision system | `game/engine/collision.py` |
| Core constants | `game/core/constants.py` |
| Component constants | `game/simulation/components/component_constants.py` |
| Registry module | `game/core/registry.py` |
| AI adapter | `game/ai/interfaces/controllable.py` |
| AI controller | `game/ai/controller.py` |
| Ship factory | `game/ui/services/ship_factory.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Quick Wins (Zero-Risk Removals) [Simple]
**Objective:** Remove dead code, workshop proxy internal usages, stale comments.

### Phase 2: Path Constant Import Migration [Simple]
**Objective:** Migrate 23 sites from `game.core.constants` path re-exports to `Paths.*`, plus 2 WIDTH/HEIGHT sites.

### Phase 3: LayerType Import Migration [Simple]
**Objective:** Migrate 24 legacy LayerType imports from `component_constants` to `game.core.constants`.

### Phase 4: Formation Delegation Removal [Medium]
**Objective:** Update 10 prod callers + 6 adapter methods + 155 test callers, remove 5 delegation properties.

### Phase 5: ShipCombatMixin Elimination [Complex]
**Objective:** Redirect all callers to `ship.combat_engine.*`, relocate `die()`, delete mixin file.

### Phase 6: BattleController & Collision Cleanup [Medium]
**Objective:** Remove proxy properties, simplify fallback logic, remove collision hasattr chain.

### Phase 7: Registry DI Fallback Migration [Complex]
**Objective:** Remove RegistryManager backward-compat fallback chains, unify on `get_default_registries()` as single service locator, fix test infrastructure.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 6248 passed, 0 failed (baseline)

### After Each Phase
- [ ] Run `pytest tests/` - full suite passes

### Final Verification
- [ ] Run full test suite: `pytest tests/`
- [ ] `grep -rn "backward compat" game/` returns zero active-code results
- [ ] All tests passing

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] Phase 1 complete
- [x] Phase 2 complete
- [x] Phase 3 complete
- [x] Phase 4 complete
- [x] Phase 5 complete
- [x] Phase 6 complete
- [x] Phase 7 complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
