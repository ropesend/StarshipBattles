"""Tests for Fleet DTOs."""
import pytest
from dataclasses import FrozenInstanceError
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType


class TestFleetOrderInfo:
    """Tests for FleetOrderInfo frozen dataclass."""

    def test_create_move_order(self):
        """FleetOrderInfo can represent a MOVE order."""
        from game.strategy.facade.dto.fleet_dto import FleetOrderInfo

        order = FleetOrderInfo(
            order_type="MOVE",
            target_description="(5, 3)",
            target_hex=HexCoord(5, 3),
        )

        assert order.order_type == "MOVE"
        assert order.target_description == "(5, 3)"
        assert order.target_hex == HexCoord(5, 3)
        assert order.target_id is None

    def test_create_colonize_order(self):
        """FleetOrderInfo can represent a COLONIZE order."""
        from game.strategy.facade.dto.fleet_dto import FleetOrderInfo

        order = FleetOrderInfo(
            order_type="COLONIZE",
            target_description="Earth",
            target_hex=HexCoord(0, 0),
        )

        assert order.order_type == "COLONIZE"
        assert order.target_description == "Earth"

    def test_create_join_fleet_order(self):
        """FleetOrderInfo can represent a JOIN_FLEET order."""
        from game.strategy.facade.dto.fleet_dto import FleetOrderInfo

        order = FleetOrderInfo(
            order_type="JOIN_FLEET",
            target_description="Fleet Alpha",
            target_id=42,
        )

        assert order.order_type == "JOIN_FLEET"
        assert order.target_id == 42
        assert order.target_hex is None

    def test_is_frozen(self):
        """FleetOrderInfo is immutable (frozen)."""
        from game.strategy.facade.dto.fleet_dto import FleetOrderInfo

        order = FleetOrderInfo(
            order_type="MOVE",
            target_description="(1, 1)",
        )

        with pytest.raises(FrozenInstanceError):
            order.order_type = "COLONIZE"


class TestShipInfo:
    """Tests for ShipInfo frozen dataclass."""

    def test_create_ship_info(self):
        """ShipInfo stores ship data correctly."""
        from game.strategy.facade.dto.fleet_dto import ShipInfo

        ship = ShipInfo(
            instance_id="ship-001",
            name="Enterprise",
            design_id="cruiser",
            ship_class="Cruiser",
            is_combat_capable=True,
            current_hp_percent=0.75,
        )

        assert ship.instance_id == "ship-001"
        assert ship.name == "Enterprise"
        assert ship.design_id == "cruiser"
        assert ship.ship_class == "Cruiser"
        assert ship.is_combat_capable is True
        assert ship.current_hp_percent == 0.75

    def test_is_frozen(self):
        """ShipInfo is immutable (frozen)."""
        from game.strategy.facade.dto.fleet_dto import ShipInfo

        ship = ShipInfo(
            instance_id="ship-001",
            name="Enterprise",
            design_id="cruiser",
            ship_class="Cruiser",
            is_combat_capable=True,
            current_hp_percent=1.0,
        )

        with pytest.raises(FrozenInstanceError):
            ship.name = "Voyager"


