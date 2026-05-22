"""PROJ-472 Phase 1C — draw_fleet_path sources segments from the facade.

The render-hot path must read the fleet path projection through
``r.scene.facade.fleets.path_projection(fleet.id, max_turns=50)`` rather than
the live-session ``r.scene.session.get_fleet_path_projection(fleet, ...)``
bypass. This is a one-for-one swap (the facade returns the same
``List[dict]`` segment shape) and must NOT call the session reader.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame

from game.ui.screens.strategy_render import fleets


def _renderer_with_facade() -> SimpleNamespace:
    path_projection = MagicMock(return_value=[])
    session = MagicMock(name="session")
    facade = SimpleNamespace(
        fleets=SimpleNamespace(path_projection=path_projection),
    )
    scene = SimpleNamespace(session=session, facade=facade)
    camera = SimpleNamespace(
        zoom=1.0,
        world_to_screen=lambda pos: pygame.math.Vector2(pos.x, pos.y),
    )
    return SimpleNamespace(
        scene=scene,
        camera=camera,
        hex_size=10,
        screen_width=800,
        screen_height=600,
        _get_font=MagicMock(),
    )


def test_draw_fleet_path_reads_projection_from_facade_not_session() -> None:
    r = renderer = _renderer_with_facade()
    fleet = SimpleNamespace(id=42)
    fleets.draw_fleet_path(renderer, MagicMock(), fleet, pygame.math.Vector2(0, 0))

    r.scene.facade.fleets.path_projection.assert_called_once_with(42, max_turns=50)
    # The live session reader must NOT be touched.
    assert not r.scene.session.get_fleet_path_projection.called
