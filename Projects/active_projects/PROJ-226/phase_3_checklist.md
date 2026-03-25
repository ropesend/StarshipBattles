# PROJ-226 Phase 3: Engine & Service Consolidation

## DUP-SE-003/004: Spawn Logic Consolidation
- [ ] Identify duplicated fleet/ship spawn logic in:
  - `game/strategy/engine/production_engine.py`
  - `game/strategy/engine/conflict_resolution_engine.py`
- [ ] Extract a shared fleet spawner utility
- [ ] Update both engines to use the shared utility
- [ ] Verify production and conflict resolution tests pass

## DUP-SE-006: JOIN_FLEET Handling Consolidation
- [ ] Map all JOIN_FLEET handling across:
  - `game/strategy/engine/fleet_order_processor.py`
  - `game/strategy/engine/command_handlers.py`
  - `game/strategy/engine/turn_engine.py`
  - `game/strategy/engine/game_session.py`
  - `game/strategy/data/fleet.py`
  - `game/strategy/interfaces/engines.py`
- [ ] Consolidate into a single authoritative handler
- [ ] Update all call sites and interfaces
- [ ] Verify fleet order tests pass

## DUP-SE-007: Registries Initialization Consolidation
- [ ] Audit duplicated registry initialization across 7 engine files:
  - `game/strategy/engine/resupply_engine.py`
  - `game/strategy/engine/resource_management_engine.py`
  - `game/strategy/engine/production_engine.py`
  - `game/strategy/engine/maintenance_engine.py`
  - `game/strategy/engine/harvesting_engine.py`
  - `game/strategy/engine/game_session.py`
  - `game/strategy/engine/empire_economy_calculator.py`
- [ ] Extract shared initialization pattern (base class or helper)
- [ ] Update all engine files
- [ ] Verify DI and initialization tests pass

## DUP-SS-01: Population Extraction
- [ ] Identify duplicated population logic in `game/strategy/services/cargo_transfer_service.py`
- [ ] Extract to a shared population utility
- [ ] Update cargo transfer service
- [ ] Verify cargo transfer tests pass

## DUP-SS-02: Superweapon Validation Consolidation
- [ ] Identify duplicated validation in:
  - `game/strategy/validation/superweapon_validator.py`
  - `game/strategy/engine/superweapon_command_handlers.py`
- [ ] Consolidate validation to `superweapon_validator.py` as single authority
- [ ] Update command handlers to delegate to validator
- [ ] Verify superweapon tests pass

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 3 items verified
