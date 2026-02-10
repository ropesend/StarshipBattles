"""
Tests for cargo tracking on ShipInstance and Fleet.

PROJ-68 Phase 5: Cargo state tracking for passenger/goods transport.
"""

import pytest
from unittest.mock import patch, MagicMock

from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


# --- Fixtures ---

@pytest.fixture
def mock_registries():
    """Create mock registries for stats calculation."""
    registries = MagicMock()
    registries.vehicle_classes = {}
    registries.modifiers = MagicMock()
    registries.modifiers.get = MagicMock(return_value=None)
    return registries


@pytest.fixture
def ship_with_cargo_capacity(mock_registries):
    """Create a ShipInstance with cargo capacity in stats."""
    instance = ShipInstance(
        instance_id="test-ship-1",
        design_id="transport",
        name="Transport Ship",
        owner_id=0,
        design_data={
            'name': 'Transport Ship',
            'expected_stats': {
                'max_hp': 100,
                'mass': 500,
                'cargo_storage': {'passengers': 5000, 'generic': 1000},
            }
        },
    )
    return instance


@pytest.fixture
def ship_without_cargo():
    """Create a ShipInstance without cargo capacity."""
    instance = ShipInstance(
        instance_id="test-ship-2",
        design_id="fighter",
        name="Fighter",
        owner_id=0,
        design_data={
            'name': 'Fighter',
            'expected_stats': {
                'max_hp': 50,
                'mass': 100,
                'cargo_storage': {},
            }
        },
    )
    return instance


@pytest.fixture
def fleet_with_cargo_ships(ship_with_cargo_capacity, ship_without_cargo):
    """Create a fleet with multiple ships including cargo ships."""
    fleet = Fleet(
        fleet_id=1,
        owner_id=0,
        location=HexCoord(0, 0),
    )
    # Add two cargo ships (create a second one)
    ship2 = ShipInstance(
        instance_id="test-ship-3",
        design_id="transport",
        name="Transport Ship 2",
        owner_id=0,
        design_data={
            'name': 'Transport Ship 2',
            'expected_stats': {
                'max_hp': 100,
                'mass': 500,
                'cargo_storage': {'passengers': 3000},
            }
        },
    )
    fleet.ships.append(ship_with_cargo_capacity)
    fleet.ships.append(ship2)
    fleet.ships.append(ship_without_cargo)
    return fleet


# --- ShipInstance Cargo Tests ---

class TestShipInstanceCargoCapacity:
    """Tests for ShipInstance.get_cargo_capacity()."""

    def test_ship_instance_cargo_capacity(self, ship_with_cargo_capacity):
        """Test reading cargo capacity from calculated stats."""
        capacity = ship_with_cargo_capacity.get_cargo_capacity('passengers')
        assert capacity == 5000

    def test_ship_instance_cargo_capacity_generic(self, ship_with_cargo_capacity):
        """Test reading generic cargo capacity."""
        capacity = ship_with_cargo_capacity.get_cargo_capacity('generic')
        assert capacity == 1000

    def test_ship_instance_cargo_capacity_missing_type(self, ship_with_cargo_capacity):
        """Test cargo capacity returns 0 for missing cargo type."""
        capacity = ship_with_cargo_capacity.get_cargo_capacity('fuel_pods')
        assert capacity == 0

    def test_ship_instance_cargo_capacity_no_cargo_ship(self, ship_without_cargo):
        """Test cargo capacity returns 0 for ships without cargo."""
        capacity = ship_without_cargo.get_cargo_capacity('passengers')
        assert capacity == 0


class TestShipInstanceLoadCargo:
    """Tests for ShipInstance.load_cargo()."""

    def test_ship_instance_load_cargo(self, ship_with_cargo_capacity):
        """Test basic cargo loading."""
        loaded = ship_with_cargo_capacity.load_cargo('passengers', 1000)
        assert loaded == 1000
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 1000

    def test_ship_instance_load_cargo_multiple_times(self, ship_with_cargo_capacity):
        """Test loading cargo multiple times accumulates."""
        ship_with_cargo_capacity.load_cargo('passengers', 1000)
        ship_with_cargo_capacity.load_cargo('passengers', 500)
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 1500

    def test_ship_instance_load_over_capacity(self, ship_with_cargo_capacity):
        """Test loading more than capacity is capped."""
        loaded = ship_with_cargo_capacity.load_cargo('passengers', 10000)
        assert loaded == 5000  # Capped at capacity
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 5000

    def test_ship_instance_load_partial_over_capacity(self, ship_with_cargo_capacity):
        """Test loading when some space is already used."""
        ship_with_cargo_capacity.load_cargo('passengers', 4000)
        loaded = ship_with_cargo_capacity.load_cargo('passengers', 3000)
        assert loaded == 1000  # Only 1000 space remaining
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 5000

    def test_ship_instance_load_no_capacity(self, ship_without_cargo):
        """Test loading to ship with no capacity returns 0."""
        loaded = ship_without_cargo.load_cargo('passengers', 100)
        assert loaded == 0

    def test_ship_instance_load_different_cargo_types(self, ship_with_cargo_capacity):
        """Test loading different cargo types independently."""
        ship_with_cargo_capacity.load_cargo('passengers', 2000)
        ship_with_cargo_capacity.load_cargo('generic', 500)
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 2000
        assert ship_with_cargo_capacity.get_current_cargo('generic') == 500


