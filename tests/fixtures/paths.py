"""
Path utilities for tests.

This module provides consistent path resolution for tests, eliminating
hardcoded paths like "C:\\Dev\\Starship Battles".

Usage:
    from tests.fixtures.paths import get_project_root, get_data_dir

    # Get paths
    root = get_project_root()
    data = get_data_dir()

    # Or use pytest fixtures (defined below)
    def test_something(data_dir):
        components_file = data_dir / "components.json"
"""
import pytest
from pathlib import Path

from game.core.paths import Paths


def get_project_root() -> Path:
    """
    Return the project root directory.

    Delegates to game.core.paths.Paths for consistent path resolution.

    Returns:
        Path to the project root directory
    """
    return Paths.get_root()


def get_data_dir() -> Path:
    """
    Return the game data directory.

    Delegates to game.core.paths.Paths for consistent path resolution.

    Returns:
        Path to the data/ directory
    """
    return Paths.get_data_dir()


def get_assets_dir() -> Path:
    """
    Return the assets directory.

    Delegates to game.core.paths.Paths for consistent path resolution.

    Returns:
        Path to the assets/ directory
    """
    return Paths.get_assets_dir()


def get_test_data_dir() -> Path:
    """
    Return the test data directory.

    Creates the directory if it doesn't exist.

    Returns:
        Path to the tests/data/ directory
    """
    test_data = get_project_root() / "tests" / "data"
    test_data.mkdir(parents=True, exist_ok=True)
    return test_data


def get_unit_test_data_dir() -> Path:
    """
    Return the unit test data directory.

    This directory contains test-specific JSON files like test_vehicleclasses.json,
    test_targeting_policies.json, etc.

    Returns:
        Path to the tests/unit/data/ directory
    """
    return get_project_root() / "tests" / "unit" / "data"


def get_combat_lab_data_dir() -> Path:
    """
    Return the combat lab data directory.

    This directory contains test data for combat simulation tests including
    components.json, modifiers.json, vehicleclasses.json, and ship configurations.

    Returns:
        Path to the combat_lab/data/ directory
    """
    return get_project_root() / "combat_lab" / "data"


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def project_root() -> Path:
    """Fixture providing the project root path."""
    return get_project_root()


@pytest.fixture
def data_dir() -> Path:
    """Fixture providing the game data directory path."""
    return get_data_dir()


@pytest.fixture
def assets_dir() -> Path:
    """Fixture providing the assets directory path."""
    return get_assets_dir()


@pytest.fixture
def test_data_dir() -> Path:
    """Fixture providing the test data directory path."""
    return get_test_data_dir()


@pytest.fixture
def unit_test_data_dir() -> Path:
    """Fixture providing the unit test data directory path."""
    return get_unit_test_data_dir()


@pytest.fixture
def combat_lab_data_dir() -> Path:
    """Fixture providing the combat lab data directory path."""
    return get_combat_lab_data_dir()
