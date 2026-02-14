"""Tests for ship detail panel functionality - PROJ-03 Phase 4."""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.ship_instance import ShipInstance


class TestShipInstanceDamageInfo:
    """Test cases for ShipInstance methods needed by detail panel."""

    @pytest.fixture
    def design_data(self):
        """Create design data with components for testing."""
        return {
            'name': 'Destroyer',
            'ship_class': 'Destroyer',
            'expected_stats': {
                'max_hp': 100,
                'mass': 500,
                'max_fuel': 100,
                'max_energy': 50,
            },
            'layers': {
                'CORE': [
                    {'id': 'reactor_standard'},
                    {'id': 'engine_basic'},
                ],
                'INNER': [
                    {'id': 'bridge_standard'},
                ],
                'OUTER': [
                    {'id': 'weapon_laser'},
                    {'id': 'weapon_missile'},
                ],
                'ARMOR': [
                    {'id': 'armor_plate'},
                ]
            }
        }

    def test_get_component_damage_summary_no_damage(self, design_data):
        """Ship with no damage should have empty damage summary."""
        instance = ShipInstance.create(design_data, owner_id=0)

        summary = instance.get_component_damage_summary()

        assert summary == {}

    def test_get_component_damage_summary_with_damage(self, design_data):
        """Ship with component damage should report it in summary."""
        instance = ShipInstance.create(design_data, owner_id=0)

        # Simulate damage to components
        instance.component_damage = {
            'reactor_standard_0': 50,  # 50 HP remaining
            'weapon_laser_0': 25,      # 25 HP remaining
        }

        summary = instance.get_component_damage_summary()

        assert 'reactor_standard_0' in summary
        assert 'weapon_laser_0' in summary
        assert summary['reactor_standard_0'] == 50
        assert summary['weapon_laser_0'] == 25

    def test_get_damaged_component_count(self, design_data):
        """Should count number of damaged components."""
        instance = ShipInstance.create(design_data, owner_id=0)

        assert instance.get_damaged_component_count() == 0

        instance.component_damage = {
            'reactor_standard_0': 50,
            'weapon_laser_0': 25,
            'armor_plate_0': 10,
        }

        assert instance.get_damaged_component_count() == 3

    def test_get_layer_damage_summary(self, design_data):
        """Should provide damage summary grouped by layer."""
        instance = ShipInstance.create(design_data, owner_id=0)

        # No damage - all layers should have 100% HP
        summary = instance.get_layer_damage_summary()

        # Even with no tracked damage, method should return empty dict
        # (we don't have layer info without converting to Ship)
        assert isinstance(summary, dict)


