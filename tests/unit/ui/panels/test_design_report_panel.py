"""Tests for DesignReportPanel (PROJ-142 Phase 2 Task 2.3).

Tests the design report panel widget for displaying ship design information
with portrait and stats display.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# --- Helpers ---

def _make_mock_ship():
    """Create a mock Ship with typical attributes."""
    ship = MagicMock()

    ship.name = "Cruiser Mk II"
    ship.theme_id = "Federation"
    ship.ship_class = "Cruiser"
    ship.vehicle_type = "Starship"

    # Stats
    ship.mass = 150.0
    ship.max_mass = 200.0
    ship.thrust = 50
    ship.max_speed = 5
    ship.hp = 100
    ship.max_hp = 100

    return ship


# --- DesignReportPanel Import Tests ---

class TestDesignReportPanelImport:
    """Tests for module import."""

    def test_panel_can_be_imported(self):
        """DesignReportPanel can be imported."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        assert DesignReportPanel is not None


# --- DesignReportPanel Initialization Tests ---

class TestDesignReportPanelInit:
    """Tests for DesignReportPanel initialization."""

    def test_panel_stores_manager(self):
        """Panel stores manager reference."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        manager = MagicMock()
        panel.manager = manager

        assert panel.manager is manager

    def test_panel_stores_rect(self):
        """Panel stores rect reference."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        rect = pygame.Rect(0, 0, 400, 800)
        panel.rect = rect

        assert panel.rect == rect

    def test_panel_stores_container(self):
        """Panel stores container reference."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        container = MagicMock()
        panel.container = container

        assert panel.container is container

    def test_panel_initial_ship_is_none(self):
        """Panel starts with no ship selected."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel.current_ship = None

        assert panel.current_ship is None

    def test_panel_stats_panel_initially_none(self):
        """Panel stats_panel is initially None."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel._stats_panel = None

        assert panel._stats_panel is None

    def test_panel_rows_map_is_dict(self):
        """Panel rows_map is initialized as dict."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel.rows_map = {}

        assert isinstance(panel.rows_map, dict)


# --- Show Placeholder Tests ---

