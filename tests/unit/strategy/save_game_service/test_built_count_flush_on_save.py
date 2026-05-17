"""PROJ-427 Phase 4: SaveGameService flushes pending built-counts at save time.

When ``SaveGameService.save_game(session)`` runs, it must ask every owning
``DesignCatalog`` on ``session.services.design_catalogs_by_empire`` to flush
its pending built-count increments through ``DesignRepository`` before the
save dict is written.

These tests pin three contracts:

- Save invokes ``flush_pending_built_counts`` on every per-empire catalog.
- A no-op flush (no pending entries) is safe — save still succeeds.
- If the session has no ``services`` attribute (degenerate / legacy session),
  save still succeeds without raising.

Schema discipline: NO ``Empire.designs_built_count`` field, NO save-format
version bump. The flush is a deferred write-back through the repository,
not a schema change.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.strategy.systems.save_game_service import SaveGameService
from tests.unit.strategy.save_game_service.conftest import MockGameSession


def _make_catalog_mock(flushed: int = 0) -> MagicMock:
    catalog = MagicMock()
    catalog.flush_pending_built_counts = MagicMock(return_value=flushed)
    return catalog


def test_save_flushes_every_empire_catalog(setup_tmpdir) -> None:
    """Each per-empire catalog must receive a ``flush_pending_built_counts``
    call when ``save_game`` runs."""
    session = MockGameSession(num_empires=2)
    cat0 = _make_catalog_mock(flushed=1)
    cat1 = _make_catalog_mock(flushed=0)

    services = MagicMock()
    services.design_catalogs_by_empire = {0: cat0, 1: cat1}
    repo = MagicMock()
    services.design_repository = repo
    session.services = services

    success, _msg, save_path = SaveGameService.save_game(session)

    assert success is True
    assert save_path is not None
    assert cat0.flush_pending_built_counts.called
    assert cat1.flush_pending_built_counts.called


def test_save_with_empty_pending_does_not_raise(setup_tmpdir) -> None:
    """If a catalog has nothing pending, the flush is still called and save
    succeeds — guard against a hypothetical short-circuit that skips empty
    catalogs and accidentally bypasses the flush for legitimately-empty ones."""
    session = MockGameSession(num_empires=1)
    cat = _make_catalog_mock(flushed=0)

    services = MagicMock()
    services.design_catalogs_by_empire = {0: cat}
    services.design_repository = MagicMock()
    session.services = services

    success, _msg, _path = SaveGameService.save_game(session)

    assert success is True
    assert cat.flush_pending_built_counts.called


def test_save_without_services_attribute_still_succeeds(setup_tmpdir) -> None:
    """A session built without the runtime-services bag (legacy / minimal
    test fixture) must still save without raising."""
    session = MockGameSession(num_empires=1)
    # No ``services`` attribute on the mock session.
    assert not hasattr(session, "services")

    success, _msg, save_path = SaveGameService.save_game(session)

    assert success is True
    assert save_path is not None
