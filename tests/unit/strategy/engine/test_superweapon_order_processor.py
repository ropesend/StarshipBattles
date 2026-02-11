"""
Tests for SuperweaponOrderProcessor.

PROJ-102 Phase 6: Tests for turn execution of superweapon orders.
"""
import pytest
from unittest.mock import MagicMock, patch
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint
from game.strategy.data.stars import Star, StarType


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy with systems."""
    galaxy = MagicMock(spec=Galaxy)
    galaxy.systems = {}
    galaxy.name_map = {}
    galaxy.planets_by_id = {}
    galaxy._planet_to_system = {}
    galaxy._global_hex_planets = {}
    return galaxy


@pytest.fixture
def mock_system():
    """Create a mock star system."""
    system = MagicMock(spec=StarSystem)
    system.name = "Alpha Centauri"
    system.global_location = HexCoord(10, 10)
    system.stars = [MagicMock(spec=Star, name="Alpha Centauri A", location=HexCoord(0, 0))]
    system.planets = []
    system.warp_points = []
    return system


@pytest.fixture
def mock_planet():
    """Create a mock planet."""
    planet = MagicMock(spec=Planet)
    planet.id = 1
    planet.name = "Alpha Centauri III"
    planet.location = HexCoord(2, 0)
    planet.planet_type = PlanetType.CONTINENTAL
    planet.owner_id = None
    return planet


@pytest.fixture
def mock_fleet():
    """Create a mock fleet with ships."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(10, 10)
    fleet.ships = []
    fleet.orders = []
    return fleet


@pytest.fixture
def mock_ship_with_ability():
    """Create a mock ship with superweapon ability."""
    ship = MagicMock()
    ship.id = "ship-1"
    ship.name = "Planet Killer"
    ship.design_data = {
        'layers': {
            'core': [{'id': 'planet_imploder'}]
        }
    }
    return ship


@pytest.fixture
def component_registry():
    """Create a mock component registry with superweapon abilities."""
    return {
        'planet_imploder': {'abilities': {'DestroyPlanet': {}}},
        'stellerator': {'abilities': {'DestroyStar': {}}},
        'quantum_tunneler': {'abilities': {'OpenWarpPoint': {}}},
        'quantum_disruptor': {'abilities': {'CloseWarpPoint': {}}},
        'dyson_constructor': {'abilities': {'CreateDysonSphere': {}}},
        'self_destruct': {'abilities': {'SelfDestruct': {}}},
    }


