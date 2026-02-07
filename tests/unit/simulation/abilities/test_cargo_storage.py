"""
Tests for CargoStorage ability.

PROJ-68 Phase 4: Cargo Ability Layer
"""

import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities import CargoStorage, create_ability, ABILITY_REGISTRY
from game.simulation.components.abilities.cargo import CargoStorage as CargoStorageClass


class TestCargoStorageCreation:
    """Test CargoStorage ability creation."""

    def test_cargo_storage_creation_dict_format(self):
        """CargoStorage handles dict format with cargo_type and capacity."""
        component = MagicMock()
        data = {"cargo_type": "passengers", "capacity": 5000}

        ability = CargoStorage(component, data)

        assert ability.cargo_type == "passengers"
        assert ability.capacity == 5000.0
        assert ability._base_capacity == 5000.0

    def test_cargo_storage_creation_scalar_format(self):
        """CargoStorage handles scalar format, defaults to generic cargo_type."""
        component = MagicMock()
        data = 3000

        ability = CargoStorage(component, data)

        assert ability.cargo_type == "generic"
        assert ability.capacity == 3000.0
        assert ability._base_capacity == 3000.0

    def test_cargo_storage_creation_float_scalar(self):
        """CargoStorage handles float scalar format."""
        component = MagicMock()
        data = 2500.5

        ability = CargoStorage(component, data)

        assert ability.cargo_type == "generic"
        assert ability.capacity == 2500.5

    def test_cargo_storage_creation_empty_dict(self):
        """CargoStorage handles empty dict with defaults."""
        component = MagicMock()
        data = {}

        ability = CargoStorage(component, data)

        assert ability.cargo_type == "generic"
        assert ability.capacity == 0.0

    def test_cargo_storage_creation_invalid_data(self):
        """CargoStorage handles invalid data gracefully."""
        component = MagicMock()
        data = "invalid"

        ability = CargoStorage(component, data)

        assert ability.cargo_type == "generic"
        assert ability.capacity == 0.0


class TestCargoStorageSyncData:
    """Test CargoStorage sync_data method."""

    def test_cargo_storage_sync_data_dict(self):
        """sync_data updates from dict format."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 1000})

        ability.sync_data({"cargo_type": "goods", "capacity": 2000})

        assert ability.cargo_type == "goods"
        assert ability.capacity == 2000.0
        assert ability._base_capacity == 2000.0

    def test_cargo_storage_sync_data_scalar(self):
        """sync_data updates from scalar format, preserves cargo_type."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 1000})

        ability.sync_data(3000)

        # cargo_type preserved, capacity updated
        assert ability.cargo_type == "passengers"
        assert ability.capacity == 3000.0
        assert ability._base_capacity == 3000.0

    def test_cargo_storage_sync_data_partial_dict(self):
        """sync_data with partial dict preserves unspecified fields."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 1000})

        ability.sync_data({"capacity": 5000})

        assert ability.cargo_type == "passengers"  # preserved
        assert ability.capacity == 5000.0


class TestCargoStorageRecalculate:
    """Test CargoStorage recalculate method."""

    def test_cargo_storage_recalculate_with_modifier(self):
        """recalculate applies stat modifiers to capacity."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 1000})

        # Mock get_effective_stat to return 1.5 multiplier
        ability.get_effective_stat = MagicMock(return_value=1.5)

        ability.recalculate()

        assert ability.capacity == 1500.0
        ability.get_effective_stat.assert_called_with('capacity_mult', 1.0)

    def test_cargo_storage_recalculate_no_modifier(self):
        """recalculate with no modifier keeps base capacity."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 2000})

        ability.get_effective_stat = MagicMock(return_value=1.0)

        ability.recalculate()

        assert ability.capacity == 2000.0


class TestCargoStorageUIRows:
    """Test CargoStorage get_ui_rows method."""

    def test_cargo_storage_ui_rows_passengers(self):
        """get_ui_rows returns passenger-styled row."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 5000})

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Passenger Cap'
        assert rows[0]['value'] == '5000'
        assert rows[0]['color_hint'] == '#98FB98'  # Pale green

    def test_cargo_storage_ui_rows_generic(self):
        """get_ui_rows returns generic-styled row."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "goods", "capacity": 3000})

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Goods Cap'
        assert rows[0]['value'] == '3000'
        assert rows[0]['color_hint'] == '#FFD700'  # Gold


class TestCargoStoragePrimaryValue:
    """Test CargoStorage get_primary_value method."""

    def test_cargo_storage_primary_value(self):
        """get_primary_value returns capacity."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 7500})

        assert ability.get_primary_value() == 7500.0


