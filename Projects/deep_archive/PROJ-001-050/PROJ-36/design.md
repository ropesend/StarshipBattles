# PROJ-36: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Source:** Code review finding - TurnEngine is a "Transitional God Class" that still orchestrates too much directly despite delegating some tasks to specialized engines.

**Current TurnEngine (479 lines):**
| Responsibility | Methods | Lines | Status |
|----------------|---------|-------|--------|
| Turn orchestration | `process_turn`, `_process_tick` | ~30 | Keep (core role) |
| Movement | delegates to `FleetMovementEngine` | - | Done (PROJ-12) |
| Production | delegates to `ProductionEngine` | - | Done (PROJ-12) |
| Order processing | delegates to `FleetOrderProcessor` | - | Done (PROJ-12) |
| **Combat resolution** | 5 methods | ~145 | **To extract** |
| **Resource consumption** | 2 methods | ~70 | **To extract** |
| **Colonize validation** | 1 method | ~40 | **To extract** |
| Legacy wrappers | 3 methods | ~20 | **To remove** |

## Swarm Findings Summary

Combined analysis from 6 specialized agents exploring the codebase.

### Architecture Analysis

**Directory Structure:**
```
game/strategy/
├── adapters/           # Layer bridging (strategy-simulation)
├── data/               # Pure domain models
├── engine/             # Orchestration & turn processing (TurnEngine lives here)
├── interfaces/         # Abstract contracts (IBattleResolver)
├── services/           # Stateless calculations
├── systems/            # Specialized subsystems
└── validation/ (NEW)   # Order validation (to be created)
```

**Existing Engine Pattern:**
- Engines are stateless - all state in empires/fleets/planets
- Lazy initialization via properties on TurnEngine
- Dependency injection for cross-layer concerns (IBattleResolver)
- No common ISubSystem interface (explicit delegation works well at current scale)

### Key Patterns to Reuse

- **Lazy Initialization**: `game/strategy/engine/turn_engine.py:90-112` - Property-based lazy init
- **Result Dataclasses**: `game/strategy/engine/fleet_order_processor.py` - `JoinFleetResult`, `ColonizeResult`
- **Validation Rule Pattern**: `game/simulation/validation/base.py` - `ValidationRule` ABC with template method
- **Dependency Injection**: `game/strategy/engine/turn_engine.py:67-83` - IBattleResolver injection

### Dependencies & Risks

**Combat Methods Dependencies:**
- `IBattleResolver` - interface for clean strategy-simulation separation
- `SimulationBattleResolver` - default implementation (lazy loaded)
- `random` module - for RNG fallback when fleets are empty
- `game.core.logger` - for combat logging

**Resource Methods Dependencies:**
- `game.core.registry.get_component_registry()` - component definitions
- `game.strategy.services.ship_stats_service.ShipStatsService` - resource calculation
- Ship design_data, component_damage, component_toggles

**Validation Dependencies:**
- `galaxy.get_planets_at_global_hex()` - O(1) spatial lookup
- `game.core.validation.ValidationResult` - return type

**Circular Dependency Risks: MINIMAL**
- All dependencies flow downward (engine → data, engine → services)
- No upward dependencies to UI layer
- IBattleResolver uses interface pattern to break cycles

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Combat state inconsistency (3+ empires) | HIGH | Add explicit multi-empire test |
| Resource depletion mid-tick cascade | HIGH | Log all auto-disables, add cascade test |
| Validation stale between UI and execution | MEDIUM | Document point-in-time semantics |
| IBattleResolver null during combat | MEDIUM | Keep lazy init with default |
| Empty fleet combat semantics | MEDIUM | Add edge case tests |

### Test Impact Analysis

**Test Files Affected:**
- `tests/unit/strategy/test_turn_engine.py` (1,207 lines) - PRIMARY, needs splitting
- `tests/strategy/test_turn_engine_strategy.py` (933 lines) - Integration tests
- `tests/integration/test_gameplay_loop.py` - Full turn cycle
- `tests/integration/test_colonization.py` - Colonization workflow

**Test Migration Plan:**
- Combat tests (15+) → `test_conflict_resolution_engine.py`
- Resource tests (17+) → `test_resource_management_engine.py`
- Validation tests (7+) → `tests/unit/strategy/validation/test_colonize_validator.py`
- Orchestration tests (~6) → Keep in `test_turn_engine.py`

### Data Flow Analysis

**Turn Processing Order (Critical - Do Not Change):**
```
Tick 1-100:
├─ Phase 0: Per-turn resource consumption (1/100th)
├─ Phase 1: Instant orders (JOIN_FLEET)
├─ Phase 2: Calculate movements
├─ Phase 3: Apply movements
└─ Phase 4: Resolve combat

End-of-Turn:
├─ Static orders (COLONIZE)
└─ Production
```

**State Mutations by Extracted Methods:**

| Method | Reads | Mutates |
|--------|-------|---------|
| `_resolve_conflicts` | fleet.location, fleet.ships | fleet.ships, empire.fleets |
| `_resolve_combat_simulated` | fleet.ships | ship.current_hp, component_damage, resource_levels |
| `_process_per_turn_resources` | ship.design_data | ship.resource_levels, component_toggles |
| `validate_colonize_order` | galaxy spatial index | (none - read only) |

### Opportunities Discovered

1. **Consolidated Resource Management**: Could centralize ALL resource consumption (per-turn + movement + warp) in ResourceManagementEngine
2. **Event-Based Combat Reporting**: Could add combat events for UI, logging, AI
3. **Order Validation Pipeline**: Could expand validation module for all order types
4. **Engine Lifecycle Hooks**: Could add hooks for mods/extensibility

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

**Key Decisions Made:**
1. Remove legacy wrapper methods (clean break)
2. Create `game/strategy/validation/` module (follows simulation pattern)
3. Keep explicit delegation (no ISubSystem interface)
4. Keep IBattleResolver injection pattern
