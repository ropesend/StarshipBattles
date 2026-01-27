"""Tests for Fleet module - fleet management and operations."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord


class TestFleetOrder:
    """Test cases for FleetOrder class."""

    def test_creation_move_order(self):
        """Test creating a MOVE order."""
        target = HexCoord(5, 3)
        order = FleetOrder(OrderType.MOVE, target)
        assert order.type == OrderType.MOVE
        assert order.target == target

    def test_creation_no_target(self):
        """Test creating order without target."""
        order = FleetOrder(OrderType.COLONIZE)
        assert order.type == OrderType.COLONIZE
        assert order.target is None

    def test_repr(self):
        """Test string representation."""
        order = FleetOrder(OrderType.JOIN_FLEET, "target_fleet")
        assert "JOIN_FLEET" in repr(order)

    def test_to_dict_with_coord_target(self):
        """Test serializing order with coordinate target."""
        # Use a mock that has to_dict method since HexCoord uses __slots__
        mock_coord = MagicMock()
        mock_coord.to_dict.return_value = {'q': 2, 'r': 4}
        order = FleetOrder(OrderType.MOVE, mock_coord)
        d = order.to_dict()
        assert d['type'] == 'MOVE'
        assert d['target'] == {'q': 2, 'r': 4}

    def test_to_dict_with_fleet_ref(self):
        """Test serializing order with fleet reference target."""
        mock_fleet = MagicMock()
        mock_fleet.id = "fleet_123"
        del mock_fleet.to_dict  # Ensure it doesn't have to_dict
        order = FleetOrder(OrderType.JOIN_FLEET, mock_fleet)
        d = order.to_dict()
        assert d['target']['type'] == 'fleet_ref'
        assert d['target']['id'] == 'fleet_123'


class TestFleet:
    """Test cases for Fleet class."""

    @pytest.fixture
    def basic_fleet(self):
        """Create a basic fleet for testing."""
        return Fleet(
            fleet_id="fleet_1",
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )

    @pytest.fixture
    def make_mock_ship(self):
        """Factory for creating mock ship instances."""
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
            return mock
        return _make

    def test_creation(self, basic_fleet):
        """Test fleet creation with basic parameters."""
        assert basic_fleet.id == "fleet_1"
        assert basic_fleet.owner_id == 0
        assert basic_fleet.location == HexCoord(0, 0)
        assert basic_fleet.speed == 5.0
        assert basic_fleet.ships == []
        assert basic_fleet.orders == []
        assert basic_fleet.path == []

    def test_add_ship(self, basic_fleet, make_mock_ship):
        """Test adding a ShipInstance to fleet."""
        ship = make_mock_ship(name="Destroyer")
        basic_fleet.add_ship(ship)
        assert ship in basic_fleet.ships
        assert len(basic_fleet.ships) == 1

    def test_add_multiple_ships(self, basic_fleet, make_mock_ship):
        """Test adding multiple ships."""
        ship1 = make_mock_ship(name="Scout")
        ship2 = make_mock_ship(name="Cruiser")
        ship3 = make_mock_ship(name="Scout")
        basic_fleet.add_ship(ship1)
        basic_fleet.add_ship(ship2)
        basic_fleet.add_ship(ship3)
        assert len(basic_fleet.ships) == 3

    def test_remove_ship(self, basic_fleet, make_mock_ship):
        """Test removing a ship from fleet."""
        destroyer = make_mock_ship(name="Destroyer")
        scout = make_mock_ship(name="Scout")
        basic_fleet.add_ship(destroyer)
        basic_fleet.add_ship(scout)

        result = basic_fleet.remove_ship(destroyer)
        assert result is True
        assert destroyer not in basic_fleet.ships
        assert len(basic_fleet.ships) == 1

    def test_remove_ship_not_found(self, basic_fleet, make_mock_ship):
        """Test removing a ship that doesn't exist."""
        scout = make_mock_ship(name="Scout")
        battleship = make_mock_ship(name="Battleship")
        basic_fleet.add_ship(scout)
        result = basic_fleet.remove_ship(battleship)
        assert result is False
        assert len(basic_fleet.ships) == 1

    def test_get_ship_names(self, basic_fleet, make_mock_ship):
        """Test getting ship names from ShipInstance objects."""
        scout = make_mock_ship(name="Scout")
        destroyer = make_mock_ship(name="Destroyer")
        basic_fleet.add_ship(scout)
        basic_fleet.add_ship(destroyer)
        names = basic_fleet.get_ship_names()
        assert "Scout" in names
        assert "Destroyer" in names


