# PROJ-354: Superweapon Spec Table Dependencies

## 1. SuperweaponOrderProcessor Method Callers

**Dispatch Location**: C:/Dev2/StarshipBattles/game/strategy/engine/order_processor.py:707-724  
All six methods (process_implode_planet, process_stellerate_star, process_open_warp_point, process_close_warp_point, process_create_dyson_sphere, process_self_destruct) are invoked via a handler registry dict in `OrderProcessor.execute_action_order()`:
- Lines 707-714: IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT
- Lines 719-724: CREATE_DYSON_SPHERE, SELF_DESTRUCT

**Command Handlers**: C:/Dev2/StarshipBattles/game/strategy/engine/superweapon_command_handlers.py  
ImplodePlanetCommandHandler, StellerateStarCommandHandler, OpenWarpPointCommandHandler, CloseWarpPointCommandHandler, CreateDysonSphereCommandHandler, SelfDestructCommandHandler validate orders via SuperweaponValidator then emit to fleet order queue (lines 40-150+).

**Tests**: C:/Dev2/StarshipBattles/tests/unit/strategy/engine/test_superweapon_order_processor.py  
Directly invoke processor methods in test classes.

## 2. Action Execution Engine → Processor Dispatch

**ActionExecutionEngine → OrderProcessor**  
C:/Dev2/StarshipBattles/game/strategy/engine/action_execution_engine.py:215  
When action order progress reaches action_time, ActionExecutionEngine._execute_action() delegates to OrderProcessor.execute_action_order(). OrderProcessor then dispatches via handler registry (order_processor.py:707-724) to SuperweaponOrderProcessor methods.

**No direct dispatch of OrderType enum values in ActionExecutionEngine** — the engine is order-agnostic; OrderProcessor's superweapon_handlers dict maps OrderType → processor method.

## 3. SuperweaponValidator.find_ship_with_ability() Call Sites

- **Validation**: C:/Dev2/StarshipBattles/game/strategy/validation/superweapon_validator.py:47 (in _require_ability, lines 36-54)
- **Processor**: C:/Dev2/StarshipBattles/game/strategy/engine/superweapon_order_processor.py
  - Line 180: DestroyPlanet (process_implode_planet)
  - Line 360: OpenWarpPoint (process_open_warp_point)
  - Line 479: CloseWarpPoint (process_close_warp_point)
  - Line 564: CreateDysonSphere (process_create_dyson_sphere)
  - Note: DestroyStar/Stellerate uses system_destroyer, SelfDestruct has no ability check

## 4. Event Types Emitted by Superweapons

**Definitions**: C:/Dev2/StarshipBattles/game/strategy/events/event_types.py:6-18
- PLANET_DESTROYED (line 13)
- STAR_DESTROYED (line 14)
- WARP_POINT_OPENED (line 15)
- WARP_POINT_CLOSED (line 16)
- DYSON_SPHERE_CREATED (line 17)
- SHIPS_SELF_DESTRUCTED (line 18)

**Emission**: C:/Dev2/StarshipBattles/game/strategy/engine/superweapon_order_processor.py
- Line 204: PLANET_DESTROYED (process_implode_planet)
- Line 277: STAR_DESTROYED (process_stellerate_star, via system_destroyer)
- Line 395: WARP_POINT_OPENED (process_open_warp_point)
- Line 497: WARP_POINT_CLOSED (process_close_warp_point)
- Line 646: DYSON_SPHERE_CREATED (process_create_dyson_sphere)
- Line 715: SHIPS_SELF_DESTRUCTED (process_self_destruct)

**Event Log Consumers**:
- C:/Dev2/StarshipBattles/game/strategy/events/event_log.py (EventLog.append)
- C:/Dev2/StarshipBattles/game/ui/screens/event_log_data_source.py (event log UI)
- C:/Dev2/StarshipBattles/game/simulation/replay/replay_capture.py (ReplayCaptureContext for replay persistence)

## 5. Stabilizer-Superweapon Blocking Relationships

**Registry**: C:/Dev2/StarshipBattles/game/strategy/services/stabilizer_registry.py:54-70

| Stabilizer Ability | Blocks |
|---|---|
| GeologicStabilizer (lines 55-59) | IMPLODE_PLANET |
| StellarStabilizer (lines 60-64) | STELLERATE_STAR, CREATE_DYSON_SPHERE |
| WarpFieldStabilizer (lines 65-69) | OPEN_WARP_POINT, CLOSE_WARP_POINT |

**Enforcement**: C:/Dev2/StarshipBattles/game/strategy/engine/superweapon_order_processor.py
- Lines 166, 248, 335, 451, 544 call _check_blocking_stabilizer (lines 731-754)
- _check_blocking_stabilizer delegates to find_blocking_stabilizer in stabilizer_registry.py:73-119

## 6. Hardcoded Ability Name Definitions

All six superweapon ability classes defined in C:/Dev2/StarshipBattles/game/simulation/components/abilities/superweapons.py:
- **DestroyPlanet** (lines 64-70): weapon_name = 'Planet Imploder'
- **DestroyStar** (lines 73-79): weapon_name = 'Stellerator'
- **OpenWarpPoint** (lines 82-88): weapon_name = 'Warp Point Creator'
- **CloseWarpPoint** (lines 91-97): weapon_name = 'Warp Point Closer'
- **CreateDysonSphere** (lines 100-107): weapon_name = 'Dyson Sphere Constructor'
- **SelfDestruct** (lines 110-116): weapon_name = 'Self-Destruct Device'

All inherit from SuperweaponMarker (lines 25-61), marked for STRATEGIC layer, SELF scope, action_time parsing (line 49).

## 7. Component Registry Data Location

**Loader**: C:/Dev2/StarshipBattles/game/simulation/components/component_loader.py  
load_components_data() and load_components() populate registries at app startup.

**Registry Access**: C:/Dev2/StarshipBattles/game/strategy/engine/superweapon_command_handlers.py:58, 80, 102, 128, 157  
session.registries.components passed to SuperweaponValidator for ability lookups.

**Ability Class Mapping**: C:/Dev2/StarshipBattles/game/simulation/components/abilities/__init__.py  
Imports DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct from superweapons.py; registry maps component_id → ability class instances.

---

**Summary**: Superweapons flow from command handlers → validator → order queue → ActionExecutionEngine → OrderProcessor.execute_action_order() → SuperweaponOrderProcessor dispatch (registry dict pattern). Stabilizers block orders via find_blocking_stabilizer. Events (PLANET_DESTROYED, etc.) routed to EventLog and replay capture. All ability names tied to superweapons.py class definitions.
