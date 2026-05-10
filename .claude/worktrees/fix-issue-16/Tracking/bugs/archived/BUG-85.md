# BUG-85: New game colonies report 0 population instead of max

## Description

Colonies at the start of a new game are now reporting 0 population. It should be maxed out.

## Priority
High

## Status (Awaiting Confirmation)

## Work Log

### Fix Applied (2026-02-11)

**Root Cause:** `NewGameSetupScreen.build_game_config()` created `PlayerConfig` with `race_id` but never passed the `race_config` object. Without `race_config`, the population seeding in `GameInitializer._setup_initial_scenario()` was skipped entirely (guarded by `if empire.race_config is not None`).

Additionally, the seeded population was hardcoded to 10,000 units instead of using `max_population`.

**Changes:**

1. **`game/ui/screens/new_game_setup_screen.py`** (line 618):
   - Added `race_config=race` to the `PlayerConfig` constructor so the full race configuration flows through to empire initialization

2. **`game/strategy/engine/game_initializer.py`** (line 172):
   - Changed initial population from hardcoded `count=10000` to `count=home_planet.max_population` so colonies start at full capacity

3. **`tests/unit/ui/test_new_game_setup.py`**:
   - Added `TestNewGameSetupRaceConfig` class with 2 tests verifying race_config propagation

4. **`tests/unit/strategy/engine/test_population_seeding.py`**:
   - Updated `test_home_colony_has_initial_population` to assert `total_population == max_population`

**Tests:** All 21 affected tests pass.
