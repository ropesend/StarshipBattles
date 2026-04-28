# Design Patterns Reference

> **Last verified:** 2026-04-28 — PROJ-318 verified `ApplicationContext` manages 10 services including the PROJ-314 `ImageProvider`; PROJ-313 superseded Pattern #30 (Registrar Close-Callback) with structural enforcement via the new `StrategyModalWindow` base class (Pattern #31 below). Pattern count is 31.

Agent-optimized reference for every core pattern in the codebase (31 patterns).
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
13. [Spec Compiler + run_battle](#13-spec-compiler--run_battle-replaces-battle-mode-strategy)
14. [Two-Phase Ability Aggregation](#14-two-phase-ability-aggregation)
15. [Factory](#15-factory)
16. [ScrollState (Scroll Utility)](#16-scrollstate-scroll-utility)
17. [Serializable Protocol](#17-serializable-protocol)
18. [Per-Battle RNG](#18-per-battle-rng-proj-252)
19. [Error Boundary](#19-error-boundary-turn-engine--proj-251)
20. [Precondition Validation](#20-precondition-validation-sub-engines--proj-251)
21. [Screen State Machine](#21-screen-state-machine-proj-259)
22. [TurnEngineConfig](#22-turnengineconfig-proj-259)
23. [Tick Phase Registry](#23-tick-phase-registry-proj-259)
24. [External-Stats Bridge](#24-external-stats-bridge-proj-270-phase-9--proj-271)
25. [Scope-Driven Team Routing](#25-scope-driven-team-routing-proj-271)
26. [Ability-Stat Registry](#26-ability-stat-registry-proj-273)
27. [Budget-Aware Randomization](#27-budget-aware-randomization-feat-12)
28. [Background Service Call](#28-background-service-call-proj-296)
29. [Universal Ability Source (PROJ-300..305)](#29-universal-ability-source-proj-300305)
30. [Registrar Close-Callback (BUG-121) — SUPERSEDED](#30-registrar-close-callback-bug-121)
31. [Strategy Modal Window Base Class (PROJ-313)](#31-strategy-modal-window-base-class-proj-313)

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
    def __init__(self, registry_manager, profiler,
                 component_cache, policy_manager, asset_manager,
                 sprite_manager, ship_theme_manager,
                 game_settings, llm_provider, image_provider):
        self.registry_manager = registry_manager
        self.profiler = profiler
        self.llm_provider = llm_provider
        self.image_provider = image_provider
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
| ComponentCacheManager | `game/simulation/components/component_loader.py` | Simulation |
| PolicyManager | `game/ai/policy_manager.py` | AI |
| AssetManager | `game/assets/asset_manager.py` | Assets |
| SpriteManager | `game/ui/renderer/sprites.py` | UI |
| ShipThemeManager | `game/ui/assets/ship_theme_manager.py` | UI |
| GameSettings | `game/ui/services/game_settings.py` | UI |
| LLMProvider | `game/services/llm/provider.py` | Services |
| ImageProvider | `game/ui/services/image/provider.py` | UI |

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

### Removed: SingletonMeta

`SingletonMeta` and `game/core/singleton.py` were removed by PROJ-297. No
current production service uses `.instance()` / `.reset()` singleton access;
new service wiring goes through `ApplicationContext`, constructor injection,
or the documented module-level `get_default_*` / `set_default_*` accessor pair.

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

## 8. MVVM (Workshop & Build Queue)

### Where

- **Design Workshop:**
    - ViewModel: `game/ui/screens/workshop_viewmodel.py` -- `WorkshopViewModel`
    - EventBus: `game/ui/screens/builder/event_bus.py` -- `EventBus`
- **Build Queue Screen:**
    - Controller (Business Logic): `game/ui/panels/build_queue_controller.py` -- `BuildQueueController`
    - Renderer (View Management): `game/ui/screens/build_queue_renderer.py` -- `BuildQueueRenderer`
    - Panel Factory: `game/ui/screens/build_queue_panel_factory.py` -- `BuildQueuePanelFactory`
    - Drag Handler: `game/ui/panels/build_queue_drag_handler.py` -- `BuildQueueDragHandler`

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

### ViewModel Operations

Beyond basic CRUD (add/remove/change class), the ViewModel provides higher-level
operations that compose service calls with layer resolution logic:

| Method | Purpose |
|--------|---------|
| `quick_add_component(component_id, selected_layer?, count?)` | Add via "+" button — auto-resolves target layer |
| `resolve_target_layer(component, selected_layer?)` | Pure logic: find best layer for a component |
| `move_component(source_layer, index, target_layer)` | Move a single component between layers |
| `move_component_group(group_key, source_layer, target_layer)` | Move all components in a group between layers |
| `resolve_move_target(component, source_layer, direction)` | Find next valid layer in up/down direction |
| `on_modifier_changed()` | Called after any modifier change — syncs multi-selection, recalculates ship stats |

**Quick-add layer resolution** (used by component palette "+" button):
1. If `selected_layer` is valid for the component → use it
2. If `selected_layer` is invalid → find nearest valid layer (prefer inner on ties)
3. If no selection → use innermost valid layer
4. HULL is never a quick-add target

**Component movement** between layers uses remove + re-add of the same instance,
preserving modifiers and state. The ViewModel resolves the target layer direction
(up = toward inner, down = toward outer), skipping layers that reject the component.

**Stats panel visibility** is data-driven via `data/stats_sections.json`:
- Each section declares visibility rules (`"always"`, `ability_present`, or `dynamic`)
- `always_visible` block per vehicle type overrides ability checks (e.g., Ships always show maneuvering)
- `resolve_section_visibility()` in `stats_config.py` resolves which sections to display
- Section headers are collapsible (click to toggle)

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

## 13. Spec Compiler + `run_battle` (replaces "Battle Mode Strategy")

### Where

- `game/simulation/battle_runner.py` — `run_battle(spec) -> BattleOutcome`
- `game/simulation/battle_spec.py` — frozen `BattleSpec` DTO
- `game/simulation/battle_outcome.py` — frozen `BattleOutcome` DTO
- Three context-specific compilers:
  - `combat_lab/spec_compiler.py::build_test_battle_spec`
  - `game/ui/screens/battle_setup/spec_compiler.py::build_manual_battle_spec`
  - `game/strategy/combat/spec_compiler.py::build_strategy_battle_spec`

### How It Works

Every battle goes through ONE entry point: `run_battle(spec)`. The
engine is context-blind. Variance lives on `BattleSpec` fields
(`boundary`, `end_condition`, `modifier_stack`, `telemetry_level`,
`post_battle_hook`) rather than in a mode switch.

```
caller domain inputs (TestScenario / BattleSetupState / Fleets)
        │
        ▼
context-specific spec compiler (build_*_battle_spec)
        │
        ▼
BattleSpec (frozen DTO)
        │
        ▼
run_battle(spec, ai_factory, ship_builder, ...)  ──► BattleOutcome
                                                          │
                                                          ▼
                                       spec.post_battle_hook(outcome)
```

This pattern replaces the deleted **Battle Mode Strategy** (PROJ-269
Phase 6 removed `BattleModeHandler` + 4 concrete handlers + the
`get_handler_for_mode(BattleMode)` factory).

### When to Use

- Adding a new battle context: create a `build_*_battle_spec()`
  compiler that translates your domain inputs into a `BattleSpec`. The
  compiler lives in YOUR layer (Combat Lab / Battle Setup / Strategy /
  …). Call `run_battle(spec, ...)`.
- Adding a new variance dimension that crosses contexts: add a field to
  `BattleSpec` and consume it from the engine. Do NOT introduce a mode
  switch.
- Adding a context-specific post-battle side effect: attach a
  `post_battle_hook` closure on the spec.

### Why it replaced the Strategy pattern

| Old "mode" trait | New `BattleSpec` field / mechanism |
|------------------|-----------------------------------|
| `can_retreat` | `BoundaryRegion(exit_policy=RETREAT)` |
| `can_reinforce` | `BattleConfig.allow_reinforcements` (visual mode only) |
| `should_clone_ships` | Caller's `ship_builder` returns a clone |
| `is_headless_default` | Driver choice: blocking `run_battle(spec)` vs per-frame `BattleController.start_from_spec(spec, ...)` |
| `apply_results(...)` | `BattleSpec.post_battle_hook` |

See `docs/systems/combat_simulation.md` §0–§1 and
`Projects/deep_archive/PROJ-251-300/PROJ-269/decisions.md` for the full
rationale.

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
- Consumers: `results_panel.py`, `test_run_details.py`, `dialogs.py`, `json_viewer.py`, `scrollable_json_panel.py`, `modifier_impact_grid.py`, `battle_panels.py`, `battle_state_viewer.py`

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

## 18. Per-Battle RNG (PROJ-252, extended by PROJ-312)

### Where

`game/simulation/systems/battle_engine.py` -- `BattleEngine.rng`,
`game/engine/collision.py` -- `CollisionSystem.rng`,
`game/simulation/combat/damage_calculator.py` -- `DamageCalculator.rng`,
`game/ai/ai_factory.py` -- `AIControllerFactory._rng` (PROJ-312),
`game/ai/controller.py` -- `AIController._rng` (PROJ-312),
`game/ai/behaviors.py` -- `ErraticBehavior._rng` (PROJ-312),
`game/strategy/engine/conflict_resolution_engine.py` -- `ConflictResolutionEngine._rng`

### How It Works

Each `BattleEngine.start(seed=N)` creates a per-instance `random.Random(seed)`.
This RNG is propagated to subsystems (`CollisionSystem`, `DamageCalculator`,
`AIControllerFactory` → `AIController` → `ErraticBehavior`). The global
`random` module is **never** seeded by simulation code.

```python
# BattleEngine.start_teams()
self._initialize_start_state(seed, ...)        # self.rng = random.Random(seed)
...
self._ai_factory.set_rng(self.rng)             # PROJ-312: AI chain
self._ai_factory.create_for_ships(team_ships, ...)
```

`ConflictResolutionEngine` has its own `self._rng = random.Random()` for
strategy-layer randomness (empire pairing in multi-empire conflicts).

### When to Use

- All combat randomness (hit rolls, damage distribution, fighter spawn offsets)
  must use the battle's `self.rng`, never `random.random()`.
- AI behaviors that need randomness (e.g. `ErraticBehavior`) take `rng` as a
  required keyword-only constructor argument and consume it via `self._rng`.
  The `AIController` forwards its own `_rng` (sourced from
  `AIControllerFactory._rng`, ultimately `BattleEngine.rng`).
- Strategy-layer randomness uses its own `Random` instance.
- **Never** call `random.seed()` from simulation or strategy code.

### Regression Contract (PROJ-312)

The AST guard at
[tests/unit/quality/test_no_unseeded_random.py](../tests/unit/quality/test_no_unseeded_random.py)
fails if any `.py` file under `game/simulation/`, `game/engine/`, or
`game/ai/` calls `random.<X>(...)` other than `random.Random(...)`. New
RNG consumers in those layers MUST inject a `random.Random` instance via
DI; module-level `random.*` is forbidden. An explicit
`# noqa: replay-determinism` allowlist marker exists for genuinely-justified
exceptions, but none are expected today.

Bit-stable replay is verified at
[tests/integration/fleet_combat/test_battle_determinism.py](../tests/integration/fleet_combat/test_battle_determinism.py)
via `TestBattleStateHashRegression` (SHA-256 of canonical per-ship final
state, asserted equal across 5 repeated runs of the same seeded battle).

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

## 21. Screen State Machine (PROJ-259)

**Where:** `game/core/state_machine.py` -- `ScreenStateMachine`, `game/app.py` -- transition table

**How It Works:**
- Declarative transition table: `_SCREEN_TRANSITIONS` frozenset of `(from_state, to_state)` tuples
- `ScreenStateMachine` validates all transitions, supports guards and on_enter/on_exit callbacks
- State stack via `push_and_transition()` / `pop_and_return()` for return-to-previous (builder, keybindings)
- `_switch_scene()` in app.py delegates to `state_machine.transition()` then sets active_scene

**When to Use:** Formalize any state machine where transitions should be validated declaratively.

---

## 22. TurnEngineConfig (PROJ-259)

**Where:** `game/strategy/engine/turn_engine_config.py` -- `TurnEngineConfig`

**How It Works:**
Frozen dataclass bundling 13 optional engine dependencies. `TurnEngine.__init__()` accepts `config=TurnEngineConfig(...)` alongside individual kwargs (individual kwargs take precedence for backward compat).

**When to Use:** Pass to `TurnEngine()` or `create_default_turn_engine()` when overriding specific engines for testing.

---

## 23. Tick Phase Registry (PROJ-259)

**Where:** `game/simulation/systems/tick_phase.py` -- `ITickPhase`, `TickPhaseRegistry`, 5 default phases

**How It Works:**
- `ITickPhase` protocol: `name`, `priority`, `execute(engine)`
- `TickPhaseRegistry`: ordered list of phases, sorted by priority (ascending)
- `BattleEngine.update()` calls `self._tick_phases.execute_all(self)`
- 5 default phases: RebuildGrid(100), AIAndShipUpdate(200), AttackProcessing(300), Ramming(400), ProjectileUpdate(500)
- Custom phases can be registered at any priority without modifying BattleEngine

**When to Use:** Extend the battle simulation with new tick phases (e.g., environmental effects) by registering a custom `ITickPhase` at the desired priority.

---

## 24. External-Stats Bridge (PROJ-270 Phase 9 + PROJ-271)

**Where:** `game/simulation/entities/ship.py` (`Ship.external_stats`), `game/simulation/combat/fleet_aura_manager.py` (`_apply_bonuses`), `game/simulation/components/abilities/base.py` (`Ability.get_effective_stat` composition), `game/simulation/entities/ship_stats.py` (`_apply_aggregated_stats` for ship-level keys).

**How It Works:**
- `ModifierStack` entries (from spec compilers) flow through `FleetAuraManager._recalculate` which aggregates per-team bonuses into `ship.external_stats: Dict[str, float]`.
- At ability-level consumption, `Ability.get_effective_stat(stat_key)` composes ability-local / component-local / ship-external values: `_mult` keys multiply (local × external); `_add` keys sum (local + external).
- At ship-level consumption (for keys like `shield_bonus_add`), `Ship.recalculate_stats` reads `ship.external_stats[stat_key]` directly and applies it to aggregated stats.
- External_stats is battle-scoped and never serialized — it's read-only composition layer preserving "ships enter unmutated".

**Why:**
- Pre-Phase 9, `FleetAuraManager._apply_bonuses` was a hardcoded 2-key sink that silently discarded every stat_key except `fleet_attack_bonus` / `fleet_defense_bonus`. Track A battle math (storm, fleet boosters) compiled real stat_keys that never reached ship stats.
- Option A (external-stats dict) chosen over Option B (synthesize `AppliedModifier` entries) because B would write back into `component.modifiers`, violating PROJ-269's invariant.

**When to Use:**
- New stat_key that applies across all components on a ship uniformly -> per-ability lookup via `STAT_BINDINGS` + `get_effective_stat`.
- New stat_key that adds "virtual" capacity/effect at the ship level (no specific ability owns it) -> ship-level read in `_apply_aggregated_stats`. `shield_bonus_add` is the reference example.

**Don't:**
- Mutate `component.stats` from outside `Component._calculate_modifier_stats`.
- Populate `ship.external_stats` from anywhere except `FleetAuraManager._apply_bonuses`.
- Serialize `external_stats` in save data — it's battle-scoped composition, rebuilt each battle.

**Known Limitation — within-source stack_group composition only (PROJ-272):**
Stack-group aggregation is WITHIN-SOURCE only. Provider auras (ship-mounted
abilities with fleet-scope) bucket under `type(ab).__name__` (e.g.,
`"ShieldModifier"`), while external `ModifierStack` entries bucket under
`effect.stat_key` (e.g., `"shield_capacity_mult"`). These are semantically
different dict keys — a provider `ShieldModifier` aura with
`stack_group="shield_boost"` and an external `shield_capacity_mult` entry
with the same `stack_group="shield_boost"` do NOT compose via MAX; they
aggregate independently. Cross-source unification would require a class-name
→ stat_key registry and is out of scope. Within each source (provider-only
OR external-only), same-stack_group entries correctly MAX and
different-stack_group entries correctly SUM.

---

## 25. Scope-Driven Team Routing (PROJ-271, PROJ-273, PROJ-275)

**Where:** `game/simulation/combat/ability_stat_registry.py` (`OPPONENT_SCOPES`, `emit_entries_for_ability`, `_route_team_ids`), `game/ui/screens/battle_setup/spec_compiler.py` (`_complex_to_entries`), `game/strategy/services/combat_modifier_collector.py` (pre-compile routing for strategy path).

**How It Works:**
- An ability's `AbilityScope` value encodes who it targets: `fleet`/`allied_*`/`player_*`/`system`/`sector` -> owner's team; `enemy_sector`/`enemy_system` -> opponent teams (plural — see fan-out below).
- Both compilers delegate enemy-scope detection to the shared `OPPONENT_SCOPES` frozenset in the ability-stat registry (single source of truth; PROJ-273 consolidated the previously-duplicated `_OPPONENT_SCOPES` locals).
- The registry's `emit_entries_for_ability(..., num_teams=N, ...)` helper fans `enemy_*` scopes out to ALL non-owner teams and returns `List[Tuple[team_id, ModifierEntry]]`. For `num_teams == 2` the fan-out degenerates to a single opposing entry; for `num_teams == 4` with `owner_team == 0` the helper returns three entries targeting teams 1, 2, 3 (PROJ-275 verified end-to-end).
- PROJ-275 Phase 3 removed the local 2-team `_route_team_for_scope` wrapper from the Battle Setup compiler. Routing lives in one place (`_route_team_ids` inside the registry), and `num_teams` is now threaded all the way from the compiler entry points.
- Strategy compiler path is simpler for the same three "classic" mods: `CombatModifierCollector` pre-computes enemy-scope effects INTO the receiving fleet's `FleetCombatModifiers` before the compiler runs, so the compiler emits to `per_team[receiver_id]` trivially.

**Why:**
- User clarified 2026-04-13: "the suppressor and booster effect is just the difference between multiplying by less than 1 or more than 1; the scope determines what vehicles/designs are impacted." No separate suppressor architecture — scope IS the routing mechanism.
- PROJ-275 extended the same logic to N teams; the single `_route_team_ids` helper returns a list regardless of N, so the compilers iterate without caring about team count.

**When to Use:**
- Any new ability type with fleet/system/sector scope options needs scope-driven routing when its effects are compiled into `ModifierStack` entries.
- Extending `OPPONENT_SCOPES` (now a single shared constant) requires adding tests proving each scope routes correctly across N-team fan-out.

---

## 26. Ability-Stat Registry (PROJ-273)

**Where:** `game/simulation/combat/ability_stat_registry.py` (`ABILITY_STAT_REGISTRY`, `AbilityStatMapping`, `emit_entries_for_ability`, `KNOWN_EXTERNAL_STAT_KEYS`), consumed by `game/ui/screens/battle_setup/spec_compiler.py::_complex_to_entries` and `game/strategy/combat/spec_compiler.py::_emit_entries_team_scoped`.

**How It Works:**
- One canonical dict maps ability class name -> `AbilityStatMapping(stat_key, operation, value_field)`. Currently three entries: `ShieldProjection -> shield_bonus_add/add/value`, `ShieldModifier -> shield_capacity_mult/multiply/multiplier`, `DamageModifier -> damage_mult/multiply/multiplier`.
- `emit_entries_for_ability(ability_name, ability_data, *, scope, owner_team, num_teams, source, source_modifier_id, source_modifier_name, stack_group=None)` returns `List[Tuple[int, ModifierEntry]]`. Team routing + N-team fan-out + value extraction all happen in one call. Returns `[]` for unknown abilities (silent skip) or zero values (nothing to apply).
- Battle Setup compiler delegates via `_complex_to_entries`. Strategy compiler delegates via a thin team-scoped wrapper (`_emit_entries_team_scoped`) since `FleetCombatModifiers` stores raw floats rather than dict-shaped ability data.
- `KNOWN_EXTERNAL_STAT_KEYS: FrozenSet[str]` enumerates every stat_key the engine actually consumes downstream of `ship.external_stats`. `FleetAuraManager._append_external_from_entry` warns once per (stat_key, source) when an entry's stat_key isn't in this set — catches silent-drop bugs where a compiler emits an entry no reader picks up.
- Glob-driven guard tests (`tests/unit/simulation/combat/test_ability_stat_registry.py`) iterate every `data/designs/qs_*_complex.json` and validate: (a) no placeholder stat_keys, (b) every combat-class ability in data is covered by the registry. New complex designs are auto-covered.

**Why:**
- Pre-PROJ-273, `_ABILITY_TO_STAT_KEY` lived in Battle Setup's spec_compiler AND the same three stat_keys were emitted via hand-rolled calls in Strategy's spec_compiler. A new ability class required touching both compilers + the ability class, with nothing alerting you if you missed a compiler. Registry consolidates this into a one-line edit.

**When to Use:**
- Adding a new combat-affecting ability (class ending in `Modifier` / `Projection`): add one entry to `ABILITY_STAT_REGISTRY`; the glob test picks up coverage automatically. Also add the `stat_key` to `KNOWN_EXTERNAL_STAT_KEYS` so the runtime warning doesn't false-positive.
- Any future caller (beyond Battle Setup + Strategy) that walks design JSONs and emits `ModifierEntry` objects should use `emit_entries_for_ability` rather than constructing `ModifierEffect` + `ModifierEntry` by hand.

---

## 27. Budget-Aware Randomization (FEAT-12)

**Where:** `game/strategy/systems/race_randomizer.py` — `RaceRandomizer.randomize_aptitudes`, `randomize_environment`, `randomize_all`. Cost authority is `game/strategy/data/race_point_budget.py::RacePointBudget`.

**How It Works:**
- Roll candidate values for each axis being randomized (aptitudes from a 2-3-high / 2-3-low / rest-at-50 shape; environmental preferences seeded from a random `homeworld_presets.json` preset, then jittered per-factor).
- Compute total cost via the same `RacePointBudget` API the UI's `_validate_for_save` uses — single source of truth for the cost contract.
- If total cost exceeds the supplied `budget`, deterministically pull the most-expensive value one step toward its free-baseline (50 for aptitudes, `factor.default_tolerance` for preferences). Repeat until under budget. Setpoints are free, so they're never rebalanced.
- Master orchestrator (`randomize_all`) apportions a 100-point budget between aptitudes and environment using a per-run random fraction in `[0.3, 0.7]`. Each sub-randomizer receives its slice independently and rebalances within it.
- All methods accept `rng: Optional[random.Random] = None` per the Per-Battle RNG pattern (#18) for deterministic testing. Module-level `random` is the default for production callers.

**Why:**
- Prevents the randomizer from emitting configurations the validator would reject on save. The randomizer doesn't reimplement cost math — it delegates to the same `RacePointBudget` the validator uses, so they cannot drift apart.
- The two-phase "roll then rebalance" structure preserves the desired distribution shape for in-budget cases while degrading gracefully when the rolled values overshoot. Random values still drive the result; the rebalance step only kicks in for the 5–10% of seeds that overshoot at low budgets.
- Preset-seeded environment generation produces biologically coherent races (an "Arid" world race naturally wants low water + high CO₂, not random gas mixtures).

**When to Use:**
- Any randomization where a global resource limit must hold over the result. Examples: race generation here; future ship-randomizer with mass / power budget; campaign-start fleet generation with ship-point budget.
- Skip if the constraint is purely per-axis (e.g. `value in [min, max]`) — straightforward `random.uniform` clamping is sufficient and doesn't need a rebalance pass.

---

## 28. Background Service Call (PROJ-296)

### Where

- `game/services/llm/background.py` — `LLMBackgroundCall`, `CallStatus`, `shutdown_all_calls`
- Called from `game/app.py` shutdown sequence before `pygame.quit()`

### How It Works

Wraps a synchronous service call (LLM `complete()`) in a worker thread. The
caller polls `.status` / `.result` / `.error` / `.elapsed_seconds` from the
pygame `update()` loop each frame instead of blocking. Cancellation via
`.cancel()` sets a `threading.Event` that the underlying provider checks
between retries; in-flight HTTP work completes in the background and is
discarded (logical cancel, not physical).

```python
call = LLMBackgroundCall(provider, messages, model="deepseek-v4-flash")
call.start()
# ... in the screen's update():
if call.status == CallStatus.DONE:
    consume(call.result)
elif call.status == CallStatus.ERROR:
    show_error(call.error)
elif call.elapsed_seconds > 30:
    offer_user_a_cancel_button()
```

**Concurrency safeguards:**

- All shared state guarded by an instance `threading.Lock`.
- A module-level counter enforces `LLMConfig.MAX_CONCURRENT_CALLS` (default 3);
  exceeding it raises `LLMConfigError` so a buggy consumer can't spam costly
  requests.
- Workers are non-daemon. `shutdown_all_calls(timeout=5.0)` joins them with
  a bounded timeout before `pygame.quit()` — a hung remote endpoint can
  never freeze the game on shutdown.
- Status reads are lock-protected, so 100 concurrent reads from different
  threads never see torn state.

### When to Use

- Any service call with unbounded latency (network I/O) that must not block
  the pygame main loop.
- Future LLM consumers (diplomacy "emails", ad-hoc summaries).
- Future non-LLM services with the same shape (cloud sync, telemetry
  uploads, asset downloads).

### Reference consumer (PROJ-299)

`game/strategy/services/race_description_llm_controller.py` —
`RaceDescriptionLLMController` is the canonical first consumer. It
owns two `LLMBackgroundCall` instances (one for the bio description,
one for socio), translates their `CallStatus` into a domain-specific
`FieldStatus` enum, and drives the Race Setup UI via an `on_change`
callback. The screen polls `controller.update()` each frame and reads
`bio_elapsed_seconds` / `socio_elapsed_seconds` to drive a 30s/90s
"still working" modal dialog. New consumers should follow the same
shape: a thin pygame-free Controller that owns the call lifecycle,
exposes per-domain status, and is polled by the UI.

### Don't

- Use for fast operations (file I/O, in-memory work) — the threading
  overhead isn't worth it.
- Skip the concurrent-call limit — it's the only protection against a
  buggy consumer racking up provider costs.
- Daemon-thread the workers — daemon threads can die mid-write, corrupting
  the result. Non-daemon + shutdown hook is the contract.

---

## Quick Reference

| Pattern | Primary File | Key Class/Function |
|---------|-------------|-------------------|
| ApplicationContext (DI) | `game/context.py` | `ApplicationContext` |
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
| Spec Compiler + run_battle | `game/simulation/battle_runner.py` + 3 compilers | `run_battle`, `BattleSpec` |
| Ability Aggregation | `game/simulation/entities/ability_aggregator.py` | `calculate_ability_totals()` |
| Factory | `game/ai/ai_factory.py`, `game/ui/services/ship_factory.py` | `AIControllerFactory`, `ShipFactory`, `PanelFactory` |
| ScrollState | `game/ui/widgets/scroll_state.py` | `ScrollState` |
| Serializable | `game/core/protocols.py` | `ISerializable` |
| Error Boundary | `game/strategy/engine/turn_state_snapshot.py` | `TurnStateSnapshot`, `EnginePhaseError` |
| Precondition Validation | `game/strategy/engine/*.py` | `_validate_tick_inputs()` |
| Screen State Machine | `game/core/state_machine.py` | `ScreenStateMachine` |
| TurnEngineConfig | `game/strategy/engine/turn_engine_config.py` | `TurnEngineConfig` |
| Tick Phase Registry | `game/simulation/systems/tick_phase.py` | `ITickPhase`, `TickPhaseRegistry` |
| External-Stats Bridge | `game/simulation/entities/ship.py` + `fleet_aura_manager.py` | `ship.external_stats`, `FleetAuraManager._apply_bonuses` |
| Scope-Driven Team Routing | `game/simulation/combat/ability_stat_registry.py` | `OPPONENT_SCOPES`, `emit_entries_for_ability` |
| Ability-Stat Registry | `game/simulation/combat/ability_stat_registry.py` | `ABILITY_STAT_REGISTRY`, `emit_entries_for_ability`, `KNOWN_EXTERNAL_STAT_KEYS` |
| Background Service Call | `game/services/llm/background.py` | `LLMBackgroundCall`, `CallStatus`, `shutdown_all_calls` |
| Universal Ability Source | `game/strategy/services/system_effects_collector.py` + `ability_sources/` | `IAbilitySource`, `collect_system_effects` |

### Critical Naming Reminders

- Ship inherits `(PhysicsBody, ShipPhysicsMixin)` -- **no ShipCombatMixin**.
- Config classes in `game/core/config.py` are **plain classes, not dataclasses**.
- Use **BattleScreen / StrategyScreen**, not BattleScene / StrategyScene.
- Use **VehicleDesignService**, not ShipBuilderService.
- **PolicyManager** is at `game/ai/policy_manager.py`.
- **EventBus** is at `game/ui/screens/builder/event_bus.py`.


## 29. Universal Ability Source (PROJ-300..305)

### Where
- Protocol: [`game/core/protocols/strategy_entities.py`](../game/core/protocols/strategy_entities.py) — `IAbilitySource` + `is_ability_source` TypeGuard
- Adapter package: [`game/strategy/services/ability_sources/`](../game/strategy/services/ability_sources/) — `FacilityAbilitySource`, `StormAbilitySource`, `PlanetIntrinsicAbilitySource`, `StarAbilitySource`, `WarpPointAbilitySource`, `SystemAbilitySource`, `FleetAbilitySource`, plus shared helpers (`roll_intrinsic_abilities`, `format_intrinsic_source_label`)
- Iterator: [`game/strategy/services/ability_iterator.py`](../game/strategy/services/ability_iterator.py)
- Collector: [`game/strategy/services/system_effects_collector.py`](../game/strategy/services/system_effects_collector.py)
- Aggregation: [`game/strategy/services/strategic_ability_scanner.py`](../game/strategy/services/strategic_ability_scanner.py) — `aggregate_multipliers` (intra-MAX, inter-MULTIPLY) + `aggregate_rates` (intra-MAX, inter-SUM)

### How It Works
Every locatable entity that contributes strategic-layer abilities — facility, storm, planet, star, warp point, system archetype, fleet — implements `IAbilitySource`. Each one declares `source_kind` / `source_label` / `source_id` / `owner_id` for UI rendering, `get_abilities()` for the ability dict, and `affects_hex` / `affects_system` for filtering.

Adapters register a provider function with `register_source_provider_at_hex` / `register_source_provider_in_system`. The iterator yields `IAbilitySource` instances; the collector walks them, applies owner-filter (ownerless apply to all empires; owned to matching empire) + scope-filter (`_SECTOR_SCOPES` vs `_SYSTEM_SCOPES`), groups by `(ability_name, resource_type | damage_type)`, and dispatches to either `aggregate_multipliers` or `aggregate_rates` depending on the effect's `kind`.

**PROJ-305 fleet integration:** `_fleet_provider` gates on `_FLEETS_AT_HEX_LOOKUP` / `_FLEETS_IN_SYSTEM_LOOKUP` callbacks registered via `set_fleet_lookups`. `GameInitializer._wire_fleet_lookups` connects them at session start.

**Validations:**
- D16 — mixed-kind groups (multiplier-only + rate-only entries in the same group) skip the offender + log warning.
- D17 — ownerless sources may not declare ownership-aware scopes (`enemy_sector`, `allied_sector`, etc.); offending entries are skipped + logged.
- D13 — components must not declare both combat scopes (self/fleet/team) and strategic scopes (sector/system/etc) on the same ability instance (test enforces).
- AST static-analysis guard prevents `get_default_registry_provider()` calls inside the adapter package (PROJ-306 layering rule).

### When to Use
- Any new entity kind that should project strategic-layer effects to a hex or system: write an adapter implementing `IAbilitySource`, register a provider.
- Storm-style "things at a hex apply effects" become one-line plug-ins instead of bespoke pipelines.

### Key behavior
- Overlapping storms multiply per-provider (no shared `stack_group`) — two ion storms apply 0.25× shields, not 0.5× (PROJ-300 D6).
- ThrustModifier is wired into combat propulsion via `ABILITY_STAT_REGISTRY` (PROJ-300 D14).
- Hostile star systems are deliberately uncapped (PROJ-302 D7); a hazard hint UI in `system_tree_panel` warns the player (D8).

---

## 30. Registrar Close-Callback (BUG-121)

> **STATUS: SUPERSEDED by Pattern #31 (PROJ-313).** This pattern documented
> the per-window manual contract used for strategy modal windows pre-PROJ-313:
> add a slot to ``StrategyWindowManager``, scan it in ``has_modal_open()``,
> override ``kill()`` on the window to fire ``on_close_callback``, and
> implement a registrar ``_on_closed`` that resets the slot. PROJ-313
> replaced this six-step manual contract with structural enforcement via
> the ``StrategyModalWindow`` base class (Pattern #31). New strategy-modal
> windows MUST subclass ``StrategyModalWindow``; do not implement Pattern
> #30 manually for new code. The pattern documentation below is preserved
> for historical reference and to explain how slot-tracked legacy windows
> still partially work during the migration window.

### Where
- Reference adopters: [`game/ui/screens/strategy_windows/planet_abilities_ctrl.py`](../game/ui/screens/strategy_windows/planet_abilities_ctrl.py) (`PlanetAbilitiesRegistrar._on_closed`); [`game/ui/screens/strategy_windows/list_windows.py`](../game/ui/screens/strategy_windows/list_windows.py) (`PlanetListRegistrar`, `StarListRegistrar`); [`game/ui/screens/strategy_windows/fleet_report_ctrl.py`](../game/ui/screens/strategy_windows/fleet_report_ctrl.py) (`FleetReportRegistrar`)
- Window classes that override `kill()` to invoke the callback: `PlanetAbilitiesWindow` ([`game/ui/screens/planet_abilities_window.py`](../game/ui/screens/planet_abilities_window.py)), `PlanetListWindow` ([`game/ui/screens/planet_list_window.py`](../game/ui/screens/planet_list_window.py))
- Modal-state reader: [`game/ui/screens/strategy_event_router.py`](../game/ui/screens/strategy_event_router.py) — `has_modal_open()` walks each tracked window slot and returns True if any is non-None.

### How It Works
Every modal-style strategy window has a registrar (a controller object on the strategy screen) that owns a slot variable like `wm.planet_abilities_window`. When the registrar opens the window it stores a reference in its slot AND passes `on_close_callback=self._on_closed` to the window constructor. The window stores the callback and overrides pygame_gui's `kill()` to invoke the callback before calling `super().kill()`. The callback resets the slot back to `None`.

This is the **write side** of `has_modal_open()`'s **read side**: both sides must be wired together. Adding a slot to `has_modal_open` without also wiring a cleanup path causes the slot to leak after the user closes the window via the title-bar `[X]`, permanently triggering `has_modal_open() == True` and silently blocking downstream input gating (e.g., the strategy screen's mouse-wheel zoom guard).

### When to Use
- Any new modal-style window tracked by `StrategyWindowManager` / `StrategyEventRouter`. **The rule is: whenever a slot is added to `has_modal_open`, a corresponding cleanup path (registrar `on_close_callback` OR `_handle_window_close` branch) must be added in the same change.**

### Why
- pygame_gui's `kill()` releases the widget but does not reset the Python attribute on the parent that holds a reference to the killed window. `has_modal_open()` checks `is not None` (not `.alive()`), so a dead reference still counts as "open" until the slot is explicitly cleared.
- The `_handle_window_close` event-driven cleanup branch is the alternative (used for ~12 slots today). The registrar callback pattern is preferred for windows whose lifecycle is owned by a registrar, because it keeps the open-and-close paths co-located.

### Key behavior
- Registrar's `_on_closed` runs synchronously inside `kill()`; the slot is `None` before `kill()` returns.
- Test contract: `tests/unit/ui/screens/test_strategy_window_manager_public_api.py::test_modal_slot_clears_after_window_kill` is parametrised over every slot in `has_modal_open`'s scan and pins the lifecycle invariant for the whole window family.


---

## 31. Strategy Modal Window Base Class (PROJ-313)

### Where
- Base class: [`game/ui/screens/strategy_modal_window.py`](../game/ui/screens/strategy_modal_window.py) — `StrategyModalWindow(UIWindow)`.
- Registry: `StrategyModalWindow._registered_subclasses` (populated by `__init_subclass__` at class definition time).
- Manager API: `StrategyWindowManager.register_modal()`, `unregister_modal()`, `iter_live_modals()` in [`game/ui/screens/strategy_window_manager.py`](../game/ui/screens/strategy_window_manager.py).
- Adopters (21 windows): `OrdersWindow`, `TransferDialog`, `CargoQuickDialog`, `PlanetSelectionWindow`, `SystemSelectionWindow`, `FleetSelectionWindow`, `EmpireBuildQueueWindow`, `EventLogWindow`, `EmpirePanelWindow`, `PlanetListWindow`, `StarListWindow`, `BuildQueueListWindow`, `FleetReportWindow`, `PlanetAbilitiesWindow`, `MoveChoiceWindow`, `FoodAllocationEditor`, `AtmosphereTargetEditor`, `GravityTargetEditor`, `WaterTargetEditor`, `RadiationShieldEditor`.

### How It Works
Subclassing `StrategyModalWindow` auto-registers the instance with a `StrategyWindowManager` on construction (via `register_modal(self)` in `__init__`) and auto-deregisters on `kill()` (via `unregister_modal(self)` before `super().kill()`).

`StrategyEventRouter.has_modal_open()` and `_is_blocking_ui_element_at()` walk a single live-list — `window_manager.iter_live_modals()` — that GC-filters dead refs via `.alive()` on every iteration. Both methods are one-liners.

The contract is structural: the constructor accepts a required keyword-only `window_manager` parameter, so forgetting registration is impossible. The `kill()` override is in the base class, so forgetting deregistration is impossible. pygame_gui's `UIWindow.kill()` is the universal funnel for every kill path (programmatic, title-bar `[X]` button, parent-kill cascade), so `StrategyModalWindow.kill()` always runs.

### When to Use
**Any new modal-style window that should block strategy-screen input.** Subclass `StrategyModalWindow`, accept `window_manager` as a keyword-only param in `__init__`, and forward it to `super().__init__(..., window_manager=window_manager)`. No further wiring required — no manual slot field on `StrategyWindowManager`, no clauses in `has_modal_open()` or `_is_blocking_ui_element_at()`, no `kill()` override.

For windows opened **outside** the strategy screen (e.g., `BuildQueueScreen` opening a `PlanetSelectionWindow`), pass `window_manager=None`. The instance simply doesn't register; the contract is preserved at strategy-screen callers.

### Why
- Eradicates the BUG-22 / BUG-69 / BUG-121 / BUG-122-foodallocation bug class structurally — clicks-through and stale-flag-leak failures are no longer possible because their causal contract steps are absent.
- The asymmetric `is not None` (in `has_modal_open`) vs `.alive()` (in `_is_blocking_ui_element_at`) check that produced BUG-121 is collapsed: both paths now walk the same `.alive()`-filtered list.
- Test contract simplification: a parametrised behavioural test iterates `_registered_subclasses` and verifies every subclass auto-registers/deregisters. Replaces the source-string-matching test that produced false negatives.

### Key Behavior
- `kill()` deregisters BEFORE `super().kill()`, so the modal is off the live list at the moment `alive()` flips to False.
- `unregister_modal` is idempotent (swallows `ValueError` for already-removed entries) — calling `kill()` twice is safe.
- `iter_live_modals` performs an in-place GC walk (`self._modals = [w for w in self._modals if w.alive()]`) on every call — orphan refs from parent-kill cascades are reaped within one walk.
- Test contract: `tests/unit/ui/screens/test_strategy_modal_window.py` covers the base class invariants; `tests/integration/ui/test_editor_click_blocking.py` covers the Phase 7 click-through fix.

### Migration notes (legacy slot fields)
The 16 slot fields on `StrategyWindowManager` are KEPT post-migration as caller-convenience pointers (used by `strategy_screen.rebuild_list()`, `handle_global_event` forwarding, "kill before re-open" idioms). They no longer participate in modal tracking — `has_modal_open()` and `_is_blocking_ui_element_at()` ignore them entirely. The legacy `_handle_window_close` event listener is also kept; it clears these slots when pygame_gui posts `UI_WINDOW_CLOSE`, so callers see `None` after close. Pattern #30's "registrar callback to clear the slot" mechanism remains active where present, but the contract for **modal tracking** is now Pattern #31.
