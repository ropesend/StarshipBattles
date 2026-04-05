# PROJ-237 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/components/abilities/planetary.py` | Production (NEW) | 3 new ability classes |
| `game/simulation/components/abilities/__init__.py` | Production | Register 3 abilities in ABILITY_REGISTRY |
| `data/components.json` | Data | Add 3 new component definitions |
| `game/strategy/data/planet.py` | Production | Add energy/shield/order fields, order methods, serialization |
| `game/strategy/data/planetary_facility.py` | Production | Add component_states dict and helpers |
| `game/strategy/data/planet_order_types.py` | Production (NEW) | PlanetOrderType enum + PlanetOrder dataclass |
| `game/strategy/engine/planet_energy_engine.py` | Production (NEW) | Per-tick energy generation/consumption engine |
| `game/strategy/engine/planet_action_engine.py` | Production (NEW) | Per-tick planet order execution engine |
| `game/strategy/services/planet_action_time_resolver.py` | Production (NEW) | Resolve action_time from ability data |
| `game/strategy/interfaces/engines.py` | Production | Add IPlanetEnergyEngine, IPlanetActionEngine |
| `game/strategy/engine/turn_engine.py` | Production | Wire 2 new engines, add 2 phases |
| `game/strategy/engine/superweapon_order_processor.py` | Production | Shield blocking check in process_implode_planet |
| `game/strategy/engine/planet_command_handlers.py` | Production (NEW) | Command handlers for planet orders |
| `game/strategy/engine/commands.py` | Production | Add 3 planet command dataclasses |
| `game/strategy/engine/command_handlers.py` | Production | Register planet command handlers |
| `game/strategy/validation/planet_order_validator.py` | Production (NEW) | Validation for planet orders |
| `game/strategy/events/event_types.py` | Production | Add shield/energy event types |
| `game/core/protocols.py` | Production | Update IPlanet with energy/shield properties |
| `game/strategy/facade/dto/planet_dto.py` | Production | Add energy/shield fields to PlanetInfo |
| `game/ui/screens/strategy_detail_fmt.py` | Production | Shield/energy display in format_planet_info() |
| `game/strategy/quickstart_builder.py` | Production | Add qs_shield_complex to INITIAL_COMPLEXES |
| `tests/fixtures/quickstart/designs/qs_shield_complex.json` | Test Fixture (NEW) | Starting complex design |
| `tests/unit/simulation/components/abilities/test_planetary_abilities.py` | Test (NEW) | Ability class tests |
| `tests/unit/strategy/data/test_planet_order_types.py` | Test (NEW) | PlanetOrder tests |
| `tests/unit/strategy/engine/test_planet_energy_engine.py` | Test (NEW) | Energy engine tests |
| `tests/unit/strategy/engine/test_planet_action_engine.py` | Test (NEW) | Planet action engine tests |
| `tests/unit/strategy/engine/test_planet_command_handlers.py` | Test (NEW) | Command handler tests |
| `tests/unit/strategy/services/test_planet_action_time_resolver.py` | Test (NEW) | Action time resolver tests |
| `tests/unit/strategy/validation/test_planet_order_validator.py` | Test (NEW) | Validator tests |
| `tests/integration/strategy/test_planet_shield_integration.py` | Test (NEW) | Full lifecycle integration test |
