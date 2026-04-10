# PROJ-266 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `tests/unit/ui/screens/test_battle_results_screen.py` | Test | 1 | New file: tests for BattleResultsScreen |
| `tests/unit/ui/screens/test_new_game_setup_extended.py` | Test | 2 | New file: extended tests for NewGameSetupScreen UI state |
| `tests/unit/test_lab/test_renderer_pure_functions.py` | Test | 3 | New file: tests for renderer and test_run_details pure logic |

## Production Files Read (not modified)

| File | Phase | Read For |
|------|-------|----------|
| `game/ui/screens/battle_results_screen.py` | 1 | Source under test |
| `game/ui/screens/battle_results_data.py` | 1 | Dataclass fixtures |
| `game/ui/screens/new_game_setup_screen.py` | 2 | Source under test |
| `game/strategy/engine/game_config.py` | 2 | THEME_DEFAULTS, GameConfig, PlayerConfig |
| `game/strategy/data/race_config.py` | 2 | RaceConfig for mock fixtures |
| `game/ui/screens/test_lab/renderer.py` | 3 | Source under test |
| `game/ui/screens/test_lab/test_run_details.py` | 3 | Source under test |
| `game/ui/screens/test_lab/formatting_utils.py` | 3 | Used by test_run_details |

## Conflict Notes

- **This is a test-only project.** Zero production files are modified.
- **No file is touched by more than one phase.** All three phases create independent test files.
- **Phases can safely run in parallel** if needed -- no shared state, no shared files.
- Phase 1 tests read from `game/ui/screens/battle_results_screen.py` and `battle_results_data.py`
- Phase 2 tests read from `game/ui/screens/new_game_setup_screen.py`
- Phase 3 tests read from `game/ui/screens/test_lab/renderer.py` and `test_run_details.py`
