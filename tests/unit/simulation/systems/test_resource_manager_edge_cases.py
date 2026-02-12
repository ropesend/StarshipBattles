"""
Unit tests for ResourceState and ResourceRegistry edge cases.

Tests consume more than available, regen capping, additive storage,
set_value at max, and reset_stats behavior.
"""
import pytest

from game.simulation.systems.resource_manager import ResourceState, ResourceRegistry


class TestResourceStateConsume:
    """Tests for ResourceState.consume edge cases."""

    def test_consume_more_than_available(self):
        """Returns False when consuming more than available."""
        state = ResourceState("fuel", max_value=100.0, current_value=30.0)

        result = state.consume(50.0)

        assert result is False
        assert state.current_value == 30.0  # Unchanged

    def test_consume_exactly_available(self):
        """Returns True when consuming exactly available amount."""
        state = ResourceState("fuel", max_value=100.0, current_value=50.0)

        result = state.consume(50.0)

        assert result is True
        assert state.current_value == 0.0

    def test_consume_partial(self):
        """Returns True for partial consumption."""
        state = ResourceState("energy", max_value=100.0, current_value=80.0)

        result = state.consume(30.0)

        assert result is True
        assert state.current_value == 50.0


class TestResourceStateRegen:
    """Tests for ResourceState regeneration edge cases."""

    def test_regen_capped_at_max(self):
        """Regeneration doesn't exceed max_value."""
        state = ResourceState("energy", max_value=100.0, current_value=99.0, regen_rate=100.0)

        # Regen rate is 100 units per second, but we should cap at max
        state.update()

        assert state.current_value == 100.0  # Capped at max

    def test_regen_at_max_no_change(self):
        """No regen when already at max."""
        state = ResourceState("energy", max_value=100.0, current_value=100.0, regen_rate=10.0)

        state.update()

        assert state.current_value == 100.0

    def test_regen_zero_rate(self):
        """Zero regen rate means no regeneration."""
        state = ResourceState("ammo", max_value=50.0, current_value=20.0, regen_rate=0.0)

        state.update()

        assert state.current_value == 20.0


class TestResourceRegistryStorage:
    """Tests for ResourceRegistry storage registration."""

    def test_register_storage_additive(self):
        """Multiple register_storage calls sum up."""
        registry = ResourceRegistry()

        registry.register_storage("fuel", 100.0)
        registry.register_storage("fuel", 50.0)

        res = registry.get_resource("fuel")
        assert res.max_value == 150.0

    def test_register_storage_creates_new(self):
        """register_storage creates resource if not exists."""
        registry = ResourceRegistry()

        registry.register_storage("newres", 200.0)

        res = registry.get_resource("newres")
        assert res is not None
        assert res.max_value == 200.0


class TestResourceRegistrySetValue:
    """Tests for ResourceRegistry.set_value edge cases."""

    def test_set_value_at_max(self):
        """set_value(max) preserves exact max value."""
        registry = ResourceRegistry()
        registry.register_storage("fuel", 100.0)

        registry.set_value("fuel", 100.0)

        assert registry.get_value("fuel") == 100.0

    def test_set_value_above_max_clamped(self):
        """set_value above max is clamped to max."""
        registry = ResourceRegistry()
        registry.register_storage("fuel", 100.0)

        registry.set_value("fuel", 150.0)

        assert registry.get_value("fuel") == 100.0

    def test_set_value_nonexistent_resource(self):
        """set_value on nonexistent resource does nothing."""
        registry = ResourceRegistry()

        # Should not crash
        registry.set_value("missing", 50.0)

        assert registry.get_value("missing") == 0.0


class TestResourceRegistryResetStats:
    """Tests for ResourceRegistry.reset_stats behavior."""

    def test_reset_stats_preserves_current(self):
        """reset_stats zeroes max but keeps current value."""
        registry = ResourceRegistry()
        registry.register_storage("fuel", 100.0)
        registry.set_value("fuel", 75.0)

        registry.reset_stats()

        res = registry.get_resource("fuel")
        assert res.max_value == 0.0
        assert res.current_value == 75.0  # Preserved!
        assert res.regen_rate == 0.0

    def test_reset_stats_then_rebuild(self):
        """After reset, can rebuild stats with new values."""
        registry = ResourceRegistry()
        registry.register_storage("energy", 100.0)
        registry.register_generation("energy", 5.0)
        registry.set_value("energy", 80.0)

        registry.reset_stats()
        registry.register_storage("energy", 150.0)
        registry.register_generation("energy", 10.0)

        res = registry.get_resource("energy")
        assert res.max_value == 150.0
        assert res.regen_rate == 10.0
        assert res.current_value == 80.0  # Still preserved


class TestResourceRegistryModifyValue:
    """Tests for ResourceRegistry.modify_value edge cases."""

    def test_modify_value_negative_clamps_to_zero(self):
        """Negative modification doesn't go below 0."""
        registry = ResourceRegistry()
        registry.register_storage("ammo", 100.0)
        registry.set_value("ammo", 10.0)

        registry.modify_value("ammo", -50.0)

        assert registry.get_value("ammo") == 0.0

    def test_modify_value_positive_clamps_to_max(self):
        """Positive modification doesn't exceed max."""
        registry = ResourceRegistry()
        registry.register_storage("ammo", 100.0)
        registry.set_value("ammo", 90.0)

        registry.modify_value("ammo", 50.0)

        assert registry.get_value("ammo") == 100.0
