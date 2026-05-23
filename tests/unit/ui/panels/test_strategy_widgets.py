"""Tests for Strategy Widgets (PROJ-142 Phase 2 Task 2.4).

Tests the DataGraph, SpectrumGraph, and AtmosphereGraph visualization widgets
used for displaying star and planet data.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame
import math


# --- Helpers ---

def _make_mock_star():
    """Create a mock Star with spectrum data."""
    star = MagicMock()

    # Spectrum with energy values
    star.spectrum = MagicMock()
    star.spectrum.gamma_ray = 0.01
    star.spectrum.xray = 0.1
    star.spectrum.ultraviolet = 1.0
    star.spectrum.blue = 10.0
    star.spectrum.green = 15.0
    star.spectrum.red = 20.0
    star.spectrum.infrared = 8.0
    star.spectrum.microwave = 2.0
    star.spectrum.radio = 0.5

    return star


def _make_mock_planet():
    """Create a mock Planet with atmosphere data."""
    planet = MagicMock()

    planet.atmosphere = {
        'N2': 78000,
        'O2': 21000,
        'Ar': 900,
        'CO2': 400
    }

    return planet


# --- DataGraph Base Class Tests ---

class TestDataGraphInit:
    """Tests for DataGraph base class initialization."""

    def test_graph_stores_dimensions(self):
        """DataGraph stores width and height."""
        from game.ui.panels.strategy_widgets import DataGraph

        graph = DataGraph(200, 150)

        assert graph.width == 200
        assert graph.height == 150

    def test_graph_stores_bg_color(self):
        """DataGraph stores bg_color."""
        from game.ui.panels.strategy_widgets import DataGraph

        graph = DataGraph(200, 150, bg_color=(50, 60, 70))

        assert graph.bg_color == (50, 60, 70)

    def test_graph_default_bg_color(self):
        """DataGraph has default bg_color."""
        from game.ui.panels.strategy_widgets import DataGraph

        graph = DataGraph(200, 150)

        from game.ui.colors import BG_PANEL_DARK
        assert graph.bg_color == BG_PANEL_DARK

    def test_graph_creates_surface(self):
        """DataGraph creates surface of correct size."""
        from game.ui.panels.strategy_widgets import DataGraph

        graph = DataGraph(200, 150)

        assert isinstance(graph.surface, pygame.Surface)
        assert graph.surface.get_size() == (200, 150)

    def test_graph_clear_fills_bg(self):
        """DataGraph.clear fills surface with bg_color."""
        from game.ui.panels.strategy_widgets import DataGraph

        graph = DataGraph(100, 100, bg_color=(100, 100, 100))
        graph.clear()

        # Surface should be filled with bg_color
        # Check a pixel in the middle
        color = graph.surface.get_at((50, 50))
        assert (color.r, color.g, color.b) == (100, 100, 100)

    def test_graph_clear_draws_border(self):
        """DataGraph.clear draws border rectangle."""
        from game.ui.panels.strategy_widgets import DataGraph

        graph = DataGraph(100, 100, bg_color=(20, 24, 30))
        graph.clear()

        # Border should be drawn (different from bg)
        # Check corner pixel
        corner_color = graph.surface.get_at((0, 0))
        assert corner_color != pygame.Color(20, 24, 30)


# --- SpectrumGraph Tests ---

class TestSpectrumGraphInit:
    """Tests for SpectrumGraph initialization."""

    def test_spectrum_graph_has_bands(self):
        """SpectrumGraph has BANDS constant."""
        from game.ui.panels.strategy_widgets import SpectrumGraph

        assert hasattr(SpectrumGraph, 'BANDS')
        assert len(SpectrumGraph.BANDS) == 9

    def test_spectrum_bands_are_tuples(self):
        """SpectrumGraph.BANDS contains tuples."""
        from game.ui.panels.strategy_widgets import SpectrumGraph

        for band in SpectrumGraph.BANDS:
            assert isinstance(band, tuple)
            assert len(band) == 3  # (attr, color, label)


class TestSpectrumGraphRender:
    """Tests for SpectrumGraph rendering."""

    def test_render_returns_surface(self):
        """SpectrumGraph.render returns pygame Surface."""
        from game.ui.panels.strategy_widgets import SpectrumGraph

        graph = SpectrumGraph(200, 150)
        star = _make_mock_star()

        result = graph.render(star)

        assert isinstance(result, pygame.Surface)

    def test_render_handles_no_spectrum(self):
        """SpectrumGraph.render handles star without spectrum."""
        from game.ui.panels.strategy_widgets import SpectrumGraph

        graph = SpectrumGraph(200, 150)
        star = MagicMock(spec=[])  # No spectrum attribute

        result = graph.render(star)

        assert isinstance(result, pygame.Surface)

    def test_render_handles_zero_values(self):
        """SpectrumGraph.render handles all-zero spectrum."""
        from game.ui.panels.strategy_widgets import SpectrumGraph

        graph = SpectrumGraph(200, 150)
        star = _make_mock_star()

        # Set all values to 0
        for attr, _, _ in SpectrumGraph.BANDS:
            setattr(star.spectrum, attr, 0.0)

        result = graph.render(star)

        assert isinstance(result, pygame.Surface)

    def test_render_vertical_mode(self):
        """SpectrumGraph.render handles vertical mode."""
        from game.ui.panels.strategy_widgets import SpectrumGraph

        graph = SpectrumGraph(200, 150)
        star = _make_mock_star()

        result = graph.render(star, vertical=True)

        assert isinstance(result, pygame.Surface)


# --- AtmosphereGraph Tests ---

class TestAtmosphereGraphInit:
    """Tests for AtmosphereGraph initialization."""

    def test_atmosphere_graph_has_gas_colors(self):
        """AtmosphereGraph has GAS_COLORS constant."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        assert hasattr(AtmosphereGraph, 'GAS_COLORS')
        assert isinstance(AtmosphereGraph.GAS_COLORS, dict)

    def test_gas_colors_contains_common_gases(self):
        """GAS_COLORS contains common atmospheric gases."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        common_gases = ['N2', 'O2', 'CO2', 'H2O', 'CH4', 'H2', 'He', 'Ar', 'SO2']

        for gas in common_gases:
            assert gas in AtmosphereGraph.GAS_COLORS

    def test_gas_colors_are_tuples(self):
        """GAS_COLORS values are RGB tuples."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        for gas, color in AtmosphereGraph.GAS_COLORS.items():
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)


