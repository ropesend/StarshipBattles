# PROJ-43: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Source Findings
The project addresses 21 architecture layer violations from `findings_01_architecture_layer_violations.md`.

### Previous Project Status
- **PROJ-11 (Architecture Layer Separation)** - Completed: Created IBattleResolver interface, moved PLANET_RESOURCES to core, removed pygame from simulation
- **PROJ-38 (Registry DI Refactor)** - Completed: Created GameRegistries, DI providers, deprecated utility functions

### Exploration Findings

#### Core Layer (VERIFIED CLEAN)
- No imports from strategy/simulation/ui/engine
- protocols.py uses TYPE_CHECKING correctly for HexCoord
- DI pattern implemented via DefaultRegistryProvider and TestRegistryProvider
- Deprecated functions still exist but emit warnings

#### Layer Violations Confirmed
| Layer | Violation Count | Files Affected |
|-------|-----------------|----------------|
| UI → Simulation | 17 imports | 13 files |
| UI → Strategy (direct, bypassing facade) | Multiple | Various |
| Strategy → Simulation | Well-controlled via adapters | - |
| Engine → Simulation | None found | Clean |

#### Circular Dependencies
| Chain | Status | Mitigation |
|-------|--------|------------|
| Fleet ↔ ShipStatsService | Active | Deferred imports |
| Ship ↔ ModifierService | Active | Deferred imports |
| TurnEngine ↔ Sub-engines | Mitigated | Lazy @property |
| Strategy ↔ Simulation | Well-designed | IBattleResolver interface |

#### Global Registry Usage
- `get_component_registry()` - DEPRECATED, still used
- `get_modifier_registry()` - DEPRECATED, still used
- `get_vehicle_classes()` - DEPRECATED, still used
- `.instance()` singleton pattern - 30+ files

## Swarm Findings Summary

### Architecture Patterns Already in Place

1. **StrategySessionFacade** (`game/strategy/facade/strategy_session_facade.py`)
   - CQRS-lite pattern
   - Returns immutable DTOs
   - Should be extended for more operations

2. **IBattleResolver Interface** (`game/strategy/interfaces/battle_resolver.py`)
   - Clean abstraction for battle resolution
   - SimulationBattleResolver implements it
   - TurnEngine uses DI for this

3. **DTO Package** (`game/strategy/facade/dto/`)
   - SystemInfo, PlanetInfo, EmpireInfo, FleetInfo
   - Good pattern to replicate for UI layer

### Key Patterns to Reuse

- **Facade Pattern**: `StrategySessionFacade` - reuse for simulation access
- **Interface Pattern**: `IBattleResolver` - reuse for sub-engine contracts
- **DTO Pattern**: Strategy DTOs - replicate for UI layer
- **DI Pattern**: `TestRegistryProvider` - extend for all services

### Dependencies & Risks

1. **UI-Simulation coupling** - 13 files need updating, risk of breaking UI functionality
   - Mitigation: Create facades incrementally, comprehensive UI tests

2. **TurnEngine refactor** - Converting lazy init to constructor DI
   - Mitigation: Create interfaces first, maintain backward compatibility during transition

3. **Registry deprecation completion** - Many files still use deprecated functions
   - Mitigation: Batch updates with search/replace, verify with tests

### Opportunities Discovered

1. **Reduce deprecation warnings** - 28327 warnings in test suite, many from registry functions
2. **Improve testability** - Full DI enables better unit testing isolation
3. **Cleaner imports** - Package-level __all__ definitions will simplify imports

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Decisions Made During Planning

1. **Full Constructor DI for TurnEngine** - User preference for extensibility over simplicity
2. **Re-verify all previous fixes** - User preference for thoroughness
3. **Split Phase 2 into sub-phases** - User preference for manageable chunks (2A, 2B, 2C)

## New Components to Create

### UI Services Layer (`game/ui/services/`)

```
game/ui/services/
├── __init__.py
├── ship_factory.py          # Factory for Ship creation
├── component_service.py     # Facade for component/modifier access
├── vehicle_class_service.py # Facade for vehicle class data
├── design_service.py        # Facade for design operations
└── battle_ui_service.py     # Interface for battle UI needs
```

### UI Interfaces Layer (`game/ui/interfaces/`)

```
game/ui/interfaces/
├── __init__.py
├── ship_factory.py    # IShipFactory protocol
└── battle_ui.py       # IBattleUI protocol
```

### Strategy Interfaces (Extend existing)

```
game/strategy/interfaces/
├── __init__.py
├── battle_resolver.py     # Existing
├── movement_engine.py     # NEW: IMovementEngine
├── production_engine.py   # NEW: IProductionEngine
├── order_processor.py     # NEW: IOrderProcessor
├── conflict_engine.py     # NEW: IConflictEngine
└── resource_engine.py     # NEW: IResourceEngine
```

### Simulation Interfaces (`game/simulation/interfaces/`)

```
game/simulation/interfaces/
├── __init__.py
├── ai_controller.py       # IAIController protocol
└── modifier_applicator.py # IModifierApplicator protocol
```

## File Modification Summary

### High-Touch Files (5+ changes expected)
- `game/ui/screens/builder/main.py`
- `game/ui/screens/workshop_screen.py`
- `game/core/registry.py`
- `game/strategy/engine/turn_engine.py`
- `game/simulation/entities/ship.py`

### Medium-Touch Files (2-4 changes)
- `game/ui/screens/setup*.py` (3 files)
- `game/ui/screens/builder/*.py` (5 files)
- `game/strategy/data/fleet.py`
- `game/simulation/systems/battle_engine.py`

### Low-Touch Files (1 change)
- Various files for import updates
- __init__.py files for __all__ definitions
