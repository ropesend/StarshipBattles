"""Shared fixtures for fleet tests."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


@pytest.fixture
def basic_fleet():
    """Create a basic fleet for testing."""
    return Fleet(
        fleet_id="fleet_1",
        owner_id=0,
        location=HexCoord(0, 0),
        speed=5.0
    )


@pytest.fixture
def make_mock_ship(fresh_registries):
    """Factory for creating mock ship instances.

    PROJ-211: Updated to set _registries for DI compliance.
    """
    from game.strategy.data.ship_instance import ShipInstance

    def _make(name="Test Ship", is_combat_capable=True):
        mock = MagicMock(spec=ShipInstance)
        mock.name = name
        mock.is_combat_capable.return_value = is_combat_capable
        mock.get_all_resource_costs_per_hex.return_value = {}
        # Required for speed recalculation
        mock.design_data = {'vehicle_type': 'Ship'}
        mock.get_calculated_stats.return_value = {
            'mass': 100,
            'strategic_movement': 500  # Results in speed ~5
        }
        # PROJ-211: Set _registries for DI compliance
        mock._registries = fresh_registries
        return mock
    return _make


@pytest.fixture
def make_ship_instance():
    """Factory for creating ShipInstance objects for serialization tests."""
    from game.strategy.data.ship_instance import ShipInstance

    def _make(name="Test Ship", design_id=None, owner_id=0):
        return ShipInstance(
            instance_id=f"test-{name.lower().replace(' ', '-')}",
            design_id=design_id or name,
            name=name,
            owner_id=owner_id,
            design_data={'name': name, 'vehicle_type': 'Ship'},
        )
    return _make