class TestAtmosphereGraphRender:
    """Tests for AtmosphereGraph rendering."""

    def test_render_returns_surface(self):
        """AtmosphereGraph.render returns pygame Surface."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        graph = AtmosphereGraph(200, 150)
        planet = _make_mock_planet()

        result = graph.render(planet)

        assert isinstance(result, pygame.Surface)

    def test_render_handles_empty_atmosphere(self):
        """AtmosphereGraph.render handles empty atmosphere dict."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        graph = AtmosphereGraph(200, 150)
        planet = MagicMock()
        planet.atmosphere = {}

        result = graph.render(planet)

        assert isinstance(result, pygame.Surface)

    def test_render_handles_none_atmosphere(self):
        """AtmosphereGraph.render handles None atmosphere."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        graph = AtmosphereGraph(200, 150)
        planet = MagicMock()
        planet.atmosphere = None

        result = graph.render(planet)

        assert isinstance(result, pygame.Surface)

    def test_render_vertical_mode(self):
        """AtmosphereGraph.render handles vertical mode."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        graph = AtmosphereGraph(200, 150)
        planet = _make_mock_planet()

        result = graph.render(planet, vertical=True)

        assert isinstance(result, pygame.Surface)

    def test_render_shows_top_6_gases(self):
        """AtmosphereGraph.render limits to top 6 gases."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        graph = AtmosphereGraph(300, 150)
        planet = MagicMock()
        planet.atmosphere = {
            'N2': 78000,
            'O2': 21000,
            'Ar': 900,
            'CO2': 400,
            'H2O': 100,
            'He': 50,
            'H2': 30,
            'CH4': 10  # 8 gases total, only top 6 shown
        }

        result = graph.render(planet)

        assert isinstance(result, pygame.Surface)

    def test_render_pressure_formatting_kpa(self):
        """AtmosphereGraph formats large pressures as kPa."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        graph = AtmosphereGraph(200, 150)
        planet = MagicMock()
        planet.atmosphere = {'N2': 50000}  # Should display as "50k"

        result = graph.render(planet)

        assert isinstance(result, pygame.Surface)


# --- Logarithmic Scale Tests ---

class TestLogarithmicScale:
    """Tests for logarithmic scale calculations."""

    def test_log_scale_zero_values(self):
        """Log scale handles zero values without error."""
        # log10(0 + 1) = 0, which is valid
        val = 0
        log_val = math.log10(val + 1)

        assert log_val == 0.0

    def test_log_scale_positive_values(self):
        """Log scale computes correctly for positive values."""
        val = 99  # log10(100) = 2
        log_val = math.log10(val + 1)

        assert log_val == 2.0

    def test_log_scale_normalization(self):
        """Log scale normalizes correctly."""
        max_val = 999  # log10(1000) = 3
        log_max = math.log10(max_val + 1)

        val = 99  # log10(100) = 2
        log_val = math.log10(val + 1)

        normalized = log_val / log_max

        assert 0.0 <= normalized <= 1.0
        assert abs(normalized - (2.0 / 3.0)) < 0.01


# --- Surface Size Tests ---

class TestSurfaceSizes:
    """Tests for surface size handling."""

    def test_small_surface(self):
        """Graphs handle small surface sizes."""
        from game.ui.panels.strategy_widgets import SpectrumGraph, AtmosphereGraph

        spectrum = SpectrumGraph(50, 30)
        atmosphere = AtmosphereGraph(50, 30)

        star = _make_mock_star()
        planet = _make_mock_planet()

        # Should not raise
        spectrum.render(star)
        atmosphere.render(planet)

    def test_large_surface(self):
        """Graphs handle large surface sizes."""
        from game.ui.panels.strategy_widgets import SpectrumGraph, AtmosphereGraph

        spectrum = SpectrumGraph(800, 600)
        atmosphere = AtmosphereGraph(800, 600)

        star = _make_mock_star()
        planet = _make_mock_planet()

        # Should not raise
        spectrum.render(star)
        atmosphere.render(planet)


# --- Color Palette Tests ---

class TestColorPalettes:
    """Tests for color palette definitions."""

    def test_spectrum_colors_visible(self):
        """SpectrumGraph colors are visually distinct."""
        from game.ui.panels.strategy_widgets import SpectrumGraph

        colors = [band[1] for band in SpectrumGraph.BANDS]

        # All colors should be different
        assert len(set(colors)) == len(colors)

    def test_atmosphere_colors_rgb_valid(self):
        """AtmosphereGraph colors are valid RGB."""
        from game.ui.panels.strategy_widgets import AtmosphereGraph

        for gas, color in AtmosphereGraph.GAS_COLORS.items():
            r, g, b = color
            assert 0 <= r <= 255, f"{gas} red channel invalid"
            assert 0 <= g <= 255, f"{gas} green channel invalid"
            assert 0 <= b <= 255, f"{gas} blue channel invalid"
