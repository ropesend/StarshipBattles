"""Test-only UI builders for ``EmpirePanelWindow`` (PROJ-329B Phase 1).

Production builder lives at ``game.ui.screens.empire_panel_window:EmpirePanelUiBuilder``.

* ``NullEmpirePanelWindowUiBuilder`` — no-op.

* ``MockEmpirePanelWindowUiBuilder`` — populates ``screen.tab_buttons``
  and ``screen.step_panels`` with three MagicMock entries each (one per
  tab) so event-handler tests asserting tab-switch semantics still work,
  and sets ``screen.current_tab = TAB_TREASURY``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.empire_panel_window import EmpirePanelWindow


class NullEmpirePanelWindowUiBuilder:
    """No-op builder."""

    def build(self, screen: "EmpirePanelWindow") -> None:
        return None


class MockEmpirePanelWindowUiBuilder:
    """Populate tab buttons + tab panels with MagicMocks; mirror tab
    button behaviour (each btn carries its tab_index attribute, and
    select/unselect flip an `is_selected` flag).
    """

    def build(self, screen: "EmpirePanelWindow") -> None:
        from game.ui.screens.empire_panel_window import TAB_NAMES, TAB_TREASURY

        screen.tab_buttons = []
        screen.step_panels = []

        for i, name in enumerate(TAB_NAMES):
            btn = MagicMock(name=f"tab_button_{name}")
            btn.tab_index = i
            btn.is_selected = False

            def _select(_btn=btn) -> None:
                _btn.is_selected = True

            def _unselect(_btn=btn) -> None:
                _btn.is_selected = False

            btn.select.side_effect = _select
            btn.unselect.side_effect = _unselect
            screen.tab_buttons.append(btn)

            panel = MagicMock(name=f"step_panel_{name}")
            panel.is_visible = False

            def _show(_p=panel) -> None:
                _p.is_visible = True

            def _hide(_p=panel) -> None:
                _p.is_visible = False

            panel.show.side_effect = _show
            panel.hide.side_effect = _hide
            screen.step_panels.append(panel)

        # Mirror production: initial tab is TAB_TREASURY, panel shown,
        # button selected.
        screen.current_tab = TAB_TREASURY
        screen.step_panels[TAB_TREASURY].show()
        screen.tab_buttons[TAB_TREASURY].select()


__all__ = [
    "NullEmpirePanelWindowUiBuilder",
    "MockEmpirePanelWindowUiBuilder",
]
