"""Test-only UI builders for ``BuildQueueListWindow`` (PROJ-328 Phase A
Task A.2).

These pair with the production ``BuildQueueListUiBuilder`` at
``game/ui/screens/build_queue_list_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol.

* ``NullBuildQueueListUiBuilder`` is a no-op builder. Use it when a
  test only exercises cheap state (``empire``, ``_mapper``,
  ``on_close_callback``) and does not touch widget refs. The screen
  leaves ``row_labels`` at its empty-list placeholder.

* ``MockBuildQueueListUiBuilder`` populates ``screen.row_labels`` with
  one ``MagicMock`` per row that the production
  ``BuildQueueRowCollector`` would emit, plus a header row. Use it for
  tests that exercise ``kill()`` cleanup or assert the row count.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
and PROJ-325 PoC finding 2, the bypass branch invokes an explicitly
supplied ``ui_builder`` so these mocks are useful without per-call
wiring.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.build_queue_list_window import BuildQueueListWindow


class NullBuildQueueListUiBuilder:
    """No-op builder. Leaves ``screen.row_labels`` empty."""

    def build(self, screen: "BuildQueueListWindow") -> None:
        return None


class MockBuildQueueListUiBuilder:
    """Builder that populates ``screen.row_labels`` with ``MagicMock``
    instances — one per row from ``BuildQueueRowCollector.collect``,
    plus a header row.

    Honours the same row-collection logic as production so tests that
    seed the empire with construction queues see the expected row
    count.
    """

    def build(self, screen: "BuildQueueListWindow") -> None:
        # Mirror the production builder's "clear then rebuild" contract.
        for lbl in screen.row_labels:
            lbl.kill()
        screen.row_labels = []

        # Header row.
        screen.row_labels.append(MagicMock(name="header_label"))

        rows = screen._row_collector.collect(screen.empire)
        for i, row in enumerate(rows):
            mock = MagicMock(name=f"row_label_{i}")
            mock.text = row.text
            screen.row_labels.append(mock)

        if not rows:
            screen.row_labels.append(MagicMock(name="empty_label"))


__all__ = ["NullBuildQueueListUiBuilder", "MockBuildQueueListUiBuilder"]
