"""Tests for ``draw_dyson_spheres`` per-hex outline pass (issue #21).

The Dyson Sphere image blit obscures the outlines drawn earlier by
``HexOutlineLayer``. To restore per-hex visibility, ``draw_dyson_spheres``
issues its own outline pass *after* the image blit (and selection ring)
and *before* the owner marker.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.core.hex_math import HexCoord, hex_circle_filled
from game.strategy.data.planet import PlanetType
from game.ui.colors import HEX_OUTLINE_OCCUPIED, HEX_OUTLINE_PLAYER_OWNED
from game.ui.screens.strategy_render.dyson_spheres import draw_dyson_spheres


@pytest.fixture(autouse=True, scope="module")
def _pygame_init():
    """Initialise pygame headlessly so ``pygame.Surface(...)`` works."""
    if not pygame.get_init():
        pygame.init()
    yield


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_planet(
    *,
    radius_hexes: int,
    owner_id: int | None,
    planet_type: PlanetType = PlanetType.DYSON_SPHERE,
    location: HexCoord | None = None,
) -> SimpleNamespace:
    """Minimal planet duck-type for the renderer."""
    loc = location if location is not None else HexCoord(0, 0)
    occupied = (
        hex_circle_filled(loc, max(0, radius_hexes - 1))
        if radius_hexes > 0
        else frozenset({loc})
    )
    return SimpleNamespace(
        planet_type=planet_type,
        radius_hexes=radius_hexes,
        owner_id=owner_id,
        location=loc,
        occupied_hexes=occupied,
    )


def _make_renderer(*, active_empire_id: int = 1, selected_object=None):
    """Renderer SimpleNamespace.

    ``_asset_manager.load_external_image`` returns the missing-texture
    sentinel by default, which makes ``load_dyson_sphere_image`` return
    ``None`` and route the renderer through the fallback-circle branch.
    The fallback branch only calls ``pygame.draw.circle(screen, ...)``,
    which needs a real ``pygame.Surface``.
    """
    missing_texture = object()
    asset_manager = SimpleNamespace(
        load_external_image=MagicMock(return_value=missing_texture),
        missing_texture=missing_texture,
    )
    camera = SimpleNamespace(
        zoom=1.0,
        world_to_screen=lambda pos: pygame.math.Vector2(pos.x, pos.y),
    )
    active_empire = SimpleNamespace(id=active_empire_id)
    session = SimpleNamespace(active_empire=active_empire)
    scene = SimpleNamespace(session=session, selected_object=selected_object)
    return SimpleNamespace(
        scene=scene,
        camera=camera,
        hex_size=10,
        empires=[],
        empire_assets={},
        _asset_manager=asset_manager,
        _draw_inner_hex=MagicMock(),
    )


def _make_screen() -> pygame.Surface:
    """Real Surface — pygame.draw.circle and screen.blit both work on it."""
    return pygame.Surface((400, 400))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_non_player_dyson_sphere_draws_red_outlines_per_hex() -> None:
    """Non-player Dyson Sphere (radius_hexes=2) issues 7 red outline calls."""
    renderer = _make_renderer(active_empire_id=1)
    sys_world_pos = pygame.math.Vector2(0, 0)
    planet = _make_planet(radius_hexes=2, owner_id=99)  # not player
    sys_obj = SimpleNamespace(planets=[planet])

    draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    # radius_hexes=2 -> hex_circle_filled(center, 1) -> 7 hexes.
    assert renderer._draw_inner_hex.call_count == 7
    for call in renderer._draw_inner_hex.call_args_list:
        # call.args = (screen, cx, cy, scale, color)
        assert call.args[4] == HEX_OUTLINE_OCCUPIED


def test_player_owned_dyson_sphere_draws_white_outlines_per_hex() -> None:
    """Player-owned Dyson Sphere draws white outlines for every hex."""
    renderer = _make_renderer(active_empire_id=1)
    sys_world_pos = pygame.math.Vector2(0, 0)
    planet = _make_planet(radius_hexes=2, owner_id=1)  # matches active empire
    sys_obj = SimpleNamespace(planets=[planet])

    draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    assert renderer._draw_inner_hex.call_count == 7
    for call in renderer._draw_inner_hex.call_args_list:
        assert call.args[4] == HEX_OUTLINE_PLAYER_OWNED


def test_outline_pass_runs_after_sphere_image_blit() -> None:
    """Z-order: every per-hex outline call is issued AFTER the sphere image
    blit. This is the load-bearing test for the issue.

    The bug was that outlines drawn earlier in ``HexOutlineLayer`` were
    overwritten by the sphere image blit. The fix is a second outline pass
    *after* the image. If a future refactor moves the outline pass back
    above the blit, this test catches it.

    ``pygame.Surface.blit`` is read-only, so we use a MagicMock screen and
    stub ``pygame.draw.circle`` (called for the cyan fallback path) so the
    test doesn't actually need a real Surface to issue draws.
    """
    renderer = _make_renderer(active_empire_id=1)

    # Force the image-blit branch by returning a non-sentinel surface.
    real_image = pygame.Surface((50, 50))
    renderer._asset_manager.load_external_image = MagicMock(
        return_value=real_image
    )

    call_log: list[str] = []

    screen = MagicMock()
    screen.blit.side_effect = lambda *a, **kw: call_log.append("blit")
    renderer._draw_inner_hex.side_effect = (
        lambda *a, **kw: call_log.append("inner_hex")
    )

    sys_world_pos = pygame.math.Vector2(0, 0)
    planet = _make_planet(radius_hexes=2, owner_id=99)
    sys_obj = SimpleNamespace(planets=[planet])

    # Stub draw.circle so the (not used here) fallback path wouldn't trip
    # over a MagicMock screen if exercised in other branches.
    with patch("pygame.draw.circle"):
        draw_dyson_spheres(renderer, screen, sys_obj, sys_world_pos)

    blit_indices = [i for i, name in enumerate(call_log) if name == "blit"]
    inner_indices = [i for i, name in enumerate(call_log) if name == "inner_hex"]

    assert blit_indices, "Expected the sphere image to be blitted at least once."
    assert inner_indices, "Expected per-hex outline calls."
    assert max(blit_indices) < min(inner_indices), (
        "Every per-hex outline call must occur AFTER the sphere image blit; "
        f"recorded sequence: {call_log}"
    )


@pytest.mark.parametrize("radius_hexes", [2, 3, 4, 5, 6])
def test_outline_call_count_matches_occupied_hexes_for_each_radius(
    radius_hexes: int,
) -> None:
    """For each radius in the acceptance-criterion range (2..6), the outline
    pass issues exactly ``len(occupied_hexes)`` calls to ``_draw_inner_hex``.
    """
    renderer = _make_renderer(active_empire_id=1)
    sys_world_pos = pygame.math.Vector2(0, 0)
    planet = _make_planet(radius_hexes=radius_hexes, owner_id=99)
    sys_obj = SimpleNamespace(planets=[planet])

    draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    expected = len(hex_circle_filled(HexCoord(0, 0), radius_hexes - 1))
    assert renderer._draw_inner_hex.call_count == expected


def test_non_dyson_planet_in_same_system_does_not_trigger_outline_pass() -> None:
    """A non-Dyson planet sharing the system with a Dyson Sphere produces
    outlines only for the sphere's hexes, not the planet's.
    """
    renderer = _make_renderer(active_empire_id=1)
    sys_world_pos = pygame.math.Vector2(0, 0)
    dyson = _make_planet(radius_hexes=2, owner_id=99)
    normal = _make_planet(
        radius_hexes=0,
        owner_id=99,
        planet_type=PlanetType.CONTINENTAL,
        location=HexCoord(5, -3),
    )
    sys_obj = SimpleNamespace(planets=[normal, dyson])

    draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    # 7 outlines for the Dyson Sphere, 0 for the normal planet.
    assert renderer._draw_inner_hex.call_count == 7
