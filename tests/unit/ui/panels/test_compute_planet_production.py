"""
Tests for compute_planet_production utility function (BUG-86).

Verifies that the shared production calculation works with both
inline abilities and registry-lookup components.
"""
import pytest
from unittest.mock import Mock, patch


class TestComputePlanetProduction:
    """Tests for the shared compute_planet_production function."""

    def test_unowned_planet_returns_empty(self, mock_registries):
        """Unowned planets (owner_id=None) return empty dict."""
        from game.ui.panels.planet_report_panel import compute_planet_production

        planet = Mock()
        planet.owner_id = None

        result = compute_planet_production(planet, mock_registries)
        assert result == {}

    def test_planet_with_inline_harvester(self, mock_registries):
        """Planet with facility having inline ResourceHarvester abilities."""
        from game.ui.panels.planet_report_panel import compute_planet_production

        facility = Mock()
        facility.is_operational = True
        facility.design_data = {
            'layers': {
                'OUTER': [
                    {
                        'id': 'metal_harvester',
                        'abilities': {
                            'ResourceHarvester': {
                                'resource_type': 'Metals',
                                'base_harvest_rate': 100.0
                            }
                        }
                    }
                ]
            }
        }

        planet = Mock()
        planet.owner_id = 1
        planet.facilities = [facility]
        planet.resources = {'Metals': {'quality': 0.8, 'quantity': 5000}}

        result = compute_planet_production(planet, mock_registries)
        assert result['Metals'] == pytest.approx(80.0)  # 100.0 * 0.8

    def test_planet_with_registry_lookup(self, mock_registries):
        """Planet with facility using component IDs resolved via registry (BUG-86)."""
        from game.ui.panels.planet_report_panel import compute_planet_production

        # Facility with component ID but NO inline abilities (real design format)
        facility = Mock()
        facility.is_operational = True
        facility.design_data = {
            'layers': {
                'OUTER': [
                    {
                        'id': 'metal_harvester',
                        'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]
                    }
                ]
            }
        }

        planet = Mock()
        planet.owner_id = 1
        planet.facilities = [facility]
        planet.resources = {'Metals': {'quality': 0.8, 'quantity': 5000}}

        # PROJ-211: Set up registries with component definition
        comp_def = Mock()
        comp_def.abilities = {
            'ResourceHarvester': {
                'resource_type': 'Metals',
                'base_harvest_rate': 100.0
            }
        }
        mock_registries.components['metal_harvester'] = comp_def

        result = compute_planet_production(planet, mock_registries)

        assert result['Metals'] == pytest.approx(80.0)  # 100.0 * 0.8

    def test_planet_no_facilities_returns_empty(self, mock_registries):
        """Planet with no facilities returns empty rates."""
        from game.ui.panels.planet_report_panel import compute_planet_production

        planet = Mock()
        planet.owner_id = 1
        planet.facilities = []

        result = compute_planet_production(planet, mock_registries)
        assert result == {}

    def test_non_operational_facility_skipped(self, mock_registries):
        """Non-operational facilities are not counted."""
        from game.ui.panels.planet_report_panel import compute_planet_production

        facility = Mock()
        facility.is_operational = False
        facility.design_data = {
            'layers': {
                'OUTER': [
                    {
                        'id': 'metal_harvester',
                        'abilities': {
                            'ResourceHarvester': {
                                'resource_type': 'Metals',
                                'base_harvest_rate': 100.0
                            }
                        }
                    }
                ]
            }
        }

        planet = Mock()
        planet.owner_id = 1
        planet.facilities = [facility]
        planet.resources = {'Metals': {'quality': 0.8, 'quantity': 5000}}

        result = compute_planet_production(planet, mock_registries)
        assert result == {}
