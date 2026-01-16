# Design Patterns in Starship Battles

## Overview

This document describes the key design patterns used throughout the Starship Battles codebase, their implementations, and guidelines for consistent usage.

## Table of Contents

1. [Singleton Pattern](#singleton-pattern)
2. [Mixin Pattern](#mixin-pattern)
3. [Event Bus Pattern](#event-bus-pattern)
4. [Template Method Pattern](#template-method-pattern)
5. [Configuration Pattern](#configuration-pattern)

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

| Class | Location | Purpose |
|-------|----------|---------|
| `RegistryManager` | `game/core/registry.py` | Component/modifier definitions |
| `StrategyManager` | `game/ai/controller.py` | AI combat strategies |
| `ShipThemeManager` | `game/simulation/ship_theme.py` | Visual themes |
| `ScreenshotManager` | `game/core/screenshot_manager.py` | Screenshot handling |
| `SpriteManager` | `game/ui/renderer/sprites.py` | Sprite caching |
| `SessionRegistryCache` | `tests/infrastructure/session_cache.py` | Test data caching |

### Usage Guidelines

1. **Always use `instance()`** - Never instantiate singletons directly
2. **Implement `reset()`** - Required for test isolation
3. **Implement `clear()`** - For resetting data without destroying instance
4. **Test fixtures should reset** - Call `reset()` in teardown

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
```

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

### Event Types

| Event | Payload | Description |
|-------|---------|-------------|
| `component_added` | `(ship, component, layer)` | Component added to ship |
| `component_removed` | `(ship, component, layer)` | Component removed from ship |
| `ship_validated` | `(ship, result)` | Validation completed |
| `layer_changed` | `(ship, layer_type)` | Active layer selection changed |

### Usage

```python
# Publisher
event_bus.emit('component_added', ship, component, layer)

# Subscriber
def on_component_added(ship, component, layer):
    update_ui_for_component(component)

event_bus.subscribe('component_added', on_component_added)
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

### Guidelines

1. **Use `frozen=True`** - Configuration should be immutable
2. **Group related values** - One config class per domain
3. **Add helper methods** - For common operations like resolution tuples
4. **Document units** - Especially for time (seconds vs ticks)
5. **Import from module** - `from game.core.config import AIConfig`

---

## Summary

| Pattern | Use When | Example |
|---------|----------|---------|
| Singleton | Global state needed, exactly one instance | `RegistryManager`, `StrategyManager` |
| Mixin | Adding behavior to a class | `ShipCombatMixin`, `ShipPhysicsMixin` |
| Event Bus | Decoupling publishers/subscribers | Component changes, validation events |
| Template Method | Shared algorithm with variable steps | `ValidationRule` hierarchy |
| Configuration | Centralizing constants | `DisplayConfig`, `AIConfig` |
