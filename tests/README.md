# Starship Battles Test Suite

## Overview

- **Total Tests:** ~1,172 tests
- **Parallel Runtime:** ~9 seconds (`pytest tests/unit -n 16`)
- **Sequential Runtime:** ~28 seconds (`pytest tests/unit -n 0`)

## Test Organization

```
tests/
├── conftest.py              # Root fixtures (session-scoped data loading)
├── README.md                # This file
├── fixtures/                # Shared test fixtures
│   ├── __init__.py
│   ├── common.py            # Function-scoped data fixtures
│   ├── paths.py             # Path utilities
│   ├── ships.py             # Ship factory and fixtures
│   ├── components.py        # Component fixtures
│   └── battle.py            # Battle engine fixtures
├── unit/                    # Unit tests
│   ├── conftest.py          # Unit test configuration
│   ├── ai/                  # AI system tests
│   ├── builder/             # Ship builder UI tests
│   ├── combat/              # Combat system tests
│   ├── entities/            # Entity tests (Ship, Component)
│   ├── performance/         # Profiling tests
│   ├── regressions/         # Regression tests
│   ├── repro_issues/        # Issue reproduction tests
│   ├── services/            # Service layer tests
│   ├── strategy/            # Strategy map tests
│   ├── systems/             # Core system tests
│   └── ui/                  # UI panel/rendering tests
└── integration/             # Integration tests
```

## Running Tests

### Basic Commands

```bash
# Run all unit tests (parallel - fastest)
python -m pytest tests/unit

# Run all unit tests (sequential - for debugging)
python -m pytest tests/unit -n 0

# Run specific test file
python -m pytest tests/unit/entities/test_ship.py -v

# Run specific test class
python -m pytest tests/unit/entities/test_ship.py::TestShip -v

# Run specific test method
python -m pytest tests/unit/entities/test_ship.py::TestShip::test_ship_creation -v
```

### Coverage

```bash
# Generate coverage report
python -m pytest tests/unit --cov=game --cov-report=term-missing

# Generate HTML coverage report
python -m pytest tests/unit --cov=game --cov-report=html
# Open htmlcov/index.html in browser
```

### Performance Analysis

```bash
# Show slowest 30 tests
python -m pytest tests/unit --durations=30

# Show all test timings
python -m pytest tests/unit --durations=0
```

## Writing Tests

### Using Fixtures

The test suite provides several shared fixtures. Import them in your test's `conftest.py`:

```python
# In tests/unit/your_module/conftest.py
from tests.fixtures.common import initialized_ship_data
from tests.fixtures.ships import basic_ship, armed_ship
```

### Available Fixtures

#### Data Initialization
- `initialized_ship_data` - Load vehicle classes and components (function-scoped)
- `initialized_ship_data_with_modifiers` - Load data + modifiers (function-scoped)
- `global_ship_data` - Session-scoped data loading (for read-only tests)

#### Ships
- `empty_ship` - Ship with only hull
- `basic_ship` - Ship with bridge and engine
- `armed_ship` - Ship with weapons and shields
- `shielded_ship` - Ship with shields, no weapons
- `fully_equipped_ship` - Ship with all component types
- `two_opposing_ships` - Tuple of (ship1, ship2) on opposing teams

#### Components
- `weapon_component`, `engine_component`, `shield_component`, etc.

#### Paths
- `project_root`, `data_dir`, `assets_dir`, `test_data_dir`

### Test File Template

```python
"""Tests for {module_name}."""
import pytest
from game.module import Class

class TestClass:
    """Test cases for Class."""

    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return Class()

    def test_method_basic(self, instance):
        """Test method with basic input."""
        result = instance.method()
        assert result == expected

    def test_method_edge_case(self, instance):
        """Test method with edge case."""
        with pytest.raises(ValueError):
            instance.method(invalid_input)
```

### Best Practices

1. **Isolation**: Each test should be independent. Use fixtures for setup/teardown.

2. **Naming**: Use descriptive test names: `test_{method}_{scenario}_{expected_result}`

3. **Assertions**: One logical assertion per test. Multiple `assert` statements are fine if testing the same concept.

4. **Fixtures**: Prefer pytest fixtures over `setUp`/`tearDown` methods.

5. **Mocking**: Use `unittest.mock.patch` for external dependencies.

6. **Parallel Safety**: Tests run in parallel with pytest-xdist. Avoid:
   - Shared global state without proper isolation
   - Fixed file paths (use temp directories)
   - Port conflicts for network tests

## Troubleshooting

### Tests Pass in Parallel but Fail Sequentially

This usually indicates tests depend on state from previous tests. Fix by:
1. Adding proper setup/teardown
2. Clearing singletons (e.g., `RegistryManager.instance().clear()`)
3. Using function-scoped fixtures instead of session-scoped

### Pygame Initialization Errors

Ensure headless mode:
```python
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()
```

### Import Errors

Check that:
1. `__init__.py` exists in test directories
2. Project root is in `PYTHONPATH`
3. Fixtures are properly imported in `conftest.py`
