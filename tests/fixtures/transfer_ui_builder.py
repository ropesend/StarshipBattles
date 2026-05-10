"""Test-only UI builders for ``TransferDialog`` (PROJ-328 Phase C).

These pair with the production ``TransferDialogUiBuilder`` at
``game/ui/screens/transfer_grid_renderer.py``. Both provide a
``build(dialog) -> None`` method matching the production builder
protocol.

The cheap-state delegates (``view_model``, ``_controller``,
``_renderer``, source/target lists, pending dict) are constructed in
Stage 1 of ``TransferDialog.__init__`` and survive ``bypass_init``
directly. The builders here are responsible only for the *widget*
slots that the production builder fills.

* ``NullTransferUiBuilder`` is a no-op builder. Use it when a test
  only exercises view-model / controller behaviour and does not
  touch widget refs. ``drop_source``, ``drop_target``, ``btn_*``,
  ``grid_container`` remain ``None``; per-row maps stay empty.

* ``MockTransferUiBuilder`` populates the dropdowns, every button,
  and the grid container with ``MagicMock`` instances. It also
  invokes ``dialog.populate_initial_data()`` so the source list +
  initial grid build run through the (real) view model and
  controller — the controller's ``handle_command`` path uses the
  test's mock facade as normal.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
and PROJ-325 PoC finding 2, the bypass branch invokes an explicitly
supplied ``ui_builder`` so these mocks are useful without per-call
wiring.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.transfer_dialog import TransferDialog


def _mock_dropdown(initial_options: List[str] | None = None,
                   selected: str = "") -> MagicMock:
    """Build a MagicMock that mimics a ``UIDropDownMenu``.

    Sets ``options_list`` (matches the attribute production code
    reads) and ``selected_option`` (read by event handlers).
    """
    dd = MagicMock(name="dropdown")
    dd.options_list = list(initial_options or [""])
    dd.selected_option = selected or (dd.options_list[0] if dd.options_list else "")
    # ``ui_container`` is read by the renderer's recreate_dropdown
    # path; supply a mock so any test that triggers a recreation
    # does not crash.
    dd.ui_container = MagicMock(name="ui_container")
    dd.relative_rect = MagicMock(name="relative_rect")
    return dd


class NullTransferUiBuilder:
    """No-op builder. Leaves widget slots at the Stage-1
    placeholders (``None`` / empty)."""

    def build(self, dialog: "TransferDialog") -> None:
        return None


class MockTransferUiBuilder:
    """Builder that populates ``TransferDialog`` widget slots with
    ``MagicMock`` instances and runs ``populate_initial_data`` so
    the dropdown source list + initial row data are seeded through
    the real view model and controller.

    Use when a test wants to exercise event-routing or pending-math
    flow against a "fully constructed" dialog without a live
    pygame display.
    """

    def build(self, dialog: "TransferDialog") -> None:
        # Chrome widget slots.
        dialog.drop_source = _mock_dropdown()
        dialog.drop_target = _mock_dropdown()
        dialog.btn_filter = MagicMock(name="btn_filter")
        dialog.btn_confirm = MagicMock(name="btn_confirm")
        dialog.btn_cancel = MagicMock(name="btn_cancel")
        dialog.btn_clear_all = MagicMock(name="btn_clear_all")
        dialog.grid_container = MagicMock(name="grid_container")
        dialog._grid_top_y = 0

        # Run the same initial-population flow production runs:
        # asks the controller for sources/targets at the hex, picks
        # a starting source, and rebuilds the grid. We monkey-patch
        # the renderer methods to no-op widget construction (the
        # widgets themselves are mocks above) — the view model / row
        # data still update correctly.
        original_recreate = dialog._renderer.recreate_dropdown
        original_build_grid = dialog._renderer.build_grid

        def _stub_recreate(_dlg, old_dropdown, options, selected):
            # Return a fresh mock dropdown with the new options so
            # subsequent ``selected_option`` reads work.
            return _mock_dropdown(initial_options=options, selected=selected)

        def _stub_build_grid(_dlg):
            # Skip widget construction; row_data has already been
            # rebuilt on the view model by the time we get here.
            return None

        dialog._renderer.recreate_dropdown = _stub_recreate  # type: ignore[assignment]
        dialog._renderer.build_grid = _stub_build_grid  # type: ignore[assignment]

        try:
            dialog.populate_initial_data()
        finally:
            dialog._renderer.recreate_dropdown = original_recreate  # type: ignore[assignment]
            dialog._renderer.build_grid = original_build_grid  # type: ignore[assignment]


__all__ = ["NullTransferUiBuilder", "MockTransferUiBuilder"]
