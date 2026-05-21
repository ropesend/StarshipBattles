"""PROJ-328 Phase B — ``NewGameSetupController``.

Owns the *mutations* and *lifecycle* for ``NewGameSetupScreen``:

* Save-name validation (filesystem-character checks + uniqueness).
* ``GameConfig`` construction from the view-model state.
* Race-modal callbacks (open browser / open setup / on-selected /
  on-created / on-cancelled).
* Start / cancel flow.

The controller takes a screen reference so it can drive the legacy
widget refs (``empire_name_inputs[i].get_text()``, ``error_label.set_text``,
``save_name_input.get_text()``, ``race_preview_labels``, etc.) — those
widget references live on the screen because the production UI builder
populates them, and existing tests reach into them. The controller is
the single named place that pulls / pushes those widget values; the
view model stays widget-free.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``):
the heavyweight modal classes (``NewGameSetupScreen``,
``TransferDialog``) get a real MVVM split. This file is the
``Controller`` half of the NewGame split.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple

import pygame

from game.core.error_codes import ErrorCode
from game.core.exceptions import SessionInitializationError, ValidationException
from game.core.paths import Paths
from game.strategy.engine.game_config import (
    DEFAULT_SYSTEM_COUNT,
    GameConfig,
    PlayerConfig,
    THEME_DEFAULTS,
)

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.systems.race_library import RaceLibrary
    from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
    from game.ui.screens.new_game_setup_view_model import NewGameSetupViewModel


logger = logging.getLogger(__name__)


class NewGameSetupController:
    """Mutation + lifecycle owner for ``NewGameSetupScreen``.

    Construction is cheap — no ``pygame_gui`` widgets are created in
    ``__init__``. The controller is built in Stage 1 of the screen's
    constructor (before the ``bypass_init`` guard) so test fixtures
    can exercise validation / config-build / callback behaviour
    without a live pygame display.
    """

    def __init__(
        self,
        *,
        screen: "NewGameSetupScreen",
        view_model: "NewGameSetupViewModel",
        race_library: "RaceLibrary",
        on_start_callback: Callable[[GameConfig], None],
        on_cancel_callback: Callable[[], None],
    ) -> None:
        self._screen = screen
        self._view_model = view_model
        self._race_library = race_library
        self._on_start_callback = on_start_callback
        self._on_cancel_callback = on_cancel_callback

    # ------------------------------------------------------------------
    # Race-modal callbacks (Load Species / Setup Species buttons)
    # ------------------------------------------------------------------

    def on_load_race_clicked(self, player_index: int) -> None:
        """Handle Load Species button — open the race browser dialog."""
        logger.debug(f"Opening race browser for player {player_index + 1}")

        # Import directly from the canonical location.
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        dialog_rect = self._centered_modal_rect(width=600, height=500)

        modal = RaceBrowserDialog(
            rect=dialog_rect,
            manager=self._screen.ui_manager,
            race_library=self._race_library,
            on_select_callback=lambda race: self.on_race_selected(player_index, race),
            on_cancel_callback=self.on_race_dialog_cancelled,
        )
        self._view_model.open_race_modal(modal, player_index)

    def on_setup_race_clicked(self, player_index: int) -> None:
        """Handle Setup Species button — open the race setup wizard."""
        logger.debug(f"Opening race setup for player {player_index + 1}")

        # Import here to avoid circular imports (the race_setup
        # package transitively imports new_game_setup_screen at
        # module load; deferring keeps the cycle broken).
        from game.ui.screens.race_setup.screen import RaceSetupScreen

        # Race setup is larger than the browser — center on screen.
        setup_rect = self._screen_centered_rect(width=1800, height=1200)

        modal = RaceSetupScreen(
            rect=setup_rect,
            manager=self._screen.ui_manager,
            on_complete_callback=lambda race: self.on_race_created(player_index, race),
            on_cancel_callback=self.on_race_dialog_cancelled,
            # BUG-92: pass loaded race so Setup Species edits existing.
            race_to_edit=self._view_model.get_race(player_index),
        )
        self._view_model.open_race_modal(modal, player_index)

    def on_race_selected(self, player_index: int, race_config: "RaceConfig") -> None:
        """Race chosen from the browser dialog."""
        logger.info(
            f"Player {player_index + 1} selected race: {race_config.name}"
        )
        self._view_model.set_race(player_index, race_config)
        self._screen._update_race_display(player_index)
        self._view_model.close_race_modal()

    def on_race_created(self, player_index: int, race_config: "RaceConfig") -> None:
        """Race created via the setup wizard."""
        logger.info(
            f"Player {player_index + 1} created race: {race_config.name}"
        )
        self._view_model.set_race(player_index, race_config)
        self._screen._update_race_display(player_index)
        self._view_model.close_race_modal()

    def on_race_dialog_cancelled(self) -> None:
        """Race dialog dismissed without a selection — clear modal state."""
        logger.debug("Race dialog cancelled")
        self._view_model.close_race_modal()

    # ------------------------------------------------------------------
    # Start / Cancel flow
    # ------------------------------------------------------------------

    def on_start_clicked(self) -> None:
        """Validate, build a ``GameConfig``, fire ``on_start_callback``,
        and kill the window. On validation failure: set the error label
        and return WITHOUT firing the callback or killing the window."""
        save_name = self._screen.save_name_input.get_text().strip()

        # PROJ-392: callers go through the controller directly; the
        # screen-level shim was removed.
        is_valid, error = NewGameSetupController.validate_save_name(
            save_name, Paths.SAVES_DIR
        )
        if not is_valid:
            self._screen.error_label.set_text(error)
            return

        empire_names = self._collect_empire_names()

        try:
            config = self.build_game_config(
                save_name,
                self._view_model.player_count,
                empire_names,
                self._view_model.active_player_races(),
                self._view_model.galaxy_type,
                self._view_model.system_count,
            )
        except ValueError as exc:
            self._screen.error_label.set_text(str(exc))
            return

        logger.info(
            f"Starting new game: {save_name} with "
            f"{self._view_model.player_count} players"
        )
        # PROJ-466: the start callback constructs a GameSession, which can
        # raise SessionInitializationError on galaxy-generation failure. Keep
        # the setup window alive and surface the error rather than killing the
        # window (leaving the session indeterminate) or letting it crash.
        try:
            self._on_start_callback(config)
        except SessionInitializationError as exc:
            logger.error("New game start failed during session init: %s", exc)
            self._screen.error_label.set_text(
                "Could not start game (galaxy generation failed). "
                "Try a different save / fewer systems."
            )
            return
        self._screen.kill()

    def on_cancel_clicked(self) -> None:
        """Fire ``on_cancel_callback`` and kill the window."""
        logger.debug("New game setup cancelled")
        self._on_cancel_callback()
        self._screen.kill()

    # ------------------------------------------------------------------
    # Helpers — empire names + modal rects
    # ------------------------------------------------------------------

    def _collect_empire_names(self) -> List[str]:
        """Pull empire names from the input widgets / race selections."""
        names: List[str] = []
        for i in range(self._view_model.player_count):
            race = self._view_model.get_race(i)
            if race is not None:
                names.append(race.name)
            else:
                names.append(self._screen.empire_name_inputs[i].get_text().strip())
        return names

    def _centered_modal_rect(self, *, width: int, height: int) -> pygame.Rect:
        """Center a modal of ``width x height`` over the parent window."""
        window_rect = self._screen.get_abs_rect()
        x = window_rect.centerx - width // 2
        y = window_rect.centery - height // 2
        return pygame.Rect(x, y, width, height)

    def _screen_centered_rect(self, *, width: int, height: int) -> pygame.Rect:
        """Center a modal on the full screen (for the race-setup wizard,
        which is larger than the parent window)."""
        screen_w = 1920  # fallback
        screen_h = 1080
        if self._screen.ui_manager:
            screen_w = self._screen.ui_manager.window_resolution[0]
            screen_h = self._screen.ui_manager.window_resolution[1]
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        return pygame.Rect(x, y, width, height)

    # ------------------------------------------------------------------
    # Static-method API — canonical home for save-name validation /
    # default-save-name generation. PROJ-392 dropped the ``NewGameSetupScreen``
    # static shims; tests and production call these directly.
    # ------------------------------------------------------------------

    @staticmethod
    def validate_save_name(
        name: str, saves_folder: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Validate a save name.

        Args:
            name: Save name to validate.
            saves_folder: Optional path to saves folder for uniqueness
                check (only enforced when the folder exists).

        Returns:
            ``(is_valid, error_message)`` — ``error_message`` is empty
            when valid.
        """
        if not name or not name.strip():
            return False, "Save name cannot be empty"

        name = name.strip()

        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, name):
            return False, "Save name contains invalid characters"

        if saves_folder and os.path.exists(saves_folder):
            save_path = os.path.join(saves_folder, name)
            if os.path.exists(save_path):
                return False, f"Save '{name}' already exists"

        return True, ""

    @staticmethod
    def generate_default_save_name() -> str:
        """Generate a default save name with current timestamp."""
        return f"save game {datetime.now().strftime('%Y-%m-%d %H%M')}"

    @staticmethod
    def build_game_config(
        save_name: str,
        player_count: int,
        empire_names: List[str],
        race_configs: Optional[List[Optional["RaceConfig"]]] = None,
        galaxy_type: str = "spiral",
        system_count: int = DEFAULT_SYSTEM_COUNT,
    ) -> GameConfig:
        """Build a ``GameConfig`` from setup-screen values.

        Args:
            save_name: Name for the save folder.
            player_count: Number of players (1-4).
            empire_names: List of empire names (may include empty strings).
            race_configs: Optional list of ``RaceConfig`` for each
                player (``None`` = use defaults).
            galaxy_type: Galaxy layout type (default: ``"spiral"``).
            system_count: Number of star systems
                (``MIN_SYSTEM_COUNT``-``MAX_SYSTEM_COUNT``, default
                ``DEFAULT_SYSTEM_COUNT``). FEAT-27: at
                ``system_count=1`` all empires share the lone system on
                different planets.

        Returns:
            Configured ``GameConfig``.

        Raises:
            ValidationException: If ``player_count`` or ``system_count``
                is invalid (e.g., more empires than systems at N>=2).
        """
        if player_count < 1 or player_count > 4:
            raise ValidationException(
                f"Invalid player count: {player_count}",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"player_count": player_count, "valid_range": "1-4"},
            )

        players: List[PlayerConfig] = []
        for i in range(player_count):
            race = (
                race_configs[i]
                if race_configs and i < len(race_configs)
                else None
            )

            # Name resolution: race name > manual input > default.
            if race and race.name:
                name = race.name
            elif i < len(empire_names) and empire_names[i].strip():
                name = empire_names[i].strip()
            else:
                name = f"Empire {i + 1}"

            # Theme resolution: race theme > default theme.
            if race and race.theme_id:
                theme = race.theme_id
                logger.debug(f"Player {i} using race theme: {theme}")
            else:
                theme = THEME_DEFAULTS[i][0]
                logger.debug(f"Player {i} using default theme: {theme}")

            color = THEME_DEFAULTS[i][1]  # color always from defaults

            flag_id = race.flag_id if race else ""
            portrait_id = race.portrait_id if race else ""
            race_id = race.race_id if race else None

            players.append(
                PlayerConfig(
                    name=name,
                    theme=theme,
                    color=color,
                    is_human=True,
                    race_id=race_id,
                    flag_id=flag_id,
                    portrait_id=portrait_id,
                    race_config=race,
                )
            )

        return GameConfig(
            save_name=save_name,
            players=players,
            galaxy_type=galaxy_type,
            system_count=system_count,
        )


__all__ = ["NewGameSetupController"]
