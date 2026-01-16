# Starship Battles Consolidation Plan

## Overview

This document outlines a comprehensive, test-driven refactoring plan to address code duplication, improve maintainability, and enhance extensibility. Each phase is broken into small, atomic tasks that can be completed within a single agent session.

**Guiding Principles:**
1. Test-driven development - write tests first, then implement
2. Small, incremental changes - each task is self-contained
3. No breaking changes - maintain backward compatibility during transition
4. Verify after each step - run relevant tests before proceeding

---

## Phase 1: Core Utilities and Infrastructure

**Goal:** Create foundational utilities that will be used throughout the refactoring.

### Task 1.1: Create JSON Utilities Module
**Estimated Scope:** ~100 lines
**Files to Create:**
- `game/core/json_utils.py`
- `tests/unit/core/test_json_utils.py`

**Steps:**
1. Write tests for `load_json()` function:
   - Test successful load
   - Test file not found (returns default)
   - Test invalid JSON (returns default)
   - Test with custom default value
2. Write tests for `save_json()` function:
   - Test successful save
   - Test directory creation
   - Test write failure handling
3. Implement `load_json()` and `save_json()` functions
4. Run tests to verify

**Test Template:**
```python
# tests/unit/core/test_json_utils.py
class TestJsonUtils:
    def test_load_json_success(self, tmp_path):
        """Load valid JSON file."""

    def test_load_json_file_not_found(self):
        """Return default when file doesn't exist."""

    def test_load_json_invalid_json(self, tmp_path):
        """Return default when JSON is malformed."""

    def test_save_json_success(self, tmp_path):
        """Save JSON to file."""

    def test_save_json_creates_directory(self, tmp_path):
        """Create parent directories if needed."""
```

---

### Task 1.2: Create Configuration Module
**Estimated Scope:** ~150 lines
**Files to Create:**
- `game/core/config.py`
- `tests/unit/core/test_config.py`

**Steps:**
1. Write tests for configuration classes:
   - Test default values are accessible
   - Test values are correct types
   - Test immutability (optional)
2. Create configuration dataclasses:
   - `DisplayConfig` - resolution, UI constants
   - `PhysicsConfig` - tick rate, speed limits
   - `AIConfig` - spacing, distances
   - `TestConfig` - test-specific settings
3. Run tests to verify

**Configuration Classes:**
```python
# game/core/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class DisplayConfig:
    DEFAULT_WIDTH: int = 2560
    DEFAULT_HEIGHT: int = 1600
    TEST_WIDTH: int = 1440
    TEST_HEIGHT: int = 900

@dataclass(frozen=True)
class AIConfig:
    MIN_SPACING: int = 150
    DEFAULT_ORBIT_DISTANCE: int = 500
    MAX_CORRECTION_FORCE: int = 500

@dataclass(frozen=True)
class PhysicsConfig:
    TICK_RATE: float = 0.01
    DEFAULT_MAX_SPEED: float = 1000.0
```

---

### Task 1.3: Create Path Utilities for Tests
**Estimated Scope:** ~80 lines
**Files to Create:**
- `tests/fixtures/paths.py`
- `tests/unit/fixtures/test_paths.py`

**Steps:**
1. Write tests for path resolution:
   - Test `get_project_root()` returns correct path
   - Test `get_data_dir()` returns data directory
   - Test `get_test_data_dir()` returns test data directory
2. Implement path utilities using `pathlib`
3. Run tests to verify

**Implementation:**
```python
# tests/fixtures/paths.py
from pathlib import Path

def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent

def get_data_dir() -> Path:
    """Return the game data directory."""
    return get_project_root() / "data"

def get_test_data_dir() -> Path:
    """Return the test data directory."""
    return get_project_root() / "tests" / "data"
```

---

## Phase 2: Ship Helper Methods

**Goal:** Add helper methods to Ship class to eliminate layer iteration duplication.

### Task 2.1: Add Ship.get_all_components() Method
**Estimated Scope:** ~50 lines
**Files to Modify:**
- `game/simulation/entities/ship.py`
**Files to Create:**
- `tests/unit/entities/test_ship_helpers.py`

**Steps:**
1. Write tests for `get_all_components()`:
   - Test returns empty list for empty ship
   - Test returns all components across all layers
   - Test order is consistent (layer order)
