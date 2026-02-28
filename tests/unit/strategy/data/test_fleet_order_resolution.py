"""Tests for fleet order reference resolution after deserialization.

PROJ-207 Phase 1: ODM-001 - Fix _fleet_ref/_planet_ref Resolution After Deserialization

When fleets are serialized and deserialized, order targets that reference other
game objects (Fleet, Planet) are stored as marker dicts (_fleet_ref, _planet_ref).
These must be resolved back to actual objects after loading.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.empire import Empire
from game.core.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy with planet lookup."""
    galaxy = MagicMock()
    galaxy._planets = {}  # For tracking registered planets

    def get_planet_by_id(planet_id):
        return galaxy._planets.get(planet_id)

    galaxy.get_planet_by_id = get_planet_by_id
    return galaxy


@pytest.fixture
def mock_planet():
    """Create a mock planet."""
    from game.strategy.data.planet import Planet
    planet = MagicMock(spec=Planet)
    planet.id = 42
    planet.name = "Colonize Target"
    planet.location = HexCoord(5, 5)
    planet.owner_id = None
    return planet


@pytest.fixture
def empires_with_fleets():
    """Create empires with fleets for resolution testing."""
    empire0 = Empire(0, "Player", (255, 0, 0))
    empire1 = Empire(1, "Enemy", (0, 0, 255))

    # Create fleets
    fleet_a = Fleet("fleet_a", 0, HexCoord(0, 0))
    fleet_b = Fleet("fleet_b", 0, HexCoord(5, 5))
    fleet_c = Fleet("fleet_c", 1, HexCoord(10, 10))

    empire0.add_fleet(fleet_a)
    empire0.add_fleet(fleet_b)
    empire1.add_fleet(fleet_c)

    return [empire0, empire1]


# =============================================================================
# Test: MOVE_TO_FLEET Order Resolution
# =============================================================================

class TestMoveToFleetResolution:
    """Tests for resolving _fleet_ref markers to actual Fleet objects."""

    def test_fleet_ref_resolved_to_fleet_object(self, empires_with_fleets, mock_galaxy):
        """After resolution, MOVE_TO_FLEET target is a Fleet object, not a dict."""
        # Create a fleet with a MOVE_TO_FLEET order targeting fleet_b via _fleet_ref
        fleet_data = {
            'id': 'fleet_a',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'MOVE_TO_FLEET', 'target': {'type': 'fleet_ref', 'id': 'fleet_b'}}
            ],
            'path': [],
            'construction_queue': [],
        }

        # Deserialize
        fleet = Fleet.from_dict(fleet_data)

        # Before resolution: target is a dict marker
        assert fleet.orders[0].target == {'_fleet_ref': 'fleet_b'}

        # Resolve references
        fleet.resolve_order_references(mock_galaxy, empires_with_fleets)

        # After resolution: target should be the actual Fleet object
        assert isinstance(fleet.orders[0].target, Fleet)
        assert fleet.orders[0].target.id == 'fleet_b'

    def test_fleet_ref_not_found_removes_order(self, empires_with_fleets, mock_galaxy, caplog):
        """If referenced fleet no longer exists, order is removed with warning."""
        fleet_data = {
            'id': 'fleet_a',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'MOVE_TO_FLEET', 'target': {'type': 'fleet_ref', 'id': 'nonexistent_fleet'}}
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        assert len(fleet.orders) == 1

        # Resolve - should remove the order since fleet doesn't exist
        fleet.resolve_order_references(mock_galaxy, empires_with_fleets)

        # Order should be removed
        assert len(fleet.orders) == 0
        assert "nonexistent_fleet" in caplog.text or len(caplog.records) > 0

    def test_join_fleet_ref_resolved(self, empires_with_fleets, mock_galaxy):
        """JOIN_FLEET orders with _fleet_ref are also resolved."""
        fleet_data = {
            'id': 'fleet_a',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'JOIN_FLEET', 'target': {'type': 'fleet_ref', 'id': 'fleet_c'}}
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        fleet.resolve_order_references(mock_galaxy, empires_with_fleets)

        # Should resolve to enemy fleet (fleet_c)
        assert isinstance(fleet.orders[0].target, Fleet)
        assert fleet.orders[0].target.id == 'fleet_c'


