"""
Unit tests for ActionTimeResolver service.

PROJ-187: Resolves action_time for tick-based order execution.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.services.action_time_resolver import ActionTimeResolver


@pytest.fixture
def mock_ship_with_colonize():
    """Create a mock ship with ColonizePlanet ability."""
    ship = MagicMock()
    ship.design_data = {
        'layers': {
            'core': [{
                'id': 'colony_pod',
                'abilities': {'ColonizePlanet': {'planet_type': 'CONTINENTAL', 'action_time': 2}}
            }]
        }
    }
    return ship


@pytest.fixture
def mock_ship_with_default_colonize():
    """Create a mock ship with ColonizePlanet ability using default action_time."""
    ship = MagicMock()
    ship.design_data = {
        'layers': {
            'core': [{
                'id': 'colony_pod',
                'abilities': {'ColonizePlanet': 'CONTINENTAL'}  # String shorthand
            }]
        }
    }
    return ship


@pytest.fixture
def mock_ship_with_destroy_planet():
    """Create a mock ship with DestroyPlanet ability."""
    ship = MagicMock()
    ship.design_data = {
        'layers': {
            'core': [{
                'id': 'planet_imploder',
                'abilities': {'DestroyPlanet': {'action_time': 3}}
            }]
        }
    }
    return ship


@pytest.fixture
def mock_ship_with_destroy_star():
    """Create a mock ship with DestroyStar ability."""
    ship = MagicMock()
    ship.design_data = {
        'layers': {
            'core': [{
                'id': 'stellerator',
                'abilities': {'DestroyStar': {'action_time': 5}}
            }]
        }
    }
    return ship


@pytest.fixture
def mock_ship_with_self_destruct():
    """Create a mock ship with SelfDestruct (boolean marker)."""
    ship = MagicMock()
    ship.design_data = {
        'layers': {
            'core': [{
                'id': 'self_destruct_device',
                'abilities': {'SelfDestruct': True}
            }]
        }
    }
    return ship


@pytest.fixture
def mock_component_registry():
    """Create a mock component registry."""
    return {}  # Not used when abilities are inline in design_data


@pytest.fixture
def mock_fleet(mock_ship_with_colonize):
    """Create a mock fleet."""
    fleet = MagicMock(spec=Fleet)
    fleet.ships = [mock_ship_with_colonize]
    return fleet


class TestActionTimeResolverColonize:
    """Tests for COLONIZE order action time resolution."""

    def test_colonize_with_action_time_from_ability(
        self, mock_ship_with_colonize, mock_component_registry
    ):
        """COLONIZE uses action_time from ColonizePlanet ability."""
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [mock_ship_with_colonize]
        order = Order(OrderType.COLONIZE, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 2

    def test_colonize_with_string_shorthand_defaults_to_1(
        self, mock_ship_with_default_colonize, mock_component_registry
    ):
        """COLONIZE with string shorthand ability defaults action_time to 1."""
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [mock_ship_with_default_colonize]
        order = Order(OrderType.COLONIZE, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 1

    def test_colonize_without_ability_defaults_to_1(self, mock_component_registry):
        """COLONIZE without ColonizePlanet ability defaults to 1."""
        ship = MagicMock()
        ship.design_data = {'layers': {'core': []}}  # No abilities
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [ship]
        order = Order(OrderType.COLONIZE, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 1


class TestActionTimeResolverSuperweapons:
    """Tests for superweapon order action time resolution."""

    def test_implode_planet_action_time(
        self, mock_ship_with_destroy_planet, mock_component_registry
    ):
        """IMPLODE_PLANET uses action_time from DestroyPlanet ability."""
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [mock_ship_with_destroy_planet]
        order = Order(OrderType.IMPLODE_PLANET, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 3

    def test_stellerate_star_action_time(
        self, mock_ship_with_destroy_star, mock_component_registry
    ):
        """STELLERATE_STAR uses action_time from DestroyStar ability."""
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [mock_ship_with_destroy_star]
        order = Order(OrderType.STELLERATE_STAR, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 5

    def test_self_destruct_boolean_marker_defaults_to_1(
        self, mock_ship_with_self_destruct, mock_component_registry
    ):
        """SELF_DESTRUCT with boolean marker defaults action_time to 1."""
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [mock_ship_with_self_destruct]
        order = Order(OrderType.SELF_DESTRUCT, target=['ship_id'])

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 1


class TestActionTimeResolverDefaults:
    """Tests for default action times on various order types."""

    @pytest.mark.parametrize("order_type", [
        OrderType.TRANSFER,
        OrderType.LOAD_POPULATION,
        OrderType.UNLOAD_POPULATION,
        OrderType.JOIN_FLEET,
    ])
    def test_default_action_time_orders(self, order_type, mock_component_registry):
        """Orders without ability-based action_time default to 1.

        PROJ-371 Phase 2 (silent-drift cleanup): ``OrderType.WARP`` was
        removed from this parametrize. The previous local
        ``MOVEMENT_ORDER_TYPES`` frozenset at action_time_resolver.py:48
        omitted ``WARP`` (silently drifted from the canonical set in
        ``data/order_types.py:58-62``); this test pinned the buggy
        behavior. The canonical movement set includes ``WARP``, so the
        resolver now returns 0 for it (handled by the movement engine,
        not the action engine).
        """
        ship = MagicMock()
        ship.design_data = {'layers': {'core': []}}
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [ship]
        order = Order(order_type, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 1


    def test_warp_returns_0_movement_engine_handled(self, mock_component_registry):
        """WARP is a movement order — resolver short-circuits to 0.

        PROJ-371 Phase 2: corrects silent drift between the (buggy)
        local frozenset and the canonical ``MOVEMENT_ORDER_TYPES`` in
        ``data/order_types.py``. WARP is now handled consistently as
        movement.
        """
        ship = MagicMock()
        ship.design_data = {'layers': {'core': []}}
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [ship]
        order = Order(OrderType.WARP, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 0

    def test_move_returns_0(self, mock_component_registry):
        """MOVE order returns 0 (handled by movement engine, not action engine)."""
        ship = MagicMock()
        ship.design_data = {'layers': {'core': []}}
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [ship]
        order = Order(OrderType.MOVE, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 0

    def test_unknown_order_type_returns_1(self, mock_component_registry):
        """Unknown/future order types default to 1."""
        ship = MagicMock()
        ship.design_data = {'layers': {'core': []}}
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [ship]
        # Create a mock order with an arbitrary type
        order = MagicMock()
        order.type = MagicMock()  # Unknown type

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        assert result == 1


class TestActionTimeResolverPlanetAbilities:
    """Tests for generic planet ability activation/deactivation timing."""

    def _planet_with_facilities(self):
        active_facility = MagicMock()
        active_facility.instance_id = "shield-facility"
        active_facility.is_operational = True
        active_facility.design_data = {
            'layers': {
                'core': [{
                    'id': 'shield_generator',
                    'abilities': {
                        'PlanetaryShield': {
                            'activation_time': 50,
                            'deactivation_time': 10,
                        }
                    },
                }]
            }
        }

        inactive_facility = MagicMock()
        inactive_facility.instance_id = "inactive-facility"
        inactive_facility.is_operational = False
        inactive_facility.design_data = {
            'layers': {
                'core': [{
                    'id': 'inactive_generator',
                    'abilities': {
                        'PlanetaryShield': {
                            'activation_time': 99,
                            'deactivation_time': 88,
                        }
                    },
                }]
            }
        }

        planet = MagicMock()
        planet.facilities = [inactive_facility, active_facility]
        return planet

    def test_activate_ability_uses_planet_activation_time(self):
        planet = self._planet_with_facilities()
        order = Order(
            OrderType.ACTIVATE_ABILITY,
            target={'ability_name': 'PlanetaryShield'},
        )

        result = ActionTimeResolver.resolve_action_time(planet, order, {})

        assert result == 50

    def test_deactivate_ability_uses_planet_deactivation_time(self):
        planet = self._planet_with_facilities()
        order = Order(
            OrderType.DEACTIVATE_ABILITY,
            target={'ability_name': 'PlanetaryShield'},
        )

        result = ActionTimeResolver.resolve_action_time(planet, order, {})

        assert result == 10

    def test_activate_ability_missing_name_defaults_to_one(self):
        planet = self._planet_with_facilities()
        order = Order(
            OrderType.ACTIVATE_ABILITY,
            target={'facility_instance_id': 'shield-facility'},
        )

        result = ActionTimeResolver.resolve_action_time(planet, order, {})

        assert result == 1

    def test_activate_ability_filters_by_facility_instance_id(self):
        planet = self._planet_with_facilities()
        order = Order(
            OrderType.ACTIVATE_ABILITY,
            target={
                'ability_name': 'PlanetaryShield',
                'facility_instance_id': 'inactive-facility',
            },
        )

        result = ActionTimeResolver.resolve_action_time(planet, order, {})

        assert result == 1


class TestActionTimeResolverMultipleShips:
    """Tests for fleets with multiple ships."""

    def test_picks_first_ship_with_ability(self, mock_component_registry):
        """When multiple ships have ability, uses the first one found."""
        ship1 = MagicMock()
        ship1.design_data = {
            'layers': {
                'core': [{
                    'id': 'colony_pod',
                    'abilities': {'ColonizePlanet': {'planet_type': 'CONTINENTAL', 'action_time': 2}}
                }]
            }
        }
        ship2 = MagicMock()
        ship2.design_data = {
            'layers': {
                'core': [{
                    'id': 'colony_pod',
                    'abilities': {'ColonizePlanet': {'planet_type': 'CONTINENTAL', 'action_time': 5}}
                }]
            }
        }
        fleet = MagicMock(spec=Fleet)
        fleet.ships = [ship1, ship2]
        order = Order(OrderType.COLONIZE, target=None)

        result = ActionTimeResolver.resolve_action_time(
            fleet, order, mock_component_registry
        )

        # Should use ship1's action_time (first ship)
        assert result == 2