2. Implement `get_all_components()` method
3. Run tests to verify
4. Run existing ship tests to ensure no regression

**Test Template:**
```python
class TestShipHelpers:
    def test_get_all_components_empty_ship(self, basic_ship_no_components):
        """Empty ship returns empty list."""
        assert basic_ship_no_components.get_all_components() == []

    def test_get_all_components_returns_all(self, basic_ship):
        """Returns components from all layers."""
        components = basic_ship.get_all_components()
        assert len(components) >= 3  # bridge, crew, life_support

    def test_get_all_components_includes_hull(self, basic_ship):
        """Includes hull component."""
        components = basic_ship.get_all_components()
        hull_comps = [c for c in components if c.layer_assigned == LayerType.HULL]
        assert len(hull_comps) >= 1
```

---

### Task 2.2: Add Ship.iter_components() Generator
**Estimated Scope:** ~40 lines
**Files to Modify:**
- `game/simulation/entities/ship.py`
- `tests/unit/entities/test_ship_helpers.py`

**Steps:**
1. Write tests for `iter_components()`:
   - Test yields (layer_type, component) tuples
   - Test iterates all layers
   - Test can be consumed multiple times
2. Implement `iter_components()` generator
3. Run tests to verify

**Implementation:**
```python
def iter_components(self) -> Iterator[Tuple[LayerType, Component]]:
    """Iterate through (layer_type, component) tuples."""
    for layer_type, layer_data in self.layers.items():
        for component in layer_data['components']:
            yield layer_type, component
```

---

### Task 2.3: Add Ship.get_components_by_ability() Method
**Estimated Scope:** ~60 lines
**Files to Modify:**
- `game/simulation/entities/ship.py`
- `tests/unit/entities/test_ship_helpers.py`

**Steps:**
1. Write tests for `get_components_by_ability()`:
   - Test returns empty list when no matches
   - Test returns only components with specified ability
   - Test with operational_only=True filter
   - Test with operational_only=False (all components)
2. Implement method
3. Run tests to verify

**Test Template:**
```python
def test_get_components_by_ability_weapons(self, armed_ship):
    """Returns only weapon components."""
    weapons = armed_ship.get_components_by_ability('WeaponAbility')
    assert all(c.has_ability('WeaponAbility') for c in weapons)

def test_get_components_by_ability_none_found(self, basic_ship):
    """Returns empty list when no components have ability."""
    shields = basic_ship.get_components_by_ability('ShieldGenerator')
    assert shields == []
```

---

### Task 2.4: Add Ship.get_components_by_layer() Method
**Estimated Scope:** ~40 lines
**Files to Modify:**
- `game/simulation/entities/ship.py`
- `tests/unit/entities/test_ship_helpers.py`

**Steps:**
1. Write tests for `get_components_by_layer()`:
   - Test returns components for valid layer
   - Test returns empty list for empty layer
   - Test raises KeyError for invalid layer (or returns empty)
2. Implement method
3. Run tests to verify

---

## Phase 3: Migrate JSON Loading

**Goal:** Replace all duplicate JSON loading patterns with the new utility.

