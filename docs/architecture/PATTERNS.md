# Design Patterns in Starship Battles

## Overview

This document describes the key design patterns used throughout the Starship Battles codebase, their implementations, and guidelines for consistent usage.

## Table of Contents

1. [Singleton Pattern](#singleton-pattern)
2. [Mixin Pattern](#mixin-pattern)
3. [Event Bus Pattern](#event-bus-pattern)
4. [Template Method Pattern](#template-method-pattern)
5. [Configuration Pattern](#configuration-pattern)
6. [ViewModel Pattern (MVVM)](#viewmodel-pattern-mvvm)
7. [Type-Safe Data Access](#type-safe-data-access)
8. [Renderer Decomposition](#renderer-decomposition)
9. [Surface Caching](#surface-caching)
10. [Modal Window Tracking](#modal-window-tracking)
11. [Naming Conventions](#naming-conventions) *(see [NAMING_CONVENTIONS.md](NAMING_CONVENTIONS.md))*
12. [Validation System Limitations](#validation-system-limitations)

---

## Singleton Pattern

### Purpose

Ensure a class has only one instance and provide global access to it. Used for managers that need consistent global state.

### Implementation

The codebase uses a thread-safe singleton pattern with double-checked locking:

```python
import threading
from typing import Optional

class StrategyManager:
    _instance: Optional['StrategyManager'] = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls) -> 'StrategyManager':
        """Get the singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for testing."""
        with cls._lock:
            cls._instance = None

    def clear(self) -> None:
        """Clear data while keeping instance."""
        self._strategies = {}
        self._loaded = False
```

### Singletons in Codebase

| Class | Location | Purpose | Access Pattern |
|-------|----------|---------|----------------|
| `RegistryManager` | `game/core/registry.py` | Component/modifier definitions | Via `get_default_registry_provider()` |
| `StrategyManager` | `game/ai/controller.py` | AI combat strategies | Direct singleton |
| `ShipThemeManager` | `game/ui/assets/ship_theme_manager.py` | Visual themes | Direct singleton |
| `ScreenshotManager` | `game/core/screenshot_manager.py` | Screenshot handling | Direct singleton |
| `SpriteManager` | `game/ui/renderer/sprites.py` | Sprite caching | Direct singleton |
| `SessionRegistryCache` | `tests/infrastructure/session_cache.py` | Test data caching | Direct singleton |

### Registry Access Pattern

**For registry access, use the provider pattern instead of direct singleton access:**

```python
from game.core.registry import get_default_registry_provider

# Recommended: Use the provider interface
provider = get_default_registry_provider()
components = provider.get_components()
modifiers = provider.get_modifiers()
ships = provider.get_ships()
```

`RegistryManager.instance()` is **internal-only** for composition roots (app startup, test fixtures).
Consumer code should use `get_default_registry_provider()` or accept an `IRegistryProvider` via dependency injection.

### Usage Guidelines

1. **Always use `instance()`** - Never instantiate singletons directly
2. **Implement `reset()`** - Required for test isolation
3. **Implement `clear()`** - For resetting data without destroying instance
4. **Test fixtures should reset** - Call `reset()` in teardown
5. **Prefer provider pattern** - For registries, use `get_default_registry_provider()` instead of direct singleton access

### Testing Singletons

```python
# conftest.py
@pytest.fixture(autouse=True)
def reset_game_state():
    yield
    # Reset singletons after each test
    StrategyManager.instance().clear()
    ShipThemeManager.reset()
    SpriteManager.reset()
    # Note: RegistryManager is handled separately via the registry_provider fixture
```

For registry testing, use the `registry_provider` fixture which handles setup and teardown automatically.

---

## Mixin Pattern

### Purpose

Add functionality to classes through multiple inheritance without deep hierarchies. Used for composing Ship behavior from multiple sources.

### Implementation

Ship uses mixins for combat and physics behavior:

```python
# ship_combat.py
class ShipCombatMixin:
    """Combat-related ship methods."""

    def fire_weapons(self):
        """Fire all ready weapons at current target."""
        for weapon in self.get_operational_weapons():
            if weapon.can_fire():
                weapon.fire(self.current_target)

    def take_damage(self, amount, damage_type):
        """Apply damage to ship layers."""
        # Implementation...

# ship_physics.py
class ShipPhysicsMixin:
    """Physics and movement ship methods."""

    def thrust_forward(self):
        """Apply forward thrust."""
        # Implementation...

    def rotate(self, direction):
        """Rotate ship by direction (-1 or 1)."""
        # Implementation...

# ship.py
class Ship(PhysicsBody, ShipCombatMixin, ShipPhysicsMixin):
    """Main ship class composing all mixins."""

    def __init__(self, name, ship_class):
        super().__init__(0, 0)
        # Ship-specific initialization...
```

### Guidelines

1. **Mixins should be stateless** - They add behavior, not state
2. **Use `self` for accessing host attributes** - Mixins rely on the host class
3. **Document expected attributes** - What the mixin expects from its host
4. **No `__init__` in mixins** - Let the host class handle initialization

---

## Event Bus Pattern

### Purpose

Decouple event producers from consumers through a publish-subscribe mechanism.

### Implementation

```python
# ui/builder/event_bus.py
import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    def emit(self, event_type: str, *args, **kwargs) -> None:
        """Emit an event to all subscribers."""
        if event_type not in self._subscribers:
            return

        # Defensive copy to allow modifications during iteration
        for callback in list(self._subscribers[event_type]):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Error in event handler for {event_type}: {e}")
```

### Event Type Constants

Use string constants to avoid typos and enable IDE autocomplete:

```python
# game/ui/screens/builder_utils.py
class BuilderEvents:
    """Event type constants for the Builder EventBus."""
    SHIP_UPDATED = 'SHIP_UPDATED'
    SELECTION_CHANGED = 'SELECTION_CHANGED'
    REGISTRY_RELOADED = 'REGISTRY_RELOADED'
    TEMPLATE_MODIFIERS_CHANGED = 'TEMPLATE_MODIFIERS_CHANGED'
    DRAG_STATE_CHANGED = 'DRAG_STATE_CHANGED'
    HULL_LAYER_VISIBILITY_CHANGED = 'HULL_LAYER_VISIBILITY_CHANGED'
```

### Event Naming Conventions

1. **Use SCREAMING_SNAKE_CASE** for event type constants
2. **Past tense or state change** - `SHIP_UPDATED`, `SELECTION_CHANGED`
3. **Group by domain** - All builder events in `BuilderEvents` class
4. **Descriptive payloads** - Document what data each event carries

### Usage

```python
from game.ui.screens.builder_utils import BuilderEvents

# Publisher (in ViewModel)
def _emit_ship_updated(self):
    self.event_bus.emit(BuilderEvents.SHIP_UPDATED, self._ship)

# Subscriber (in View/Panel)
def __init__(self, event_bus):
    event_bus.subscribe(BuilderEvents.SHIP_UPDATED, self._on_ship_updated)

def _on_ship_updated(self, ship):
    """Refresh panel when ship changes."""
    self.refresh()
```

---

## Template Method Pattern

### Purpose

Define a skeleton algorithm with customizable steps. Used in validation rules to eliminate duplicate guard clauses.

### Implementation

```python
# game/simulation/validation/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ValidationResult:
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class ValidationRule(ABC):
    """Base class for validation rules using template method."""

    def validate(self, ship, component=None, layer_type=None) -> ValidationResult:
        """Template method - orchestrates validation."""
        # Guard clause handled once in base class
        if not self._should_validate(component, layer_type):
            return ValidationResult(True)

        # Delegate to subclass for actual validation
        return self._do_validate(ship, component, layer_type)

    def _should_validate(self, component, layer_type) -> bool:
        """Override to customize when validation runs."""
        return component is not None and layer_type is not None

    @abstractmethod
    def _do_validate(self, ship, component, layer_type) -> ValidationResult:
        """Implement actual validation logic."""
        pass
```

### Usage

```python
class LayerCapacityRule(ValidationRule):
    """Validate layer has capacity for component."""

    def _do_validate(self, ship, component, layer_type) -> ValidationResult:
        layer = ship.layers.get(layer_type)
        if not layer:
            return ValidationResult(False, [f"Layer {layer_type} not found"])

        if len(layer['components']) >= layer['max_capacity']:
            return ValidationResult(False, [f"Layer {layer_type} at capacity"])

        return ValidationResult(True)


class UniqueComponentRule(ValidationRule):
    """Validate one-per-ship components."""

    def _should_validate(self, component, layer_type) -> bool:
        # Only validate components marked as unique
        return component and getattr(component, 'unique', False)

    def _do_validate(self, ship, component, layer_type) -> ValidationResult:
        existing = ship.get_component_by_id(component.id)
        if existing:
            return ValidationResult(False, [f"{component.name} already installed"])
        return ValidationResult(True)
```

---

## Configuration Pattern

### Purpose

Centralize magic numbers and configuration values in typed, documented classes.

### Implementation

```python
# game/core/config.py
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class DisplayConfig:
    """Display and resolution configuration."""
    DEFAULT_WIDTH: int = 2560
    DEFAULT_HEIGHT: int = 1600
    TEST_WIDTH: int = 1440
    TEST_HEIGHT: int = 900

    @classmethod
    def default_resolution(cls) -> Tuple[int, int]:
        return (cls.DEFAULT_WIDTH, cls.DEFAULT_HEIGHT)

    @classmethod
    def test_resolution(cls) -> Tuple[int, int]:
        return (cls.TEST_WIDTH, cls.TEST_HEIGHT)

@dataclass(frozen=True)
class AIConfig:
    """AI behavior configuration."""
    MIN_SPACING: int = 150
    DEFAULT_ORBIT_DISTANCE: int = 500
    MAX_CORRECTION_FORCE: int = 500

@dataclass(frozen=True)
class PhysicsConfig:
    """Physics simulation configuration."""
    TICK_RATE: float = 0.01  # 100 ticks per second
```

### Usage

```python
from game.core.config import DisplayConfig, AIConfig, PhysicsConfig

# Display setup
WIDTH, HEIGHT = DisplayConfig.default_resolution()

# AI behaviors
class KiteBehavior(AIBehavior):
    MIN_SPACING: int = AIConfig.MIN_SPACING

# Physics
dt = PhysicsConfig.TICK_RATE
```

### UI Layout Configuration

For UI panels and screens, use the same frozen dataclass pattern:

```python
# game/ui/screens/builder_utils.py
from dataclasses import dataclass

@dataclass(frozen=True)
class PanelWidths:
    """Fixed panel widths (in pixels)."""
    component_palette: int = 400   # Left panel - component selection
    layer_panel: int = 500         # Layer/structure view
    right_panel: int = 750         # Ship stats and portrait
    detail_panel: int = 500        # Component detail overlay

@dataclass(frozen=True)
class PanelHeights:
    """Fixed panel heights (in pixels)."""
    bottom_bar: int = 60           # Bottom button bar
    weapons_report: int = 400      # Weapons report panel
    modifier_panel: int = 400      # Modifier editor

@dataclass(frozen=True)
class Margins:
    """Standard spacing values."""
    edge: int = 20                 # Edge padding from screen borders
    gutter: int = 10               # Gap between adjacent panels
    section: int = 20              # Space between logical sections

# Singleton instances for easy import
PANEL_WIDTHS = PanelWidths()
PANEL_HEIGHTS = PanelHeights()
MARGINS = Margins()
```

### Layout Helper Functions

```python
def calculate_center_width(screen_width: int) -> int:
    """Calculate available width for center content area."""
    return screen_width - PANEL_WIDTHS.component_palette - PANEL_WIDTHS.right_panel

def calculate_dynamic_layer_width(screen_width: int) -> int:
    """Calculate a responsive layer panel width based on available space."""
    center = calculate_center_width(screen_width)
    dynamic_width = int(center * 0.375)
    return max(375, min(625, dynamic_width))  # Clamped to reasonable bounds
```

### Guidelines

1. **Use `frozen=True`** - Configuration should be immutable
2. **Group related values** - One config class per domain
3. **Add helper methods** - For common operations like resolution tuples
4. **Document units** - Especially for time (seconds vs ticks), pixels vs percentages
5. **Import from module** - `from game.core.config import AIConfig`
6. **Create singletons** - For frequently-used layout constants (e.g., `PANEL_WIDTHS`)
7. **Provide helper functions** - For dynamic calculations based on screen size

---

## ViewModel Pattern (MVVM)

### Purpose

Separate UI presentation logic from business logic using a Model-View-ViewModel architecture.
The ViewModel acts as an intermediary between the View (UI panels) and the Model (domain objects),
managing state and emitting events when state changes.

### Implementation

The Design Workshop uses this pattern for its ship builder UI:

```python
# game/ui/screens/workshop_viewmodel.py

class WorkshopViewModel:
    """
    Central ViewModel for Design Workshop.

    Holds all builder state and emits events via EventBus when state changes.
    Views subscribe to events and update themselves accordingly.
    """

    def __init__(self, event_bus, screen_width: int, screen_height: int):
        self.event_bus = event_bus

        # Service layer for ship operations
        self._ship_service = ShipBuilderService()

        # Core state
        self._ship: Optional[Ship] = None
        self._selected_components: List[Tuple[LayerType, int, Component]] = []
        self._dragged_item: Optional[Component] = None

    @property
    def ship(self) -> Optional[Ship]:
        """The ship currently being edited."""
        return self._ship

    @ship.setter
    def ship(self, value: Ship):
        self._ship = value
        self._emit_ship_updated()

    def _emit_ship_updated(self):
        """Emit SHIP_UPDATED event."""
        self.event_bus.emit(BuilderEvents.SHIP_UPDATED, self._ship)

    def add_component(self, component_id: str, layer: LayerType) -> bool:
        """Add a component using the service layer."""
        result = self._ship_service.add_component(self._ship, component_id, layer)
        if result.success:
            self.notify_ship_changed()
        return result.success
```

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       View Layer                                 │
│  ComponentPalettePanel  │  LayerPanel  │  ModifierEditorPanel   │
│         ↓ subscribe                ↓ subscribe                   │
├─────────────────────────────────────────────────────────────────┤
│                    WorkshopViewModel                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  State: ship, selected_components, dragged_item          │   │
│  │  Events: SHIP_UPDATED, SELECTION_CHANGED, DRAG_STATE_...│   │
│  └──────────────────────────────────────────────────────────┘   │
│         ↓ delegates to                                           │
├─────────────────────────────────────────────────────────────────┤
│                    Service Layer                                 │
│              ShipBuilderService (validation, operations)         │
├─────────────────────────────────────────────────────────────────┤
│                    Model Layer                                   │
│              Ship, Component, LayerType                          │
└─────────────────────────────────────────────────────────────────┘
```

### Event Types

| Event | Payload | Trigger |
|-------|---------|---------|
| `SHIP_UPDATED` | `Ship` | Ship properties or components change |
| `SELECTION_CHANGED` | `Optional[Tuple]` | Component selection changes |
| `DRAG_STATE_CHANGED` | `Optional[Component]` | Drag operation starts/ends |
| `TEMPLATE_MODIFIERS_CHANGED` | `Component` | Template modifier values change |
| `HULL_LAYER_VISIBILITY_CHANGED` | `bool` | Hull layer toggle |

### Usage

```python
# View subscribes to events
class ComponentPalettePanel:
    def __init__(self, viewmodel: WorkshopViewModel):
        self.viewmodel = viewmodel
        viewmodel.event_bus.subscribe(
            BuilderEvents.SHIP_UPDATED,
            self._on_ship_updated
        )

    def _on_ship_updated(self, ship: Ship):
        """Refresh panel when ship changes."""
        self.refresh_component_list()

# View calls ViewModel methods
class LayerPanel:
    def on_component_drop(self, component_id: str, layer: LayerType):
        """Handle component drop onto layer."""
        success = self.viewmodel.add_component(component_id, layer)
        if not success:
            self.show_error(self.viewmodel.last_errors)
```

### Guidelines

1. **State lives in ViewModel** - Views should be stateless display logic
2. **Use EventBus for notifications** - Don't call view methods directly from ViewModel
3. **Delegate to services** - ViewModel orchestrates, services implement business logic
4. **Properties emit events** - Use setter properties to automatically notify on change
5. **Handle errors in ViewModel** - Expose `last_errors` for views to display
6. **Single source of truth** - Only ViewModel holds authoritative state

### Testing

```python
def test_add_component_emits_event():
    event_bus = EventBus()
    vm = WorkshopViewModel(event_bus, 1920, 1080)
    vm.create_default_ship()

    received = []
    event_bus.subscribe(BuilderEvents.SHIP_UPDATED, lambda s: received.append(s))

    vm.add_component("basic_engine", LayerType.INTERNAL)

    assert len(received) == 1
    assert received[0] == vm.ship
```

---

## Type-Safe Data Access

### Purpose

Provide safe access to object attributes when the attribute may be optional or vary between
object types. Common in UI code that renders heterogeneous collections.

### When to Use `getattr`

**Legitimate uses:**
- Optional attributes that may not exist on all instances
- Backward compatibility with older object versions
- Polymorphic rendering of different object types
- Default fallback values for missing data

**Avoid when:**
- The attribute should always exist (use direct access instead)
- Type checking could be done once at the container level
- A Protocol/ABC could define the expected interface

### Patterns

**1. Optional attributes with defaults:**
```python
# Good - is_derelict is optional on Ship
is_derelict = getattr(ship, 'is_derelict', False)

# Good - crew system is optional
crew_required = getattr(ship, 'crew_required', 0)
crew_onboard = getattr(ship, 'crew_onboard', 0)
```

**2. Polymorphic access with fallback chain:**
```python
# Good - target could be Ship or Projectile
target_name = getattr(target, 'name', getattr(target, 'type', 'Unknown').title())
```

**3. Enum/status with default:**
```python
from game.simulation.components.component import ComponentStatus

# Good - status may not be set on older components
status = getattr(comp, 'status', ComponentStatus.ACTIVE)
```

### Preferred Alternatives

**Protocol for expected interfaces:**
```python
from typing import Protocol

class Targetable(Protocol):
    """Interface for objects that can be targeted."""
    @property
    def name(self) -> str: ...
    @property
    def position(self) -> Vector2: ...

def render_target(target: Targetable):
    # Direct access - no getattr needed
    label = target.name
```

**Type hints with Optional:**
```python
from typing import Optional

class Ship:
    is_derelict: bool = False  # Always defined with default
    secondary_targets: Optional[List['Ship']] = None  # Explicitly optional
```

### Guidelines

1. **Document optional attributes** - Use type hints with `Optional[T]`
2. **Provide sensible defaults** - `getattr(obj, 'attr', sensible_default)`
3. **Prefer Protocols** - When multiple types share the same interface
4. **Use constants for defaults** - Import from config instead of magic values
5. **Consider DTO/ViewModel** - For complex UI data, create a dedicated class

### Data Contracts

Key UI data contracts in the codebase:

| Object | Required Attributes | Optional Attributes |
|--------|---------------------|---------------------|
| Ship | `name`, `is_alive`, `position`, `team_id` | `is_derelict`, `current_target`, `crew_*` |
| Component | `id`, `name`, `is_active` | `status`, `shots_fired`, `shots_hit` |
| Projectile | `position`, `velocity` | `target`, `hp`, `endurance`, `status` |

---

## Renderer Decomposition

### Purpose

Break down complex rendering code into focused methods, each responsible for
drawing a specific category of objects. This improves readability and testability.

### Implementation

```python
# game/ui/screens/strategy_renderer.py

class StrategyRenderer:
    """Handles all rendering for the strategy map."""

    def __init__(self, scene):
        self.scene = scene  # Reference to data source

    def draw(self, screen):
        """Main entry point - orchestrates sub-renderers."""
        self._draw_grid(screen)
        self._draw_warp_lanes(screen)
        self._draw_systems(screen)
        self._draw_fleets(screen)
        self._draw_hover_hex(screen)
        self._draw_move_preview(screen)

    def _draw_grid(self, screen):
        """Draw hex grid background."""
        # ... grid rendering logic

    def _draw_systems(self, screen):
        """Draw star systems with planets."""
        for sys in self.systems:
            self._draw_system_details(screen, sys)

    def _draw_system_details(self, screen, sys):
        """Draw individual system and its planets."""
        # ... detailed system rendering
```

### Naming Conventions

| Method Prefix | Purpose | Example |
|---------------|---------|---------|
| `draw()` | Public entry point | `draw(screen)` |
| `_draw_*` | Private sub-renderers | `_draw_grid()`, `_draw_fleets()` |
| `_draw_*_details` | Detailed item rendering | `_draw_system_details()` |
| `_draw_*_overlay` | Overlays/effects | `_draw_hover_overlay()` |

### Scene/Renderer Separation

```
┌─────────────────────────────────────────┐
│            Screen (e.g., StrategyScreen) │
│  - Input handling                        │
│  - UI widgets (buttons, panels)          │
│  - Coordinates scene and renderer        │
├─────────────────────────────────────────┤
│            Scene (e.g., StrategyScene)   │
│  - Game state (galaxy, fleets, camera)   │
│  - Selection state                       │
│  - World-to-screen coordinate mapping    │
├─────────────────────────────────────────┤
│         Renderer (e.g., StrategyRenderer)│
│  - All pygame.draw.* calls               │
│  - Sprite blitting                       │
│  - Color/visual decisions                │
└─────────────────────────────────────────┘
```

### Guidelines

1. **One method per object category** - Systems, fleets, grid, overlays
2. **Extract detail methods** - When a loop body exceeds 20 lines
3. **Use scene reference** - Renderer reads from scene, doesn't modify state
4. **Keep `draw()` simple** - Should just call sub-renderers in order
5. **Private methods for internals** - Only `draw()` is public
6. **Document render order** - Z-order matters (grid first, overlays last)

---

## Surface Caching

### Purpose

Cache expensive pygame surface operations (text rendering, rotation, scaling) to avoid
recalculating every frame.

### Implementation

```python
class GridPanel:
    def __init__(self):
        # Cache dictionary: key -> cached surface
        self._header_cache: Dict[str, pygame.Surface] = {}

    def _get_rotated_header(self, text: str) -> pygame.Surface:
        """Get a rotated header surface, using cache."""
        if text not in self._header_cache:
            # Expensive operation - render and rotate
            surf = self.header_font.render(text, True, self.COLOR_TEXT)
            rotated = pygame.transform.rotate(surf, 45)
            self._header_cache[text] = rotated
        return self._header_cache[text]

    def invalidate_cache(self):
        """Clear cache when underlying data changes."""
        self._header_cache.clear()
```

### When to Cache

| Operation | Cache? | Why |
|-----------|--------|-----|
| Font rendering | Yes | Relatively expensive per character |
| Surface rotation | Yes | Creates new surface each call |
| Surface scaling | Yes | Creates new surface each call |
| Color fills | No | Very fast, not worth caching |
| Line drawing | No | Fast, position-dependent |

### Cache Invalidation

Common invalidation triggers:
- **Data change**: Call `invalidate_cache()` when source data changes
- **Selection change**: May need to re-render highlighted items
- **Theme/color change**: Font colors or styles changed
- **Resize**: Cached surfaces may be wrong size

### Guidelines

1. **Use dict-based cache** - Simple `{key: surface}` mapping
2. **Clear on data change** - Implement `invalidate_cache()` method
3. **Key by content** - Use text/value as key, not index
4. **Don't over-cache** - Only for repeatedly-used expensive surfaces
5. **Consider memory** - Clear caches when panel is hidden

### Global Caching (SpriteManager)

For game-wide sprite caching:

```python
# game/ui/renderer/sprites.py
class SpriteManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_sprite(self, name: str, size: tuple) -> pygame.Surface:
        """Get sprite, caching by name and size."""
        key = (name, size)
        if key not in self._cache:
            self._cache[key] = self._load_and_scale(name, size)
        return self._cache[key]
```

---

## Modal Window Tracking

### Purpose

Track which popup windows are open to prevent input conflicts and ensure proper
event routing.

### Implementation

```python
# game/ui/screens/strategy_screen.py

class StrategyScreen:
    def __init__(self):
        # Track open windows - None when closed
        self.fleet_orders_window = None
        self.planet_list_window = None
        self.fleet_report_window = None

    def _has_modal_open(self) -> bool:
        """Check if any modal sub-panel is currently open."""
        if self.fleet_orders_window is not None:
            return True
        if self.planet_list_window is not None:
            return True
        if self.fleet_report_window is not None:
            return True
        return False

    def handle_event(self, event):
        # Skip game input when modal is open
        if not self._has_modal_open():
            self._handle_game_input(event)

    def open_orders_window(self, fleet):
        """Open the Fleet Orders Window."""
        if self.fleet_orders_window:
            self.fleet_orders_window.kill()  # Close existing
        self.fleet_orders_window = FleetOrdersWindow(...)

    # Handle pygame_gui close events
    def process_events(self, event):
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.fleet_orders_window:
                self.fleet_orders_window = None
            elif event.ui_element == self.fleet_report_window:
                self.fleet_report_window = None
```

### Window Types

| Window | Purpose | Modal? |
|--------|---------|--------|
| `FleetOrdersWindow` | Issue fleet commands | Yes |
| `PlanetListWindow` | View all planets | Yes |
| `FleetReportWindow` | Fleet details | Yes |
| `PlanetSelectionWindow` | Choose planet for action | Yes |

### Guidelines

1. **Null when closed** - Set window reference to `None` on close
2. **Kill before reopen** - Call `kill()` if reopening same window type
3. **Check before input** - Use `_has_modal_open()` to guard game input
4. **Handle close events** - Listen for `UI_WINDOW_CLOSE` from pygame_gui
5. **Single modal** - Generally only one modal window at a time

### Event Routing

```
Event Flow:
┌──────────────────────────────────────┐
│        pygame.event.get()             │
├──────────────────────────────────────┤
│    pygame_gui manager.process()       │
│    (handles window events internally) │
├──────────────────────────────────────┤
│    Screen.process_events()            │
│    - UI_WINDOW_CLOSE → clear ref      │
│    - UI_BUTTON_PRESSED → actions      │
├──────────────────────────────────────┤
│    if not _has_modal_open():          │
│        _handle_game_input()           │
│        (map clicks, keyboard)         │
└──────────────────────────────────────┘
```

---

## Naming Conventions

> **See [NAMING_CONVENTIONS.md](NAMING_CONVENTIONS.md) for the comprehensive naming guide** covering methods, properties, classes, constants, files, and domain-specific conventions (Battle vs Combat, Builder vs Workshop, etc.).

---

## Validation System Limitations

### Design-Time vs Runtime Stats

The validation system in `game/simulation/ship_validator.py` operates on **base stats only**, not runtime-calculated values:

```python
# ClassRequirementsRule checks ability totals
totals = calculate_ability_totals(ship.get_all_components())
if totals.get('CombatPropulsion', 0) == 0:
    result.add_error("Ship requires propulsion")
```

**Limitation**: Validation cannot access:
- Modifier-adjusted stats (only visible after `apply_modifier_effects()`)
- Stats that depend on ship state (crew manning, damage)
- Stats calculated from other stats (effective speed from thrust/mass)

### Workarounds

1. **Use base stat requirements**: Design rules check for ability presence, not calculated values
2. **Runtime validation**: Some checks happen during battle initialization
3. **Warning vs Error**: Use warnings for "soft" constraints that may resolve at runtime

### Example: Crew Requirements

```python
# Design-time: Check ability exists
if ship.has_ability('RequiresCommandAndControl'):
    if not ship.has_ability('CommandAndControl'):
        result.add_error("Ship requires Command & Control")

# Runtime: Check crew manning (in battle_engine.py)
if ship.crew_onboard < ship.crew_required:
    ship.is_operational = False
```

### Future Work

A full solution would require:
1. Evaluating modifiers during validation
2. Passing ship context (mass, class) to validation
3. Separate "design validation" vs "deployment validation" phases

This is tracked as potential future enhancement.

---

## Summary

| Pattern | Use When | Example |
|---------|----------|---------|
| Singleton | Global state needed, exactly one instance | `RegistryManager`, `StrategyManager` |
| Mixin | Adding behavior to a class | `ShipCombatMixin`, `ShipPhysicsMixin` |
| Event Bus | Decoupling publishers/subscribers | Component changes, validation events |
| Template Method | Shared algorithm with variable steps | `ValidationRule` hierarchy |
| Configuration | Centralizing constants | `DisplayConfig`, `AIConfig` |
| ViewModel (MVVM) | Separating UI state from presentation | `WorkshopViewModel` |
| Type-Safe Access | Optional attributes, polymorphic data | `getattr(ship, 'is_derelict', False)` |
| Renderer Decomposition | Complex rendering with many object types | `StrategyRenderer` with `_draw_*` methods |
| Surface Caching | Expensive rendering operations | `_header_cache` in GridPanel |
| Modal Tracking | Managing multiple popup windows | `_has_modal_open()` in StrategyScreen |
| Naming Conventions | Code readability and consistency | See [NAMING_CONVENTIONS.md](NAMING_CONVENTIONS.md) |
| Validation Limitations | Understanding design-time constraints | See [Validation System Limitations](#validation-system-limitations) |
