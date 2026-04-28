"""Tests for ship detail panel functionality - PROJ-03 Phase 4."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from unittest.mock import MagicMock, patch

from game.core.component_state import (
    ComponentInstanceView,
    ComponentState,
    component_state_key,
)
from game.strategy.data.ship_instance import (
    ShipInstance,
    _build_full_hp_components_from_design,
)


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


class TestIterAllComponentsByLayer:
    """PROJ-315 Phase 1 Task 1.2: Test iter_all_components_by_layer()."""

    @pytest.fixture
    def design_data_with_layers(self):
        return {
            'name': 'TestShip',
            'expected_stats': {'max_hp': 100},
            'layers': {
                'CORE': [
                    {'id': 'reactor_standard'},
                    {'id': 'engine_basic'},
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
                ],
            },
        }

    def test_pristine_ship_yields_every_layer_at_full_hp(
        self, design_data_with_layers, ship_factory
    ):
        instance = ship_factory(design_data_with_layers, owner_id=0)

        result = instance.iter_all_components_by_layer()

        assert set(result.keys()) == {'CORE', 'INNER', 'OUTER', 'ARMOR'}
        for views in result.values():
            for view in views:
                assert isinstance(view, ComponentInstanceView)
                assert view.is_active is True
                assert view.current_hp == view.max_hp

    def test_partially_damaged_views_match_component_state(
        self, design_data_with_layers, ship_factory
    ):
        instance = ship_factory(design_data_with_layers, owner_id=0)
        instance.components[component_state_key('reactor_standard', 0)] = ComponentState(
            component_id='reactor_standard',
            instance_index=0,
            current_hp=30.0,
            max_hp=100.0,
            is_active=False,
        )

        result = instance.iter_all_components_by_layer()

        core_views = result['CORE']
        reactor_view = next(v for v in core_views if v.component_id == 'reactor_standard')
        assert reactor_view.current_hp == 30
        assert reactor_view.max_hp == 100
        assert reactor_view.is_active is False

    def test_hull_layer_filtered_out(self, ship_factory):
        design = {
            'name': 'WithHull',
            'expected_stats': {'max_hp': 100},
            'layers': {
                'HULL': [{'id': 'hull_plating'}],
                'CORE': [{'id': 'reactor_standard'}],
            },
        }
        instance = ship_factory(design, owner_id=0)

        result = instance.iter_all_components_by_layer()

        assert 'HULL' not in result
        assert 'CORE' in result

    def test_component_id_with_underscores_preserved(self):
        """Regression: the old `_`-split parser at ship_detail_panel.py:367-375
        broke ids like `reactor_mark_2`. The new view uses
        `ComponentInstanceView.component_id` directly — never re-parsed.
        """
        design = {
            'name': 'MarkTwo',
            'expected_stats': {'max_hp': 100},
            'layers': {
                'CORE': [
                    {'id': 'reactor_mark_2'},
                ],
            },
        }
        instance = ShipInstance(
            instance_id='ship_mark_two',
            design_id='mark_two',
            name='Mark Two',
            owner_id=0,
            design_data=design,
            components={
                component_state_key('reactor_mark_2', 0): ComponentState(
                    component_id='reactor_mark_2',
                    instance_index=0,
                    current_hp=100.0,
                    max_hp=100.0,
                ),
            },
        )

        result = instance.iter_all_components_by_layer()

        core_views = result['CORE']
        assert len(core_views) == 1
        assert core_views[0].component_id == 'reactor_mark_2'
        assert core_views[0].instance_index == 0

    def test_empty_layers_returns_empty_dict(self, ship_factory):
        design = {
            'name': 'NoLayers',
            'expected_stats': {'max_hp': 100},
        }
        instance = ship_factory(design, owner_id=0)

        result = instance.iter_all_components_by_layer()

        assert result == {}

    def test_instance_index_numbering_per_component_id(self):
        design = {
            'name': 'FourEngines',
            'expected_stats': {'max_hp': 100},
            'layers': {
                'CORE': [
                    {'id': 'engine_basic'},
                    {'id': 'engine_basic'},
                    {'id': 'engine_basic'},
                    {'id': 'engine_basic'},
                ],
            },
        }
        instance = ShipInstance(
            instance_id='ship_four_engines',
            design_id='four_engines',
            name='Four Engines',
            owner_id=0,
            design_data=design,
            components={
                component_state_key('engine_basic', idx): ComponentState(
                    component_id='engine_basic',
                    instance_index=idx,
                    current_hp=100.0,
                    max_hp=100.0,
                )
                for idx in range(4)
            },
        )

        result = instance.iter_all_components_by_layer()

        engine_views = [v for v in result['CORE'] if v.component_id == 'engine_basic']
        assert len(engine_views) == 4
        assert [v.instance_index for v in engine_views] == [0, 1, 2, 3]

    def test_default_view_when_state_missing(self, monkeypatch):
        """When ComponentState is absent for a key, view defaults to full HP / active."""
        design = {
            'name': 'Defaulty',
            'expected_stats': {'max_hp': 100},
            'layers': {
                'CORE': [{'id': 'reactor_standard'}],
            },
        }
        instance = ShipInstance(
            instance_id='ship_defaulty',
            design_id='defaulty',
            name='Defaulty',
            owner_id=0,
            design_data=design,
            components={},
        )

        class Provider:
            def get_components(self):
                return {'reactor_standard': SimpleNamespace(max_hp=100)}

        monkeypatch.setattr(
            'game.core.registry.get_default_registry_provider',
            lambda: Provider(),
        )

        result = instance.iter_all_components_by_layer()

        view = result['CORE'][0]
        assert view.is_active is True
        assert view.current_hp == 100
        assert view.max_hp == 100


class TestIterAllComponentsByLayerRemediations:
    """PROJ-317 regressions for PROJ-315 audit findings R1 and R4."""

    def test_iter_keys_match_full_hp_builder_for_cross_layer_design(
        self, fresh_registries
    ):
        """R1: iterator indices must match the canonical seeding helper."""
        design_path = (
            Path(__file__).resolve().parents[3]
            / 'data'
            / 'designs'
            / 'qs_battleship.json'
        )
        design = json.loads(design_path.read_text(encoding='utf-8'))
        seeded_components = _build_full_hp_components_from_design(
            design, fresh_registries
        )
        instance = ShipInstance(
            instance_id='ship_qs_battleship',
            design_id='qs_battleship',
            name='QS Battleship',
            owner_id=0,
            design_data=design,
            components=seeded_components,
        )

        result = instance.iter_all_components_by_layer()

        design_component_ids = {
            entry['id']
            for entries in design['layers'].values()
            for entry in entries
        }
        iter_keys = {
            (view.component_id, view.instance_index)
            for layer_views in result.values()
            for view in layer_views
        }
        seeded_keys = {
            (state.component_id, state.instance_index)
            for state in seeded_components.values()
            if state.component_id in design_component_ids
        }
        assert ('battery', 1) in seeded_keys
        assert ('fuel_tank', 1) in seeded_keys
        assert iter_keys == seeded_keys

    def test_cross_layer_component_ids_use_ship_wide_instance_index(self):
        """R1: shared component ids across layers must not alias to index 0."""
        design = {
            'name': 'CrossLayerBattery',
            'layers': {
                'CORE': [{'id': 'battery'}],
                'INNER': [{'id': 'battery'}],
            },
        }
        instance = ShipInstance(
            instance_id='ship_cross_layer',
            design_id='cross_layer',
            name='Cross Layer',
            owner_id=0,
            design_data=design,
            components={
                component_state_key('battery', 0): ComponentState(
                    component_id='battery',
                    instance_index=0,
                    current_hp=10.0,
                    max_hp=100.0,
                    is_active=False,
                ),
                component_state_key('battery', 1): ComponentState(
                    component_id='battery',
                    instance_index=1,
                    current_hp=90.0,
                    max_hp=100.0,
                    is_active=True,
                ),
            },
        )

        result = instance.iter_all_components_by_layer()

        assert [(v.instance_index, v.current_hp) for v in result['CORE']] == [(0, 10)]
        assert [(v.instance_index, v.current_hp) for v in result['INNER']] == [(1, 90)]

    def test_missing_state_uses_registry_max_hp_for_full_hp_view(self, monkeypatch):
        """R4: missing ComponentState should not render as 0/0."""
        design = {
            'name': 'MissingState',
            'layers': {
                'CORE': [{'id': 'fallback_component'}],
            },
        }
        instance = ShipInstance(
            instance_id='ship_missing_state',
            design_id='missing_state',
            name='Missing State',
            owner_id=0,
            design_data=design,
            components={},
        )

        class Provider:
            def get_components(self):
                return {'fallback_component': SimpleNamespace(max_hp=42)}

        monkeypatch.setattr(
            'game.core.registry.get_default_registry_provider',
            lambda: Provider(),
        )

        result = instance.iter_all_components_by_layer()

        view = result['CORE'][0]
        assert view.current_hp == 42
        assert view.max_hp == 42
        assert view.is_active is True

    def test_missing_state_prefers_injected_registries(
        self, monkeypatch, minimal_registries
    ):
        """R4: prefer the instance DI registry before global fallback."""
        design = {
            'name': 'InjectedRegistryMissingState',
            'layers': {
                'CORE': [{'id': 'local_component'}],
            },
        }
        instance = ShipInstance(
            instance_id='ship_injected_registry_missing_state',
            design_id='injected_registry_missing_state',
            name='Injected Registry Missing State',
            owner_id=0,
            design_data=design,
            components={},
        )
        minimal_registries.components['local_component'] = SimpleNamespace(max_hp=64)
        instance.set_registries(minimal_registries)

        def unexpected_global_provider():
            raise AssertionError('global registry should not be used')

        monkeypatch.setattr(
            'game.core.registry.get_default_registry_provider',
            unexpected_global_provider,
        )

        result = instance.iter_all_components_by_layer()

        view = result['CORE'][0]
        assert view.current_hp == 64
        assert view.max_hp == 64
        assert view.is_active is True

    def test_missing_state_and_unknown_registry_component_skips_instance(self, monkeypatch):
        """R4 dual-miss: skip rather than emit a meaningless zero-HP view."""
        design = {
            'name': 'UnknownMissingState',
            'layers': {
                'CORE': [{'id': 'unknown_component'}],
            },
        }
        instance = ShipInstance(
            instance_id='ship_unknown_missing_state',
            design_id='unknown_missing_state',
            name='Unknown Missing State',
            owner_id=0,
            design_data=design,
            components={},
        )

        class Provider:
            def get_components(self):
                return {}

        monkeypatch.setattr(
            'game.core.registry.get_default_registry_provider',
            lambda: Provider(),
        )

        result = instance.iter_all_components_by_layer()

        assert result['CORE'] == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