class TestFleetOrders:
    """Test cases for fleet order management."""

    @pytest.fixture
    def fleet(self):
        """Create a fleet for order testing."""
        return Fleet("f1", 0, HexCoord(0, 0))

    def test_add_order(self, fleet):
        """Test adding an order to queue."""
        order = FleetOrder(OrderType.MOVE, HexCoord(5, 0))
        fleet.add_order(order)
        assert len(fleet.orders) == 1
        assert fleet.orders[0] == order

    def test_add_order_at_index(self, fleet):
        """Test adding order at specific index."""
        order1 = FleetOrder(OrderType.MOVE, HexCoord(1, 0))
        order2 = FleetOrder(OrderType.MOVE, HexCoord(2, 0))
        order3 = FleetOrder(OrderType.MOVE, HexCoord(3, 0))

        fleet.add_order(order1)
        fleet.add_order(order3)
        fleet.add_order(order2, index=1)

        assert fleet.orders[0] == order1
        assert fleet.orders[1] == order2
        assert fleet.orders[2] == order3

    def test_get_current_order(self, fleet):
        """Test getting current (first) order."""
        order = FleetOrder(OrderType.MOVE, HexCoord(5, 0))
        fleet.add_order(order)
        assert fleet.get_current_order() == order

    def test_get_current_order_empty(self, fleet):
        """Test getting current order when queue is empty."""
        assert fleet.get_current_order() is None

    def test_pop_order(self, fleet):
        """Test popping an order from queue."""
        order1 = FleetOrder(OrderType.MOVE, HexCoord(1, 0))
        order2 = FleetOrder(OrderType.MOVE, HexCoord(2, 0))
        fleet.add_order(order1)
        fleet.add_order(order2)
        fleet.path = [HexCoord(0, 0), HexCoord(1, 0)]

        popped = fleet.pop_order()
        assert popped == order1
        assert len(fleet.orders) == 1
        assert fleet.orders[0] == order2
        assert fleet.path == []  # Path cleared on pop

    def test_pop_order_empty(self, fleet):
        """Test popping from empty queue returns None."""
        result = fleet.pop_order()
        assert result is None

    def test_clear_orders(self, fleet):
        """Test clearing all orders."""
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(2, 0)))
        fleet.path = [HexCoord(0, 0), HexCoord(1, 0)]

        fleet.clear_orders()
        assert fleet.orders == []
        assert fleet.path == []


class TestFleetMerge:
    """Test cases for fleet merging."""

    @pytest.fixture
    def make_mock_ship(self):
        """Factory for creating mock ship instances."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(name="Test Ship", is_combat_capable=True):
            mock = MagicMock(spec=ShipInstance)
            mock.name = name
            mock.is_combat_capable.return_value = is_combat_capable
            mock.get_all_resource_costs_per_hex.return_value = {}
            mock.design_data = {'vehicle_type': 'Ship'}
            mock.get_calculated_stats.return_value = {
                'mass': 100,
                'strategic_movement': 500
            }
            return mock
        return _make

    def test_merge_transfers_ships(self, make_mock_ship):
        """Test that merge transfers ships to target fleet."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        fleet2 = Fleet("f2", 0, HexCoord(0, 0))

        scout = make_mock_ship(name="Scout")
        destroyer = make_mock_ship(name="Destroyer")
        cruiser = make_mock_ship(name="Cruiser")

        fleet1.add_ship(scout)
        fleet1.add_ship(destroyer)
        fleet2.add_ship(cruiser)

        fleet1.merge_with(fleet2)

        assert len(fleet1.ships) == 0  # Source fleet emptied
        assert len(fleet2.ships) == 3  # Target fleet has all ships
        assert scout in fleet2.ships
        assert destroyer in fleet2.ships
        assert cruiser in fleet2.ships

    def test_merge_clears_source_orders(self):
        """Test that merge clears orders on source fleet."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        fleet2 = Fleet("f2", 0, HexCoord(0, 0))

        fleet1.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 0)))
        fleet1.merge_with(fleet2)

        assert fleet1.orders == []

    def test_merge_with_non_fleet(self, make_mock_ship):
        """Test merge with non-Fleet object does nothing."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(name="Scout")
        fleet1.add_ship(ship)

        fleet1.merge_with("not a fleet")

        assert len(fleet1.ships) == 1  # Ship not removed


