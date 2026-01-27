# Pattern Scout Report - PROJ-16

**Agent Role:** Pattern Scout
**Date:** 2026-01-25

## Recent Migration Patterns in Codebase

### PROJ-11 Pattern: Re-export with Backward Compat Comment

**File:** `game/ui/screens/fleet_report_filters.py:11-29`
```python
# PROJ-11: Import has_warp_capability from strategy services (canonical location)
# Re-exported here for backward compatibility with existing code
from game.strategy.services.ship_stats_service import ShipStatsService

# Re-export for backward compatibility
def has_warp_capability(ship: ShipInstance) -> bool:
    """
    PROJ-11: This is a thin wrapper around ShipStatsService.has_warp_capability().
    New code should import from game.strategy.services.ship_stats_service directly.
    """
    return ShipStatsService.has_warp_capability(ship)
```

### Deprecation Warning Pattern

**File:** `game/strategy/engine/turn_engine.py:264-272`
```python
""".. deprecated::"""
warnings.warn(
    "_execute_move_step is deprecated. Use _calculate_next_hex and apply movement manually.",
    DeprecationWarning,
    stacklevel=2
)
```

## Import Style Conventions

### Absolute Imports (Preferred)
All imports use `from game.X import Y` format. No relative imports found.

### Import Ordering
1. Standard library (typing, warnings, time, etc.)
2. Third-party (pygame, pytest, etc.)
3. Local absolute imports (from game.X)

### Multi-line Imports
Use parentheses style:
```python
from pygame_gui.elements import (
    UIWindow, UILabel, UITextEntryLine, UIButton,
    UIDropDownMenu, UITextBox
)
```

### TYPE_CHECKING Pattern
```python
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.math import Vector2
```

## Interface Export Pattern

**File:** `game/ai/interfaces/__init__.py`
```python
"""
AI Interfaces package.

PROJ-12 Phase 5: Contains interface abstractions for AI system.
Decouples AI from specific entity implementations.
"""

from game.ai.interfaces.controllable import IControllable, ShipControllableAdapter

__all__ = ['IControllable', 'ShipControllableAdapter']
```

## Wrapper Class Patterns

### Adapter Pattern
`game/ai/interfaces/controllable.py:162` - ShipControllableAdapter wraps Ship for IControllable

### Proxy Pattern
`game/core/profiling.py:133` - _ProfilerProxy for lazy singleton access

### Thin Wrapper Pattern
`ui/builder/modifier_logic.py:8` - ModifierLogic delegates to ModifierService

## Test Import Patterns

- Tests create mock structures instead of importing real ones
- Integration tests use real imports
- Unit tests prefer mocking
