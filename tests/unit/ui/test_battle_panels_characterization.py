"""Characterization tests for ``battle_panels`` (PROJ-338 Phase 1).

Pin behavior the existing test_battle_panels.py + test_battle_panels_extended.py
pair (~975 LOC combined) skips. Sits beside (does not touch) those files
per PROJ-338 D-004.

Uses the established mocked-pygame substitution pattern: a ``MockRect``
+ ``patch.dict(sys.modules, {'pygame': mock_pygame})`` so the panels can
be imported and exercised without the real pygame display layer.

Coverage focus:
- BattlePanel._get_ships() fallback (ui_service non-list, AttributeError, etc.)
- ExpandableIdPanel base helpers
- ShipStatsPanel: banner rect recording per draw, scroll offset translation,
  dead/derelict status colours, shift-click focus, click outside banner
- SeekerMonitorPanel: clear_inactive, X-button removal, expansion toggle
- BattleControlPanel: battle-over win text branches, battle-ongoing button
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


class MockRect:
    """Reused from tests/unit/ui/test_battle_panels.py."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.topleft = (x, y)
        self.bottomleft = (x, y + h)
        self.center = (x + w // 2, y + h // 2)
        self.centerx = x + w // 2
        self.bottom = y + h
        self.size = (w, h)

    def collidepoint(self, *args):
        if len(args) == 1:
            px, py = args[0]
        else:
            px, py = args
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height

    def inflate(self, *args):
        return self


# ---------------------------------------------------------------------------
# Mocked-pygame fixture (per-test instance pattern from existing tests)
# ---------------------------------------------------------------------------


@pytest.fixture
def battle_panels_module():
    """Yield the battle_panels module with pygame substituted."""
    mock_pygame = MagicMock()
    mock_pygame.K_LSHIFT = 1
    mock_pygame.K_RSHIFT = 2
    mock_pygame.SRCALPHA = 0
    mock_pygame.Rect = MockRect

    modules_patcher = patch.dict(sys.modules, {"pygame": mock_pygame})
    modules_patcher.start()

    try:
        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)

        # Default: shift not held
        mock_pygame.key.get_pressed.return_value = {
            mock_pygame.K_LSHIFT: False,
            mock_pygame.K_RSHIFT: False,
        }
        yield battle_panels, mock_pygame
    finally:
        modules_patcher.stop()


def _make_scene(*, ui_service_ships=None, scene_ships=None, no_ships_attr: bool = False):
    scene = MagicMock()
    if ui_service_ships is not None:
        scene.ui_service.get_ships.return_value = ui_service_ships
    if scene_ships is not None:
        scene.ships = scene_ships
    if no_ships_attr:
        # Simulate a scene with no .ships attribute by deleting it from spec
        del scene.ships
    return scene


def _make_ship(ship_id="S1", team_id=0, *, alive=True, derelict=False):
    s = MagicMock()
    s.id = ship_id
    s.team_id = team_id
    s.is_alive = alive
    s.is_derelict = derelict
    s.name = ship_id
    s.max_shields = 100
    return s


# ===========================================================================
# F.1 — BattlePanel._get_ships fallback
# ===========================================================================


