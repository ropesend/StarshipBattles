"""
Shared fixtures for resource system tests.

PROJ-211: Updated make_ship_instance to use DI.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List

from game.core.registry import RegistryManager, GameRegistries
from game.strategy.data.ship_instance import ShipInstance


@pytest.fixture
def loaded_registry():
    """
    Registry with real component data loaded.

    # PROJ-195: Legitimate — integration tests that add test components to singleton
    # for full-pipeline testing. ShipInstance.get_calculated_stats() internally uses
    # get_default_registry_provider() which reads from the singleton, so these tests
    # must add components there.

    Relies on reset_game_state (autouse) for isolation.
    That fixture clears, hydrates from SessionRegistryCache,
    and cleans up after each test automatically.
    """
    return RegistryManager.instance()


@pytest.fixture
def singleton_registries(loaded_registry):
    """
    GameRegistries backed by the singleton RegistryManager.

    PROJ-211: Use this when you need GameRegistries that tracks the singleton's
    state (e.g., when dynamically adding components during tests).

    The returned GameRegistries references the singleton's dictionaries directly,
    so any components added to loaded_registry.components will be visible.
    """
    return GameRegistries(
        components=loaded_registry.components,
        modifiers=loaded_registry.modifiers,
        vehicle_classes=loaded_registry.vehicle_classes,
        resources=loaded_registry.resources
    )


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
    name: str = None,
    registries: GameRegistries = None,
) -> ShipInstance:
    """Create a ShipInstance from design data.

    PROJ-211: Added registries parameter for DI compliance.
    """
    return ShipInstance.create(
        design_data=design_data,
        owner_id=owner_id,
        name=name or design_data.get('name', 'Test Ship'),
        registries=registries
    )
