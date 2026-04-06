"""Tests for ComponentActivationState — per-component activation timer state machine.

State machine: INACTIVE → ACTIVATING → ACTIVE → DEACTIVATING → INACTIVE
"""
import pytest
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)


class TestActivationPhase:
    """ActivationPhase enum basics."""

    def test_has_four_phases(self):
        assert len(ActivationPhase) == 4

    def test_values_are_strings(self):
        assert ActivationPhase.INACTIVE.value == "inactive"
        assert ActivationPhase.ACTIVATING.value == "activating"
        assert ActivationPhase.ACTIVE.value == "active"
        assert ActivationPhase.DEACTIVATING.value == "deactivating"


class TestComponentActivationStateInit:
    """Default construction and basic properties."""

    def test_default_is_inactive(self):
        state = ComponentActivationState()
        assert state.phase == ActivationPhase.INACTIVE

    def test_default_progress_zero(self):
        state = ComponentActivationState()
        assert state.progress_ticks == 0
        assert state.required_ticks == 0

    def test_is_functionally_active_only_when_active(self):
        for phase in ActivationPhase:
            state = ComponentActivationState(phase=phase)
            if phase == ActivationPhase.ACTIVE:
                assert state.is_functionally_active is True
            else:
                assert state.is_functionally_active is False

    def test_is_draining_energy(self):
        """Energy drains during ACTIVATING, ACTIVE, and DEACTIVATING."""
        draining_phases = {ActivationPhase.ACTIVATING, ActivationPhase.ACTIVE, ActivationPhase.DEACTIVATING}
        for phase in ActivationPhase:
            state = ComponentActivationState(phase=phase, energy_drain_rate=10.0)
            if phase in draining_phases:
                assert state.is_draining_energy is True
            else:
                assert state.is_draining_energy is False

    def test_is_draining_energy_false_when_rate_zero(self):
        """No drain even in active phases if drain rate is 0."""
        state = ComponentActivationState(phase=ActivationPhase.ACTIVE, energy_drain_rate=0.0)
        assert state.is_draining_energy is False


class TestStartActivating:
    """Transition from INACTIVE to ACTIVATING."""

    def test_starts_activating(self):
        state = ComponentActivationState()
        state.start_activating(required_ticks=250, energy_drain_rate=50.0)
        assert state.phase == ActivationPhase.ACTIVATING
        assert state.progress_ticks == 0
        assert state.required_ticks == 250
        assert state.energy_drain_rate == 50.0

    def test_cannot_activate_when_already_active(self):
        state = ComponentActivationState(phase=ActivationPhase.ACTIVE)
        with pytest.raises(ValueError):
            state.start_activating(required_ticks=100, energy_drain_rate=10.0)

    def test_cannot_activate_when_already_activating(self):
        state = ComponentActivationState(phase=ActivationPhase.ACTIVATING)
        with pytest.raises(ValueError):
            state.start_activating(required_ticks=100, energy_drain_rate=10.0)


class TestStartDeactivating:
    """Transition from ACTIVE to DEACTIVATING."""

    def test_starts_deactivating(self):
        state = ComponentActivationState(phase=ActivationPhase.ACTIVE, energy_drain_rate=50.0)
        state.start_deactivating(required_ticks=150)
        assert state.phase == ActivationPhase.DEACTIVATING
        assert state.progress_ticks == 0
        assert state.required_ticks == 150
        assert state.energy_drain_rate == 50.0  # preserves drain rate

    def test_cannot_deactivate_when_inactive(self):
        state = ComponentActivationState(phase=ActivationPhase.INACTIVE)
        with pytest.raises(ValueError):
            state.start_deactivating(required_ticks=100)


class TestCancel:
    """Cancel resets to INACTIVE from any transitional state."""

    def test_cancel_from_activating(self):
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=100,
            required_ticks=250,
            energy_drain_rate=50.0,
        )
        state.cancel()
        assert state.phase == ActivationPhase.INACTIVE
        assert state.progress_ticks == 0
        assert state.required_ticks == 0
        assert state.energy_drain_rate == 0.0

    def test_cancel_from_deactivating(self):
        state = ComponentActivationState(phase=ActivationPhase.DEACTIVATING)
        state.cancel()
        assert state.phase == ActivationPhase.INACTIVE

    def test_cancel_from_active(self):
        """Cancel from ACTIVE goes directly to INACTIVE (instant shutdown)."""
        state = ComponentActivationState(phase=ActivationPhase.ACTIVE)
        state.cancel()
        assert state.phase == ActivationPhase.INACTIVE

    def test_cancel_from_inactive_is_noop(self):
        state = ComponentActivationState(phase=ActivationPhase.INACTIVE)
        state.cancel()
        assert state.phase == ActivationPhase.INACTIVE


