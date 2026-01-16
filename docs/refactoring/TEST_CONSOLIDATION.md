# Test Framework Consolidation

## Overview

This document audits the test framework structure and outlines the consolidation plan for Phase 10.

## Current Structure

### 1. `test_framework/` - Combat Lab Test Framework

**Purpose:** Provides the infrastructure for running visual combat scenarios in the Combat Lab UI.

**Key Files:**
- `scenario.py` - `CombatScenario` base class for defining reproducible combat tests
- `registry.py` - `TestRegistry` singleton for discovering and managing test scenarios
- `runner.py` - `TestRunner` class that executes scenarios (headless or visual)
- `test_history.py` - Tracks test execution history
- `scenarios/` - Contains specific combat test scenarios (simple_duel, range_test, etc.)
- `services/` - Service layer for Combat Lab UI (6 service classes)

**Provides:**
- `CombatScenario` - Base class with setup(), update(), verify(), create_ship() methods
- `TestRegistry` - Singleton for scenario discovery with filtering by category/tag
- `TestRunner` - Executes scenarios with data loading and result logging

### 2. `simulation_tests/` - Extended Test Scenarios

**Purpose:** Extends the base `CombatScenario` with rich metadata and validation for pytest integration.

**Key Files:**
- `conftest.py` - pytest fixtures for isolated registry and data loading
- `scenarios/base.py` - `TestScenario` extends `CombatScenario` with `TestMetadata`
- `scenarios/validation.py` - Validation rules for automated test verification
- `scenarios/*.py` - Weapon, propulsion, resource test scenarios
- `tests/*.py` - Actual pytest test files that run scenarios
- `data/` - Test-specific data files (ships, components, vehicle classes)
- `logging_config.py` - Logging configuration for test output

**Provides:**
- `TestScenario` - Extended scenario with metadata, helper methods
- `TestMetadata` - Rich test documentation (category, conditions, pass_criteria)
- `ValidationRule`, `Validator` - Automated result validation
- Pre-built test ships in `data/ships/`

### 3. `tests/test_framework/services/` - Unit Tests for Combat Lab Services

**Purpose:** Unit tests for the service layer in `test_framework/services/`.

**Key Files:**
- `conftest.py` - Mock fixtures for service testing
- `test_*.py` - Tests for each service (metadata, scenario_data, execution, etc.)

**Provides:**
- Mock objects: `mock_battle_engine`, `mock_test_scenario`, `mock_test_registry`
- Helper functions: `create_test_metadata()`
- Sample data fixtures: `sample_ship_data`, `sample_component_data`

### 4. `tests/fixtures/` - Shared Test Fixtures

**Purpose:** Provides reusable fixtures for unit tests throughout the project.

**Key Files:**
- `__init__.py` - Exports all fixture factories
- `paths.py` - Path resolution utilities (`get_project_root`, `get_data_dir`)
- `ships.py` - Ship creation (`create_test_ship`)
- `components.py` - Component factories (`create_weapon`, `create_shield`, etc.)
- `battle.py` - Battle engine fixtures

**Provides:**
- Path utilities for consistent data access
- Ship and component factory functions
- Battle engine creation helpers

## Identified Duplication

### 1. Scenario Base Classes
- `test_framework/scenario.py` → `CombatScenario`
- `simulation_tests/scenarios/base.py` → `TestScenario` (extends CombatScenario)

**Relationship:** Proper inheritance, no duplication. `TestScenario` correctly extends `CombatScenario`.

### 2. Registry Pattern
- `test_framework/registry.py` → `TestRegistry` (discovers in simulation_tests/scenarios/)

**Issue:** Registry is in `test_framework/` but scans `simulation_tests/scenarios/`. This is intentional as the registry bridges both systems.

### 3. Isolated Registry Fixtures
- `simulation_tests/conftest.py` → `isolated_registry` fixture
- `tests/unit/conftest.py` → likely has similar fixture

**Potential Duplication:** Both need isolated registry loading but may use different data directories.

### 4. Mock Battle Engine Fixtures
- `tests/test_framework/services/conftest.py` → `mock_battle_engine`
- `tests/fixtures/battle.py` → `create_mock_battle_engine`

**Duplication:** Same concept in two places. Should consolidate.

### 5. Data Directories
- `simulation_tests/data/` - Combat Lab test data
- `data/` - Production game data
- `tests/data/` - (if exists) Unit test data

