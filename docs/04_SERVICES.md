# Service Layer Architecture

## Overview

The Starship Battles codebase uses a service layer pattern to provide clean abstractions between UI components and domain logic. Services act as facades that encapsulate complex operations and provide stable APIs for UI consumption.

Services exist in two layers:
- **Simulation services** (`game/simulation/services/`) -- battle lifecycle, ship design, component modifiers, design loading, registry loading
- **Strategy services** (`game/strategy/services/`) -- fleet navigation, fleet speed, ship stats, cargo transfers, design costs, area effects, component inspection, action timing, modifier resolution, strategic ability scanning, system effects collection

---

## Service Directory

```
game/simulation/services/
    __init__.py
    battle_service.py           # Battle creation and simulation control
    design_loader.py            # Load ship designs into Ship objects
    modifier_service.py         # Low-level component modifier handling
    registry_loader.py          # Load registry data from disk
    vehicle_design_service.py   # Ship creation and modification

game/ui/screens/builder/
    modifier_logic.py           # ModifierLogicService - builder modifier logic (DI)
    modifier_utils.py           # copy_modifiers() utility
    stat_definitions.py         # StatDefinition class
    stat_getters.py             # Stat value getters, formatters, validators
    stat_rows_dynamic.py        # Dynamic resource/strategic row generation
    stats_config.py             # Stats layout loader + re-exports

game/strategy/services/
    __init__.py
    action_time_resolver.py     # Resolve tick-based action times for orders
    area_effect_manager.py      # Aggregate environmental effects at hex locations
    cargo_transfer_service.py   # Cargo transfer business logic
    component_inspector.py      # Inspect design components and abilities
    design_cost_calculator.py   # Calculate design resource costs
    fleet_cargo_projector.py    # Project future cargo state from order queue
    fleet_navigation_service.py # Fleet pathfinding and movement
    fleet_speed_calculator.py   # Strategic movement speed calculation
    modifier_resolver.py        # Resolve size_mount modifiers from design_data
    ship_stats_calculator.py    # DEPRECATED — stat calculation moved to simulation layer
    strategic_ability_scanner.py # Find strategic abilities across spatial scopes
    system_effects_collector.py  # Aggregate system-scope effects for UI display

game/strategy/data/                # Data models (not services, but consumed via service-like helpers)
    environmental_preference.py # PROJ-283: EnvironmentalPreference dataclass
    habitability_factors.py     # PROJ-283: HabitabilityFactor + FACTOR_REGISTRY
    race_config.py              # PROJ-283: RaceConfig.preferences, base_reproduction_rate, base_happiness
    race_point_budget.py        # PROJ-283: RacePointBudget.calculate_preferences_cost / calculate_reproduction_cost
    homeworld_presets.py        # PROJ-283: apply_preset_to_config (registry-native partial overrides)

game/strategy/formulas/
    habitability.py             # PROJ-283: registry-driven calculate_habitability + score_planet_for_race
```

---

## Simulation Layer Services

### ShipMaterializer (PROJ-274)

**Location:** `game/simulation/services/ship_materializer.py`

**Purpose:** Turn a `ShipSpec` into a live `Ship` without forcing every caller to supply a `ship_builder` closure. Before PROJ-274, six forks of that closure lived across `game/app.py`, Combat Lab services, and test fixtures; ShipMaterializer consolidates them into a protocol + two implementations, registered on ApplicationContext.

**Protocol:**
```python
@runtime_checkable
class IShipMaterializer(Protocol):
    def materialize(
        self,
        ship_spec: ShipSpec,
        team_id: int,
        registries: GameRegistries,
    ) -> Ship: ...
```

**Implementations:**

| Class | Use case | Requires |
|-------|----------|----------|
| `InstanceBackedMaterializer` | Strategy, Battle Setup, `game/app.py::start_battle` — callers with a `ShipInstance` already populated | `ship_spec.instance_ref` set to the `ShipInstance` |
| `DesignOnlyMaterializer(design_loader)` | Combat Lab scenarios — construct ships from JSON by filename | A `design_loader(design_id: str) -> dict` closure |

**Module accessors (PROJ-258 pattern):**

```python
from game.simulation.services.ship_materializer import (
    get_default_ship_materializer,
    set_default_ship_materializer,
    InstanceBackedMaterializer,
    DesignOnlyMaterializer,
)

# Production default (lazy-init): InstanceBackedMaterializer.
mat = get_default_ship_materializer()

# Combat Lab swaps at TestRunner.__init__:
set_default_ship_materializer(
    DesignOnlyMaterializer(design_loader=load_combat_lab_design)
)
```

**run_battle integration:**

Both `run_battle(spec, ai_factory=..., ship_builder=None)` and `BattleController.start_from_spec(spec, ..., ship_builder=None)` fall back to the context materializer when no explicit `ship_builder` is supplied (PROJ-274 Phase 5). Internally `_default_ship_builder_from_context()` in `game/simulation/battle_runner.py` assembles a `(ship_spec, team_id) -> Ship` closure using the default materializer + default registry provider. Test code keeps the kwarg for isolation.

**ShipSpec extension:**

`ShipSpec` carries a new `instance_ref: Optional[Any] = None` field. Instance-backed compilers (strategy, battle_setup) set it to the owning `ShipInstance`; Combat Lab leaves it `None`. Typed `Optional[Any]` so the simulation layer doesn't import from strategy.

**Call sites (after migration):**

| Caller | Ship builder supplied? | Materializer used |
|--------|------------------------|-------------------|
| `game/app.py::start_battle` | No | InstanceBackedMaterializer (default) |
| `combat_lab/services/test_execution_service.py` | No | DesignOnlyMaterializer (installed by TestRunner) |
| `combat_lab/services/scenario_run_helper.py` | Yes (role-tagging wrapper) | Wraps context builder |
| `game/ui/screens/test_lab/screen.py` | No | DesignOnlyMaterializer |
| `combat_lab/scenarios/templates.py::ComparisonScenario` | Yes (role-tagging wrapper) | Wraps context builder |
| Tests (test_three_team_battle, test_boundary_retreat, etc.) | Yes (explicit stub) | Override takes priority |

---

### BattleService

**Location:** `game/simulation/services/battle_service.py`

**Purpose:** Abstraction layer between UI and BattleEngine. Manages the full battle lifecycle: creation, ship assignment, simulation execution, and state queries.

> **PROJ-269 + PROJ-270:** All headless callers route through
> `game.simulation.battle_runner.run_battle(spec)` — it constructs +
> drives `BattleEngine` directly, no `BattleService` wrapper. The
> service is now used only by the visual-mode `BattleController` for
> per-frame ticking. `BattleController` also emits a `BattleOutcome`
> at battle end (PROJ-270 Phase 4.4) so visual-mode UI consumes the
> same DTO contract as headless callers. See `combat_simulation.md`
> §0–§1 for the spec-compiler-driven flow that replaced the legacy
> `create_*_battle` factories.

**Dependencies:** None (no constructor args). Internally creates `BattleEngine` and `BattleLogger`. AI factory is injected at battle creation time via the `ai_factory` parameter.