### Task 3.1: Migrate ship.py JSON Loading
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/simulation/entities/ship.py`

**Steps:**
1. Add import for `json_utils`
2. Replace JSON loading in `load_vehicle_classes()` with `load_json()`
3. Run existing ship tests to verify no regression
4. Run full test suite for simulation module

**Before:**
```python
try:
    with open(filepath, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    raise RuntimeError(f"Critical Error: {filepath} not found.")
```

**After:**
```python
from game.core.json_utils import load_json
data = load_json(filepath)
if data is None:
    raise RuntimeError(f"Critical Error: {filepath} not found.")
```

---

### Task 3.2: Migrate controller.py JSON Loading
**Estimated Scope:** ~40 lines changed
**Files to Modify:**
- `game/ai/controller.py`

**Steps:**
1. Add import for `json_utils`
2. Replace 3 JSON loading blocks in `StrategyManager.load_data()`
3. Run AI controller tests to verify
4. Run full AI test suite

---

### Task 3.3: Migrate preset_manager.py JSON Loading
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/simulation/preset_manager.py`

**Steps:**
1. Add import for `json_utils`
2. Replace JSON load/save in `load_presets()` and `save_presets()`
3. Run preset manager tests to verify

---

### Task 3.4: Migrate persistence.py JSON Loading
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/simulation/systems/persistence.py`

**Steps:**
1. Add import for `json_utils`
2. Replace JSON operations
3. Run persistence tests to verify

---

### Task 3.5: Migrate ship_theme.py JSON Loading
**Estimated Scope:** ~20 lines changed
**Files to Modify:**
- `game/simulation/ship_theme.py`

**Steps:**
1. Add import for `json_utils`
2. Replace JSON loading in theme loading
3. Run theme-related tests to verify

---

### Task 3.6: Migrate setup_screen.py JSON Loading
**Estimated Scope:** ~50 lines changed
**Files to Modify:**
- `game/ui/screens/setup_screen.py`

**Steps:**
1. Add import for `json_utils`
2. Replace 6 JSON loading locations
3. Run setup screen tests to verify

---

### Task 3.7: Migrate Remaining JSON Loading (Sweep)
**Estimated Scope:** ~60 lines changed
**Files to Check/Modify:**
- `game/ui/screens/planet_list_window.py`
- Any other files using raw JSON loading

**Steps:**
1. Search for remaining `json.load` and `json.dump` calls
2. Replace with `json_utils` functions
3. Run affected tests
4. Run full test suite

---

## Phase 4: Standardize Singleton Pattern

**Goal:** Make StrategyManager follow the same pattern as RegistryManager.

### Task 4.1: Write Tests for New StrategyManager Pattern
**Estimated Scope:** ~80 lines
**Files to Create:**
- `tests/unit/ai/test_strategy_manager_singleton.py`

**Steps:**
1. Write tests for singleton behavior:
   - Test `instance()` returns same object
   - Test `instance()` is thread-safe
   - Test `clear()` resets data but keeps instance
   - Test `reset()` destroys instance (for testing)
2. Write tests for data loading:
   - Test `load_data()` populates strategies
   - Test lazy loading doesn't happen on import

---

### Task 4.2: Refactor StrategyManager to Singleton Pattern
**Estimated Scope:** ~100 lines changed
**Files to Modify:**
- `game/ai/controller.py`

**Steps:**
1. Add class-level `_instance` and `_lock` attributes
2. Add `instance()` classmethod with double-checked locking
3. Add `reset()` classmethod for testing
4. Remove module-level `STRATEGY_MANAGER` global
5. Remove `load_combat_strategies()` call at module level
6. Update `reset_strategy_manager()` to use new pattern
7. Run new singleton tests
8. Run existing AI tests

**Before:**
```python
STRATEGY_MANAGER = None

def load_combat_strategies(filepath=None):
    global STRATEGY_MANAGER
    if STRATEGY_MANAGER is None:
        STRATEGY_MANAGER = StrategyManager()
    ...

load_combat_strategies()  # Side effect on import
```

**After:**
```python
class StrategyManager:
    _instance: Optional['StrategyManager'] = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls) -> 'StrategyManager':
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
```

---

### Task 4.3: Update StrategyManager References
**Estimated Scope:** ~50 lines changed
**Files to Modify:**
- `game/ai/controller.py` (internal references)
- `conftest.py` (reset function)

**Steps:**
1. Update `AIController.get_resolved_strategy()` to use `StrategyManager.instance()`
2. Update `get_strategy_names()` to use `StrategyManager.instance()`
3. Update `conftest.py` reset to use `StrategyManager.reset()`
4. Run all AI tests
5. Run full test suite

---

### Task 4.4: Add Lazy Loading to StrategyManager
**Estimated Scope:** ~40 lines changed
**Files to Modify:**
- `game/ai/controller.py`

**Steps:**
1. Add `_loaded` flag to StrategyManager
2. Add `ensure_loaded()` method that loads on first access
3. Call `ensure_loaded()` in `get_strategy()`, `get_targeting_policy()`, etc.
4. Write tests for lazy loading behavior
5. Run all tests

---

## Phase 5: Fix Test Infrastructure

**Goal:** Consolidate test fixtures and remove hardcoded paths.

### Task 5.1: Create Shared Ship Fixtures
**Estimated Scope:** ~120 lines
**Files to Create:**
- `tests/fixtures/__init__.py`
- `tests/fixtures/ships.py`
- `tests/unit/fixtures/test_ship_fixtures.py`

**Steps:**
1. Write tests for ship fixtures:
   - Test `empty_ship` fixture has no components
   - Test `basic_ship` fixture has required components
   - Test `armed_ship` fixture has weapons
2. Create ship factory fixtures
3. Run fixture tests

**Fixtures to Create:**
```python
@pytest.fixture
def empty_ship():
    """Ship with no components (except hull)."""

