"""Tests for PlanetActionEngine — instant dispatch of activation orders.

Orders are instant: they set ComponentActivationState on the facility
and are popped immediately. The timer is managed by ComponentActivationEngine.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.engine.planet_action_engine import PlanetActionEngine
from game.strategy.data.order_types import Order as PlanetOrder
from game.strategy.data.order_types import OrderType
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)


def _make_facility(instance_id, design_data, is_operational=True):
    """Create a mock PlanetaryFacility with activation state support."""
    facility = MagicMock()
    facility.instance_id = instance_id
    facility.design_data = design_data
    facility.is_operational = is_operational
    facility.component_states = {}

    def get_activation_state(key):
        data = facility.component_states.get(key)
        if data is None:
            return ComponentActivationState()
        return ComponentActivationState.from_dict(data)

    def set_activation_state(key, state):
        facility.component_states[key] = state.to_dict()

    def set_component_active(comp_id, active):
        pass  # Legacy — no longer used for activation

    facility.get_activation_state = get_activation_state
    facility.set_activation_state = set_activation_state
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
                            "activation_time": 250,
                            "deactivation_time": 150
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
    planet.active_abilities = {'PlanetaryShield': False}
    planet.orders = orders or []

    def get_current_order():
        return planet.orders[0] if planet.orders else None

    def pop_order():
        return planet.orders.pop(0) if planet.orders else None

    def add_order(order):
        planet.orders.append(order)

    planet.get_current_order = get_current_order
    planet.pop_order = pop_order
    planet.add_order = add_order
    return planet


def _make_empire(colonies=None):
    empire = MagicMock()
    empire.id = 1
    empire.colonies = colonies or []
    return empire


class TestPlanetActionEngine:
    """Tests for PlanetActionEngine instant dispatch."""

    def test_empty_order_queue_no_action(self):
        """Planet with no orders produces no result."""
        engine = PlanetActionEngine()
        planet = _make_planet()
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 0

    def test_activate_order_is_instant(self):
        """ACTIVATE_ABILITY order is popped immediately (no tick progress)."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = PlanetOrder(OrderType.ACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1", "ability_name": "PlanetaryShield"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 1
        assert results[0].action_completed is True
        assert len(planet.orders) == 0  # Order popped immediately

    def test_activate_sets_activating_state(self):
        """ACTIVATE_ABILITY sets ComponentActivationState to ACTIVATING."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = PlanetOrder(OrderType.ACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1", "ability_name": "PlanetaryShield"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        # Find the activation state that was set
        states_with_activating = [
            ComponentActivationState.from_dict(v)
            for v in facility.component_states.values()
            if isinstance(v, dict) and v.get('phase') == 'activating'
        ]
        assert len(states_with_activating) == 1
        state = states_with_activating[0]
        assert state.phase == ActivationPhase.ACTIVATING
        assert state.required_ticks == 250
        assert state.energy_drain_rate == 25.0
        assert state.ability_name == "PlanetaryShield"

    def test_deactivate_from_active_sets_deactivating(self):
        """DEACTIVATE_ABILITY from ACTIVE sets DEACTIVATING state."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        # Pre-set as ACTIVE
        facility.component_states["OUTER:0:geologic_stabilizer_sector"] = ComponentActivationState(
            phase=ActivationPhase.ACTIVE,
            ability_name="PlanetaryShield",
            energy_drain_rate=25.0,
        ).to_dict()

        order = PlanetOrder(OrderType.DEACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1",
                                   "ability_name": "PlanetaryShield",
                                   "component_key": "OUTER:0:geologic_stabilizer_sector"})
        planet = _make_planet(facilities=[facility], orders=[order])
        planet.active_abilities = {'PlanetaryShield': True}
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        state = facility.get_activation_state("OUTER:0:geologic_stabilizer_sector")
        assert state.phase == ActivationPhase.DEACTIVATING
        assert state.required_ticks == 150
        assert len(planet.orders) == 0

    def test_deactivate_from_activating_cancels(self):
        """DEACTIVATE_ABILITY from ACTIVATING cancels to INACTIVE."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        facility.component_states["OUTER:0:geologic_stabilizer_sector"] = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=100,
            required_ticks=250,
            ability_name="PlanetaryShield",
            energy_drain_rate=25.0,
        ).to_dict()

        order = PlanetOrder(OrderType.DEACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1",
                                   "ability_name": "PlanetaryShield",
                                   "component_key": "OUTER:0:geologic_stabilizer_sector"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        state = facility.get_activation_state("OUTER:0:geologic_stabilizer_sector")
        assert state.phase == ActivationPhase.INACTIVE
        assert state.progress_ticks == 0

    def test_destroyed_facility_cancels_order(self):
        """Order is canceled if target facility no longer exists."""
        engine = PlanetActionEngine()
        order = PlanetOrder(OrderType.ACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1", "ability_name": "PlanetaryShield"})
        planet = _make_planet(facilities=[], orders=[order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 0
        assert len(planet.orders) == 0

    def test_multiple_instant_orders_process_sequentially(self):
        """Multiple instant orders process FIFO — each popped before next starts."""
        engine = PlanetActionEngine()
        design = {
            "layers": {
                "OUTER": [
                    {"id": "comp_a", "abilities": {"AbilityA": {"activation_time": 100, "deactivation_time": 50, "energy_drain_rate": 10}}},
                    {"id": "comp_b", "abilities": {"AbilityB": {"activation_time": 200, "deactivation_time": 75, "energy_drain_rate": 20}}},
                ]
            }
        }
        facility = _make_facility("fac-1", design)
        order1 = PlanetOrder(OrderType.ACTIVATE_ABILITY,
                            target={"facility_instance_id": "fac-1", "ability_name": "AbilityA"})
        order2 = PlanetOrder(OrderType.ACTIVATE_ABILITY,
                            target={"facility_instance_id": "fac-1", "ability_name": "AbilityB"})
        planet = _make_planet(facilities=[facility], orders=[order1, order2])
        empire = _make_empire(colonies=[planet])

        # First tick processes order1
        results = engine.process_planet_actions_tick(1, [empire])
        assert len(results) == 1
        assert len(planet.orders) == 1  # order2 still in queue

        # Second tick processes order2
        results = engine.process_planet_actions_tick(2, [empire])
        assert len(results) == 1
        assert len(planet.orders) == 0

        # Both components should be ACTIVATING
        activating_count = sum(
            1 for v in facility.component_states.values()
            if isinstance(v, dict) and v.get('phase') == 'activating'
        )
        assert activating_count == 2