**Result Object:**
```python
@dataclass
class BattleServiceResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    engine: Optional[BattleEngine] = None
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_battle` | `(seed: Optional[int], enable_logging: bool, ai_factory: Optional[IAIControllerFactory] = None) -> BattleServiceResult` | Create a new battle instance with optional seed, logging, and AI factory |
| `add_ship` | `(ship: Ship, team_id: int) -> BattleServiceResult` | Add a ship to team 0 or 1 (before start only) |
| `remove_ship` | `(ship: Ship) -> BattleServiceResult` | Remove a ship from the battle (before start only) |
| `start_battle` | `(end_condition: Optional[IEndCondition], absolute_max_ticks: Optional[int]) -> BattleServiceResult` | Start the simulation with the given end condition |
| `update` | `() -> BattleServiceResult` | Run one simulation tick |
| `run_ticks` | `(count: int) -> BattleServiceResult` | Run multiple ticks (stops early if battle ends) |
| `is_battle_over` | `() -> bool` | Check if the battle has ended |
| `get_winner` | `() -> Optional[int]` | Get winning team ID (0, 1, -1 for draw, None if no engine) |
| `get_battle_state` | `() -> Dict[str, Any]` | Get full state dict (tick count, ships, projectiles, etc.) |
| `get_all_ships` | `() -> List[Ship]` | Get all ships in battle |
| `get_alive_ships` | `() -> List[Ship]` | Get only living ships |
| `get_engine` | `() -> Optional[BattleEngine]` | Get the underlying BattleEngine directly |
| `reset` | `() -> None` | Clear all battle state, close logger |

**Usage:**
```python
from game.simulation.services.battle_service import BattleService
from game.simulation.systems.battle_end_conditions import (
    TeamEliminatedCondition, TickLimitCondition, AnyCondition,
)

service = BattleService()
result = service.create_battle(seed=42, enable_logging=True)

service.add_ship(ship1, team_id=0)
service.add_ship(ship2, team_id=1)

# Simple: end when a team is eliminated (default)
service.start_battle()

# Or composable: end when eliminated OR after 10,000 ticks
service.start_battle(end_condition=AnyCondition([
    TeamEliminatedCondition(),
    TickLimitCondition(max_ticks=10000),
]))

while not service.is_battle_over():
    service.update()

winner = service.get_winner()
service.reset()
```

---

### VehicleDesignService

**Location:** `game/simulation/services/vehicle_design_service.py`

**Purpose:** High-level operations for ship creation and modification. Abstracts layer management, component validation, class changes, and stat recalculation.

**Dependencies:** Requires `GameRegistries` via constructor injection (strict DI, no fallback).

**Result Object:**
```python
@dataclass
class DesignResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ship: Optional[Ship] = None
    removed_component: Optional[Component] = None
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_ship` | `(name: str, ship_class: str, theme_id: str = "Federation", x: float = 0.0, y: float = 0.0, color: tuple = (100,100,255), team_id: int = 0) -> DesignResult` | Create a new ship. Only `name` and `ship_class` are required. |
| `add_component` | `(ship: Ship, component_id: str, layer: LayerType) -> DesignResult` | Create component from registry ID and add to ship |
| `add_component_instance` | `(ship: Ship, component: Component, layer: LayerType) -> DesignResult` | Add a pre-constructed component instance to ship |
| `add_component_bulk` | `(ship: Ship, component_id: str, layer: LayerType, count: int) -> DesignResult` | Add multiple copies of a component |
| `remove_component` | `(ship: Ship, layer: LayerType, index: int) -> DesignResult` | Remove component by layer and index |
| `move_component` | `(ship: Ship, source_layer: LayerType, index: int, target_layer: LayerType) -> DesignResult` | Move component between layers (atomic remove + re-add, preserves instance). Mass budget is advisory — moves are not blocked by it. |
| `change_class` | `(ship: Ship, new_class: str, migrate_components: bool = True) -> DesignResult` | Change vehicle class, optionally migrating components (default: migrate) |
| `validate_design` | `(ship: Ship) -> ValidationResult` | Full design validation |
| `get_available_components` | `(ship: Ship, layer: LayerType) -> List[str]` | Get component IDs valid for the given layer |
| `get_layer_info` | `(ship: Ship, layer: LayerType) -> dict` | Get layer details (components, restrictions, radius_pct) |
| `get_ship_summary` | `(ship: Ship) -> dict` | Get summary of ship stats (mass, hp, speed, validity, etc.) |

**Usage:**
```python
from game.simulation.services.vehicle_design_service import VehicleDesignService
from game.core.constants import LayerType
from game.core.registry import GameRegistries

registries = GameRegistries.from_data_files()
service = VehicleDesignService(registries=registries)

# Create a ship
result = service.create_ship(name="USS Enterprise", ship_class="Cruiser", theme_id="Federation")
if result.success:
    ship = result.ship

    # Add components
    result = service.add_component(ship, "laser_cannon", LayerType.OUTER)
    result = service.add_component_bulk(ship, "standard_armor", LayerType.OUTER, count=4)

    # Validate
    validation = service.validate_design(ship)
    if not validation.is_valid:
        print(validation.errors)

    # Get summary
    summary = service.get_ship_summary(ship)
    print(f"{summary['name']}: {summary['mass']}/{summary['max_mass']}kg")
```

#### WorkshopViewModel Higher-Level Operations

The `WorkshopViewModel` (`game/ui/screens/workshop_viewmodel.py`) composes
`VehicleDesignService` calls with layer resolution and UI state management.
These are not service methods but ViewModel methods that delegate to the service.

| Method | Signature | Description |
|--------|-----------|-------------|
| `resolve_target_layer` | `(component: Component, selected_layer: Optional[LayerType]) -> Optional[LayerType]` | Find best layer for quick-add (innermost valid, or nearest to selection) |
| `quick_add_component` | `(component_id: str, selected_layer?: LayerType, count?: int) -> bool` | Add component via palette "+" button with auto layer resolution |
| `move_component` | `(source_layer: LayerType, index: int, target_layer: LayerType) -> bool` | Move single component between layers (remove + re-add instance) |
| `move_component_group` | `(group_key: str, source_layer: LayerType, target_layer: LayerType) -> bool` | Move all components in a group between layers |
| `resolve_move_target` | `(component: Component, source_layer: LayerType, direction: str) -> Optional[LayerType]` | Find next valid layer in "up"/"down" direction (skips HULL and invalid layers) |
| `on_modifier_changed` | `() -> None` | Called after any modifier change — syncs multi-selection, always recalculates ship stats |

#### Stats Panel Configuration

The stats panel is driven by `data/stats_sections.json`. Each section declares visibility
rules, column placement, and stat definitions. Key files:

| File | Purpose |
|------|---------|
| `data/stats_sections.json` | Section definitions, visibility rules, always-visible overrides |
| `game/ui/screens/builder/stat_getters.py` | Getter functions registered in `GETTERS` dict |
| `game/ui/screens/builder/stat_rows_dynamic.py` | Dynamic row generators for variable-content sections |
| `game/ui/screens/builder/stats_config.py` | Config loader, `SECTION_GENERATORS` registry, `resolve_section_visibility()` |
| `game/ui/panels/design_stats_panel.py` | Panel rendering with collapsible sections |

