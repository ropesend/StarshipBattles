"""
Tests for BattleResultsScreen testable logic.

PROJ-266 Phase 1: Coverage for init, _hp_color, scroll, return navigation,
event routing, and handle_resize.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# =============================================================================
# _hp_color Tests (module-level pure function)
# =============================================================================


class TestHpColor:
    """Tests for the _hp_color() color mapping function."""

    def test_zero_hp_returns_destroyed(self):
        from game.ui.screens.battle_results_screen import _hp_color, HP_DESTROYED
        assert _hp_color(0) == HP_DESTROYED

    def test_negative_hp_returns_destroyed(self):
        from game.ui.screens.battle_results_screen import _hp_color, HP_DESTROYED
        assert _hp_color(-5) == HP_DESTROYED

    def test_low_hp_returns_critical(self):
        from game.ui.screens.battle_results_screen import _hp_color, HP_CRITICAL
        assert _hp_color(10) == HP_CRITICAL

    def test_medium_hp_returns_damaged(self):
        from game.ui.screens.battle_results_screen import _hp_color, HP_DAMAGED
        assert _hp_color(30) == HP_DAMAGED

    def test_high_hp_returns_healthy(self):
        from game.ui.screens.battle_results_screen import _hp_color, HP_HEALTHY
        assert _hp_color(80) == HP_HEALTHY

    def test_full_hp_returns_healthy(self):
        from game.ui.screens.battle_results_screen import _hp_color, HP_HEALTHY
        assert _hp_color(100) == HP_HEALTHY


# =============================================================================
# BattleResultsScreen Tests
# =============================================================================


@pytest.fixture
def mock_results():
    """Create a mock BattleResults."""
    results = MagicMock()
    results.return_destination = "strategy"
    results.winner_team = 0
    results.tick_count = 500
    results.team_summaries = {0: MagicMock(), 1: MagicMock()}
    results.ship_results = []
    return results


@pytest.fixture
def screen(mock_results):
    """Create a BattleResultsScreen with mocked pygame."""
    with patch('game.ui.screens.battle_results_screen.get_font', return_value=MagicMock()):
        from game.ui.screens.battle_results_screen import BattleResultsScreen
        return BattleResultsScreen(1920, 1080, mock_results, scene_callback=MagicMock())


class TestBattleResultsScreenInit:
    """Tests for BattleResultsScreen initialization."""

    def test_stores_dimensions(self, screen):
        assert screen.screen_width == 1920
        assert screen.screen_height == 1080

    def test_stores_results(self, screen, mock_results):
        assert screen.results is mock_results

    def test_scroll_offsets_start_at_zero(self, screen):
        assert screen._scroll_offset_0 == 0
        assert screen._scroll_offset_1 == 0

    def test_stores_callback(self, screen):
        assert screen.scene_callback is not None


class TestScrollLogic:
    """Tests for _handle_scroll per-column scrolling."""

    def test_scroll_left_column(self, screen):
        """Scrolling with mouse on left half affects column 0."""
        screen._handle_scroll(30, mouse_x=100)  # Left of center
        assert screen._scroll_offset_0 == 30
        assert screen._scroll_offset_1 == 0

    def test_scroll_right_column(self, screen):
        """Scrolling with mouse on right half affects column 1."""
        screen._handle_scroll(30, mouse_x=1500)  # Right of center
        assert screen._scroll_offset_0 == 0
        assert screen._scroll_offset_1 == 30

    def test_scroll_clamps_to_zero(self, screen):
        """Scroll offset cannot go below 0."""
        screen._handle_scroll(-100, mouse_x=100)
        assert screen._scroll_offset_0 == 0

    def test_scroll_accumulates(self, screen):
        """Multiple scrolls accumulate."""
        screen._handle_scroll(20, mouse_x=100)
        screen._handle_scroll(30, mouse_x=100)
        assert screen._scroll_offset_0 == 50


class TestReturnNavigation:
    """Tests for return button and keyboard navigation."""

    def test_trigger_return_calls_callback(self, screen):
        """_trigger_return calls scene_callback with return_to_destination."""
        screen._trigger_return()
        screen.scene_callback.assert_called_once_with(
            "return_to_destination", destination="strategy"
        )

    def test_trigger_return_no_callback(self, mock_results):
        """_trigger_return is safe when no callback set."""
        with patch('game.ui.screens.battle_results_screen.get_font', return_value=MagicMock()):
            from game.ui.screens.battle_results_screen import BattleResultsScreen
            s = BattleResultsScreen(1920, 1080, mock_results, scene_callback=None)
            s._trigger_return()  # Should not raise

    def test_escape_key_triggers_return(self, screen):
        """Escape key triggers return."""
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE
        screen.handle_event(event)
        screen.scene_callback.assert_called_once()

    def test_enter_key_triggers_return(self, screen):
        """Enter key triggers return."""
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_RETURN
        screen.handle_event(event)
        screen.scene_callback.assert_called_once()


class TestHandleResize:
    """Tests for handle_resize()."""

    def test_resize_updates_dimensions(self, screen):
        screen.handle_resize(2560, 1440)
        assert screen.screen_width == 2560
        assert screen.screen_height == 1440
