"""
Validator rules for the Maintenance abstraction (QA Observation 5).

Two new design-time rules replace the old crew-required-vs-crew-capacity check:

1. Crew-needs-LS hard rule: if a design declares CrewCapacity > 0 and
   LifeSupportCapacity < CrewCapacity, REJECT at design time. No silent
   runtime degradation.

2. Maintenance rule: if RequiresMaintenance (summed across components) >
   ProvidesMaintenance, REJECT with a clear error.
"""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game.simulation.validation.ship_validator import ClassRequirementsRule


@pytest.fixture
def mock_registries():
    registries = Mock()
    registries.vehicle_classes = {"Cruiser": {"max_mass": 10000}}
    return registries


@pytest.fixture
def mock_ship():
    ship = Mock()
    ship.ship_class = "Cruiser"
    ship.get_all_components.return_value = []
    return ship


class TestCrewNeedsLifeSupportRule:
    """When CrewCapacity > LifeSupportCapacity, validator rejects with explicit error."""

    def test_crew_without_life_support_rejects(self, mock_registries, mock_ship):
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "CrewCapacity": 10,
                "LifeSupportCapacity": 0,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            assert not result.is_valid
            # Error must mention both numbers and the crew/life-support relationship.
            joined = " ".join(result.errors).lower()
            assert "10" in joined
            assert "life support" in joined
            assert "crew" in joined

    def test_crew_with_insufficient_life_support_rejects(self, mock_registries, mock_ship):
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "CrewCapacity": 10,
                "LifeSupportCapacity": 5,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            assert not result.is_valid
            joined = " ".join(result.errors).lower()
            assert "10" in joined and "5" in joined

    def test_crew_matched_by_life_support_passes(self, mock_registries, mock_ship):
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "CrewCapacity": 10,
                "LifeSupportCapacity": 25,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            # No crew-LS error
            joined = " ".join(result.errors).lower()
            assert "life support" not in joined or "crew" not in joined

    def test_zero_crew_zero_life_support_passes(self, mock_registries, mock_ship):
        """A crewless design (e.g. mine) doesn't need life support."""
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "CrewCapacity": 0,
                "LifeSupportCapacity": 0,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            joined = " ".join(result.errors).lower()
            assert "crew" not in joined


class TestMaintenanceRule:
    """RequiresMaintenance total must be covered by ProvidesMaintenance total."""

    def test_insufficient_maintenance_rejects(self, mock_registries, mock_ship):
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "RequiresMaintenance": 10,
                "ProvidesMaintenance": 3,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            assert not result.is_valid
            joined = " ".join(result.errors).lower()
            assert "maintenance" in joined
            # Error should mention both numbers
            assert "10" in joined and "3" in joined

    def test_exactly_enough_maintenance_passes(self, mock_registries, mock_ship):
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "RequiresMaintenance": 10,
                "ProvidesMaintenance": 10,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            joined = " ".join(result.errors).lower()
            assert "maintenance" not in joined

    def test_zero_requires_passes(self, mock_registries, mock_ship):
        """A design with no maintenance-consuming components needs no maintenance providers."""
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "RequiresMaintenance": 0,
                "ProvidesMaintenance": 0,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            joined = " ".join(result.errors).lower()
            assert "maintenance" not in joined

    def test_excess_maintenance_passes(self, mock_registries, mock_ship):
        with patch("game.simulation.entities.ship_stats.ShipStatsCalculator") as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                "RequiresMaintenance": 5,
                "ProvidesMaintenance": 25,
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            joined = " ".join(result.errors).lower()
            assert "maintenance" not in joined
