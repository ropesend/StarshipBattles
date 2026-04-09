# Design Patterns Reference

Agent-optimized reference for every core pattern in the codebase (20 patterns).
Each section: **Where**, **How It Works**, **When to Use**.

---

## Table of Contents

1. [ApplicationContext (DI Container)](#1-applicationcontext-di-container--proj-258)
2. [Protocol + TypeGuard](#2-protocol--typeguard)
3. [Dependency Injection (Registry)](#3-dependency-injection-registry)
4. [Registry Pattern](#4-registry-pattern)
5. [Facade / Delegate](#5-facade--delegate)
6. [CQRS-lite (Strategy Session)](#6-cqrs-lite-strategy-session)
7. [CommandHandlerRegistry](#7-commandhandlerregistry)
8. [MVVM (Workshop)](#8-mvvm-workshop)
9. [Template Method (Validation)](#9-template-method-validation)
10. [Event Bus](#10-event-bus)
11. [Surface Caching (SpriteManager)](#11-surface-caching-spritemanager)
12. [Configuration Classes](#12-configuration-classes)
13. [Battle Mode Strategy](#13-battle-mode-strategy)
14. [Two-Phase Ability Aggregation](#14-two-phase-ability-aggregation)
15. [Factory](#15-factory)
16. [ScrollState (Scroll Utility)](#16-scrollstate-scroll-utility)
17. [Serializable Protocol](#17-serializable-protocol)
18. [Per-Battle RNG](#18-per-battle-rng-proj-252)

---

## 1. ApplicationContext (DI Container) — PROJ-258

### Where

- Container: `game/context.py` -- `ApplicationContext`
- Factory methods: `create_production()`, `create_test(**overrides)`
- Composition root: `game/app.py` -- `Game.__init__` creates context

### How It Works

`ApplicationContext` is a dependency injection container holding references to all application
services. Created once at startup (production) or per-test (testing). Passed explicitly to code
that needs service references. **Not a singleton** — the caller manages lifetime.

```python
# game/context.py
class ApplicationContext:
    def __init__(self, registry_manager, profiler, strategy_metadata,
                 component_cache, strategy_manager, asset_manager,
                 sprite_manager, ship_theme_manager, screenshot_manager,
                 game_settings):
        self.registry_manager = registry_manager
        self.profiler = profiler
        # ... all 10 services

    @classmethod
    def create_production(cls) -> 'ApplicationContext':
        """Creates all services directly. Called once from app.py."""
        ...

    @classmethod
    def create_test(cls, **overrides) -> 'ApplicationContext':
        """Creates fresh lightweight instances. Override specific services via kwargs."""
        ...
```

### Services Managed (10 total)

| Service | File | Layer |
|---------|------|-------|
| RegistryManager | `game/core/registry.py` | Core |
| Profiler | `game/core/profiling.py` | Core |
| StrategyMetadataService | `game/core/strategy_metadata.py` | Core |
| ComponentCacheManager | `game/simulation/components/component_loader.py` | Simulation |
| StrategyManager | `game/ai/strategy_manager.py` | AI |
| AssetManager | `game/assets/asset_manager.py` | Assets |
| SpriteManager | `game/ui/renderer/sprites.py` | UI |
| ShipThemeManager | `game/ui/assets/ship_theme_manager.py` | UI |
| ScreenshotManager | `game/ui/services/screenshot_manager.py` | UI |
| GameSettings | `game/ui/services/game_settings.py` | UI |

### How Services Are Accessed

Each service has a module-level `get_default_xxx()` / `set_default_xxx()` accessor pair.
`ApplicationContext.create_production()` creates all instances and sets all module-level
references, ensuring `get_default_xxx()` returns the same instance as `ctx.xxx`.

```python
# Production code — via ApplicationContext (preferred)
ctx = ApplicationContext.create_production()
ctx.profiler.start()

# Production code — via module-level accessor (for decorators, convenience functions)
from game.core.profiling import get_default_profiler
profiler = get_default_profiler()

# Test code — fresh isolated instances
ctx = ApplicationContext.create_test(profiler=mock_profiler)
```

### Legacy: SingletonMeta (Deprecated)

`SingletonMeta` (`game/core/singleton.py`) is retained but **no production code uses it**.
No `.instance()` or `.reset()` methods exist on any of the 10 services.

---

## 2. Protocol + TypeGuard

### Where

`game/core/protocols.py` -- all protocol definitions and TypeGuard functions.

### How It Works

The codebase uses `@runtime_checkable` Protocol classes to define structural interfaces,
paired with TypeGuard functions that use duck typing (hasattr checks) for safe narrowing.

```python
# game/core/protocols.py (actual code)
@runtime_checkable
class IFleet(Protocol):
    @property
    def ships(self) -> List[Any]: ...
    @property
    def orders(self) -> List[Any]: ...
    @property
    def location(self) -> Any: ...
    @property
    def owner_id(self) -> int: ...
    # ... more properties

def _has_attrs(obj: Any, *attrs: str) -> bool:
    return all(hasattr(obj, attr) for attr in attrs)

def is_fleet(obj: Any) -> TypeGuard[IFleet]:
    """Check minimal distinguishing attributes."""
    return _has_attrs(obj, 'ships', 'orders')
```

**Why duck typing?** `isinstance()` with `@runtime_checkable` requires full protocol
compliance, which breaks with test mocks. Duck typing checks only the minimal
distinguishing attributes.

Protocol families (representative subset — see `game/core/protocols.py` for the full list of 23+ protocols):

| Protocol | Distinguishing Attrs | Layer |
|----------|---------------------|-------|
| `IFleet` | `ships`, `orders` | Strategy |
| `IPlanet` | `planet_type` | Strategy |
| `IStarSystem` | `stars`, `planets`, `warp_points` | Strategy |
| `ICombatShip` | `team_id`, `hp`, `is_derelict` | Simulation |
| `IRegistryProvider` | `get_components`, `get_modifiers` | Core |
| `IPostBattleShip` | `hp`, `max_hp`, `is_alive` | Cross-layer boundary |
| `IScene` | `handle_event`, `update`, `draw` | UI |

### When to Use

- Cross-layer boundaries where you cannot import the concrete class.
- Polymorphic code that handles multiple entity types (e.g., rendering fleets vs planets).
- Always pair a Protocol with a TypeGuard function for runtime checks.

---

## 3. Dependency Injection (Registry)

### Where

`game/core/registry.py` -- `IRegistryProvider` (protocol in `protocols.py`),
`DefaultRegistryProvider`, `TestRegistryProvider`, `get_default_registry_provider()`.

### How It Works

Three access modes, from most to least preferred:

**1. Constructor injection (best):**
```python
def __init__(self, registry: IRegistryProvider):
    self._registry = registry
    components = registry.get_components()
```

**2. Factory function (acceptable for leaf code):**
```python
from game.core.registry import get_default_registry_provider
provider = get_default_registry_provider()
```

**3. Direct access (composition roots only):**
```python
mgr = ctx.registry_manager  # Via ApplicationContext
mgr.hydrate(components_data, modifiers_data, vehicle_classes_data)
```

**Production path:** `DefaultRegistryProvider` delegates to module-level RegistryManager:

```python
# game/core/registry.py (actual code)
class DefaultRegistryProvider:
    def get_components(self) -> Dict[str, Any]:
        return get_default_registry_manager().components
```

**Test path:** `TestRegistryProvider` holds isolated data:

```python
# game/core/registry.py (actual code)
class TestRegistryProvider:
    def __init__(self, components=None, modifiers=None, ...):
        self._components = components if components is not None else {}
    def get_components(self) -> Dict[str, Any]:
        return self._components
```

**Ship class requires registries (strict DI):**
```python
# game/simulation/entities/ship.py (actual code)
class Ship(PhysicsBody, ShipPhysicsMixin):
    def __init__(self, name, x, y, color, team_id=0, ship_class="Escort",
                 theme_id="Federation", *, registries: GameRegistries):
        if registries is None:
            raise ValidationException("registries is required ...")
```

**GameRegistries defaults `resource_catalog`:**

`GameRegistries.__post_init__()` automatically provides an empty `ResourceCatalog` when
`resource_catalog=None`. This means callers that don't need resource data (tests, validators)
can omit it without crashing. Production code should always pass the real catalog explicitly:

```python
registries = GameRegistries(
    components=provider.get_components(),
    modifiers=provider.get_modifiers(),
    vehicle_classes=provider.get_vehicle_classes(),
    resources=provider.get_resources(),
    resource_catalog=provider.get_resource_catalog(),  # explicit in production
)
```

**ShipStatsCalculator requires `resource_catalog` for `calculate()`:**

`ShipStatsCalculator` uses lazy resolution — it accepts `resource_catalog` at construction
and resolves planetary resource IDs on first `calculate()` call. Omitting both
`resource_catalog` and `planetary_resource_ids` raises `TypeError` at `calculate()` time.
The `calculate_ability_totals()` method does not require a catalog.

```python
# game/simulation/entities/ship_stats.py
calculator = ShipStatsCalculator(
    registries.vehicle_classes,
    resource_catalog=registries.resource_catalog,
)
calculator.calculate(ship)
```

### Simulation Code Must NOT Use Global Lookup (PROJ-252)

`get_default_registry_provider()` must **never** be called from `game/simulation/` code.
Ship already holds `_registries` (`GameRegistries`, which implements `IRegistryProvider`).
Simulation delegates (ShipComponentManager, ShipValidatorHelper) must use
`self._ship._registries` instead of calling the global factory function.

### When to Use

- All services and domain objects that need component/modifier/vehicle-class data.
- Tests: use `TestRegistryProvider` for isolation; never depend on global service state.

### Critical: Registry Lookup for Facility Ability Checks (PROJ-237/238)

**When checking if a facility/complex has a specific ability, you MUST use registry lookup.**

Facility `design_data` stores components as ID references (`{"id": "generator", "modifiers": [...]}`), **not** with inline abilities. The abilities are defined in `data/components.json` and accessed via the component registry. Checking `comp.get('abilities', {})` directly will silently return empty and miss the ability.

**Correct pattern:**
```python
from game.strategy.services.component_inspector import get_component_abilities
from game.core.registry import get_default_registry_provider

provider = get_default_registry_provider()
comp_registry = provider.get_components()

# For each component in facility.design_data:
comp_id = comp.get('id')
comp_def = comp_registry.get(comp_id)
abilities = get_component_abilities(comp_def)
if 'PlanetaryShield' in abilities:
    # Found it
```

**Anti-pattern (WILL FAIL on loaded designs):**
```python
# WRONG: Only checks inline abilities — these don't exist in loaded designs
if 'PlanetaryShield' in comp.get('abilities', {}):
    pass  # Never reaches here for registry-defined abilities
```

**Helper:** Use `_facility_has_ability(facility, ability_name, component_registry)` from `game/strategy/validation/planet_order_validator.py` — it handles both inline and registry lookup.

**In UI code:** Use `get_default_registry_provider()` (factory function pattern #2 above) to get the registry. Do NOT try to access registries via `scene.facade` — the facade does not expose registries.

### Critical: Unified Stat Calculation (Single Source of Truth)

**All ship/design stat calculations MUST go through the simulation `Ship` object.**

The canonical path is `calculate_design_stats()` in `game/simulation/entities/ship_design_stats.py`, which calls `Ship.from_dict()` + `recalculate_stats()`. This is the ONLY code path for computing stats from design JSON.

**DO NOT:**
- Write new stat calculation code that iterates components and sums abilities manually
- Compute mass, HP, crew, resource storage, or movement by reading component definitions directly
- Create "lightweight" stat calculators that skip Ship instantiation
- Duplicate formula evaluation logic from `ShipStatsCalculator`

**DO:**
- Use `calculate_design_stats(design_data, registries)` for design JSON → stats dict
- Use `ship_instance.get_calculated_stats()` for ShipInstance → stats dict (delegates to above)
- Use `component_inspector.has_warp_capability(ship)` for warp capability checks
- Use `component_inspector.get_ability_list(abilities, name)` for ability data normalization

**Why:** The project previously had two parallel stat calculators (simulation and strategy) that diverged, producing different mass/HP values for the same design. The strategy calculator is now deprecated. One code path prevents future drift.

```python
# Correct: use the canonical function
from game.simulation.entities.ship_design_stats import calculate_design_stats
stats = calculate_design_stats(design_data, registries)

# Correct: use ShipInstance's cached wrapper
stats = ship_instance.get_calculated_stats()

# WRONG: manual component iteration for stat calculation
total_mass = 0
for comp in iter_components(design_data):
    total_mass += comp_registry[comp['id']].mass  # DO NOT DO THIS
```

---

## 4. Registry Pattern

### Where

- `game/core/registry.py` -- `RegistryManager`, `GameRegistries`
- Data files: `data/components.json`, `data/modifiers.json`, `data/vehicleclasses.json`, `data/resources.json`
- `game/core/resources.py` -- `ResourceCatalog`, `ResourceDefinition`

### How It Works

`RegistryManager` (managed by ApplicationContext) holds four dictionaries: `components`, `modifiers`,
`vehicle_classes`, and `resources`. `GameRegistries` is an immutable (`@dataclass(frozen=True)`)
container that bundles these together for DI. It also holds an optional `ResourceCatalog`
which provides typed, immutable access to all resource definitions (both planetary materials
and operational consumables).

```python
# game/core/registry.py (actual code)
@dataclass(frozen=True)
class GameRegistries:
    components: Dict[str, Any]
    modifiers: Dict[str, Any]
    vehicle_classes: Dict[str, Any]
    resources: Dict[str, Any]
    resource_catalog: Optional[ResourceCatalog] = None

    # Also implements IRegistryProvider interface
    def get_components(self) -> Dict[str, Any]:
        return self.components
```

Lifecycle:
1. **Load:** Game startup loads JSON files into `RegistryManager` dictionaries.
2. **Freeze:** `freeze_registry()` prevents accidental mutations during gameplay.
3. **Access:** Consumer code receives `IRegistryProvider` or `GameRegistries` via DI.
4. **Test reset:** `RegistryManager.reset()` destroys the instance; `.clear()` empties data.

### When to Use

- Looking up component definitions, modifier specs, or vehicle class data.

---

## 5. Facade / Delegate

### Where

- **Facade:** `game/strategy/facade/strategy_session_facade.py` -- `StrategySessionFacade`
- **Delegate:** `game/simulation/entities/ship.py` -- Ship delegates combat to `ShipCombatEngine`

### How It Works

**StrategySessionFacade** wraps `GameSession` to provide the UI a clean interface.
The UI never touches `GameSession` directly.

```python
# game/strategy/facade/strategy_session_facade.py (actual code)
class StrategySessionFacade:
    def __init__(self, session: 'GameSession') -> None:
        self._session = session

    # COMMANDS (Write Path)
    def handle_command(self, command: 'Command') -> ValidationResult:
        return self._session.handle_command(command)

    # QUERIES (Read Path) - return DTOs, never domain objects
    def get_fleet(self, fleet_id: int) -> Optional[FleetInfo]:
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return None
        return FleetInfo.from_fleet(fleet)
```

**Ship -> ShipComponentManager delegation:** Ship lazily creates a
`ShipComponentManager` and delegates all component lifecycle operations
(add, remove, bulk add, cache, iteration, layer queries) to it.

**Ship -> ShipCombatManager delegation:** Ship lazily creates a
`ShipCombatManager` and delegates combat orchestration (update loop, derelict
status, death, firing state) to it. The combat manager also owns the
`ShipCombatEngine` as a sub-delegate.

**Ship -> ShipCombatEngine delegation:** Ship's `combat_engine` property
delegates through `ShipCombatManager` which lazily creates a `ShipCombatEngine`.

```python
# game/simulation/entities/ship.py (actual code)
class Ship(PhysicsBody, ShipPhysicsMixin):

    @property
    def combat_engine(self):
        return self.combat_manager.combat_engine
```

**Fleet delegates:** Fleet also uses the delegate pattern to decompose responsibilities:
- `FleetCapabilityCalculator` -- computes fleet-level capabilities from ship components
- `FleetConsumableAggregator` -- aggregates resource totals across all ships in a fleet
- `FleetBattleAdapter` -- adapts fleet data for the combat simulation layer

**ShipInstance delegates:** ShipInstance uses delegation to separate concerns:
- `ShipInstanceBridge` -- conversion between strategy ShipInstance and simulation Ship (`to_ship`, `update_from_ship`)
- `ShipInstanceSerializer` -- serialization/deserialization (`to_dict`, `from_dict`, `clone`)
- `ShipConsumableManager` -- consumable tracking (fuel, energy, ammo)
- `ShipCargoManager` -- cargo loading/unloading
- `ShipDisplayFormatter` -- display string formatting

**Component delegates (PROJ-241):** Component uses 4 delegates with a consistent pattern:
- `ComponentHealthManager` -- HP tracking, damage processing, status updates
- `ComponentResourceManager` -- resource activation costs (check, consume, try_activate)
- `ModifierManager` -- modifier state ownership, add/remove/query, effects aggregation
- `AbilityManager` -- ability instances + MRO index, instantiation, querying, tag-based lookups

All 4 delegates follow the same pattern:
```python
# game/simulation/components/modifier_manager.py (actual code)
class ModifierManager:
    __slots__ = ('_component', '_modifiers')

    def __init__(self, component: 'Component'):
        self._component = component
        self._modifiers: list = []
        self._load_initial_modifiers()
```

Component provides facade properties for backward compatibility:
```python
# game/simulation/components/component.py (actual code)
@property
def modifiers(self):
    """Facade: access modifier list through delegate."""
    return self.modifier_manager.modifiers

@property
def ability_instances(self):
    """Facade: access ability instances through delegate."""
    return self._ability_mgr.ability_instances
```

Note: `ComponentStatsCalculator` remains a static namespace (no state to own).

### When to Use

- **Facade:** Layer boundary needs a simplified, controlled API (UI to engine).
- **Delegate:** Class would become a god class. Extract behavior; original keeps public API.

---

## 6. CQRS-lite (Strategy Session)

### Where

- Facade: `game/strategy/facade/strategy_session_facade.py`
- DTOs: `game/strategy/facade/dto/` (fleet_dto.py, system_dto.py, planet_dto.py, empire_dto.py)
- Commands: `game/strategy/engine/commands.py`

### How It Works

The strategy layer separates reads and writes:

- **Commands (writes):** All state mutations go through `handle_command(Command)`.
  Commands are plain data objects dispatched to handlers.
- **Queries (reads):** Return frozen `@dataclass` DTOs, never live domain objects.

```python
# Write path -- UI sends a command
from game.strategy.engine.commands import IssueMoveCommand
result = facade.handle_command(IssueMoveCommand(fleet_id=42, target_hex=hex))

# Read path -- UI queries for display data
fleet_info: FleetInfo = facade.get_fleet(42)  # Returns frozen DTO
```

DTO example:

```python
# game/strategy/facade/dto/fleet_dto.py (actual code)
@dataclass(frozen=True)
class FleetOrderInfo:
    order_type: str
    target_description: str
    target_hex: Optional[HexCoord] = None
    target_id: Optional[int] = None

@dataclass(frozen=True)
class ShipInfo:
    instance_id: str
    name: str
    design_id: str
    ship_class: str
```

### When to Use

- All UI-to-strategy-engine communication must go through the facade.
- Never expose mutable domain objects to the UI layer.
- Commands should be validated and return `ValidationResult`.

---

## 7. CommandHandlerRegistry

### Where

`game/strategy/engine/command_handlers.py` -- `CommandHandlerRegistry`, `ICommandHandler`,
`BaseCommandHandler`, and all concrete handlers.

### How It Works

Registry-based dispatch replaces a giant switch/if-else in `GameSession`.

```python
# game/strategy/engine/command_handlers.py (actual code)
@runtime_checkable
class ICommandHandler(Protocol):
    def execute(self, session: 'GameSession', command: 'Command') -> ValidationResult: ...

class CommandHandlerRegistry:
    def __init__(self):
        self._handlers: Dict[str, ICommandHandler] = {}

    def register(self, command_name: str, handler: ICommandHandler) -> None:
        self._handlers[command_name] = handler

    def dispatch(self, command_name: str, session, command) -> ValidationResult:
        handler = self._handlers.get(command_name)
        if handler is None:
            return ValidationResult.error(f"Unknown command type: {command_name}")
        return handler.execute(session, command)
```

Handlers extend `BaseCommandHandler` for common resolution helpers:

```python
class ColonizeCommandHandler(BaseCommandHandler):
    def execute(self, session, cmd) -> ValidationResult:
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error
        # ... validation and application
```

Factory creates the default registry with all handlers:

```python
def create_default_registry() -> CommandHandlerRegistry:
    registry = CommandHandlerRegistry()
    registry.register('IssueColonizeCommand', ColonizeCommandHandler())
    registry.register('IssueMoveCommand', MoveCommandHandler())
    # ... 20+ handlers registered
    return registry
```

### When to Use

- Adding a new strategy command: create a handler class, register it in `create_default_registry()`.
- Each handler follows: resolve entities, validate, apply, return `ValidationResult`.

---

## 8. MVVM (Workshop)

### Where

- ViewModel: `game/ui/screens/workshop_viewmodel.py` -- `WorkshopViewModel`
- EventBus: `game/ui/screens/builder/event_bus.py` -- `EventBus`
- Events: `game/ui/screens/builder_utils.py` -- `BuilderEvents`
- Service: `game/simulation/services/vehicle_design_service.py` -- `VehicleDesignService`

### How It Works

The Design Workshop uses Model-View-ViewModel. The ViewModel holds all state, emits
events on changes, and delegates operations to `VehicleDesignService`.

```python
# game/ui/screens/workshop_viewmodel.py (actual code)
class WorkshopViewModel:
    def __init__(self, event_bus, screen_width, screen_height, *, context=None):
        self.event_bus = event_bus
        self._ship_service = VehicleDesignService(...)  # NOT ShipBuilderService
        self._ship: Optional[Ship] = None
        self._selected_components: List[Tuple[LayerType, int, Component]] = []
        self._dragged_item: Optional[Component] = None
```

Data flow:
```
View (panels) --[user action]--> ViewModel --[delegates]--> VehicleDesignService
                                     |
                                     v
                              EventBus.emit(SHIP_UPDATED)
                                     |
                                     v
                          View (panels) refresh via subscription
```

### When to Use

- Complex UI screens with multiple panels sharing state.
- The ViewModel is the single source of truth; views are stateless renderers.
- Always use `VehicleDesignService` (not `ShipBuilderService`) for ship operations.
- **Ship mutations must go through the ViewModel** (e.g., `viewmodel.remove_component()`), never directly on the Ship object. The ViewModel delegates to `VehicleDesignService` which provides validation and result handling, then emits the appropriate events.

---

## 9. Template Method (Validation)

### Where

`game/simulation/validation/base.py` -- `ValidationRule`, `DesignValidationRule`, `AdditionValidationRule`

### How It Works

`ValidationRule` defines the algorithm skeleton. Subclasses override `_do_validate()`
for specific logic and optionally `_should_validate()` to control when the rule runs.

```python
# game/simulation/validation/base.py (actual code)
class ValidationRule(ABC):
    def validate(self, ship, component=None, layer_type=None) -> ValidationResult:
        if not self._should_validate(component, layer_type):
            return ValidationResult.success()
        return self._do_validate(ship, component, layer_type)

    def _should_validate(self, component, layer_type) -> bool:
        return component is not None and layer_type is not None

    @abstractmethod
    def _do_validate(self, ship, component, layer_type) -> ValidationResult:
        pass

class DesignValidationRule(ValidationRule):
    """Always runs -- validates the ship design as a whole."""
    def _should_validate(self, component, layer_type) -> bool:
        return True

class AdditionValidationRule(ValidationRule):
    """Only runs when adding a component (default guard)."""
    pass
```

### When to Use

- Adding a new validation rule: extend `DesignValidationRule` or `AdditionValidationRule`.
- Override `_should_validate()` for custom guard logic (e.g., only for unique components).
- Implement `_do_validate()` with your rule; return `ValidationResult.success()` or `.error(msg)`.

---

## 10. Event Bus

### Where

- Implementation: `game/ui/screens/builder/event_bus.py` -- `EventBus`
- Event constants: `game/ui/screens/builder_utils.py` -- `BuilderEvents`

### How It Works

Simple pub/sub with string event types, defensive copy during emit, and error isolation.

```python
# game/ui/screens/builder/event_bus.py (actual code)
class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        if not callable(callback):
            raise ValidationException(...)
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def emit(self, event_type, data=None):
        if event_type in self._subscribers:
            handlers = list(self._subscribers[event_type])  # Defensive copy
            for callback in handlers:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
```

Event constants:

```python
# game/ui/screens/builder_utils.py (actual code)
class BuilderEvents:
    SHIP_UPDATED = 'SHIP_UPDATED'
    SELECTION_CHANGED = 'SELECTION_CHANGED'
    REGISTRY_RELOADED = 'REGISTRY_RELOADED'
    TEMPLATE_MODIFIERS_CHANGED = 'TEMPLATE_MODIFIERS_CHANGED'
    DRAG_STATE_CHANGED = 'DRAG_STATE_CHANGED'
    HULL_LAYER_VISIBILITY_CHANGED = 'HULL_LAYER_VISIBILITY_CHANGED'
```

**Key detail:** `emit()` passes a single `data` argument (not `*args, **kwargs`).
Subscribers receive one argument: `callback(data)`.

### When to Use

- Decoupling UI panels that need to react to shared state changes.
- Always use string constants from `BuilderEvents`, never raw strings.
- Currently scoped to the Workshop UI; not a general-purpose game event system.

### Strategy-Layer Event Logging (PROJ-252)

`game/core/event_logging.py` provides a separate `EventBus` class for structured
simulation/strategy events. Each `GameSession` creates its own `EventBus` instance,
avoiding process-global mutable state.

```python
# game/core/event_logging.py
class EventBus:
    def __init__(self, handler=None):
        self._handler = handler
    def log_event(self, event_type, **kwargs): ...
```

The module-level `log_event()` function is a backward-compatibility shim. New code
should prefer explicit `EventBus` injection where possible.

---

## 11. Surface Caching (SpriteManager)

### Where

`game/ui/renderer/sprites.py` -- `SpriteManager` (managed by ApplicationContext)

### How It Works

`SpriteManager` loads component sprite images once and caches them by index.
Individual UI panels also maintain local caches for expensive operations
(rotated text, scaled surfaces).

```python
# game/ui/renderer/sprites.py (actual code)
class SpriteManager:
    def __init__(self):
        self.sprites = []
        self.tile_size = 36

    def load_sprites(self, base_path: str = None) -> None:
        # Loads 64px sprites from Paths.COMPONENTS_64_DIR
        # Uses regex to parse {resolution}Portrait_Comp_{number}.png filenames
        if base_path is not None:
            sprite_dir = os.path.join(base_path, "assets", "Images", "Components", "Components 64")
        else:
            sprite_dir = Paths.COMPONENTS_64_DIR
        # ...
```

### When to Use

- Cache: font rendering, surface rotation, surface scaling (all create new surfaces).
- Do not cache: color fills, line drawing (fast, position-dependent).
- Individual panels use `Dict[str, Surface]` caches with `invalidate_cache()` methods.

---

## 12. Configuration Classes

### Where

`game/core/config.py` -- `DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig`

### How It Works

Configuration classes are **plain classes with class-level attributes** (not `@dataclass`).
They use `@classmethod` helpers for common operations.

```python
# game/core/config.py (actual code)
class DisplayConfig:
    """Display and resolution configuration."""
    DEFAULT_WIDTH: int = 3840
    DEFAULT_HEIGHT: int = 2160
    WINDOWED_WIDTH: int = 2560
    WINDOWED_HEIGHT: int = 1600
    TEST_WIDTH: int = 1440
    TEST_HEIGHT: int = 900

    @classmethod
    def default_resolution(cls) -> Tuple[int, int]:
        return (cls.DEFAULT_WIDTH, cls.DEFAULT_HEIGHT)

class AIConfig:
    MIN_SPACING: int = 150
    DEFAULT_ORBIT_DISTANCE: int = 500
    MAX_CORRECTION_FORCE: int = 500
    # ... many more

class PhysicsConfig:
    TICK_RATE: float = 0.01
    DEFAULT_LINEAR_DRAG: float = 0.5

class BattleConfig:
    TARGET_QUERY_RADIUS: int = 200000
    COLLISION_BUFFER: int = 100
```

**Important:** These are NOT `@dataclass(frozen=True)`. They are plain classes used as
namespace containers for constants. Do not add `@dataclass` decorators.

Layout config in `game/ui/screens/builder_utils.py` does use frozen dataclasses for
instantiated layout objects:

```python
@dataclass(frozen=True)
class PanelWidths:
    component_palette: int = 400
    layer_panel: int = 500
PANEL_WIDTHS = PanelWidths()  # Singleton instance
```

### Data-Driven Configs (Strategy Layer)

The strategy layer uses a second config pattern for **JSON-backed tunable parameters** loaded
from `data/astrophysics.json`. These are classes with `DEFAULT_*` dicts, `_load_from_json()`
/ `_use_defaults()` methods, and an `@lru_cache` getter function with graceful fallback.

**Files:**
- `game/strategy/data/classification_config.py` -- `ClassificationConfig` (planet classification thresholds)
- `game/strategy/data/resource_generation_config.py` -- `ResourceGenerationConfig` (resource quantity/quality/affinities)
- `game/strategy/data/star_generation_config.py` -- `StarGenerationConfig` (star type weights, mass distribution, SB type properties)
- `game/strategy/data/orbital_generation_config.py` -- `OrbitalGenerationConfig` (orbital placement, moon system, surface flags)

```python
# game/strategy/data/classification_config.py (actual code, representative)
class ClassificationConfig:
    DEFAULT_MASS = {
        "dwarf_max": 2.0e23,
        "giant_min": 6.0e24,
        "gas_giant_min": 1.0e26,
    }
    # ... more DEFAULT_* dicts

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        if data and "classification" in data:
            self._load_from_json(data["classification"])
        else:
            self._use_defaults()

    def _load_from_json(self, section: Dict[str, Any]) -> None:
        subsection = section.get("mass_thresholds", {})
        self.dwarf_max = subsection.get("dwarf_max", self.DEFAULT_MASS["dwarf_max"])
        # ... each attribute uses .get() with DEFAULT dict fallback

    def _use_defaults(self) -> None:
        self.dwarf_max = self.DEFAULT_MASS["dwarf_max"]
        # ... direct assignment from DEFAULT dicts

@lru_cache(maxsize=1)
def get_classification_config() -> ClassificationConfig:
    try:
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader
        loader = AstrophysicsLoader()
        data = loader.load()
        return ClassificationConfig(data)
    except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.warning(f"Failed to load classification config: {e}")
        return ClassificationConfig(None)  # Falls back to hardcoded defaults
```

Key characteristics:
- `@lru_cache(maxsize=1)` — singleton; loads once per process
- **Late import** of `AstrophysicsLoader` inside the getter (avoids circular imports)
- **Broad exception handling** — catches all likely loading failures, falls back to defaults
- **Tests must call `get_*_config.cache_clear()`** in setup/teardown to prevent pollution
- Consumers import the getter via late import inside methods (e.g., `planet_gen.py` line 458)

### When to Use

- **Core config (static):** Game-engine constants that never change at runtime (AI, Physics, Battle, Display). Use plain classes in `game/core/config.py`.
- **Strategy data-driven config (JSON-backed):** Gameplay tuning parameters loaded from `astrophysics.json`. Use the `@lru_cache` getter pattern in `game/strategy/data/*_config.py`.
- **UI layout config:** Frozen dataclasses with singleton instances.
- Always import from the config module, never inline magic numbers.

---

## 13. Battle Mode Strategy

### Where

`game/simulation/combat/battle_mode_handler.py` -- `BattleModeHandler` ABC and four concrete handlers.

### How It Works

The Strategy pattern eliminates mode-specific conditionals in `BattleController`.
Each battle mode (Manual, Test, Strategy, Hypothetical) has a dedicated handler.

```python
# game/simulation/combat/battle_mode_handler.py (actual code)
class BattleModeHandler(ABC):
    @abstractmethod
    def configure(self, controller, config) -> None: ...
    @abstractmethod
    def can_retreat(self) -> bool: ...
    @abstractmethod
    def can_reinforce(self) -> bool: ...
    @abstractmethod
    def should_clone_ships(self) -> bool: ...
    @abstractmethod
    def is_headless_default(self) -> bool: ...
    @abstractmethod
    def apply_results(self, controller, results) -> None: ...
```

Concrete handlers:

| Handler | Retreat | Reinforce | Clone | Headless | Effects |
|---------|---------|-----------|-------|----------|---------|
| `ManualBattleModeHandler` | No | No | No | No | None |
| `TestBattleModeHandler` | No | No | No | Yes | None |
| `StrategyBattleModeHandler` | Yes | Yes | No | Yes | Fleet updates |
| `HypotheticalBattleModeHandler` | No | No | Yes | Yes | None |

Factory function selects the handler:

```python
def get_handler_for_mode(mode: BattleMode) -> BattleModeHandler:
    handlers = {
        BattleMode.MANUAL: ManualBattleModeHandler,
        BattleMode.TEST: TestBattleModeHandler,
        BattleMode.STRATEGY: StrategyBattleModeHandler,
        BattleMode.HYPOTHETICAL: HypotheticalBattleModeHandler,
    }
    return handlers[mode]()
```

### When to Use

- Adding a new battle mode: create a handler, add it to the factory dict.
- Never add mode-specific if/else branches in `BattleController`.

---

## 14. Two-Phase Ability Aggregation

### Where

`game/simulation/entities/ability_aggregator.py` -- `calculate_ability_totals()`,
`_aggregate_ability_groups()`

### How It Works

Abilities on ship components support stacking groups. Aggregation is two-phase:

1. **Intra-group (MAX):** Within the same named stack group, take the highest value.
   This models redundancy -- two sensors in the same group do not stack.
2. **Inter-group (SUM):** Across different groups, sum the contributions.

Marker abilities (`CommandAndControl`, `Armor`, etc.) use boolean True semantics
instead of numeric aggregation.

```python
# game/simulation/entities/ability_aggregator.py
MARKER_ABILITIES = {'CommandAndControl', 'Armor', 'RequiresCommandAndControl', ...}

def _aggregate_ability_groups(ability_groups):
    totals = {}
    for ability_name, groups in ability_groups.items():
        group_contributions = []
        for key, values in groups.items():
            nums = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if nums:
                group_contributions.append(max(nums))          # Phase 1: MAX within group
            elif any(v is True for v in values):
                group_contributions.append(True)

        if not group_contributions:
            continue

        first = group_contributions[0]
        if isinstance(first, bool):
            totals[ability_name] = True
        else:
            totals[ability_name] = sum(                        # Phase 2: SUM
                v for v in group_contributions if isinstance(v, (int, float))
            )
    return totals
```

### When to Use

- Calculating effective ship stats from components.
- All numeric abilities use SUM across groups by default.
  Add to `MARKER_ABILITIES` for boolean presence checks.
- Stack groups are defined in component JSON via the `stack_group` field.
- **PROJ-253:** `FleetAuraManager._recalculate()` now delegates to `_aggregate_ability_groups()` instead of reimplementing the two-phase logic. Any new aggregation code must use the shared function.

---

## 15. Factory

### Where

- `game/ai/ai_factory.py` -- `AIControllerFactory`
- `game/ui/services/ship_factory.py` -- `ShipFactory`
- `game/ui/widgets/panel_factory.py` -- `PanelFactory`

### How It Works

Factory classes encapsulate object creation logic, hiding constructor complexity and
configuration details from callers. They are used throughout the codebase where object
construction requires assembling dependencies, applying defaults, or selecting concrete
implementations.

### When to Use

- Object creation requires non-trivial setup, dependency resolution, or conditional logic.
- Callers should not need to know concrete implementation details.
- Centralizes construction so changes to dependencies propagate from one place.

---

## 16. ScrollState (Scroll Utility)

### Where

- Implementation: `game/ui/widgets/scroll_state.py` -- `ScrollState`
- Tests: `tests/unit/ui/widgets/test_scroll_state.py`
- Consumers: `results_panel.py`, `test_run_details.py`, `dialogs.py`, `json_viewer.py`, `scrollable_json_panel.py`, `modifier_impact_grid.py`, `battle_panels.py`, `setup_screen.py`, `battle_state_viewer.py`

### How It Works

`ScrollState` encapsulates the common scroll_offset + MOUSEWHEEL handling pattern into a reusable utility. It manages offset tracking, clamping, mousewheel events, and scroll ratio calculation for scrollbar positioning.

```python
from game.ui.widgets.scroll_state import ScrollState

# In __init__:
self.scroll = ScrollState(step=20)

# When content changes:
self.scroll.content_height = total_content_height
self.scroll.viewport_height = visible_area_height
self.scroll.clamp()

# In event handler:
if event.type == pygame.MOUSEWHEEL:
    if self.scroll.handle_mousewheel(event):
        return True  # consumed

# In draw method:
y = start_y - self.scroll.offset

# For scrollbar thumb positioning:
thumb_y = track_y + int(self.scroll.scroll_ratio * available_range)
```

Works with both pixel-based scrolling (default) and line-based scrolling (set content_height to line count, viewport_height to visible line count, step to lines per scroll tick).

### When to Use

- Any UI panel or widget that needs vertical scrolling with MOUSEWHEEL support.
- Replaces the ad-hoc `self.scroll_offset = 0; self.max_scroll = 0` pattern.
- Do NOT use for zoom handling (camera) or scrollbar-driven scrolling (pygame_gui widgets).

---

## 17. Serializable Protocol

### Where

- Protocol: `game/core/protocols.py` -- `ISerializable`
- Tests: `tests/unit/core/test_serializable_protocol.py`
- Implementors: `ComponentState`, `ShipState`, `ProjectileState`, `BattleState`, `BattleResults` in `game/simulation/battle_state.py`; `ShipInstance` via `ShipInstanceSerializer` in `game/strategy/data/ship_instance_serializer.py`

### How It Works

`ISerializable` is a `@runtime_checkable` Protocol that defines the `to_dict()` / `from_dict()` contract. It exists for **type checking only** -- there is no mixin or base class, because each implementor has domain-specific serialization logic.

```python
@runtime_checkable
class ISerializable(Protocol):
    def to_dict(self) -> Dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ISerializable': ...
```

### When to Use

- Use as a type annotation when a function accepts any serializable object.
- Do NOT create a mixin. Each class implements its own `to_dict()`/`from_dict()`.

---

## 18. Per-Battle RNG (PROJ-252)

### Where

`game/simulation/systems/battle_engine.py` -- `BattleEngine.rng`,
`game/engine/collision.py` -- `CollisionSystem.rng`,
`game/simulation/combat/damage_calculator.py` -- `DamageCalculator.rng`,
`game/strategy/engine/conflict_resolution_engine.py` -- `ConflictResolutionEngine._rng`

### How It Works

Each `BattleEngine.start(seed=N)` creates a per-instance `random.Random(seed)`.
This RNG is propagated to subsystems (`CollisionSystem`, `DamageCalculator`).
The global `random` module is **never** seeded by simulation code.

```python
# BattleEngine.start()
self.rng = random.Random(seed)
self.collision_system.rng = self.rng
```

`ConflictResolutionEngine` has its own `self._rng = random.Random()` for
strategy-layer randomness (empire pairing in multi-empire conflicts).

### When to Use

- All combat randomness (hit rolls, damage distribution, fighter spawn offsets)
  must use the battle's `self.rng`, never `random.random()`.
- Strategy-layer randomness uses its own `Random` instance.
- **Never** call `random.seed()` from simulation or strategy code.

---

## 19. Error Boundary (Turn Engine — PROJ-251)

**Where:** `game/strategy/engine/turn_engine.py`, `game/strategy/engine/turn_state_snapshot.py`

**How It Works:**
1. `TurnStateSnapshot.capture()` serializes all empires + galaxy via `to_dict()` before each turn
2. `_time_phase()` wraps each sub-engine call — any exception becomes `EnginePhaseError`
3. `process_turn()` catches `EnginePhaseError`, restores from snapshot, dumps crash file, re-raises
4. `GameSession.process_turn()` catches `EnginePhaseError` for UI notification

**When to Use:** Whenever a complex operation involves multiple sequential mutations that must succeed atomically. The snapshot-and-rollback pattern is more practical than full transactional semantics when the state graph is complex.

**Key Classes:** `TurnStateSnapshot`, `EnginePhaseError`

---

## 20. Precondition Validation (Sub-Engines — PROJ-251)

**Where:** All 14 sub-engines in `game/strategy/engine/`

**How It Works:**
Each sub-engine has `_validate_tick_inputs(empires)` called at the start of its tick method. Checks for null references, missing attributes, and impossible values. Raises `ValidationException` with context dict identifying the broken entity.

**When to Use:** At the entry point of any method that mutates state based on external inputs. Validates preconditions before any mutations occur, so the error boundary (pattern 19) gets a clear, descriptive exception rather than a cryptic `AttributeError`.

**Key Pattern:**
```python
def _validate_tick_inputs(self, empires):
    from game.core.exceptions import ValidationException
    for empire in empires:
        for fleet in empire.fleets:
            if fleet.location is None:
                raise ValidationException(
                    f"Empire {empire.id}: fleet '{fleet.id}' has None location",
                    context={"empire_id": empire.id, "fleet_id": fleet.id}
                )
```

---

## Quick Reference

| Pattern | Primary File | Key Class/Function |
|---------|-------------|-------------------|
| ApplicationContext (DI) | `game/context.py` | `ApplicationContext` |
| Singleton (deprecated) | `game/core/singleton.py` | `SingletonMeta` |
| Protocol+TypeGuard | `game/core/protocols.py` | `IFleet`, `is_fleet()` |
| DI (Registry) | `game/core/registry.py` | `DefaultRegistryProvider`, `TestRegistryProvider` |
| Registry | `game/core/registry.py` | `RegistryManager`, `GameRegistries` |
| Facade | `game/strategy/facade/strategy_session_facade.py` | `StrategySessionFacade` |
| Delegate | `game/simulation/entities/ship_combat_engine.py` | `ShipCombatEngine` |
| Delegate | `game/simulation/components/modifier_manager.py` | `ModifierManager` |
| Delegate | `game/simulation/components/ability_manager.py` | `AbilityManager` |
| Delegate | `game/simulation/components/component_health_manager.py` | `ComponentHealthManager` |
| Delegate | `game/simulation/components/component_resource_manager.py` | `ComponentResourceManager` |
| CQRS-lite | `game/strategy/facade/` | Commands + DTOs |
| CommandHandler | `game/strategy/engine/command_handlers.py` | `CommandHandlerRegistry` |
| MVVM | `game/ui/screens/workshop_viewmodel.py` | `WorkshopViewModel` |
| Template Method | `game/simulation/validation/base.py` | `ValidationRule` |
| Event Bus | `game/ui/screens/builder/event_bus.py` | `EventBus`, `BuilderEvents` |
| Surface Cache | `game/ui/renderer/sprites.py` | `SpriteManager` |
| Config Classes | `game/core/config.py` | `DisplayConfig`, `AIConfig`, `PhysicsConfig` |
| Battle Mode | `game/simulation/combat/battle_mode_handler.py` | `BattleModeHandler` |
| Ability Aggregation | `game/simulation/entities/ability_aggregator.py` | `calculate_ability_totals()` |
| Factory | `game/ai/ai_factory.py`, `game/ui/services/ship_factory.py` | `AIControllerFactory`, `ShipFactory`, `PanelFactory` |
| ScrollState | `game/ui/widgets/scroll_state.py` | `ScrollState` |
| Serializable | `game/core/protocols.py` | `ISerializable` |
| Error Boundary | `game/strategy/engine/turn_state_snapshot.py` | `TurnStateSnapshot`, `EnginePhaseError` |
| Precondition Validation | `game/strategy/engine/*.py` | `_validate_tick_inputs()` |

### Critical Naming Reminders

- Ship inherits `(PhysicsBody, ShipPhysicsMixin)` -- **no ShipCombatMixin**.
- Config classes in `game/core/config.py` are **plain classes, not dataclasses**.
- Use **BattleScreen / StrategyScreen**, not BattleScene / StrategyScene.
- Use **VehicleDesignService**, not ShipBuilderService.
- **ScreenshotManager** is at `game/ui/services/screenshot_manager.py`.
- **StrategyManager** is at `game/ai/strategy_manager.py`.
- **EventBus** is at `game/ui/screens/builder/event_bus.py`.