@pytest.fixture
def basic_ship():
    """Ship with bridge, crew_quarters, life_support."""

@pytest.fixture
def armed_ship(basic_ship):
    """Basic ship plus a weapon."""

@pytest.fixture
def shielded_ship(basic_ship):
    """Basic ship plus shields."""

@pytest.fixture
def fully_equipped_ship():
    """Ship with all common component types."""
```

---

### Task 5.2: Create Component Factory Fixtures
**Estimated Scope:** ~80 lines
**Files to Create:**
- `tests/fixtures/components.py`
- `tests/unit/fixtures/test_component_fixtures.py`

**Steps:**
1. Write tests for component fixtures
2. Create component factory fixtures:
   - `weapon_component` - parameterized weapon
   - `engine_component` - parameterized engine
   - `armor_component` - parameterized armor
3. Run fixture tests

---

### Task 5.3: Create Battle Engine Fixtures
**Estimated Scope:** ~100 lines
**Files to Create:**
- `tests/fixtures/battle.py`
- `tests/unit/fixtures/test_battle_fixtures.py`

**Steps:**
1. Write tests for battle fixtures
2. Create battle-related fixtures:
   - `battle_engine` - configured engine
   - `two_ship_battle` - engine with two opposing ships
   - `fleet_battle` - engine with multiple ships per team
3. Run fixture tests

---

### Task 5.4: Migrate Unit Tests - AI Module (Remove Hardcoded Paths)
**Estimated Scope:** ~100 lines changed
**Files to Modify:**
- `tests/unit/ai/test_ai.py`
- `tests/unit/ai/test_ai_behaviors.py`
- `tests/unit/ai/test_strategy_system.py`
- `tests/unit/ai/test_advanced_behaviors.py`
- `tests/unit/ai/test_movement_and_ai.py`

**Steps:**
1. Replace hardcoded paths with `get_data_dir()` fixture
2. Replace manual ship creation with ship fixtures
3. Run AI tests to verify
4. Ensure all tests still pass

---

### Task 5.5: Migrate Unit Tests - Combat Module
**Estimated Scope:** ~150 lines changed
**Files to Modify:**
- `tests/unit/combat/test_weapons.py`
- `tests/unit/combat/test_combat.py`
- `tests/unit/combat/test_battle_engine_core.py`
- `tests/unit/combat/test_projectiles.py`
- (and other combat tests)

**Steps:**
1. Replace hardcoded paths
2. Replace manual ship creation with fixtures
3. Run combat tests
4. Verify no regressions

---

### Task 5.6: Migrate Unit Tests - Entities Module
**Estimated Scope:** ~200 lines changed
**Files to Modify:**
- `tests/unit/entities/test_components.py`
- `tests/unit/entities/test_ship_resources.py`
- `tests/unit/entities/test_ship_stats.py`
- (and other entity tests)

**Steps:**
1. Replace hardcoded paths
2. Replace manual ship/component creation with fixtures
3. Run entity tests
4. Verify no regressions

---

### Task 5.7: Migrate Unit Tests - Builder Module
**Estimated Scope:** ~150 lines changed
**Files to Modify:**
- `tests/unit/builder/test_builder_logic.py`
- `tests/unit/builder/test_builder_validation.py`
- (and other builder tests)

**Steps:**
1. Replace hardcoded paths
2. Replace manual ship creation with fixtures
3. Run builder tests
4. Verify no regressions

---

### Task 5.8: Migrate Unit Tests - UI Module
**Estimated Scope:** ~100 lines changed
**Files to Modify:**
- `tests/unit/ui/test_detail_panel_rendering.py`
- `tests/unit/ui/test_battle_panels.py`
- (and other UI tests)

**Steps:**
1. Replace hardcoded paths
2. Use appropriate fixtures
3. Run UI tests
4. Verify no regressions

---

### Task 5.9: Migrate Unit Tests - Systems Module
**Estimated Scope:** ~80 lines changed
**Files to Modify:**
- `tests/unit/systems/test_physics.py`
- `tests/unit/systems/test_spatial.py`
- `tests/unit/systems/test_collision_system.py`
- (and other system tests)

**Steps:**
1. Replace hardcoded paths
2. Use appropriate fixtures
3. Run system tests
4. Verify no regressions

---

### Task 5.10: Clean Up Duplicate conftest.py Code
**Estimated Scope:** ~100 lines changed
**Files to Modify:**
- `conftest.py`
- `tests/unit/conftest.py`
- `tests/unit/ui/conftest.py`
- `simulation_tests/conftest.py`

**Steps:**
1. Extract common fixtures to `tests/fixtures/common.py`
2. Import shared fixtures in each conftest
3. Remove duplicate `isolated_registry` implementations
4. Consolidate pygame initialization
5. Run full test suite

---

## Phase 6: Fix Layer Coupling (UI → Domain Import)

**Goal:** Remove improper import from simulation layer to UI layer.

### Task 6.1: Create ModifierService in Simulation Layer
**Estimated Scope:** ~80 lines
**Files to Create:**
- `game/simulation/services/__init__.py`
- `game/simulation/services/modifier_service.py`
- `tests/unit/simulation/services/test_modifier_service.py`

**Steps:**
1. Write tests for modifier service:
   - Test `ensure_mandatory_modifiers()` adds required modifiers
   - Test doesn't duplicate existing modifiers
   - Test works with various component types
2. Create `ModifierService` class
3. Move `ensure_mandatory_modifiers()` logic from `ui.builder.modifier_logic`
4. Run tests

---

### Task 6.2: Update Ship to Use ModifierService
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/simulation/entities/ship.py`

