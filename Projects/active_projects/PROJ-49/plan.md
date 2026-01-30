# PROJ-49: Performance & Dead Code Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-49` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-49 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dead Code Cleanup | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simple Performance Fixes | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Component Caching | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. HP Ratio Caching | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Spatial Grid Optimization | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. O(n^2) Targeting Optimization | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-30
**Active Phase:** All Phases Complete - Ready for Audit
**Last Action:** Phase 6 complete - Capabilities caching for O(n) component lookups
**Next Action:** Trigger audit
**Blockers:** None

## Overview
Comprehensive project to address all performance bottlenecks and dead code issues identified in `findings_08_performance_dead_code.md`. This includes critical hot-path optimizations, O(n^2) algorithm fixes, dead code removal, duplicate consolidation, and codebase cleanup.

## Goals
- Eliminate critical performance bottlenecks affecting every tick (PERF-01 to PERF-10)
- Remove confirmed dead code and duplicate implementations
- Consolidate duplicate classes to single canonical versions
- Clean up repository artifacts (backup files, __pycache__, marked-for-deletion)
- Improve code maintainability without breaking existing functionality

## Scope
**In Scope:**
- All PERF-XX issues from findings document (PERF-01 through PERF-10)
- All DC-XX dead code issues (confirmed ones)
- All SIM-XXX simulation issues related to performance
- Duplicate class consolidation (panels, setup screens, projectile managers)
- Repository cleanup (backup files, marked directories)

**Out of Scope:**
- DC-01, UI-002, UI-003 broken imports (confirmed WORKING via launcher.py path setup)
- SIM-021 Formula eval() replacement (confirmed SECURE with proper sandboxing)
- New feature development
- Architecture redesign beyond performance fixes

## Key Files
| Component | File Path | Issue |
|-----------|-----------|-------|
| Component iteration | `game/simulation/entities/ship_stats.py:89` | PERF-01 |
| Battle engine hot path | `game/simulation/systems/battle_engine.py:520` | PERF-01 |
| Projectile list rebuild | `game/simulation/projectile_manager.py:138` | PERF-02 |
| O(n^2) targeting | `game/ai/controller.py:124-141` | PERF-03 |
| Ability MRO lookup | `game/simulation/components/component.py:182-209` | PERF-05 |
| Spatial grid rebuild | `game/simulation/systems/battle_engine.py:349-356` | PERF-06 |
| Dead panels | `game/ui/hud/panels.py` vs `game/ui/panels/battle_panels.py` | DC-001 |
| Dead setup screen | `game/ui/screens/setup.py` | UI-001 |
| Dead projectile mgr | `game/simulation/systems/projectile_manager.py` | SIM-009 |
| Dead ValidatorProxy | `game/simulation/entities/ship.py:29-34` | DC-06/SIM-006 |

## Decisions Log Summary
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Skip DC-01, UI-002, UI-003 | Imports confirmed working via launcher.py path setup |
| 2026-01-28 | Skip SIM-021 eval() replacement | Formula system is properly secured with AST validation |
| 2026-01-28 | Dead code first, then performance | Quick wins clean up codebase before complex perf work |
| 2026-01-28 | Archive dead code before deletion | User preference for safety |

See [decisions.md](decisions.md) for full decision log.

## Test Baseline
- **Date:** 2026-01-28
- **Tests:** 5296 passed, 3 skipped
- **Time:** 41.54s
- **Warnings:** Deprecation warnings for registry access (expected, tracked by PROJ-38)

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings_08_performance_dead_code.md](../../../findings_08_performance_dead_code.md) - Source findings

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (5296 baseline)
- [ ] Performance profiling shows improvement
- [ ] Audit passed
- [ ] User verified
