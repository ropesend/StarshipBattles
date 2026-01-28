"""
Tests for ShipValidator Dependency Injection (PROJ-38 Phase 5).

Tests that ClassRequirementsRule accepts registries parameter for DI.
"""
import pytest
from unittest.mock import Mock, patch

from game.simulation.ship_validator import ClassRequirementsRule
from game.simulation.validation.base import ValidationResult


class TestClassRequirementsRuleDI:
    """Tests for ClassRequirementsRule dependency injection."""

    @pytest.fixture
    def mock_ship(self):
        """Create a mock ship for testing."""
        ship = Mock()
        ship.ship_class = "Cruiser"
        ship.get_all_components.return_value = []
        return ship

    @pytest.fixture
    def mock_registries(self):
        """Create mock GameRegistries with vehicle_classes."""
        registries = Mock()
        registries.vehicle_classes = {
            "Cruiser": {
                "max_mass": 10000,
                "layers": [],
            },
            "Escort": {
                "max_mass": 5000,
                "layers": [],
            },
        }
        return registries

    def test_class_requirements_rule_accepts_registries_parameter(self):
        """ClassRequirementsRule.__init__() should accept registries parameter."""
        mock_registries = Mock()
        mock_registries.vehicle_classes = {}

        # Should not raise - registries parameter accepted
        rule = ClassRequirementsRule(registries=mock_registries)
        assert rule._registries is mock_registries

    def test_class_requirements_rule_uses_injected_registries(self, mock_ship, mock_registries):
        """ClassRequirementsRule should use injected registries when provided."""
        rule = ClassRequirementsRule(registries=mock_registries)

        with patch('game.simulation.ship_validator.get_vehicle_classes') as mock_get_classes:
            mock_get_classes.return_value = {}  # Should not be used

            result = rule.validate(mock_ship)

            # Global function should NOT be called when registries provided
            mock_get_classes.assert_not_called()

    def test_class_requirements_rule_falls_back_to_global(self, mock_ship):
        """ClassRequirementsRule should use global function when no registries."""
        rule = ClassRequirementsRule()  # No registries parameter

        with patch('game.simulation.ship_validator.get_vehicle_classes') as mock_get_classes:
            mock_get_classes.return_value = {
                "Cruiser": {"max_mass": 10000}
            }

            result = rule.validate(mock_ship)

            # Global function SHOULD be called when no registries
            mock_get_classes.assert_called_once()

    def test_class_requirements_rule_stores_registries(self, mock_registries):
        """ClassRequirementsRule should store registries on instance."""
        rule = ClassRequirementsRule(registries=mock_registries)
        assert rule._registries is mock_registries

    def test_class_requirements_rule_none_registries_uses_fallback(self, mock_ship):
        """ClassRequirementsRule with registries=None should use global fallback."""
        rule = ClassRequirementsRule(registries=None)

        with patch('game.simulation.ship_validator.get_vehicle_classes') as mock_get_classes:
            mock_get_classes.return_value = {
                "Cruiser": {"max_mass": 10000}
            }

            result = rule.validate(mock_ship)

            # Global function should be called when registries=None
            mock_get_classes.assert_called_once()
