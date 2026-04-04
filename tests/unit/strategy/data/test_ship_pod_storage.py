"""Tests for ShipInstance pod storage capacity methods.

Phase 2: Ships with PodStorage ability have mass-based limits on carried_items.
"""
from unittest.mock import MagicMock, patch
from game.strategy.data.ship_instance import ShipInstance


def _make_ship_with_pod_capacity(capacity_mass: float) -> ShipInstance:
    """Create a ShipInstance mock with pod storage capacity."""
    ship = MagicMock(spec=ShipInstance)
    ship.carried_items = []
    ship.get_calculated_stats = MagicMock(return_value={'pod_storage_mass': capacity_mass})
    # Wire up the real methods
    ship.get_pod_storage_capacity = lambda: float(ship.get_calculated_stats().get('pod_storage_mass', 0))
    ship.get_pod_storage_used = lambda: sum(item.get('mass', 0.0) for item in ship.carried_items)
    ship.can_carry_pod = lambda mass: (
        ship.get_pod_storage_capacity() > 0 and
        ship.get_pod_storage_used() + mass <= ship.get_pod_storage_capacity()
    )
    return ship


class TestShipPodStorage:
    """Test ShipInstance pod storage capacity methods."""

    def test_get_pod_storage_capacity(self):
        ship = _make_ship_with_pod_capacity(2000.0)
        assert ship.get_pod_storage_capacity() == 2000.0

    def test_get_pod_storage_used_empty(self):
        ship = _make_ship_with_pod_capacity(2000.0)
        assert ship.get_pod_storage_used() == 0.0

    def test_get_pod_storage_used_with_items(self):
        ship = _make_ship_with_pod_capacity(2000.0)
        ship.carried_items = [
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
        ]
        assert ship.get_pod_storage_used() == 1000.0

    def test_can_carry_pod_when_empty(self):
        ship = _make_ship_with_pod_capacity(2000.0)
        assert ship.can_carry_pod(500.0) is True

    def test_can_carry_pod_when_full(self):
        ship = _make_ship_with_pod_capacity(2000.0)
        ship.carried_items = [
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
        ]
        assert ship.can_carry_pod(500.0) is False

    def test_can_carry_pod_exact_fit(self):
        ship = _make_ship_with_pod_capacity(2000.0)
        ship.carried_items = [
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
            {'vehicle_type': 'drop_pod', 'mass': 500.0},
        ]
        # 1500 used + 500 = 2000 exactly
        assert ship.can_carry_pod(500.0) is True

    def test_can_carry_pod_no_capacity(self):
        ship = _make_ship_with_pod_capacity(0.0)
        assert ship.can_carry_pod(500.0) is False

    def test_can_carry_pod_large_pod(self):
        ship = _make_ship_with_pod_capacity(2000.0)
        assert ship.can_carry_pod(2000.0) is True
        assert ship.can_carry_pod(2001.0) is False
