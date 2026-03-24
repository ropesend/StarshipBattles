"""Tests for Empire fleet auto-registration/unregistration (PROJ-219).

Verifies that Empire.add_fleet() auto-registers with galaxy and
Empire.remove_fleet() auto-unregisters from galaxy.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


@pytest.fixture
def galaxy():
    """Mock galaxy with register/unregister methods."""
    mock = MagicMock()
    mock.register_fleet = MagicMock()
    mock.unregister_fleet = MagicMock()
    return mock


@pytest.fixture
def empire():
    """Empire without galaxy reference."""
    return Empire(0, "Test Empire", (255, 0, 0))


@pytest.fixture
def empire_with_galaxy(galaxy):
    """Empire with galaxy reference set."""
    emp = Empire(0, "Test Empire", (255, 0, 0))
    emp.set_galaxy(galaxy)
    return emp


@pytest.fixture
def fleet():
    """Simple fleet for testing."""
    return Fleet(1, 0, HexCoord(0, 0))


class TestEmpireFleetAutoRegistration:
    """Tests for automatic fleet registration/unregistration via Empire."""

    def test_add_fleet_without_galaxy_does_not_crash(self, empire, fleet):
        """Empire without galaxy can still add fleets (backward compat)."""
        empire.add_fleet(fleet)
        assert fleet in empire.fleets
        assert fleet.owner_id == 0

    def test_add_fleet_with_galaxy_auto_registers(self, empire_with_galaxy, galaxy, fleet):
        """add_fleet() auto-registers fleet with galaxy when galaxy is set."""
        empire_with_galaxy.add_fleet(fleet)
        assert fleet in empire_with_galaxy.fleets
        assert fleet.owner_id == 0
        galaxy.register_fleet.assert_called_once_with(fleet)

    def test_remove_fleet_with_galaxy_auto_unregisters(self, empire_with_galaxy, galaxy, fleet):
        """remove_fleet() auto-unregisters fleet from galaxy when galaxy is set."""
        empire_with_galaxy.add_fleet(fleet)
        galaxy.register_fleet.reset_mock()

        empire_with_galaxy.remove_fleet(fleet)
        assert fleet not in empire_with_galaxy.fleets
        galaxy.unregister_fleet.assert_called_once_with(fleet)

    def test_remove_fleet_without_galaxy_does_not_crash(self, empire, fleet):
        """Empire without galaxy can still remove fleets (backward compat)."""
        empire.add_fleet(fleet)
        empire.remove_fleet(fleet)
        assert fleet not in empire.fleets

    def test_set_galaxy_enables_registration(self, empire, galaxy, fleet):
        """set_galaxy() enables auto-registration for subsequent calls."""
        # Before set_galaxy: no registration
        empire.add_fleet(fleet)
        galaxy.register_fleet.assert_not_called()

        # Set galaxy
        empire.set_galaxy(galaxy)

        # After set_galaxy: registration enabled
        fleet2 = Fleet(2, 0, HexCoord(1, 1))
        empire.add_fleet(fleet2)
        galaxy.register_fleet.assert_called_once_with(fleet2)

    def test_remove_fleet_not_in_list_does_not_crash(self, empire_with_galaxy, galaxy, fleet):
        """Removing a fleet not in empire.fleets is a no-op (no crash, no unregister)."""
        empire_with_galaxy.remove_fleet(fleet)
        assert fleet not in empire_with_galaxy.fleets
        galaxy.unregister_fleet.assert_not_called()

    def test_galaxy_not_serialized(self, empire_with_galaxy):
        """_galaxy is transient and not included in to_dict()."""
        data = empire_with_galaxy.to_dict()
        assert '_galaxy' not in data
        assert 'galaxy' not in data


class TestRemoveFleetPursuerCancel:
    """Tests for pursuer cancellation when fleet is removed (PROJ-222 Phase 4)."""

    def test_remove_fleet_cancels_pursuer_orders(self):
        """When Fleet B is removed, Fleet A (pursuing B) should have its orders cancelled."""
        from game.strategy.data.order_types import FleetOrder, OrderType

        empire = Empire(0, "Test", (255, 0, 0))
        fleet_a = Fleet(1, 0, HexCoord(0, 0))
        fleet_b = Fleet(2, 0, HexCoord(5, 5))

        empire.add_fleet(fleet_a)
        empire.add_fleet(fleet_b)

        # A pursues B
        fleet_a.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=fleet_b))
        fleet_a.add_order(FleetOrder(OrderType.JOIN_FLEET, target=fleet_b))
        fleet_b.pursuer_tracker.add_pursuer(fleet_a)

        # B is destroyed
        empire.remove_fleet(fleet_b)

        # A's targeting orders should be removed
        assert len(fleet_a.orders) == 0
        assert fleet_b.pursuer_tracker.pursuer_count == 0

    def test_remove_fleet_no_pursuers(self):
        """Removing a fleet with no pursuers should not error."""
        empire = Empire(0, "Test", (255, 0, 0))
        fleet = Fleet(1, 0, HexCoord(0, 0))
        empire.add_fleet(fleet)

        # Should not raise
        empire.remove_fleet(fleet)
        assert fleet not in empire.fleets

    def test_remove_fleet_preserves_non_targeting_orders(self):
        """Only orders targeting the removed fleet are cancelled."""
        from game.strategy.data.order_types import FleetOrder, OrderType

        empire = Empire(0, "Test", (255, 0, 0))
        fleet_a = Fleet(1, 0, HexCoord(0, 0))
        fleet_b = Fleet(2, 0, HexCoord(5, 5))
        fleet_c = Fleet(3, 0, HexCoord(10, 10))

        empire.add_fleet(fleet_a)
        empire.add_fleet(fleet_b)
        empire.add_fleet(fleet_c)

        # A has orders targeting both B and C
        fleet_a.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(3, 3)))
        fleet_a.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=fleet_b))
        fleet_a.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=fleet_c))
        fleet_b.pursuer_tracker.add_pursuer(fleet_a)

        # B is destroyed
        empire.remove_fleet(fleet_b)

        # Only B-targeting order removed; MOVE and C-targeting preserved
        assert len(fleet_a.orders) == 2
        assert fleet_a.orders[0].target == HexCoord(3, 3)
        assert fleet_a.orders[1].target is fleet_c
