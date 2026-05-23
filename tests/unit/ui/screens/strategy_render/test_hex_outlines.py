from __future__ import annotations

import math
from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame

from game.core.hex_math import HexCoord
from game.ui.colors import HEX_OUTLINE_OCCUPIED, HEX_OUTLINE_PLAYER_OWNED
from game.ui.screens.strategy_render.hex_outlines import HexOutlineLayer


class _StubWorld:
    """PROJ-477 Phase 5: scene.world live-seam stub for hex-outline tests.

    Reads through to the renderer's galaxy-state maps + empires DYNAMICALLY so
    tests that reassign ``renderer.galaxy.state.*`` / ``renderer.empires`` after
    construction are reflected (the render path reads these per build)."""

    def __init__(self, renderer):
        self._r = renderer

    def iter_empires(self):
        return iter(self._r.empires)

    @property
    def global_hex_planets(self):
        return self._r.galaxy.state.global_hex_planets

    @property
    def global_hex_zones(self):
        return self._r.galaxy.state.global_hex_zones

    @property
    def global_hex_warp_points(self):
        return self._r.galaxy.state.global_hex_warp_points


def _renderer_context() -> SimpleNamespace:
    # PROJ-472 1C: hex outlines read the active-empire id + turn number
    # through facade-fed scene accessors, not scene.session.*.
    scene = SimpleNamespace(active_empire_id=1, turn_number=7)
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
    renderer = SimpleNamespace(
        scene=scene,
        galaxy=galaxy,
        empires=[],
        camera=camera,
        hex_size=10,
        screen_width=800,
        screen_height=600,
        _draw_inner_hex=MagicMock(),
    )
    # PROJ-477 Phase 5: hex outlines read galaxy-state maps + empires through
    # r.world (the live seam, dynamic read-through).
    renderer.world = _StubWorld(renderer)
    return renderer


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
    renderer.scene.turn_number = 8
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

    # PROJ-491 Task 1.1: tolerance-based assertion replaces brittle exact-float
    # equality. We check call count + per-call structure with math.isclose on
    # the float coordinates (irrational sqrt(3) values otherwise force fragile
    # literal copies).
    expected = [
        (screen, 0.0, 0.0, 0.88, HEX_OUTLINE_PLAYER_OWNED),
        (screen, 15.0, 8.660254037844386, 0.88, HEX_OUTLINE_OCCUPIED),
        (screen, 30.0, 17.32050807568877, 0.90, HEX_OUTLINE_PLAYER_OWNED),
        (screen, 30.0, 17.32050807568877, 0.80, HEX_OUTLINE_OCCUPIED),
    ]
    actual_calls = renderer._draw_inner_hex.call_args_list
    assert len(actual_calls) == len(expected)
    for actual_call, (exp_screen, exp_x, exp_y, exp_scale, exp_color) in zip(
        actual_calls, expected
    ):
        args, _kwargs = actual_call
        got_screen, got_x, got_y, got_scale, got_color = args
        assert got_screen is exp_screen
        assert math.isclose(got_x, exp_x, abs_tol=1e-9)
        assert math.isclose(got_y, exp_y, abs_tol=1e-9)
        assert math.isclose(got_scale, exp_scale, abs_tol=1e-9)
        assert got_color == exp_color


def test_draw_skips_offscreen_outline() -> None:
    layer = HexOutlineLayer()
    renderer = _renderer_context()
    layer.get_data = MagicMock(return_value={HexCoord(0, 0): (False, True)})
    renderer.camera.world_to_screen = lambda _pos: pygame.math.Vector2(-100, 0)

    layer.draw(renderer, MagicMock())

    renderer._draw_inner_hex.assert_not_called()


def test_build_data_includes_dyson_sphere_zone_hexes(_pygame_inited=None) -> None:
    """Issue #21 regression: Dyson Sphere occupied hexes contribute to
    ``build_data()`` so the pre-image outline pass renders them before the
    sphere image blit. This documents that ``draw_dyson_spheres`` itself
    must NOT issue a duplicate post-blit outline pass.
    """
    from game.core.hex_math import hex_circle_filled

    layer = HexOutlineLayer()
    renderer = _renderer_context()

    dyson_sphere = SimpleNamespace(owner_id=99)  # non-player
    center = HexCoord(0, 0)
    occupied = hex_circle_filled(center, 1)  # 7 hexes for radius_hexes=2

    for global_hex in occupied:
        renderer.galaxy.state.global_hex_zones[global_hex] = [dyson_sphere]

    data = layer.build_data(renderer)

    assert len(data) == 7
    for global_hex in occupied:
        # owner_id 99 != active empire id 1, so non-player ownership.
        assert data[global_hex] == (False, True), (
            f"Expected non-player ownership for Dyson Sphere hex {global_hex}, "
            f"got {data[global_hex]}."
        )
