# Starship Battles Test Suite

## Overview

- **Total Tests:** ~5700+ tests
- **Parallel Runtime:** ~40 seconds (`pytest tests/ -n 4`)
- **Sequential Runtime:** ~90 seconds (`pytest tests/ -n 0`)

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
│   ├── battle.py            # Battle engine fixtures
│   ├── ai.py                # AI fixtures
│   └── test_scenarios.py    # Combat Lab scenario mocks
├── unit/                    # Unit tests (mirrors game/ structure)
│   ├── conftest.py          # Unit test configuration
│   ├── ai/                  # AI system tests
│   ├── assets/              # Asset manager tests (mirrors game/assets/)
│   ├── builder/             # Ship builder UI tests
│   ├── combat/              # Combat system tests
│   ├── core/                # Core module tests (mirrors game/core/)
│   ├── entities/            # Entity tests (Ship, Component)
│   ├── fixtures/            # Fixture tests
│   ├── quickstart/          # Quickstart system tests
│   ├── research/            # Research system tests (mirrors game/research/)
│   │   ├── data/            # Research data tests
│   │   ├── systems/         # Research systems tests
│   │   └── ui/              # Research UI tests
│   ├── simulation/          # Simulation tests (mirrors game/simulation/)
│   │   ├── managers/        # Simulation manager tests
│   │   └── services/        # Simulation service tests
│   ├── strategy/            # Strategy map tests
│   ├── systems/             # Core system tests
│   ├── combat_lab/      # Test framework tests (Combat Lab)
│   │   └── services/        # Combat Lab service tests
│   └── ui/                  # UI panel/rendering tests
├── integration/             # Integration tests
│   ├── ai_strategy/         # AI policy integration
│   ├── colonization/        # Colonization workflow tests
│   ├── fleet_combat/        # Fleet combat tests
│   ├── gameplay_loop/       # Full gameplay loop tests
│   ├── research_workflow/   # Research workflow tests
│   ├── resource_system/     # Resource system tests
│   ├── save_load/           # Save/load integration tests
│   ├── strategy/            # Strategy map integration tests
│   │   ├── facade/          # Facade pattern tests
│   │   ├── production/      # Production system tests
│   │   └── turn_engine/     # Turn engine tests
│   └── ui/                  # UI integration tests
│       └── build_queue_screen/  # Build queue tests
└── infrastructure/          # Test infrastructure
    └── session_cache.py     # Session-scoped registry cache
