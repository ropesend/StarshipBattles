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
