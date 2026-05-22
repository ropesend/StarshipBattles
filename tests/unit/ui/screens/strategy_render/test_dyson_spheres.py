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

import math

from game.core.hex_math import HexCoord, hex_circle_filled, hex_to_pixel
from game.strategy.data.planet import PlanetType
from game.ui.screens.strategy_render.dyson_spheres import draw_dyson_spheres

# Symmetric slack on the occupied-hex bbox fit assertion. Covers the
# 1.05x DYSON_SPHERE_FILL_FACTOR plus integer rounding from the int()
# cast in screen_radius — see #26 QA iteration 2.
DYSON_SPHERE_FIT_TOLERANCE: float = 1.06


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
    empires: list = []
    # PROJ-477 Phase 5: render reads owners through r.world.iter_empires().
    world = SimpleNamespace(iter_empires=lambda: iter(empires))
    return SimpleNamespace(
        scene=scene,
        camera=camera,
        hex_size=10,
        empires=empires,
        world=world,
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


def _occupied_hex_bbox(
    location: HexCoord, radius_hexes: int, hex_size: float
) -> tuple[float, float]:
    """Compute the world-space bounding box of ``occupied_hexes(planet)``.

    Mirrors ``PlanetQueryService.occupied_hexes``: the occupied set is
    ``hex_circle_filled(location, radius_hexes - 1)``. We take each hex's
    centre via ``hex_to_pixel`` and inflate by ``(hex_size, sqrt(3)/2 * hex_size)``
    so the bbox spans corner-to-corner horizontally and flat-to-flat vertically
    for each hex (the maximum hex extent in those axes).

    Returns:
        (width, height) of the bounding box in world units.
    """
    occupied = hex_circle_filled(location, max(0, radius_hexes - 1))
    pixels = [hex_to_pixel(h, hex_size) for h in occupied]
    apothem = (math.sqrt(3) / 2.0) * hex_size
    min_x = min(p[0] for p in pixels) - hex_size
    max_x = max(p[0] for p in pixels) + hex_size
    min_y = min(p[1] for p in pixels) - apothem
    max_y = max(p[1] for p in pixels) + apothem
    return (max_x - min_x, max_y - min_y)


@pytest.mark.parametrize("radius_hexes", [2, 3, 4, 5, 6])
def test_sphere_image_fits_inside_occupied_hex_bounding_box(
    radius_hexes: int,
) -> None:
    """AC for #26: the rendered sphere image must fit inside the bounding
    box of the planet's ``occupied_hexes()`` at every supported radius.

    The image is square, sized to ``screen_radius * 2`` pixels in both axes.
    At zoom = 1.0, world units == screen pixels, so we can compare the
    scaled image's dimensions directly against the world-space bounding
    box of the occupied hex disc. If the formula on
    ``dyson_spheres.py:52`` overshoots the disc (the bug), this assertion
    fails for radii where the overshoot exceeds the bbox apothem.
    """
    renderer = _make_renderer(active_empire_id=1)
    # Force the image-blit branch so we can capture the scaled size.
    real_image = pygame.Surface((50, 50))
    renderer._asset_manager.load_external_image = MagicMock(return_value=real_image)

    captured_sizes: list[tuple[int, int]] = []
    original_smoothscale = pygame.transform.smoothscale

    def _capturing_smoothscale(surf, size):
        captured_sizes.append(tuple(size))
        return original_smoothscale(surf, size)

    sys_world_pos = pygame.math.Vector2(0, 0)
    planet = _make_planet(radius_hexes=radius_hexes, owner_id=None)
    sys_obj = SimpleNamespace(planets=[planet])

    screen = MagicMock()
    with patch(
        "game.ui.screens.strategy_render.dyson_spheres.pygame.transform.smoothscale",
        side_effect=_capturing_smoothscale,
    ):
        draw_dyson_spheres(renderer, screen, sys_obj, sys_world_pos)

    assert captured_sizes, "Expected smoothscale to be called for the sphere image."
    img_w, img_h = captured_sizes[0]

    bbox_w, bbox_h = _occupied_hex_bbox(planet.location, radius_hexes, renderer.hex_size)
    bbox_min = min(bbox_w, bbox_h)
    tolerance = bbox_min * DYSON_SPHERE_FIT_TOLERANCE

    assert img_w <= tolerance, (
        f"radius_hexes={radius_hexes}: sphere image width {img_w}px exceeds "
        f"occupied-hex bbox min dim {bbox_min:.2f}px * {DYSON_SPHERE_FIT_TOLERANCE} "
        f"= {tolerance:.2f}px (bbox=({bbox_w:.2f}, {bbox_h:.2f}))."
    )
    assert img_h <= tolerance, (
        f"radius_hexes={radius_hexes}: sphere image height {img_h}px exceeds "
        f"occupied-hex bbox min dim {bbox_min:.2f}px * {DYSON_SPHERE_FIT_TOLERANCE} "
        f"= {tolerance:.2f}px (bbox=({bbox_w:.2f}, {bbox_h:.2f}))."
    )
