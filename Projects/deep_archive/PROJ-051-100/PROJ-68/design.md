# PROJ-68: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Existing Systems

**Planet Model** (`game/strategy/data/planet.py`):
- Has `surface_area` (m²), `surface_gravity` (m/s²), `surface_temperature` (K), `surface_water` (0-1), `atmosphere` dict, `planet_type` enum
- Has `owner_id`, `construction_queue`, `facilities`, `resources`
- Has `to_dict()`/`from_dict()` serialization
- **NO population data currently** — colonies are binary (owned or not)

**RaceConfig** (`game/strategy/data/race_config.py`):
- Environmental tolerances: `gravity_ideal/tolerance`, `temperature_ideal/tolerance`, `water_ideal/tolerance`, `atmosphere_preferences`, `radiation_tolerance`
- Population aptitudes: `aptitude_population_growth` (1-10), `aptitude_happiness` (1-10), `aptitude_tolerance_other_species`
- **NOT stored on Empire at runtime** — only `flag_id`/`portrait_id` propagate

**Empire** (`game/strategy/data/empire.py`):
- `colonies: List[Planet]`, `fleets: List[Fleet]`
- Serialization stores `colony_ids`, resolves via `galaxy.get_planet_by_id()` on load

**Resource System** (`game/simulation/components/abilities/resources.py`):
- `ResourceStorage`: `resource_type`, `max_amount`, `STAT_BINDINGS` for modifiers
- `ResourceConsumption`: `resource_type`, `amount`, `trigger`
- `ShipStatsCalculator` aggregates in Phase 3
- `Ship.resources = ResourceRegistry` tracks current state
- `ShipInstance.resource_levels` tracks strategic-layer state (only non-defaults)
- Fleet has atomic consume methods (verify all before consuming any)
- **This is the model pattern for the new CargoStorage ability**

**Colony Pods / Colonization**:
- `ColonizePlanet` ability is a simple marker (planet_type string)
- `FleetOrderProcessor.process_colonize()` creates colony, removes colony ship
- `ColonizeValidator` validates pod availability

**Turn Engine** (`game/strategy/engine/turn_engine.py`):
- 100 subtick loop: Phase 0 (resources), Phase 1 (instant orders), Phase 2-3 (movement), Phase 4 (combat)
- End-of-turn: colonize/join orders processed
- Production phase after subturn loop
- DI pattern: all engines injected via constructor, lazy property creation

**Fleet Orders**:
- `OrderType` enum: MOVE, COLONIZE, MOVE_TO_FLEET, JOIN_FLEET
- `FleetOrder` with type and target
- `FleetOrderProcessor` handles order lifecycle

## Key Patterns to Reuse

- **ResourceStorage pattern** (`game/simulation/components/abilities/resources.py:151-189`): Template for `CargoStorage` ability — `STAT_BINDINGS`, `sync_data()`, `recalculate()`, `get_ui_rows()`
- **Ability registry pattern** (`game/simulation/components/abilities/__init__.py:56-103`): Add to `ABILITY_REGISTRY` dict, import, `create_ability()` factory
- **TurnEngine DI pattern** (`game/strategy/engine/turn_engine.py:83-178`): Optional param in `__init__`, lazy property for default creation
- **Interface pattern** (`game/strategy/interfaces/engines.py`): ABC with abstract methods, added to `__all__`
- **Fleet atomic operations** (`game/strategy/data/fleet.py`): Verify-all-then-consume pattern for fleet-level resource/cargo operations
- **ShipInstance state tracking** (`game/strategy/data/ship_instance.py`): `resource_levels` tracks only non-default values, `cargo_contents` should follow same pattern
- **DTO factory pattern** (`game/strategy/facade/dto/planet_dto.py:38-57`): `@classmethod from_planet()` factory on frozen dataclass

## Architecture

### Population Data Model
```
Planet
├── populations: List[SpeciesPopulation]
│   ├── race_id: str
│   ├── count: int (1 unit = 1,000 people)
│   └── happiness: float (0.0 - 1.0)
├── max_population: int (computed from surface_area)
└── total_population: int (computed sum)

Empire
└── race_config: Optional[RaceConfig]
```

### Cargo System Architecture
```
Component JSON → CargoStorage ability → ShipStatsCalculator aggregation
                                              ↓
                                    stats['cargo_storage'] dict
                                              ↓
ShipInstance.cargo_contents ←→ load_cargo() / unload_cargo()
                                              ↓
Fleet.load_cargo_to_fleet() / unload_cargo_from_fleet()
```

### Population Growth Pipeline
```
Per Turn:
  For each empire:
    For each colony:
      For each species population:
        1. habitability = score_planet_for_race(colony, race_config)
        2. K = max_population * habitability (effective carrying capacity)
        3. r = aptitude_to_growth_rate(aptitude_population_growth)
        4. growth = r * P * (1 - P/K) * happiness
        5. P_new = P + growth (clamped ≥ 0)
```

### Habitability Scoring
```
Factors (each 0.0 - 1.0):
  gravity_score   = linear_falloff(planet_g, ideal_g, tolerance_g)
  temp_score      = linear_falloff(planet_temp, ideal_temp, tolerance_temp)
  water_score     = linear_falloff(planet_water, ideal_water, tolerance_water)
  atmosphere_score = weighted_gas_compatibility(planet_atmo, race_prefs)
  radiation_score  = magnetic_field_vs_tolerance(mag_field, rad_tolerance)

Final = geometric_mean(factors) → 0.0 to 1.0
```

### TRANSFER Order Flow
```
UI → IssueTransferCommand → GameSession dispatch
  → FleetOrder(TRANSFER, target={direction, cargo_type, amount, planet_id})
  → End-of-turn: FleetOrderProcessor.process_transfer()
    → TransferValidator.validate()
    → Load: colony.pop.count -= N, fleet.load_cargo('passengers', N)
    → Unload: fleet.unload_cargo('passengers', N), colony.pop.count += N
```

## Dependencies & Risks
1. **Planet serialization backward compat** — `from_dict()` must handle missing `populations` key for old saves. Mitigation: default to empty list
2. **Empire serialization** — Adding `race_config` to Empire.to_dict() increases save file size. Mitigation: Only serialize if present
3. **ShipStatsCalculator changes** — Must not break existing resource aggregation. Mitigation: Add cargo as separate accumulator, comprehensive tests
4. **Multi-species complexity** — Per-species happiness + growth is more complex than single-species. Mitigation: Start simple (empire's own race only), extensible later
5. **TRANSFER order target serialization** — FleetOrder.target is polymorphic (HexCoord, Planet, Fleet, dict). Mitigation: Add dict handler to to_dict()/from_dict()

## Opportunities Discovered
- Habitability scoring can later drive colony mood, rebellion, and economic output
- Cargo system is foundation for trade routes, supply lines, and logistics gameplay
- Population data enables workforce requirements for production (future project)
- Per-species happiness enables diplomacy mechanics (tolerance_other_species)
