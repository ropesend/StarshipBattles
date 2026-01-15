"""
Pytest fixtures for simulation tests.

Provides isolated data loading to prevent registry pollution between tests.
"""
import os
import sys

import pytest

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Path to simulation test data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='session', autouse=True)
def validate_test_data_schemas():
    """
    Validate all test data files against JSON schemas before running tests.

    This fixture runs once per test session to catch data errors early.
    If validation fails, the entire test session is aborted.
    """
    from simulation_tests.data.schema_validator import validate_test_data, validate_component_references

    print("\n" + "="*60)
    print("Validating Combat Lab test data schemas...")
    print("="*60 + "\n")

    # Schema validation
    passed, failed = validate_test_data(verbose=True)

    # Referential integrity validation
    valid_refs, invalid_refs = validate_component_references(verbose=True)

    # Fail fast if validation errors found
    if failed > 0:
        pytest.fail(f"Schema validation failed: {failed} files have errors. Fix schemas before running tests.")

    if invalid_refs > 0:
        pytest.fail(f"Component reference validation failed: {invalid_refs} ships have invalid component references.")

    print("[SUCCESS] All test data validated successfully\n")


@pytest.fixture(scope='session', autouse=True)
def init_pygame():
    """Initialize pygame once for all tests (needed for Vector2)."""
    import pygame
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(scope='class')
def isolated_registry():
    """
    Provide isolated registry for each test class.
    
    Clears all registries before loading test data, ensures no pollution
    from previous tests or production data.
    """
    from game.core.registry import RegistryManager
    from game.simulation.entities.ship import load_vehicle_classes
    from game.simulation.components.component import load_components, load_modifiers
    from game.ai.controller import load_combat_strategies
    
    # Clear registries
    RegistryManager.instance().clear()
    
    # Load test data
    load_vehicle_classes(os.path.join(DATA_DIR, 'vehicleclasses.json'))
    load_components(os.path.join(DATA_DIR, 'components.json'))
    load_modifiers(os.path.join(DATA_DIR, 'modifiers.json'))
    
    # Load combat strategies for AI
    load_combat_strategies(DATA_DIR)
    
    yield
    
    # Cleanup after test class
    RegistryManager.instance().clear()


@pytest.fixture
def data_dir():
    """Return path to simulation test data directory."""
    return DATA_DIR


@pytest.fixture
def ships_dir(data_dir):
    """Return path to pre-built ship JSON files."""
    return os.path.join(data_dir, 'ships')
