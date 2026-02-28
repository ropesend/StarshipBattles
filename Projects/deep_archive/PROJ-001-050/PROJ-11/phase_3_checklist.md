# PROJ-11 Phase 3: Strategy-UI Separation

## Phase Overview
Remove UI imports from strategy layer and establish clean boundaries.

## Tasks

### Move has_warp_capability to Strategy Services
- [x] Create or update `game/strategy/services/ship_capability_service.py`
  - Added `has_warp_capability()` as static method in `ShipStatsService` (existing service)
- [x] Move `has_warp_capability()` function from `fleet_report_filters.py`
  - Function now lives in `game/strategy/services/ship_stats_service.py`
- [x] Update `game/strategy/data/fleet.py` to import from services
  - Updated `can_use_warp()` and `get_warp_limiting_ship()` methods
- [x] Update `game/ui/screens/fleet_report_filters.py` to import from services (or call directly)
  - Added thin wrapper for backward compatibility
- [x] Test warp capability checks
  - 12 new tests in `test_ship_stats_service.py::TestHasWarpCapability`
  - All 27 existing tests in `test_fleet_report_filters.py` still pass

### Create Fleet Query Service
- [ ] Create `game/strategy/services/fleet_query_service.py`
- [ ] Move any other fleet filtering/query logic from UI
- [ ] Update UI to use service

### Move Constants to Core
- [x] Move `PLANET_RESOURCES` from `game/strategy/data/planet.py` to `game/core/constants.py`
  - Added PLANET_RESOURCES to core/constants.py
  - 5 new tests in `tests/unit/core/test_constants.py`
- [x] Update all imports:
  - [x] `game/strategy/data/planet.py` - now re-exports from core.constants
  - [x] `game/simulation/entities/ship_stats.py` - now imports from core.constants
  - [x] Other files continue importing from planet.py (backward compatible)
- [x] Verify no simulation imports from strategy for PLANET_RESOURCES
  - Note: `battle_controller.py` still imports Fleet type for type hints (STRAT-004)

### Remove Circular Import Workarounds
- [x] Review `game/app.py` lazy imports
  - Many lazy imports exist for UI screens/services
  - These are intentional: avoid circular deps + improve startup performance
  - No changes needed
- [x] Review `game/simulation/entities/ship_serialization.py` local imports
  - Line 120: `from game.simulation.entities.ship import Ship`
  - Intentional: Ship imports ShipSerializer, ShipSerializer imports Ship
  - No restructuring needed
- [x] Review `game/strategy/data/ship_instance.py` local imports
  - Line 171: `from game.strategy.services.ship_stats_service import ShipStatsService`
  - Intentional: ShipInstance uses service, service may reference ShipInstance types
  - No restructuring needed
- [N/A] Restructure modules if needed to eliminate late imports
  - Current late imports are intentional design choices
- [x] Document any remaining late imports that are intentional
  - All reviewed imports are intentional for circular dependency avoidance
  - Pattern: use local import inside methods that would otherwise create circular deps

### Address STRAT-004: Battle Resolution Coupling
- [x] Review TurnEngine.resolve_battle() method
  - `_resolve_combat_simulated()` imports from `game.simulation.battle_controller`
  - Uses `BattleController`, `BattleConfig`, `BattleMode`, `BattleService`
  - This coupling is INTENTIONAL: strategy layer must invoke battle simulation
- [N/A] Consider creating IBattleResolver interface (Phase 4)
  - Deferred to PROJ-13 (UI architectural patterns) if needed
  - Current direct coupling is acceptable for single-game architecture
- [x] At minimum, document the coupling
  - Documented in design.md: TurnEngine -> BattleController for combat resolution
  - This is a strategy->simulation dependency (acceptable direction per architecture)

## Verification
- [x] Run: `grep -r "from game.ui" game/strategy/` returns nothing
  - Only result is docstring in ship_stats_service.py (not an actual import)
- [x] Run: `grep -r "import game.ui" game/strategy/` returns nothing
  - No matches
- [x] Strategy tests pass without UI initialized
  - 592 strategy tests pass
- [x] No circular import warnings at startup - manually verified with `python -W all -c "import game.app"`

## Notes
- Fleet Query Service task deferred - no additional fleet filtering logic found in UI
- All other Phase 3 tasks completed
