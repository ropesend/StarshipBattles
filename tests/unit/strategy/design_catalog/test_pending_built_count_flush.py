"""PROJ-427 Phase 4: DesignCatalog pending built-count flush tests (TDD-first).

Catalog accumulates ``record_built(design_id)`` increments in memory during
the production tick. Only at save time does ``flush_pending_built_counts(
repository)`` drain those increments through ``DesignRepository.increment_built_count``.

These tests pin three contracts:

- ``record_built`` never touches the repository.
- ``flush_pending_built_counts`` empties the pending map and calls
  ``DesignRepository.increment_built_count`` exactly once per pending unit.
- ``flush_pending_built_counts`` is a no-op when nothing is pending.
"""
from __future__ import annotations

from typing import List
from unittest.mock import MagicMock

import pytest

from game.strategy.systems.design_catalog import DesignCatalog


class _RecordingRepo:
    """Minimal repository stub that records ``increment_built_count`` calls."""

    def __init__(self) -> None:
        self.increment_calls: List[str] = []

    def increment_built_count(self, design_id: str) -> bool:
        self.increment_calls.append(design_id)
        return True


def test_pending_increment_does_not_call_repository_during_tick() -> None:
    """``record_built`` must not call any repository method.

    Mirrors the Phase 0 no-disk-read assertion for tick-path: built-count
    increments are deferred until save time.
    """
    catalog = DesignCatalog(empire_id=1)
    repo = MagicMock()

    catalog.record_built("fighter_a")
    catalog.record_built("fighter_a")
    catalog.record_built("frigate_b")

    repo.assert_not_called()
    # The pending dict reflects the increments in-memory.
    assert dict(catalog.pending_built_counts) == {"fighter_a": 2, "frigate_b": 1}


def test_save_flushes_pending_increments_through_repository() -> None:
    """``flush_pending_built_counts`` calls ``increment_built_count`` once per
    pending unit and empties the pending map."""
    catalog = DesignCatalog(empire_id=1)
    catalog.record_built("fighter_a")
    catalog.record_built("fighter_a")
    catalog.record_built("frigate_b")

    repo = _RecordingRepo()
    flushed = catalog.flush_pending_built_counts(repo)

    # Two distinct design_ids flushed.
    assert flushed == 2
    # Three increment calls in total (2x fighter_a + 1x frigate_b).
    assert sorted(repo.increment_calls) == sorted(
        ["fighter_a", "fighter_a", "frigate_b"]
    )
    # Pending map drained.
    assert dict(catalog.pending_built_counts) == {}


def test_save_with_no_pending_increments_is_a_noop_on_repository() -> None:
    """No pending entries => zero repository calls and a 0 return."""
    catalog = DesignCatalog(empire_id=1)
    repo = _RecordingRepo()

    flushed = catalog.flush_pending_built_counts(repo)

    assert flushed == 0
    assert repo.increment_calls == []
