"""Tests for ``draw_dyson_spheres`` (issue #21).

After the rejection of commit ``1c82bdb55``, the per-hex outline pass for
Dyson Spheres lives entirely in ``HexOutlineLayer.draw()`` (step 3 of the
strategy renderer's draw order), which runs BEFORE the sphere image blit.
``draw_dyson_spheres`` itself does NOT issue any outline draws — that
matches how stars render and produces the requested z-order where outlines
appear only where they peek beyond the sphere silhouette.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.planet import PlanetType
from game.ui.screens.strategy_render.dyson_spheres import draw_dyson_spheres


@pytest.fixture(autouse=True, scope="module")
def _pygame_init():
    """Initialise pygame headlessly so ``pygame.Surface(...)`` works."""
    if not pygame.get_init():
        pygame.init()
    yield


def _make_planet(
    *,
    radius_hexes: int,
    owner_id: int | None,
    planet_type: PlanetType = PlanetType.DYSON_SPHERE,
    location: HexCoord | None = None,
) -> SimpleNamespace:
    """Minimal planet duck-type for the renderer."""
    loc = location if location is not None else HexCoord(0, 0)
    return SimpleNamespace(
        planet_type=planet_type,
        radius_hexes=radius_hexes,
        owner_id=owner_id,
        location=loc,
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


@pytest.mark.parametrize("radius_hexes", [2, 3, 4, 5, 6])
@pytest.mark.parametrize("owner_id", [None, 1, 99])
def test_draw_dyson_spheres_does_not_issue_inner_hex_outlines(
    radius_hexes: int, owner_id: int | None,
) -> None:
    """The load-bearing regression test for issue #21.

    Per-hex outlines for Dyson-Sphere-occupied hexes are drawn by
    ``HexOutlineLayer.draw()`` BEFORE the sphere image blit. The Dyson
    Sphere renderer must NOT issue its own outline pass — that would
    paint borders on top of the sphere image (the rejected behavior
    from commit ``1c82bdb55``).
    """
    renderer = _make_renderer(active_empire_id=1)
    sys_world_pos = pygame.math.Vector2(0, 0)
    planet = _make_planet(radius_hexes=radius_hexes, owner_id=owner_id)
    sys_obj = SimpleNamespace(planets=[planet])

    draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    renderer._draw_inner_hex.assert_not_called()


def test_sphere_image_blitted_when_image_available() -> None:
    """When the Sphereworld image loads successfully, it is blitted to the screen."""
    renderer = _make_renderer(active_empire_id=1)
    real_image = pygame.Surface((50, 50))
    renderer._asset_manager.load_external_image = MagicMock(return_value=real_image)

    screen = MagicMock()
    sys_world_pos = pygame.math.Vector2(0, 0)
    planet = _make_planet(radius_hexes=2, owner_id=99)
    sys_obj = SimpleNamespace(planets=[planet])

    draw_dyson_spheres(renderer, screen, sys_obj, sys_world_pos)

    assert screen.blit.called, "Expected the sphere image to be blitted."


def test_selection_ring_drawn_when_selected() -> None:
    """When the Dyson Sphere is the selected object, a WHITE selection ring is drawn."""
    planet = _make_planet(radius_hexes=2, owner_id=99)
    renderer = _make_renderer(active_empire_id=1, selected_object=planet)
    sys_obj = SimpleNamespace(planets=[planet])
    sys_world_pos = pygame.math.Vector2(0, 0)

    with patch("game.ui.screens.strategy_render.dyson_spheres.pygame.draw.circle") as mock_circle:
        draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    from game.ui.colors import WHITE
    selection_calls = [
        c for c in mock_circle.call_args_list
        if len(c.args) >= 2 and c.args[1] == WHITE
    ]
    assert selection_calls, "Expected a WHITE selection ring when planet is selected."


def test_fallback_circle_drawn_when_image_missing() -> None:
    """When ``load_dyson_sphere_image`` returns None, a DYSON_FALLBACK circle is drawn."""
    renderer = _make_renderer(active_empire_id=1)
    sys_obj = SimpleNamespace(planets=[_make_planet(radius_hexes=2, owner_id=None)])
    sys_world_pos = pygame.math.Vector2(0, 0)

    with patch("game.ui.screens.strategy_render.dyson_spheres.pygame.draw.circle") as mock_circle:
        draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    from game.ui.colors import DYSON_FALLBACK
    fallback_calls = [
        c for c in mock_circle.call_args_list
        if len(c.args) >= 2 and c.args[1] == DYSON_FALLBACK
    ]
    assert fallback_calls, "Expected a DYSON_FALLBACK circle when image is missing."


def test_unowned_dyson_sphere_does_not_attempt_owner_marker() -> None:
    """When ``planet.owner_id is None``, the owner-marker block is skipped.

    The owner-marker branch contains a preserved latent ``screen_diameter``
    NameError (documented in the file-header docstring, out of scope for
    #21). This test pins the unowned path so a future refactor that
    inadvertently runs that branch is caught.
    """
    renderer = _make_renderer(active_empire_id=1)
    planet = _make_planet(radius_hexes=2, owner_id=None)
    sys_obj = SimpleNamespace(planets=[planet])
    sys_world_pos = pygame.math.Vector2(0, 0)

    draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    # If the owner-marker branch had run, it would have raised NameError.
    # Reaching this line is the assertion.


def test_non_dyson_planet_in_system_is_skipped() -> None:
    """A non-Dyson planet sharing a system with a Dyson Sphere triggers no outlines."""
    renderer = _make_renderer(active_empire_id=1)
    dyson = _make_planet(radius_hexes=2, owner_id=99)
    normal = _make_planet(
        radius_hexes=0,
        owner_id=99,
        planet_type=PlanetType.CONTINENTAL,
        location=HexCoord(5, -3),
    )
    sys_obj = SimpleNamespace(planets=[normal, dyson])
    sys_world_pos = pygame.math.Vector2(0, 0)

    draw_dyson_spheres(renderer, _make_screen(), sys_obj, sys_world_pos)

    renderer._draw_inner_hex.assert_not_called()
