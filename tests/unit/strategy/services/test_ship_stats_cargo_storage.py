"""Tests for ShipStatsCalculator cargo_storage aggregation.

Moved from tests/unit/simulation/abilities/test_cargo_storage.py
to respect layer boundaries: ShipStatsCalculator is strategy-layer code.
"""
import pytest

from game.core.registry import GameRegistries
from game.simulation.components.component import load_components_data, load_modifiers_data
from game.simulation.entities.ship_loader import load_vehicle_classes_data
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator


class TestShipStatsCargoStorage:
    """Test ShipStatsCalculator cargo_storage aggregation."""

    @pytest.fixture
    def mock_registries(self):
        """Create mock GameRegistries for testing."""
        minimal_registries = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
        return GameRegistries(
            components=load_components_data(registries=minimal_registries),
            modifiers=load_modifiers_data(),
            vehicle_classes=load_vehicle_classes_data(),
            resources={}
        )

    def test_ship_stats_includes_cargo_storage(self, mock_registries):
        """ShipStatsCalculator aggregates CargoStorage abilities by cargo_type."""
        # Design with passenger_quarters component
        design = {
            'ship_class': 'frigate',
            'layers': {
                'Infrastructure': [
                    {'id': 'passenger_quarters', 'modifiers': []},
                ]
            }
        }

        service = ShipStatsCalculator(registries=mock_registries)
        stats = service.calculate_stats(design)

        assert 'cargo_storage' in stats
        assert isinstance(stats['cargo_storage'], dict)
        assert 'passengers' in stats['cargo_storage']
        assert stats['cargo_storage']['passengers'] == 5000.0

    def test_ship_stats_cargo_storage_multiple_components(self, mock_registries):
        """ShipStatsCalculator sums cargo storage from multiple components."""
        # Design with two passenger_quarters components
        design = {
            'ship_class': 'frigate',
            'layers': {
                'Infrastructure': [
                    {'id': 'passenger_quarters', 'modifiers': []},
                    {'id': 'passenger_quarters', 'modifiers': []},
                ]
            }
        }

        service = ShipStatsCalculator(registries=mock_registries)
        stats = service.calculate_stats(design)

        assert stats['cargo_storage']['passengers'] == 10000.0
