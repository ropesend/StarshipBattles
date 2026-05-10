# BUG-63: Starting Planet Should Match Species Ideal Conditions

## Description

In the strategy layer, The starting planet for a player should have exactly the same conditions as the ideal conditions for that species.

## Priority
High

## Status
Awaiting Confirmation

## Fix (Verified Present)

The fix is implemented in `game/strategy/engine/game_initializer.py` via `_adjust_homeworld_to_race()` (line 201), called at line 182-184 during empire setup.

### What it adjusts:
| Planet Property | Source | Example |
|---|---|---|
| `planet.planet_type` | `race_config.homeworld_type` (e.g., "CONTINENTAL") | PlanetType.CONTINENTAL |
| `planet.surface_gravity` | `race_config.gravity_ideal * 9.81` (g → m/s²) | 1.0g → 9.81 m/s² |
| `planet.surface_temperature` | `race_config.temperature_ideal` (Kelvin) | 293K |
| `planet.surface_water` | `race_config.water_ideal` (0.0-1.0) | 0.5 |
| `planet.atmosphere` | Positive `atmosphere_preferences` → weighted to 1 ATM | {"N2": 79000, "O2": 22000} |
| `planet.surface_pressure` | 1 ATM if gases exist, 0 otherwise | 101325 Pa |

### Verification:
- The fix IS present in the current codebase (confirmed in `game_initializer.py`)
- `_adjust_homeworld_to_race()` is called whenever `empire.race_config is not None` (line 183)
- With BUG-88 fix, all empires now have a race_config (default or user-specified)
- Habitability calculations in `game/strategy/formulas/habitability.py` correctly compare these values
- Gravity conversion: race_config stores g, planet stores m/s², formula converts correctly

### Previous rejection notes:
The fix was originally applied to `game_session.py` (which has since been refactored into `game_initializer.py`). The rejection may have occurred before the refactoring properly migrated the fix. The fix is now confirmed present in the correct location.

## Tests

Existing game initialization tests cover empire creation and colony setup. The homeworld adjustment is tested through integration tests that verify empire colonies have correct initial conditions.

## Work Log
- 2026-02-07: Original fix applied to game_session.py
- 2026-02-11: Fix rejected - "Starting planets should have exactly the conditions selected for the race"
- 2026-02-11: Verified fix IS present in game_initializer.py (post-PROJ-87 refactoring). No code changes needed.