class TestProcessImplodePlanet:
    """Tests for process_implode_planet()."""

    def test_planet_removed_from_system(
        self, mock_fleet, mock_system, mock_planet, mock_ship_with_ability, component_registry
    ):
        """Planet should be removed from system.planets."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        # Setup
        mock_system.planets = [mock_planet]
        mock_fleet.ships = [mock_ship_with_ability]
        mock_fleet.location = mock_system.global_location + mock_planet.location

        order = FleetOrder(OrderType.IMPLODE_PLANET, target=mock_planet)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.get_planet_by_id.return_value = mock_planet
        mock_galaxy.unregister_planet = MagicMock()
        mock_galaxy._planet_to_system = {mock_planet: mock_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        # Act
        result = processor.process_implode_planet(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        mock_galaxy.unregister_planet.assert_called_once_with(mock_planet)
        assert result.success

    def test_ship_with_ability_removed(
        self, mock_fleet, mock_system, mock_planet, mock_ship_with_ability, component_registry
    ):
        """Ship carrying DestroyPlanet ability should be removed from fleet."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        # Setup
        other_ship = MagicMock()
        other_ship.id = "ship-2"
        other_ship.design_data = {'layers': {}}

        mock_fleet.ships = [mock_ship_with_ability, other_ship]
        mock_fleet.location = mock_system.global_location + mock_planet.location

        order = FleetOrder(OrderType.IMPLODE_PLANET, target=mock_planet)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.unregister_planet = MagicMock()
        mock_galaxy._planet_to_system = {mock_planet: mock_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        # Act
        processor.process_implode_planet(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        mock_fleet.remove_ship.assert_called_once_with(mock_ship_with_ability)

    def test_event_logged(
        self, mock_fleet, mock_system, mock_planet, mock_ship_with_ability, component_registry
    ):
        """PLANET_DESTROYED event should be logged."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        mock_fleet.ships = [mock_ship_with_ability]
        mock_fleet.location = mock_system.global_location

        order = FleetOrder(OrderType.IMPLODE_PLANET, target=mock_planet)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.unregister_planet = MagicMock()
        mock_galaxy._planet_to_system = {mock_planet: mock_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.id = 0
        empire.colonies = []

        with patch('game.strategy.engine.superweapon_order_processor.log_event') as mock_log:
            processor.process_implode_planet(
                mock_fleet, empire, mock_galaxy, component_registry
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            from game.strategy.events.event_types import EventType, EventCategory
            assert call_args[0][0] == EventType.PLANET_DESTROYED
            assert call_args[1]['category'] == EventCategory.SUPERWEAPONS


class TestProcessStellerateStar:
    """Tests for process_stellerate_star()."""

    def test_all_stars_removed(
        self, mock_fleet, mock_system, component_registry
    ):
        """All stars should be removed from the system."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        # Setup ship with DestroyStar
        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'stellerator'}]}}
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_system.stars = [MagicMock(), MagicMock()]  # 2 stars
        mock_system.planets = []

        order = FleetOrder(OrderType.STELLERATE_STAR)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.get_all_fleets_in_system.return_value = [(MagicMock(), mock_fleet)]

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.id = 0
        empires = [empire]

        # Act
        result = processor.process_stellerate_star(
            mock_fleet, empire, mock_galaxy, empires, component_registry
        )

        # Assert - stars should be cleared
        assert mock_system.stars == []
        assert result.fleet_consumed  # Suicide weapon

    def test_all_planets_removed(
        self, mock_fleet, mock_system, mock_planet, component_registry
    ):
        """All planets should be removed and unregistered."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'stellerator'}]}}
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_system.planets = [mock_planet]

        order = FleetOrder(OrderType.STELLERATE_STAR)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.get_all_fleets_in_system.return_value = [(MagicMock(), mock_fleet)]

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []
        empires = [empire]

        # Act
        processor.process_stellerate_star(
            mock_fleet, empire, mock_galaxy, empires, component_registry
        )

        # Assert
        mock_galaxy.unregister_planet.assert_called_with(mock_planet)

    def test_all_fleets_destroyed_including_actor(
        self, mock_fleet, mock_system, component_registry
    ):
        """All fleets in system (including the acting fleet) should be destroyed."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'stellerator'}]}}
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        # Another fleet in the system
        other_fleet = MagicMock(spec=Fleet)
        other_fleet.id = 2
        other_fleet.location = mock_system.global_location

        order = FleetOrder(OrderType.STELLERATE_STAR)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}

        empire1 = MagicMock()
        empire1.id = 0
        empire2 = MagicMock()
        empire2.id = 1

        # Both fleets in system
        mock_galaxy.get_all_fleets_in_system.return_value = [
            (empire1, mock_fleet),
            (empire2, other_fleet)
        ]

        processor = SuperweaponOrderProcessor()
        empires = [empire1, empire2]

        # Act
        processor.process_stellerate_star(
            mock_fleet, empire1, mock_galaxy, empires, component_registry
        )

        # Assert - both empires should have remove_fleet called
        empire1.remove_fleet.assert_called_with(mock_fleet)
        empire2.remove_fleet.assert_called_with(other_fleet)

    def test_warp_points_preserved(
        self, mock_fleet, mock_system, component_registry
    ):
        """Warp points should NOT be removed."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'stellerator'}]}}
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        warp_point = WarpPoint("Beta Centauri", HexCoord(5, 0))
        mock_system.warp_points = [warp_point]
        mock_system.planets = []

        order = FleetOrder(OrderType.STELLERATE_STAR)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.get_all_fleets_in_system.return_value = [(MagicMock(), mock_fleet)]

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empires = [empire]

        # Act
        processor.process_stellerate_star(
            mock_fleet, empire, mock_galaxy, empires, component_registry
        )

        # Assert - warp points unchanged
        assert len(mock_system.warp_points) == 1
        assert mock_system.warp_points[0].destination_id == "Beta Centauri"


class TestProcessOpenWarpPoint:
    """Tests for process_open_warp_point()."""

    def test_warp_points_created_in_both_systems(self, mock_fleet, component_registry):
        """Warp points should be created in both current and target systems."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        # Setup ship with OpenWarpPoint
        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'quantum_tunneler'}]}}

        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)
        current_system.warp_points = []
        current_system.stars = [MagicMock(location=HexCoord(0, 0))]

        target_system = MagicMock(spec=StarSystem)
        target_system.name = "Beta"
        target_system.global_location = HexCoord(50, 50)
        target_system.warp_points = []
        target_system.stars = [MagicMock(location=HexCoord(0, 0))]

        mock_fleet.ships = [ship]
        mock_fleet.location = current_system.global_location

        order_target = {'target_system_name': 'Beta'}
        order = FleetOrder(OrderType.OPEN_WARP_POINT, target=order_target)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {
            current_system.global_location: current_system,
        }
        mock_galaxy.name_map = {
            'Alpha': current_system,
            'Beta': target_system,
        }

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        # Act
        processor.process_open_warp_point(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert - both systems should have warp points added
        assert len(current_system.warp_points) == 1
        assert current_system.warp_points[0].destination_id == "Beta"
        assert len(target_system.warp_points) == 1
        assert target_system.warp_points[0].destination_id == "Alpha"

    def test_ship_consumed(self, mock_fleet, component_registry):
        """Ship with OpenWarpPoint should be removed from fleet."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'quantum_tunneler'}]}}

        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)
        current_system.warp_points = []
        current_system.stars = [MagicMock(location=HexCoord(0, 0))]

        target_system = MagicMock(spec=StarSystem)
        target_system.name = "Beta"
        target_system.global_location = HexCoord(50, 50)
        target_system.warp_points = []

        mock_fleet.ships = [ship]
        mock_fleet.location = current_system.global_location

        order = FleetOrder(OrderType.OPEN_WARP_POINT, target={'target_system_name': 'Beta'})
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {current_system.global_location: current_system}
        mock_galaxy.name_map = {'Alpha': current_system, 'Beta': target_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        # Act
        processor.process_open_warp_point(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        mock_fleet.remove_ship.assert_called_once_with(ship)


class TestProcessCloseWarpPoint:
    """Tests for process_close_warp_point()."""

    def test_both_ends_removed(self, mock_fleet, component_registry):
        """Both ends of the warp link should be removed."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'quantum_disruptor'}]}}

        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)
        wp = WarpPoint("Beta", HexCoord(5, 0))
        current_system.warp_points = [wp]

        mock_fleet.ships = [ship]
        mock_fleet.location = current_system.global_location + wp.location

        order = FleetOrder(OrderType.CLOSE_WARP_POINT, target="Beta")
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {current_system.global_location: current_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        # Act
        processor.process_close_warp_point(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        mock_galaxy.remove_warp_link.assert_called_once_with("Alpha", "Beta")

    def test_ship_consumed(self, mock_fleet, component_registry):
        """Ship with CloseWarpPoint should be removed."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'quantum_disruptor'}]}}

        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)
        wp = WarpPoint("Beta", HexCoord(5, 0))
        current_system.warp_points = [wp]

        mock_fleet.ships = [ship]
        mock_fleet.location = current_system.global_location + wp.location

        order = FleetOrder(OrderType.CLOSE_WARP_POINT, target="Beta")
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {current_system.global_location: current_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        # Act
        processor.process_close_warp_point(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        mock_fleet.remove_ship.assert_called_once_with(ship)


class TestProcessCreateDysonSphere:
    """Tests for process_create_dyson_sphere()."""

    def test_star_removed(self, mock_fleet, mock_system, component_registry):
        """Star should be removed from system."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'dyson_constructor'}]}}

        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_system.stars = [MagicMock()]
        mock_system.planets = []

        order = FleetOrder(OrderType.CREATE_DYSON_SPHERE)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.register_planet = MagicMock()

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        # Act
        processor.process_create_dyson_sphere(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        assert mock_system.stars == []

    def test_nearby_planets_removed(self, mock_fleet, mock_system, component_registry):
        """Planets within 9 hexes should be removed."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'dyson_constructor'}]}}

        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        star = MagicMock()
        star.location = HexCoord(0, 0)
        mock_system.stars = [star]

        # One planet close (should be removed), one far (should stay)
        close_planet = MagicMock()
        close_planet.id = 1
        close_planet.location = HexCoord(5, 0)  # 5 hexes from star

        far_planet = MagicMock()
        far_planet.id = 2
        far_planet.location = HexCoord(15, 0)  # 15 hexes from star

        mock_system.planets = [close_planet, far_planet]

        order = FleetOrder(OrderType.CREATE_DYSON_SPHERE)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.register_planet = MagicMock()

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        # Act
        processor.process_create_dyson_sphere(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert - close planet unregistered, far planet NOT unregistered
        calls = [call[0][0] for call in mock_galaxy.unregister_planet.call_args_list]
        assert close_planet in calls
        assert far_planet not in calls

    def test_dyson_sphere_created(self, mock_fleet, mock_system, component_registry):
        """Dyson Sphere planet should be created at system center."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'dyson_constructor'}]}}

        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        star = MagicMock()
        star.location = HexCoord(0, 0)
        mock_system.stars = [star]
        mock_system.planets = []

        order = FleetOrder(OrderType.CREATE_DYSON_SPHERE)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.register_planet = MagicMock()

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        # Act
        processor.process_create_dyson_sphere(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert - register_planet called with a Dyson Sphere
        mock_galaxy.register_planet.assert_called_once()
        call_args = mock_galaxy.register_planet.call_args
        dyson = call_args[0][1]  # Second positional arg is the planet
        assert dyson.planet_type == PlanetType.DYSON_SPHERE
        assert dyson.location == HexCoord(0, 0)

    def test_ship_consumed(self, mock_fleet, mock_system, component_registry):
        """Ship with CreateDysonSphere should be removed."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.design_data = {'layers': {'core': [{'id': 'dyson_constructor'}]}}

        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        star = MagicMock()
        star.location = HexCoord(0, 0)
        mock_system.stars = [star]
        mock_system.planets = []

        order = FleetOrder(OrderType.CREATE_DYSON_SPHERE)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.register_planet = MagicMock()

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        # Act
        processor.process_create_dyson_sphere(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        mock_fleet.remove_ship.assert_called_once_with(ship)


class TestProcessSelfDestruct:
    """Tests for process_self_destruct()."""

    def test_specified_ships_removed(self, mock_fleet):
        """Specified ships should be removed from fleet."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship1 = MagicMock()
        ship1.id = "ship-1"
        ship2 = MagicMock()
        ship2.id = "ship-2"
        ship3 = MagicMock()
        ship3.id = "ship-3"

        mock_fleet.ships = [ship1, ship2, ship3]

        # Only destruct ship1 and ship3
        order = FleetOrder(OrderType.SELF_DESTRUCT, target=["ship-1", "ship-3"])
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        # Act
        processor.process_self_destruct(mock_fleet, empire, mock_galaxy)

        # Assert
        remove_calls = [call[0][0] for call in mock_fleet.remove_ship.call_args_list]
        assert ship1 in remove_calls
        assert ship3 in remove_calls
        assert ship2 not in remove_calls

    def test_event_logged(self, mock_fleet):
        """SHIPS_SELF_DESTRUCTED event should be logged."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        ship = MagicMock()
        ship.id = "ship-1"
        ship.name = "Exploder"
        mock_fleet.ships = [ship]

        order = FleetOrder(OrderType.SELF_DESTRUCT, target=["ship-1"])
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.id = 0

        with patch('game.strategy.engine.superweapon_order_processor.log_event') as mock_log:
            processor.process_self_destruct(mock_fleet, empire, mock_galaxy)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            from game.strategy.events.event_types import EventType, EventCategory
            assert call_args[0][0] == EventType.SHIPS_SELF_DESTRUCTED
            assert call_args[1]['category'] == EventCategory.SUPERWEAPONS


class TestComponentConsumption:
    """Tests for component consumption patterns."""

    def test_fleet_not_removed_if_ships_remain(
        self, mock_fleet, mock_system, mock_planet, mock_ship_with_ability, component_registry
    ):
        """Fleet should NOT be flagged for removal if ships remain after operation."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        other_ship = MagicMock()
        other_ship.id = "ship-2"
        other_ship.design_data = {'layers': {}}

        mock_fleet.ships = [mock_ship_with_ability, other_ship]
        mock_fleet.location = mock_system.global_location

        order = FleetOrder(OrderType.IMPLODE_PLANET, target=mock_planet)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.unregister_planet = MagicMock()
        mock_galaxy._planet_to_system = {mock_planet: mock_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        # Simulate remove_ship behavior
        def do_remove(ship):
            mock_fleet.ships.remove(ship)
        mock_fleet.remove_ship.side_effect = do_remove

        # Act
        result = processor.process_implode_planet(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        assert not result.fleet_consumed
        assert len(mock_fleet.ships) == 1  # other_ship remains

    def test_fleet_removed_if_last_ship(
        self, mock_fleet, mock_system, mock_planet, mock_ship_with_ability, component_registry
    ):
        """Fleet should be flagged for removal if no ships remain."""
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor

        mock_fleet.ships = [mock_ship_with_ability]  # Only one ship
        mock_fleet.location = mock_system.global_location

        order = FleetOrder(OrderType.IMPLODE_PLANET, target=mock_planet)
        mock_fleet.get_current_order.return_value = order

        mock_galaxy = MagicMock()
        mock_galaxy.unregister_planet = MagicMock()
        mock_galaxy._planet_to_system = {mock_planet: mock_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        # Simulate remove_ship behavior
        def do_remove(ship):
            mock_fleet.ships.remove(ship)
        mock_fleet.remove_ship.side_effect = do_remove

        # Act
        result = processor.process_implode_planet(
            mock_fleet, empire, mock_galaxy, component_registry
        )

        # Assert
        assert result.fleet_consumed
        assert len(mock_fleet.ships) == 0