class TestShipInstanceUnloadCargo:
    """Tests for ShipInstance.unload_cargo()."""

    def test_ship_instance_unload_cargo(self, ship_with_cargo_capacity):
        """Test basic cargo unloading."""
        ship_with_cargo_capacity.load_cargo('passengers', 3000)
        unloaded = ship_with_cargo_capacity.unload_cargo('passengers', 1000)
        assert unloaded == 1000
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 2000

    def test_ship_instance_unload_more_than_current(self, ship_with_cargo_capacity):
        """Test unloading more than current is capped."""
        ship_with_cargo_capacity.load_cargo('passengers', 500)
        unloaded = ship_with_cargo_capacity.unload_cargo('passengers', 1000)
        assert unloaded == 500  # Capped at current
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 0

    def test_ship_instance_unload_empty_cargo(self, ship_with_cargo_capacity):
        """Test unloading from empty cargo returns 0."""
        unloaded = ship_with_cargo_capacity.unload_cargo('passengers', 100)
        assert unloaded == 0

    def test_ship_instance_unload_clears_zero_entry(self, ship_with_cargo_capacity):
        """Test that unloading all cargo removes entry from dict."""
        ship_with_cargo_capacity.load_cargo('passengers', 100)
        ship_with_cargo_capacity.unload_cargo('passengers', 100)
        # Zero entries should be cleaned up
        assert 'passengers' not in ship_with_cargo_capacity.cargo_contents


class TestShipInstanceCargoSpaceAvailable:
    """Tests for ShipInstance.get_cargo_space_available()."""

    def test_cargo_space_available_empty(self, ship_with_cargo_capacity):
        """Test available space when empty."""
        available = ship_with_cargo_capacity.get_cargo_space_available('passengers')
        assert available == 5000

    def test_cargo_space_available_partial(self, ship_with_cargo_capacity):
        """Test available space when partially loaded."""
        ship_with_cargo_capacity.load_cargo('passengers', 3000)
        available = ship_with_cargo_capacity.get_cargo_space_available('passengers')
        assert available == 2000

    def test_cargo_space_available_full(self, ship_with_cargo_capacity):
        """Test available space when full."""
        ship_with_cargo_capacity.load_cargo('passengers', 5000)
        available = ship_with_cargo_capacity.get_cargo_space_available('passengers')
        assert available == 0


class TestShipInstanceCargoSerialization:
    """Tests for cargo serialization roundtrip."""

    def test_ship_instance_cargo_serialization_roundtrip(self, ship_with_cargo_capacity):
        """Test cargo contents survive serialization."""
        ship_with_cargo_capacity.load_cargo('passengers', 2500)
        ship_with_cargo_capacity.load_cargo('generic', 750)

        # Serialize
        data = ship_with_cargo_capacity.to_dict()

        # Verify cargo_contents in serialized data
        assert 'cargo_contents' in data
        assert data['cargo_contents'] == {'passengers': 2500, 'generic': 750}

        # Deserialize
        restored = ShipInstance.from_dict(data)

        # Verify cargo restored
        assert restored.get_current_cargo('passengers') == 2500
        assert restored.get_current_cargo('generic') == 750

    def test_empty_cargo_not_serialized(self, ship_with_cargo_capacity):
        """Test that empty cargo dict is not included in serialization."""
        # No cargo loaded
        data = ship_with_cargo_capacity.to_dict()
        # cargo_contents should be empty dict or not present
        assert data.get('cargo_contents', {}) == {}

    def test_zero_cargo_removed_from_dict(self, ship_with_cargo_capacity):
        """Test that zero-amount cargo entries are removed."""
        ship_with_cargo_capacity.load_cargo('passengers', 100)
        ship_with_cargo_capacity.unload_cargo('passengers', 100)
        assert ship_with_cargo_capacity.cargo_contents == {}


class TestShipInstanceCargoClone:
    """Tests for cargo preservation in clone()."""

    def test_clone_preserves_cargo(self, ship_with_cargo_capacity):
        """Test that clone() deep copies cargo contents."""
        ship_with_cargo_capacity.load_cargo('passengers', 1500)
        clone = ship_with_cargo_capacity.clone()

        # Clone should have same cargo
        assert clone.get_current_cargo('passengers') == 1500

        # Modifying original should not affect clone
        ship_with_cargo_capacity.load_cargo('passengers', 500)
        assert clone.get_current_cargo('passengers') == 1500
        assert ship_with_cargo_capacity.get_current_cargo('passengers') == 2000