**Steps:**
1. Replace import of `ui.builder.modifier_logic`
2. Import `game.simulation.services.modifier_service`
3. Update calls in `add_component()` and `add_components_bulk()`
4. Run ship tests
5. Run full test suite

---

### Task 6.3: Update UI to Use ModifierService
**Estimated Scope:** ~50 lines changed
**Files to Modify:**
- `ui/builder/modifier_logic.py`

**Steps:**
1. Import `ModifierService` from simulation layer
2. Delegate `ensure_mandatory_modifiers()` to service
3. Keep UI-specific logic in modifier_logic.py
4. Run builder tests
5. Run UI tests

---

## Phase 7: Enhance Event Bus

**Goal:** Improve event bus with proper logging and error handling.

### Task 7.1: Write Tests for Enhanced Event Bus
**Estimated Scope:** ~100 lines
**Files to Create/Modify:**
- `tests/unit/systems/test_event_bus.py` (enhance existing)

**Steps:**
1. Write tests for:
   - Error handling uses logger (not print)
   - Multiple subscribers receive events
   - Unsubscribe works correctly
   - Event with no subscribers doesn't error
2. Write tests for optional enhancements:
   - Priority ordering
   - Weak references (optional)

---

### Task 7.2: Implement Enhanced Event Bus
**Estimated Scope:** ~60 lines changed
**Files to Modify:**
- `ui/builder/event_bus.py`

**Steps:**
1. Add proper logging import
2. Replace `print()` with `logger.exception()`
3. Add defensive copy of subscribers list during emit
4. Run event bus tests
5. Run builder tests that use event bus

---

## Phase 8: Replace Print Statements with Logging

**Goal:** Standardize all output to use the logging system.

### Task 8.1: Audit and Replace Prints in game/simulation/
**Estimated Scope:** ~50 lines changed
**Files to Modify:**
- `game/simulation/entities/ship.py`
- `game/simulation/ship_validator.py`
- `game/simulation/preset_manager.py`
- Other simulation files with print statements

**Steps:**
1. Search for `print(` in game/simulation/
2. Replace with appropriate log level:
   - Errors → `log_error()`
   - Warnings → `log_warning()`
   - Info → `log_info()`
   - Debug → `log_debug()`
