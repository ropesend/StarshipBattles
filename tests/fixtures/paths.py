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
from typing import Optional

# Cache the project root to avoid repeated filesystem traversal
_project_root: Optional[Path] = None


def get_project_root() -> Path:
    """
    Return the project root directory.

    The project root is identified by containing both 'game/' and 'data/' directories.
    This function caches the result for performance.

    Returns:
        Path to the project root directory

    Raises:
        RuntimeError: If project root cannot be found
    """
    global _project_root

    if _project_root is not None:
        return _project_root

    # Start from this file's location and walk up
    current = Path(__file__).resolve().parent

    # Walk up the directory tree looking for project markers
    for _ in range(10):  # Limit iterations to avoid infinite loop
        if (current / "game").is_dir() and (current / "data").is_dir():
            _project_root = current
            return _project_root
        parent = current.parent
        if parent == current:
            # Reached filesystem root
            break
        current = parent

    raise RuntimeError(
        "Could not find project root. Expected directory containing 'game/' and 'data/'."
    )


def get_data_dir() -> Path:
    """
    Return the game data directory.

    Returns:
        Path to the data/ directory
    """
    return get_project_root() / "data"


def get_assets_dir() -> Path:
    """
    Return the assets directory.

    Returns:
        Path to the assets/ directory
    """
    return get_project_root() / "assets"


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
