"""
Shared fixtures for resource system tests.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List

from game.core.registry import RegistryManager
from game.strategy.data.ship_instance import ShipInstance


@pytest.fixture
def registry_manager():
    """Get a clean registry manager for each test."""
    mgr = RegistryManager.instance()
    # Store original state
    orig_components = dict(mgr.components)
    orig_resources = dict(mgr.resources)

    yield mgr

    # Restore original state
    mgr.components.clear()
    mgr.components.update(orig_components)
    mgr.resources.clear()
    mgr.resources.update(orig_resources)


@pytest.fixture
def loaded_registry(global_ship_data, registry_manager):
    """
    Registry with real component data loaded.

    Uses the global_ship_data fixture to ensure components are loaded.
    """
    return registry_manager


@dataclass
class MockComponentDef:
    """Mock component definition for testing."""
    id: str
    mass: float
    max_hp: float
    type_str: str
    abilities: Dict[str, Any]


def create_mock_component(
    comp_id: str,
    mass: float = 100,
    max_hp: float = 100,
    comp_type: str = "Generic",
    abilities: Dict[str, Any] = None
) -> MockComponentDef:
    """Create a mock component definition."""
    return MockComponentDef(
        id=comp_id,
        mass=mass,
        max_hp=max_hp,
        type_str=comp_type,
        abilities=abilities or {}
    )


def create_test_ship_design(
    name: str,
    components: List[Dict[str, Any]],
    vehicle_type: str = "Ship"
) -> Dict[str, Any]:
    """Create a test ship design dictionary."""
    return {
        'name': name,
        'vehicle_type': vehicle_type,
        'layers': {
            'CORE': components
        },
        'expected_stats': {}
    }


def make_ship_instance(
    design_data: Dict[str, Any],
    owner_id: int = 0,
    name: str = None
) -> ShipInstance:
    """Create a ShipInstance from design data."""
    return ShipInstance.create(
        design_data=design_data,
        owner_id=owner_id,
        name=name or design_data.get('name', 'Test Ship')
    )
