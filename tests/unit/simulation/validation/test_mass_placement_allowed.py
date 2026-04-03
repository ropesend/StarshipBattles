"""Tests for allowing component placement over mass limits.

Components should be placeable even when they exceed mass budgets.
The mass violation is tracked via ship.mass_limits_ok and shown as a warning,
but does not prevent placement.
"""
import pytest
from game.simulation.components.component import create_component
from game.simulation.entities.ship import Ship
from game.core.constants import LayerType


class TestMassPlacementAllowed:
    """Verify that components can be placed even when over mass budget."""

    def test_component_added_when_over_ship_mass(self, fresh_registries):
        """Component should be accepted even when it exceeds ship mass budget."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries,
                     ship_class="Escort")  # Small ship with low mass budget

        # Add many heavy components to exceed mass
        comp = create_component('railgun', registries=fresh_registries)
        added = ship.add_component(comp, LayerType.OUTER)
        assert added is True

        # Keep adding until we're over budget
        for _ in range(20):
            comp = create_component('railgun', registries=fresh_registries)
            result = ship.add_component(comp, LayerType.OUTER)
            # Should always succeed (mass is not a placement blocker)
            assert result is True

        # Ship should be over mass budget
        assert ship.mass > ship.max_mass_budget
        assert ship.mass_limits_ok is False

    def test_mass_limits_ok_false_when_over_budget(self, fresh_registries):
        """mass_limits_ok should be False when ship exceeds mass budget."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries,
                     ship_class="Escort")

        # Add components until over budget
        for _ in range(20):
            comp = create_component('railgun', registries=fresh_registries)
            ship.add_component(comp, LayerType.OUTER)

        assert ship.mass_limits_ok is False

    def test_mass_limits_ok_true_when_under_budget(self, fresh_registries):
        """mass_limits_ok should be True when ship is under mass budget."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries,
                     ship_class="Dreadnought")  # Large ship

        comp = create_component('railgun', registries=fresh_registries)
        ship.add_component(comp, LayerType.OUTER)

        assert ship.mass_limits_ok is True

    def test_non_mass_validation_still_blocks(self, fresh_registries):
        """Other validation rules (vehicle type, unique, etc.) should still block."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries,
                     ship_class="Escort")

        # Try to add a component not allowed on this vehicle type
        comp = create_component('metal_harvester', registries=fresh_registries)
        result = ship.add_component(comp, LayerType.CORE)

        # Should be rejected by LayerConstraintRule (not allowed on Ship type)
        assert result is False

    def test_bulk_add_continues_past_mass_limit(self, fresh_registries):
        """add_components_bulk should keep adding past mass limit."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries,
                     ship_class="Escort")

        comp = create_component('railgun', registries=fresh_registries)
        added = ship.add_components_bulk(comp, LayerType.OUTER, 30)

        # All 30 should be added (mass doesn't block)
        assert added == 30
        assert ship.mass_limits_ok is False


class TestMassValidInSerialization:
    """Verify mass_valid is stored in expected_stats during serialization."""

    def test_to_dict_includes_mass_valid_true(self, fresh_registries):
        """Serialized ship should include mass_valid=True when under budget."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries,
                     ship_class="Dreadnought")
        comp = create_component('railgun', registries=fresh_registries)
        ship.add_component(comp, LayerType.OUTER)

        data = ship.to_dict()
        assert data["expected_stats"]["mass_valid"] is True

    def test_to_dict_includes_mass_valid_false(self, fresh_registries):
        """Serialized ship should include mass_valid=False when over budget."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries,
                     ship_class="Escort")

        for _ in range(20):
            comp = create_component('railgun', registries=fresh_registries)
            ship.add_component(comp, LayerType.OUTER)

        data = ship.to_dict()
        assert data["expected_stats"]["mass_valid"] is False
