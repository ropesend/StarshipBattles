"""Tests for cargo_storage aggregation through the design-stats pipeline.

Validates that CargoStorage abilities are correctly aggregated by
cargo_type when a design is run through `calculate_design_stats`.
Acts as a data-integrity check on `data/components.json`
(passenger_quarters.capacity = 5000).

Migrated from the deleted strategy-layer `ShipStatsCalculator` tests
when PROJ-276 eradicated the dual-path calculator.
"""
import pytest

from game.core.registry import GameRegistries
from game.simulation.components.component import load_components_data, load_modifiers_data
from game.simulation.entities.ship_design_stats import calculate_design_stats
from game.simulation.entities.ship_loader import load_vehicle_classes_data


class TestCargoStorageAggregation:
    @pytest.fixture
    def mock_registries(self):
        minimal_registries = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
        return GameRegistries(
            components=load_components_data(registries=minimal_registries),
            modifiers=load_modifiers_data(),
            vehicle_classes=load_vehicle_classes_data(),
            resources={}
        )

    def test_cargo_storage_populated_from_passenger_quarters(self, mock_registries):
        # passenger_quarters has CrewRequired: 10 — pair it with a
        # crew_quarters (CrewCapacity: 10) so the simulation layer's
        # Phase 2 crew allocation leaves the component active.
        design = {
            'ship_class': 'frigate',
            'layers': {
                'CORE': [
                    {'id': 'crew_quarters', 'modifiers': []},
                    {'id': 'passenger_quarters', 'modifiers': []},
                ]
            }
        }

        stats = calculate_design_stats(design, mock_registries)

        assert 'cargo_storage' in stats
        assert isinstance(stats['cargo_storage'], dict)
        assert 'passengers' in stats['cargo_storage']
        assert stats['cargo_storage']['passengers'] == 5000.0

    def test_cargo_storage_sums_multiple_components(self, mock_registries):
        # 2 passenger_quarters × 10 crew each = 20 crew required.
        # Provide 2 crew_quarters (10 each) to satisfy.
        design = {
            'ship_class': 'frigate',
            'layers': {
                'CORE': [
                    {'id': 'crew_quarters', 'modifiers': []},
                    {'id': 'crew_quarters', 'modifiers': []},
                    {'id': 'passenger_quarters', 'modifiers': []},
                    {'id': 'passenger_quarters', 'modifiers': []},
                ]
            }
        }

        stats = calculate_design_stats(design, mock_registries)

        assert stats['cargo_storage']['passengers'] == 10000.0
