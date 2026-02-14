# UI Test Patterns (PROJ-142 Phase 2 Task 2.11)

This document establishes consistent testing patterns for UI screens and panels.

## Standard Class Naming

Use descriptive class names that indicate the feature being tested:

```python
class TestShipDetailPanelInit:
    """Tests for initialization."""
    ...

class TestShipDetailPanelUpdates:
    """Tests for update methods."""
    ...

class TestShipDetailPanelEvents:
    """Tests for event handling."""
    ...
```

**Pattern:** `Test<Component><Feature>`

## Standard Imports

```python
"""Tests for <component> (PROJ-XXX Phase X Task X.X)."""

import pytest
from unittest.mock import MagicMock, patch
import pygame
```

- Standard imports at top
- Game imports can be in helpers or at module level
- Document which PROJ and task the tests belong to

## Fixture Pattern: Bypass-Init

For UI components with complex initialization, use bypass-init:

```python
def _make_mock_ship():
    """Create a mock Ship with typical attributes."""
    ship = MagicMock()
    ship.name = "Test Ship"
    # ... set all needed attributes
    return ship


class TestComponentInit:
    def test_stores_manager(self):
        from game.ui.panels.my_panel import MyPanel

        with patch.object(MyPanel, '__init__', lambda self, *a, **kw: None):
            panel = MyPanel.__new__(MyPanel)

        manager = MagicMock()
        panel.manager = manager

        assert panel.manager is manager
```

**Key points:**
- Use `patch.object` with lambda to skip `__init__`
- Use `__new__` to create instance
- Manually assign attributes being tested

## Testing Method Behavior

For testing method behavior:

```python
def test_update_calls_helper(self):
    from game.ui.panels.my_panel import MyPanel

    with patch.object(MyPanel, '__init__', lambda self, *a, **kw: None):
        panel = MyPanel.__new__(MyPanel)

    panel._helper_method = MagicMock()
    panel.some_attribute = "value"

    panel.update()

    panel._helper_method.assert_called_once()
```

## Pygame Fixtures

When tests need pygame initialized:

```python
class TestRendering:
    @pytest.fixture
    def init_pygame(self):
        """Initialize pygame for surface operations."""
        pygame.init()
        yield
        pygame.quit()

    def test_creates_surface(self, init_pygame):
        surface = pygame.Surface((100, 100))
        assert surface.get_size() == (100, 100)
```

## Test Class Organization

Organize tests by behavior category:

```python
# Import tests
class TestMyPanelImport:
    """Tests for module import."""
    ...

# Initialization tests
class TestMyPanelInit:
    """Tests for initialization."""
    ...

# State/property tests
class TestMyPanelState:
    """Tests for state management."""
    ...

# Method behavior tests
class TestMyPanelUpdates:
    """Tests for update methods."""
    ...

# Event handling tests
class TestMyPanelEvents:
    """Tests for event handling."""
    ...

# Cleanup tests
class TestMyPanelKill:
    """Tests for cleanup."""
    ...
```

## Mock Helper Conventions

Name helpers with `_make_mock_` prefix:

```python
def _make_mock_ship():
    """Create a mock Ship."""
    ...

def _make_mock_planet():
    """Create a mock Planet."""
    ...

def _make_mock_event_bus():
    """Create a mock EventBus."""
    ...
```

## Test Docstrings

Each test should have a single-line docstring:

```python
def test_clear_kills_elements(self):
    """_clear_elements kills all UI elements."""
    ...

def test_update_none_shows_placeholder(self):
    """update(None) shows placeholder."""
    ...
```

## Edge Case Testing

Separate edge case tests into dedicated classes:

```python
class TestMyPanelEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_handles_none_input(self):
        """None input is handled gracefully."""
        ...

    def test_handles_empty_list(self):
        """Empty list input is handled."""
        ...

    def test_handles_invalid_index(self):
        """Invalid index does not raise."""
        ...
```

## Test Independence

Each test should be independent:

- Don't rely on test execution order
- Create fresh mocks in each test
- Use fixtures for shared setup that yields fresh instances
- Clean up any global state in teardown
