"""
Common test fixtures shared across test modules.

This module provides reusable fixtures for initializing ship data,
eliminating duplication across module-specific conftest files.

Usage in conftest.py:
    from tests.fixtures.common import (
        initialized_ship_data,
        initialized_ship_data_with_modifiers,
    )
"""
import pytest
from pathlib import Path

from tests.fixtures.paths import get_data_dir, get_project_root, get_unit_test_data_dir
from game.simulation.entities.ship import initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers


@pytest.fixture
def initialized_ship_data():
    """
    Initialize ship data from production data directory.

    Loads vehicle classes and components but not modifiers.
    Use initialized_ship_data_with_modifiers if modifiers are needed.
    """
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    return True


@pytest.fixture
def initialized_ship_data_with_modifiers():
    """
    Initialize ship data and modifiers from production data directory.

    Loads vehicle classes, components, and modifiers.
    """
    initialize_ship_data(str(get_project_root()))
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"))
    load_modifiers(str(data_dir / "modifiers.json"))
    return True
