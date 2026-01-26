"""
Tests for ShipFormation class (formation relationship management).
TDD-first approach for ShipFormation extraction from Ship class.
"""
import pytest
import pygame
from unittest import mock

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.entities.ship_formation import ShipFormation
from game.simulation.components.component import load_components
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for each test."""
    if not pygame.get_init():
        pygame.init()
    initialize_ship_data()
    load_components(str(get_data_dir() / "components.json"))
    yield
    RegistryManager.instance().clear()
    if pygame.get_init():
        pygame.quit()
    mock.patch.stopall()


class TestShipFormationUnit:
    """Unit tests for ShipFormation class in isolation."""

    def test_initialization_defaults(self, pygame_init):
        """ShipFormation initializes with correct default values."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        formation = ShipFormation(ship)

        assert formation.ship is ship
        assert formation.master is None
        assert formation.offset is None
        assert formation.rotation_mode == 'relative'
        assert formation.members == []
        assert formation.active is True

    def test_is_master_property(self, pygame_init):
        """is_master returns True when ship has members."""
        ship = Ship("MasterShip", 0, 0, (255, 255, 255))
        formation = ShipFormation(ship)

        assert formation.is_master is False

        # Add a dummy member
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        formation.members.append(follower)

        assert formation.is_master is True

    def test_is_member_property(self, pygame_init):
        """is_member returns True when ship has a master."""
        ship = Ship("FollowerShip", 100, 0, (255, 255, 255))
        formation = ShipFormation(ship)

        assert formation.is_member is False

        master = Ship("MasterShip", 0, 0, (200, 200, 200))
        formation.master = master

        assert formation.is_member is True

    def test_join_formation(self, pygame_init):
        """join() sets up the formation relationship correctly."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))

        offset = pygame.math.Vector2(50, 30)
        follower_formation = ShipFormation(follower)
        follower_formation.join(master, offset)

        assert follower_formation.master is master
        assert follower_formation.offset == offset
        assert follower_formation.active is True

    def test_leave_formation(self, pygame_init):
        """leave() clears the formation relationship."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))

        offset = pygame.math.Vector2(50, 30)
        follower_formation = ShipFormation(follower)
        follower_formation.join(master, offset)

        # Now leave
        follower_formation.leave()

        assert follower_formation.master is None
        assert follower_formation.active is False

    def test_add_member(self, pygame_init):
        """add_member() adds a follower to the formation."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))

        master_formation = ShipFormation(master)
        offset = pygame.math.Vector2(-50, 20)
        master_formation.add_member(follower, offset)

        assert follower in master_formation.members
        assert master_formation.is_master is True

    def test_remove_member(self, pygame_init):
        """remove_member() removes a follower from the formation."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))

        master_formation = ShipFormation(master)
        offset = pygame.math.Vector2(-50, 20)
        master_formation.add_member(follower, offset)

        # Now remove
        master_formation.remove_member(follower)

        assert follower not in master_formation.members
        assert master_formation.is_master is False

    def test_rotation_mode_fixed(self, pygame_init):
        """rotation_mode can be set to 'fixed'."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        formation = ShipFormation(ship)

        formation.rotation_mode = 'fixed'
        assert formation.rotation_mode == 'fixed'


class TestShipFormationIntegration:
    """Integration tests for ShipFormation with Ship class."""

    def test_ship_has_formation_attribute(self, pygame_init):
        """Ship has a formation attribute of type ShipFormation."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))

        assert hasattr(ship, 'formation')
        assert isinstance(ship.formation, ShipFormation)

    def test_backward_compat_formation_master(self, pygame_init):
        """ship.formation_master delegates to ship.formation.master."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))

        # Set via delegation property
        follower.formation_master = master

        # Verify via formation object
        assert follower.formation.master is master

        # Get via delegation property
        assert follower.formation_master is master

    def test_backward_compat_formation_offset(self, pygame_init):
        """ship.formation_offset delegates to ship.formation.offset."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        offset = pygame.math.Vector2(100, 50)

        ship.formation_offset = offset

        assert ship.formation.offset == offset
        assert ship.formation_offset == offset

    def test_backward_compat_formation_rotation_mode(self, pygame_init):
        """ship.formation_rotation_mode delegates to ship.formation.rotation_mode."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))

        ship.formation_rotation_mode = 'fixed'

        assert ship.formation.rotation_mode == 'fixed'
        assert ship.formation_rotation_mode == 'fixed'

    def test_backward_compat_formation_members(self, pygame_init):
        """ship.formation_members delegates to ship.formation.members."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))

        master.formation_members.append(follower)

        assert follower in master.formation.members
        assert follower in master.formation_members

    def test_backward_compat_in_formation(self, pygame_init):
        """ship.in_formation delegates to ship.formation.active."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))

        assert ship.in_formation is True

        ship.in_formation = False

        assert ship.formation.active is False
        assert ship.in_formation is False
