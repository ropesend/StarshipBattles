"""Tests for ShipStatsCalculator PodStorage ability accumulation.

Phase 2: PodStorage is a mass-based ability on ship components that limits
how many drop pods (carried_items) a ship can hold. It follows the same
pattern as the planet StagingYard ability.
"""
import pytest

from game.core.registry import GameRegistries
from game.simulation.components.component import load_components_data, load_modifiers_data
from game.simulation.entities.ship_loader import load_vehicle_classes_data
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator


class TestShipStatsPodStorage:
    """Test ShipStatsCalculator pod_storage_mass aggregation."""

    @pytest.fixture
    def mock_registries(self):
        """Create GameRegistries with real component data."""
        minimal_registries = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
        return GameRegistries(
            components=load_components_data(registries=minimal_registries),
            modifiers=load_modifiers_data(),
            vehicle_classes=load_vehicle_classes_data(),
            resources={}
        )

    def test_pod_storage_mass_from_colony_pod_bay(self, mock_registries):
        """colony_pod_bay component should contribute pod_storage_mass."""
        design = {
            'ship_class': 'frigate',
            'layers': {
                'Infrastructure': [
                    {'id': 'colony_pod_bay', 'modifiers': []},
                ]
            }
        }

        service = ShipStatsCalculator(registries=mock_registries)
        stats = service.calculate_stats(design)

        assert 'pod_storage_mass' in stats
        assert stats['pod_storage_mass'] == 2000.0

    def test_pod_storage_mass_stacks_from_multiple_bays(self, mock_registries):
        """Multiple PodStorage components should sum their capacity_mass."""
        design = {
            'ship_class': 'frigate',
            'layers': {
                'Infrastructure': [
                    {'id': 'colony_pod_bay', 'modifiers': []},
                    {'id': 'colony_pod_bay', 'modifiers': []},
                ]
            }
        }

        service = ShipStatsCalculator(registries=mock_registries)
        stats = service.calculate_stats(design)

        assert stats['pod_storage_mass'] == 4000.0

    def test_pod_storage_mass_zero_when_no_bay(self, mock_registries):
        """Ships without PodStorage should have pod_storage_mass == 0."""
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

        assert stats.get('pod_storage_mass', 0) == 0

    def test_pod_storage_mass_degrades_with_damage(self, mock_registries):
        """Damaged PodStorage component should have reduced capacity."""
        design = {
            'ship_class': 'frigate',
            'layers': {
                'Infrastructure': [
                    {'id': 'colony_pod_bay', 'modifiers': []},
                ]
            }
        }

        # colony_pod_bay has max_hp=200. Set current_hp to 150 (75% health).
        # Effectiveness curve: linear degradation from 100% HP down to 30% threshold.
        component_damage = {'colony_pod_bay': 150}

        service = ShipStatsCalculator(registries=mock_registries)
        stats = service.calculate_stats(design, component_damage=component_damage)

        # Should be reduced (exact value depends on effectiveness curve)
        assert stats['pod_storage_mass'] < 2000.0
        assert stats['pod_storage_mass'] > 0