class TestShipInstanceDisplayMethods:
    """Test display-related methods for ShipInstance."""

    @pytest.fixture
    def design_data(self):
        return {
            'name': 'Cruiser',
            'expected_stats': {'max_hp': 200, 'mass': 1000},
        }

    def test_get_status_text_ok(self, design_data):
        """Healthy ship should return OK status."""
        instance = ShipInstance.create(design_data, owner_id=0)

        status = instance.get_status_text()

        assert status == "OK"

    def test_get_status_text_damaged(self, design_data):
        """Damaged ship should return DAMAGED status."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.current_hp = 150

        status = instance.get_status_text()

        assert status == "DAMAGED"

    def test_get_status_text_derelict(self, design_data):
        """Derelict ship should return DERELICT status."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.is_derelict = True

        status = instance.get_status_text()

        assert status == "DERELICT"

    def test_get_status_text_destroyed(self, design_data):
        """Destroyed ship should return DESTROYED status."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.is_alive = False

        status = instance.get_status_text()

        assert status == "DESTROYED"

    def test_get_hp_display_full(self, design_data):
        """Full HP ship should show max/max."""
        instance = ShipInstance.create(design_data, owner_id=0)

        display = instance.get_hp_display()

        assert display == "200/200"

    def test_get_hp_display_damaged(self, design_data):
        """Damaged ship should show current/max."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.current_hp = 150

        display = instance.get_hp_display()

        assert display == "150/200"

    def test_get_hp_display_destroyed(self, design_data):
        """Destroyed ship should show 0/max."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.is_alive = False
        instance.current_hp = 0

        display = instance.get_hp_display()

        assert display == "0/200"


class TestShipInstanceResourceDisplay:
    """Test resource display methods."""

    @pytest.fixture
    def design_data(self):
        return {
            'name': 'Tanker',
            'expected_stats': {
                'max_hp': 100,
                'resource_storage': {
                    'fuel': 500,
                    'energy': 200,
                    'ammo': 50,
                },
            },
        }

    def test_get_resource_display_full(self, design_data):
        """Full resources should show max/max."""
        instance = ShipInstance.create(design_data, owner_id=0)

        fuel_display = instance.get_resource_display('fuel')

        assert fuel_display == "500/500"

    def test_get_resource_display_partial(self, design_data):
        """Partial resources should show current/max."""
        instance = ShipInstance.create(design_data, owner_id=0)
        instance.resource_levels['fuel'] = 250

        fuel_display = instance.get_resource_display('fuel')

        assert fuel_display == "250/500"

    def test_get_resource_display_unknown_resource(self, design_data):
        """Unknown resource should return N/A."""
        instance = ShipInstance.create(design_data, owner_id=0)

        display = instance.get_resource_display('unknown_resource')

        assert display == "N/A"


class TestShipDetailPanelHelper:
    """Test helper functions for ship detail panel."""

    def test_get_damage_color_green(self):
        """High HP should return green color."""
        from game.ui.panels.ship_detail_panel import get_damage_color

        color = get_damage_color(1.0)  # 100%

        assert color == (100, 200, 100)  # Green

    def test_get_damage_color_yellow(self):
        """Medium HP should return yellow color."""
        from game.ui.panels.ship_detail_panel import get_damage_color

        color = get_damage_color(0.6)  # 60%

        assert color == (200, 200, 100)  # Yellow

    def test_get_damage_color_red(self):
        """Low HP should return red color."""
        from game.ui.panels.ship_detail_panel import get_damage_color

        color = get_damage_color(0.3)  # 30%

        assert color == (200, 100, 100)  # Red

    def test_get_damage_color_gray(self):
        """Destroyed (0 HP) should return gray color."""
        from game.ui.panels.ship_detail_panel import get_damage_color

        color = get_damage_color(0.0)  # 0%

        assert color == (100, 100, 100)  # Gray


class TestShipInstanceLayerInfo:
    """Test layer information extraction for component damage display."""

    @pytest.fixture
    def design_data_with_layers(self):
        """Design data with explicit layer structure."""
        return {
            'name': 'TestShip',
            'expected_stats': {'max_hp': 100},
            'layers': {
                'CORE': [
                    {'id': 'reactor_standard'},
                    {'id': 'engine_basic'},
                ],
                'INNER': [
                    {'id': 'bridge_standard'},
                ],
                'OUTER': [
                    {'id': 'weapon_laser'},
                ],
                'ARMOR': [
                    {'id': 'armor_plate'},
                ]
            }
        }

    def test_get_components_by_layer_from_design(self, design_data_with_layers):
        """Should extract component list grouped by layer from design data."""
        instance = ShipInstance.create(design_data_with_layers, owner_id=0)

        by_layer = instance.get_components_by_layer()

        assert 'CORE' in by_layer
        assert len(by_layer['CORE']) == 2
        assert by_layer['CORE'][0]['id'] == 'reactor_standard'
        assert 'INNER' in by_layer
        assert len(by_layer['INNER']) == 1
        assert 'OUTER' in by_layer
        assert 'ARMOR' in by_layer

    def test_get_components_by_layer_empty_layers(self):
        """Design without layers should return empty dict."""
        design_data = {
            'name': 'Simple',
            'expected_stats': {'max_hp': 50},
        }
        instance = ShipInstance.create(design_data, owner_id=0)

        by_layer = instance.get_components_by_layer()

        assert by_layer == {}

    def test_get_damaged_components_by_layer(self, design_data_with_layers):
        """Should extract only damaged components grouped by layer."""
        instance = ShipInstance.create(design_data_with_layers, owner_id=0)
        instance.component_damage = {
            'reactor_standard_0': 50,  # CORE layer
            'weapon_laser_0': 25,      # OUTER layer
        }

        damaged_by_layer = instance.get_damaged_components_by_layer()

        assert 'CORE' in damaged_by_layer
        assert len(damaged_by_layer['CORE']) == 1
        assert damaged_by_layer['CORE'][0] == ('reactor_standard_0', 50)
        assert 'OUTER' in damaged_by_layer
        assert len(damaged_by_layer['OUTER']) == 1
        assert 'INNER' not in damaged_by_layer  # No damaged components
        assert 'ARMOR' not in damaged_by_layer


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
