"""Save/load coverage for the `data_path` field added by the mode-scoped
data lifecycle.

Contract:
- A `GameSession`'s `data_path` reflects the registry's active data path
  at save time.
- `GameSession.to_dict()` includes `data_path` in the save dict.
- `SaveGameService.load_game(...)` reads `data_path` from the save file
  and calls `load_data_from_path(...)` BEFORE rehydrating the session.
- Saves missing the `data_path` field (pre-feature saves) default to
  `Paths.DEFAULT_GAME_DATA_DIR` via `dict.get()` — no migration shim,
  per CLAUDE.md's "old saves are disposable" rule.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from game.core.paths import Paths


@pytest.fixture
def temp_saves_dir(monkeypatch):
    tmp = tempfile.mkdtemp(prefix="sb_data_path_save_")
    monkeypatch.setattr(Paths, "SAVES_DIR", tmp)
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


def _build_minimal_session(data_path: str | None = None):
    """Construct a GameSession with a 1-system / 1-empire quickstart config."""
    from game.data_loader import load_data_from_path
    from game.strategy.engine.game_session import GameSession
    from game.strategy.quickstart_builder import QuickstartBuilder

    if data_path is not None:
        load_data_from_path(data_path)

    config = QuickstartBuilder.build_1p_config()
    return GameSession(config=config)


@pytest.mark.use_custom_data
def test_save_dict_includes_data_path():
    """to_dict() carries the active registry data path."""
    from game.data_loader import unload_data
    try:
        session = _build_minimal_session(Paths.DEFAULT_GAME_DATA_DIR)
        save_dict = session.to_dict()
        assert "data_path" in save_dict
        assert save_dict["data_path"] == Paths.DEFAULT_GAME_DATA_DIR
    finally:
        unload_data()


@pytest.mark.use_custom_data
def test_save_then_load_preserves_data_path(temp_saves_dir):
    """Round-trip: data_path written on save reappears on load and the
    matching data set is hydrated into the registry."""
    from game.data_loader import load_data_from_path, unload_data
    from game.core.registry import get_default_registry_manager
    from game.strategy.systems.save_game_service import SaveGameService

    try:
        session = _build_minimal_session(Paths.DEFAULT_GAME_DATA_DIR)
        ok, msg, save_path = SaveGameService.save_game(session, save_name="TestDataPath")
        assert ok, msg

        # Pollute the registry with combat-lab data to simulate the bug
        # scenario, then load the save and confirm stock data is restored.
        load_data_from_path(Paths.COMBAT_LAB_DATA_DIR)
        mgr = get_default_registry_manager()
        assert "metal_harvester" not in mgr.components

        loaded, msg = SaveGameService.load_game(save_path)
        assert loaded is not None, msg
        assert mgr.active_data_path == Paths.DEFAULT_GAME_DATA_DIR
        assert "metal_harvester" in mgr.components
    finally:
        unload_data()


@pytest.mark.use_custom_data
def test_load_legacy_save_without_data_path_defaults_to_stock(temp_saves_dir):
    """Old saves with no `data_path` field load against the default game
    data path. No migration shim required — just `dict.get(...)` defaulting.
    """
    from game.data_loader import load_data_from_path, unload_data
    from game.core.registry import get_default_registry_manager
    from game.strategy.systems.save_game_service import SaveGameService

    try:
        session = _build_minimal_session(Paths.DEFAULT_GAME_DATA_DIR)
        ok, msg, save_path = SaveGameService.save_game(session, save_name="LegacySim")
        assert ok, msg

        # Strip the data_path field from the turn file to simulate a save
        # produced by code that pre-dates this change.
        turn_file = Path(save_path) / "turns" / "turn_1.json"
        import json
        data = json.loads(turn_file.read_text(encoding="utf-8"))
        data.pop("data_path", None)
        turn_file.write_text(json.dumps(data), encoding="utf-8")

        load_data_from_path(Paths.COMBAT_LAB_DATA_DIR)
        mgr = get_default_registry_manager()
        assert "metal_harvester" not in mgr.components

        loaded, msg = SaveGameService.load_game(save_path)
        assert loaded is not None, msg
        # Default applied.
        assert mgr.active_data_path == Paths.DEFAULT_GAME_DATA_DIR
        assert "metal_harvester" in mgr.components
    finally:
        unload_data()