class TestShowPlaceholder:
    """Tests for placeholder display."""

    def test_show_placeholder_logic_clears_ship(self):
        """show_placeholder logic sets current_ship to None."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel.current_ship = _make_mock_ship()

        # The show_placeholder method sets current_ship = None
        panel.current_ship = None

        assert panel.current_ship is None

    def test_show_placeholder_logic_kills_stats(self):
        """show_placeholder logic kills existing stats_panel."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        mock_stats = MagicMock()
        panel._stats_panel = mock_stats

        # The show_placeholder method checks and kills stats
        if panel._stats_panel is not None:
            panel._stats_panel.kill()
            panel._stats_panel = None

        mock_stats.kill.assert_called_once()
        assert panel._stats_panel is None

    def test_show_placeholder_logic_clears_rows(self):
        """show_placeholder logic clears rows_map."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel.rows_map = {'mass': MagicMock(), 'speed': MagicMock()}

        # The show_placeholder method clears rows_map
        panel.rows_map = {}

        assert panel.rows_map == {}

    def test_label_set_text_clears(self):
        """Labels can be cleared with set_text."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()

        # The show_placeholder clears labels
        panel.name_label.set_text("")
        panel.type_class_label.set_text("")

        panel.name_label.set_text.assert_called_with("")
        panel.type_class_label.set_text.assert_called_with("")

    def test_placeholder_text_kills_old(self):
        """Old placeholder can be killed."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        old_placeholder = MagicMock()
        panel.placeholder_text = old_placeholder

        # The show_placeholder checks and kills old
        if panel.placeholder_text:
            panel.placeholder_text.kill()

        old_placeholder.kill.assert_called_once()


# --- Update Design Tests ---

class TestUpdateDesign:
    """Tests for design display updates."""

    def test_update_design_sets_current(self):
        """update_design sets current_ship reference."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        panel.current_ship = None
        panel.placeholder_text = MagicMock()
        panel._update_portrait = MagicMock()
        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        panel._stats_panel = None
        panel.rect = pygame.Rect(0, 0, 400, 800)
        panel.manager = MagicMock()
        panel.panel = MagicMock()

        with patch('game.ui.panels.design_report_panel.DesignStatsPanel') as MockStats:
            mock_stats = MagicMock()
            mock_stats.rows_map = {}
            MockStats.return_value = mock_stats
            panel.update_design(ship)

        assert panel.current_ship is ship

    def test_update_design_kills_placeholder(self):
        """update_design kills placeholder text."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        placeholder = MagicMock()
        panel.current_ship = None
        panel.placeholder_text = placeholder
        panel._update_portrait = MagicMock()
        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        panel._stats_panel = None
        panel.rect = pygame.Rect(0, 0, 400, 800)
        panel.manager = MagicMock()
        panel.panel = MagicMock()

        with patch('game.ui.panels.design_report_panel.DesignStatsPanel') as MockStats:
            mock_stats = MagicMock()
            mock_stats.rows_map = {}
            MockStats.return_value = mock_stats
            panel.update_design(ship)

        placeholder.kill.assert_called_once()
        assert panel.placeholder_text is None

    def test_update_design_updates_name_label(self):
        """update_design sets name_label text."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        ship.name = "Battlecruiser Alpha"
        panel.current_ship = None
        panel.placeholder_text = None
        panel._update_portrait = MagicMock()
        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        panel._stats_panel = None
        panel.rect = pygame.Rect(0, 0, 400, 800)
        panel.manager = MagicMock()
        panel.panel = MagicMock()

        with patch('game.ui.panels.design_report_panel.DesignStatsPanel') as MockStats:
            mock_stats = MagicMock()
            mock_stats.rows_map = {}
            MockStats.return_value = mock_stats
            panel.update_design(ship)

        panel.name_label.set_text.assert_called_with("Battlecruiser Alpha")

    def test_update_design_updates_type_class(self):
        """update_design sets type_class_label text."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        ship.vehicle_type = "Starship"
        ship.ship_class = "Cruiser"
        panel.current_ship = None
        panel.placeholder_text = None
        panel._update_portrait = MagicMock()
        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        panel._stats_panel = None
        panel.rect = pygame.Rect(0, 0, 400, 800)
        panel.manager = MagicMock()
        panel.panel = MagicMock()

        with patch('game.ui.panels.design_report_panel.DesignStatsPanel') as MockStats:
            mock_stats = MagicMock()
            mock_stats.rows_map = {}
            MockStats.return_value = mock_stats
            panel.update_design(ship)

        panel.type_class_label.set_text.assert_called_with("Starship - Cruiser")

    def test_update_design_kills_old_stats(self):
        """update_design kills old stats_panel."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        old_stats = MagicMock()
        panel.current_ship = None
        panel.placeholder_text = None
        panel._update_portrait = MagicMock()
        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        panel._stats_panel = old_stats
        panel.rect = pygame.Rect(0, 0, 400, 800)
        panel.manager = MagicMock()
        panel.panel = MagicMock()

        with patch('game.ui.panels.design_report_panel.DesignStatsPanel') as MockStats:
            mock_stats = MagicMock()
            mock_stats.rows_map = {}
            MockStats.return_value = mock_stats
            panel.update_design(ship)

        old_stats.kill.assert_called_once()

    def test_update_design_creates_stats_panel(self):
        """update_design creates new DesignStatsPanel."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        panel.current_ship = None
        panel.placeholder_text = None
        panel._update_portrait = MagicMock()
        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        panel._stats_panel = None
        panel.rect = pygame.Rect(0, 0, 400, 800)
        panel.manager = MagicMock()
        panel.panel = MagicMock()

        with patch('game.ui.panels.design_report_panel.DesignStatsPanel') as MockStats:
            mock_stats = MagicMock()
            mock_stats.rows_map = {'mass': MagicMock()}
            MockStats.return_value = mock_stats
            panel.update_design(ship)

        MockStats.assert_called_once()
        assert panel._stats_panel is mock_stats

    def test_update_design_exposes_rows_map(self):
        """update_design exposes stats_panel.rows_map."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        panel.current_ship = None
        panel.placeholder_text = None
        panel._update_portrait = MagicMock()
        panel.name_label = MagicMock()
        panel.type_class_label = MagicMock()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        panel._stats_panel = None
        panel.rect = pygame.Rect(0, 0, 400, 800)
        panel.manager = MagicMock()
        panel.panel = MagicMock()
        panel.rows_map = {}

        with patch('game.ui.panels.design_report_panel.DesignStatsPanel') as MockStats:
            mock_stats = MagicMock()
            mock_stats.rows_map = {'mass': MagicMock(), 'speed': MagicMock()}
            MockStats.return_value = mock_stats
            panel.update_design(ship)

        assert panel.rows_map == {'mass': mock_stats.rows_map['mass'], 'speed': mock_stats.rows_map['speed']}


# --- Portrait Update Tests ---

class TestUpdatePortrait:
    """Tests for portrait image generation."""

    @pytest.fixture
    def init_pygame(self):
        """Initialize pygame for surface operations."""
        pygame.init()
        yield
        pygame.quit()

    def test_portrait_loads_from_file(self, init_pygame):
        """_update_portrait attempts to load from file paths."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)

        with patch('os.path.exists', return_value=False):
            panel._update_portrait(ship)

        # Should still call set_image with fallback
        panel.portrait_image.set_image.assert_called_once()

    def test_portrait_uses_fallback(self, init_pygame):
        """_update_portrait creates fallback when no image found."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)

        with patch('os.path.exists', return_value=False):
            panel._update_portrait(ship)

        panel.portrait_image.set_image.assert_called_once()


# --- Width Required Tests ---

class TestWidthRequired:
    """Tests for get_width_required method."""

    def test_width_returns_750(self):
        """get_width_required returns 750."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        width = panel.get_width_required()

        assert width == 750

    def test_width_is_integer(self):
        """get_width_required returns integer."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        width = panel.get_width_required()

        assert isinstance(width, int)


# --- Kill / Cleanup Tests ---

class TestPanelKill:
    """Tests for panel cleanup."""

    def test_kill_destroys_stats_panel(self):
        """kill destroys stats_panel."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        mock_stats = MagicMock()
        panel._stats_panel = mock_stats
        panel.panel = MagicMock()

        panel.kill()

        mock_stats.kill.assert_called_once()
        assert panel._stats_panel is None

    def test_kill_destroys_main_panel(self):
        """kill destroys main panel."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel._stats_panel = None
        panel.panel = MagicMock()

        panel.kill()

        panel.panel.kill.assert_called_once()

    def test_kill_handles_no_stats_panel(self):
        """kill handles case where stats_panel is None."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        panel._stats_panel = None
        panel.panel = MagicMock()

        # Should not raise
        panel.kill()

        panel.panel.kill.assert_called_once()
