"""Tests for PlanetActionEngine — instant dispatch of activation orders.

Orders are instant: they set ComponentActivationState on the facility
and are popped immediately. The timer is managed by ComponentActivationEngine.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.engine.planet_action_engine import PlanetActionEngine
from game.strategy.data.order_types import Order as Order
from game.strategy.data.order_types import OrderType
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.events.event_types import EventType, EventCategory


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
    # active_abilities is a derived property on real Planet; not needed on mocks
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


# PROJ-479 Task 5.4 (DUP-005): _make_empire moved to engine/conftest.py
from .conftest import make_mock_empire as _make_empire  # noqa: E402


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
        order = Order(OrderType.ACTIVATE_ABILITY,
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
        order = Order(OrderType.ACTIVATE_ABILITY,
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

        order = Order(OrderType.DEACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1",
                                   "ability_name": "PlanetaryShield",
                                   "component_key": "OUTER:0:geologic_stabilizer_sector"})
        planet = _make_planet(facilities=[facility], orders=[order])
        # active_abilities is derived from component_states on real Planet
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

        order = Order(OrderType.DEACTIVATE_ABILITY,
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
        order = Order(OrderType.ACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1", "ability_name": "PlanetaryShield"})
        planet = _make_planet(facilities=[], orders=[order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 0
        assert len(planet.orders) == 0

    def test_multiple_planet_action_orders_all_dispatch_same_tick(self):
        """All planet action orders dispatch instantly on the same tick."""
        engine = PlanetActionEngine()
        # PROJ-429 Phase 8: ACTIVATE_ABILITY orders now fail fast against
        # unregistered ability names; use real registered stabilizers.
        design = {
            "layers": {
                "OUTER": [
                    {"id": "comp_a", "abilities": {"GeologicStabilizer": {"activation_time": 100, "deactivation_time": 50, "energy_drain_rate": 10}}},
                    {"id": "comp_b", "abilities": {"StellarStabilizer": {"activation_time": 200, "deactivation_time": 75, "energy_drain_rate": 20}}},
                ]
            }
        }
        facility = _make_facility("fac-1", design)
        order1 = Order(OrderType.ACTIVATE_ABILITY,
                            target={"facility_instance_id": "fac-1", "ability_name": "GeologicStabilizer"})
        order2 = Order(OrderType.ACTIVATE_ABILITY,
                            target={"facility_instance_id": "fac-1", "ability_name": "StellarStabilizer"})
        planet = _make_planet(facilities=[facility], orders=[order1, order2])
        empire = _make_empire(colonies=[planet])

        # Single tick should process BOTH orders
        results = engine.process_planet_actions_tick(1, [empire])
        assert len(results) == 2
        assert len(planet.orders) == 0  # Both popped

        # Both components should be ACTIVATING
        activating_count = sum(
            1 for v in facility.component_states.values()
            if isinstance(v, dict) and v.get('phase') == 'activating'
        )
        assert activating_count == 2

    def test_three_stabilizers_same_tick_same_progress(self):
        """Three activations dispatched on same tick should have equal progress after N ticks."""
        engine = PlanetActionEngine()
        design = {
            "layers": {
                "OUTER": [
                    {"id": "geo", "abilities": {"GeologicStabilizer": {"activation_time": 250, "deactivation_time": 150, "energy_drain_rate": 50, "scope": "system"}}},
                    {"id": "stellar", "abilities": {"StellarStabilizer": {"activation_time": 250, "deactivation_time": 150, "energy_drain_rate": 250, "scope": "system"}}},
                    {"id": "warp", "abilities": {"WarpFieldStabilizer": {"activation_time": 250, "deactivation_time": 150, "energy_drain_rate": 150, "scope": "system"}}},
                ]
            }
        }
        facility = _make_facility("fac-1", design)
        orders = [
            Order(OrderType.ACTIVATE_ABILITY, target={"facility_instance_id": "fac-1", "ability_name": "GeologicStabilizer"}),
            Order(OrderType.ACTIVATE_ABILITY, target={"facility_instance_id": "fac-1", "ability_name": "StellarStabilizer"}),
            Order(OrderType.ACTIVATE_ABILITY, target={"facility_instance_id": "fac-1", "ability_name": "WarpFieldStabilizer"}),
        ]
        planet = _make_planet(facilities=[facility], orders=orders)
        empire = _make_empire(colonies=[planet])

        # All three should dispatch on the same tick
        results = engine.process_planet_actions_tick(1, [empire])
        assert len(results) == 3
        assert len(planet.orders) == 0

        # All three should be at progress_ticks=0 (just started)
        for key in facility.component_states:
            state_data = facility.component_states[key]
            assert state_data['phase'] == 'activating'
            assert state_data['progress_ticks'] == 0

    def test_mixed_orders_stops_at_non_planet_action(self):
        """Planet action orders dispatch until a non-planet-action order is reached."""
        engine = PlanetActionEngine()
        # PROJ-429 Phase 8: ACTIVATE_ABILITY orders now fail fast against
        # unregistered ability names; use a real registered stabilizer.
        design = {
            "layers": {
                "OUTER": [
                    {"id": "comp_a", "abilities": {"GeologicStabilizer": {"activation_time": 100, "deactivation_time": 50, "energy_drain_rate": 10}}},
                ]
            }
        }
        facility = _make_facility("fac-1", design)
        activate_order = Order(OrderType.ACTIVATE_ABILITY,
                                    target={"facility_instance_id": "fac-1", "ability_name": "GeologicStabilizer"})
        # A non-planet-action order blocks further processing
        move_order = Order(OrderType.MOVE, target=None)
        deactivate_order = Order(OrderType.DEACTIVATE_ABILITY,
                                      target={"facility_instance_id": "fac-1", "ability_name": "GeologicStabilizer"})
        planet = _make_planet(facilities=[facility], orders=[activate_order, move_order, deactivate_order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        # Only the first activation should process; MOVE blocks the deactivation
        assert len(results) == 1
        assert len(planet.orders) == 2  # MOVE + DEACTIVATE remain

    def test_activate_then_deactivate_same_tick(self):
        """Activate + Deactivate on same tick: both process instantly."""
        engine = PlanetActionEngine()
        # PROJ-429 Phase 8: ACTIVATE_ABILITY orders now fail fast against
        # unregistered ability names; use real registered stabilizers.
        design = {
            "layers": {
                "OUTER": [
                    {"id": "comp_a", "abilities": {"GeologicStabilizer": {"activation_time": 100, "deactivation_time": 50, "energy_drain_rate": 10}}},
                    {"id": "comp_b", "abilities": {"StellarStabilizer": {"activation_time": 200, "deactivation_time": 75, "energy_drain_rate": 20}}},
                ]
            }
        }
        facility = _make_facility("fac-1", design)
        # Pre-set StellarStabilizer as active
        facility.component_states["OUTER:1:comp_b"] = ComponentActivationState(
            phase=ActivationPhase.ACTIVE,
            ability_name="StellarStabilizer",
            energy_drain_rate=20.0,
        ).to_dict()

        activate_a = Order(OrderType.ACTIVATE_ABILITY,
                                target={"facility_instance_id": "fac-1", "ability_name": "GeologicStabilizer"})
        deactivate_b = Order(OrderType.DEACTIVATE_ABILITY,
                                  target={"facility_instance_id": "fac-1", "ability_name": "StellarStabilizer",
                                          "component_key": "OUTER:1:comp_b"})
        planet = _make_planet(facilities=[facility], orders=[activate_a, deactivate_b])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 2
        assert len(planet.orders) == 0

    def test_activate_when_component_already_active_does_not_restart(self, caplog):
        """ACTIVATE_ABILITY only starts from INACTIVE component state."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        key = "OUTER:0:geologic_stabilizer_sector"
        facility.component_states[key] = ComponentActivationState(
            phase=ActivationPhase.ACTIVE,
            progress_ticks=0,
            required_ticks=250,
            ability_name="PlanetaryShield",
            energy_drain_rate=25.0,
        ).to_dict()
        order = Order(OrderType.ACTIVATE_ABILITY, target={
            "facility_instance_id": "fac-1",
            "ability_name": "PlanetaryShield",
            "component_key": key,
        })
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        with caplog.at_level("WARNING"):
            results = engine.process_planet_actions_tick(1, [empire])

        state = facility.get_activation_state(key)
        assert state.phase == ActivationPhase.ACTIVE
        assert len(results) == 1
        assert len(planet.orders) == 0
        assert "cannot activate PlanetaryShield" in caplog.text

    def test_activate_missing_ability_pops_order_without_setting_state(self):
        """Missing ability resolution takes the no-component-key guard path."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = Order(OrderType.ACTIVATE_ABILITY, target={
            "facility_instance_id": "fac-1",
            "ability_name": "MissingAbility",
        })
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        results = engine.process_planet_actions_tick(1, [empire])

        assert len(results) == 1
        assert len(planet.orders) == 0
        assert facility.component_states == {}

    def test_deactivate_from_inactive_logs_warning_without_state_change(self, caplog):
        """DEACTIVATE_ABILITY rejects components that are not active."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        key = "OUTER:0:geologic_stabilizer_sector"
        facility.component_states[key] = ComponentActivationState(
            phase=ActivationPhase.INACTIVE,
            ability_name="PlanetaryShield",
        ).to_dict()
        order = Order(OrderType.DEACTIVATE_ABILITY, target={
            "facility_instance_id": "fac-1",
            "ability_name": "PlanetaryShield",
            "component_key": key,
        })
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        with caplog.at_level("WARNING"):
            results = engine.process_planet_actions_tick(1, [empire])

        state = facility.get_activation_state(key)
        assert state.phase == ActivationPhase.INACTIVE
        assert len(results) == 1
        assert len(planet.orders) == 0
        assert "cannot deactivate PlanetaryShield" in caplog.text

    def test_find_target_facility_non_dict_target_returns_none(self):
        """PROJ-393: non-dict targets are no longer auto-resolved to a shield."""
        engine = PlanetActionEngine()
        no_shield = _make_facility("fac-1", {"layers": {"OUTER": [{"id": "plain"}]}})
        shield = _make_facility("fac-2", _shield_design())
        planet = _make_planet(facilities=[no_shield, shield])
        order = Order(OrderType.ACTIVATE_ABILITY, target=None)

        assert engine._find_target_facility(planet, order) is None

    def test_find_target_facility_returns_none_when_no_facility_has_ability(self):
        """Ability fallback returns None when no facility can satisfy the target."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", {"layers": {"OUTER": [{"id": "plain"}]}})
        planet = _make_planet(facilities=[facility])
        order = Order(OrderType.ACTIVATE_ABILITY, target={
            "ability_name": "MissingAbility",
        })

        assert engine._find_target_facility(planet, order) is None

    def test_target_facility_exists_allows_non_dict_and_unconstrained_targets(self):
        """Targets without a facility constraint should not cancel the order."""
        engine = PlanetActionEngine()
        planet = _make_planet()

        assert engine._target_facility_exists(
            planet, Order(OrderType.ACTIVATE_ABILITY, target=None)
        ) is True
        assert engine._target_facility_exists(
            planet, Order(OrderType.ACTIVATE_ABILITY, target={"ability_name": "A"})
        ) is True


class TestPlanetActionEngineEvents:
    """Tests for shield event logging in PlanetActionEngine."""

    def _make_event_bus(self):
        """Create a mock EventBus that records log_event calls."""
        bus = MagicMock()
        bus.logged = []

        def log_event(event_type, **kwargs):
            bus.logged.append((event_type, kwargs))

        bus.log_event = log_event
        return bus

    def test_activate_logs_shield_activated_event(self):
        """ACTIVATE_ABILITY logs SHIELD_ACTIVATED event via event_bus."""
        event_bus = self._make_event_bus()
        engine = PlanetActionEngine(event_bus=event_bus)
        facility = _make_facility("fac-1", _shield_design())
        order = Order(OrderType.ACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1",
                                   "ability_name": "PlanetaryShield"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        assert len(event_bus.logged) == 1
        event_type, kwargs = event_bus.logged[0]
        assert event_type == EventType.SHIELD_ACTIVATED
        assert kwargs['category'] == EventCategory.PLANET_OPERATIONS
        assert kwargs['empire_id'] == 1
        assert 'PlanetaryShield' in kwargs['message']
        assert kwargs['planet_name'] == 'TestPlanet'

    def test_deactivate_from_active_logs_shield_deactivated_event(self):
        """DEACTIVATE_ABILITY from ACTIVE logs SHIELD_DEACTIVATED event."""
        event_bus = self._make_event_bus()
        engine = PlanetActionEngine(event_bus=event_bus)
        facility = _make_facility("fac-1", _shield_design())
        facility.component_states["OUTER:0:geologic_stabilizer_sector"] = ComponentActivationState(
            phase=ActivationPhase.ACTIVE,
            ability_name="PlanetaryShield",
            energy_drain_rate=25.0,
        ).to_dict()

        order = Order(OrderType.DEACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1",
                                   "ability_name": "PlanetaryShield",
                                   "component_key": "OUTER:0:geologic_stabilizer_sector"})
        planet = _make_planet(facilities=[facility], orders=[order])
        # active_abilities is derived from component_states on real Planet
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        assert len(event_bus.logged) == 1
        event_type, kwargs = event_bus.logged[0]
        assert event_type == EventType.SHIELD_DEACTIVATED
        assert kwargs['category'] == EventCategory.PLANET_OPERATIONS
        assert kwargs['empire_id'] == 1
        assert 'PlanetaryShield' in kwargs['message']

    def test_deactivate_from_activating_logs_shield_deactivated_event(self):
        """DEACTIVATE_ABILITY canceling activation also logs SHIELD_DEACTIVATED."""
        event_bus = self._make_event_bus()
        engine = PlanetActionEngine(event_bus=event_bus)
        facility = _make_facility("fac-1", _shield_design())
        facility.component_states["OUTER:0:geologic_stabilizer_sector"] = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=50,
            required_ticks=250,
            ability_name="PlanetaryShield",
            energy_drain_rate=25.0,
        ).to_dict()

        order = Order(OrderType.DEACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1",
                                   "ability_name": "PlanetaryShield",
                                   "component_key": "OUTER:0:geologic_stabilizer_sector"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        engine.process_planet_actions_tick(1, [empire])

        assert len(event_bus.logged) == 1
        event_type, kwargs = event_bus.logged[0]
        assert event_type == EventType.SHIELD_DEACTIVATED
        assert kwargs['category'] == EventCategory.PLANET_OPERATIONS

    def test_no_event_without_event_bus(self):
        """No crash when event_bus is not provided."""
        engine = PlanetActionEngine()
        facility = _make_facility("fac-1", _shield_design())
        order = Order(OrderType.ACTIVATE_ABILITY,
                           target={"facility_instance_id": "fac-1",
                                   "ability_name": "PlanetaryShield"})
        planet = _make_planet(facilities=[facility], orders=[order])
        empire = _make_empire(colonies=[planet])

        # Should not raise
        results = engine.process_planet_actions_tick(1, [empire])
        assert len(results) == 1
