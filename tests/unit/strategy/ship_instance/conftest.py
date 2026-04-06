"""
Shared fixtures for ShipInstance PROJ-08 tests.

PROJ-48: Extracted from test_ship_instance_proj08.py during test file splitting.
PROJ-211: Added make_ship_with_stats fixture for DI-compliant ship creation.
"""

import pytest
from game.strategy.data.ship_instance import ShipInstance


@pytest.fixture
def make_design_data_with_stats():
    """Factory for creating design_data with expected_stats."""
    def _make(expected_stats=None):
        return {
            'layers': {},
            'name': 'TestShip',
            'expected_stats': expected_stats or {}
        }
    return _make


@pytest.fixture
def make_ship_with_stats(fresh_registries, make_design_data_with_stats):
    """
    Factory for creating ShipInstance with expected_stats and DI-compliant registries.

    PROJ-211: Use this fixture instead of direct ShipInstance() constructor
    when tests need to call get_calculated_stats() or related methods.
    """
    def _make(expected_stats=None, **kwargs):
        design_data = make_design_data_with_stats(expected_stats)
        ship = ShipInstance(
            instance_id=kwargs.get('instance_id', 'test-1'),
            design_id=kwargs.get('design_id', 'TestDesign'),
            name=kwargs.get('name', 'Test Ship'),
            owner_id=kwargs.get('owner_id', 0),
            design_data=design_data
        )
        ship.set_registries(fresh_registries)
        # Pre-set cached stats so tests that need known stat values
        # don't depend on the stat calculator (which needs real components).
        if expected_stats:
            ship._cached_stats = expected_stats
        return ship
    return _make