# --- Fleet Cargo Tests ---

class TestFleetCargoCapacity:
    """Tests for Fleet.get_fleet_cargo_capacity()."""

    def test_fleet_cargo_capacity_sum(self, fleet_with_cargo_ships):
        """Test fleet cargo capacity sums across all ships."""
        # Ship 1: 5000 passengers, Ship 2: 3000 passengers, Ship 3: 0
        capacity = fleet_with_cargo_ships.get_fleet_cargo_capacity('passengers')
        assert capacity == 8000

    def test_fleet_cargo_capacity_generic(self, fleet_with_cargo_ships):
        """Test fleet generic cargo capacity."""
        # Only Ship 1 has generic: 1000
        capacity = fleet_with_cargo_ships.get_fleet_cargo_capacity('generic')
        assert capacity == 1000

    def test_fleet_cargo_capacity_missing_type(self, fleet_with_cargo_ships):
        """Test fleet cargo capacity for missing type returns 0."""
        capacity = fleet_with_cargo_ships.get_fleet_cargo_capacity('fuel_pods')
        assert capacity == 0


class TestFleetLoadCargo:
    """Tests for Fleet.load_cargo_to_fleet()."""

    def test_fleet_load_distributes_across_ships(self, fleet_with_cargo_ships):
        """Test loading distributes cargo across ships."""
        loaded = fleet_with_cargo_ships.load_cargo_to_fleet('passengers', 6000)
        assert loaded == 6000

        # Should have filled first ship (5000) and put 1000 in second
        ship1 = fleet_with_cargo_ships.ships[0]
        ship2 = fleet_with_cargo_ships.ships[1]
        total = ship1.get_current_cargo('passengers') + ship2.get_current_cargo('passengers')
        assert total == 6000

    def test_fleet_load_caps_at_capacity(self, fleet_with_cargo_ships):
        """Test loading more than fleet capacity is capped."""
        loaded = fleet_with_cargo_ships.load_cargo_to_fleet('passengers', 20000)
        assert loaded == 8000  # Total fleet capacity

    def test_fleet_load_to_empty_fleet(self):
        """Test loading to fleet with no cargo capacity."""
        fleet = Fleet(fleet_id=2, owner_id=0, location=HexCoord(0, 0))
        ship = ShipInstance(
            instance_id="no-cargo",
            design_id="fighter",
            name="Fighter",
            owner_id=0,
            design_data={'expected_stats': {'cargo_storage': {}}},
        )
        fleet.ships.append(ship)
        loaded = fleet.load_cargo_to_fleet('passengers', 100)
        assert loaded == 0


class TestFleetUnloadCargo:
    """Tests for Fleet.unload_cargo_from_fleet()."""

    def test_fleet_unload_from_multiple_ships(self, fleet_with_cargo_ships):
        """Test unloading collects from multiple ships."""
        # Load cargo to multiple ships
        fleet_with_cargo_ships.ships[0].load_cargo('passengers', 3000)
        fleet_with_cargo_ships.ships[1].load_cargo('passengers', 2000)

        # Unload 4000 - should take from both ships
        unloaded = fleet_with_cargo_ships.unload_cargo_from_fleet('passengers', 4000)
        assert unloaded == 4000

        # Verify total remaining
        remaining = fleet_with_cargo_ships.get_fleet_cargo_current('passengers')
        assert remaining == 1000

    def test_fleet_unload_more_than_available(self, fleet_with_cargo_ships):
        """Test unloading more than available is capped."""
        fleet_with_cargo_ships.ships[0].load_cargo('passengers', 1000)
        unloaded = fleet_with_cargo_ships.unload_cargo_from_fleet('passengers', 5000)
        assert unloaded == 1000

    def test_fleet_unload_from_empty(self, fleet_with_cargo_ships):
        """Test unloading from fleet with no cargo."""
        unloaded = fleet_with_cargo_ships.unload_cargo_from_fleet('passengers', 100)
        assert unloaded == 0


class TestFleetCargoCurrent:
    """Tests for Fleet.get_fleet_cargo_current()."""

    def test_fleet_cargo_current_sum(self, fleet_with_cargo_ships):
        """Test fleet current cargo sums across ships."""
        fleet_with_cargo_ships.ships[0].load_cargo('passengers', 1000)
        fleet_with_cargo_ships.ships[1].load_cargo('passengers', 500)

        current = fleet_with_cargo_ships.get_fleet_cargo_current('passengers')
        assert current == 1500

    def test_fleet_cargo_current_empty(self, fleet_with_cargo_ships):
        """Test fleet current cargo when empty."""
        current = fleet_with_cargo_ships.get_fleet_cargo_current('passengers')
        assert current == 0
