"""PROJ-328 Phase B — production ``NewGameSetupUiBuilder``.

Wraps the existing ``_create_ui()`` flow on ``NewGameSetupScreen`` so
the heavy ``pygame_gui`` widget construction lives behind a builder
protocol the screen calls *after* the bypass point. Tests can swap in
``NullNewGameSetupUiBuilder`` (no-op) or ``MockNewGameSetupUiBuilder``
(MagicMock-populated widget slots) from
``tests/fixtures/new_game_setup_ui_builder.py``.

See the consensus refactor plan at
``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``
for the rationale (why ``bypass_init`` stays + why production widget
construction sits behind a per-class builder rather than a universal
panel registry).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.screens.new_game_setup_screen import NewGameSetupScreen


class NewGameSetupUiBuilder:
    """Production widget builder. Delegates to the screen's existing
    private ``_create_ui()`` method.

    The screen owns the actual ``pygame_gui`` construction code (it
    reads ``self.get_container()`` etc., which is only meaningful on a
    fully initialized ``UIWindow``). The builder is a thin seam so the
    call can be substituted in tests; the implementation lives on the
    screen because the construction reaches into a number of screen
    helpers (``_create_empire_inputs`` / ``_update_empire_visibility``).
    """

    def build(self, screen: "NewGameSetupScreen") -> None:
        screen._create_ui()


__all__ = ["NewGameSetupUiBuilder"]
