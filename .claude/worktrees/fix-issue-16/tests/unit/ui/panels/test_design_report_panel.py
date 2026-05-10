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

    def test_portrait_uses_ship_theme_manager(self) -> None:
        """_update_portrait uses ShipThemeManager's unified Surface contract."""
        from game.ui.panels.design_report_panel import DesignReportPanel

        with patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignReportPanel.__new__(DesignReportPanel)

        ship = _make_mock_ship()
        panel.portrait_image = MagicMock()
        panel.portrait_image.relative_rect = pygame.Rect(0, 0, 200, 200)
        source = pygame.Surface((64, 64))
        manager = MagicMock()
        manager.get_portrait_image.return_value = source

        with patch(
            'game.ui.panels.design_report_panel.get_default_ship_theme_manager',
            return_value=manager,
        ):
            panel._update_portrait(ship)

        manager.get_portrait_image.assert_called_once_with(ship.theme_id, ship.ship_class)
        panel.portrait_image.set_image.assert_called_once()
        assert panel.portrait_image.set_image.call_args.args[0].get_size() == (200, 200)

    def test_portrait_loads_from_file(self):
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

    def test_portrait_uses_fallback(self):
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