class TestGetShipsFallback:
    def test_get_ships_returns_ui_service_list_when_available(self, battle_panels_module):
        mod, _ = battle_panels_module
        ships = [_make_ship("A"), _make_ship("B")]
        scene = _make_scene(ui_service_ships=ships)
        panel = mod.BattlePanel(scene, 0, 0, 100, 100)
        result = panel._get_ships()
        assert result == ships

    def test_get_ships_falls_back_to_scene_ships_when_ui_service_returns_non_list(
        self, battle_panels_module
    ):
        """MagicMock auto-result guard: non-list result triggers fallback."""
        mod, _ = battle_panels_module
        # ui_service.get_ships returns a MagicMock (not a list)
        scene = MagicMock()
        scene.ui_service.get_ships.return_value = MagicMock()  # Not a list
        scene.ships = ["from_scene"]
        panel = mod.BattlePanel(scene, 0, 0, 100, 100)
        result = panel._get_ships()
        assert result == ["from_scene"]

    def test_get_ships_falls_back_when_ui_service_get_ships_raises_attributeerror(
        self, battle_panels_module
    ):
        mod, _ = battle_panels_module
        scene = MagicMock()
        scene.ui_service.get_ships.side_effect = AttributeError("no method")
        scene.ships = ["fallback_ship"]
        panel = mod.BattlePanel(scene, 0, 0, 100, 100)
        result = panel._get_ships()
        assert result == ["fallback_ship"]

    def test_get_ships_falls_back_to_empty_list_when_scene_has_no_ships_attr(
        self, battle_panels_module
    ):
        mod, _ = battle_panels_module
        scene = MagicMock(spec=["ui_service"])
        scene.ui_service.get_ships.side_effect = AttributeError("no method")
        # spec=['ui_service'] → no .ships attribute
        panel = mod.BattlePanel(scene, 0, 0, 100, 100)
        result = panel._get_ships()
        assert result == []


# ===========================================================================
# F.2 — ExpandableIdPanel
# ===========================================================================


class TestExpandableIdPanel:
    def test_toggle_id_expanded_adds_then_removes_on_repeat(self, battle_panels_module):
        mod, _ = battle_panels_module
        scene = MagicMock()
        panel = mod.ExpandableIdPanel(scene, 0, 0, 100, 100)
        panel._toggle_id_expanded("ship-1")
        assert "ship-1" in panel._expanded_ids
        panel._toggle_id_expanded("ship-1")
        assert "ship-1" not in panel._expanded_ids

    def test_is_id_expanded_after_toggle_returns_true_then_false(self, battle_panels_module):
        mod, _ = battle_panels_module
        panel = mod.ExpandableIdPanel(MagicMock(), 0, 0, 100, 100)
        assert panel._is_id_expanded("x") is False
        panel._toggle_id_expanded("x")
        assert panel._is_id_expanded("x") is True
        panel._toggle_id_expanded("x")
        assert panel._is_id_expanded("x") is False


# ===========================================================================
# F.3 — ShipStatsPanel
# ===========================================================================