3. Run simulation tests

---

### Task 8.2: Audit and Replace Prints in game/ai/
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/ai/controller.py`
- `game/ai/behaviors.py`

**Steps:**
1. Search for `print(` in game/ai/
2. Replace with appropriate log calls
3. Run AI tests

---

### Task 8.3: Audit and Replace Prints in game/ui/
**Estimated Scope:** ~40 lines changed
**Files to Modify:**
- `game/ui/screens/*.py`
- `ui/builder/*.py`

**Steps:**
1. Search for `print(` in UI files
2. Replace with appropriate log calls
3. Run UI tests

---

### Task 8.4: Audit and Replace Prints in game/core/
**Estimated Scope:** ~20 lines changed
**Files to Modify:**
- `game/core/*.py`

**Steps:**
1. Search for `print(` in core files
2. Replace with log calls
3. Run core tests

---

## Phase 9: Refactor Layer Iteration Usage

**Goal:** Replace manual layer iteration with new Ship helper methods.

### Task 9.1: Refactor ship_validator.py
**Estimated Scope:** ~60 lines changed
**Files to Modify:**
- `game/simulation/ship_validator.py`

**Steps:**
1. Replace layer iteration patterns with `ship.get_all_components()`
2. Replace ability checks with `ship.get_components_by_ability()`
3. Run validator tests
4. Run full test suite

---

### Task 9.2: Refactor controller.py (AI)
**Estimated Scope:** ~40 lines changed
**Files to Modify:**
- `game/ai/controller.py`

**Steps:**
1. Replace layer iteration in `_stat_get_hp_percent()`
2. Replace layer iteration in `_stat_is_in_pdc_arc()`
3. Replace layer iteration in `_check_formation_integrity()`
4. Run AI tests

---

### Task 9.3: Refactor ship_combat.py
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/simulation/entities/ship_combat.py`

**Steps:**
1. Replace layer iteration patterns
2. Run combat tests

---

### Task 9.4: Refactor ship_stats.py
**Estimated Scope:** ~40 lines changed
**Files to Modify:**
- `game/simulation/entities/ship_stats.py`

**Steps:**
1. Replace layer iteration patterns
2. Run ship stats tests

---

### Task 9.5: Refactor Remaining Files (Sweep)
**Estimated Scope:** ~60 lines changed
**Files to Check:**
- All files in `game/` using layer iteration

**Steps:**
1. Search for `for layer in.*layers.values()` pattern
2. Refactor remaining occurrences
3. Run full test suite

---

## Phase 10: Consolidate Test Framework

**Goal:** Merge fragmented test infrastructure into single coherent structure.

### Task 10.1: Audit Test Framework Duplication
**Estimated Scope:** Documentation only
**Files to Review:**
- `test_framework/`
- `simulation_tests/`
- `tests/test_framework/`

**Steps:**
1. Document what each test framework provides
2. Identify overlapping functionality
3. Create migration plan for consolidation
4. Document in `docs/refactoring/TEST_CONSOLIDATION.md`

---

### Task 10.2: Merge test_framework/ into simulation_tests/
**Estimated Scope:** ~200 lines moved/changed
**Files to Modify:**
- Move `test_framework/scenario.py` → `simulation_tests/scenarios/base.py`
- Move `test_framework/registry.py` → `simulation_tests/registry.py`
- Update imports in simulation_tests/

**Steps:**
1. Copy files to new locations
2. Update imports in moved files
3. Update imports in simulation_tests/tests/
4. Run simulation tests
5. Delete old test_framework/ files

---

### Task 10.3: Consolidate tests/test_framework/services/
**Estimated Scope:** ~150 lines changed
**Files to Modify:**
- `tests/test_framework/services/conftest.py`
- `tests/fixtures/`

**Steps:**
1. Move reusable fixtures to `tests/fixtures/`
2. Update imports in test files
3. Delete duplicate conftest.py
4. Run affected tests

---

### Task 10.4: Update Documentation
**Estimated Scope:** Documentation only
**Files to Modify:**
- `simulation_tests/QUICK_START_GUIDE.md`
- `docs/refactoring/TEST_CONSOLIDATION.md`

**Steps:**
1. Update test framework documentation
2. Document new fixture locations
3. Update import paths in examples

---

## Phase 11: Create Service Layer

**Goal:** Add abstraction layer between UI and domain objects.

### Task 11.1: Create ShipBuilderService
**Estimated Scope:** ~150 lines
**Files to Create:**
- `game/simulation/services/ship_builder_service.py`
- `tests/unit/simulation/services/test_ship_builder_service.py`

**Steps:**
1. Write tests for ship builder service:
   - Test `create_ship()` returns valid ship
   - Test `add_component()` validates and adds
   - Test `remove_component()` removes correctly
   - Test `change_class()` handles migration
2. Implement service methods
3. Run tests

**Service Interface:**
```python
class ShipBuilderService:
    def create_ship(self, name: str, ship_class: str, theme_id: str = "Federation") -> Ship:
        """Create a new ship with default hull."""

    def add_component(self, ship: Ship, component_id: str, layer: LayerType) -> Result:
        """Add component with validation."""

    def remove_component(self, ship: Ship, layer: LayerType, index: int) -> Result:
        """Remove component at index."""

    def validate_design(self, ship: Ship) -> ValidationResult:
        """Validate complete ship design."""
```

---

### Task 11.2: Create BattleService
**Estimated Scope:** ~120 lines
**Files to Create:**
- `game/simulation/services/battle_service.py`
- `tests/unit/simulation/services/test_battle_service.py`

**Steps:**
1. Write tests for battle service:
   - Test `create_battle()` sets up engine
   - Test `add_ship()` adds to correct team
   - Test `start_battle()` begins simulation
   - Test `get_battle_state()` returns current state
2. Implement service methods
3. Run tests

---

### Task 11.3: Create DataService
**Estimated Scope:** ~100 lines
**Files to Create:**
- `game/simulation/services/data_service.py`
- `tests/unit/simulation/services/test_data_service.py`

**Steps:**
1. Write tests for data service:
   - Test `load_components()` populates registry
   - Test `load_modifiers()` populates registry
   - Test `load_vehicle_classes()` populates registry
   - Test `is_loaded()` returns correct state
2. Implement service as facade over existing loaders
3. Run tests

---

### Task 11.4: Update UI to Use Services (Builder)
**Estimated Scope:** ~100 lines changed
**Files to Modify:**
- `game/ui/screens/builder_screen.py`
- `ui/builder/interaction_controller.py`

**Steps:**
1. Import ShipBuilderService
2. Replace direct Ship manipulation with service calls
3. Run builder tests
4. Run UI tests

---

### Task 11.5: Update UI to Use Services (Battle)
**Estimated Scope:** ~80 lines changed
**Files to Modify:**
- `game/ui/screens/battle_scene.py`
- `game/ui/screens/setup_screen.py`

**Steps:**
1. Import BattleService
2. Replace direct BattleEngine manipulation with service calls
3. Run battle tests
4. Run UI tests

---

## Phase 12: Validation Rule Refactoring

**Goal:** Reduce duplication in validation rules using template method pattern.

### Task 12.1: Create Base ValidationRule Class
**Estimated Scope:** ~80 lines
**Files to Create:**
- `game/simulation/validation/__init__.py`
- `game/simulation/validation/base.py`
- `tests/unit/simulation/validation/test_base_rule.py`

**Steps:**
1. Write tests for base rule:
   - Test `_should_validate()` default behavior
   - Test subclass can override `_should_validate()`
   - Test `validate()` calls `_do_validate()` when appropriate
2. Implement abstract base class
3. Run tests

**Implementation:**
```python
class ValidationRule(ABC):
    def validate(self, ship, component=None, layer_type=None) -> ValidationResult:
        if not self._should_validate(component, layer_type):
            return ValidationResult(True)
        return self._do_validate(ship, component, layer_type)

    def _should_validate(self, component, layer_type) -> bool:
        return component is not None and layer_type is not None

    @abstractmethod
    def _do_validate(self, ship, component, layer_type) -> ValidationResult:
        pass
```

---

### Task 12.2: Migrate Existing Rules to Base Class
**Estimated Scope:** ~150 lines changed
**Files to Modify:**
- `game/simulation/ship_validator.py`

**Steps:**
1. Import base ValidationRule
2. Refactor each rule class to extend ValidationRule
3. Move validation logic to `_do_validate()`
4. Remove duplicate guard clauses
5. Run validator tests
6. Run full test suite

---

## Phase 13: Configuration Migration

**Goal:** Replace magic numbers with configuration references.

### Task 13.1: Migrate Display Configuration
**Estimated Scope:** ~40 lines changed
**Files to Modify:**
- `game/app.py`
- `conftest.py`

**Steps:**
1. Import DisplayConfig
2. Replace hardcoded resolution values
3. Run app tests
4. Run test suite

---

### Task 13.2: Migrate AI Configuration
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/ai/behaviors.py`

**Steps:**
1. Import AIConfig
2. Replace hardcoded spacing/distance values
3. Run AI tests

---

### Task 13.3: Migrate Physics Configuration
**Estimated Scope:** ~30 lines changed
**Files to Modify:**
- `game/simulation/physics_constants.py`
- `game/engine/physics.py`

**Steps:**
1. Import PhysicsConfig
2. Replace hardcoded physics values
3. Run physics tests

---

## Phase 14: Final Cleanup and Documentation

### Task 14.1: Remove Deprecated Code
**Estimated Scope:** ~50 lines removed
**Files to Modify:**
- Various files with TODO/DEPRECATED comments

**Steps:**
1. Search for `# TODO`, `# DEPRECATED`, `# REMOVE`
2. Remove dead code
3. Run full test suite

---

### Task 14.2: Update Architecture Documentation
**Estimated Scope:** Documentation only
**Files to Modify:**
- `docs/architecture/`
- Create `docs/architecture/SERVICES.md`
- Create `docs/architecture/PATTERNS.md`

**Steps:**
1. Document service layer architecture
2. Document singleton pattern usage
3. Document event bus patterns
4. Update existing architecture docs

---

### Task 14.3: Update Test Documentation
**Estimated Scope:** Documentation only
**Files to Modify:**
- `docs/unit_test_plan.md`
- `docs/test_migration_guide.md`

**Steps:**
1. Document new fixture locations
2. Document test patterns
3. Update examples

---

### Task 14.4: Final Test Suite Validation
**Estimated Scope:** Testing only

**Steps:**
1. Run full test suite
2. Check test coverage report
3. Identify any remaining issues
4. Document known issues if any

---

## Execution Order Summary

| Phase | Tasks | Dependencies | Est. Total Scope |
|-------|-------|--------------|------------------|
| 1 | 1.1-1.3 | None | ~330 lines |
| 2 | 2.1-2.4 | Phase 1 | ~190 lines |
| 3 | 3.1-3.7 | Phase 1 | ~260 lines |
| 4 | 4.1-4.4 | Phase 1 | ~270 lines |
| 5 | 5.1-5.10 | Phase 1 | ~1180 lines |
| 6 | 6.1-6.3 | Phase 2 | ~160 lines |
| 7 | 7.1-7.2 | None | ~160 lines |
| 8 | 8.1-8.4 | None | ~140 lines |
| 9 | 9.1-9.5 | Phase 2 | ~230 lines |
| 10 | 10.1-10.4 | Phase 5 | ~350+ lines |
| 11 | 11.1-11.5 | Phase 6 | ~550 lines |
| 12 | 12.1-12.2 | None | ~230 lines |
| 13 | 13.1-13.3 | Phase 1 | ~100 lines |
| 14 | 14.1-14.4 | All | Documentation |

**Total Estimated Changes:** ~4,150+ lines across ~70 tasks

---

## Risk Mitigation

1. **Run tests after every task** - Catch regressions immediately
2. **Commit after each task** - Easy rollback if issues found
3. **Keep backward compatibility** - Old patterns work during transition
4. **Document breaking changes** - If any occur, document clearly

---

## Success Criteria

- [ ] All tests pass after each phase
- [ ] No hardcoded paths in test files
- [ ] Single JSON utility used throughout
- [ ] Consistent singleton pattern
- [ ] No UI→Domain imports in simulation layer
- [ ] All print() replaced with logging
- [ ] Layer iteration uses Ship helper methods
- [ ] Test fixtures consolidated
- [ ] Service layer in place
- [ ] Documentation updated
