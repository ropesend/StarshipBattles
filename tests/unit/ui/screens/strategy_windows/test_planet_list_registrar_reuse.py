"""PROJ-411 Task 2.1: ``PlanetListRegistrar`` reuse path.

When the registrar's slot is occupied by a live window, ``open()`` calls
``open_for_galaxy()`` on the existing instance instead of constructing
a fresh ``PlanetListWindow``. When the slot is empty or the window is
no longer ``.alive()``, the registrar falls back to fresh construction.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.strategy_windows.list_windows import PlanetListRegistrar


def _make_composer(*, existing_window=None):
    """Build a MagicMock composer that the registrar reads from."""
    composer = MagicMock(name="composer")
    composer.width = 1920
    composer.height = 1080
    composer.manager = MagicMock(name="ui_manager")
    composer._asset_resolver = MagicMock(name="asset_resolver")
    composer.planet_list_window = existing_window
    composer.scene = MagicMock(name="scene")
    composer.scene.galaxy = MagicMock(name="galaxy")
    # PROJ-477 Phase 4: list windows take scene.world; iter_empires must yield
    # a real (empty) sequence for the owner-name lookup list.
    composer.scene.world.iter_empires.side_effect = lambda: iter(())
    composer.scene.current_empire = MagicMock(name="empire")
    composer.scene.session = MagicMock(name="session")
    composer.scene.session.empires = []
    composer.scene.session.registries = MagicMock(name="registries")
    facade = MagicMock(name="facade")
    facade.economy.race_registry = MagicMock(return_value=MagicMock(name="race_registry"))
    composer.scene.facade = facade
    return composer


def test_open_constructs_fresh_window_when_slot_empty():
    """First open: slot is None → registrar constructs a new window."""
    composer = _make_composer(existing_window=None)
    registrar = PlanetListRegistrar(composer)
    with patch(
        "game.ui.screens.strategy_windows.list_windows.PlanetListWindow"
    ) as mock_cls:
        registrar.open()
    mock_cls.assert_called_once()
    composer.planet_list_window = mock_cls.return_value  # mimic assignment


def test_open_reuses_alive_window_via_open_for_galaxy():
    """Slot has an alive window → registrar calls ``open_for_galaxy``."""
    alive_window = MagicMock(name="existing_window")
    alive_window.alive.return_value = True
    composer = _make_composer(existing_window=alive_window)
    registrar = PlanetListRegistrar(composer)
    with patch(
        "game.ui.screens.strategy_windows.list_windows.PlanetListWindow"
    ) as mock_cls:
        registrar.open()
    mock_cls.assert_not_called()
    alive_window.open_for_galaxy.assert_called_once()
    # PROJ-477 Phase 4: world + empire + facade should be threaded through.
    args, kwargs = alive_window.open_for_galaxy.call_args
    assert args[0] is composer.scene.world
    assert args[1] is composer.scene.current_empire
    assert kwargs.get("facade") is composer.scene.facade


def test_open_constructs_fresh_when_slot_holds_dead_window():
    """Slot has a non-None but dead window (after kill) → construct fresh."""
    dead_window = MagicMock(name="dead_window")
    dead_window.alive.return_value = False
    composer = _make_composer(existing_window=dead_window)
    registrar = PlanetListRegistrar(composer)
    with patch(
        "game.ui.screens.strategy_windows.list_windows.PlanetListWindow"
    ) as mock_cls:
        registrar.open()
    mock_cls.assert_called_once()
    dead_window.open_for_galaxy.assert_not_called()


def test_on_closed_clears_slot():
    """``_on_closed`` (invoked by kill() on Esc / scene exit) nulls the slot."""
    composer = _make_composer(existing_window=MagicMock())
    registrar = PlanetListRegistrar(composer)
    registrar._on_closed()
    assert composer.planet_list_window is None
