"""
PROJ-343 T1.4 — Failing API test: TransferDialog must stay open on
input-validation aborts so the user can correct.

Bug shape (verified by planning instance 2026-05-04):
- `transfer_dialog.py:372-378` `_on_confirm` uses `try/finally: self.kill()`.
  The dialog ALWAYS closes — even when the controller's `confirm_pending`
  returns 0 because of input-validation issues (no source/target, both
  endpoints non-fleet, all pending zero).
- Pre-refactor (audit S1.2 added the `try/finally`): there were three
  early-return abort paths that kept the dialog open.

Fix shape (PROJ-343 Phase 6): the controller returns a richer
`ConfirmResult(orders_issued, aborted_for_correction)` and the dialog
calls `kill()` only when `not aborted_for_correction`. Unrecoverable
exceptions still kill (no leaking modals).

Currently FAILS: dialog.kill IS called on validation abort. Will PASS
once T1.4 is fixed.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.ui.screens.transfer_dialog import TransferDialog


def test_dialog_surfaces_rejection_message_via_scene_ui():
    """QA Obs 5 follow-up (2026-05-16): when ``confirm_pending`` returns
    a ``rejection_message`` (every command rejected by the facade), the
    dialog calls ``scene.ui.show_error_message`` so the user actually
    sees why "Confirm All" appeared to do nothing. Pre-fix the message
    was logged but silently swallowed at the UI."""
    dialog = TransferDialog.__new__(TransferDialog)

    confirm_result = MagicMock()
    confirm_result.orders_issued = 0
    confirm_result.aborted_for_correction = True
    confirm_result.rejection_message = "Invalid cargo type 'vehicle:qs_mine'."

    controller = MagicMock()
    controller.confirm_pending.return_value = confirm_result
    dialog._controller = controller
    dialog.kill = MagicMock()

    # Wire the scene → ui.show_error_message surface the dialog uses.
    scene = MagicMock()
    scene.ui.show_error_message = MagicMock()
    dialog.scene = scene

    dialog._on_confirm()

    scene.ui.show_error_message.assert_called_once_with(
        "Transfer failed: Invalid cargo type 'vehicle:qs_mine'.",
    )
    dialog.kill.assert_not_called()  # validation abort stays open.


def test_dialog_no_message_call_when_no_rejection_message():
    """Validation abort with no rejection (e.g. all pending zero) must
    NOT trigger an error popup. The dialog stays open silently."""
    dialog = TransferDialog.__new__(TransferDialog)

    confirm_result = MagicMock()
    confirm_result.orders_issued = 0
    confirm_result.aborted_for_correction = True
    confirm_result.rejection_message = None

    controller = MagicMock()
    controller.confirm_pending.return_value = confirm_result
    dialog._controller = controller
    dialog.kill = MagicMock()

    scene = MagicMock()
    scene.ui.show_error_message = MagicMock()
    dialog.scene = scene

    dialog._on_confirm()

    scene.ui.show_error_message.assert_not_called()


def test_dialog_stays_open_when_controller_signals_validation_abort():
    """Validation-abort path (e.g., no source/target picked) must keep the
    dialog open — `kill()` is NOT called.

    Built via `__new__` to avoid pygame_gui side effects; we manually wire
    only the attributes `_on_confirm` touches.
    """
    dialog = TransferDialog.__new__(TransferDialog)

    # Stub controller. Post-fix the controller will return a
    # `ConfirmResult(orders_issued=0, aborted_for_correction=True)`.
    # Pre-fix the controller returns plain int 0 — but the always-kill
    # `try/finally` ignores the return value and kills regardless.
    confirm_result = MagicMock()
    confirm_result.orders_issued = 0
    confirm_result.aborted_for_correction = True

    controller = MagicMock()
    controller.confirm_pending.return_value = confirm_result

    dialog._controller = controller

    # Spy on kill — we want to assert it's NOT called.
    dialog.kill = MagicMock()

    dialog._on_confirm()

    controller.confirm_pending.assert_called_once()
    # Currently FAILS: `try/finally: self.kill()` always invokes kill().
    # After T1.4 fix: dialog stays open on validation abort.
    dialog.kill.assert_not_called()
