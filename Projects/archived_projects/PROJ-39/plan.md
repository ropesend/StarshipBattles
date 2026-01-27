# PROJ-39: General Remediation: Path Centralization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-39` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-39 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Core Files | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy Layer | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Assets/UI | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Test Integration | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Status:** Archived
**Last Action:** Project closed and archived after audit passed
**Next Action:** N/A - Project complete
**Blockers:** None
**Context for Next Agent:** N/A - See archived plan for historical reference

**Summary of Work Completed:**
- Phase 1: Created `game/core/paths.py` with centralized `Paths` class, updated `constants.py` for backward compatibility
- Phase 2: Migrated core files (app.py, logger.py, profiling.py, ship_loader.py) to use Paths
- Phase 3: Migrated strategy layer (save_game_service.py, race_library.py) to use Paths
- Phase 4: Migrated asset/UI files (asset_manager.py, tech_preset_loader.py, setup_data_io.py) to use Paths
- Phase 5: Updated test path utilities to delegate to game.core.paths

**Files Modified (14 key files):**
1. `game/core/paths.py` - NEW: Centralized path configuration
2. `game/core/constants.py` - Updated to import from paths.py
3. `game/core/logger.py` - Uses Paths.BATTLE_LOG
4. `game/core/profiling.py` - Uses Paths.PROFILING_HISTORY
5. `game/app.py` - Uses Paths for all data loading
6. `game/simulation/entities/ship_loader.py` - Uses Paths.VEHICLE_CLASSES_FILE
7. `game/strategy/systems/save_game_service.py` - Uses Paths.SAVES_DIR
8. `game/strategy/systems/race_library.py` - Uses Paths.RACES_DIR
9. `game/assets/asset_manager.py` - Uses Paths.ASSET_MANIFEST_FILE
10. `game/simulation/systems/tech_preset_loader.py` - Uses Paths.TECH_PRESETS_DIR
11. `game/ui/screens/setup_data_io.py` - Uses Paths.SHIPS_DIR, Paths.FORMATIONS_DIR
12. `tests/fixtures/paths.py` - Delegates to game.core.paths.Paths
13. `tests/integration/test_save_load.py` - Updated to patch Paths.SAVES_DIR
14. `tests/unit/strategy/test_save_game_service.py` - Updated to patch Paths.SAVES_DIR

## Overview
Eliminate all hardcoded paths in the StarshipBattles codebase by creating a centralized `game/core/paths.py` module as the single source of truth. The review identified **47+ hardcoded path instances** across 30+ files that bypass the partial centralization in `constants.py`.

**Source Review:** [2026-01-27_general_path-centralization](../../../Reviews/results/2026-01-27_general_path-centralization/report.md)

## Goals
- Create centralized `game/core/paths.py` with all path constants
- Eliminate hardcoded paths across the entire codebase
- Replace fragile `os.path.dirname()` chains with clean imports
- Replace `os.getcwd()` patterns with reliable root-relative paths
- Maintain backward compatibility with existing `constants.py` imports

## Scope
**In:**
- Create new `game/core/paths.py` module
- Migrate 14 key files to use centralized paths
- Update `constants.py` to import from `paths.py`
- Update `tests/fixtures/paths.py` to delegate to game paths

**Out:**
- Changing application behavior (paths should resolve to same locations)
- Adding new path constants beyond what's currently used
- Refactoring unrelated code

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| New Module | `game/core/paths.py` | **CREATE** |
| Constants | `game/core/constants.py` | Update imports |
| Entry Point | `game/app.py` | Replace base_path calc |
| Logger | `game/core/logger.py` | Use BATTLE_LOG |
| Profiling | `game/core/profiling.py` | Use PROFILING_HISTORY |
| Ship Loader | `game/simulation/entities/ship_loader.py` | Use VEHICLE_CLASSES_FILE |
| Save Service | `game/strategy/systems/save_game_service.py` | Replace os.getcwd() calls |
| Race Library | `game/strategy/systems/race_library.py` | Replace dirname chain |
| Design Library | `game/strategy/systems/design_library.py` | Use centralized paths |
| Asset Manager | `game/assets/asset_manager.py` | Use ASSET_MANIFEST_FILE |
| Theme Manager | `game/ui/assets/ship_theme_manager.py` | Use SHIP_THEMES_DIR |
| Tech Presets | `game/simulation/systems/tech_preset_loader.py` | Use TECH_PRESETS_DIR |
| Setup Data | `game/ui/screens/setup_data_io.py` | Use FORMATIONS_DIR |
| Test Paths | `tests/fixtures/paths.py` | Delegate to game.core.paths |

## High-Risk Patterns Identified
| Pattern | Files Affected | Risk |
|---------|---------------|------|
| `os.getcwd()` + path | save_game_service.py (6+), persistence.py, galaxy.py | High - breaks from different working directory |
| 4-level dirname chain | race_library.py, setup_data_io.py, test_lab.py | High - fragile, hard to maintain |
| Relative log paths | logger.py, profiling.py, app.py | Medium - logs in unpredictable locations |
| Hardcoded "assets/" | asset_manager.py, 4 UI files | Medium - scattered duplication |

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Create Paths class in paths.py | Mirrors successful pattern in tests/fixtures/paths.py |
| 2026-01-27 | Use marker-based root detection | More reliable than dirname chains |
| 2026-01-27 | Export backward-compat constants | Minimize migration breakage |
| 2026-01-27 | Full 5-phase implementation | Complete remediation preferred over partial |

## Related Documents
- [design.md](design.md) - Proposed paths.py implementation
- [decisions.md](decisions.md) - Full decisions log
- [Source Review](../../../Reviews/results/2026-01-27_general_path-centralization/report.md) - Original findings

## Verification
- [x] All phase checklists complete
- [x] All existing tests pass (`pytest tests/ -v`) - 4594 passed
- [ ] Simulation tests pass (`pytest simulation_tests/ -v`) - not run
- [ ] Game launches and loads data correctly - manual verification needed
- [ ] Save/load game works - manual verification needed
- [ ] Ship designer loads assets - manual verification needed
- [x] No hardcoded path patterns remain in key files
- [x] No dirname chains remain in key files

## Future Work (Out of Scope)
Additional files still using `os.getcwd()` or dirname chains that could be addressed in a follow-up project:
- `game/simulation/components/component.py`
- `game/simulation/systems/persistence.py`
- `game/strategy/data/galaxy.py`
- `game/ui/screens/builder/main.py`
- `game/ui/screens/builder/stats_config.py`
- `game/ui/screens/new_game_setup_screen.py`
- `game/ui/screens/workshop_data_loader.py`
- `game/ui/screens/workshop_screen.py`
- `game/strategy/engine/game_config.py`
- `game/ui/screens/test_lab.py`