To add a new stat: add getter to `stat_getters.py`, register in `GETTERS`, add item to section in JSON.
To add a new section: add generator to `stat_rows_dynamic.py`, register in `SECTION_GENERATORS`, add section to JSON.

---

### ModifierService (Simulation Layer)

**Location:** `game/simulation/services/modifier_service.py`

**Purpose:** Low-level modifier operations in the simulation layer -- restriction checking, registry access. Used internally by `ComponentService`.

**Dependencies:** Requires `modifier_registry: Dict[str, Any]` via constructor (strict DI, no fallback).

---

### ModifierLogicService (UI Layer)

**Location:** `game/ui/screens/builder/modifier_logic.py`

**Purpose:** Builder-specific modifier logic -- validation, mandatory checks, initial value calculation, component-specific constraints (e.g., turret mount arc limits), and snap calculations for step buttons. Acts as a bridge between UI controls and the underlying `ComponentService`.

**Dependencies:** Requires `IRegistryProvider` via constructor injection (strict DI). Creates a `ComponentService` internally.

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `is_modifier_allowed` | `(mod_id: str, component) -> bool` | Check if modifier is valid for this component (type/ability restrictions) |
| `get_mandatory_modifiers` | `(component) -> list` | Get list of mandatory modifier IDs for this component |
| `is_modifier_mandatory` | `(mod_id: str, component) -> bool` | Check if a specific modifier is mandatory |
| `get_initial_value` | `(mod_id: str, component) -> float` | Get the default value for a newly applied modifier (uses dispatch dict) |
| `ensure_mandatory_modifiers` | `(component) -> None` | Auto-apply all required modifiers with default values |
| `get_local_min_max` | `(mod_id: str, component) -> tuple` | Get (min, max) value range, accounting for component constraints |
| `calculate_snap_value` | `(current, step, direction, min_val, max_val, smart_floor) -> float` | Static. Calculate snap value for step buttons |

**Usage:**
```python
from game.ui.screens.builder.modifier_logic import ModifierLogicService

service = ModifierLogicService(registry_provider=context.registries)

# Check allowance and mandatory status
if service.is_modifier_allowed('turret_mount', weapon):
    print("Turret mount available")

# Auto-apply all mandatory modifiers
service.ensure_mandatory_modifiers(weapon)

# Get valid range for turret arc
min_val, max_val = service.get_local_min_max('turret_mount', weapon)
print(f"Turret arc: {min_val} to {max_val} degrees")
```

> **Note:** A deprecated `ModifierLogic` static wrapper class remains in the same file for backward compatibility during transition. New code should use `ModifierLogicService` instances.

---

### SimulationDesignLoader

**Location:** `game/simulation/services/design_loader.py`

**Purpose:** Loads ship designs from JSON files or design data dicts and creates Ship simulation entities. Handles the simulation layer concern of instantiating Ship objects with proper stat recalculation.

**Dependencies:** Requires `GameRegistries` via keyword-only constructor argument (strict DI, raises `ValidationException` if None).

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `load_ship_from_design_data` | `(design_data: dict, center_x: int, center_y: int) -> Optional[Ship]` | Create a Ship from a design data dict; returns None on error |
| `load_ship_from_file` | `(file_path: str, width: int = 1920, height: int = 1080) -> Tuple[Optional[Ship], str]` | Load a Ship from a JSON file; returns (Ship or None, message) |

**Usage:**
```python
from game.simulation.services.design_loader import SimulationDesignLoader

loader = SimulationDesignLoader(registries=registries)

# From design data dict
ship = loader.load_ship_from_design_data(design_data, center_x=960, center_y=540)

# From file
ship, message = loader.load_ship_from_file("designs/cruiser.json")
if ship:
    print(f"Loaded: {ship.name}")
else:
    print(f"Error: {message}")
```

---

### reload_registries_from_directory (free function)

**Location:** `game/simulation/services/registry_loader.py`

**Purpose:** Reloads all registry data (components, modifiers, vehicle classes) from a directory. Extracted from `RegistryManager` to fix a Core-to-Simulation layer violation.

**Signature:**
```python
def reload_registries_from_directory(
    registry_manager: RegistryManager,
    data_dir: Union[str, Path]
) -> bool
```

**Behavior:**
- Clears all existing registry data, then loads modifiers, components, and vehicle classes from JSON files in `data_dir`
- Checks for `test_`-prefixed file variants first (for test data directories)
- Returns `True` if directory exists, `False` if directory is invalid
- Raises `FrozenStateException` if registry is frozen

**Usage:**
```python
from game.simulation.services.registry_loader import reload_registries_from_directory

success = reload_registries_from_directory(registry_manager, "data/")
```

---

## Strategy Layer Services

### FleetNavigationService

**Location:** `game/strategy/services/fleet_navigation_service.py`

**Purpose:** Single source of truth for all fleet navigation calculations. Both UI path projection and turn execution use the same logic through this service, ensuring consistency.

**Dependencies:** None (stateless service, no constructor args).

**Data Types:**

```python
@dataclass(frozen=True)
class NavigationState:
    """Immutable snapshot of fleet state for pure-function navigation."""
    location: HexCoord
    path: tuple           # tuple[HexCoord, ...]
    orders: tuple         # tuple[FleetOrder, ...]
    speed: float
    can_warp: bool

    @classmethod
    def from_fleet(cls, fleet: Fleet) -> NavigationState: ...

@dataclass(frozen=True)
class PathSegment:
    """One step in a projected path (for UI visualization)."""
    start: HexCoord
    end: HexCoord
    turn: int
    is_warp: bool

    def to_dict(self) -> dict: ...

@dataclass(frozen=True)
class NavigationStep:
    """Result of computing one navigation step."""
    next_hex: Optional[HexCoord]
    new_state: NavigationState
    order_complete: bool = False
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_destination` | `(state: NavigationState, order: FleetOrder, galaxy) -> Optional[HexCoord]` | Determine target hex for a given order (MOVE, MOVE_TO_FLEET, etc.) |
| `compute_path` | `(state: NavigationState, destination: HexCoord, galaxy) -> list` | Calculate path from current location to destination |
| `compute_next_step` | `(state: NavigationState, galaxy) -> NavigationStep` | Pure function: compute next hex and new state without mutation |
| `project_path` | `(fleet: Fleet, galaxy, max_turns: int = 10, component_registry=None) -> list[PathSegment]` | Project fleet movement over multiple turns (for UI visualization) |
| `project_path_as_dicts` | `(fleet: Fleet, galaxy, max_turns: int = 10, component_registry=None) -> list[dict]` | Same as project_path but returns list of dicts |
| `compute_path_for_warp` | `(state: NavigationState, warp_point_hex: HexCoord, galaxy) -> list` | Calculate path to a warp point hex for warp jump navigation |
| `calculate_fleet_next_hex` | `(fleet: Fleet, galaxy) -> Optional[HexCoord]` | Mutation bridge: compute next hex AND apply state changes to Fleet object |

