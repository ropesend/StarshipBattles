"""PROJ-427 Phase 5: SaveGameService replay-store is instance-owned.

The module-globals ``_replay_store`` / ``set_replay_store`` / ``get_replay_store``
/ ``_notify_replay_store_save_or_load`` / ``_notify_replay_store_save_deleted``
are removed. Replay-store wiring is now owned by a SaveGameService instance:

- ``SaveGameService()`` can be constructed (optionally with ``replay_store=...``).
- ``set_replay_store`` / ``get_replay_store`` are instance methods.
- A process-level singleton exposed by ``SaveGameService.default()`` lets
  static ``save_game`` / ``load_game`` / ``delete_save`` keep working
  without forcing every caller to plumb a constructed instance.
- All bootstrap / test wiring routes through
  ``SaveGameService.default().set_replay_store(store)`` (or constructs a
  dedicated ``SaveGameService(replay_store=...)`` instance).
"""
from __future__ import annotations

import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from game.core import paths as paths_module
from game.strategy.systems.save_game_service import SaveGameService
from tests.unit.strategy.save_game_service.conftest import MockGameSession


@pytest.fixture
def setup_tmpdir():
    tmpdir = tempfile.mkdtemp()
    saves_dir = os.path.join(tmpdir, "saves")
    os.makedirs(saves_dir, exist_ok=True)
    with patch.object(paths_module.Paths, "SAVES_DIR", saves_dir):
        yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture(autouse=True)
def _reset_default_singleton_replay_store():
    """Ensure every test starts with a clean default-singleton state."""
    SaveGameService.default().set_replay_store(None)
    yield
    SaveGameService.default().set_replay_store(None)


def test_module_globals_are_removed() -> None:
    """The module-level replay-store names must be gone after Phase 5."""
    from game.strategy.systems import save_game_service as sgs_mod

    assert not hasattr(sgs_mod, "_replay_store")
    assert not hasattr(sgs_mod, "set_replay_store")
    assert not hasattr(sgs_mod, "get_replay_store")
    assert not hasattr(sgs_mod, "_notify_replay_store_save_or_load")
    assert not hasattr(sgs_mod, "_notify_replay_store_save_deleted")


def test_instance_set_get_replay_store_round_trip() -> None:
    """A constructed instance owns its own replay-store reference."""
    spy = MagicMock()
    svc = SaveGameService(replay_store=spy)
    assert svc.get_replay_store() is spy

    new_spy = MagicMock()
    svc.set_replay_store(new_spy)
    assert svc.get_replay_store() is new_spy

    svc.set_replay_store(None)
    assert svc.get_replay_store() is None


def test_default_singleton_is_stable_and_shared() -> None:
    """``SaveGameService.default()`` always returns the same instance."""
    spy = MagicMock()
    SaveGameService.default().set_replay_store(spy)
    assert SaveGameService.default().get_replay_store() is spy
    assert SaveGameService.default() is SaveGameService.default()


def test_save_notifies_default_singleton_replay_store(setup_tmpdir) -> None:
    """Static ``save_game(...)`` notifies the default singleton's replay store."""
    spy = MagicMock()
    SaveGameService.default().set_replay_store(spy)

    session = MockGameSession()
    success, _msg, save_path = SaveGameService.save_game(
        session, "Phase5ReplayInstanceSave"
    )
    assert success
    spy.set_save_root.assert_called()


def test_delete_notifies_default_singleton_replay_store_clear(setup_tmpdir) -> None:
    """Static ``delete_save(...)`` notifies the default singleton's replay store."""
    session = MockGameSession()
    success, _msg, save_path = SaveGameService.save_game(
        session, "Phase5ReplayInstanceDelete"
    )
    assert success

    spy = MagicMock()
    SaveGameService.default().set_replay_store(spy)
    SaveGameService.delete_save(save_path)
    spy.clear_save_root.assert_called()


def test_save_without_registered_replay_store_is_safe(setup_tmpdir) -> None:
    """If no replay store is registered, save / delete still succeed (no notification)."""
    session = MockGameSession()
    success, _msg, save_path = SaveGameService.save_game(
        session, "Phase5ReplayInstanceNoStore"
    )
    assert success

    success2, _msg2 = SaveGameService.delete_save(save_path)
    assert success2
