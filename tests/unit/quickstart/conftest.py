"""
Conftest for quickstart fixture tests.

Provides path fixtures and utilities for loading quickstart test fixtures.
"""
import pytest
from pathlib import Path
from typing import List, Tuple, Dict, Any

from game.core.json_utils import load_json
from tests.fixtures.paths import get_project_root


def get_quickstart_fixtures_dir() -> Path:
    """Return the quickstart fixtures directory."""
    return get_project_root() / "tests" / "fixtures" / "quickstart"


def get_quickstart_races_dir() -> Path:
    """Return the quickstart races fixtures directory."""
    return get_quickstart_fixtures_dir() / "races"


def get_quickstart_designs_dir() -> Path:
    """Return the quickstart designs fixtures directory."""
    return get_quickstart_fixtures_dir() / "designs"


def load_all_quickstart_races() -> List[Tuple[str, Dict[str, Any]]]:
    """
    Load all race fixtures from the quickstart races directory.

    Returns:
        List of (race_name, race_data) tuples
    """
    races_dir = get_quickstart_races_dir()
    races = []
    if races_dir.exists():
        for json_file in sorted(races_dir.glob("*.json")):
            data = load_json(str(json_file))
            if data:
                races.append((json_file.stem, data))
    return races


def load_all_quickstart_designs() -> List[Tuple[str, Dict[str, Any]]]:
    """
    Load all design fixtures from the quickstart designs directory.

    Returns:
        List of (design_name, design_data) tuples
    """
    designs_dir = get_quickstart_designs_dir()
    designs = []
    if designs_dir.exists():
        for json_file in sorted(designs_dir.glob("*.json")):
            data = load_json(str(json_file))
            if data:
                designs.append((json_file.stem, data))
    return designs


@pytest.fixture
def quickstart_fixtures_dir() -> Path:
    """Fixture providing the quickstart fixtures directory path."""
    return get_quickstart_fixtures_dir()


@pytest.fixture
def quickstart_races_dir() -> Path:
    """Fixture providing the quickstart races directory path."""
    return get_quickstart_races_dir()


@pytest.fixture
def quickstart_designs_dir() -> Path:
    """Fixture providing the quickstart designs directory path."""
    return get_quickstart_designs_dir()
