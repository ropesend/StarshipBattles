# BUG-63: Starting Planet Should Match Species Ideal Conditions

## Description

In the strategy layer, The starting planet for a player should have exactly the same conditions as the ideal conditions for that species.

## Priority
High

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** `_setup_initial_scenario()` in `game_session.py` assigned the first planet as homeworld without adjusting its conditions to match the species' environmental preferences. A Magma-loving species could end up on an Earth-like planet.

**Changes:**

1. **`game/strategy/engine/game_session.py`**:
   - Added `_adjust_homeworld_to_race(planet, race_config)` static method
   - Called before `empire.add_colony()` when empire has a race_config
   - Adjusts:
     - `planet.planet_type` from `race_config.homeworld_type` (e.g., CONTINENTAL, MAGMA)
     - `planet.surface_gravity` = `race_config.gravity_ideal * 9.81` (g to m/s^2)
     - `planet.surface_temperature` = `race_config.temperature_ideal` (Kelvin)
     - `planet.surface_water` = `race_config.water_ideal` (0.0-1.0)
     - `planet.atmosphere` built from positive atmosphere preferences, distributed across 1 ATM total pressure
     - `planet.surface_pressure` = 1 ATM (if any atmosphere gases) or 0 (if none)

**Result:** Starting planets now have conditions matching the species' ideal environment, ensuring 100% habitability from the start.

**Tests:** All 341 strategy/gameplay tests pass (294 strategy integration + 27 gameplay loop + 20 game session).

---
### ❌ Fix Rejected [2026-02-11 00:00]
**Reason:** Starting planets should have exactly the conditions that are selected for the race at the start of the game, the homeworld should be ideal.
**New Constraints:** None provided beyond the original requirement.
---