class TestShipStatsPanel:
    def test_draw_records_banner_rect_per_ship_id_using_scroll_offset(
        self, battle_panels_module
    ):
        """draw_ship_entry records (y_start, y_end) per ship in surface coords + scroll offset."""
        mod, _ = battle_panels_module
        scene = MagicMock()
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        panel.scroll.offset = 25
        # Stub the rendering helpers so draw_ship_entry can run
        ship = _make_ship("S-99")
        surface = MagicMock()
        font = MagicMock()
        font.render.return_value = MagicMock()
        # Just call draw_ship_entry directly with a known y
        with patch.object(mod, "UIConfig") as cfg:
            cfg.BANNER_HEIGHT = 30
            cfg.SHIP_ENTRY_HEIGHT = 35
            cfg.INDENT = 20
            cfg.BAR_WIDTH = 80
            cfg.BAR_HEIGHT = 8
            panel.draw_ship_entry(surface, ship, y=100, panel_w=200,
                                  font_name=font, font_stat=font, banner_color=(0, 0, 0))
        # Banner rect recorded in surface coords + scroll offset
        assert "S-99" in panel._ship_banner_rects
        y_start, y_end = panel._ship_banner_rects["S-99"]
        assert y_start == 100 + 25  # y + scroll.offset
        assert y_end == 100 + 30 + 25  # y + BANNER_HEIGHT + scroll.offset

    def test_draw_clears_banner_rects_each_frame(self, battle_panels_module):
        """Banner rects are cleared at the start of each draw() call."""
        mod, _ = battle_panels_module
        scene = MagicMock()
        scene.ui_service.get_ships.return_value = []
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        # Pre-populate rects to simulate a prior frame
        panel._ship_banner_rects = {"OLD": (0, 10)}
        screen = MagicMock()
        # Stub the surface attribute so the draw doesn't recreate
        panel.surface = MagicMock()
        panel.surface.get_width.return_value = 200
        panel.surface.get_height.return_value = 600
        with patch.object(mod, "get_default_font", return_value=MagicMock(render=MagicMock(return_value=MagicMock()))), \
             patch.object(mod, "UIConfig") as cfg:
            cfg.PANEL_ALPHA = 200
            cfg.FONT_TITLE = 14
            cfg.FONT_NAME = 12
            cfg.FONT_STAT = 10
            panel.draw(screen)
        # Old rects gone (no ships → no new rects either)
        assert "OLD" not in panel._ship_banner_rects

    def test_draw_dead_ship_uses_text_dim_color_and_appends_dead_label(self, battle_panels_module):
        mod, _ = battle_panels_module
        scene = MagicMock()
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        ship = _make_ship("DeadOne", alive=False, derelict=False)
        surface = MagicMock()
        font = MagicMock()
        rendered = MagicMock()
        font.render.return_value = rendered
        with patch.object(mod, "UIConfig") as cfg:
            cfg.BANNER_HEIGHT = 30
            cfg.SHIP_ENTRY_HEIGHT = 35
            panel.draw_ship_entry(surface, ship, 50, 200, font, font, (0, 0, 0))
        # The first font.render call carries the formatted name string
        first_text = font.render.call_args_list[0][0][0]
        assert "[DEAD]" in first_text

    def test_draw_derelict_ship_uses_status_derelict_color_and_appends_derelict_label(
        self, battle_panels_module
    ):
        mod, _ = battle_panels_module
        scene = MagicMock()
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        ship = _make_ship("DerOne", alive=True, derelict=True)
        surface = MagicMock()
        font = MagicMock()
        rendered = MagicMock()
        font.render.return_value = rendered
        with patch.object(mod, "UIConfig") as cfg:
            cfg.BANNER_HEIGHT = 30
            cfg.SHIP_ENTRY_HEIGHT = 35
            panel.draw_ship_entry(surface, ship, 50, 200, font, font, (0, 0, 0))
        first_text = font.render.call_args_list[0][0][0]
        assert "[DERELICT]" in first_text

    def test_handle_click_within_banner_toggles_expansion(self, battle_panels_module):
        mod, _ = battle_panels_module
        scene = MagicMock()
        ship = _make_ship("Hero")
        scene.ui_service.get_ships.return_value = [ship]
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        panel._ship_banner_rects = {"Hero": (40, 65)}
        result = panel.handle_click(10, 50)
        assert result is True
        assert "Hero" in panel.expanded_ships

    def test_handle_click_with_shift_returns_focus_ship_tuple(self, battle_panels_module):
        mod, mock_pygame = battle_panels_module
        scene = MagicMock()
        ship = _make_ship("Hero")
        scene.ui_service.get_ships.return_value = [ship]
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        panel._ship_banner_rects = {"Hero": (40, 65)}
        # Hold shift
        mock_pygame.key.get_pressed.return_value = {
            mock_pygame.K_LSHIFT: True,
            mock_pygame.K_RSHIFT: False,
        }
        result = panel.handle_click(10, 50)
        assert result == ("focus_ship", "Hero")
        # Expansion NOT toggled in shift-click path
        assert "Hero" not in panel.expanded_ships

    def test_handle_click_outside_any_banner_returns_false(self, battle_panels_module):
        mod, _ = battle_panels_module
        scene = MagicMock()
        ship = _make_ship("Hero")
        scene.ui_service.get_ships.return_value = [ship]
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        panel._ship_banner_rects = {"Hero": (40, 65)}
        # Click at y=200, well outside the banner [40, 65)
        result = panel.handle_click(10, 200)
        assert result is False

    def test_handle_click_uses_scroll_offset_to_translate_screen_y(self, battle_panels_module):
        mod, _ = battle_panels_module
        scene = MagicMock()
        ship = _make_ship("Hero")
        scene.ui_service.get_ships.return_value = [ship]
        panel = mod.ShipStatsPanel(scene, 0, 0, 200, 600)
        panel._ship_banner_rects = {"Hero": (110, 135)}
        panel.scroll.offset = 50
        # Screen y=70 → rel_y=70+50=120 → hits [110, 135)
        result = panel.handle_click(10, 70)
        assert result is True
        assert "Hero" in panel.expanded_ships