class TestCargoStorageRegistry:
    """Test CargoStorage registry integration."""

    def test_cargo_storage_in_registry(self):
        """CargoStorage is registered in ABILITY_REGISTRY."""
        assert "CargoStorage" in ABILITY_REGISTRY
        assert ABILITY_REGISTRY["CargoStorage"] is CargoStorageClass

    def test_cargo_storage_registry_creation(self):
        """create_ability creates CargoStorage from registry."""
        component = MagicMock()
        data = {"cargo_type": "passengers", "capacity": 4000}

        ability = create_ability("CargoStorage", component, data)

        assert ability is not None
        assert isinstance(ability, CargoStorage)
        assert ability.cargo_type == "passengers"
        assert ability.capacity == 4000.0


class TestCargoStorageLayer:
    """Test CargoStorage layer attribute."""

    def test_cargo_storage_layer_strategic(self):
        """CargoStorage has strategic layer."""
        component = MagicMock()
        ability = CargoStorage(component, {"cargo_type": "passengers", "capacity": 1000})

        assert ability.layer == 'strategic'


class TestShipStatsCargoStorage:
    """Test ShipStatsCalculator cargo_storage aggregation."""

    @pytest.fixture
    def mock_registries(self):
        """Create mock GameRegistries for testing."""
        from game.core.registry import GameRegistries
        from game.simulation.components.component import load_components_data, load_modifiers_data
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        return GameRegistries(
            components=load_components_data(),
            modifiers=load_modifiers_data(),
            vehicle_classes=load_vehicle_classes_data(),
            resources={}
        )

    def test_ship_stats_includes_cargo_storage(self, mock_registries):
        """ShipStatsCalculator aggregates CargoStorage abilities by cargo_type."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

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
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

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


class TestPassengerQuartersComponent:
    """Test passenger_quarters component from components.json."""

    def test_passenger_quarters_component_loads(self):
        """passenger_quarters component loads from components.json."""
        from game.simulation.components.component import load_components_data

        components = load_components_data()
        component = components.get('passenger_quarters')

        assert component is not None
        assert component.name == 'Passenger Quarters'
        assert component.type_str == 'Infrastructure'
        assert component.mass == 200
        assert component.max_hp == 150

    def test_passenger_quarters_has_cargo_storage_ability(self):
        """passenger_quarters has CargoStorage ability with correct data."""
        from game.simulation.components.component import load_components_data

        components = load_components_data()
        component = components.get('passenger_quarters')

        abilities = component.abilities
        assert 'CargoStorage' in abilities

        cargo_data = abilities['CargoStorage']
        assert cargo_data['cargo_type'] == 'passengers'
        assert cargo_data['capacity'] == 5000

    def test_passenger_quarters_has_life_support(self):
        """passenger_quarters has LifeSupportCapacity ability."""
        from game.simulation.components.component import load_components_data

        components = load_components_data()
        component = components.get('passenger_quarters')

        abilities = component.abilities
        assert 'LifeSupportCapacity' in abilities
        assert abilities['LifeSupportCapacity'] == 5000

    def test_passenger_quarters_requires_crew(self):
        """passenger_quarters has CrewRequired ability."""
        from game.simulation.components.component import load_components_data

        components = load_components_data()
        component = components.get('passenger_quarters')

        abilities = component.abilities
        assert 'CrewRequired' in abilities
        assert abilities['CrewRequired'] == 10
