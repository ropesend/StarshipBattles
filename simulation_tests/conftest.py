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
