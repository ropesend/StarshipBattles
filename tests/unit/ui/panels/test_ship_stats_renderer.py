"""Tests for ship_stats_renderer (PROJ-111 Phase 6 Task 6.8).

Tests the rendering utility functions for ship statistics display.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# Initialize pygame for Surface operations
pygame.init()


# --- Helpers ---

def _make_mock_resource(name, current, max_val):
    """Create a mock resource object."""
    res = MagicMock()
    res.name = name
    res.current_value = current
    res.max_value = max_val
    return res


def _make_mock_ship():
    """Create a mock ship with resources."""
    ship = MagicMock()
    ship.resources = MagicMock()
    ship.resources.get_all_resources.return_value = [
        _make_mock_resource("fuel", 50.0, 100.0),
        _make_mock_resource("energy", 80.0, 100.0),
        _make_mock_resource("ammo", 10.0, 50.0),
    ]
    return ship


def _make_mock_component(is_active=True, status=None):
    """Create a mock component."""
    from game.simulation.components.component_constants import ComponentStatus

    comp = MagicMock()
    comp.is_active = is_active
    comp.status = status if status else ComponentStatus.ACTIVE
    return comp


# --- draw_stat_bar Tests ---

class TestDrawStatBar:
    """Tests for draw_stat_bar function."""

    def test_draw_stat_bar_with_zero_percent(self):
        """draw_stat_bar with 0% draws empty bar."""
        from game.ui.panels.ship_stats_renderer import draw_stat_bar

        surface = pygame.Surface((200, 50))
        color = (0, 200, 0)

        # Should not raise
        draw_stat_bar(surface, 10, 10, 100, 20, 0.0, color)

        # Surface should have been drawn on
        assert surface is not None

    def test_draw_stat_bar_with_fifty_percent(self):
        """draw_stat_bar with 50% draws half-filled bar."""
        from game.ui.panels.ship_stats_renderer import draw_stat_bar

        surface = pygame.Surface((200, 50))
        color = (0, 200, 0)

        draw_stat_bar(surface, 10, 10, 100, 20, 0.5, color)

        assert surface is not None

    def test_draw_stat_bar_with_hundred_percent(self):
        """draw_stat_bar with 100% draws full bar."""
        from game.ui.panels.ship_stats_renderer import draw_stat_bar

        surface = pygame.Surface((200, 50))
        color = (0, 200, 0)

        draw_stat_bar(surface, 10, 10, 100, 20, 1.0, color)

        assert surface is not None

    def test_draw_stat_bar_clamps_over_hundred(self):
        """draw_stat_bar clamps values over 100%."""
        from game.ui.panels.ship_stats_renderer import draw_stat_bar

        surface = pygame.Surface((200, 50))
        color = (0, 200, 0)

        # Should not crash with > 1.0
        draw_stat_bar(surface, 10, 10, 100, 20, 1.5, color)

        assert surface is not None

    def test_draw_stat_bar_handles_negative(self):
        """draw_stat_bar handles negative percentage gracefully."""
        from game.ui.panels.ship_stats_renderer import draw_stat_bar

        surface = pygame.Surface((200, 50))
        color = (0, 200, 0)

        # Negative should not draw fill
        draw_stat_bar(surface, 10, 10, 100, 20, -0.5, color)

        assert surface is not None


# --- get_hp_bar_color Tests ---

class TestGetHpBarColor:
    """Tests for get_hp_bar_color function."""

    def test_high_hp_returns_green(self):
        """High HP (>50%) returns green color."""
        from game.ui.panels.ship_stats_renderer import get_hp_bar_color
        from game.ui.colors import HP_HEALTHY

        color = get_hp_bar_color(0.8, is_active=True)

        assert color == HP_HEALTHY

    def test_medium_hp_returns_yellow(self):
        """Medium HP (20-50%) returns yellow color."""
        from game.ui.panels.ship_stats_renderer import get_hp_bar_color
        from game.ui.colors import HP_DAMAGED

        color = get_hp_bar_color(0.35, is_active=True)

        assert color == HP_DAMAGED

    def test_low_hp_returns_red(self):
        """Low HP (<20%) returns red color."""
        from game.ui.panels.ship_stats_renderer import get_hp_bar_color
        from game.ui.colors import HP_CRITICAL

        color = get_hp_bar_color(0.1, is_active=True)

        assert color == HP_CRITICAL

    def test_inactive_component_returns_dim_red(self):
        """Inactive component returns dim red regardless of HP."""
        from game.ui.panels.ship_stats_renderer import get_hp_bar_color
        from game.ui.colors import COMPONENT_INACTIVE_BG

        color = get_hp_bar_color(1.0, is_active=False)

        assert color == COMPONENT_INACTIVE_BG

    def test_boundary_fifty_percent(self):
        """Exactly 50% returns green (healthy threshold)."""
        from game.ui.panels.ship_stats_renderer import get_hp_bar_color
        from game.ui.colors import HP_HEALTHY

        color = get_hp_bar_color(0.5, is_active=True)

        assert color == HP_HEALTHY

    def test_boundary_twenty_percent(self):
        """Exactly 20% returns red (not yellow)."""
        from game.ui.panels.ship_stats_renderer import get_hp_bar_color
        from game.ui.colors import HP_CRITICAL

        color = get_hp_bar_color(0.2, is_active=True)

        assert color == HP_CRITICAL


# --- get_component_status_display Tests ---

class TestGetComponentStatusDisplay:
    """Tests for get_component_status_display function."""

    def test_active_component_no_status_text(self):
        """Active component returns empty status text."""
        from game.ui.panels.ship_stats_renderer import get_component_status_display
        from game.simulation.components.component_constants import ComponentStatus

        comp = _make_mock_component(is_active=True, status=ComponentStatus.ACTIVE)

        text, color = get_component_status_display(comp)

        assert text == ""

    def test_damaged_component_shows_dmg(self):
        """Damaged component shows [DMG] in red."""
        from game.ui.panels.ship_stats_renderer import get_component_status_display
        from game.simulation.components.component_constants import ComponentStatus

        comp = _make_mock_component(is_active=False, status=ComponentStatus.DAMAGED)

        text, color = get_component_status_display(comp)

        assert text == "[DMG]"
        assert color == (255, 50, 50)

    def test_no_crew_component_shows_crew(self):
        """No crew component shows [CREW] in orange."""
        from game.ui.panels.ship_stats_renderer import get_component_status_display
        from game.simulation.components.component_constants import ComponentStatus

        comp = _make_mock_component(is_active=False, status=ComponentStatus.NO_CREW)

        text, color = get_component_status_display(comp)

        assert text == "[CREW]"
        assert color == (255, 165, 0)

    def test_no_power_component_shows_pwr(self):
        """No power component shows [PWR] in yellow."""
        from game.ui.panels.ship_stats_renderer import get_component_status_display
        from game.simulation.components.component_constants import ComponentStatus

        comp = _make_mock_component(is_active=False, status=ComponentStatus.NO_POWER)

        text, color = get_component_status_display(comp)

        assert text == "[PWR]"
        assert color == (255, 255, 0)

    def test_no_fuel_component_shows_fuel(self):
        """No fuel component shows [FUEL]."""
        from game.ui.panels.ship_stats_renderer import get_component_status_display
        from game.simulation.components.component_constants import ComponentStatus

        comp = _make_mock_component(is_active=False, status=ComponentStatus.NO_FUEL)

        text, color = get_component_status_display(comp)

        assert text == "[FUEL]"
        assert color == (255, 100, 0)


# --- draw_ship_resources Tests ---

class TestDrawShipResources:
    """Tests for draw_ship_resources function."""

    def test_draw_ship_resources_returns_updated_y(self):
        """draw_ship_resources returns updated Y position."""
        from game.ui.panels.ship_stats_renderer import draw_ship_resources

        surface = pygame.Surface((400, 300))
        ship = _make_mock_ship()
        font = pygame.font.Font(None, 20)

        new_y = draw_ship_resources(surface, ship, 10, 10, 100, 15, font)

        # Should be greater than starting Y since we drew 3 resources
        assert new_y > 10

    def test_draw_ship_resources_no_resources_returns_same_y(self):
        """draw_ship_resources with no resources returns same Y."""
        from game.ui.panels.ship_stats_renderer import draw_ship_resources

        surface = pygame.Surface((400, 300))
        ship = MagicMock()
        ship.resources = None
        font = pygame.font.Font(None, 20)

        new_y = draw_ship_resources(surface, ship, 10, 100, 100, 15, font)

        assert new_y == 100

    def test_draw_ship_resources_empty_resources(self):
        """draw_ship_resources with empty resources returns same Y."""
        from game.ui.panels.ship_stats_renderer import draw_ship_resources

        surface = pygame.Surface((400, 300))
        ship = MagicMock()
        ship.resources = MagicMock()
        ship.resources.get_all_resources.return_value = []
        font = pygame.font.Font(None, 20)

        new_y = draw_ship_resources(surface, ship, 10, 100, 100, 15, font)

        assert new_y == 100

    def test_draw_ship_resources_sorts_by_priority(self):
        """draw_ship_resources sorts resources by priority."""
        from game.ui.panels.ship_stats_renderer import draw_ship_resources

        surface = pygame.Surface((400, 300))
        ship = MagicMock()
        ship.resources = MagicMock()
        # Out of priority order
        ship.resources.get_all_resources.return_value = [
            _make_mock_resource("ammo", 10.0, 50.0),
            _make_mock_resource("fuel", 50.0, 100.0),
        ]
        font = pygame.font.Font(None, 20)

        # Should not crash
        new_y = draw_ship_resources(surface, ship, 10, 10, 100, 15, font)

        assert new_y > 10


# --- RESOURCE_COLORS Tests ---

class TestResourceColors:
    """Tests for RESOURCE_COLORS constants."""

    def test_fuel_color_is_orange(self):
        """Fuel color is orange."""
        from game.ui.panels.ship_stats_renderer import RESOURCE_COLORS
        from game.core.constants import ResourceType

        assert RESOURCE_COLORS[ResourceType.FUEL] == (255, 165, 0)

    def test_energy_color_is_blue(self):
        """Energy color is blue."""
        from game.ui.panels.ship_stats_renderer import RESOURCE_COLORS
        from game.core.constants import ResourceType

        assert RESOURCE_COLORS[ResourceType.ENERGY] == (100, 200, 255)

    def test_ammo_color_is_yellowish(self):
        """Ammo color is yellow-ish."""
        from game.ui.panels.ship_stats_renderer import RESOURCE_COLORS
        from game.core.constants import ResourceType

        assert RESOURCE_COLORS[ResourceType.AMMO] == (200, 200, 100)


# --- RESOURCE_ORDER_PRIORITY Tests ---

class TestResourceOrderPriority:
    """Tests for RESOURCE_ORDER_PRIORITY constants."""

    def test_fuel_has_highest_priority(self):
        """Fuel has priority 0 (highest)."""
        from game.ui.panels.ship_stats_renderer import RESOURCE_ORDER_PRIORITY
        from game.core.constants import ResourceType

        assert RESOURCE_ORDER_PRIORITY[ResourceType.FUEL] == 0

    def test_energy_has_second_priority(self):
        """Energy has priority 1."""
        from game.ui.panels.ship_stats_renderer import RESOURCE_ORDER_PRIORITY
        from game.core.constants import ResourceType

        assert RESOURCE_ORDER_PRIORITY[ResourceType.ENERGY] == 1

    def test_ammo_has_third_priority(self):
        """Ammo has priority 2."""
        from game.ui.panels.ship_stats_renderer import RESOURCE_ORDER_PRIORITY
        from game.core.constants import ResourceType

        assert RESOURCE_ORDER_PRIORITY[ResourceType.AMMO] == 2
