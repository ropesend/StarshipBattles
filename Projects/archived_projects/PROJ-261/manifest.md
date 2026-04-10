# PROJ-261 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `tests/unit/entities/test_ship.py` | Test | 1 | Rename shadowed TestHullAutoEquip at line 276 |
| `tests/unit/strategy/facade/test_strategy_session_facade.py` | Test | 1 | Rename shadowed TestGameStateQueries at line 695 |
| `tests/unit/strategy/generation/density/test_geometric.py` | Test | 2 | Remove `or True` at line 86 |
| `tests/unit/strategy/generation/density/test_spiral_arm.py` | Test | 2 | Remove `or True` at line 78 |
| `tests/unit/strategy/generation/density/test_layout_loader.py` | Test | 2 | Remove `or True` at line 150 |
| `game/strategy/systems/save_game_service.py` | Production | 3 | Fix `json.JSONDecodeError` to `JSONDecodeError` at line 463 |
| `tests/unit/strategy/systems/test_save_game_service.py` | Test | 3 | Add test for JSONDecodeError handling (if not already covered) |
| `game/research/data/research_tracker.py` | Production | 4 | Add allocation clamping in `set_rp_budget()` at line 206 |
| `tests/unit/research/test_research_tracker.py` | Test | 4 | Add test for budget reduction clamping |

## Conflict Notes

- **No file is touched by more than one phase.** Phases can safely run in parallel if needed.
- Phase 1 and Phase 2 only modify test files -- zero production code risk.
- Phase 3 modifies one production file with a one-line fix.
- Phase 4 modifies one production file and one test file.