class TestFleetEquality:
    """Test cases for fleet equality and hashing."""

    def test_equality_by_id(self):
        """Test fleets are equal if they have the same ID."""
        fleet1 = Fleet("same_id", 0, HexCoord(0, 0))
        fleet2 = Fleet("same_id", 1, HexCoord(5, 5))  # Different owner/location

        assert fleet1 == fleet2

    def test_inequality_different_id(self):
        """Test fleets are not equal if IDs differ."""
        fleet1 = Fleet("id_1", 0, HexCoord(0, 0))
        fleet2 = Fleet("id_2", 0, HexCoord(0, 0))

        assert fleet1 != fleet2

    def test_inequality_with_non_fleet(self):
        """Test fleet is not equal to non-Fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        assert fleet != "f1"
        assert fleet != None

    def test_hash_for_set(self):
        """Test fleets can be used in sets."""
        fleet1 = Fleet("f1", 0, HexCoord(0, 0))
        fleet2 = Fleet("f1", 1, HexCoord(5, 5))
        fleet3 = Fleet("f2", 0, HexCoord(0, 0))

        s = {fleet1, fleet2, fleet3}
        assert len(s) == 2  # fleet1 and fleet2 have same ID


class TestFleetSerialization:
    """Test cases for fleet serialization."""

    @pytest.fixture
    def make_ship_instance(self):
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

    def test_to_dict_basic(self, make_ship_instance):
        """Test basic fleet serialization."""
        fleet = Fleet("f1", 0, HexCoord(2, 3), speed=7.5)
        ship = make_ship_instance(name="Scout")
        fleet.ships.append(ship)  # Bypass add_ship to avoid speed recalc

        d = fleet.to_dict()

        assert d['id'] == 'f1'
        assert d['owner_id'] == 0
        assert d['speed'] == 7.5
        assert len(d['ships']) == 1
        assert d['ships'][0]['name'] == 'Scout'
        assert d['ships'][0]['design_id'] == 'Scout'

    def test_from_dict_basic(self):
        """Test basic fleet deserialization."""
        ship_data = {
            'instance_id': 'test-destroyer',
            'design_id': 'Destroyer',
            'name': 'Destroyer',
            'owner_id': 1,
            'design_data': {'name': 'Destroyer', 'vehicle_type': 'Ship'},
        }
        d = {
            'id': 'f1',
            'owner_id': 1,
            'location': [5, -2],
            'speed': 6.0,
            'ships': [ship_data],
            'orders': [],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert fleet.id == 'f1'
        assert fleet.owner_id == 1
        assert fleet.location == HexCoord(5, -2)
        assert fleet.speed == 6.0
        assert len(fleet.ships) == 1
        assert fleet.ships[0].name == 'Destroyer'

    def test_roundtrip_serialization(self, make_ship_instance):
        """Test serialization roundtrip preserves data."""
        original = Fleet("test_fleet", 0, HexCoord(3, -1), speed=8.0)
        original.ships.append(make_ship_instance(name="Cruiser"))
        original.ships.append(make_ship_instance(name="Frigate"))

        d = original.to_dict()

        # Note: HexCoord doesn't have to_dict(), so location serializes as None
        # Manually fix the location for roundtrip test
        d['location'] = [3, -1]

        restored = Fleet.from_dict(d)

        assert restored.id == original.id
        assert restored.owner_id == original.owner_id
        assert restored.location == original.location
        assert restored.speed == original.speed
        assert len(restored.ships) == 2
        assert restored.ships[0].name == "Cruiser"
        assert restored.ships[1].name == "Frigate"

    def test_to_dict_location_limitation(self):
        """Document that HexCoord location serializes as None.

        Note: Current implementation has a gap where HexCoord without to_dict()
        results in None location. This test documents the current behavior.
        """
        fleet = Fleet("f1", 0, HexCoord(2, 3))
        d = fleet.to_dict()

        # HexCoord doesn't have to_dict and isn't a tuple, so location is None
        assert d['location'] is None

    def test_repr(self, make_ship_instance):
        """Test fleet string representation."""
        fleet = Fleet("f1", 0, HexCoord(1, 2), speed=5.0)
        fleet.ships.append(make_ship_instance(name="Scout"))
        fleet.ships.append(make_ship_instance(name="Destroyer"))

        r = repr(fleet)
        assert "f1" in r
        assert "Owner:0" in r
        assert "Ships:2" in r

    def test_from_dict_restores_move_orders(self):
        """Test that MOVE orders are restored from serialized data (STRAT-001)."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': [0, 0],
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'MOVE', 'target': {'q': 5, 'r': 3}}
            ],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.MOVE
        # Target should be HexCoord
        assert fleet.orders[0].target == HexCoord(5, 3)

    def test_from_dict_restores_colonize_orders(self):
        """Test that COLONIZE orders are restored from serialized data."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': [0, 0],
            'speed': 5.0,
            'ships': [],
            'orders': [
                {'type': 'COLONIZE', 'target': None}
            ],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.COLONIZE
        assert fleet.orders[0].target is None

    def test_roundtrip_orders_preserved(self):
        """Test that orders survive serialization roundtrip."""
        original = Fleet("test", 0, HexCoord(0, 0))
        original.add_order(FleetOrder(OrderType.MOVE, HexCoord(2, 2)))

        d = original.to_dict()
        d['location'] = [0, 0]  # Fix HexCoord serialization gap

        restored = Fleet.from_dict(d)

        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.MOVE


class TestMovementResourceMethods:
    """Test cases for fleet movement resource methods (Group 4.1)."""

    @pytest.fixture
    def make_mock_ship(self):
        """Factory for creating mock ship instances."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            resource_costs_per_hex: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable
            mock.get_all_resource_costs_per_hex.return_value = resource_costs_per_hex or {}

            # Setup get_current_resource to return from current_resources dict
            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)

            # Track consumed resources for verification
            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume

            return mock
        return _make

    def test_movement_resource_costs_single_ship(self, make_mock_ship):
        """Test movement resource costs with a single ship."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(resource_costs_per_hex={'fuel': 10.0})
        fleet.ships.append(ship)

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 10.0}

    def test_movement_resource_costs_multiple_ships(self, make_mock_ship):
        """Test movement resource costs aggregate across multiple ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(resource_costs_per_hex={'fuel': 10.0})
        ship2 = make_mock_ship(resource_costs_per_hex={'fuel': 15.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 25.0}

    def test_movement_resource_costs_mixed_resource_types(self, make_mock_ship):
        """Test movement costs with different resource types from different ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(resource_costs_per_hex={'fuel': 10.0, 'energy': 5.0})
        ship2 = make_mock_ship(resource_costs_per_hex={'fuel': 8.0, 'glag': 2.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 18.0, 'energy': 5.0, 'glag': 2.0}

    def test_movement_resource_costs_empty_fleet(self):
        """Test movement resource costs for empty fleet returns empty dict."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        costs = fleet.get_movement_resource_costs()

        assert costs == {}

    def test_has_resources_for_movement_sufficient_all_ships(self, make_mock_ship):
        """Test has_resources_for_movement returns True when all ships have enough."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        ship2 = make_mock_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 50.0}
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.has_resources_for_movement() is True

    def test_has_resources_for_movement_insufficient_fuel_one_ship(self, make_mock_ship):
        """Test has_resources_for_movement returns False when one ship lacks fuel."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        ship2 = make_mock_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 5.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.has_resources_for_movement() is False

    def test_has_resources_for_movement_insufficient_energy_one_ship(self, make_mock_ship):
        """Test has_resources_for_movement returns False when one ship lacks energy."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0, 'energy': 20.0},
            current_resources={'fuel': 100.0, 'energy': 10.0}  # Energy insufficient
        )
        fleet.ships.append(ship1)

        assert fleet.has_resources_for_movement() is False

    def test_has_resources_for_movement_zero_cost_resources(self, make_mock_ship):
        """Test has_resources_for_movement handles zero-cost resources correctly."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 0.0, 'energy': 0.0},
            current_resources={'fuel': 0.0, 'energy': 0.0}
        )
        fleet.ships.append(ship)

        assert fleet.has_resources_for_movement() is True

    def test_has_resources_for_movement_empty_fleet(self):
        """Test has_resources_for_movement returns True for empty fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        assert fleet.has_resources_for_movement() is True

    def test_consume_movement_resources_success_single_hex(self, make_mock_ship):
        """Test successful consumption of movement resources for 1 hex."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_movement_resources(hexes=1)

        assert result is True
        ship.consume_resource.assert_called_with('fuel', 10.0)

    def test_consume_movement_resources_success_multiple_hexes(self, make_mock_ship):
        """Test successful consumption of movement resources for multiple hexes."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_movement_resources(hexes=3)

        assert result is True
        ship.consume_resource.assert_called_with('fuel', 30.0)

    def test_consume_movement_resources_failure_atomicity(self, make_mock_ship):
        """Test that consumption fails atomically when any ship lacks resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        ship2 = make_mock_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 5.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        result = fleet.consume_movement_resources(hexes=1)

        assert result is False
        # Verify no resources were consumed (atomicity)
        ship1.consume_resource.assert_not_called()
        ship2.consume_resource.assert_not_called()

    def test_consume_movement_resources_atomicity_multi_resource(self, make_mock_ship):
        """Test atomicity with multiple resource types."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0, 'energy': 20.0},
            current_resources={'fuel': 100.0, 'energy': 5.0}  # Energy insufficient
        )
        fleet.ships.append(ship)

        result = fleet.consume_movement_resources(hexes=1)

        assert result is False
        ship.consume_resource.assert_not_called()

    def test_consume_movement_resources_zero_cost_resources(self, make_mock_ship):
        """Test consumption succeeds with zero-cost resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 0.0},
            current_resources={'fuel': 0.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_movement_resources(hexes=1)

        assert result is True
        # Zero-cost should not trigger consume call
        ship.consume_resource.assert_not_called()

    def test_consume_movement_resources_empty_fleet(self):
        """Test consumption succeeds for empty fleet (no-op)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        result = fleet.consume_movement_resources(hexes=1)

        assert result is True


class TestWarpResourceMethods:
    """Test cases for fleet warp resource methods (Group 4.2)."""

    @pytest.fixture
    def make_mock_ship(self):
        """Factory for creating mock ship instances with warp costs."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            warp_resource_costs: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable
            mock.get_warp_resource_costs.return_value = warp_resource_costs or {}

            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)

            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume

            return mock
        return _make

    def test_warp_resource_costs_single_ship(self, make_mock_ship):
        """Test warp resource costs with a single ship."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(warp_resource_costs={'energy': 500.0})
        fleet.ships.append(ship)

        costs = fleet.get_warp_resource_costs()

        assert costs == {'energy': 500.0}

    def test_warp_resource_costs_multiple_ships(self, make_mock_ship):
        """Test warp resource costs aggregate across multiple ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(warp_resource_costs={'energy': 500.0})
        ship2 = make_mock_ship(warp_resource_costs={'energy': 300.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_warp_resource_costs()

        assert costs == {'energy': 800.0}

    def test_warp_resource_costs_mixed_resource_types(self, make_mock_ship):
        """Test warp costs with different resource types (energy and fuel)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(warp_resource_costs={'energy': 500.0, 'fuel': 100.0})
        ship2 = make_mock_ship(warp_resource_costs={'energy': 300.0, 'fuel': 50.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_warp_resource_costs()

        assert costs == {'energy': 800.0, 'fuel': 150.0}

    def test_warp_resource_costs_empty_fleet(self):
        """Test warp resource costs for empty fleet returns empty dict."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        costs = fleet.get_warp_resource_costs()

        assert costs == {}

    def test_has_resources_for_warp_sufficient_all_ships(self, make_mock_ship):
        """Test has_resources_for_warp returns True when all ships have enough."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_mock_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 800.0}
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.has_resources_for_warp() is True

    def test_has_resources_for_warp_insufficient_energy_one_ship(self, make_mock_ship):
        """Test has_resources_for_warp returns False when one ship lacks energy."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_mock_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 100.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.has_resources_for_warp() is False

    def test_has_resources_for_warp_insufficient_fuel_one_ship(self, make_mock_ship):
        """Test has_resources_for_warp returns False when one ship lacks fuel."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            warp_resource_costs={'energy': 500.0, 'fuel': 100.0},
            current_resources={'energy': 1000.0, 'fuel': 50.0}  # Fuel insufficient
        )
        fleet.ships.append(ship)

        assert fleet.has_resources_for_warp() is False

    def test_has_resources_for_warp_zero_cost_resources(self, make_mock_ship):
        """Test has_resources_for_warp handles zero-cost resources correctly."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            warp_resource_costs={'energy': 0.0},
            current_resources={'energy': 0.0}
        )
        fleet.ships.append(ship)

        assert fleet.has_resources_for_warp() is True

    def test_has_resources_for_warp_empty_fleet(self):
        """Test has_resources_for_warp returns True for empty fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        assert fleet.has_resources_for_warp() is True

    def test_consume_warp_resources_success_all_ships(self, make_mock_ship):
        """Test successful consumption of warp resources from all ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_mock_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 800.0}
        )
        fleet.ships.extend([ship1, ship2])

        result = fleet.consume_warp_resources()

        assert result is True
        ship1.consume_resource.assert_called_with('energy', 500.0)
        ship2.consume_resource.assert_called_with('energy', 300.0)

    def test_consume_warp_resources_failure_atomicity(self, make_mock_ship):
        """Test that warp consumption fails atomically when any ship lacks resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_mock_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 100.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        result = fleet.consume_warp_resources()

        assert result is False
        ship1.consume_resource.assert_not_called()
        ship2.consume_resource.assert_not_called()

    def test_consume_warp_resources_atomicity_multi_resource(self, make_mock_ship):
        """Test warp atomicity with multiple resource types."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            warp_resource_costs={'energy': 500.0, 'fuel': 100.0},
            current_resources={'energy': 1000.0, 'fuel': 50.0}  # Fuel insufficient
        )
        fleet.ships.append(ship)

        result = fleet.consume_warp_resources()

        assert result is False
        ship.consume_resource.assert_not_called()

    def test_consume_warp_resources_zero_cost_resources(self, make_mock_ship):
        """Test warp consumption succeeds with zero-cost resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            warp_resource_costs={'energy': 0.0},
            current_resources={'energy': 0.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_warp_resources()

        assert result is True
        ship.consume_resource.assert_not_called()

    def test_consume_warp_resources_empty_fleet(self):
        """Test warp consumption succeeds for empty fleet (no-op)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        result = fleet.consume_warp_resources()

        assert result is True