# =============================================================================
# Test: Planet Reference Resolution
# =============================================================================

class TestPlanetRefResolution:
    """Tests for resolving _planet_ref markers to actual Planet objects."""

    def test_planet_ref_resolved_to_planet_object(self, mock_galaxy, mock_planet):
        """After resolution, COLONIZE target with _planet_ref is a Planet object."""
        # Register the planet in the mock galaxy
        mock_galaxy._planets[42] = mock_planet

        fleet_data = {
            'id': 'colonizer',
            'owner_id': 0,
            'location': {'q': 5, 'r': 5},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'COLONIZE', 'target': {'type': 'planet_ref', 'id': 42}}
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)

        # Before resolution: target is a dict marker
        assert fleet.orders[0].target == {'_planet_ref': 42}

        # Resolve references
        fleet.resolve_order_references(mock_galaxy, [])

        # After resolution: target should be the actual Planet object
        assert fleet.orders[0].target is mock_planet
        assert fleet.orders[0].target.id == 42

    def test_planet_ref_not_found_removes_order(self, mock_galaxy, caplog):
        """If referenced planet no longer exists, order is removed with warning."""
        # Planet 999 is not registered
        fleet_data = {
            'id': 'colonizer',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'COLONIZE', 'target': {'type': 'planet_ref', 'id': 999}}
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        assert len(fleet.orders) == 1

        fleet.resolve_order_references(mock_galaxy, [])

        # Order should be removed
        assert len(fleet.orders) == 0

    def test_implode_planet_ref_resolved(self, mock_galaxy, mock_planet):
        """IMPLODE_PLANET orders with _planet_ref are also resolved."""
        mock_galaxy._planets[42] = mock_planet

        fleet_data = {
            'id': 'destroyer',
            'owner_id': 0,
            'location': {'q': 5, 'r': 5},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'IMPLODE_PLANET', 'target': {'type': 'planet_ref', 'id': 42}}
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        fleet.resolve_order_references(mock_galaxy, [])

        assert fleet.orders[0].target is mock_planet


# =============================================================================
# Test: Mixed Order Queue Resolution
# =============================================================================