**Architecture:**
- **Core (pure, stateless):** `get_destination`, `compute_path`, `compute_next_step` -- operate on immutable `NavigationState`, no side effects
- **Projection (for UI):** `project_path`, `project_path_as_dicts` -- simulate future movement for visualization
- **Execution (for TurnEngine):** `calculate_fleet_next_hex` -- wraps pure functions and mutates Fleet object

**Usage:**
```python
from game.strategy.services.fleet_navigation_service import FleetNavigationService

nav_service = FleetNavigationService()

# UI: project path for visualization
segments = nav_service.project_path(fleet, galaxy, max_turns=10)
for seg in segments:
    print(f"Turn {seg.turn}: {seg.start} -> {seg.end} (warp={seg.is_warp})")

# Turn execution: get next hex and mutate fleet
next_hex = nav_service.calculate_fleet_next_hex(fleet, galaxy)
if next_hex:
    fleet.location = next_hex

# Pure function usage with NavigationState
from game.strategy.services.fleet_navigation_service import NavigationState
state = NavigationState.from_fleet(fleet)
step = nav_service.compute_next_step(state, galaxy)
print(f"Next: {step.next_hex}, order_complete={step.order_complete}")
```

---

### FleetSpeedCalculator

**Location:** `game/strategy/services/fleet_speed_calculator.py`

**Purpose:** Calculates strategic movement speed (hexes per turn) for individual ships and fleets. Fleet speed is determined by its slowest combat-capable ship (convoy behavior).

**Dependencies:** None (all methods are `@staticmethod`).

**Constants:**
```python
K_STRATEGIC = 25           # Movement point to hex conversion factor
MAX_HEXES_PER_TURN = 10
MIN_HEXES_PER_TURN = 0
IMMOBILE_VEHICLE_TYPES = {'Planetary Complex', 'Satellite', 'Station'}
CARRIER_BASED_TYPES = {'Fighter'}
BASE_TICKS_PER_MOVEMENT = 100  # Module constant: base ticks per movement step
```

**Formula:** `hexes = floor((strategic_movement * K_STRATEGIC) / mass)`, clamped to [0, 10].

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `calculate_ship_speed` | `(ship_instance: ShipInstance) -> int` | Calculate hexes/turn for a single ship from design data |
| `calculate_fleet_speed` | `(fleet: Fleet) -> float` | Calculate fleet speed as slowest combat-capable ship's speed |
| `calculate_fleet_speed_with_environment` | `(fleet: Fleet, environmental_effects) -> float` | Calculate fleet speed accounting for environmental effects (e.g., storm strategic_mult) |
| `update_fleet_speed` | `(fleet: Fleet) -> None` | Update `fleet.speed` in-place from current ship composition |

**Module-level function:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_tick_interval` | `(speed: float) -> int` | Convert fleet speed to tick interval between movement steps, using `BASE_TICKS_PER_MOVEMENT` |

**Special cases for `calculate_ship_speed`:**
- Planetary complexes, satellites, stations: always 0 (immobile)
- Fighters: always 0 (carrier-based, no independent strategic movement)
- Ships with no `StrategicMovement` ability: 0

**Usage:**
```python
from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

# Single ship speed
speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)
print(f"Ship speed: {speed} hexes/turn")

# Fleet speed (slowest ship)
fleet_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

# Update fleet object in-place (call after adding/removing/damaging ships)
FleetSpeedCalculator.update_fleet_speed(fleet)
```

---

### Ship Design Stats (Unified Stat Calculation)

**Location:** `game/simulation/entities/ship_design_stats.py`

**Purpose:** Single source of truth for computing ship stats from design JSON. Uses `Ship.from_dict()` + `recalculate_stats()` so all stat calculations go through one code path (the simulation `ShipStatsCalculator` in `game/simulation/entities/ship_stats.py`).

**PROJ-254:** No `expected_stats` fallback — if `Ship.from_dict()` fails, the error propagates. Callers must handle exceptions if design data may be invalid.

**Dependencies:** Requires `GameRegistries` parameter (strict DI). The underlying `ShipStatsCalculator` requires `resource_catalog` for its `calculate()` method (lazy resolution — raises `TypeError` if omitted). `GameRegistries.__post_init__()` defaults to an empty catalog when not provided, so test code that only calls `calculate_ability_totals()` works without explicit catalog injection.

**Key Function:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_design_stats` | `(design_data, registries, components=None, component_toggles=None) -> Dict` | Calculate all ship stats from design JSON, respecting per-instance damage and toggles |

**Return dict:**
```python
{
    'max_hp': int,                            # Total HP from all components
    'mass': float,                            # Total mass (includes hull base mass)
    'resource_storage': Dict[str, float],     # resource_type -> capacity
    'cargo_storage': Dict[str, float],        # cargo_type -> capacity
    'pod_storage_mass': float,                # Mass capacity for drop pods
    'resource_consumption_per_hex': Dict[str, float],   # per-hex movement costs
    'resource_consumption_per_turn': Dict[str, float],  # per-turn maintenance costs
    'warp_resource_costs': Dict[str, float],  # per-warp-jump costs
    'strategic_movement': float,              # Movement points for strategic map
    'warp_max_tonnage': int,                  # Max ship mass for warp (0 if damaged)
}
```

**Component toggles:** Toggled-off components are excluded from the design before Ship creation, so their stats don't contribute.

**Per-instance damage:** The `components` kwarg accepts a
`Dict[str, ComponentState]` keyed by
`component_state_key(component_id, instance_index)` (i.e. `"{id}#{idx}"`).
Each `ComponentState.current_hp` is applied to the matching Ship
component before `recalculate_stats()` runs, which then applies the
simulation's damage model (threshold-based deactivation, crew
reallocation, etc.). PROJ-276 replaced the old
`component_damage: Dict[str, int]` param with this per-instance form.

**Usage:**
```python
from game.simulation.entities.ship_design_stats import calculate_design_stats
from game.strategy.data.component_state import ComponentState, component_state_key

# Calculate stats for undamaged ship
stats = calculate_design_stats(design_data, registries)
print(f"HP: {stats['max_hp']}, Mass: {stats['mass']}")

# Calculate with per-instance damage
components = {
    component_state_key('bridge', 0): ComponentState(
        component_id='bridge', instance_index=0, current_hp=50.0, max_hp=100.0,
    ),
    component_state_key('standard_engine', 0): ComponentState(
        component_id='standard_engine', instance_index=0, current_hp=30.0, max_hp=100.0,
    ),
}
stats = calculate_design_stats(design_data, registries, components=components)

# Check warp capability (lives in component_inspector)
from game.strategy.services.component_inspector import has_warp_capability
if has_warp_capability(ship_instance):
    print("Ship can use warp points")
```

**Callers:**
- `ShipInstance.get_calculated_stats()` — primary consumer, caches results
- `ProductionSpawner._spawn_to_staging_yard()` — mass calculation for staging
- `Tools/validate_designs/validate_designs.py` — mass consistency checks
- `Tools/fix_designs/fix_designs.py` — expected_stats recalculation

