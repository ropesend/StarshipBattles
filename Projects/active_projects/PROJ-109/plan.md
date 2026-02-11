# PROJ-109: Legacy Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-109` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-109 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dead Code Deletion (8 tasks) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simple Shim Removals (10 tasks) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Medium Complexity Removals (8 tasks) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Complex Legacy Eradication (8 tasks) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Foundation Cleanup (3 tasks) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** All phases complete - Ready for Audit
**Last Action:** Phase 5 complete (3 tasks): Logger converted to SingletonMeta, _ProfilerProxy removed, target_evaluator audit (no unused params found)
**Next Action:** Run Audit Cycle 1
**Blockers:** None

## Overview
Remove legacy backward compatibility shims, deprecated code paths, dead code, and obsolete patterns identified during the 2026-02-10 full-codebase sweep. The project policy states: "When a new system replaces an old one, ERADICATE the old system completely." This project follows through on that policy by removing all identified legacy holdovers.

## Goals
- Remove all backward compatibility shims and wrappers
- Delete dead/unreachable code paths
- Eliminate deprecated parameters and dual-path patterns
- Remove save game migration code (per disposable saves policy)
- Clean up proxy patterns and fallback mechanisms
- Remove misleading "backward compat" comments on non-legacy code

## Scope
**In:**
- All CRITICAL and MAJOR legacy findings from sweep (with exceptions noted below)
- Backward compat shims, deprecated parameters, dead code
- Save format migration code
- Registry fallback patterns (bootstrap vs strict DI)
- Deprecated scene transition mechanisms
- Misleading "backward compat" comments on valid code
- Logger/Profiler proxy pattern cleanup

**Out:**
- LEG-UI2-001: Singleton-to-DI migration for SpriteManager/ShipThemeManager (DEC-002 - needs own project)
- LEG-FND-007: old_ variable naming in research_service.py (DEC-008 - style preference, not legacy)
- LEG-FND-008: TypeGuard import fallback (DEC-009 - Python version compat, not legacy)
- LEG-UI2-007: Fallback image creation (DEC-010 - defensive programming, not legacy)
- Architecture violations (PROJ-106)
- God class decomposition (PROJ-86/87/88/89)

## Findings Coverage

### Addressed (37 tasks across 5 phases)
| Finding | Phase | Task | Severity |
|---------|-------|------|----------|
| LEG-SIM-002 | 1 | 1.1 | MAJOR |
| LEG-UI2-003/LEG-UI1-003 | 1 | 1.2 | MAJOR |
| LEG-FND-004 (create) | 1 | 1.3 | MAJOR |
| LEG-SIM-005 | 1 | 1.4 | MINOR |
| LEG-UI1-004 | 1 | 1.5 | MAJOR |
| LEG-UI1-011 | 1 | 1.6 | MINOR |
| LEG-SIM-007 | 1 | 1.7 | INFO |
| LEG-SIM-006 | 1 | 1.8 | MINOR |
| LEG-STR-003 | 2 | 2.1 | MAJOR |
| LEG-STR-004 | 2 | 2.2 | MAJOR |
| LEG-STR-005 | 2 | 2.3 | MAJOR |
| LEG-UI2-004 | 2 | 2.4 | MAJOR |
| LEG-UI2-005 | 2 | 2.5 | MAJOR |
| LEG-UI1-006 | 2 | 2.6 | MAJOR |
| LEG-UI2-002 | 2 | 2.7 | CRITICAL |
| LEG-UI1-007/LEG-UI2-008 | 2 | 2.8 | MAJOR/MINOR |
| LEG-STR-010/013/014/012 | 2 | 2.9 | MINOR/INFO |
| LEG-STR-009 | 2 | 2.10 | MINOR |
| LEG-FND-004 (validation_result) | 3 | 3.1 | MAJOR |
| LEG-FND-001 (partial) | 3 | 3.1 | CRITICAL |
| LEG-UI1-001/010 | 3 | 3.2 | CRITICAL/MINOR |
| LEG-UI1-002 | 3 | 3.3 | CRITICAL |
| LEG-UI1-005 | 3 | 3.4 | MAJOR |
| LEG-UI1-008/009 | 3 | 3.5 | MINOR |
| LEG-STR-006 | 3 | 3.6 | MAJOR |
| LEG-STR-011 | 3 | 3.7 | MINOR |
| LEG-STR-008 | 3 | 3.8 | MINOR |
| LEG-STR-001 | 4 | 4.1 | CRITICAL |
| LEG-SIM-001 | 4 | 4.2 | CRITICAL |
| LEG-SIM-003 | 4 | 4.3 | MAJOR |
| LEG-SIM-004 | 4 | 4.4 | MAJOR |
| LEG-STR-002 | 4 | 4.5 | CRITICAL |
| LEG-STR-007 | 4 | 4.6 | MAJOR |
| LEG-STR-012 | 4 | 4.7 | MINOR |
| LEG-FND-006 | 4 | 4.8 | MINOR |
| LEG-FND-002 | 5 | 5.1 | MAJOR |
| LEG-FND-003 | 5 | 5.2 | MAJOR |
| LEG-FND-005 | 5 | 5.3 | MINOR |

### Excluded (with rationale)
| Finding | Reason | Decision |
|---------|--------|----------|
| LEG-UI2-001 | Singleton-to-DI (18+ call sites, needs own project) | DEC-002 |
| LEG-FND-007 | Style preference, not legacy code | DEC-008 |
| LEG-FND-008 | Python version compat, not legacy | DEC-009 |
| LEG-UI2-007 | Defensive programming, not legacy | DEC-010 |

### Kept (with comment cleanup only)
| Finding | Action | Decision |
|---------|--------|----------|
| LEG-FND-001 (.message) | Keep .message property | DEC-005 |
| LEG-STR-010 | Remove misleading comment | DEC-015 |
| LEG-STR-013 | Remove misleading comment | DEC-016 |
| LEG-STR-014 | Fix comment | DEC-017 |

## Key Files
| Component | File Path |
|-----------|-----------|
| ValidationResult | `game/core/validation.py` |
| Logger proxy | `game/core/logger.py` |
| Profiler proxy | `game/core/profiling.py` |
| Registry fallback | `game/simulation/components/component.py` |
| BattleEngine AI init | `game/simulation/systems/battle_engine.py` |
| Save game migration | `game/strategy/systems/save_game_service.py` |
| Fleet order formats | `game/strategy/data/fleet.py` |
| Scene transitions | `game/ui/screens/battle_screen.py` |
| Input handler legacy | `game/ui/screens/strategy_input_handler.py` |
| Build queue legacy | `game/ui/screens/build_queue_screen.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log (17 decisions)
- **Source sweep:** `Reviews/results/2026-02-10_sweep_full-codebase-sweep/findings/legacy_*.md`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (8164 baseline)
- [ ] No DeprecationWarnings in test output
- [ ] No "backward compat" comments remain in targeted code
- [ ] Audit passed
- [ ] User verified