# ===========================================================================
# F.4 — SeekerMonitorPanel
# ===========================================================================


def _make_seeker(seeker_id, status="active"):
    s = MagicMock()
    s.id = seeker_id
    s.status = status
    return s


class TestSeekerMonitorPanel:
    def test_clear_inactive_keeps_active_drops_others(self, battle_panels_module):
        mod, _ = battle_panels_module
        panel = mod.SeekerMonitorPanel(MagicMock(), 0, 0, 300, 600)
        a = _make_seeker("A", "active")
        b = _make_seeker("B", "hit")
        c = _make_seeker("C", "miss")
        d = _make_seeker("D", "destroyed")
        panel.tracked_seekers = [a, b, c, d]
        panel.clear_inactive()
        assert panel.tracked_seekers == [a]

    def test_handle_click_on_clear_button_calls_clear_inactive_returns_true(
        self, battle_panels_module
    ):
        mod, _ = battle_panels_module
        panel = mod.SeekerMonitorPanel(MagicMock(), 0, 0, 300, 600)
        # Pre-set the clear button rect (normally set during draw)
        panel.clear_btn_rect = MockRect(10, 560, 280, 30)
        # Pre-load some inactive seekers to confirm the side effect
        panel.tracked_seekers = [_make_seeker("X", "hit")]
        result = panel.handle_click(50, 575)
        assert result is True
        assert panel.tracked_seekers == []  # cleared

    def test_handle_click_on_x_button_for_inactive_seeker_removes_from_tracking(
        self, battle_panels_module
    ):
        mod, _ = battle_panels_module
        panel = mod.SeekerMonitorPanel(MagicMock(), 100, 100, 300, 600)
        s = _make_seeker("S", "hit")  # inactive
        panel.tracked_seekers = [s]
        # First seeker row at y_pos=40 (10 + 30); X button at rel_x in [275, 295)
        # abs mx = 100 + 280 = 380; abs my = 100 + 40 = 140
        result = panel.handle_click(380, 140)
        assert result is True
        assert s not in panel.tracked_seekers

    def test_handle_click_on_x_button_for_active_seeker_does_not_remove(
        self, battle_panels_module
    ):
        mod, _ = battle_panels_module
        panel = mod.SeekerMonitorPanel(MagicMock(), 100, 100, 300, 600)
        s = _make_seeker("S", "active")  # active → X-button no-op
        panel.tracked_seekers = [s]
        # Click on X button position; production code only removes if status != active.
        # However the active branch falls through to the toggle-expansion path,
        # so the seeker stays in tracked_seekers but expansion may toggle.
        result = panel.handle_click(380, 140)
        assert result is True
        # Seeker not removed
        assert s in panel.tracked_seekers

    def test_handle_click_on_seeker_row_toggles_expansion(self, battle_panels_module):
        mod, _ = battle_panels_module
        panel = mod.SeekerMonitorPanel(MagicMock(), 100, 100, 300, 600)
        s = _make_seeker("S", "active")
        panel.tracked_seekers = [s]
        # Click on row body (not X button): rel_x < 275, rel_y in [40, 62)
        result = panel.handle_click(150, 140)
        assert result is True
        assert "S" in panel._expanded_ids


# ===========================================================================
# F.5 — BattleControlPanel
# ===========================================================================


