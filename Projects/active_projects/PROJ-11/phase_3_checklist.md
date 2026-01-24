# PROJ-11 Phase 3: Strategy-UI Separation

## Phase Overview
Remove UI imports from strategy layer and establish clean boundaries.

## Tasks

### Move has_warp_capability to Strategy Services
- [ ] Create or update `game/strategy/services/ship_capability_service.py`
- [ ] Move `has_warp_capability()` function from `fleet_report_filters.py`
- [ ] Update `game/strategy/data/fleet.py` to import from services
- [ ] Update `game/ui/screens/fleet_report_filters.py` to import from services (or call directly)
- [ ] Test warp capability checks

### Create Fleet Query Service
- [ ] Create `game/strategy/services/fleet_query_service.py`
- [ ] Move any other fleet filtering/query logic from UI
- [ ] Update UI to use service

### Move Constants to Core
- [ ] Move `PLANET_RESOURCES` from `game/strategy/data/planet.py` to `game/core/constants.py`
- [ ] Update all imports:
  - [ ] `game/strategy/data/planet.py`
  - [ ] `game/simulation/entities/ship_stats.py`
  - [ ] Any other files importing PLANET_RESOURCES
- [ ] Verify no simulation imports from strategy

### Remove Circular Import Workarounds
- [ ] Review `game/app.py` lazy imports
- [ ] Review `game/simulation/entities/ship_serialization.py` local imports
- [ ] Review `game/strategy/data/ship_instance.py` local imports
- [ ] Restructure modules if needed to eliminate late imports
- [ ] Document any remaining late imports that are intentional

### Address STRAT-004: Battle Resolution Coupling
- [ ] Review TurnEngine.resolve_battle() method
- [ ] Consider creating IBattleResolver interface (Phase 4)
- [ ] At minimum, document the coupling

## Verification
- [ ] Run: `grep -r "from game.ui" game/strategy/` returns nothing
- [ ] Run: `grep -r "import game.ui" game/strategy/` returns nothing
- [ ] Strategy tests pass without UI initialized
- [ ] No circular import warnings at startup
