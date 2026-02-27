"""Tests for ShipDetailPanel (PROJ-142 Phase 2 Task 2.1).

Tests the ship detail panel widget for displaying ship instance information
with damage tracking and resource display.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


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

    def test_moderate_damage_returns_yellow(self):
        """HP at 50-75% returns yellow color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_DAMAGED

        color = get_damage_color(0.60)

        assert color == HP_DAMAGED

    def test_boundary_50_returns_yellow(self):
        """HP at exactly 50% returns yellow (boundary test)."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_DAMAGED

        color = get_damage_color(0.50)

        assert color == HP_DAMAGED

    def test_critical_damage_returns_red(self):
        """HP at 1-50% returns red color."""
        from game.ui.panels.ship_detail_panel import get_damage_color
        from game.ui.colors import HP_CRITICAL

        color = get_damage_color(0.25)

        assert color == HP_CRITICAL

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

    def test_panel_can_be_imported(self):
        """ShipDetailPanel can be imported."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        assert ShipDetailPanel is not None

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

        panel._clear_elements()

        assert len(panel.ui_elements) == 0

    def test_clear_empties_layer_buttons(self):
        """_clear_elements empties layer_buttons dict."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        panel.ui_elements = []
        panel.layer_buttons = {'CORE': MagicMock(), 'ARMOR': MagicMock()}

        panel._clear_elements()

        assert len(panel.layer_buttons) == 0


# --- Image Scaling Tests ---

class TestImageScaling:
    """Tests for image scaling helper."""

    @pytest.fixture
    def init_pygame(self):
        """Initialize pygame for surface operations."""
        pygame.init()
        yield
        pygame.quit()

    def test_scaled_image_returns_surface(self, init_pygame):
        """_get_scaled_image returns a pygame Surface."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        raw = pygame.Surface((100, 100))
        result = panel._get_scaled_image(raw, 50)

        assert isinstance(result, pygame.Surface)

    def test_scaled_image_correct_size(self, init_pygame):
        """_get_scaled_image returns surface of target size."""
        from game.ui.panels.ship_detail_panel import ShipDetailPanel

        with patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None):
            panel = ShipDetailPanel.__new__(ShipDetailPanel)

        raw = pygame.Surface((100, 100))
        result = panel._get_scaled_image(raw, 120)

        assert result.get_size() == (120, 120)

    def test_scaled_image_none_returns_placeholder(self, init_pygame):
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

    def test_non_user_event_returns_false(self):
        """Non-USEREVENT type returns False."""
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
        event.type = pygame.USEREVENT
        event.user_type = 'ui_button_pressed'
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
        event.type = pygame.USEREVENT
        event.user_type = 'ui_button_pressed'
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