class TestTick:
    """Tick advances progress and triggers transitions."""

    def test_tick_increments_progress_during_activating(self):
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=0,
            required_ticks=250,
        )
        transitioned = state.tick()
        assert transitioned is False
        assert state.progress_ticks == 1

    def test_tick_completes_activation(self):
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=249,
            required_ticks=250,
        )
        transitioned = state.tick()
        assert transitioned is True
        assert state.phase == ActivationPhase.ACTIVE
        assert state.progress_ticks == 0
        assert state.required_ticks == 0

    def test_tick_increments_progress_during_deactivating(self):
        state = ComponentActivationState(
            phase=ActivationPhase.DEACTIVATING,
            progress_ticks=50,
            required_ticks=150,
        )
        transitioned = state.tick()
        assert transitioned is False
        assert state.progress_ticks == 51

    def test_tick_completes_deactivation(self):
        state = ComponentActivationState(
            phase=ActivationPhase.DEACTIVATING,
            progress_ticks=149,
            required_ticks=150,
            energy_drain_rate=50.0,
        )
        transitioned = state.tick()
        assert transitioned is True
        assert state.phase == ActivationPhase.INACTIVE
        assert state.progress_ticks == 0
        assert state.energy_drain_rate == 0.0

    def test_tick_noop_when_inactive(self):
        state = ComponentActivationState(phase=ActivationPhase.INACTIVE)
        transitioned = state.tick()
        assert transitioned is False
        assert state.phase == ActivationPhase.INACTIVE

    def test_tick_noop_when_active(self):
        state = ComponentActivationState(phase=ActivationPhase.ACTIVE)
        transitioned = state.tick()
        assert transitioned is False
        assert state.phase == ActivationPhase.ACTIVE

    def test_full_activation_cycle(self):
        """250 ticks to activate, then 150 ticks to deactivate."""
        state = ComponentActivationState()
        state.start_activating(required_ticks=250, energy_drain_rate=50.0)

        # Tick 249 times — still activating
        for _ in range(249):
            assert state.tick() is False
        assert state.phase == ActivationPhase.ACTIVATING
        assert state.progress_ticks == 249

        # Tick 250 — transitions to ACTIVE
        assert state.tick() is True
        assert state.phase == ActivationPhase.ACTIVE

        # Start deactivating
        state.start_deactivating(required_ticks=150)
        assert state.phase == ActivationPhase.DEACTIVATING

        # Tick 149 times — still deactivating
        for _ in range(149):
            assert state.tick() is False

        # Tick 150 — transitions to INACTIVE
        assert state.tick() is True
        assert state.phase == ActivationPhase.INACTIVE


class TestSerialization:
    """to_dict/from_dict round-trip."""

    def test_round_trip_inactive(self):
        state = ComponentActivationState()
        data = state.to_dict()
        restored = ComponentActivationState.from_dict(data)
        assert restored.phase == ActivationPhase.INACTIVE
        assert restored.progress_ticks == 0

    def test_round_trip_activating(self):
        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=100,
            required_ticks=250,
            ability_name="StellarStabilizer",
            energy_drain_rate=50.0,
        )
        data = state.to_dict()
        restored = ComponentActivationState.from_dict(data)
        assert restored.phase == ActivationPhase.ACTIVATING
        assert restored.progress_ticks == 100
        assert restored.required_ticks == 250
        assert restored.ability_name == "StellarStabilizer"
        assert restored.energy_drain_rate == 50.0

    def test_backward_compat_active_true(self):
        """Old format {'active': True} should map to ACTIVE."""
        data = {'active': True}
        restored = ComponentActivationState.from_dict(data)
        assert restored.phase == ActivationPhase.ACTIVE

    def test_backward_compat_active_false(self):
        """Old format {'active': False} should map to INACTIVE."""
        data = {'active': False}
        restored = ComponentActivationState.from_dict(data)
        assert restored.phase == ActivationPhase.INACTIVE

    def test_backward_compat_empty_dict(self):
        """Empty dict should map to INACTIVE."""
        restored = ComponentActivationState.from_dict({})
        assert restored.phase == ActivationPhase.INACTIVE
