"""
PROJ-343 T1.5 — Failing API test: CargoQuickDialog must guarantee window
teardown even on facade-dispatch exception.

Bug shape (verified by planning instance 2026-05-04):
- `cargo_quick_dialog.py:300-306` `_issue_orders` calls
  `self.controller.issue_orders(self.cargo_items)` and only THEN calls
  `self.kill()`. There is no `try/finally`.
- The controller calls `facade.handle_command()`, which can raise on
  dispatch failure. When it does, the exception propagates with the
  dialog still alive — exact bug class audit S1.2 fixed for TransferDialog.

Fix shape (PROJ-343 Phase 7): wrap `_issue_orders` body in
`try/finally: self.kill()` so the dialog always tears down.

Currently FAILS: kill is NOT called when controller raises. Will PASS once
T1.5 is fixed.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.ui.screens.cargo_quick_dialog import CargoQuickDialog


def test_dialog_kills_when_controller_raises_during_issue_orders():
    """A controller exception during `issue_orders` must NOT leak — `kill`
    is invoked even when the dispatch raises.

    Built via `__new__` to avoid pygame_gui side effects.
    """
    dialog = CargoQuickDialog.__new__(CargoQuickDialog)

    controller = MagicMock()
    controller.issue_orders.side_effect = RuntimeError("forced facade failure")

    dialog.controller = controller
    dialog.cargo_items = []
    dialog.kill = MagicMock()

    # Exception MUST still propagate to the caller — the fix is "kill in
    # finally", not "swallow exceptions".
    with pytest.raises(RuntimeError, match="forced facade failure"):
        dialog._issue_orders()

    controller.issue_orders.assert_called_once()
    # Currently FAILS: `kill()` runs only after `issue_orders` returns
    # normally; on exception it's skipped.
    dialog.kill.assert_called_once()
