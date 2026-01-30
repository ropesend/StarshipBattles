"""
Tests for ResourceManagementEngine initialization and ResourceDepletion dataclass.
"""

import pytest


class TestResourceManagementEngineInit:
    """Tests for ResourceManagementEngine initialization."""

    def test_engine_can_be_created(self):
        """ResourceManagementEngine can be instantiated."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

        assert engine is not None

    def test_engine_is_stateless(self):
        """ResourceManagementEngine should be stateless."""
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = ResourceManagementEngine()

        # Engine should have no significant state
        # (no instance variables beyond methods)
        assert not hasattr(engine, '_state') or engine._state is None


class TestResourceDepletion:
    """Tests for ResourceDepletion dataclass."""

    def test_resource_depletion_can_be_created(self):
        """ResourceDepletion can be instantiated."""
        from game.strategy.engine.resource_management_engine import ResourceDepletion

        depletion = ResourceDepletion(
            ship_name="Test Ship",
            resource_type="power",
            components_disabled=["reactor_01"]
        )

        assert depletion.ship_name == "Test Ship"
        assert depletion.resource_type == "power"
        assert depletion.components_disabled == ["reactor_01"]

    def test_resource_depletion_empty_components(self):
        """ResourceDepletion with no components disabled."""
        from game.strategy.engine.resource_management_engine import ResourceDepletion

        depletion = ResourceDepletion(
            ship_name="Test Ship",
            resource_type="fuel",
            components_disabled=[]
        )

        assert depletion.components_disabled == []
