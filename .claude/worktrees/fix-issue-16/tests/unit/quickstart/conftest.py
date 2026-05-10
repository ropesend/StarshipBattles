"""
Conftest for quickstart fixture tests.

Provides path fixtures and utilities for loading quickstart starter data files.
"""
import pytest
from pathlib import Path
from typing import List, Tuple, Dict, Any

from game.core.json_utils import load_json
from game.core.paths import Paths


def get_quickstart_races_dir() -> Path:
    """Return the starter races data directory."""
    return Paths.get_starter_races_dir()


def get_quickstart_designs_dir() -> Path:
    """Return the starter designs data directory."""
    return Paths.get_starter_designs_dir()


def load_all_quickstart_races() -> List[Tuple[str, Dict[str, Any]]]:
    """
    Load all race files from the starter races data directory.

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
    Load all design files from the starter designs data directory.

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
def quickstart_races_dir() -> Path:
    """Fixture providing the starter races directory path."""
    return get_quickstart_races_dir()


@pytest.fixture
def quickstart_designs_dir() -> Path:
    """Fixture providing the starter designs directory path."""
    return get_quickstart_designs_dir()