```

---

## Fixture Hierarchy

The pytest fixture system uses a hierarchical structure. Fixtures defined at higher levels are automatically available to tests at lower levels.

```
conftest.py (project root)
├── reset_game_state [autouse, function] - Primary test isolation
├── enforce_headless [autouse, session] - Pygame headless mode
│
└── tests/conftest.py
    ├── global_ship_data [session] - Session-scoped data loading
    ├── global_ship_data_with_modifiers [session] - Data + modifiers
    ├── session_registries [session] - DI GameRegistries
    ├── fresh_registries [function] - Deep-copied registries
    ├── minimal_registries [function] - Empty registries
    ├── make_mock_ship_instance() - Helper function
    │
    └── tests/unit/conftest.py
        ├── pytest_configure() - Pre-import game.ui
        │
        ├── tests/unit/ai/conftest.py
        │   └── [imports: unit_test_data_dir, policy_manager_with_test_data]
        │
        ├── tests/unit/builder/conftest.py
        │   └── builder_test_setup [autouse, function] - Placeholder (cleanup in root)
        │
        ├── tests/unit/combat/conftest.py
        │   └── combat_test_setup [autouse, function] - Placeholder (cleanup in root)
        │
        ├── tests/unit/entities/conftest.py
        │   ├── entities_test_setup [autouse, function] - Pygame init
        │   └── basic_ship - Alias for basic_cruiser_ship
        │
        ├── tests/unit/fixtures/conftest.py
        │   └── [imports all fixtures from tests/fixtures/*.py]
        │
        ├── tests/unit/quickstart/conftest.py
        │   ├── quickstart_fixtures_dir [function]
        │   ├── quickstart_races_dir [function]
        │   └── quickstart_designs_dir [function]
        │
        ├── tests/unit/research/conftest.py
        │   ├── research_tracker [function]
        │   ├── populated_tracker [function]
        │   └── mock_tech_tree [function]
        │
        ├── tests/unit/strategy/conftest.py
        │   ├── reset_resource_registry [function]
        │   ├── temp_resources_json [function]
        │   ├── custom_resource_registry [function]
        │   ├── mock_component [function] - Factory for MockComponent
        │   ├── make_design_data [function] - Factory
        │   ├── make_design_data_with_stats [function] - Factory
        │   ├── ship_stats_with_custom_resources [function]
        │   ├── mock_component_registry [function] - Factory
        │   ├── ship_with_per_turn_component [function]
        │   ├── ship_with_warp_drive [function]
        │   ├── ship_with_custom_resources [function]
        │   ├── fleet_with_resource_ships [function]
        │   └── empty_fleet [function]
        │
        ├── tests/unit/systems/conftest.py
        │   └── systems_test_setup [autouse, function] - Pygame init
        │
        └── tests/unit/ui/conftest.py
            ├── pytest_configure() - Pre-import game.ui modules
            ├── pytest_configure_node() - Worker verification
            └── pygame_display_reset [autouse, function] - Display setup/reset

    └── tests/unit/combat_lab/services/conftest.py
        ├── mock_battle_engine [function]
        ├── mock_battle_screen [function]
        ├── mock_game [function]
        ├── mock_test_scenario [function]
        ├── mock_test_runner [function]
        ├── mock_test_registry [function]
        ├── mock_test_history [function]
        ├── sample_test_metadata [function]
        ├── sample_scenario_info [function]
        ├── sample_ship_data [function]
        ├── sample_target_data [function]
        ├── sample_component_data [function]
        ├── sample_components_file [function]
        ├── temp_data_dir [function]
        ├── observer_spy [function]
        └── sample_validation_* [function]

combat_lab/conftest.py (separate test suite)
├── validate_test_data_schemas [autouse, session] - Schema validation
├── init_pygame [autouse, session] - Pygame init
├── isolated_registry [class] - Class-scoped isolated registry
├── data_dir [function] - Simulation test data path
└── ships_dir [function] - Ships directory path
```

---

## Fixture Scopes

| Scope | Description | Use Case |
|-------|-------------|----------|
| `session` | Created once per test session | Expensive data loading, pygame init |
| `class` | Created once per test class | Test class setup |
| `function` | Created for each test function | Most fixtures, test isolation |

---

## Key Fixtures

### Test Isolation (Root conftest.py)

**`reset_game_state`** (autouse, function)
- Primary test isolation fixture using Fast Hydration pattern
- Automatically runs for every test
- Pre-test: Clears all singleton state
- Setup: Hydrates registries from session cache (no disk I/O)
- Post-test: Cleans up all singletons (Registry, Logger, Profiler, AI, UI managers)
- Use `@pytest.mark.use_custom_data` to skip production data hydration

**`enforce_headless`** (autouse, session)
- Initializes pygame in headless mode once per session
- Creates persistent 1440x900 dummy display
- Prevents window creation during tests

### DI Registry Fixtures (tests/conftest.py)

**`session_registries`** (session)
- Session-scoped GameRegistries loaded once
- Read-only, shared across all tests
- Use for tests that don't modify registry data

**`fresh_registries`** (function)
- Deep-copied GameRegistries for each test
- Use when test modifies registry data
- Ensures test isolation

**`minimal_registries`** (function)
- Empty GameRegistries with empty dictionaries
- Use for isolated unit tests
- Add only what your test needs

### Data Loading Fixtures

**`global_ship_data`** (session)
- Loads vehicle classes and components once per session
- Does NOT load modifiers
- Return value: `True` when loaded

**`global_ship_data_with_modifiers`** (session)
- Extends global_ship_data with modifier loading
- Return value: `True` when loaded

**`initialized_ship_data`** (function)
- Function-scoped data initialization
- Use when test needs fresh data loading (rare)

---

## Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.use_custom_data` | Skip production data hydration in reset_game_state |
| `@pytest.mark.integration` | Mark integration tests |
| `@pytest.mark.slow` | Mark slow tests |

---

## Running Tests

### Basic Commands

```bash
# Run all tests (parallel - recommended)
pytest tests/ -n 4

# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/entities/test_ship.py -v

# Run specific test class
pytest tests/unit/entities/test_ship.py::TestShip -v

# Run specific test method
pytest tests/unit/entities/test_ship.py::TestShip::test_ship_creation -v

# Run with testmon (incremental - fastest for development)
pytest tests/ --testmon
```

### Coverage

```bash
# Generate coverage report
pytest tests/ --cov=game --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=game --cov-report=html
```

### Performance Analysis

```bash
# Show slowest 30 tests
pytest tests/ --durations=30

# Show all test timings
pytest tests/ --durations=0
```

---

## Writing Tests

### Using Fixtures

The test suite provides several shared fixtures. Import them in your test's `conftest.py`:

```python
# In tests/unit/your_module/conftest.py
from tests.fixtures.common import initialized_ship_data
from tests.fixtures.ships import basic_ship, armed_ship
```

### Factory vs Fixture Pattern

**Factory (callable)**: Use when tests need custom configuration
```python
from tests.fixtures.ships import create_test_ship

def test_custom_ship():
    ship = create_test_ship(name="Custom", add_weapons=3)
```

**Fixture (pytest parameter)**: Use for standard configurations
```python
def test_basic_ship(basic_ship):
    assert basic_ship.max_hp > 0
```

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

### Assertion Helpers (tests/conftest.py)

PROJ-48 added assertion helper functions for better error messages:

**`assert_success(success, message)`**
- Use for save/load operations that return (success, message) tuples
- Provides better error messages than bare `assert success`

```python
from tests.conftest import assert_success

success, message = SaveGameService.save_game(session, "TestGame")
assert_success(success, message)
```

**`assert_list_length(items, expected_length, description)`**
- Use for assertions about list/collection lengths
- Provides better error messages than bare `assert len(items) == N`

```python
from tests.conftest import assert_list_length

assert_list_length(events, 1, "events after selection")
```

---

### Docstrings

Test classes and complex test methods should have docstrings:

- **Test classes**: Add a docstring describing what class/feature is being tested
  - Pattern: `"""Tests for <feature/class>."""`
  - Example: `"""Tests for ShipStatsService damage calculations."""`

- **Test methods**: Add docstrings for complex scenarios only
  - Simple tests: Method name should be self-documenting
  - Complex tests: Add docstring explaining the scenario

```python
class TestWeaponFiring:
    """Tests for weapon firing mechanics and target selection."""

    def test_fire_weapon_hits_target(self):
        # Simple test - name is descriptive enough
        ...

    def test_fire_weapon_with_interference_field(self):
        """Verify weapon accuracy penalty when firing through interference.

        The interference field should reduce hit chance by 25% but
        not affect damage if the shot lands.
        """
        ...
```

---

### Best Practices

1. **Isolation**: Each test should be independent. The `reset_game_state` fixture handles cleanup automatically.

2. **Naming**: Use descriptive test names: `test_{method}_{scenario}_{expected_result}`

3. **Assertions**: One logical assertion per test. Multiple `assert` statements are fine if testing the same concept.

4. **Fixtures**: Prefer pytest fixtures over `setUp`/`tearDown` methods.

5. **Mocking**: Use `unittest.mock.patch` for external dependencies.

6. **Parallel Safety**: Tests run in parallel with pytest-xdist. The test infrastructure handles isolation.

---

## Naming Conventions

### Test Files
- All test files must follow `test_*.py` naming pattern
- Benchmark/utility scripts go in `scripts/`, not `tests/`
- Exception: `conftest.py` for pytest fixture configuration

### Test Classes
- Name: `Test<SourceClassName>` or `Test<Feature>`
- One test class per source class when possible
- Example: `TestShip` for `Ship` class tests
- Example: `TestContinuousCollisionDetection` for CCD feature tests

### Test Methods
- Pattern: `test_<what>_<condition>` or `test_<feature>_<expected_result>`
- Example: `test_add_component_invalid_layer_raises_error`
- Example: `test_static_target_direct_shot`
- Keep names descriptive but not excessively long

### Mock Classes
- Test doubles should be named `Mock<OriginalClassName>`
- Example: `MockBattleEngine`, `MockShip`, `MockComponent`
- Use `Mock*` prefix consistently (not Stub or Fake)
- For interfaces: `MockMovementEngine` for `IMovementEngine`

---

## Mock Patterns

### Patch Styles

Both styles are acceptable. Choose based on readability and scope:

**Context Manager** (preferred for localized patches):
```python
from unittest.mock import patch, MagicMock

def test_something():
    with patch('module.path.ClassName') as mock_class:
        mock_class.return_value = MagicMock()
        # test code - patch is scoped to this block
```

**Decorator** (preferred for whole-function patches):
```python
@patch('module.path.ClassName')
def test_something(mock_class):
    # test code - patch is scoped to entire function
```

**Guideline**: Maintain consistency within a single test file. Avoid mixing styles in the same file unless necessary.

### Factory Functions

Factory functions provide reusable mock creation with configurable defaults.

**Naming Convention:**
- Pattern: `create_mock_<resource>()` for mock factories
- Pattern: `create_<resource>()` for real object factories
- Example: `create_mock_battle_engine()`, `create_test_ship()`

**Location:**
- Domain-specific mocks: Co-locate with related fixtures in `tests/fixtures/*.py`
- Test-specific mocks: Within test file or local conftest.py

**Available Mock Factories:**
```python
from tests.fixtures.battle import (
    create_mock_battle_engine,  # Mock BattleEngine
    create_mock_battle_screen,  # Mock BattleScreen
)
from tests.fixtures.test_scenarios import (
    create_mock_test_scenario,  # Mock TestScenario
    create_mock_test_registry,  # Mock TestRegistry
    create_mock_test_runner,    # Mock TestRunner
    create_mock_test_history,   # Mock TestHistory
)
```

### Inline Mock Classes

When a test needs a custom mock class:

```python
class MockComponent:
    """Test double for Component class."""
    def __init__(self, comp_id="test"):
        self.id = comp_id
        self.abilities = {}
```

- Always use `Mock*` prefix
- Add docstring explaining what it mocks
- Keep in test file if used only there
- Move to conftest.py if used across multiple files in same directory

### MagicMock vs Mock

- Use `MagicMock` when you need magic method support (`__len__`, `__iter__`, etc.)
- Use `Mock` for simpler mocks without magic method needs
- Both auto-create attributes on access

---

## Adding New Fixtures

1. **Module-specific**: Add to module's conftest.py
2. **Shared across modules**: Add to `tests/fixtures/*.py`
3. **Import in conftest**: `from tests.fixtures.X import fixture_name  # noqa: F401`

---

## Troubleshooting

### Tests Pass in Parallel but Fail Sequentially

This usually indicates tests depend on state from previous tests. The `reset_game_state` fixture should prevent this, but if you see issues:
1. Check if test uses `@pytest.mark.use_custom_data` marker
2. Ensure singleton cleanup is complete in reset_game_state

### Pygame Initialization Errors

The `enforce_headless` fixture handles this automatically. If issues persist:
```python
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
```

### Import Errors

Check that:
1. `__init__.py` exists in test directories
2. Project root is in `PYTHONPATH`
3. Fixtures are properly imported in `conftest.py`

---

---

## Skipped Tests

Some tests are conditionally skipped. This is intentional:

### Snapshot Regression Tests (`tests/regression/`)
- Tests in `modifier_ability_snapshots/` LOUDLY FAIL on missing baselines via
  `fail_missing_baseline()` (see
  `tests/regression/modifier_ability_snapshots/conftest.py:210-226`); the
  helper writes the fresh baseline to disk so the maintainer can inspect,
  accept, and commit before re-running. There is no silent skip — the
  "skip on first run" wording predates PROJ-446 Phase 1 Task 1.4 (F-C-025).
- Comparator is symmetric (PROJ-499): unexpected keys in actual produce a
  diff just like missing keys; bulk-accept schema drift is no longer
  possible. Re-shoots are deliberate, reviewed events.

### Missing Component/Data Skips
- Various tests skip if expected components/modifiers not in registry
- Pattern: `if 'component_id' not in registry: pytest.skip(...)`
- These ensure tests gracefully handle missing test data

### Platform/Environment Skips
- `test_research_renderer.py`: Skips when running in xdist parallel workers
- Uses `@pytest.mark.skipif` decorator properly

### Feature Not Implemented
- Reproduction tests for features under development

---

## See Also

- [tests/fixtures/README.md](fixtures/README.md) - Detailed fixture module documentation
- [CLAUDE.md](../CLAUDE.md) - Development guidelines
