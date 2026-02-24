"""
Tests for compute_planet_production utility function (BUG-86).

Verifies that the shared production calculation works with both
inline abilities and registry-lookup components.
"""
import pytest
from unittest.mock import Mock, patch


class TestComputePlanetProduction:
    """Tests for the shared compute_planet_production function."""

    def test_unowned_planet_returns_empty(self):
        """Unowned planets (owner_id=None) return empty dict."""
        from game.ui.panels.planet_report_panel import compute_planet_production

        planet = Mock()
        planet.owner_id = None

        result = compute_planet_production(planet)
        assert result == {}

    def test_planet_with_inline_harvester(self):
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

        result = compute_planet_production(planet)
        assert result['Metals'] == pytest.approx(80.0)  # 100.0 * 0.8

    def test_planet_with_registry_lookup(self):
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

        # PROJ-174: Mock registry provider (DI pattern)
        mock_provider = Mock()
        comp_def = Mock()
        comp_def.abilities = {
            'ResourceHarvester': {
                'resource_type': 'Metals',
                'base_harvest_rate': 100.0
            }
        }
        # The function calls provider.get_components() which returns a dict
        mock_provider.get_components.return_value = {'metal_harvester': comp_def}
        mock_provider.get_modifiers.return_value = {}
        mock_provider.get_vehicle_classes.return_value = {}
        mock_provider.get_resources.return_value = {}

        with patch('game.core.registry.get_default_registry_provider',
                   return_value=mock_provider):
            result = compute_planet_production(planet)

        assert result['Metals'] == pytest.approx(80.0)  # 100.0 * 0.8

    def test_planet_no_facilities_returns_empty(self):
        """Planet with no facilities returns empty rates."""
        from game.ui.panels.planet_report_panel import compute_planet_production

        planet = Mock()
        planet.owner_id = 1
        planet.facilities = []

        result = compute_planet_production(planet)
        assert result == {}

    def test_non_operational_facility_skipped(self):
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

        result = compute_planet_production(planet)
        assert result == {}
