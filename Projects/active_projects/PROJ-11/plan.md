# PROJ-11: Architecture Refactoring

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-11` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-11 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Circular Dependencies | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. God Objects Refactoring | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Layer Coupling | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Simulation Module | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-01-24 05:20
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 - Circular dependency resolution
**Blockers:** Should complete PROJ-10 (Security) first

## Overview
This project addresses **architectural issues** that block maintainability and extensibility. These are the foundational changes needed before the codebase can grow sustainably.

**Total Findings:** 18 (Critical: 5, Major: 13)

**Dependencies:** Complete PROJ-10 first (security fixes should not be blocked by refactoring)

## Goals
### Phase 1: Circular Dependencies (CRITICAL)
- Eliminate circular import workarounds (AR-03, MOD-SIM-03)
- Implement dependency injection patterns
- Create clear module interfaces

### Phase 2: God Objects Refactoring (CRITICAL)
- Break up StrategyInterface (AR-01, MOD-UI-01)
- Extract Ship class responsibilities (CQ-05, MOD-SIM-06)
- Refactor app.py orchestrator (AR-08)

### Phase 3: Layer Coupling (MAJOR)
- Create GameFacade for UI (AR-02, MOD-UI-04)
- Fix UI-to-Strategy coupling (AR-04, MOD-STR-06)
- Establish clear layer boundaries

### Phase 4: Simulation Module (MAJOR)
- Unify ability systems (MOD-SIM-01)
- Extract stat calculation phases (MOD-SIM-02)
- Fix modifier dependency resolution (MOD-SIM-07)

## Scope
**In:**
- `game/app.py` - Orchestrator refactoring
- `game/ui/screens/strategy_screen.py` - God object breakup
- `game/simulation/entities/ship.py` - SRP violations
- `game/simulation/entities/ship_stats.py` - Stat calculation
- `game/simulation/components/component.py` - Ability system
- Circular dependency resolution throughout

**Out:**
- Security fixes (PROJ-10)
- Performance optimization (PROJ-12)
- Dead code cleanup (PROJ-13)

## Key Files
| Component | File Path |
|-----------|-----------|
| App Orchestrator | `game/app.py` |
| Strategy Interface | `game/ui/screens/strategy_screen.py` |
| Ship Entity | `game/simulation/entities/ship.py` |
| Ship Stats | `game/simulation/entities/ship_stats.py` |
| Component System | `game/simulation/components/component.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis
- [decisions.md](decisions.md) - Decisions log
- [Review Report](../../Reviews/results/2026-01-24_general_maintainability-extensibility-health/report.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No circular imports (verified with tool)
- [ ] God objects broken into < 300 lines each
- [ ] Layer boundaries enforced
- [ ] Audit passed
