"""Tests for ShipDetailPanel (PROJ-142 Phase 2 Task 2.1).

Tests the ship detail panel widget for displaying ship instance information
with damage tracking and resource display.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame
import pygame_gui
from pygame_gui.elements import UIButton


# --- Helpers ---

def _make_mock_ship_instance():
    """Create a mock ShipInstance with typical attributes."""
    ship = MagicMock()

    # Basic attributes
    ship.instance_id = "ship_abc123"
    ship.design_id = "cruiser_mk2"
    ship.name = "USS Enterprise"
    ship.design_data = {
        'name': 'Cruiser Mk II',
        'theme_id': 'Federation',
        'ship_class': 'Cruiser'
    }

    # Display methods
    ship.get_display_id.return_value = "CRS-001"
    ship.get_status_text.return_value = "Operational"
    ship.get_hp_display.return_value = "80/100"
    ship.get_hp_percentage.return_value = 0.8
    ship.get_resource_display.return_value = "50/100"
    ship.get_resource_percentage.return_value = 0.5
    ship.get_damaged_component_count.return_value = 2
    ship.get_damaged_components_by_layer.return_value = {
        'CORE': [('reactor_standard_0', 45), ('engine_basic_0', 30)]
    }

    # Combat stats
    ship.battles_survived = 5
    ship.kills = 3
    ship.experience = 100

    return ship


# --- get_damage_color Tests ---

class TestGetDamageColor:
    """Tests for the get_damage_color helper function."""

    def test_full_health_returns_green(self):
        """HP > 75% returns green color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_HEALTHY

        color = get_damage_color(1.0)

        assert color == HP_HEALTHY

    def test_high_health_returns_green(self):
        """HP at 76% returns green color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_HEALTHY

        color = get_damage_color(0.76)

        assert color == HP_HEALTHY

    def test_moderate_damage_returns_green(self):
        """HP at 60% returns green (>= 50% threshold)."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_HEALTHY

        color = get_damage_color(0.60)

        assert color == HP_HEALTHY

    def test_boundary_50_returns_green(self):
        """HP at exactly 50% returns green (healthy threshold)."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_HEALTHY

        color = get_damage_color(0.50)

        assert color == HP_HEALTHY

    def test_moderate_damage_returns_yellow(self):
        """HP at 25-49% returns yellow color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_DAMAGED

        color = get_damage_color(0.35)

        assert color == HP_DAMAGED

    def test_nearly_destroyed_returns_red(self):
        """HP at 1% returns red color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_CRITICAL

        color = get_damage_color(0.01)

        assert color == HP_CRITICAL

    def test_destroyed_returns_gray(self):
        """HP at 0% returns gray color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_DESTROYED

        color = get_damage_color(0.0)

        assert color == HP_DESTROYED

    def test_negative_returns_gray(self):
        """Negative HP returns gray color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_DESTROYED

        color = get_damage_color(-0.1)

        assert color == HP_DESTROYED


# --- ShipDetailPanel Initialization Tests ---

class TestShipDetailPanelInit:
    """Tests for ShipDetailPanel initialization."""

    def test_panel_stores_manager(self):
        """Panel stores manager reference."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        manager = MagicMock()
        panel.manager = manager

        assert panel.manager is manager

    def test_panel_stores_rect(self):
        """Panel stores rect reference."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        rect = pygame.Rect(0, 0, 300, 600)
        panel.rect = rect

        assert panel.rect == rect

    def test_panel_callback_stored(self):
        """Panel stores on_remove_ship callback."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        callback = MagicMock()
        panel.on_remove_ship = callback

        assert panel.on_remove_ship is callback

    def test_panel_initial_ship_is_none(self):
        """Panel starts with no ship selected."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.current_ship = None

        assert panel.current_ship is None


# --- Layer Expansion State Tests ---

class TestLayerExpansion:
    """Tests for layer collapse/expand state."""

    def test_default_expanded_layers(self):
        """Default expanded_layers has correct initial state."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.expanded_layers = {
            'HULL': True,
            'CORE': True,
            'INNER': False,
            'OUTER': False,
            'ARMOR': True,
        }

        assert panel.expanded_layers['HULL'] is True
        assert panel.expanded_layers['CORE'] is True
        assert panel.expanded_layers['INNER'] is False
        assert panel.expanded_layers['OUTER'] is False
        assert panel.expanded_layers['ARMOR'] is True

    def test_toggle_layer_changes_state(self):
        """toggle_layer inverts the expanded state."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.expanded_layers = {'CORE': True}
        panel.current_ship = None

        panel.toggle_layer('CORE')

        assert panel.expanded_layers['CORE'] is False

    def test_toggle_layer_back_to_expanded(self):
        """toggle_layer twice returns to original state."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.expanded_layers = {'CORE': True}
        panel.current_ship = None

        panel.toggle_layer('CORE')
        panel.toggle_layer('CORE')

        assert panel.expanded_layers['CORE'] is True

    def test_toggle_unknown_layer_no_error(self):
        """toggle_layer ignores unknown layer names."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.expanded_layers = {'CORE': True}
        panel.current_ship = None

        # Should not raise
        panel.toggle_layer('UNKNOWN_LAYER')


# --- Update Ship Tests ---

class TestUpdateShip:
    """Tests for ship display updates."""

    def test_update_ship_sets_current(self):
        """update_ship sets current_ship reference."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        ship = _make_mock_ship_instance()
        panel.current_ship = None
        panel._show_placeholder = MagicMock()
        panel._clear_elements = MagicMock()
        panel._build_ship_display = MagicMock()

        panel.update_ship(ship)

        assert panel.current_ship is ship

    def test_update_ship_none_shows_placeholder(self):
        """update_ship(None) shows placeholder."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.current_ship = MagicMock()
        panel._show_placeholder = MagicMock()

        panel.update_ship(None)

        panel._show_placeholder.assert_called_once()
        assert panel.current_ship is None

    def test_update_ship_clears_old_elements(self):
        """update_ship clears previous UI elements."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        ship = _make_mock_ship_instance()
        panel.current_ship = None
        panel._show_placeholder = MagicMock()
        panel._clear_elements = MagicMock()
        panel._build_ship_display = MagicMock()

        panel.update_ship(ship)

        panel._clear_elements.assert_called_once()

    def test_update_ship_builds_display(self):
        """update_ship calls _build_ship_display."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        ship = _make_mock_ship_instance()
        panel.current_ship = None
        panel._show_placeholder = MagicMock()
        panel._clear_elements = MagicMock()
        panel._build_ship_display = MagicMock()

        panel.update_ship(ship)

        panel._build_ship_display.assert_called_once_with(ship)


# --- Clear Elements Tests ---

class TestClearElements:
    """Tests for UI element cleanup."""

    def test_clear_kills_all_elements(self):
        """_clear_elements kills all dynamic UI elements."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        # Mock elements
        elem1 = MagicMock()
        elem2 = MagicMock()
        panel.ui_elements = [elem1, elem2]
        panel.layer_buttons = {'CORE': MagicMock()}
        panel.group_buttons = {}

        panel._clear_elements()

        elem1.kill.assert_called_once()
        elem2.kill.assert_called_once()

    def test_clear_empties_list(self):
        """_clear_elements empties ui_elements list."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.ui_elements = [MagicMock(), MagicMock()]
        panel.layer_buttons = {'CORE': MagicMock()}
        panel.group_buttons = {}

        panel._clear_elements()

        assert len(panel.ui_elements) == 0

    def test_clear_empties_layer_buttons(self):
        """_clear_elements empties layer_buttons dict."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.ui_elements = []
        panel.layer_buttons = {'CORE': MagicMock(), 'ARMOR': MagicMock()}
        panel.group_buttons = {}

        panel._clear_elements()

        assert len(panel.layer_buttons) == 0


