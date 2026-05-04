"""Test-only UI builders for ``CargoQuickDialog`` (PROJ-329C Phase 2).

These pair with the production ``CargoQuickDialogUiBuilder`` at
``game/ui/screens/cargo_quick_dialog.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullCargoQuickDialogUiBuilder`` is a no-op builder.

* ``MockCargoQuickDialogUiBuilder`` populates ``screen.lbl_title``,
  ``screen.btn_confirm``, ``screen.btn_cancel`` with MagicMocks. By
  default leaves ``screen.cargo_items`` empty (matches the "no items"
  production branch). Pass ``mock_items=...`` to seed cargo rows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.cargo_quick_dialog import CargoQuickDialog


class NullCargoQuickDialogUiBuilder:
    """No-op builder. Leaves widget slots in the empty Stage-1 state."""

    def build(self, screen: "CargoQuickDialog") -> None:
        return None


class MockCargoQuickDialogUiBuilder:
    """Builder that populates the dialog widget slots with MagicMocks.

    By default produces no cargo rows (matches the "no items" production
    branch). Tests can pass ``mock_items`` (list of dicts shaped like
    a production ``cargo_item``) to seed rows.
    """

    def __init__(
        self,
        mock_items: Optional[List[Dict[str, Any]]] = None,
        show_no_items: bool = False,
    ) -> None:
        self.mock_items = mock_items or []
        self.show_no_items = show_no_items or not self.mock_items

    def build(self, screen: "CargoQuickDialog") -> None:
        for required in ("cargo_items", "fleet", "direction"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockCargoQuickDialogUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        screen.lbl_title = MagicMock(name="lbl_title")
        screen.btn_confirm = MagicMock(name="btn_confirm")
        screen.btn_cancel = MagicMock(name="btn_cancel")

        for item in self.mock_items:
            row = {
                'label': item.get('label', 'mock'),
                'type': item.get('type', 'passengers'),
                'species_id': item.get('species_id'),
                'max': item.get('max', 0),
                'planet_id': item.get('planet_id'),
                'slider': item.get('slider', MagicMock(name='slider')),
                'lbl_val': item.get('lbl_val', MagicMock(name='lbl_val')),
                'btn_all': item.get('btn_all', MagicMock(name='btn_all')),
                'lbl': item.get('lbl', MagicMock(name='lbl')),
            }
            screen.cargo_items.append(row)

        if self.show_no_items and not screen.cargo_items:
            screen.lbl_no_items = MagicMock(name="lbl_no_items")


__all__ = [
    "NullCargoQuickDialogUiBuilder",
    "MockCargoQuickDialogUiBuilder",
]