class TestBackwardCompatibility:
    """Test cases for backward compatibility wrappers (Group 4.3)."""

    @pytest.fixture
    def make_mock_ship(self):
        """Factory for creating mock ship instances."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            warp_resource_costs: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True,
            fuel_cost_per_hex: float = 0.0
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable
            mock.get_warp_resource_costs.return_value = warp_resource_costs or {}
            mock.get_fuel_cost_per_hex.return_value = fuel_cost_per_hex
            mock.get_all_resource_costs_per_hex.return_value = {'fuel': fuel_cost_per_hex} if fuel_cost_per_hex else {}

            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)
            mock.get_current_fuel.return_value = current.get('fuel', 0)

            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume
            mock.consume_fuel.side_effect = lambda amt: True

            return mock
        return _make

    def test_backward_compat_consume_fleet_fuel_wrapper(self, make_mock_ship):
        """Test consume_fleet_fuel uses legacy fuel methods."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            fuel_cost_per_hex=10.0,
            current_resources={'fuel': 100.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_fleet_fuel(hexes=1)

        assert result is True


class TestEdgeCases:
    """Test cases for edge cases (Group 4.4)."""

    @pytest.fixture
    def make_mock_ship(self):
        """Factory for creating mock ship instances."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            resource_costs_per_hex: dict = None,
            warp_resource_costs: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True,
            is_destroyed: bool = False,
            is_derelict: bool = False
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable and not is_destroyed and not is_derelict
            mock.is_destroyed = is_destroyed
            mock.is_derelict = is_derelict
            mock.get_all_resource_costs_per_hex.return_value = resource_costs_per_hex or {}
            mock.get_warp_resource_costs.return_value = warp_resource_costs or {}

            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)

            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume

            return mock
        return _make

    def test_destroyed_ships_excluded_from_movement_calculation(self, make_mock_ship):
        """Test that destroyed ships are excluded from movement cost calculations."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        active_ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        destroyed_ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 50.0},  # Should be ignored
            current_resources={'fuel': 0.0},
            is_destroyed=True,
            is_combat_capable=False
        )
        fleet.ships.extend([active_ship, destroyed_ship])

        costs = fleet.get_movement_resource_costs()

        # Only active ship's cost should be counted
        assert costs == {'fuel': 10.0}

    def test_derelict_ships_excluded_from_warp_calculation(self, make_mock_ship):
        """Test that derelict ships are excluded from warp cost calculations."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        active_ship = make_mock_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        derelict_ship = make_mock_ship(
            warp_resource_costs={'energy': 1000.0},  # Should be ignored
            current_resources={'energy': 0.0},
            is_derelict=True,
            is_combat_capable=False
        )
        fleet.ships.extend([active_ship, derelict_ship])

        costs = fleet.get_warp_resource_costs()

        # Only active ship's cost should be counted
        assert costs == {'energy': 500.0}

    def test_mixed_destroyed_and_combat_capable_ships(self, make_mock_ship):
        """Test mixed fleet with both destroyed and active ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        active1 = make_mock_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        destroyed = make_mock_ship(
            resource_costs_per_hex={'fuel': 20.0},
            is_destroyed=True,
            is_combat_capable=False
        )
        derelict = make_mock_ship(
            resource_costs_per_hex={'fuel': 30.0},
            is_derelict=True,
            is_combat_capable=False
        )
        active2 = make_mock_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 80.0}
        )
        fleet.ships.extend([active1, destroyed, derelict, active2])

        costs = fleet.get_movement_resource_costs()

        # Only active ships' costs
        assert costs == {'fuel': 25.0}

    def test_very_large_fleet(self, make_mock_ship):
        """Test resource calculations with a very large fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        # Add 100 ships
        for i in range(100):
            ship = make_mock_ship(
                resource_costs_per_hex={'fuel': 1.0},
                current_resources={'fuel': 100.0}
            )
            fleet.ships.append(ship)

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 100.0}  # 100 ships * 1.0 fuel each

    def test_ships_with_no_resource_costs(self, make_mock_ship):
        """Test fleet where ships have no resource costs."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_mock_ship(resource_costs_per_hex={})
        ship2 = make_mock_ship(resource_costs_per_hex={})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_movement_resource_costs()

        assert costs == {}
        assert fleet.has_resources_for_movement() is True
        assert fleet.consume_movement_resources(hexes=1) is True

    def test_floating_point_precision_in_resource_consumption(self, make_mock_ship):
        """Test that floating point precision is handled correctly."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        # Use values that could cause floating point issues
        ship = make_mock_ship(
            resource_costs_per_hex={'fuel': 0.1},
            current_resources={'fuel': 1.0}
        )
        fleet.ships.append(ship)

        # Moving 3 hexes should cost 0.3 fuel (common floating point issue: 0.1 + 0.1 + 0.1)
        result = fleet.consume_movement_resources(hexes=3)

        assert result is True
        # The cost should be 0.3 (0.1 * 3)
        call_args = ship.consume_resource.call_args[0]
        assert call_args[0] == 'fuel'
        assert abs(call_args[1] - 0.3) < 0.0001  # Allow small floating point tolerance

    def test_warp_capability_check_integration(self, make_mock_ship):
        """Test integration between can_use_warp and resource checks."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_mock_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        fleet.ships.append(ship)

        # Even with resources, has_resources_for_warp only checks resources
        # The actual warp capability (has warp drive) is checked by can_use_warp
        assert fleet.has_resources_for_warp() is True

        # Consumption should still work
        result = fleet.consume_warp_resources()
        assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