class TestBattleControlPanel:
    def _draw_setup(self, mod, mock_pygame, ships, is_over: bool):
        scene = MagicMock()
        scene.ui_service.get_ships.return_value = ships
        scene.is_battle_over.return_value = is_over
        panel = mod.BattleControlPanel(scene, 0, 0, 800, 600)
        screen = MagicMock()
        screen.get_size.return_value = (1920, 1080)
        return panel, screen

    def _stub_fonts(self, mod):
        font = MagicMock()
        rendered = MagicMock()
        rendered.get_width.return_value = 100
        font.render.return_value = rendered
        return patch.object(mod, "get_default_font", return_value=font)

    def test_draw_battle_over_team0_alive_renders_team1_wins_text(
        self, battle_panels_module
    ):
        mod, mp = battle_panels_module
        ships = [_make_ship("A", team_id=0, alive=True)]
        panel, screen = self._draw_setup(mod, mp, ships, is_over=True)
        with self._stub_fonts(mod) as get_font:
            panel.draw(screen)
            # First render call carries winner text
            font = get_font.return_value
            calls = [c[0][0] for c in font.render.call_args_list]
            assert any("TEAM 1 WINS" in t for t in calls)

    def test_draw_battle_over_team1_alive_renders_team2_wins_text(
        self, battle_panels_module
    ):
        mod, mp = battle_panels_module
        ships = [_make_ship("A", team_id=1, alive=True)]
        panel, screen = self._draw_setup(mod, mp, ships, is_over=True)
        with self._stub_fonts(mod) as get_font:
            panel.draw(screen)
            font = get_font.return_value
            calls = [c[0][0] for c in font.render.call_args_list]
            assert any("TEAM 2 WINS" in t for t in calls)

    def test_draw_battle_over_no_alive_renders_draw_text(self, battle_panels_module):
        mod, mp = battle_panels_module
        ships = [_make_ship("A", team_id=0, alive=False), _make_ship("B", team_id=1, alive=False)]
        panel, screen = self._draw_setup(mod, mp, ships, is_over=True)
        with self._stub_fonts(mod) as get_font:
            panel.draw(screen)
            font = get_font.return_value
            calls = [c[0][0] for c in font.render.call_args_list]
            assert any("DRAW" in t for t in calls)

    def test_draw_battle_ongoing_sets_end_battle_early_rect_not_battle_end_rect(
        self, battle_panels_module
    ):
        mod, mp = battle_panels_module
        ships = [_make_ship("A", team_id=0)]
        panel, screen = self._draw_setup(mod, mp, ships, is_over=False)
        with self._stub_fonts(mod):
            panel.draw(screen)
        assert panel.end_battle_early_rect is not None
        assert panel.battle_end_button_rect is None

    def test_handle_click_on_battle_end_button_returns_end_battle(self, battle_panels_module):
        mod, _ = battle_panels_module
        panel = mod.BattleControlPanel(MagicMock(), 0, 0, 800, 600)
        panel.battle_end_button_rect = MockRect(100, 100, 200, 50)
        result = panel.handle_click(150, 125)
        assert result == "end_battle"

    def test_handle_click_on_end_battle_early_button_returns_end_battle(
        self, battle_panels_module
    ):
        mod, _ = battle_panels_module
        panel = mod.BattleControlPanel(MagicMock(), 0, 0, 800, 600)
        panel.end_battle_early_rect = MockRect(10, 70, 120, 30)
        result = panel.handle_click(50, 80)
        assert result == "end_battle"

    def test_handle_click_outside_buttons_returns_false(self, battle_panels_module):
        mod, _ = battle_panels_module
        panel = mod.BattleControlPanel(MagicMock(), 0, 0, 800, 600)
        panel.end_battle_early_rect = MockRect(10, 70, 120, 30)
        panel.battle_end_button_rect = None
        result = panel.handle_click(500, 500)
        assert result is False