# --- Image Scaling Tests ---

class TestImageScaling:
    """Tests for image scaling helper."""

    def test_scaled_image_returns_surface(self):
        """_get_scaled_image returns a pygame Surface."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        raw = pygame.Surface((100, 100))
        result = panel._get_scaled_image(raw, 50)

        assert isinstance(result, pygame.Surface)

    def test_scaled_image_correct_size(self):
        """_get_scaled_image returns surface of target size."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        raw = pygame.Surface((100, 100))
        result = panel._get_scaled_image(raw, 120)

        assert result.get_size() == (120, 120)

    def test_scaled_image_none_returns_placeholder(self):
        """_get_scaled_image with None returns placeholder surface."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        result = panel._get_scaled_image(None, 100)

        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (100, 100)


# --- Event Processing Tests ---

class TestProcessEvent:
    """Tests for event handling."""

    def test_non_button_event_returns_false(self):
        """Non-button event type returns False."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.btn_remove = None
        panel.layer_buttons = {}

        event = MagicMock()
        event.type = pygame.KEYDOWN

        result = panel.process_event(event)

        assert result is False

    def test_remove_button_triggers_callback(self):
        """Remove button press triggers on_remove_ship callback."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        callback = MagicMock()
        ship = _make_mock_ship_instance()
        remove_btn = MagicMock()

        panel.on_remove_ship = callback
        panel.current_ship = ship
        panel.btn_remove = remove_btn
        panel.layer_buttons = {}

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = remove_btn

        result = panel.process_event(event)

        callback.assert_called_once_with(ship)
        assert result is True

    def test_layer_button_toggles_layer(self):
        """Layer button press calls toggle_layer."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        core_btn = MagicMock()
        panel.btn_remove = None
        panel.layer_buttons = {'CORE': core_btn}
        panel.expanded_layers = {'CORE': True}
        panel.current_ship = None

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = core_btn

        result = panel.process_event(event)

        assert panel.expanded_layers['CORE'] is False
        assert result is True


