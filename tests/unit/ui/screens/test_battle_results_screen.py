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

    # PROJ-480 Task 3.34: parametrize 6 _hp_color band tests on
    # (hp, expected_color_constant_name). The constants are imported
    # inside the test body to keep the original lazy-import pattern.
    @pytest.mark.parametrize(
        "hp, color_constant",
        [
            (0, "HP_DESTROYED"),
            (-5, "HP_DESTROYED"),
            (10, "HP_CRITICAL"),
            (30, "HP_DAMAGED"),
            (80, "HP_HEALTHY"),
            (100, "HP_HEALTHY"),
        ],
        ids=["zero", "negative", "low_critical", "medium_damaged",
             "high_healthy", "full_healthy"],
    )
    def test_hp_color_band(self, hp, color_constant):
        from game.ui.screens import battle_results_screen as brs
        expected = getattr(brs, color_constant)
        assert brs._hp_color(hp) == expected


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


class TestShieldsRenderedOnResultsCard:
    """PROJ-271 Phase 8 Task 8.1: shield numbers must appear on the
    per-ship results card. Previously `ShipResult.max_shields` /
    `current_shields` were populated but hidden — user could not
    observe PROJ-270/271 modifier effects."""

    def _ship_result(self, **overrides):
        """Build a ShipResult with sensible defaults."""
        from game.ui.screens.battle_results_data import ShipResult, WeaponStats
        defaults = dict(
            name="TestShip",
            team_id=0,
            is_alive=True,
            is_derelict=False,
            hp=400.0,
            max_hp=500.0,
            hp_percent=80.0,
            current_shields=300.0,
            max_shields=575.0,
            weapons=[],
            total_shots_fired=0,
            total_shots_hit=0,
            overall_accuracy=0.0,
        )
        defaults.update(overrides)
        return ShipResult(**defaults)

    def test_shields_row_rendered_on_ship_card(self, screen):
        """`_draw_ship_card` must call small_font.render with a string
        containing both current and max shields."""
        import pygame
        # Patch pygame.draw calls to no-op so we can focus on text.
        with patch("pygame.draw.rect"):
            ship = self._ship_result()
            # Intercept all text renders.
            screen._small_font.render = MagicMock(return_value=MagicMock(
                get_width=lambda: 50, get_height=lambda: 12,
            ))
            screen._body_font.render = MagicMock(return_value=MagicMock(
                get_width=lambda: 50, get_height=lambda: 16,
            ))
            mock_screen = MagicMock()
            screen._draw_ship_card(mock_screen, 0, 0, 300, ship)

            rendered_strings = [
                call.args[0]
                for call in screen._small_font.render.call_args_list
            ]
            shields_lines = [
                s for s in rendered_strings
                if "Shields" in s or "shields" in s
            ]
            assert shields_lines, (
                f"Expected a shields row on ship card; got rendered strings: "
                f"{rendered_strings}"
            )
            # At least one line should contain both the current and max values.
            combined = " ".join(shields_lines)
            assert "300" in combined and "575" in combined, (
                f"Expected shield numbers 300/575 in render output; got: "
                f"{shields_lines}"
            )
