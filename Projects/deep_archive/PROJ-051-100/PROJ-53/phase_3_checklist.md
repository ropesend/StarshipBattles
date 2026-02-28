# Phase 3: Fix Production Code Breakage

**Objective:** Fix all production code that broke due to legacy pattern removal.

**Prerequisite:** Phase 1-2 complete

**Status:** Complete

---

## Tasks

### 3.1 Fix UI Renderer - Direct Property Access
**File:** `game/ui/renderer/game_renderer.py` (lines 171-177) - Active renderer
**Note:** `renderer.py` was dead code (never imported) and has been deleted.

- [x] Replace `ship.current_fuel` with `ship.resources.get_value('fuel')`
- [x] Replace `ship.max_fuel` with `ship.resources.get_max_value('fuel')`
- [x] Replace `ship.current_energy` with `ship.resources.get_value('energy')`
- [x] Replace `ship.max_energy` with `ship.resources.get_max_value('energy')`
- [x] Replace `ship.current_ammo` with `ship.resources.get_value('ammo')`
- [x] Replace `ship.max_ammo` with `ship.resources.get_max_value('ammo')`
- [x] Handle case where resource doesn't exist (return 0)

### 3.2 Fix Fleet Report Window
**File:** `game/ui/screens/fleet_report_window.py`

- [x] Replace `stats['max_fuel']` with resource-based access
- [x] Replace `stats['total_fuel']` with resource-based access
- [x] Replace `stats['max_energy']` with resource-based access
- [x] Replace `stats['total_energy']` with resource-based access
- [x] Update any other legacy stat keys

### 3.3 Fix Fleet Report Filters
**File:** `game/ui/screens/fleet_report_filters.py`

- [x] Replace hardcoded fuel tracking with resource-based tracking
- [x] Update filter logic to use resources container

### 3.4 Fix Ship Combat Engine - Shield Regen
**File:** `game/simulation/entities/ship_combat_engine.py`

- [x] Refactor shield regen to use ResourceConsumption ability check
- [x] Ensure shield regen respects energy availability

### 3.5 Fix Combat Endurance Calculation
**File:** `game/simulation/entities/combat_endurance.py`

- [x] Calculate consumption rates from ResourceConsumption abilities
- [x] Store results appropriately for UI access

### 3.6 Fix Ship Stats - Legacy Ability Handling
**File:** `game/simulation/entities/ship_stats.py`

- [x] Remove references to legacy ability names
- [x] Ensure all stat aggregation uses modern ability classes
- [x] Remove orphan `strategic_fuel_per_hex` field (Audit cleanup)

### 3.7 Fix Ship Serialization
**File:** `game/simulation/entities/ship_serialization.py`

- [x] Update serialization to use modern patterns
- [x] Remove legacy property serialization (`strategic_fuel_per_hex` removed in Audit cleanup)

### 3.8 Fix Builder Stats Config
**File:** `game/ui/screens/builder/stats_config.py`

- [x] Verify dynamic resource discovery still works
- [x] Update any hardcoded resource name references

### 3.9 Run Production Code Tests
- [x] Run `pytest tests/unit/` - all passing
- [x] Run `pytest tests/integration/` - all passing
- [x] All production-related tests pass

---

## Files Modified
- `game/ui/renderer/game_renderer.py` - Uses modern resource API
- `game/ui/renderer/renderer.py` - DELETED (dead code)
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/fleet_report_filters.py`
- `game/simulation/entities/ship_combat_engine.py`
- `game/simulation/entities/combat_endurance.py`
- `game/simulation/entities/ship_stats.py`
- `game/simulation/entities/ship_serialization.py`
- `game/ui/screens/builder/stats_config.py`

---

## Notes

- `renderer.py` was identified as dead code during audit and deleted
- `strategic_fuel_per_hex` was orphan code (set but never read) and removed during audit cleanup