**Intent:** Separate test data from production data is correct and should be maintained.

## Consolidation Plan

### Task 10.2: Keep test_framework/ as Combat Lab core, but clean up

**Actions:**
1. `test_framework/scenario.py` - Keep as base class (minimal)
2. `test_framework/registry.py` - Keep, already properly references simulation_tests
3. `test_framework/runner.py` - Keep, used by Combat Lab UI
4. `test_framework/services/` - Keep, used by Combat Lab UI
5. `test_framework/scenarios/` - These are legacy simple scenarios, consider deprecating

**No merge needed** - The structure is actually correct:
- `test_framework/` = Combat Lab infrastructure
- `simulation_tests/` = Extended scenarios with pytest integration

### Task 10.3: Consolidate Mock Fixtures

**Move to `tests/fixtures/`:**
1. Move `create_test_metadata()` helper from services conftest to fixtures
2. Move mock fixtures (mock_battle_engine, mock_test_scenario) to fixtures/battle.py
3. Update imports in tests/test_framework/services/

**After consolidation:**
- `tests/fixtures/battle.py` - All battle-related mocks
- `tests/fixtures/test_scenarios.py` - Test scenario helpers (new file)
- `tests/test_framework/services/conftest.py` - Minimal, imports from fixtures

### Task 10.4: Documentation Updates

1. Update `simulation_tests/QUICK_START_GUIDE.md` with current structure
2. Document the relationship between frameworks
3. Add examples for creating new test scenarios

## Success Criteria

- [x] No duplicate mock fixtures (consolidated to tests/fixtures/test_scenarios.py)
- [x] Clear separation: test_framework (Combat Lab) vs simulation_tests (pytest scenarios)
- [x] Shared fixtures in tests/fixtures/ used by both
- [x] Documentation explains the architecture
- [x] All 1020 tests still pass

## Changes Made (Phase 10)

### New Files Created
- `tests/fixtures/test_scenarios.py` - Consolidated test scenario fixtures
- `docs/refactoring/TEST_CONSOLIDATION.md` - This documentation

### Files Modified
- `tests/fixtures/__init__.py` - Added exports for test scenario fixtures
- `tests/test_framework/services/conftest.py` - Now imports from tests/fixtures/

### Shared Fixtures Available
After Phase 10, the following fixtures are available from `tests.fixtures`:

```python
# Test scenario factories
from tests.fixtures import (
    create_test_metadata,        # Create TestMetadata with defaults
    create_mock_test_scenario,   # Mock TestScenario for unit tests
    create_mock_test_registry,   # Mock TestRegistry
    create_mock_test_runner,     # Mock TestRunner
    create_mock_test_history,    # Mock TestHistory
    create_scenario_info,        # Create registry scenario info dict
    create_sample_ship_data,     # Sample ship JSON data
    create_sample_component_data, # Sample component JSON data
)

# Battle engine factories (already existed)
from tests.fixtures import (
    create_mock_battle_engine,
    create_mock_battle_scene,
    create_battle_engine,
    create_battle_engine_with_ships,
)
```

## File Relationships Diagram

```
test_framework/                    # Combat Lab infrastructure
├── scenario.py                    # CombatScenario base class
├── registry.py                    # TestRegistry (discovers scenarios)
├── runner.py                      # TestRunner (executes scenarios)
├── test_history.py                # Execution history tracking
├── services/                      # UI service layer
│   ├── test_execution_service.py
│   ├── test_lab_controller.py
│   └── ...
└── scenarios/                     # Legacy simple scenarios
    └── simple_duel.py, etc.

simulation_tests/                  # Extended test scenarios
├── conftest.py                    # pytest fixtures
├── scenarios/
│   ├── base.py                    # TestScenario extends CombatScenario
│   ├── validation.py              # Validation rules
│   ├── beam_scenarios.py          # Weapon tests
│   └── ...
├── tests/                         # pytest test files
│   ├── test_beam_weapons.py
│   └── ...
└── data/                          # Test-specific data
    ├── ships/
    ├── components.json
    └── ...

tests/
├── fixtures/                      # Shared fixtures (Phase 5 created)
│   ├── paths.py
│   ├── ships.py
│   ├── components.py
│   └── battle.py
├── test_framework/
│   └── services/                  # Unit tests for Combat Lab services
│       ├── conftest.py            # Service-specific mocks
│       └── test_*.py
└── unit/                          # Unit tests for game code
    └── ...
```
