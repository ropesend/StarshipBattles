"""Test-only UI builders for ``OrdersWindow`` (PROJ-328 Phase A
Task A.3).

These pair with the production ``OrdersWindowUiBuilder`` at
``game/ui/screens/orders_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol.

* ``NullOrdersUiBuilder`` is a no-op builder. Use it when a test only
  exercises cheap state (``entity``, ``_mapper``, callbacks,
  ``_order_describer``) and does not touch widget refs. ``rows``
  remains empty; ``list_container`` and ``btn_clear`` remain ``None``.

* ``MockOrdersUiBuilder`` populates ``screen.list_container``,
  ``screen.btn_clear``, and ``screen.rows`` with ``MagicMock``
  instances matching the legacy ``__new__``-helper expectations.
  Routes through the real ``OrderDescriber`` so seeding the entity
  with orders produces the right number of rows.

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
    from game.ui.screens.orders_window import OrdersWindow


class NullOrdersUiBuilder:
    """No-op builder. Leaves widget slots at the placeholder values
    set in Stage-1."""

    def build(self, screen: "OrdersWindow") -> None:
        return None


class MockOrdersUiBuilder:
    """Builder that populates ``OrdersWindow``'s widget slots with
    ``MagicMock`` instances.

    Routes through the real ``OrderDescriber`` so tests that seed
    ``entity.orders`` with concrete ``Order`` instances see the right
    number of rows in ``screen.rows``.
    """

    def build(self, screen: "OrdersWindow") -> None:
        screen.list_container = MagicMock(name="list_container")
        screen.btn_clear = MagicMock(name="btn_clear")

        descriptions = screen._order_describer.describe_all(screen.entity)
        screen.rows = []
        for desc_row in descriptions:
            row = {
                'idx': MagicMock(name=f"idx_{desc_row.index}"),
                'desc': MagicMock(name=f"desc_{desc_row.index}"),
                'description': desc_row,
                'order_ref': desc_row.order,
                'up': MagicMock(name=f"up_{desc_row.index}"),
                'down': MagicMock(name=f"down_{desc_row.index}"),
                'del': MagicMock(name=f"del_{desc_row.index}"),
            }
            if desc_row.is_editable:
                row['edit'] = MagicMock(name=f"edit_{desc_row.index}")
            screen.rows.append(row)


__all__ = ["NullOrdersUiBuilder", "MockOrdersUiBuilder"]
