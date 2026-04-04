"""Tests for PlanetActionEngine (PROJ-237)."""

import pytest
from unittest.mock import MagicMock

from game.strategy.engine.planet_action_engine import PlanetActionEngine
from game.strategy.data.order_types import Order as PlanetOrder
from game.strategy.data.order_types import OrderType


def _make_facility(instance_id, design_data, is_operational=True):
    """Create a mock PlanetaryFacility."""
    facility = MagicMock()
    facility.instance_id = instance_id
    facility.design_data = design_data
    facility.is_operational = is_operational
    facility.component_states = {}

    def set_component_active(comp_id, active):
        if comp_id not in facility.component_states:
            facility.component_states[comp_id] = {}
        facility.component_states[comp_id]['active'] = active

    facility.set_component_active = set_component_active
    return facility


def _shield_design():
    return {
        "layers": {
            "OUTER": [
                {
                    "id": "geologic_stabilizer_sector",
                    "abilities": {
                        "PlanetaryShield": {
                            "energy_drain_rate": 25.0,
                            "activation_time": 5,
                            "deactivation_time": 2
                        }
                    }
                }
            ]
        }
    }


def _make_planet(name="TestPlanet", facilities=None, orders=None):
    """Create a mock Planet with order management."""
    planet = MagicMock()
    planet.name = name
    planet.id = 1
    planet.facilities = facilities or []
    planet.energy = 100.0
    planet.energy_capacity = 5000.0
    planet.shield_active = False
    planet.orders = orders or []

    def get_current_order():
        return planet.orders[0] if planet.orders else None

    def pop_order():
        return planet.orders.pop(0) if planet.orders else None

    planet.get_current_order = get_current_order
    planet.pop_order = pop_order
    return planet


def _make_empire(colonies=None):
    empire = MagicMock()
    empire.id = 1
    empire.colonies = colonies or []
    return empire


class TestPlanetActionEngine:
    """Tests for PlanetActionEngine."""

    def test_empty_order_queue_no_action(self):
        """Planet with no orders produces no result."""
        engine = PlanetActionEngine()
        planet = _make_planet()
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 0

    def test_execution_progress_increments(self):
        """Order's execution_progress increments each tick."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = PlanetOrder(OrderType.ACTIVATE_SHIELD,
                           target={"facility_instance_id": "fac-1"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 1
        assert results[0].execution_progress == 1
        assert results[0].action_completed is False

    def test_order_completes_at_action_time(self):
        """Order executes when execution_progress reaches action_time."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = PlanetOrder(OrderType.ACTIVATE_SHIELD,
                           target={"facility_instance_id": "fac-1"})
        order.execution_progress = 4  # One tick away from activation_time=5
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 1
        assert results[0].action_completed is True
        assert planet.shield_active is True
        assert len(planet.orders) == 0  # Order popped

    def test_activate_shield_sets_active(self):
        """ACTIVATE_SHIELD order sets planet.shield_active = True."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = PlanetOrder(OrderType.ACTIVATE_SHIELD,
                           target={"facility_instance_id": "fac-1"})
        order.execution_progress = 4
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        assert planet.shield_active is True

    def test_deactivate_shield_sets_inactive(self):
        """DEACTIVATE_SHIELD order sets planet.shield_active = False."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = PlanetOrder(OrderType.DEACTIVATE_SHIELD,
                           target={"facility_instance_id": "fac-1"})
        order.execution_progress = 1  # deactivation_time=2
        planet = _make_planet(facilities=[facility], orders=[order])
        planet.shield_active = True
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        assert planet.shield_active is False
        assert len(planet.orders) == 0

    def test_destroyed_facility_cancels_order(self):
        """Order is canceled if target facility no longer exists."""
        engine = PlanetActionEngine()
        # No facilities on planet, but order targets "fac-1"
        order = PlanetOrder(OrderType.ACTIVATE_SHIELD,
                           target={"facility_instance_id": "fac-1"})
        planet = _make_planet(facilities=[], orders=[order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 0
        assert len(planet.orders) == 0  # Order was popped

    def test_multiple_orders_fifo(self):
        """Orders are processed FIFO — first in queue gets ticked."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order1 = PlanetOrder(OrderType.ACTIVATE_SHIELD,
                            target={"facility_instance_id": "fac-1"})
        order2 = PlanetOrder(OrderType.DEACTIVATE_SHIELD,
                            target={"facility_instance_id": "fac-1"})
        planet = _make_planet(facilities=[facility], orders=[order1, order2])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        # Only order1 gets ticked
        assert results[0].order_type == OrderType.ACTIVATE_SHIELD
        assert order1.execution_progress == 1
        assert order2.execution_progress == 0

    def test_multi_turn_order_persists(self):
        """Orders with action_time > 100 persist across multiple ticks."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = PlanetOrder(OrderType.ACTIVATE_SHIELD,
                           target={"facility_instance_id": "fac-1"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        # Process 4 ticks (activation_time=5)
        for tick in range(1, 5):
            engine.process_planet_actions_tick(tick, [empire])

        assert order.execution_progress == 4
        assert planet.shield_active is False  # Not yet complete
        assert len(planet.orders) == 1  # Still in queue

        # 5th tick completes it
        engine.process_planet_actions_tick(5, [empire])
        assert planet.shield_active is True
        assert len(planet.orders) == 0