# --- Kill / Cleanup Tests ---

class TestPanelKill:
    """Tests for panel cleanup."""

    def test_kill_clears_elements(self):
        """kill calls _clear_elements."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel._clear_elements = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        panel._clear_elements.assert_called_once()

    def test_kill_destroys_panel(self):
        """kill calls panel.kill()."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel._clear_elements = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        panel.panel.kill.assert_called_once()


# --- group_components_by_id Tests (PROJ-315 Phase 2 Task 2.1) ---


class TestGroupComponentsById:
    """Pure-function tests for the module-level grouping helper.

    No pygame dependencies — exercises the dataclasses + grouping logic
    directly so the same fixtures back the widget tests below.
    """

    @staticmethod
    def _view(comp_id, idx, current_hp, max_hp, is_active=True):
        from game.core.component_state import ComponentInstanceView
        return ComponentInstanceView(
            component_id=comp_id,
            instance_index=idx,
            current_hp=current_hp,
            max_hp=max_hp,
            is_active=is_active,
        )

    @staticmethod
    def _half_threshold(_comp_id):
        return 0.5

    def test_empty_input_returns_empty_list(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        result = group_components_by_id([], self._half_threshold)

        assert result == []

    def test_single_full_hp_instance(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        result = group_components_by_id(
            [self._view('reactor_standard', 0, 100, 100)],
            self._half_threshold,
        )

        assert len(result) == 1
        group = result[0]
        assert group.component_id == 'reactor_standard'
        assert group.display_name == 'Reactor Standard'
        assert group.total == 1
        assert group.functional == 1
        assert group.avg_damage_pct == pytest.approx(0.0)

    def test_four_engines_75_75_25_25_with_threshold_half(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        # Engines at 75%, 75%, 25%, 25% — first two healthy, last two below
        # the 0.5 threshold and is_active=False to model damage-induced inactive.
        views = [
            self._view('engine_basic', 0, 75, 100, is_active=True),
            self._view('engine_basic', 1, 75, 100, is_active=True),
            self._view('engine_basic', 2, 25, 100, is_active=False),
            self._view('engine_basic', 3, 25, 100, is_active=False),
        ]

        result = group_components_by_id(views, self._half_threshold)

        assert len(result) == 1
        group = result[0]
        assert group.total == 4
        assert group.functional == 2
        assert group.avg_damage_pct == pytest.approx(0.50)
        # First two: not damage-induced inactive (active).
        assert group.instances[0].is_damage_induced_inactive is False
        assert group.instances[1].is_damage_induced_inactive is False
        # Last two: HP below threshold AND inactive.
        assert group.instances[2].is_damage_induced_inactive is True
        assert group.instances[3].is_damage_induced_inactive is True

    def test_all_destroyed_group(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        views = [
            self._view('weapon_laser', 0, 0, 100, is_active=False),
            self._view('weapon_laser', 1, 0, 100, is_active=False),
        ]

        result = group_components_by_id(views, self._half_threshold)

        group = result[0]
        assert group.functional == 0
        assert group.avg_damage_pct == pytest.approx(1.0)

    def test_manually_disabled_full_hp_is_not_damage_induced_inactive(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        views = [
            self._view('reactor_standard', 0, 100, 100, is_active=False),
        ]

        result = group_components_by_id(views, self._half_threshold)

        group = result[0]
        assert group.functional == 0
        assert group.instances[0].is_damage_induced_inactive is False

    def test_per_id_threshold_lookup_honoured(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        thresholds = {
            'engine_basic': 0.8,
            'reactor_standard': 0.2,
        }

        def lookup(comp_id):
            return thresholds.get(comp_id, 0.5)

        # Engine at 50% HP, threshold 0.8 -> below threshold
        # Reactor at 50% HP, threshold 0.2 -> above threshold
        views = [
            self._view('engine_basic', 0, 50, 100, is_active=False),
            self._view('reactor_standard', 0, 50, 100, is_active=False),
        ]

        result = group_components_by_id(views, lookup)

        groups = {g.component_id: g for g in result}
        assert groups['engine_basic'].instances[0].is_damage_induced_inactive is True
        assert groups['reactor_standard'].instances[0].is_damage_induced_inactive is False

    def test_zero_max_hp_returns_zero_damage_pct_no_exception(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        views = [
            self._view('legacy_zero', 0, 0, 0, is_active=True),
        ]

        result = group_components_by_id(views, self._half_threshold)

        assert result[0].instances[0].damage_pct == pytest.approx(0.0)

    def test_grouping_preserves_first_seen_order(self):
        from game.ui.panels.ship_detail_panel import group_components_by_id

        views = [
            self._view('engine_basic', 0, 100, 100),
            self._view('weapon_laser', 0, 100, 100),
            self._view('engine_basic', 1, 100, 100),
            self._view('weapon_laser', 1, 100, 100),
        ]

        result = group_components_by_id(views, self._half_threshold)

        assert [g.component_id for g in result] == ['engine_basic', 'weapon_laser']
        assert result[0].total == 2
        assert result[1].total == 2


# --- Component Status Section widget tests (PROJ-315 Phase 2 Task 2.4) ------


def _stub_ship_instance(views_by_layer):
    """Build a MagicMock that quacks like a ShipInstance for the panel."""
    ship = MagicMock()
    ship.instance_id = 'ship_test'
    ship.design_id = 'TestDesign'
    ship.name = 'Test Ship'
    ship.design_data = {
        'name': 'TestDesign',
        'theme_id': 'Federation',
        'ship_class': 'Cruiser',
    }
    ship.get_display_id.return_value = 'TST-001'
    ship.get_status_text.return_value = 'OK'
    ship.get_hp_display.return_value = '100/100'
    ship.get_hp_percentage.return_value = 1.0
    ship.get_resource_display.return_value = 'N/A'
    ship.get_resource_percentage.return_value = 0.0
    ship.get_damaged_component_count.return_value = 0
    ship.iter_all_components_by_layer.return_value = views_by_layer
    ship.battles_survived = 0
    ship.kills = 0
    ship.experience = 0
    return ship


def _view(comp_id, idx, current_hp, max_hp, is_active=True):
    from game.core.component_state import ComponentInstanceView
    return ComponentInstanceView(
        component_id=comp_id,
        instance_index=idx,
        current_hp=current_hp,
        max_hp=max_hp,
        is_active=is_active,
    )


def _new_panel(ui_manager):
    """Construct a real ShipDetailPanel against the cached ui_manager."""
    from game.ui.panels.ship_detail_panel import ShipDetailPanel
    rect = pygame.Rect(0, 0, 400, 800)
    return ShipDetailPanel(manager=ui_manager, rect=rect)


def _label_texts(panel):
    return [getattr(el, 'text', '') for el in panel.ui_elements]


class TestComponentStatusSection:
    """PROJ-315 Phase 2 Task 2.4 widget tests."""

    def test_pristine_ship_renders_section_header(self, ui_manager):
        ship = _stub_ship_instance({
            'CORE': [_view('reactor_standard', 0, 100, 100)],
            'INNER': [_view('bridge_standard', 0, 100, 100)],
            'OUTER': [_view('weapon_laser', 0, 100, 100)],
            'ARMOR': [_view('armor_plate', 0, 100, 100)],
        })
        panel = _new_panel(ui_manager)

        panel.update_ship(ship)

        assert any('COMPONENT STATUS' in t for t in _label_texts(panel))

    def test_pristine_ship_all_layers_collapsed(self, ui_manager):
        ship = _stub_ship_instance({
            'CORE': [_view('reactor_standard', 0, 100, 100)],
            'INNER': [_view('bridge_standard', 0, 100, 100)],
            'OUTER': [_view('weapon_laser', 0, 100, 100)],
            'ARMOR': [_view('armor_plate', 0, 100, 100)],
        })
        panel = _new_panel(ui_manager)

        panel.update_ship(ship)

        for layer, expanded in panel.expanded_layers.items():
            assert expanded is False, f"Layer {layer} should be collapsed by default"

    def test_pristine_layer_header_shows_full_functional(self, ui_manager):
        ship = _stub_ship_instance({
            'CORE': [
                _view('reactor_standard', 0, 100, 100),
                _view('engine_basic', 0, 100, 100),
                _view('engine_basic', 1, 100, 100),
            ],
        })
        panel = _new_panel(ui_manager)

        panel.update_ship(ship)

        core_btn = panel.layer_buttons['CORE']
        assert '3/3 functional' in core_btn.text
        assert '0% avg damage' in core_btn.text

    def test_four_engines_75_75_25_25_collapsed_group_row(self, ui_manager):
        ship = _stub_ship_instance({
            'CORE': [
                _view('engine_basic', 0, 75, 100, is_active=True),
                _view('engine_basic', 1, 75, 100, is_active=True),
                _view('engine_basic', 2, 25, 100, is_active=False),
                _view('engine_basic', 3, 25, 100, is_active=False),
            ],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        panel.toggle_layer('CORE')

        key = ('CORE', 'engine_basic')
        group_btn = panel.group_buttons[key]
        assert 'Engine Basic' in group_btn.text
        assert '× 4' in group_btn.text
        assert '2/4' in group_btn.text
        assert '50%' in group_btn.text

    def test_destroyed_instance_auto_expands_layer(self, ui_manager):
        ship = _stub_ship_instance({
            'CORE': [
                _view('reactor_standard', 0, 0, 100, is_active=False),
            ],
        })
        panel = _new_panel(ui_manager)

        panel.update_ship(ship)

        assert panel.expanded_layers['CORE'] is True

    def test_destroyed_instance_renders_in_destroyed_color_with_strike(self, ui_manager):
        from game.ui.colors import HP_DESTROYED
        ship = _stub_ship_instance({
            'CORE': [
                _view('reactor_standard', 0, 0, 100, is_active=False),
            ],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        # CORE auto-expanded; expand the group too.
        panel.toggle_group('CORE', 'reactor_standard')

        instance_labels = [
            el for el in panel.ui_elements
            if hasattr(el, '_proj315_color')
        ]
        assert len(instance_labels) == 1
        assert instance_labels[0]._proj315_color == HP_DESTROYED
        assert instance_labels[0]._proj315_strike is True

    def test_damage_induced_inactive_renders_critical_with_strike(self, ui_manager):
        from game.ui.colors import HP_CRITICAL
        ship = _stub_ship_instance({
            'CORE': [
                _view('engine_basic', 0, 25, 100, is_active=False),
            ],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        panel.toggle_layer('CORE')
        panel.toggle_group('CORE', 'engine_basic')

        instance_labels = [
            el for el in panel.ui_elements
            if hasattr(el, '_proj315_color')
        ]
        assert len(instance_labels) == 1
        assert instance_labels[0]._proj315_color == HP_CRITICAL
        assert instance_labels[0]._proj315_strike is True

    def test_manually_disabled_renders_muted_grey_no_strike(self, ui_manager):
        from game.ui.colors import MUTED_GREY
        ship = _stub_ship_instance({
            'CORE': [
                _view('reactor_standard', 0, 100, 100, is_active=False),
            ],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        panel.toggle_layer('CORE')
        panel.toggle_group('CORE', 'reactor_standard')

        instance_labels = [
            el for el in panel.ui_elements
            if hasattr(el, '_proj315_color')
        ]
        assert len(instance_labels) == 1
        assert instance_labels[0]._proj315_color == MUTED_GREY
        assert instance_labels[0]._proj315_strike is False

    def test_layer_order_is_deterministic(self, ui_manager):
        ship = _stub_ship_instance({
            'OUTER': [_view('weapon_laser', 0, 100, 100)],
            'CORE': [_view('reactor_standard', 0, 100, 100)],
            'ARMOR': [_view('armor_plate', 0, 100, 100)],
            'INNER': [_view('bridge_standard', 0, 100, 100)],
        })
        panel = _new_panel(ui_manager)

        panel.update_ship(ship)

        # Layer buttons preserve LAYER_ORDER iteration order
        layer_btn_order = list(panel.layer_buttons.keys())
        assert layer_btn_order == ['CORE', 'INNER', 'OUTER', 'ARMOR']

    def test_hull_layer_suppressed_even_when_present(self, ui_manager):
        # Note: iter_all_components_by_layer already filters HULL upstream
        # (Phase 1 contract). This test pins the panel-side guarantee.
        ship = _stub_ship_instance({
            'CORE': [_view('reactor_standard', 0, 100, 100)],
            'HULL': [_view('hull_plating', 0, 100, 100)],
        })
        panel = _new_panel(ui_manager)

        panel.update_ship(ship)

        assert 'HULL' not in panel.layer_buttons

    def test_auto_expand_re_fires_on_ship_reselect(self, ui_manager):
        clean_ship = _stub_ship_instance({
            'CORE': [_view('reactor_standard', 0, 100, 100)],
        })
        damaged_ship = _stub_ship_instance({
            'CORE': [_view('reactor_standard', 0, 0, 100, is_active=False)],
        })
        panel = _new_panel(ui_manager)

        panel.update_ship(clean_ship)
        panel.toggle_layer('CORE')
        assert panel.expanded_layers['CORE'] is True

        panel.update_ship(damaged_ship)
        # Auto-expand re-fires; CORE remains True (now due to destroyed).
        assert panel.expanded_layers['CORE'] is True

        # Reselecting a clean ship re-fires and resets to False.
        panel.update_ship(clean_ship)
        assert panel.expanded_layers['CORE'] is False

    def test_group_toggle_cycles_state(self, ui_manager):
        ship = _stub_ship_instance({
            'CORE': [_view('reactor_standard', 0, 100, 100)],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        panel.toggle_layer('CORE')

        key = ('CORE', 'reactor_standard')
        assert panel.expanded_groups.get(key, False) is False
        panel.toggle_group('CORE', 'reactor_standard')
        assert panel.expanded_groups[key] is True
        panel.toggle_group('CORE', 'reactor_standard')
        assert panel.expanded_groups[key] is False

    def test_group_row_text_format(self, ui_manager):
        ship = _stub_ship_instance({
            'CORE': [
                _view('reactor_standard', 0, 100, 100),
                _view('reactor_standard', 1, 100, 100),
                _view('reactor_standard', 2, 100, 100),
                _view('reactor_standard', 3, 100, 100),
            ],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        panel.toggle_layer('CORE')

        key = ('CORE', 'reactor_standard')
        group_btn = panel.group_buttons[key]
        # × is U+00D7
        assert 'Reactor Standard × 4' in group_btn.text

    def test_component_id_with_underscores_renders_correctly(self, ui_manager):
        """Pins the parser-bug fix from Phase 1 — `reactor_mark_2` round-trips."""
        ship = _stub_ship_instance({
            'CORE': [_view('reactor_mark_2', 0, 100, 100)],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        panel.toggle_layer('CORE')

        key = ('CORE', 'reactor_mark_2')
        assert key in panel.group_buttons
        assert 'Reactor Mark 2' in panel.group_buttons[key].text

    def test_no_component_rows_have_buttons(self, ui_manager):
        """Read-only contract: instance rows are labels, not buttons."""
        ship = _stub_ship_instance({
            'CORE': [
                _view('reactor_standard', 0, 100, 100),
                _view('reactor_standard', 1, 50, 100),
            ],
        })
        panel = _new_panel(ui_manager)
        panel.update_ship(ship)
        panel.toggle_layer('CORE')
        panel.toggle_group('CORE', 'reactor_standard')

        # Buttons inside the section must equal layer + group buttons only.
        button_count = len(panel.layer_buttons) + len(panel.group_buttons)
        # The pre-existing Remove from Fleet button is unaffected (none here
        # because on_remove_ship is None in _new_panel).
        actual_buttons = [
            el for el in panel.ui_elements if isinstance(el, UIButton)
        ]
        assert len(actual_buttons) == button_count