class TestMixedOrderResolution:
    """Tests for resolving order queues with multiple order types."""

    def test_mixed_queue_resolves_correctly(self, empires_with_fleets, mock_galaxy, mock_planet):
        """Order queue with mixed types resolves all refs correctly."""
        mock_galaxy._planets[42] = mock_planet

        fleet_data = {
            'id': 'multi_mission',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                # MOVE order - no resolution needed
                {'type': 'MOVE', 'target': {'q': 1, 'r': 1}},
                # MOVE_TO_FLEET - needs fleet resolution
                {'type': 'MOVE_TO_FLEET', 'target': {'type': 'fleet_ref', 'id': 'fleet_b'}},
                # COLONIZE - needs planet resolution
                {'type': 'COLONIZE', 'target': {'type': 'planet_ref', 'id': 42}},
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        fleet.resolve_order_references(mock_galaxy, empires_with_fleets)

        # Verify all orders resolved correctly
        assert len(fleet.orders) == 3

        # Order 0: MOVE - target is HexCoord
        assert fleet.orders[0].type == OrderType.MOVE
        assert isinstance(fleet.orders[0].target, HexCoord)
        assert fleet.orders[0].target == HexCoord(1, 1)

        # Order 1: MOVE_TO_FLEET - target is Fleet
        assert fleet.orders[1].type == OrderType.MOVE_TO_FLEET
        assert isinstance(fleet.orders[1].target, Fleet)
        assert fleet.orders[1].target.id == 'fleet_b'

        # Order 2: COLONIZE - target is Planet
        assert fleet.orders[2].type == OrderType.COLONIZE
        assert fleet.orders[2].target is mock_planet

    def test_partial_resolution_removes_only_invalid(self, empires_with_fleets, mock_galaxy, mock_planet):
        """If some refs are invalid, only those orders are removed."""
        mock_galaxy._planets[42] = mock_planet

        fleet_data = {
            'id': 'partial',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                # Valid fleet ref
                {'type': 'MOVE_TO_FLEET', 'target': {'type': 'fleet_ref', 'id': 'fleet_b'}},
                # Invalid fleet ref - should be removed
                {'type': 'JOIN_FLEET', 'target': {'type': 'fleet_ref', 'id': 'deleted_fleet'}},
                # Valid planet ref
                {'type': 'COLONIZE', 'target': {'type': 'planet_ref', 'id': 42}},
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        fleet.resolve_order_references(mock_galaxy, empires_with_fleets)

        # Only 2 orders should remain (invalid JOIN_FLEET removed)
        assert len(fleet.orders) == 2
        assert fleet.orders[0].type == OrderType.MOVE_TO_FLEET
        assert fleet.orders[1].type == OrderType.COLONIZE


# =============================================================================
# Test: Orders Without Refs Are Unchanged
# =============================================================================

# =============================================================================
# Test: FleetOrder Serialization Round-Trip (Task 1.2)
# =============================================================================

class TestFleetOrderSerialization:
    """Tests for FleetOrder to_dict serialization with Planet targets."""

    def test_colonize_order_serializes_planet_as_planet_ref(self):
        """COLONIZE order serializes Planet target as _planet_ref, not full dict."""
        from game.strategy.data.planet import Planet
        planet = MagicMock(spec=Planet)
        planet.id = 42
        planet.name = "Colonize Target"

        order = FleetOrder(OrderType.COLONIZE, planet)
        data = order.to_dict()

        # Should serialize as planet_ref, not full planet dict
        assert data['target']['type'] == 'planet_ref'
        assert data['target']['id'] == 42

    def test_colonize_order_round_trip_with_resolution(self, mock_galaxy, mock_planet):
        """COLONIZE order round-trips correctly with resolution."""
        from game.strategy.data.planet import Planet
        planet = MagicMock(spec=Planet)
        planet.id = 42

        # Serialize
        order = FleetOrder(OrderType.COLONIZE, planet)
        data = order.to_dict()

        # Deserialize via Fleet.from_dict
        mock_galaxy._planets[42] = mock_planet
        fleet_data = {
            'id': 'test',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [data],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        fleet.resolve_order_references(mock_galaxy, [])

        # Target should be resolved to the Planet object
        assert fleet.orders[0].target is mock_planet
        assert fleet.orders[0].target.id == 42


class TestOrdersWithoutRefs:
    """Tests that orders without refs are not modified."""

    def test_move_order_unchanged(self, mock_galaxy):
        """MOVE order with HexCoord target is unchanged by resolution."""
        fleet_data = {
            'id': 'mover',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'MOVE', 'target': {'q': 5, 'r': 3}},
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        original_target = fleet.orders[0].target

        fleet.resolve_order_references(mock_galaxy, [])

        assert fleet.orders[0].target == original_target
        assert fleet.orders[0].target == HexCoord(5, 3)

    def test_build_order_unchanged(self, mock_galaxy):
        """BUILD order with None target is unchanged."""
        fleet_data = {
            'id': 'builder',
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'BUILD', 'target': None},
            ],
            'path': [],
            'construction_queue': [],
        }

        fleet = Fleet.from_dict(fleet_data)
        fleet.resolve_order_references(mock_galaxy, [])

        assert fleet.orders[0].type == OrderType.BUILD
        assert fleet.orders[0].target is None
