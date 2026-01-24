# PROJ-12: Design Document

## Ship Class Decomposition

### Current Structure (750+ lines, 50+ methods)
```
Ship
├── Physics (via PhysicsBody mixin)
│   ├── position, velocity, rotation
│   ├── acceleration, drag
│   └── update_physics()
├── Combat (via ShipCombatMixin)
│   ├── fire_weapons()
│   ├── take_damage()
│   ├── current_target
│   └── solve_lead()
├── Components
│   ├── add_component(), remove_component()
│   ├── get_all_components()
│   ├── layers management
│   └── ability aggregation
├── Formation
│   ├── formation_master, formation_members
│   ├── formation_offset
│   └── formation delegates
├── Stats
│   ├── recalculate_stats()
│   ├── stat caching
│   └── resource management
├── Serialization
│   ├── to_dict(), from_dict()
│   └── migration handling
└── Validation
    ├── check_validity()
    └── get_missing_requirements()
```

### Target Structure
```
Ship (< 200 lines - thin facade)
├── Delegates to:
│   ├── ShipCombatEngine (fire_weapons, take_damage, targeting)
│   ├── ShipComponentManager (add/remove/get components, layers)
│   ├── ShipStatsAggregator (stat calculation, caching)
│   └── ShipFormationController (formation logic)
├── Core data only:
│   ├── id, team_id, class_id
│   ├── position, velocity, rotation (from PhysicsBody)
│   └── is_alive, is_derelict
└── Serialization handled by ShipSerializer service
```

### New Classes

#### ShipCombatEngine
```python
class ShipCombatEngine:
    """Handles all combat-related logic for a ship."""

    def __init__(self, ship: 'Ship', projectile_manager: ProjectileManager):
        self._ship = ship
        self._projectile_manager = projectile_manager

    def fire_weapons(self, targets: List['Ship'], grid: SpatialGrid) -> None:
        """Fire all ready weapons at available targets."""
        # Extracted from Ship.fire_weapons()
        pass

    def process_hangar_launch(self, components: List[Component]) -> None:
        """Launch vehicles from hangars."""
        pass

    def select_target(self, candidates: List['Ship']) -> Optional['Ship']:
        """Select best target from candidates."""
        pass

    def take_damage(self, amount: float, damage_type: str) -> DamageResult:
        """Apply damage to ship, returning result."""
        pass
```

#### ShipComponentManager
```python
class ShipComponentManager:
    """Manages ship components and layers."""

    def __init__(self, ship: 'Ship'):
        self._ship = ship
        self._layers: Dict[LayerType, ComponentLayer] = {}
        self._components: List[Component] = []

    def add_component(self, component: Component) -> ValidationResult:
        """Add component with validation."""
        pass

    def remove_component(self, component: Component) -> bool:
        """Remove component from ship."""
        pass

    def get_components_by_ability(self, ability_type: Type) -> List[Component]:
        """Get all components with specified ability."""
        pass

    def get_layer(self, layer_type: LayerType) -> ComponentLayer:
        """Get specific layer."""
        pass
```

## TurnEngine Decomposition

### Current Structure (737 lines)
```
TurnEngine
├── Movement (_calculate_next_hex, path management)
├── Combat Resolution (RNG and simulated)
├── Resource Consumption (fuel, supplies)
├── Production (construction queue, spawning)
├── Colonization
└── Order Processing
```

### Target Structure
```
TurnEngine (< 200 lines - orchestrator only)
├── Delegates to:
│   ├── FleetMovementEngine (movement, pathfinding, fuel)
│   ├── CombatResolutionEngine (battle orchestration)
│   ├── ProductionEngine (construction, spawning)
│   └── FleetOrderProcessor (order lifecycle)
└── Orchestrates turn phases:
    1. Process movement
    2. Resolve conflicts
    3. Process production
    4. Execute end-turn orders
```

### New Classes

#### FleetMovementEngine
```python
class FleetMovementEngine:
    """Handles fleet movement and resource consumption."""

    def __init__(self, galaxy: Galaxy, mobility_service: FleetMobilityService):
        self._galaxy = galaxy
        self._mobility_service = mobility_service

    def calculate_movement(self, fleet: Fleet, ticks_per_turn: int) -> MovementResult:
        """Calculate fleet movement for the turn."""
        pass

    def apply_movement(self, fleet: Fleet, result: MovementResult) -> None:
        """Apply calculated movement to fleet."""
        pass

    def consume_resources(self, fleet: Fleet, distance: float) -> None:
        """Consume movement resources."""
        pass
```

#### CombatResolutionEngine
```python
class CombatResolutionEngine:
    """Handles combat between fleets."""

    def __init__(self, battle_resolver: IBattleResolver):
        self._battle_resolver = battle_resolver

    def detect_conflicts(self, fleets: List[Fleet]) -> List[Conflict]:
        """Detect fleet conflicts at same location."""
        pass

    def resolve_conflict(self, conflict: Conflict, seed: int) -> BattleResult:
        """Resolve a single conflict."""
        pass
```

## RaceSetupScreen Decomposition

### Current Structure (2,325 lines)
```
RaceSetupScreen
├── UI Rendering
├── Event Handling
├── Race Configuration
├── Validation
├── Asset Preview (portraits, flags, ships, text)
└── RaceBrowserDialog (embedded)
```

### Target Structure
```
RaceSetupScreen (< 500 lines - composition)
├── Uses:
│   ├── RacePreviewRenderer (portrait, flag, ship preview)
│   ├── RaceValidator (validation logic)
│   ├── RaceConfigPanel (configuration controls)
│   └── RaceBrowserDialog (separate file)
└── Coordinates:
    ├── User input → config changes
    ├── Config changes → preview updates
    └── Validation → error display
```

## Testing Strategy

### Unit Tests for New Classes
- ShipCombatEngine: test targeting, damage, weapon firing
- ShipComponentManager: test add/remove, layer management
- FleetMovementEngine: test pathfinding, resource consumption
- CombatResolutionEngine: test conflict detection, resolution

### Integration Tests
- Ship operations still work through facade
- TurnEngine orchestration maintains correct turn phases
- RaceSetupScreen UI flows work correctly

### Regression Tests
- All existing ship tests pass
- All existing turn tests pass
- Save/load compatibility maintained
