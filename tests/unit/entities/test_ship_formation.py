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
def pygame_init(fresh_registries):
    """Initialize and cleanup pygame for each test."""
    if not pygame.get_init():
        pygame.init()
    yield fresh_registries
    if pygame.get_init():
        pygame.quit()
    mock.patch.stopall()


class TestShipFormationUnit:
    """Unit tests for ShipFormation class in isolation."""

    def test_initialization_defaults(self, pygame_init):
        """ShipFormation initializes with correct default values."""
        registries = pygame_init
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=registries)
        formation = ShipFormation(ship)

        assert formation.ship is ship
        assert formation.master is None
        assert formation.offset is None
        assert formation.rotation_mode == 'relative'
        assert formation.members == []
        assert formation.active is True

    def test_is_master_property(self, pygame_init):
        """is_master returns True when ship has members."""
        registries = pygame_init
        ship = Ship("MasterShip", 0, 0, (255, 255, 255), registries=registries)
        formation = ShipFormation(ship)

        assert formation.is_master is False

        # Add a dummy member
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200), registries=registries)
        formation.members.append(follower)

        assert formation.is_master is True

    def test_is_member_property(self, pygame_init):
        """is_member returns True when ship has a master."""
        registries = pygame_init
        ship = Ship("FollowerShip", 100, 0, (255, 255, 255), registries=registries)
        formation = ShipFormation(ship)

        assert formation.is_member is False

        master = Ship("MasterShip", 0, 0, (200, 200, 200), registries=registries)
        formation.master = master

        assert formation.is_member is True

    def test_join_formation(self, pygame_init):
        """join() sets up the formation relationship correctly."""
        registries = pygame_init
        master = Ship("MasterShip", 0, 0, (255, 255, 255), registries=registries)
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200), registries=registries)

        offset = pygame.math.Vector2(50, 30)
        follower_formation = ShipFormation(follower)
        follower_formation.join(master, offset)

        assert follower_formation.master is master
        assert follower_formation.offset == offset
        assert follower_formation.active is True

    def test_leave_formation(self, pygame_init):
        """leave() clears the formation relationship."""
        registries = pygame_init
        master = Ship("MasterShip", 0, 0, (255, 255, 255), registries=registries)
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200), registries=registries)

        offset = pygame.math.Vector2(50, 30)
        follower_formation = ShipFormation(follower)
        follower_formation.join(master, offset)

        # Now leave
        follower_formation.leave()

        assert follower_formation.master is None
        assert follower_formation.active is False

    def test_add_member(self, pygame_init):
        """add_member() adds a follower to the formation."""
        registries = pygame_init
        master = Ship("MasterShip", 0, 0, (255, 255, 255), registries=registries)
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200), registries=registries)

        master_formation = ShipFormation(master)
        offset = pygame.math.Vector2(-50, 20)
        master_formation.add_member(follower, offset)

        assert follower in master_formation.members
        assert master_formation.is_master is True

    def test_remove_member(self, pygame_init):
        """remove_member() removes a follower from the formation."""
        registries = pygame_init
        master = Ship("MasterShip", 0, 0, (255, 255, 255), registries=registries)
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200), registries=registries)

        master_formation = ShipFormation(master)
        offset = pygame.math.Vector2(-50, 20)
        master_formation.add_member(follower, offset)

        # Now remove
        master_formation.remove_member(follower)

        assert follower not in master_formation.members
        assert master_formation.is_master is False

    def test_rotation_mode_fixed(self, pygame_init):
        """rotation_mode can be set to 'fixed'."""
        registries = pygame_init
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=registries)
        formation = ShipFormation(ship)

        formation.rotation_mode = 'fixed'
        assert formation.rotation_mode == 'fixed'


class TestShipFormationIntegration:
    """Integration tests for ShipFormation with Ship class."""

    def test_ship_has_formation_attribute(self, pygame_init):
        """Ship has a formation attribute of type ShipFormation."""
        registries = pygame_init
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=registries)

        assert hasattr(ship, 'formation')
        assert isinstance(ship.formation, ShipFormation)

    def test_formation_master_via_direct_api(self, pygame_init):
        """ship.formation.master can be set and read directly."""
        registries = pygame_init
        master = Ship("MasterShip", 0, 0, (255, 255, 255), registries=registries)
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200), registries=registries)

        # Set via direct formation API
        follower.formation.master = master

        # Verify via formation object
        assert follower.formation.master is master

    def test_formation_offset_via_direct_api(self, pygame_init):
        """ship.formation.offset can be set and read directly."""
        registries = pygame_init
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=registries)
        offset = pygame.math.Vector2(100, 50)

        ship.formation.offset = offset

        assert ship.formation.offset == offset

    def test_formation_rotation_mode_via_direct_api(self, pygame_init):
        """ship.formation.rotation_mode can be set and read directly."""
        registries = pygame_init
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=registries)

        ship.formation.rotation_mode = 'fixed'

        assert ship.formation.rotation_mode == 'fixed'

    def test_formation_members_via_direct_api(self, pygame_init):
        """ship.formation.members can be appended to and read directly."""
        registries = pygame_init
        master = Ship("MasterShip", 0, 0, (255, 255, 255), registries=registries)
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200), registries=registries)

        master.formation.members.append(follower)

        assert follower in master.formation.members

    def test_formation_active_via_direct_api(self, pygame_init):
        """ship.formation.active can be set and read directly."""
        registries = pygame_init
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=registries)

        assert ship.formation.active is True

        ship.formation.active = False

        assert ship.formation.active is False
