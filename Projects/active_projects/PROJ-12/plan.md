# PROJ-12: Performance Optimization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-12` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Battle Loop Hot Path | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. AI & Spatial Queries | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Component & Stats | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-01-24 05:25
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 - Battle loop optimization
**Blockers:** Should complete PROJ-10, PROJ-11 first (refactoring may change hot paths)

## Overview
This project addresses **performance issues** that will become bottlenecks as battles scale (more ships, larger galaxies). Focus is on hot paths in the battle simulation loop.

**Total Findings:** 17 (Critical: 2, Major: 6, Minor: 9)

**Dependencies:** Best to complete after PROJ-11 (architecture changes may affect these areas)

## Goals
### Phase 1: Battle Loop Hot Path (CRITICAL)
- Fix spatial grid rebuild every frame (PERF-02)
- Fix inefficient type check in projectile collision (PERF-01)
- Fix projectile removal pattern (PERF-08)
- Fix grid clear method (PERF-12)

### Phase 2: AI & Spatial Queries (MAJOR)
- Consolidate multiple spatial queries per AI (PERF-03)
- Cache AI query results within update cycle
- Optimize target evaluation

### Phase 3: Component & Stats (MAJOR)
- Fix full component iteration in stat calculation (PERF-04)
- Reduce deep copy on component creation (PERF-05)
- Cache ability lookups (PERF-06, PERF-10)
- Cache ability totals (PERF-14)

## Scope
**In:**
- `game/simulation/systems/battle_engine.py` - Main loop
- `game/simulation/projectile_manager.py` - Collision detection
- `game/engine/spatial.py` - Spatial grid
- `game/ai/controller.py` - AI queries
- `game/simulation/entities/ship_stats.py` - Stat calculation
- `game/simulation/components/component.py` - Component creation

**Out:**
- Security fixes (PROJ-10)
- Architecture refactoring (PROJ-11)
- Non-hot-path code optimization

## Key Files
| Component | File Path |
|-----------|-----------|
| Battle Engine | `game/simulation/systems/battle_engine.py` |
| Projectile Manager | `game/simulation/projectile_manager.py` |
| Spatial Grid | `game/engine/spatial.py` |
| AI Controller | `game/ai/controller.py` |
| Ship Stats | `game/simulation/entities/ship_stats.py` |

## Related Documents
- [design.md](design.md) - Performance analysis
- [decisions.md](decisions.md) - Decisions log
- [Review Report](../../Reviews/results/2026-01-24_general_maintainability-extensibility-health/report.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Battle with 60+ ships runs at 60 FPS
- [ ] Profile shows no obvious bottlenecks
- [ ] Audit passed
