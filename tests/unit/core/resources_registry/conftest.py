"""
Shared fixtures for resource registry tests.
"""
import json
import pytest

from game.core.registry import get_default_registry_manager


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensure clean registry state before and after each test.

    # PROJ-195: Legitimate — isolation fixture for resource registry tests
    """
    registry = get_default_registry_manager()
    # Unfreeze if frozen
    registry._frozen = False
    registry.resources.clear()
    yield
    registry._frozen = False
    registry.resources.clear()


@pytest.fixture
def sample_resources_data():
    """Standard test data for resources."""
    return {
        "resources": [
            {"id": "fuel", "name": "Fuel", "max": 100},
            {"id": "energy", "name": "Energy", "max": 200},
            {"id": "ammo", "name": "Ammunition", "max": 50}
        ]
    }


@pytest.fixture
def sample_resources_file(tmp_path, sample_resources_data):
    """Create a temporary resources JSON file."""
    filepath = tmp_path / "resources.json"
    filepath.write_text(json.dumps(sample_resources_data))
    return str(filepath)
