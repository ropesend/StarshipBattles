# PROJ-15: Phase 2 - Remove Shims and Aliases

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
| 1. Singleton Aliases | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fleet Warp Aliases | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ShipBuilderService Shim | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. PathSegment & to_hit_profile | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Deprecated Functions | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Builder Shims | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-25
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Comprehensive analysis and planning complete
**Next Action:** Begin Phase 1 - Singleton Aliases
**Blockers:** None

## Overview
Phase 2 of the Legacy Code Cleanup project. Removes backward compatibility shims (5 files to delete), method aliases (fleet warp, PathSegment.hex, to_hit_profile), singleton get_instance() aliases, and deprecated functions (load_combat_strategies, _execute_move_step).

## Goals
- Delete 5 shim files (builder_screen.py, builder_viewmodel.py, builder_data_loader.py, builder_event_router.py, ship_builder_service.py)
- Remove method aliases and update all callers to use canonical names
- Remove deprecated functions and update callers
- Standardize singleton accessor pattern to instance()

## Scope
**In Scope:**
- Builder → Workshop shim files (4 files)
- ShipBuilderService → VehicleDesignService shim (1 file)
- Fleet warp method aliases (has_energy_for_warp, consume_warp_energy)
- PathSegment.hex property alias
- to_hit_profile → total_defense_score alias
- Singleton get_instance() aliases (3 classes)
- Deprecated load_combat_strategies() function
- Deprecated TurnEngine._execute_move_step() method

**Out of Scope (Defer to Phase 3):**
- `project_path_as_dicts()` wrapper (requires updating pathfinding callers)
- TurnEngine._spawn_complex, _spawn_ship, _calculate_next_hex (useful delegators, not aliases)

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| SpriteManager | `game/ui/renderer/sprites.py` | Remove get_instance alias (line 47) |
| ShipThemeManager | `game/simulation/ship_theme.py` | Remove get_instance alias (line 44) |
| ScreenshotManager | `game/core/screenshot_manager.py` | Remove get_instance alias (line 47) |
| Fleet | `game/strategy/data/fleet.py` | Remove warp aliases (lines 350-403) |
| PathSegment | `game/strategy/engine/fleet_movement.py` | Remove hex property (lines 43-46) |
| to_hit_profile | `game/simulation/entities/ship.py:130`, `ship_stats.py:389-390`, `data/stats_layout.json:276` | Remove alias |
| ShipBuilderService | `game/simulation/services/ship_builder_service.py` | DELETE FILE |
| BuilderSceneGUI | `game/ui/screens/builder_screen.py` | DELETE FILE |
| BuilderViewModel | `game/ui/screens/builder_viewmodel.py` | DELETE FILE |
| BuilderDataLoader | `game/ui/screens/builder_data_loader.py` | DELETE FILE |
| BuilderEventRouter | `game/ui/screens/builder_event_router.py` | DELETE FILE |
| load_combat_strategies | `game/ai/strategy_manager.py:151-171` | Delete function |
| _execute_move_step | `game/strategy/engine/turn_engine.py:261-286` | Delete method |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Include to_hit_profile removal | Investigation confirmed stats_layout.json is NOT deprecated, alias can be safely removed |
| 2026-01-25 | Defer project_path_as_dicts() | Used by pathfinding.py, requires broader changes |
| 2026-01-25 | Keep TurnEngine._spawn_* methods | These are delegators to ProductionEngine, not aliases |
| 2026-01-25 | Order phases by risk | Start with singleton aliases (lowest risk), end with builder shims (highest risk) |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log
- [../legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md](../legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md) - Original phase specification

## Verification
### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No import errors when running `python -c "import game"`

### Final Verification
- [ ] `pytest tests/` - Full test suite passes
- [ ] `python -m game.app` - Application launches
- [ ] Navigate to Design Workshop - opens correctly
- [ ] No DeprecationWarning emissions during tests
- [ ] All 5 shim files deleted

## Pre-existing Issues
- Test `test_intercept_integration` is flaky when run with parallel workers (pre-existing)
- Test isolation issues exist in strategy tests when run in parallel (pre-existing)

## Risks & Mitigations
1. **BuilderSceneGUI wrapper complexity** - The shim is 154 lines with __getattr__ delegation. Mitigation: Update tests last, verify app.py works first.
2. **workshop_viewmodel.py dependency** - Uses ShipBuilderService extensively. Mitigation: Update imports systematically.
3. **Test flakiness** - Some tests have isolation issues. Mitigation: Run tests with `-n 1` if failures occur.
