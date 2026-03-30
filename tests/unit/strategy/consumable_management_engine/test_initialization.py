"""
Tests for ConsumableManagementEngine initialization and ResourceDepletion dataclass.

PROJ-50: Updated to use strict DI (registries required).
"""

import pytest
from game.core.registry import GameRegistries
from game.core.exceptions import ValidationException


@pytest.fixture
def mock_registries():
    """Create minimal registries for testing."""
    return GameRegistries(
        components={},
        modifiers={},
        vehicle_classes={},
        resources={}
    )


class TestConsumableManagementEngineInit:
    """Tests for ConsumableManagementEngine initialization."""

    def test_engine_can_be_created(self, mock_registries):
        """ConsumableManagementEngine can be instantiated with registries."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = ConsumableManagementEngine(registries=mock_registries)

        assert engine is not None

    def test_engine_requires_registries(self):
        """ConsumableManagementEngine should require registries (strict DI)."""
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        # PROJ-50: Should raise ValidationException when registries is None
        with pytest.raises(ValidationException) as exc_info:
            ConsumableManagementEngine(registries=None)
        assert "registries is required" in str(exc_info.value)


class TestResourceDepletion:
    """Tests for ResourceDepletion dataclass."""

    def test_resource_depletion_can_be_created(self):
        """ResourceDepletion can be instantiated."""
        from game.strategy.engine.consumable_management_engine import ResourceDepletion

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
        from game.strategy.engine.consumable_management_engine import ResourceDepletion

        depletion = ResourceDepletion(
            ship_name="Test Ship",
            resource_type="fuel",
            components_disabled=[]
        )

        assert depletion.components_disabled == []
