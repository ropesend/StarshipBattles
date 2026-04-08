# PROJ-224 Phase 1: Bug Fixes

## DUP-SYS-004: Team-Alive Counting Fix
- [x] Read `game/simulation/systems/battle_engine.py` — find `is_battle_over()` and `get_winner()`
- [x] Identify the derelict handling difference between the two methods
- [x] Extract a shared `_count_alive_teams()` helper method
- [x] Update both `is_battle_over()` and `get_winner()` to use the shared helper
- [x] Write/update tests to verify consistent derelict handling
- [x] Run `pytest tests/ -n 12` — all pass

**Notes:** Bug confirmed: `get_winner()` ignored `check_derelict` setting. Created `_count_alive_teams()` helper that respects `end_condition.check_derelict`. Both `is_battle_over()` and `get_winner()` now use it. Added 4 tests in `TestTeamAliveCountingConsistency` class.

## Completion
- [x] All items above checked off
- [x] Tests pass
