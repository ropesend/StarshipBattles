"""
Tests for ShipValidator Dependency Injection (PROJ-50 Strict DI).

Tests that ClassRequirementsRule requires registries parameter (no fallback).
"""
import pytest
from unittest.mock import Mock

from game.simulation.validation.ship_validator import ClassRequirementsRule, ShipDesignValidator
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
        """ClassRequirementsRule should use injected registries."""
        rule = ClassRequirementsRule(registries=mock_registries)

        result = rule.validate(mock_ship)

        # Should complete without error using injected registries
        assert isinstance(result, ValidationResult)

    def test_class_requirements_rule_requires_registries(self):
        """PROJ-50: ClassRequirementsRule now requires registries parameter."""
        # Should raise TypeError when registries=None
        with pytest.raises(TypeError, match="registries is required"):
            ClassRequirementsRule(registries=None)

    def test_class_requirements_rule_stores_registries(self, mock_registries):
        """ClassRequirementsRule should store registries on instance."""
        rule = ClassRequirementsRule(registries=mock_registries)
        assert rule._registries is mock_registries


class TestShipDesignValidatorDI:
    """Tests for ShipDesignValidator dependency injection."""

    @pytest.fixture
    def mock_registries(self):
        """Create mock GameRegistries with vehicle_classes."""
        registries = Mock()
        registries.vehicle_classes = {
            "Cruiser": {
                "max_mass": 10000,
                "layers": [],
            },
        }
        return registries

    def test_ship_design_validator_requires_registries(self):
        """PROJ-50: ShipDesignValidator now requires registries parameter."""
        with pytest.raises(TypeError, match="registries is required"):
            ShipDesignValidator(registries=None)

    def test_ship_design_validator_accepts_registries(self, mock_registries):
        """ShipDesignValidator should accept registries parameter."""
        validator = ShipDesignValidator(registries=mock_registries)
        # Should complete without error
        assert validator is not None
