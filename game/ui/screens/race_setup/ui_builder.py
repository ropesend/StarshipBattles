"""PROJ-325 Phase 3 — production ``RaceSetupUiBuilder``.

Wraps the existing ``_create_ui()`` flow on ``RaceSetupScreen`` so the
heavy ``pygame_gui`` widget construction lives behind a builder
protocol the screen calls *after* the bypass point. Tests can swap in
``NullRaceSetupUiBuilder`` (no-op) or ``MockRaceSetupUiBuilder``
(MagicMock-populated widget slots) from
``tests/fixtures/race_setup_ui_builders.py``.

See the consensus refactor plan at
``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``
for the rationale (why we did not eliminate ``bypass_init`` and why
production widget construction sits behind a per-class builder rather
than a universal panel registry).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.screens.race_setup.screen import RaceSetupScreen


class RaceSetupUiBuilder:
    """Production widget builder. Delegates to the screen's existing
    private ``_create_ui()`` method.

    The screen owns the actual pygame_gui construction code (it reads
    ``self.get_container()`` etc., which is only meaningful on a fully
    initialized ``UIWindow``). The builder is a thin seam so the call
    can be substituted in tests; the implementation lives on the
    screen because the construction reaches into a number of screen
    helpers (``_create_tab_buttons`` / ``_create_step_panels`` /
    ``_create_navigation_buttons``).
    """

    def build(self, screen: "RaceSetupScreen") -> None:
        screen._create_ui()


__all__ = ["RaceSetupUiBuilder"]
