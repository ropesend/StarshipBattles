"""Test-only UI builders for ``NewGameSetupScreen`` (PROJ-328 Phase B).

These pair with the production ``NewGameSetupUiBuilder`` at
``game/ui/screens/new_game_setup_ui_builder.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol.

The cheap-state delegates (``_view_model``, ``_controller``,
``race_library``, the ``on_*_callback`` references) are constructed in
Stage 1 of ``NewGameSetupScreen.__init__`` and survive ``bypass_init``
directly. The builders here are responsible only for the *widget*
slots that the production UI builder fills:

* ``save_name_input``, ``player_count_dropdown``,
  ``galaxy_type_dropdown``, ``system_count_slider``,
  ``system_count_label``, ``btn_start``, ``btn_cancel``,
  ``error_label``.
* The four-element row arrays — ``empire_name_inputs``,
  ``theme_labels``, ``num_labels``, ``race_preview_labels``,
  ``load_race_buttons``, ``setup_race_buttons``.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
and PROJ-325 PoC finding 2, the bypass branch invokes an explicitly
supplied ``ui_builder`` so these mocks are useful without per-call
wiring.

PoC finding 4 (renderer-internal reach-throughs): the existing
``test_new_game_setup_extended.py`` does NOT reach into any
controller- or view-model-internal widget refs — every widget access
is on the screen itself (e.g., ``screen.race_preview_labels[i]``).
``MockNewGameSetupUiBuilder`` therefore only writes to the screen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.new_game_setup_screen import NewGameSetupScreen


# Number of player-row widgets allocated. Mirrors
# ``new_game_setup_view_model.MAX_PLAYER_SLOTS`` — duplicated here so
# the fixture has no test-time dependency on production constants.
_PLAYER_SLOT_COUNT = 4


class NullNewGameSetupUiBuilder:
    """No-op builder. Leaves widget slots at their Stage-1 placeholder
    values (``None`` for scalar refs, empty lists for collections)."""

    def build(self, screen: "NewGameSetupScreen") -> None:
        return None


class MockNewGameSetupUiBuilder:
    """Builder that populates ``NewGameSetupScreen``'s widget slots with
    ``MagicMock`` instances matching the legacy helper expectations.

    Mirrors the per-attribute wiring that ``_make_screen`` in
    ``test_new_game_setup_extended.py`` used to do inline (lines 16-49
    pre-PROJ-328). Centralized here so adding/renaming a widget slot
    only requires one edit instead of one per test.
    """

    def build(self, screen: "NewGameSetupScreen") -> None:
        # Top-level widget refs.
        screen.save_name_input = MagicMock(name="save_name_input")
        screen.save_name_input.get_text.return_value = "TestSave"
        screen.player_count_dropdown = MagicMock(name="player_count_dropdown")
        screen.galaxy_type_dropdown = MagicMock(name="galaxy_type_dropdown")
        screen.system_count_slider = MagicMock(name="system_count_slider")
        screen.system_count_label = MagicMock(name="system_count_label")
        screen.btn_start = MagicMock(name="btn_start")
        screen.btn_cancel = MagicMock(name="btn_cancel")
        screen.error_label = MagicMock(name="error_label")

        # Player-row widgets — four slots regardless of current
        # ``player_count`` (the production builder also allocates four
        # and toggles visibility via ``_update_empire_visibility``).
        screen.empire_name_inputs = [
            MagicMock(name=f"empire_name_input_{i}")
            for i in range(_PLAYER_SLOT_COUNT)
        ]
        screen.theme_labels = [
            MagicMock(name=f"theme_label_{i}")
            for i in range(_PLAYER_SLOT_COUNT)
        ]
        screen.num_labels = [
            MagicMock(name=f"num_label_{i}")
            for i in range(_PLAYER_SLOT_COUNT)
        ]
        screen.race_preview_labels = [
            MagicMock(name=f"race_preview_label_{i}")
            for i in range(_PLAYER_SLOT_COUNT)
        ]
        screen.load_race_buttons = [
            MagicMock(name=f"load_race_button_{i}")
            for i in range(_PLAYER_SLOT_COUNT)
        ]
        screen.setup_race_buttons = [
            MagicMock(name=f"setup_race_button_{i}")
            for i in range(_PLAYER_SLOT_COUNT)
        ]


__all__ = ["NullNewGameSetupUiBuilder", "MockNewGameSetupUiBuilder"]
