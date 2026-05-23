"""Tests for ComponentActivationEngine — tick-based activation timer processing."""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.component_activation_engine import ComponentActivationEngine
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)


def _make_facility(instance_id="fac-1", component_states=None):
    """Create a mock facility with activation states."""
    facility = MagicMock()
    facility.instance_id = instance_id
    facility.is_operational = True
    facility.component_states = component_states or {}

    def get_activation_state(key):
        data = facility.component_states.get(key)
        if data is None:
            return ComponentActivationState()
        return ComponentActivationState.from_dict(data)

    def set_activation_state(key, state):
        facility.component_states[key] = state.to_dict()

    facility.get_activation_state = get_activation_state
    facility.set_activation_state = set_activation_state
    return facility


def _make_planet(name="TestPlanet", facilities=None):
    planet = MagicMock()
    planet.name = name
    planet.id = 1
    planet.facilities = facilities or []
    return planet


# PROJ-479 Task 5.4 (DUP-005): _make_empire moved to engine/conftest.py
from .conftest import make_mock_empire as _make_empire  # noqa: E402


class TestComponentActivationEngine:
    """Tests for the activation timer engine."""

    def test_no_activations_no_results(self):
        engine = ComponentActivationEngine()
        planet = _make_planet()
        empire = _make_empire(colonies=[planet])
        results = engine.process_activation_tick(1, [empire])
        assert results == []

    def test_activating_component_ticks(self):
        """ACTIVATING component should have progress incremented."""
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=0,
            required_ticks=250,
            ability_name="StellarStabilizer",
            energy_drain_rate=250.0,
        )
        facility = _make_facility(component_states={
            "OUTER:0:stellar_stabilizer": state.to_dict()
        })
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        engine.process_activation_tick(1, [empire])

        updated = facility.get_activation_state("OUTER:0:stellar_stabilizer")
        assert updated.progress_ticks == 1
        assert updated.phase == ActivationPhase.ACTIVATING

    def test_activation_completes_transitions_to_active(self):
        """When activation completes, component state transitions to ACTIVE."""
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=249,
            required_ticks=250,
            ability_name="StellarStabilizer",
            energy_drain_rate=250.0,
        )
        facility = _make_facility(component_states={
            "OUTER:0:stellar_stabilizer": state.to_dict()
        })
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        results = engine.process_activation_tick(1, [empire])

        updated = facility.get_activation_state("OUTER:0:stellar_stabilizer")
        assert updated.phase == ActivationPhase.ACTIVE
        assert len(results) == 1
        assert results[0]['transitioned'] is True

    def test_deactivation_completes_transitions_to_inactive(self):
        """When deactivation completes, component state transitions to INACTIVE."""
        state = ComponentActivationState(
            phase=ActivationPhase.DEACTIVATING,
            progress_ticks=149,
            required_ticks=150,
            ability_name="WarpFieldStabilizer",
            energy_drain_rate=150.0,
        )
        facility = _make_facility(component_states={
            "OUTER:0:warp_stabilizer": state.to_dict()
        })
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        engine.process_activation_tick(1, [empire])

        updated = facility.get_activation_state("OUTER:0:warp_stabilizer")
        assert updated.phase == ActivationPhase.INACTIVE

    def test_three_components_tick_in_parallel(self):
        """Three ACTIVATING components should all tick on the same tick."""
        states = {}
        for i, name in enumerate(["GeologicStabilizer", "StellarStabilizer", "WarpFieldStabilizer"]):
            states[f"OUTER:{i}:comp_{i}"] = ComponentActivationState(
                phase=ActivationPhase.ACTIVATING,
                progress_ticks=0,
                required_ticks=250,
                ability_name=name,
                energy_drain_rate=50.0,
            ).to_dict()

        facility = _make_facility(component_states=states)
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        engine.process_activation_tick(1, [empire])

        for key in states:
            updated = facility.get_activation_state(key)
            assert updated.progress_ticks == 1

    def test_three_components_complete_on_same_tick(self):
        """Three activations started together should complete together."""
        states = {}
        for i, name in enumerate(["GeologicStabilizer", "StellarStabilizer", "WarpFieldStabilizer"]):
            states[f"OUTER:{i}:comp_{i}"] = ComponentActivationState(
                phase=ActivationPhase.ACTIVATING,
                progress_ticks=249,
                required_ticks=250,
                ability_name=name,
                energy_drain_rate=50.0,
            ).to_dict()

        facility = _make_facility(component_states=states)
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        results = engine.process_activation_tick(1, [empire])

        transitioned = [r for r in results if r['transitioned']]
        assert len(transitioned) == 3
        for key in states:
            updated = facility.get_activation_state(key)
            assert updated.phase == ActivationPhase.ACTIVE

    def test_inactive_and_active_components_not_ticked(self):
        """INACTIVE and ACTIVE components should not produce results."""
        states = {
            "OUTER:0:inactive": ComponentActivationState(
                phase=ActivationPhase.INACTIVE
            ).to_dict(),
            "OUTER:1:active": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="SomeAbility",
            ).to_dict(),
        }
        facility = _make_facility(component_states=states)
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        results = engine.process_activation_tick(1, [empire])
        assert results == []

    def test_non_operational_facility_is_not_ticked(self):
        """Facilities that are offline should not advance activation timers."""
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=0,
            required_ticks=10,
            ability_name="StellarStabilizer",
        )
        facility = _make_facility(component_states={
            "OUTER:0:stellar_stabilizer": state.to_dict()
        })
        facility.is_operational = False
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        results = engine.process_activation_tick(1, [empire])

        updated = facility.get_activation_state("OUTER:0:stellar_stabilizer")
        assert updated.progress_ticks == 0
        assert results == []

    def test_non_dict_component_state_is_ignored(self):
        """Malformed state payloads are skipped instead of crashing the tick."""
        facility = _make_facility(component_states={
            "OUTER:0:bad_state": "not-a-state-dict"
        })
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])
        engine = ComponentActivationEngine()

        results = engine.process_activation_tick(1, [empire])

        assert facility.component_states["OUTER:0:bad_state"] == "not-a-state-dict"
        assert results == []
