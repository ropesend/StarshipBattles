"""Tests for PlanetaryFacility activation state integration."""
import pytest
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)


def _make_facility(component_states=None):
    """Create a minimal PlanetaryFacility."""
    return PlanetaryFacility(
        instance_id="fac-1",
        design_id="test_complex",
        name="Test Complex",
        design_data={"layers": {"OUTER": [{"id": "stabilizer"}]}},
        component_states=component_states or {},
    )


class TestGetActivationState:
    """Tests for get_activation_state method."""

    def test_returns_inactive_for_unknown_key(self):
        facility = _make_facility()
        state = facility.get_activation_state("OUTER:0:stabilizer")
        assert state.phase == ActivationPhase.INACTIVE

    def test_returns_stored_state(self):
        stored = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=50,
            required_ticks=250,
            ability_name="GeologicStabilizer",
            energy_drain_rate=25.0,
        )
        facility = _make_facility(component_states={
            "OUTER:0:stabilizer": stored.to_dict()
        })
        state = facility.get_activation_state("OUTER:0:stabilizer")
        assert state.phase == ActivationPhase.ACTIVATING
        assert state.progress_ticks == 50

    def test_backward_compat_active_true(self):
        """Old format {'active': True} returns ACTIVE state."""
        facility = _make_facility(component_states={
            "stabilizer": {"active": True}
        })
        state = facility.get_activation_state("stabilizer")
        assert state.phase == ActivationPhase.ACTIVE

    def test_backward_compat_active_false(self):
        """Old format {'active': False} returns INACTIVE state."""
        facility = _make_facility(component_states={
            "stabilizer": {"active": False}
        })
        state = facility.get_activation_state("stabilizer")
        assert state.phase == ActivationPhase.INACTIVE


class TestSetActivationState:
    """Tests for set_activation_state method."""

    def test_stores_state(self):
        facility = _make_facility()
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=0,
            required_ticks=250,
            ability_name="StellarStabilizer",
            energy_drain_rate=250.0,
        )
        facility.set_activation_state("OUTER:0:stellar_stabilizer", state)

        retrieved = facility.get_activation_state("OUTER:0:stellar_stabilizer")
        assert retrieved.phase == ActivationPhase.ACTIVATING
        assert retrieved.required_ticks == 250

    def test_overwrites_existing_state(self):
        facility = _make_facility(component_states={
            "OUTER:0:stabilizer": ComponentActivationState(
                phase=ActivationPhase.ACTIVE
            ).to_dict()
        })
        new_state = ComponentActivationState(
            phase=ActivationPhase.DEACTIVATING,
            required_ticks=150,
        )
        facility.set_activation_state("OUTER:0:stabilizer", new_state)

        retrieved = facility.get_activation_state("OUTER:0:stabilizer")
        assert retrieved.phase == ActivationPhase.DEACTIVATING


class TestIsComponentActive:
    """is_component_active should check ComponentActivationState."""

    def test_active_when_functionally_active(self):
        facility = _make_facility(component_states={
            "OUTER:0:stabilizer": ComponentActivationState(
                phase=ActivationPhase.ACTIVE
            ).to_dict()
        })
        assert facility.is_component_active("OUTER:0:stabilizer") is True

    def test_inactive_when_activating(self):
        facility = _make_facility(component_states={
            "OUTER:0:stabilizer": ComponentActivationState(
                phase=ActivationPhase.ACTIVATING
            ).to_dict()
        })
        assert facility.is_component_active("OUTER:0:stabilizer") is False

    def test_inactive_when_deactivating(self):
        facility = _make_facility(component_states={
            "OUTER:0:stabilizer": ComponentActivationState(
                phase=ActivationPhase.DEACTIVATING
            ).to_dict()
        })
        assert facility.is_component_active("OUTER:0:stabilizer") is False

    def test_backward_compat_old_format(self):
        facility = _make_facility(component_states={
            "stabilizer": {"active": True}
        })
        assert facility.is_component_active("stabilizer") is True


class TestSerialization:
    """to_dict/from_dict preserves activation states."""

    def test_round_trip(self):
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=100,
            required_ticks=250,
            ability_name="WarpFieldStabilizer",
            energy_drain_rate=150.0,
        )
        facility = _make_facility()
        facility.set_activation_state("OUTER:0:warp_stabilizer", state)

        data = facility.to_dict()
        restored = PlanetaryFacility.from_dict(data)

        restored_state = restored.get_activation_state("OUTER:0:warp_stabilizer")
        assert restored_state.phase == ActivationPhase.ACTIVATING
        assert restored_state.progress_ticks == 100
        assert restored_state.ability_name == "WarpFieldStabilizer"
