"""Tests for ship detail panel functionality - PROJ-03 Phase 4."""
import pytest
from unittest.mock import MagicMock, patch

from game.core.component_state import ComponentState, component_state_key
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

    def test_get_damaged_component_count(self, design_data, ship_factory):
        """Should count number of damaged component instances."""
        instance = ship_factory(design_data, owner_id=0)

        assert instance.get_damaged_component_count() == 0

        # Drop three specific instances below full HP.
        def _damage(cid: str, idx: int, current: float) -> None:
            key = component_state_key(cid, idx)
            cs = instance.components.get(key)
            if cs is None:
                # Design-driven tests may start with empty components dict
                # if the ship_factory short-circuits stat initialization —
                # populate directly with synthetic max_hp.
                instance.components[key] = ComponentState(
                    component_id=cid, instance_index=idx,
                    current_hp=current, max_hp=100.0,
                )
            else:
                cs.current_hp = current

        _damage('reactor_standard', 0, 50)
        _damage('weapon_laser', 0, 25)
        _damage('armor_plate', 0, 10)

        assert instance.get_damaged_component_count() == 3

class TestShipInstanceDisplayMethods:
    """Test display-related methods for ShipInstance."""

    @pytest.fixture
    def design_data(self):
        return {
            'name': 'Cruiser',
            'expected_stats': {'max_hp': 200, 'mass': 1000},
        }

    def test_get_status_text_ok(self, design_data, ship_factory):
        """Healthy ship should return OK status."""
        instance = ship_factory(design_data, owner_id=0)

        status = instance.get_status_text()

        assert status == "OK"

    def test_get_status_text_damaged(self, design_data, ship_factory):
        """Damaged ship should return DAMAGED status."""
        instance = ship_factory(design_data, owner_id=0)
        instance.current_hp = 150

        status = instance.get_status_text()

        assert status == "DAMAGED"

    def test_get_status_text_derelict(self, design_data, ship_factory):
        """Derelict ship should return DERELICT status."""
        instance = ship_factory(design_data, owner_id=0)
        instance.is_derelict = True

        status = instance.get_status_text()

        assert status == "DERELICT"

    def test_get_status_text_destroyed(self, design_data, ship_factory):
        """Destroyed ship should return DESTROYED status."""
        instance = ship_factory(design_data, owner_id=0)
        instance.is_alive = False

        status = instance.get_status_text()

        assert status == "DESTROYED"

    def test_get_hp_display_full(self, design_data, ship_factory):
        """Full HP ship should show max/max."""
        instance = ship_factory(design_data, owner_id=0)

        display = instance.get_hp_display()

        assert display == "200/200"

    def test_get_hp_display_damaged(self, design_data, ship_factory):
        """Damaged ship should show current/max."""
        instance = ship_factory(design_data, owner_id=0)
        instance.current_hp = 150

        display = instance.get_hp_display()

        assert display == "150/200"

    def test_get_hp_display_destroyed(self, design_data, ship_factory):
        """Destroyed ship should show 0/max."""
        instance = ship_factory(design_data, owner_id=0)
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

    def test_get_resource_display_full(self, design_data, ship_factory):
        """Full resources should show max/max."""
        instance = ship_factory(design_data, owner_id=0)

        fuel_display = instance.get_resource_display('fuel')

        assert fuel_display == "500/500"

    def test_get_resource_display_partial(self, design_data, ship_factory):
        """Partial resources should show current/max."""
        instance = ship_factory(design_data, owner_id=0)
        instance.consumable_levels['fuel'] = 250

        fuel_display = instance.get_resource_display('fuel')

        assert fuel_display == "250/500"

    def test_get_resource_display_unknown_resource(self, design_data, ship_factory):
        """Unknown resource should return N/A."""
        instance = ship_factory(design_data, owner_id=0)

        display = instance.get_resource_display('unknown_resource')

        assert display == "N/A"


class TestShipDetailPanelHelper:
    """Test helper functions for ship detail panel."""

    def test_get_damage_color_green(self):
        """High HP should return green color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_HEALTHY

        color = get_damage_color(1.0)  # 100%

        assert color == HP_HEALTHY

    def test_get_damage_color_yellow(self):
        """Medium HP (25-49%) should return yellow color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_DAMAGED

        color = get_damage_color(0.35)  # 35%

        assert color == HP_DAMAGED

    def test_get_damage_color_red(self):
        """Low HP (<25%) should return red color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_CRITICAL

        color = get_damage_color(0.15)  # 15%

        assert color == HP_CRITICAL

    def test_get_damage_color_gray(self):
        """Destroyed (0 HP) should return gray color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_DESTROYED

        color = get_damage_color(0.0)  # 0%

        assert color == HP_DESTROYED


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

    def test_get_components_by_layer_from_design(self, design_data_with_layers, ship_factory):
        """Should extract component list grouped by layer from design data."""
        instance = ship_factory(design_data_with_layers, owner_id=0)

        by_layer = instance.get_components_by_layer()

        assert 'CORE' in by_layer
        assert len(by_layer['CORE']) == 2
        assert by_layer['CORE'][0]['id'] == 'reactor_standard'
        assert 'INNER' in by_layer
        assert len(by_layer['INNER']) == 1
        assert 'OUTER' in by_layer
        assert 'ARMOR' in by_layer

    def test_get_components_by_layer_empty_layers(self, ship_factory):
        """Design without layers should return empty dict."""
        design_data = {
            'name': 'Simple',
            'expected_stats': {'max_hp': 50},
        }
        instance = ship_factory(design_data, owner_id=0)

        by_layer = instance.get_components_by_layer()

        assert by_layer == {}

    def test_get_damaged_components_by_layer(self, design_data_with_layers, ship_factory):
        """Should extract only damaged components grouped by layer."""
        instance = ship_factory(design_data_with_layers, owner_id=0)
        # Seed per-instance state for the two components we want to damage.
        instance.components[component_state_key('reactor_standard', 0)] = ComponentState(
            component_id='reactor_standard', instance_index=0,
            current_hp=50.0, max_hp=100.0,
        )
        instance.components[component_state_key('weapon_laser', 0)] = ComponentState(
            component_id='weapon_laser', instance_index=0,
            current_hp=25.0, max_hp=100.0,
        )

        damaged_by_layer = instance.get_damaged_components_by_layer()

        assert 'CORE' in damaged_by_layer
        assert len(damaged_by_layer['CORE']) == 1
        assert damaged_by_layer['CORE'][0] == ('reactor_standard#0', 50)
        assert 'OUTER' in damaged_by_layer
        assert len(damaged_by_layer['OUTER']) == 1
        assert damaged_by_layer['OUTER'][0] == ('weapon_laser#0', 25)
        assert 'INNER' not in damaged_by_layer  # No damaged components
        assert 'ARMOR' not in damaged_by_layer


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
