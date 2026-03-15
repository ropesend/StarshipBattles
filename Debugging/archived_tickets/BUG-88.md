# BUG-88: Empire Population tab blank - missing species information cards

## Description
The Population tab in the Empire Overview should show all of the information about each species in the empire. Currently there is no mechanism to have more than 1 but the underlying code should allow for multiple species cards when there is more than one species. Right now the screen is blank and it should at least provide the species information from the start of the game.

## Priority
**High** - Significant feature broken (entire tab is blank/non-functional)

## Status (Awaiting Confirmation)

## Root Cause
The Population tab checks `empire.race_config` and shows "No species data available" when it's None. The Empire gets its `race_config` from `PlayerConfig.race_config`, which is only set when the user explicitly selects or creates a race during game setup. If the user starts a game without going through race setup, `race_config` is None and the tab is blank.

The rendering code itself (portrait, flag, identity, aptitudes, environment, descriptions) was already implemented and correct — it just never ran because `race_config` was always None for the common game start path.

## Fix
**`game/strategy/engine/game_initializer.py`**: In `_create_empires()`, when `player_cfg.race_config` is None, create a default `RaceConfig` using the player's name and theme. This ensures every empire always has race data for the Population tab to display.

The default RaceConfig uses:
- `race_id=f"empire_{i}"` — unique identifier
- `name`, `faction_name`, `race_name` — from player name
- `theme_id` — from player theme
- `flag_id`, `portrait_id` — from player config (may be empty)
- All other fields use RaceConfig defaults (Earth-like environment, 50 aptitudes, etc.)

## Tests Added
- `test_empire_always_has_race_config` — empires without explicit race_config get a default
- `test_empire_preserves_explicit_race_config` — empires with explicit race_config keep it

## Work Log
- Traced the flow: PlayerConfig.race_config -> Empire.race_config -> _build_population_tab check
- Identified that race_config is None when user doesn't configure a race in game setup
- Added default RaceConfig creation in _create_empires() for missing race configs
- All 18 initializer tests pass