> **Note:** The strategy layer previously contained a duplicate `ShipStatsCalculator` at `game/strategy/services/ship_stats_calculator.py`. It was deleted in PROJ-276 after an audit confirmed zero production importers. Its utility methods `has_warp_capability()` and `get_ability_list()` live in `component_inspector`. Stat calculation now has a single source of truth: `calculate_design_stats()` above.

---

### ActionTimeResolver

**Location:** `game/strategy/services/action_time_resolver.py`

**Purpose:** Resolves the `action_time` (ticks to complete) for tick-based order execution. Looks up action times from component abilities on fleet ships.

**Dependencies:** None (all methods are `@staticmethod`).

**Module Constants:**
```python
ORDER_TO_ABILITY_MAP: Dict[OrderType, str] = {
    OrderType.COLONIZE: 'ColonizePlanet',
    OrderType.IMPLODE_PLANET: 'DestroyPlanet',
    OrderType.STELLERATE_STAR: 'DestroyStar',
    OrderType.OPEN_WARP_POINT: 'OpenWarpPoint',
    OrderType.CLOSE_WARP_POINT: 'CloseWarpPoint',
    OrderType.CREATE_DYSON_SPHERE: 'CreateDysonSphere',
    OrderType.SELF_DESTRUCT: 'SelfDestruct',
}
MOVEMENT_ORDER_TYPES: frozenset  # {OrderType.MOVE, OrderType.MOVE_TO_FLEET}
```

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `resolve_action_time` | `(fleet, order, component_registry=None) -> int` | Resolve ticks required: 0 for movement orders, ability's `action_time` for ability-based orders, 1 as default |

**Usage:**
```python
from game.strategy.services.action_time_resolver import ActionTimeResolver

ticks = ActionTimeResolver.resolve_action_time(fleet, order, component_registry)
```

---

### CargoTransferService

**Location:** `game/strategy/services/cargo_transfer_service.py`

**Purpose:** Shared business logic for cargo transfer operations, extracted from UI dialogs into a testable service. Handles colony resolution, population extraction, inventory inspection, and transfer command assembly.

**Dependencies:** None (all methods are `@staticmethod`).

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `resolve_colonies` | `(facade, hex_coord, fleet) -> List[PlanetInfo]` | Find colonized planets at a hex, with fallback to fleet location and projected position |
| `get_unload_items` | `(facade, fleet_id, colonies) -> List[Dict]` | Get items that can be unloaded (dropped) from a fleet |
| `get_load_items` | `(facade, colonies) -> List[Dict]` | Get items that can be loaded from colonies (population) |
| `get_inventory_items` | `(obj_info) -> List[Dict]` | Extract inventory items from a FleetInfo or PlanetInfo |
| `build_transfer_command` | `(fleet_id, planet_id, cargo_type, direction, amount, max_amount, species_id=None) -> IssueTransferCommand` | Build a transfer command (amount=0 means "transfer all") |

**Module-level function:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `project_fleet_position` | `(fleet) -> HexCoord` | Walk fleet's order queue to find projected position after all MOVE/WARP orders |

**Usage:**
```python
from game.strategy.services.cargo_transfer_service import CargoTransferService

colonies = CargoTransferService.resolve_colonies(facade, hex_coord, fleet)
unload = CargoTransferService.get_unload_items(facade, fleet.id, colonies)
load = CargoTransferService.get_load_items(facade, colonies)

cmd = CargoTransferService.build_transfer_command(
    fleet_id=fleet.id, planet_id=colony.planet_id,
    cargo_type='passengers', direction='load',
    amount=500, max_amount=1000
)
```

---

### StrategicAbilityScanner

**Location:** `game/strategy/services/strategic_ability_scanner.py`

**Purpose:** Scoped ability queries for the strategy layer. Finds active instances of strategic abilities (stabilizers, harvest boosters, build rate boosters) across spatial scopes (planet, sector, system, empire). Provides aggregation using two-phase stacking (intra-group MAX, inter-group MULTIPLY).

**Dependencies:** None (module-level functions). Uses `iter_keyed_components` from `game.core.patterns.layer_iterator` for component iteration with composite keys.

**Key Functions:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `find_abilities_at_planet` | `(ability_key, planet, registries=None, require_active=False) -> List[Dict]` | Find all instances of an ability on a planet's operational facilities |
| `find_abilities_in_scope` | `(ability_key, target_planet, galaxy, empire, scope, registries=None, require_active=False) -> List[Dict]` | Find abilities affecting a planet at a given spatial scope |
| `aggregate_multipliers` | `(entries) -> float` | Two-phase stacking: intra-group MAX, inter-group MULTIPLY |

**Scope resolution:** `find_abilities_in_scope` resolves which planets to scan based on the `scope` parameter:

| Scope | Planets scanned |
|-------|----------------|
| `planet` / `self` | Target planet only |
| `sector` | All empire-owned planets at the target's **global hex** (via `galaxy.get_planet_global_hex` + `galaxy.get_planets_at_global_hex`) |
| `system` | All empire-owned planets in the target's **star system** (via `galaxy.get_system_of_planet`) |
| `empire` | All empire colonies |

**Activation filtering (`require_active`):** When `True`, only returns abilities from components whose `ComponentActivationState.phase` is `ACTIVE`. Used by `StabilizerRegistry.find_blocking_stabilizer()` to ensure stabilizers must be manually activated before they provide protection. Always-on abilities (harvest boosters, build rate boosters) use the default `False`.

**Registry parameter is critical** — facility `design_data` typically stores bare component IDs
(`{"id": "stellar_stabilizer"}`) and the ability data is looked up via the component registry.
Callers that omit the `registries` argument will silently get no abilities back, even from ACTIVE
stabilizers. The scanner's `_extract_ability` delegates to
`component_inspector.extract_abilities_from_component`, which accepts either a `GameRegistries`
or a plain components dict. PROJ-277 regression.

**Used by:** `StabilizerRegistry` (superweapon blocking), `HarvestingEngine` (harvest rate boosters), `build_queue_source` (build rate boosters), `SystemEffectsCollector` (system/sector effect display).

### StabilizerRegistry (`game/strategy/services/stabilizer_registry.py`)

Data-driven "which stabilizer blocks which superweapon" mapping. `STABILIZERS` is a tuple of
`StabilizerSpec(ability_name, scopes, blocks)` — one entry per stabilizer ability.
`find_blocking_stabilizer(order_type, reference_planet, galaxy, empires, component_registry)`
returns the first matching `StabilizerSpec` with an ACTIVE instance in scope, or `None`.

Adding a new stabilizer or extending an existing one to cover a new superweapon is a single
edit to `STABILIZERS`. Superweapon handlers call
`self._check_blocking_stabilizer(order_type, ref_planet, galaxy, empires, component_registry)`
which delegates to this registry.

### SystemDestroyer (`game/strategy/services/system_destroyer.py`)

Centralizes the tear-down of an entire star system for superweapons like `STELLERATE_STAR`.
Uses a **collect-then-mutate** protocol: `collect_system_contents(system, galaxy, empires)`
returns an immutable `SystemDestructionPlan` listing every planet, star, and fleet to
remove, then `destroy_system(plan, galaxy, empires)` applies the removals.

