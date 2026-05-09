from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import call
from unittest.mock import MagicMock

import pygame

from game.core.hex_math import HexCoord
from game.ui.colors import HEX_OUTLINE_OCCUPIED, HEX_OUTLINE_PLAYER_OWNED
from game.ui.screens.strategy_render.hex_outlines import HexOutlineLayer


def _renderer_context() -> SimpleNamespace:
    active_empire = SimpleNamespace(id=1)
    session = SimpleNamespace(active_empire=active_empire, turn_number=7)
    scene = SimpleNamespace(session=session)
    galaxy = SimpleNamespace(
        state=SimpleNamespace(
            global_hex_planets={},
            global_hex_zones={},
            global_hex_warp_points={},
        ),
    )
    camera = SimpleNamespace(
        world_to_screen=lambda pos: pygame.math.Vector2(pos.x, pos.y),
    )
    return SimpleNamespace(
        scene=scene,
        galaxy=galaxy,
        empires=[],
        camera=camera,
        hex_size=10,
        screen_width=800,
        screen_height=600,
        _draw_inner_hex=MagicMock(),
    )


def test_build_data_combines_player_and_non_player_occupancy() -> None:
    layer = HexOutlineLayer()
    renderer = _renderer_context()
    shared_hex = HexCoord(2, 3)
    fleet_hex = HexCoord(5, 0)

    renderer.galaxy.state.global_hex_planets[shared_hex] = [
        SimpleNamespace(owner_id=1),
        SimpleNamespace(owner_id=2),
    ]
    renderer.galaxy.state.global_hex_zones[shared_hex] = [
        SimpleNamespace(owner_id=1),
        object(),
    ]
    renderer.galaxy.state.global_hex_warp_points = {shared_hex}
    renderer.empires = [
        SimpleNamespace(fleets=[SimpleNamespace(location=fleet_hex, owner_id=1)]),
        SimpleNamespace(fleets=[SimpleNamespace(location=fleet_hex, owner_id=2)]),
        SimpleNamespace(fleets=[SimpleNamespace(location=None, owner_id=2)]),
    ]

    data = layer.build_data(renderer)

    assert data[shared_hex] == (True, True)
    assert data[fleet_hex] == (True, True)


def test_get_data_reuses_cache_until_turn_changes() -> None:
    layer = HexOutlineLayer()
    renderer = _renderer_context()
    layer.build_data = MagicMock(side_effect=[{"turn": 7}, {"turn": 8}])

    first = layer.get_data(renderer)
    second = layer.get_data(renderer)
    renderer.scene.session.turn_number = 8
    third = layer.get_data(renderer)

    assert first == {"turn": 7}
    assert second is first
    assert third == {"turn": 8}
    assert layer.build_data.call_count == 2


def test_draw_dispatches_inner_hex_outlines_by_ownership_state() -> None:
    layer = HexOutlineLayer()
    renderer = _renderer_context()
    player_hex = HexCoord(0, 0)
    occupied_hex = HexCoord(1, 0)
    mixed_hex = HexCoord(2, 0)
    layer.get_data = MagicMock(
        return_value={
            player_hex: (True, False),
            occupied_hex: (False, True),
            mixed_hex: (True, True),
        }
    )

    screen = MagicMock()

    layer.draw(renderer, screen)

    assert renderer._draw_inner_hex.call_args_list == [
        call(screen, 0.0, 0.0, 0.88, HEX_OUTLINE_PLAYER_OWNED),
        call(screen, 15.0, 8.660254037844386, 0.88, HEX_OUTLINE_OCCUPIED),
        call(screen, 30.0, 17.32050807568877, 0.90, HEX_OUTLINE_PLAYER_OWNED),
        call(screen, 30.0, 17.32050807568877, 0.80, HEX_OUTLINE_OCCUPIED),
    ]


def test_draw_skips_offscreen_outline() -> None:
    layer = HexOutlineLayer()
    renderer = _renderer_context()
    layer.get_data = MagicMock(return_value={HexCoord(0, 0): (False, True)})
    renderer.camera.world_to_screen = lambda _pos: pygame.math.Vector2(-100, 0)

    layer.draw(renderer, MagicMock())

    renderer._draw_inner_hex.assert_not_called()
