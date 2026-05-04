"""PROJ-328 Phase B — ``NewGameSetupViewModel``.

Pure-Python state container for ``NewGameSetupScreen``. Owns the
user-input state (player count, galaxy type, system count, per-player
race selections, currently-active modal) so the screen / controller /
UI builder can read and mutate state through one named surface.

NO pygame imports. NO validation logic (lives in
``NewGameSetupController``). NO widget references. The view model is a
cheap collaborator in the PROJ-325 sense: its constructor does not
create ``pygame_gui`` elements or require a live display.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``):
the heavyweight modal classes (``NewGameSetupScreen``,
``TransferDialog``) get a real MVVM split. This file is the
``ViewModel`` half of the NewGame split.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from game.strategy.engine.game_config import (
    DEFAULT_SYSTEM_COUNT,
    MAX_SYSTEM_COUNT,
    MIN_SYSTEM_COUNT,
)

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


# Maximum supported player slots. The screen always allocates four
# row widgets and toggles visibility based on ``player_count`` — keep
# the constant here so the controller / UI builder agree on the bound.
MAX_PLAYER_SLOTS: int = 4

# Default initial player count when the screen first opens.
DEFAULT_PLAYER_COUNT: int = 2

# Default galaxy type when the screen first opens.
DEFAULT_GALAXY_TYPE: str = "spiral"


class NewGameSetupViewModel:
    """Pure-Python state for ``NewGameSetupScreen``.

    Tracks the user-input state and exposes derived predicates the
    controller and UI builder consume. Holds no widget references and
    performs no validation (validation lives on the controller).

    The view model is constructed in ``Stage 1`` of the screen's
    ``__init__`` (before the ``bypass_init`` guard), so test fixtures
    that bypass the heavy ``pygame_gui`` shell still get a real,
    behavioural view-model instance.
    """

    def __init__(
        self,
        *,
        player_count: int = DEFAULT_PLAYER_COUNT,
        galaxy_type: str = DEFAULT_GALAXY_TYPE,
        system_count: int = DEFAULT_SYSTEM_COUNT,
    ) -> None:
        """Create a view model with the given initial selection state.

        Args:
            player_count: Initial player count (defaults to
                ``DEFAULT_PLAYER_COUNT``). Will be clamped via
                ``set_player_count`` semantics if a caller mutates it
                directly to an out-of-range value — but the UI dropdown
                only emits values in ``[1, MAX_PLAYER_SLOTS]``.
            galaxy_type: Initial galaxy layout type (defaults to
                ``DEFAULT_GALAXY_TYPE``). Validated by the controller
                at config-build time, not here.
            system_count: Initial star-system count (defaults to
                ``DEFAULT_SYSTEM_COUNT``). Bounded
                ``[MIN_SYSTEM_COUNT, MAX_SYSTEM_COUNT]`` by the
                slider's quadratic curve, not by the view model.
        """
        self.player_count: int = player_count
        self.galaxy_type: str = galaxy_type
        self.system_count: int = system_count

        # One slot per potential player — the screen always allocates
        # widgets for the maximum and toggles visibility. ``None``
        # means "use defaults" (default theme + manually-typed empire
        # name).
        self.player_races: List[Optional["RaceConfig"]] = [
            None for _ in range(MAX_PLAYER_SLOTS)
        ]

        # Modal state tracking. The screen opens at most one nested
        # race modal at a time; the index tells the callback which
        # player slot the result applies to.
        self.active_race_modal: object | None = None
        self.race_modal_player_index: int = -1

    # ------------------------------------------------------------------
    # Player-slot visibility / race selection
    # ------------------------------------------------------------------

    def is_player_visible(self, player_index: int) -> bool:
        """Return ``True`` if the player slot is within the active
        ``player_count`` and should therefore be visible in the UI."""
        return 0 <= player_index < self.player_count

    def set_player_count(self, count: int) -> List[int]:
        """Set the active player count and return the indices of any
        slots that became hidden as a result.

        Slots that became hidden may need their race selection
        cleared by the caller — this view model intentionally does
        NOT clear them itself so the caller can decide whether to
        clear, keep, or animate the change. The screen's existing
        behaviour (clear-on-hide) is encoded by the controller, not
        the view model.
        """
        previous = self.player_count
        self.player_count = count
        if count >= previous:
            return []
        return list(range(count, previous))

    def clear_race(self, player_index: int) -> None:
        """Clear the race selection for ``player_index``.

        Idempotent: clearing an already-empty slot is a no-op.
        """
        if 0 <= player_index < MAX_PLAYER_SLOTS:
            self.player_races[player_index] = None

    def set_race(self, player_index: int, race: "RaceConfig") -> None:
        """Assign ``race`` to ``player_index``."""
        if 0 <= player_index < MAX_PLAYER_SLOTS:
            self.player_races[player_index] = race

    def get_race(self, player_index: int) -> Optional["RaceConfig"]:
        """Return the race at ``player_index`` (or ``None``)."""
        if 0 <= player_index < MAX_PLAYER_SLOTS:
            return self.player_races[player_index]
        return None

    def active_player_races(self) -> List[Optional["RaceConfig"]]:
        """Return the race selections for the currently visible player
        slots — i.e. ``player_races[:player_count]``.

        Used by the controller when assembling ``GameConfig``.
        """
        return self.player_races[: self.player_count]

    # ------------------------------------------------------------------
    # Modal state
    # ------------------------------------------------------------------

    def open_race_modal(self, modal: object, player_index: int) -> None:
        """Record an opened race modal for ``player_index``."""
        self.active_race_modal = modal
        self.race_modal_player_index = player_index

    def close_race_modal(self) -> None:
        """Clear the modal-tracking state.

        Called from the controller's race-modal callbacks (selected,
        created, cancelled). Idempotent.
        """
        self.active_race_modal = None
        self.race_modal_player_index = -1

    # ------------------------------------------------------------------
    # System-count / galaxy bounds (delegated to game_config)
    # ------------------------------------------------------------------

    @staticmethod
    def system_count_min() -> int:
        """Return the minimum valid star-system count."""
        return MIN_SYSTEM_COUNT

    @staticmethod
    def system_count_max() -> int:
        """Return the maximum valid star-system count."""
        return MAX_SYSTEM_COUNT


__all__ = [
    "DEFAULT_GALAXY_TYPE",
    "DEFAULT_PLAYER_COUNT",
    "MAX_PLAYER_SLOTS",
    "NewGameSetupViewModel",
]
