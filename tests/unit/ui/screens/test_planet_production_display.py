"""Tests for planet production display calculation.

BUG-78: Production values were displaying as 0 because compute_planet_production
only checked inline abilities in design_data, not the component registry.
"""
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, field
from typing import Dict, Any, List

from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter


@dataclass
class MockFacility:
    """Minimal facility for testing production calculation."""
    design_data: Dict[str, Any]
    is_operational: bool = True


@dataclass
class MockPlanet:
    """Minimal planet for testing production calculation."""
    owner_id: int = 0
    resources: Dict[str, dict] = field(default_factory=dict)
    facilities: List = field(default_factory=list)


class TestComputePlanetProduction:
    """Tests for StrategyDetailFormatter.compute_planet_production."""

    @pytest.fixture
    def formatter(self):
        """Create a minimal StrategyDetailFormatter for testing."""
        formatter = StrategyDetailFormatter.__new__(StrategyDetailFormatter)
        formatter.scene = MagicMock()
        return formatter

    def test_returns_empty_for_unowned_planet(self, formatter):
        """Unowned planet returns empty production rates."""
        planet = MockPlanet(owner_id=None)
        result = formatter.compute_planet_production(planet)
        assert result == {}

    def test_inline_abilities_still_work(self, formatter):
        """Components with inline abilities are still detected."""
        facility = MockFacility(design_data={
            'layers': {
                'OUTER': [{
                    'id': 'test_harvester',
                    'abilities': {
                        'ResourceHarvester': {
                            'resource_type': 'Metals',
                            'base_harvest_rate': 100.0
                        }
                    }
                }]
            }
        })
        planet = MockPlanet(
            owner_id=0,
            resources={'Metals': {'quantity': 5000, 'quality': 0.8}},
            facilities=[facility]
        )

        result = formatter.compute_planet_production(planet)
        assert result['Metals'] == pytest.approx(80.0)  # 100 * 0.8

    def test_registry_lookup_finds_harvester(self, formatter):
        """Components looked up via registry detect harvester abilities (BUG-78 fix)."""
        # Facility with component ID only (no inline abilities) - typical real data
        facility = MockFacility(design_data={
            'layers': {
                'OUTER': [{
                    'id': 'metal_harvester',
                    'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]
                }]
            }
        })
        planet = MockPlanet(
            owner_id=0,
            resources={'Metals': {'quantity': 5000, 'quality': 0.8}},
            facilities=[facility]
        )

        # Mock the registry to return a component with ResourceHarvester ability
        mock_comp_def = MagicMock()
        mock_comp_def.abilities = {
            'ResourceHarvester': {
                'resource_type': 'Metals',
                'base_harvest_rate': 100.0
            }
        }
        mock_registries = MagicMock()
        mock_registries.components.get.return_value = mock_comp_def

        with patch('game.core.registry.get_default_registries',
                   return_value=mock_registries):
            result = formatter.compute_planet_production(planet)

        assert 'Metals' in result
        assert result['Metals'] == pytest.approx(80.0)  # 100 * 0.8

    def test_non_operational_facility_skipped(self, formatter):
        """Non-operational facilities are excluded from production."""
        facility = MockFacility(
            design_data={
                'layers': {
                    'OUTER': [{
                        'id': 'test_harvester',
                        'abilities': {
                            'ResourceHarvester': {
                                'resource_type': 'Metals',
                                'base_harvest_rate': 100.0
                            }
                        }
                    }]
                }
            },
            is_operational=False
        )
        planet = MockPlanet(
            owner_id=0,
            resources={'Metals': {'quantity': 5000, 'quality': 0.8}},
            facilities=[facility]
        )

        result = formatter.compute_planet_production(planet)
        assert result == {}

    def test_zero_quality_produces_zero(self, formatter):
        """Planet with zero resource quality produces zero."""
        facility = MockFacility(design_data={
            'layers': {
                'OUTER': [{
                    'id': 'test_harvester',
                    'abilities': {
                        'ResourceHarvester': {
                            'resource_type': 'Metals',
                            'base_harvest_rate': 100.0
                        }
                    }
                }]
            }
        })
        planet = MockPlanet(
            owner_id=0,
            resources={'Metals': {'quantity': 5000, 'quality': 0.0}},
            facilities=[facility]
        )

        result = formatter.compute_planet_production(planet)
        # quality=0 means rate*0 = 0, so Metals shouldn't appear (base_rate * 0 = 0 is not > 0)
        assert result.get('Metals', 0.0) == pytest.approx(0.0)
