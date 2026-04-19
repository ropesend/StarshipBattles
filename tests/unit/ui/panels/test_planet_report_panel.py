"""Tests for PlanetReportPanel (PROJ-142 Phase 2 Task 2.2).

Tests the planet report panel widget for displaying planet information
with atmosphere graphs and resource grids.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import pygame


# --- Helpers ---

def _make_mock_planet():
    """Create a mock Planet with typical attributes."""
    planet = MagicMock()

    planet.name = "Terra Nova"
    planet.planet_type = MagicMock()
    planet.planet_type.name = "TERRESTRIAL"
    planet.atmosphere = {
        'N2': 78000,
        'O2': 21000,
        'Ar': 900,
        'CO2': 40
    }
    planet.deposits = {
        'minerals': {'quantity': 5000, 'quality': 0.8},
        'metals': {'quantity': 3000, 'quality': 0.6},
        'organics': {'quantity': 2000, 'quality': 0.9},
        'exotics': {'quantity': 100, 'quality': 0.3},
        'volatiles': {'quantity': 1500, 'quality': 0.5}
    }
    planet.facilities = []
    planet.owner_id = None

    return planet


def _make_mock_facility(name: str, design_id: str):
    """Create a mock facility."""
    facility = MagicMock()
    facility.name = name
    facility.design_id = design_id
    facility.is_operational = True
    facility.design_data = {}
    return facility


# --- PlanetReportPanel Import Tests ---

# --- Complexes List Tests ---

class TestComplexesList:
    """Tests for complexes list display."""

    def test_complexes_list_disabled_returns_early(self):
        """_update_complexes_list returns early if disabled."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel.complexes_container = None
        panel.complex_items = []

        # Should not raise
        panel._update_complexes_list()


# --- Number Formatting Tests ---

class TestNumberFormatting:
    """Tests for compact number formatting (delegated to shared utility)."""

    def test_format_small_number(self):
        """Numbers < 1000 display as integers."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(500) == "500"

    def test_format_thousand(self):
        """Numbers 1000-999999 display with 'k' suffix."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(5000) == "5k"

    def test_format_large_thousand(self):
        """Large thousands format correctly."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(500000) == "500k"

    def test_format_million(self):
        """Numbers >= 1000000 display with 'M' suffix."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(5000000) == "5.0M"

    def test_format_million_decimal(self):
        """Millions display with one decimal place."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(1500000) == "1.5M"


# --- Resource Grid Tests ---

class TestResourceGrid:
    """Tests for resource grid functionality."""

    def test_resource_grid_items_list_exists(self):
        """_resource_grid_items is a list."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._resource_grid_items = []

        assert isinstance(panel._resource_grid_items, list)

    def test_update_resource_grid_calls_build(self):
        """_update_resource_grid calls _build_resource_grid."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._build_resource_grid = MagicMock()

        panel._update_resource_grid()

        panel._build_resource_grid.assert_called_once()


# --- Portrait Tests ---

class TestPortrait:
    """Tests for planet portrait generation."""

    def test_portrait_uses_provided_surface(self):
        """_update_portrait uses provided portrait_surface."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        portrait = pygame.Surface((150, 150))
        panel.portrait_image = MagicMock()
        panel.planet = _make_mock_planet()

        panel._update_portrait(portrait)

        panel.portrait_image.set_image.assert_called_once()

    def test_portrait_generates_placeholder(self):
        """_update_portrait generates placeholder when no surface."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel.portrait_image = MagicMock()
        panel.planet = _make_mock_planet()

        panel._update_portrait(None)

        panel.portrait_image.set_image.assert_called_once()


# --- Height Required Tests ---

class TestHeightRequired:
    """Tests for get_height_required method."""

    def test_height_includes_resource_panel(self):
        """get_height_required includes RESOURCE_PANEL_HEIGHT."""
        from game.ui.panels.planet_report_panel import (
            PlanetReportPanel,
            RESOURCE_PANEL_HEIGHT
        )

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        height = panel.get_height_required()

        assert height == 350 + RESOURCE_PANEL_HEIGHT

    def test_height_is_integer(self):
        """get_height_required returns integer."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        height = panel.get_height_required()

        assert isinstance(height, int)


# --- Kill / Cleanup Tests ---

class TestPanelKill:
    """Tests for panel cleanup."""

    def test_kill_clears_resource_items(self):
        """kill clears resource grid items."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        item = MagicMock()
        panel._resource_grid_items = [item]
        panel.resource_panel = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        item.kill.assert_called_once()

    def test_kill_destroys_resource_panel(self):
        """kill destroys resource_panel."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._resource_grid_items = []
        panel.resource_panel = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        panel.resource_panel.kill.assert_called_once()

    def test_kill_destroys_main_panel(self):
        """kill destroys main panel."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._resource_grid_items = []
        panel.resource_panel = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        panel.panel.kill.assert_called_once()


# --- compute_planet_production Tests ---

class TestComputePlanetProduction:
    """Tests for compute_planet_production function."""

    def test_unowned_planet_returns_empty(self, mock_registries):
        """Unowned planet returns empty dict."""
        from game.strategy.services.planet_economy_projector import compute_planet_production

        planet = _make_mock_planet()
        planet.owner_id = None

        result = compute_planet_production(planet, mock_registries)

        assert result == {}

    def test_function_exists(self):
        """compute_planet_production function exists."""
        from game.strategy.services.planet_economy_projector import compute_planet_production

        assert callable(compute_planet_production)

    def test_function_accepts_planet(self, mock_registries):
        """compute_planet_production accepts planet argument."""
        from game.strategy.services.planet_economy_projector import compute_planet_production

        planet = _make_mock_planet()
        planet.owner_id = None

        # Should not raise
        result = compute_planet_production(planet, mock_registries)

        assert isinstance(result, dict)


# --- _get_harvester_info Tests ---

class TestGetHarvesterInfo:
    """Tests for _get_harvester_info helper."""

    def test_inline_harvester_returned(self):
        """Inline ResourceHarvester ability is returned."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        comp = {
            'id': 'mining_facility',
            'abilities': {
                'ResourceHarvester': {
                    'resource_type': 'minerals',
                    'base_harvest_rate': 10.0
                }
            }
        }

        result = _get_harvester_info(comp, None)

        assert result is not None
        assert result['resource_type'] == 'minerals'

    def test_non_dict_returns_none(self):
        """Non-dict component returns None."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        result = _get_harvester_info("not_a_dict", None)

        assert result is None

    def test_no_abilities_returns_none(self):
        """Component without abilities key returns None (falls to registry lookup)."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        comp = {'id': 'basic_component'}
        registries = MagicMock()
        registries.components.get.return_value = None

        result = _get_harvester_info(comp, registries)

        assert result is None