Fleet inclusion is by hex distance (any fleet within `SYSTEM_RADIUS_HEXES = 50` of the
system's `global_location`), matching `pathfinding.get_system_at_hex(radius=50)`. This is
broader than `GalaxySpatialIndex.get_all_fleets_in_system`, which only checked hexes with a
placed entity — the collect-then-mutate protocol also makes the pre-PROJ-277 ordering bug
(planets unregistered before fleet scan) structurally impossible.

---

### SystemEffectsCollector

**Location:** `game/strategy/services/system_effects_collector.py`

**Purpose:** Aggregates system-scope abilities from empire-owned colonies in a star system for UI display. Handles both activatable abilities (stabilizers with ComponentActivationState) and passive abilities (harvest boosters, build rate boosters, quality improvers).

**Dependencies:** None (module-level function). Uses `strategic_ability_scanner.aggregate_multipliers()` for two-phase stacking.

**Key Function:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `collect_system_effects` | `(system, empire_id, registries=None) -> List[Dict]` | Collect all system-scope effects grouped by ability type with aggregate status and stacked values |

**Return dict keys:** `ability_name`, `display_name`, `group_key`, `status`, `resource_type`, `aggregate_value`, `providers` (list of facility/planet/component info).

---

### DesignCostCalculator

**Location:** `game/strategy/services/design_cost_calculator.py`

**Purpose:** Centralized calculator for design resource costs. Resolves component costs from the registry via Ship loading, handling formula-based values and modifier multipliers. Applies the vehicle class `cost_multiplier` from `vehicleclasses.json` (e.g., Drop Pods use 5x).

**Dependencies:** None (all methods are `@staticmethod`). Accepts `GameRegistries` as a method parameter.

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `calculate_total_cost` | `(design_data, registries) -> Dict[str, float]` | Calculate total resource cost; tries inline costs first, then Ship loading from registry. Applies `cost_multiplier` from vehicle class definition. |
| `_apply_cost_multiplier` | `(base_cost, design_data, registries) -> Dict[str, float]` | Internal: looks up `cost_multiplier` from `vehicleclasses.json` via the design's `ship_class` and multiplies all resource costs. Default multiplier is 1.0. |

**Usage:**
```python
from game.strategy.services.design_cost_calculator import DesignCostCalculator

cost = DesignCostCalculator.calculate_total_cost(design_data, registries)
```

---

### FleetCargoProjector

**Location:** `game/strategy/services/fleet_cargo_projector.py`

**Purpose:** Projects future cargo state by walking the fleet's order queue. Used when queuing transfer orders to determine what cargo the fleet will have after earlier queued orders execute.

**Dependencies:** None (all methods are `@staticmethod`).

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_projected_cargo` | `(fleet: Fleet, cargo_type: str) -> int` | Compute projected cargo after all queued orders, applying load/unload deltas |

**Usage:**
```python
from game.strategy.services.fleet_cargo_projector import FleetCargoProjector

# Check projected passengers after queued orders
projected = FleetCargoProjector.get_projected_cargo(fleet, 'passengers')
```

---

### AreaEffectManager

**Location:** `game/strategy/services/area_effect_manager.py`

**Purpose:** Aggregates environmental effects from storms at a hex location. Queries the galaxy's zone spatial index and combines effects from overlapping storms.

**Dependencies:** None (no constructor args).

**Data Type:**
```python
@dataclass
class EnvironmentalEffects:
    shield_capacity_mult: float = 1.0   # Multiplier for shield capacity
    thrust_mult: float = 1.0            # Multiplier for tactical movement
    strategic_mult: float = 1.0         # Multiplier for strategic movement speed
    damage_per_tick: float = 0.0        # Hull damage per tick in storm
    fuel_drain_per_tick: float = 0.0    # Fuel consumed per tick in storm
    in_storm: bool = False              # True if any storm is present
    storm_names: List[str]              # Names of storms at this location
```

**Stacking rules:** Multiplicative effects stack multiplicatively; additive effects sum.

**Key Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_effects_at_global_hex` | `(galaxy, global_hex) -> EnvironmentalEffects` | Get aggregated storm effects at a hex; returns neutral effects if no storms |

**Usage:**
```python
from game.strategy.services.area_effect_manager import AreaEffectManager

manager = AreaEffectManager()
effects = manager.get_effects_at_global_hex(galaxy, fleet.location)
if effects.in_storm:
    print(f"In storm: shields at {effects.shield_capacity_mult:.0%}")
```

---

### ComponentInspector (module-level functions)

**Location:** `game/strategy/services/component_inspector.py`

**Purpose:** Utility functions for inspecting ship/facility design components and abilities. Consolidates duplicated component/ability iteration patterns from strategy layer validators.

**Dependencies:** None (all functions are stateless). Accept `component_registry: Dict[str, Any]` as parameter where needed.

**Key Functions:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_component_abilities` | `(comp_def) -> Dict[str, Any]` | Extract abilities dict from a component definition (dict or Component object) |
| `get_component_type` | `(comp_def) -> str` | Extract component type string from a definition |
| `get_component_threshold` | `(comp_def, default) -> float` | Extract damage threshold from a definition |
| `iterate_design_components` | `(design_data, component_registry) -> Iterator[Tuple[dict, Any, dict]]` | Iterate all components in a design, yielding (entry, definition, abilities) |
| `ship_has_ability` | `(ship, ability_name, component_registry) -> bool` | Check if a ship has a component with a specific ability |
| `find_ship_with_ability` | `(fleet_ships, ability_name, component_registry) -> Optional[ShipInstance]` | Find first ship in a list with a specific ability |
| `count_ability` | `(ship, ability_name, component_registry) -> int` | Count components on a ship with a specific ability |
| `list_ship_abilities` | `(ship, component_registry) -> List[str]` | Get all unique ability names from a ship's components |
| `get_ability_list` | `(abilities, ability_name) -> List[Dict]` | Normalize ability data to list of dicts (handles single/list/scalar formats) |
| `has_warp_capability` | `(ship) -> bool` | Check if a ship has functional warp (tonnage, storage, undamaged drive) |

**`get_ability_list`** is the canonical way to extract ability data from component ability dicts. Always use this instead of manually checking `isinstance(val, list)` — it handles all formats: single dicts, lists, and scalar values.

**`has_warp_capability`** checks warp tonnage >= ship mass, and that the ship has enough resource storage for at least one warp jump. Uses `get_calculated_stats()` so it respects damage state.

**Usage:**
```python
from game.strategy.services.component_inspector import (
    ship_has_ability, find_ship_with_ability, iterate_design_components,
    get_ability_list, has_warp_capability,
)

# Check if ship can colonize
if ship_has_ability(ship, 'ColonizePlanet', component_registry):
    print("Ship has colony pod")

# Find a colonizer in the fleet
colonizer = find_ship_with_ability(fleet.ships, 'ColonizePlanet', component_registry)

# Iterate all components
for entry, comp_def, abilities in iterate_design_components(design_data, registry):
    print(f"Component {entry.get('id')}: {list(abilities.keys())}")

# Normalize ability data (handles single dict, list, or scalar)
for ability_data in get_ability_list(abilities, 'ResourceConsumption'):
    print(f"Consumes {ability_data.get('resource')}: {ability_data.get('amount')}")

# Check warp capability
if has_warp_capability(ship_instance):
    print("Ship can use warp points")
```

---

### Race Habitability & Point-Buy (PROJ-283)

**Locations:**
- `game/strategy/data/environmental_preference.py` — `EnvironmentalPreference(setpoint, tolerance, min_value, max_value, step)` dataclass
- `game/strategy/data/habitability_factors.py` — `HabitabilityFactor` dataclass + module-level `FACTOR_REGISTRY: Dict[str, HabitabilityFactor]` (7 scalar factors + 10 gas factors); `get_factor(id)`, `iter_scalar_factors()`, `iter_gas_factors()` lookup helpers
- `game/strategy/data/race_config.py` — `RaceConfig.preferences: Dict[str, EnvironmentalPreference]` (registry-keyed, backfilled from `FACTOR_REGISTRY` defaults via `__post_init__`); `RaceConfig.base_reproduction_rate: float = 0.03`; `RaceConfig.base_happiness: float = 0.5`
- `game/strategy/data/race_point_budget.py` — `RacePointBudget` instance methods: `calculate_aptitude_cost`, `calculate_preferences_cost`, `calculate_reproduction_cost(rate)`, `calculate_total_cost`, `get_remaining_points`, `is_within_budget`, `get_aptitude_breakdown`, `get_breakdown`
- `game/strategy/data/homeworld_presets.py` — `apply_preset_to_config(preset, race_config)` overlays a preset's partial `preferences` dict onto a race
- `game/strategy/formulas/habitability.py` — `calculate_habitability(planet, race_config) -> float` iterates `FACTOR_REGISTRY` and combines per-factor scores via weighted geometric mean; `score_planet_for_race(planet, race_config)` is a thin wrapper

**Pattern (PROJ-283):** "Add an axis with one data edit." Adding a `HabitabilityFactor` registration to `FACTOR_REGISTRY` automatically surfaces the factor in `calculate_habitability`, `RacePointBudget`, the race-setup UI panel, the homeworld preset translation, and the population engine — no code changes elsewhere required. Per-factor weights tune the importance of each axis in the weighted-geometric-mean combiner. The `(setpoint, tolerance)` UX contract is universal: setpoint is free, tolerance deviation from the registry default costs `_exponential_cost(steps) = 2^steps - 1`.

**Cost methods:**

| Method | Returns | Notes |
|--------|---------|-------|
| `calculate_aptitude_cost(rc)` | int | Sum across the 7 paid aptitudes (Phase 3 dropped `happiness` and `population_growth` — both replaced by `base_*` floats on RaceConfig). |
| `calculate_preferences_cost(rc)` | int | Sum of per-axis tolerance-deviation costs across all 17 factors. |
| `calculate_reproduction_cost(rate)` | int | Exponential cost above default 3%; linear refund (2 pts per 1% step) below default down to 0.5% floor. Linear-in-rate math (not integer-step) so the floor returns -5 exactly. |
| `calculate_total_cost(rc)` | int | Sum of the three above. |
| `get_remaining_points(rc)` | int | `total_budget − total_cost`. |
| `get_breakdown(rc)` | Dict[str, int] | Flat per-source breakdown: `aptitude:strength`, `pref:gravity`, `reproduction`, etc. Sum equals `calculate_total_cost(rc)`. |

See [docs/systems/strategy_layer.md §7](systems/strategy_layer.md#7-race-preferences--habitability-proj-283) for the full architecture, weight table, adding-a-factor recipe, and the legacy → new field migration table.

### Colony Demographics Loop (PROJ-284)

**Locations:**
- `game/strategy/data/colony_species_config.py` — `ColonySpeciesConfig(food_allocation: float = 1.0, last_food_ratio: float = 1.0)` per-colony per-species dataclass stored as `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`. `to_dict` excludes the transient `last_food_ratio`; `from_dict` always resets it to 1.0. `__post_init__` validates `food_allocation >= 0`. `Planet.get_species_config(race_id)` is a lazy-create-and-store helper.
- `game/strategy/config/economy_config.py` — `EconomyConfig(population_food_resource, food_per_pop_per_turn)` frozen dataclass. Loader `load_economy_config(path=None)` + module-accessor singleton (`get_default_economy_config` / `set_default_economy_config`) per the CLAUDE.md `get_default_*` pattern. Graceful fallback to defaults on missing/malformed `data/economy.json`.
- `data/economy.json` — `{"population_food_resource": "organics", "food_per_pop_per_turn": 0.001}`. Modders swap `"organics"` for any `resources.json` id; UI auto-relabels via `ResourceCatalog.get(id).name`.
- `game/strategy/engine/organics_consumption_engine.py` — `OrganicsConsumptionEngine.process_consumption(empires) -> None`. Drains `needed = pop.count * food_allocation * food_per_pop_per_turn` from each colony's `stockpile[food_resource]`, caps at available, writes `cfg.last_food_ratio = supplied / needed` (or 1.0 for zero-need edge cases).
- `game/strategy/engine/happiness_engine.py` — `HappinessEngine.process_happiness(empires, galaxy) -> None`. Writes `pop.happiness = clamp(race.base_happiness * cfg.last_food_ratio * habitability, 0, 3)` via `score_planet_for_race(planet, race_config)`. Unbounded above 1.0 (up to 3x) so over-supply + ideal habitability can boost growth past the neutral point.
- `game/strategy/engine/population_engine.py` — `PopulationEngine._grow_species` reworked: `growth = (base_reproduction_rate * last_food_ratio) * P * (1 - P/K_eff) * happiness + decline_term`, where `K_eff = max(1.0, max_population * habitability)` and `decline_term = -DECLINE_RATE * P * (1 - last_food_ratio)` when `last_food_ratio < 1.0` else 0. `DECLINE_RATE = 0.02` module constant.
- `game/strategy/interfaces/engines.py` — `IOrganicsConsumptionEngine`, `IHappinessEngine` protocols. Both wired onto `TurnEngineConfig` (fields 14 + 15) and `TurnEngine.__init__` kwargs.
- `game/ui/screens/food_allocation_editor.py` — `FoodAllocationEditor` pygame_gui window with per-species slider (0.0–5.0, step 0.05) + typed input (accepts any non-negative value) + live consumption preview. Title reads `{resource.name} Allocation — {planet.name}`. Apply callback writes to `planet.get_species_config(race_id).food_allocation`. Module-level pure helpers (`gather_rows`, `resolve_food_resource_name`, `compute_consumption_preview`, `apply_allocations`) are testable without pygame.

**Turn order (post-PROJ-284):** `[100-tick loop] → OrganicsConsumptionEngine.process_consumption → HappinessEngine.process_happiness → PopulationEngine.process_population_growth → QualityEngine → AtmosphereEngine → WaterEngine`.

**Transient-field contract:** `ColonySpeciesConfig.last_food_ratio` is TRANSIENT. Engines MUST overwrite it every turn — `OrganicsConsumptionEngine` writes 1.0 explicitly for zero-population / zero-allocation edge cases so downstream readers (HappinessEngine, PopulationEngine) never see a stale carry-over. Saving it would misrepresent post-load demographic state.

**UI surface:** `FoodAllocationEditor` is opened from `PlanetAbilitiesWindow` via the "Food" button (population-driven — shown when `planet.populations` is non-empty, NOT gated on a facility ability). Routed through `strategy_window_manager._open_planet_editor` → `strategy_event_router._open_food_allocation_editor`. Direct mutation on `ColonySpeciesConfig.food_allocation` (no command class; food allocation is a player-facing dial, not a replayable strategy command).

See [docs/systems/strategy_layer.md §8](systems/strategy_layer.md#8-colony-demographics-loop-proj-284) for the full pipeline, formula derivations, and the "swap the food resource" recipe.

### Colony Economy Multiplier (PROJ-285)

**Locations:**
- `game/strategy/formulas/colony_output.py` — `planet_habitability_multiplier(planet, race_registry) -> float` pure helper. Population-weighted mean of `score_planet_for_race(planet, race_for(pop))` across `planet.populations`. Uncolonized planets / missing-race-all-species / zero-total-count return 1.0. Species with missing `race_id` in the registry are excluded from BOTH numerator and denominator (not scored as 0) — save-drift defence.
- `game/strategy/data/planet.py` — `Planet.get_cached_habitability_multiplier(race_registry, turn) -> float` per-turn cache accessor. Fields `_cached_habitability_multiplier` + `_cached_multiplier_turn` are `init=False, compare=False` and NOT emitted by `to_dict` — post-load planets re-warm on first read.
- `game/strategy/engine/harvesting_engine.py` — `HarvestingEngine.__init__(registries, race_registry=None)`. When `race_registry` is None (legacy pattern), habitability hook short-circuits to 1.0. New kwarg preserves 850+ lines of pre-PROJ-285 MagicMock-based tests without retargeting. `_get_habitability_mult(colony)` + `set_current_turn(turn)` helpers.
- `game/strategy/engine/production_engine.py` — `ProductionEngine.__init__(registries, race_registry=None, event_bus=None)`. Same short-circuit behavior. The hook in `_process_queue_tick_dynamic` scales the `production_rate` dict BEFORE the tick-capacity while-loop runs — downstream math honors the multiplier automatically. Fleet queues always get 1.0 (no planet context).
- `game/strategy/engine/turn_engine.py` — `process_turn` calls `set_current_turn(session.turn_number)` on both harvesting + production engines before the 100-tick loop (guarded with `getattr` so mock engines don't break).

**Turn flow:** Habitability is computed ONCE per colony per turn (first read wins), then reused across all 100 tick iterations of harvest + production. The cache invalidates at each turn boundary when `TurnEngine` bumps the engine's `_current_turn`.

**Stacks alongside:**
- `ResourceHarvestBooster` aggregation (`aggregate_multipliers` in `game/strategy/services/strategic_ability_scanner.py`) — harvest path.
- `BuildRateBooster` aggregation (same scanner) — production path.

Multiplicative: `effective_rate = base_rate * booster_mult * habitability_mult`.

See [docs/systems/production_system.md § Habitability Multiplier](systems/production_system.md#habitability-multiplier-proj-285) and [docs/systems/strategy_layer.md §9](systems/strategy_layer.md#9-colony-economy-multiplier-proj-285).

---

## Design Principles

### 1. Strict Dependency Injection

All services that need registries use **constructor injection with no fallback**:

```python
# Correct
service = VehicleDesignService(registries=game_registries)
service = ModifierLogicService(registry_provider=game_registries)
loader = SimulationDesignLoader(registries=game_registries)

# Raises TypeError or ValidationException
service = VehicleDesignService(registries=None)
```

Stateless services require no constructor args:
```python
service = BattleService()
nav_service = FleetNavigationService()
manager = AreaEffectManager()
# FleetSpeedCalculator, ActionTimeResolver, DesignCostCalculator use only static methods
```

### 2. Result Objects

Services return result objects for operations that can fail, rather than raising exceptions:

```python
@dataclass
class ServiceResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

**Handling results:**
```python
result = service.some_operation()
if result.success:
    process(result.data)
else:
    for error in result.errors:
        logger.error(error)

for warning in result.warnings:
    logger.warning(warning)
```

### 3. Pure Functions Where Possible

`FleetNavigationService` demonstrates the pattern of separating pure computation from mutation:
- **Pure core:** `compute_next_step(state, galaxy) -> NavigationStep` -- no side effects
- **Mutation bridge:** `calculate_fleet_next_hex(fleet, galaxy)` -- wraps pure function, applies changes to Fleet

### 4. Static Methods for Stateless Logic

`FleetSpeedCalculator`, `ActionTimeResolver`, `DesignCostCalculator`, `CargoTransferService`, and `FleetCargoProjector` are entirely static -- no instance state needed. `ComponentInspector` uses module-level functions rather than a class — including `has_warp_capability()` and `get_ability_list()`. `calculate_design_stats()` is a standalone function in `game/simulation/entities/ship_design_stats.py`.

---

## Layer Separation

```
+---------------------------------------------------------+
|                      UI Layer                           |
|  (builder_screen.py, battle_scene.py, strategy_screen)  |
+----------------------------+----------------------------+
                             | Uses
                             v
+---------------------------------------------------------+
|                   Service Layer                         |
|  Simulation: BattleService, VehicleDesignService,       |
|              ModifierService, SimulationDesignLoader,    |
|              reload_registries_from_directory            |
|  Strategy:   FleetNavigationService,                    |
|              FleetSpeedCalculator, ComponentInspector,   |
|              ActionTimeResolver, CargoTransferService,   |
|              DesignCostCalculator, FleetCargoProjector,  |
|              AreaEffectManager, SystemEffectsCollector,  |
|              BuildQueueController, BuildQueueRenderer    |
+----------------------------+----------------------------+
                             | Uses
                             v
+---------------------------------------------------------+
|                   Domain Layer                          |
|  (Ship, Component, BattleEngine, Fleet, Galaxy)         |
+---------------------------------------------------------+
```

**Rules:**
- UI can import services
- Services can import domain objects
- Domain should NOT import services or UI
- UI should NOT directly manipulate domain objects for complex operations

---

## Testing Services

Services are tested in:
```
tests/unit/services/                    # Simulation services
tests/unit/strategy/services/           # Strategy services
```

**Example Test:**
```python
class TestVehicleDesignService:
    def test_create_ship_returns_valid_ship(self, registries):
        service = VehicleDesignService(registries=registries)
        result = service.create_ship(
            name="Test Ship",
            ship_class="Escort",
            theme_id="Federation"
        )
        assert result.success is True
        assert result.ship is not None
        assert result.ship.name == "Test Ship"

    def test_add_invalid_component_returns_error(self, registries):
        service = VehicleDesignService(registries=registries)
        result = service.create_ship("Test", "Escort")
        ship = result.ship

        result = service.add_component(ship, "nonexistent_component", LayerType.OUTER)
        assert not result.success
        assert len(result.errors) > 0
```

---

*Last Updated: April 2026*