class TestFleetInfo:
    """Tests for FleetInfo frozen dataclass."""

    def test_create_basic_fleet_info(self):
        """FleetInfo stores fleet data correctly."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo

        fleet = FleetInfo(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(10, 5),
            speed=5.0,
            ship_count=3,
        )

        assert fleet.fleet_id == 1
        assert fleet.owner_id == 0
        assert fleet.location == HexCoord(10, 5)
        assert fleet.speed == 5.0
        assert fleet.ship_count == 3
        assert fleet.ships == ()
        assert fleet.orders == ()
        assert fleet.has_orders is False
        assert fleet.can_use_warp is False
        assert fleet.projected_path == ()

    def test_create_fleet_with_ships_and_orders(self):
        """FleetInfo can include ships and orders."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo, ShipInfo, FleetOrderInfo

        ships = (
            ShipInfo("s1", "Ship A", "design1", "Frigate", True, 1.0),
            ShipInfo("s2", "Ship B", "design2", "Cruiser", True, 0.8),
        )
        orders = (
            FleetOrderInfo("MOVE", "(5, 3)", HexCoord(5, 3)),
        )
        path = (HexCoord(10, 5), HexCoord(8, 4), HexCoord(6, 4), HexCoord(5, 3))

        fleet = FleetInfo(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(10, 5),
            speed=5.0,
            ship_count=2,
            ships=ships,
            orders=orders,
            has_orders=True,
            can_use_warp=True,
            projected_path=path,
        )

        assert fleet.ship_count == 2
        assert len(fleet.ships) == 2
        assert fleet.ships[0].name == "Ship A"
        assert len(fleet.orders) == 1
        assert fleet.has_orders is True
        assert fleet.can_use_warp is True
        assert len(fleet.projected_path) == 4

    def test_is_frozen(self):
        """FleetInfo is immutable (frozen)."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo

        fleet = FleetInfo(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(10, 5),
            speed=5.0,
            ship_count=3,
        )

        with pytest.raises(FrozenInstanceError):
            fleet.fleet_id = 2

    def test_collection_fields_are_immutable_tuples(self):
        """FleetInfo collection fields (ships, orders, projected_path) are immutable tuples."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo, ShipInfo, FleetOrderInfo

        ships = (
            ShipInfo("s1", "Ship A", "design1", "Frigate", True, 1.0),
        )
        orders = (
            FleetOrderInfo("MOVE", "(5, 3)", HexCoord(5, 3)),
        )
        path = (HexCoord(10, 5), HexCoord(8, 4), HexCoord(5, 3))

        fleet = FleetInfo(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(10, 5),
            speed=5.0,
            ship_count=1,
            ships=ships,
            orders=orders,
            has_orders=True,
            projected_path=path,
        )

        # Verify fields are tuples, not lists
        assert isinstance(fleet.ships, tuple), "ships should be a tuple for immutability"
        assert isinstance(fleet.orders, tuple), "orders should be a tuple for immutability"
        assert isinstance(fleet.projected_path, tuple), "projected_path should be a tuple for immutability"

        # Verify they cannot be mutated (tuples don't have append)
        with pytest.raises(AttributeError):
            fleet.ships.append(ShipInfo("s2", "Ship B", "design2", "Cruiser", True, 1.0))
        with pytest.raises(AttributeError):
            fleet.orders.append(FleetOrderInfo("COLONIZE", "Planet", HexCoord(0, 0)))
        with pytest.raises(AttributeError):
            fleet.projected_path.append(HexCoord(0, 0))

    def test_from_fleet_returns_tuples(self):
        """FleetInfo.from_fleet returns tuples for collection fields."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo
        from game.strategy.data.ship_instance import ShipInstance

        fleet = Fleet(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0,
        )

        # Add a ship
        ship = ShipInstance(
            instance_id="test-ship",
            design_id="test_design",
            name="Test Ship",
            owner_id=0,
            design_data={"name": "Test Ship", "ship_class": "Frigate", "layers": {}},
        )
        fleet.ships.append(ship)

        # Add an order and path
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 5)))
        fleet.path = [HexCoord(0, 0), HexCoord(2, 2), HexCoord(5, 5)]

        # Convert via factory method
        info = FleetInfo.from_fleet(fleet)

        # Verify all collection fields are tuples
        assert isinstance(info.ships, tuple), "ships should be tuple from from_fleet"
        assert isinstance(info.orders, tuple), "orders should be tuple from from_fleet"
        assert isinstance(info.projected_path, tuple), "projected_path should be tuple from from_fleet"

        # Verify content is preserved
        assert len(info.ships) == 1
        assert len(info.orders) == 1
        assert len(info.projected_path) == 3


class TestFleetInfoFactory:
    """Tests for FleetInfo.from_fleet factory method."""

    def test_from_fleet_basic(self):
        """from_fleet creates DTO from basic Fleet."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo

        fleet = Fleet(
            fleet_id=42,
            owner_id=1,
            location=HexCoord(3, 7),
            speed=4.5,
        )

        info = FleetInfo.from_fleet(fleet)

        assert info.fleet_id == 42
        assert info.owner_id == 1
        assert info.location == HexCoord(3, 7)
        assert info.speed == 4.5
        assert info.ship_count == 0
        assert info.ships == ()
        assert info.orders == ()
        assert info.has_orders is False

    def test_from_fleet_with_ships(self):
        """from_fleet includes ship information."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo
        from game.strategy.data.ship_instance import ShipInstance

        fleet = Fleet(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0,
        )

        # Create a ship instance with minimal design data
        ship = ShipInstance(
            instance_id="test-ship-001",
            design_id="test_design",
            name="Test Cruiser",
            owner_id=0,
            design_data={
                "name": "Test Cruiser",
                "ship_class": "Cruiser",
                "layers": {},
            },
        )
        fleet.ships.append(ship)

        info = FleetInfo.from_fleet(fleet)

        assert info.ship_count == 1
        assert len(info.ships) == 1
        assert info.ships[0].instance_id == "test-ship-001"
        assert info.ships[0].name == "Test Cruiser"
        assert info.ships[0].is_combat_capable is True  # Not destroyed/derelict
        assert info.ships[0].current_hp_percent == 1.0  # No damage

    def test_from_fleet_with_damaged_ship(self):
        """from_fleet correctly reports damaged ship HP."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo
        from game.strategy.data.ship_instance import ShipInstance

        fleet = Fleet(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0,
        )

        ship = ShipInstance(
            instance_id="damaged-ship",
            design_id="test_design",
            name="Damaged Ship",
            owner_id=0,
            design_data={
                "name": "Damaged Ship",
                "ship_class": "Frigate",
                "layers": {},
            },
            current_hp=50,  # Damaged
        )
        # Mock the calculated stats to return max_hp
        ship._cached_stats = {"max_hp": 100}
        fleet.ships.append(ship)

        info = FleetInfo.from_fleet(fleet)

        assert info.ships[0].current_hp_percent == 0.5

    def test_from_fleet_with_orders(self):
        """from_fleet includes order information."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo

        fleet = Fleet(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0,
        )
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 5)))
        fleet.path = [HexCoord(0, 0), HexCoord(2, 2), HexCoord(5, 5)]

        info = FleetInfo.from_fleet(fleet)

        assert info.has_orders is True
        assert len(info.orders) == 1
        assert info.orders[0].order_type == "MOVE"
        assert info.orders[0].target_hex == HexCoord(5, 5)
        assert info.projected_path == (HexCoord(0, 0), HexCoord(2, 2), HexCoord(5, 5))

    def test_from_fleet_with_join_fleet_order(self):
        """from_fleet handles JOIN_FLEET order with fleet target."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo

        target_fleet = Fleet(
            fleet_id=99,
            owner_id=0,
            location=HexCoord(10, 10),
        )

        fleet = Fleet(
            fleet_id=1,
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0,
        )
        fleet.add_order(FleetOrder(OrderType.JOIN_FLEET, target_fleet))

        info = FleetInfo.from_fleet(fleet)

        assert len(info.orders) == 1
        assert info.orders[0].order_type == "JOIN_FLEET"
        assert info.orders[0].target_id == 99  # Fleet ID
