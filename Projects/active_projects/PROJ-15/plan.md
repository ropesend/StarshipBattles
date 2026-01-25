# PROJ-15: Legacy Cleanup Phase 2 - Remove Shims and Aliases

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-15` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-15 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Pure Alias Files | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Singleton Aliases | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Method/Property Aliases | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Deprecated Functions | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. BuilderSceneGUI Wrapper | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Test Directory Rename | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Audit Fix | Pending | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-01-25
**Active Phase:** Phase 7 - Audit Fix
**Last Action:** Audit found 1 test file missed during Phase 3 - `tests/strategy/test_path_projection.py` still references `'hex'` key instead of `'end'`.
**Next Action:** Fix test_path_projection.py to use 'end' key instead of 'hex'
**Blockers:** None
**Summary:**
- Phases 1-6 complete
- Audit FAILED: 1 test file was not updated when PathSegment.to_dict() removed 'hex' key
- Fix required in tests/strategy/test_path_projection.py lines 81-84

## Overview
Remove backward compatibility shims and aliases introduced during previous refactoring efforts. This includes Builder → Workshop shim files, singleton accessor aliases, method/property aliases, and deprecated functions.

## Goals
- Delete 5 shim files that re-export Workshop classes under old Builder names
- Remove `get_instance` singleton accessor aliases (use `instance()` pattern)
- Remove method aliases: Fleet warp methods, PathSegment.hex, project_path_as_dicts, to_hit_profile
- Remove deprecated functions: load_combat_strategies, TurnEngine wrappers
- Rename test directory from `tests/unit/builder/` to `tests/unit/workshop/`

## Scope
**In:**
- All shim files in game/ui/screens/ with "builder" prefix
- ship_builder_service.py shim
- Singleton accessor aliases in 3 manager classes
- Method aliases in fleet.py, fleet_movement.py, ship_stats.py
- Deprecated functions in strategy_manager.py, turn_engine.py
- Test file renames and import updates

**Out:**
- Phases 3-8 of legacy cleanup
- Actual Workshop/DesignWorkshopGUI implementation changes
- New feature development

## Key Files
| Component | File Path |
|-----------|-----------|
| Main Wrapper | `game/ui/screens/builder_screen.py` (DELETED) |
| App Entry | `game/app.py` |
| Workshop GUI | `game/ui/screens/workshop_screen.py` |
| Services Init | `game/simulation/services/__init__.py` |
| Fleet | `game/strategy/data/fleet.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Ship Stats | `game/simulation/entities/ship_stats.py` |
| Strategy Manager | `game/ai/strategy_manager.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log
- [Projects/legacy_cleanup/README.md](../../legacy_cleanup/README.md) - Master cleanup plan
- [Projects/legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md](../../legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md) - Original phase spec

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing: `pytest tests/ simulation_tests/`
- [x] Game launches: `python -c "from game.app import Game"` (Import OK)
- [x] No deprecation warnings in output
- [ ] User verified

## Audit Log
| Date | Auditor | Result | Notes |
|------|---------|--------|-------|
| 2026-01-25 | Claude (Skeptical Reviewer) | FAILED | 1 test file missed: tests/strategy/test_path_projection.py still uses 'hex' key |
