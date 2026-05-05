"""Focused tests for strategy click hit-testing and picking helpers."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame

from game.core.hex_math import HexCoord
from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher


class _IdentityCamera:
    def __init__(self, *, zoom: float = 1.0) -> None:
        self.zoom = zoom

    def world_to_screen(self, world_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        return pygame.math.Vector2(world_pos.x, world_pos.y)

    def screen_to_world(self, _screen_pos: tuple[int, int]) -> SimpleNamespace:
        return SimpleNamespace(x=0.0, y=0.0)


def _planet(
    name: str,
    location: HexCoord,
    *,
    mass: float = 1.0,
    radius: float = 1.0,
    planet_type: str = "Rocky",
) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        location=location,
        mass=mass,
        radius=radius,
        planet_type=SimpleNamespace(name=planet_type),
    )


def _system(planets: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(
        name="Sol",
        global_location=HexCoord(0, 0),
        planets=planets,
        warp_points=[],
        stars=[],
    )


def _dispatcher(scene: SimpleNamespace | None = None) -> ClickModeDispatcher:
    if scene is None:
        scene = SimpleNamespace(
            camera=_IdentityCamera(zoom=2.0),
            hex_size=10,
            empires=[],
            galaxy=None,
            ui=MagicMock(),
            on_ui_selection=MagicMock(),
            selected_object=None,
            last_selected_system=None,
        )
    handler = SimpleNamespace(scene=scene, input_mode="SELECT", _fleet_router=MagicMock())
    return ClickModeDispatcher(handler)


def test_click_dispatcher_planet_hit_test_prefers_expanded_planet() -> None:
    big = _planet("Big", HexCoord(0, 0), mass=100.0, radius=10.0)
    small = _planet("Small", HexCoord(0, 0), mass=10.0, radius=5.0)
    dispatcher = _dispatcher()

    hit = dispatcher._hit_test_planets(15, 0, _system([big, small]))

    assert hit is small


def test_hit_test_single_giant_uses_larger_click_radius() -> None:
    giant = _planet("Jupiter", HexCoord(0, 0), planet_type="Gas Giant")
    dispatcher = _dispatcher()

    hit = dispatcher._hit_test_planets(18, 0, _system([giant]))

    assert hit is giant


def test_resolve_click_target_returns_planet_logical_hex_when_visual_hit() -> None:
    planet = _planet("Target", HexCoord(3, 4))
    system = _system([planet])
    system.global_location = HexCoord(10, -2)
    scene = SimpleNamespace(
        camera=_IdentityCamera(zoom=1.0),
        hex_size=10,
        _get_system_at_hex=MagicMock(return_value=system),
    )
    dispatcher = _dispatcher(scene)
    dispatcher._hit_test_planets = MagicMock(return_value=planet)

    with patch(
        "game.ui.screens.strategy_click_dispatcher.pixel_to_hex",
        return_value=HexCoord(99, 99),
    ):
        target_hex = dispatcher._resolve_click_target(100, 200)

    assert target_hex == HexCoord(13, 2)
    dispatcher._hit_test_planets.assert_called_once_with(100, 200, system)


def test_resolve_click_target_returns_raw_hex_when_zoom_too_low() -> None:
    raw_hex = HexCoord(6, 7)
    scene = SimpleNamespace(
        camera=_IdentityCamera(zoom=0.4),
        hex_size=10,
        _get_system_at_hex=MagicMock(return_value=_system([])),
    )
    dispatcher = _dispatcher(scene)
    dispatcher._hit_test_planets = MagicMock()

    with patch("game.ui.screens.strategy_click_dispatcher.pixel_to_hex", return_value=raw_hex):
        target_hex = dispatcher._resolve_click_target(100, 200)

    assert target_hex == raw_hex
    dispatcher._hit_test_planets.assert_not_called()


def test_handle_picking_prioritizes_hit_tested_planet_in_shared_hex() -> None:
    first_planet = _planet("First", HexCoord(0, 0))
    hit_planet = _planet("Hit", HexCoord(0, 0))
    system = _system([first_planet, hit_planet])
    scene = SimpleNamespace(
        camera=_IdentityCamera(zoom=2.0),
        hex_size=10,
        _get_system_at_hex=MagicMock(return_value=system),
        empires=[],
        galaxy=None,
        ui=MagicMock(),
        on_ui_selection=MagicMock(),
        selected_object=None,
        last_selected_system=None,
    )
    dispatcher = _dispatcher(scene)
    dispatcher._hit_test_planets = MagicMock(return_value=hit_planet)

    with patch(
        "game.ui.screens.strategy_click_dispatcher.pixel_to_hex",
        return_value=HexCoord(0, 0),
    ):
        dispatcher._handle_picking(100, 200)

    sector_contents = scene.ui.show_sector_info.call_args.args[1]
    assert sector_contents[0] is hit_planet
    assert first_planet in sector_contents
    scene.on_ui_selection.assert_called_once_with(hit_planet)
    assert scene.selected_object is hit_planet
    assert scene.last_selected_system is system


def test_handle_picking_clears_detail_for_empty_space() -> None:
    scene = SimpleNamespace(
        camera=_IdentityCamera(zoom=1.0),
        hex_size=10,
        _get_system_at_hex=MagicMock(return_value=None),
        empires=[],
        galaxy=None,
        ui=MagicMock(),
        on_ui_selection=MagicMock(),
        selected_object=object(),
        last_selected_system=None,
    )
    dispatcher = _dispatcher(scene)

    with patch(
        "game.ui.screens.strategy_click_dispatcher.pixel_to_hex",
        return_value=HexCoord(5, 5),
    ):
        dispatcher._handle_picking(100, 200)

    scene.ui.show_system_info.assert_called_once_with(None, [])
    scene.ui.show_detailed_report.assert_called_once_with(None, None)
    scene.on_ui_selection.assert_not_called()
    assert scene.selected_object is None
