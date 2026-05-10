"""
Tests for Ship.id using UUID4 instead of id(self).

PROJ-247: Ship ID should be a stable UUID4 string, not a memory address.
This ensures:
- Ship IDs are unique across process lifetime
- Ship IDs survive garbage collection (no address reuse)
- Ship IDs are proper UUID4 format
- Two different Ship instances get different IDs
"""
import re
import pytest

from game.simulation.entities.ship import Ship
from game.core.registry import GameRegistries


UUID4_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
)


@pytest.fixture
def registries():
    """Create minimal GameRegistries for Ship construction."""
    return GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})


class TestShipIdIsUUID:
    """Ship.id should be a UUID4 string."""

    def test_ship_id_is_uuid4_format(self, registries):
        """Ship.id should match UUID4 pattern."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=registries)
        assert UUID4_PATTERN.match(ship.id), (
            f"Ship.id should be UUID4 format, got: {ship.id}"
        )

    def test_ship_id_is_string(self, registries):
        """Ship.id should be a string."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=registries)
        assert isinstance(ship.id, str)

    def test_two_ships_have_different_ids(self, registries):
        """Two different ships should have different IDs."""
        ship1 = Ship("Ship1", 0, 0, (255, 0, 0), registries=registries)
        ship2 = Ship("Ship2", 100, 100, (0, 255, 0), registries=registries)
        assert ship1.id != ship2.id

    def test_ship_id_not_memory_address(self, registries):
        """Ship.id should NOT be the str(id(self)) memory address."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=registries)
        # Memory addresses are plain decimal integers as strings
        # UUID4 strings contain hyphens, so they can never match
        assert '-' in ship.id, "Ship.id should contain hyphens (UUID4 format)"

    def test_ship_id_stable_after_creation(self, registries):
        """Ship.id should not change after creation."""
        ship = Ship("Test", 0, 0, (255, 0, 0), registries=registries)
        id_at_creation = ship.id
        # Do some operations
        ship.recalculate_stats()
        assert ship.id == id_at_creation
