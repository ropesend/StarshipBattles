"""
New Game Setup Screen - UI for configuring a new game.

Allows users to:
- Enter a save name
- Select number of players (1-4)
- Select or create races for each player
- Start the game with race-based themes and visuals

PROJ-40: Moved RaceConfig to TYPE_CHECKING (type-hints only).
"""
from __future__ import annotations

import os
import re
from datetime import datetime
import pygame
import pygame_gui
from typing import Callable, Optional, Tuple, List, TYPE_CHECKING

import logging

logger = logging.getLogger(__name__)
from game.core.paths import Paths
from game.ui.colors import TEXT_ERROR
from game.strategy.engine.game_config import GameConfig, PlayerConfig, THEME_DEFAULTS, VALID_GALAXY_TYPES
from game.strategy.systems.race_library import RaceLibrary
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class NewGameSetupScreen(pygame_gui.elements.UIWindow):
    """Window for configuring a new game."""

    def __init__(self, rect, manager, on_start_callback: Callable[[GameConfig], None],
                 on_cancel_callback: Callable[[], None]):
        """
        Create new game setup window.

        Args:
            rect: Window rectangle
            manager: pygame_gui UIManager
            on_start_callback: Callback(GameConfig) when user starts game
            on_cancel_callback: Callback() when user cancels
        """
        super().__init__(
            rect,
            manager,
            window_display_title="New Game Setup",
            object_id="#new_game_setup_window",
            resizable=False
        )

        self.on_start_callback = on_start_callback
        self.on_cancel_callback = on_cancel_callback

        self.player_count = 2  # Default
        self.galaxy_type = "spiral"  # Default galaxy type
        self.empire_name_inputs = []  # List of UITextEntryLine
        self.theme_labels = []  # List of UILabel showing assigned theme
        self.num_labels = []  # List of UILabel for player numbers

        # Race selection state
        self.race_library = RaceLibrary()
        self.player_races: List[Optional[RaceConfig]] = [None, None, None, None]
        self.race_preview_labels: List[pygame_gui.elements.UILabel] = []
        self.load_race_buttons: List[pygame_gui.elements.UIButton] = []
        self.setup_race_buttons: List[pygame_gui.elements.UIButton] = []

        # Modal state tracking
        self.active_race_modal = None
        self.race_modal_player_index = -1

        self._create_ui()

    def _create_ui(self) -> None:
        """Create UI elements."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        y_offset = 10

        # Save name label and input
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Save Name:",
            manager=self.ui_manager,
            container=container
        )
        y_offset += 25

        self.save_name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, y_offset, content_width, 35),
            manager=self.ui_manager,
            container=container,
            placeholder_text="Enter save name..."
        )
        self.save_name_input.set_text(self.generate_default_save_name())
        y_offset += 45

        # Player count label and dropdown
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Number of Players:",
            manager=self.ui_manager,
            container=container
        )
        y_offset += 25

        self.player_count_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["1", "2", "3", "4"],
            starting_option="2",
            relative_rect=pygame.Rect(10, y_offset, 100, 35),
            manager=self.ui_manager,
            container=container
        )
        y_offset += 50

        # Galaxy type label and dropdown
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Galaxy Type:",
            manager=self.ui_manager,
            container=container
        )
        y_offset += 25

        # Sort galaxy types for consistent display, with spiral first
        galaxy_types = sorted(list(VALID_GALAXY_TYPES))
        self.galaxy_type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=galaxy_types,
            starting_option=self.galaxy_type,
            relative_rect=pygame.Rect(10, y_offset, 150, 35),
            manager=self.ui_manager,
            container=container
        )
        y_offset += 50

        # Star system count label, slider, and value display
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Star Systems:",
            manager=self.ui_manager,
            container=container
        )
        y_offset += 25

        self.system_count = 50  # Default
        self.system_count_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(10, y_offset, content_width - 60, 30),
            start_value=self.system_count,
            value_range=(25, 150),
            manager=self.ui_manager,
            container=container,
            click_increment=5
        )
        self.system_count_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(content_width - 40, y_offset, 50, 30),
            text=str(self.system_count),
            manager=self.ui_manager,
            container=container
        )
        y_offset += 45

        # Empire/Race section header
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, content_width, 25),
            text="Player Species:",
            manager=self.ui_manager,
            container=container
        )
        y_offset += 30

        # Create empire name inputs with race selection (4 max, hide unused)
        self.empire_inputs_start_y = y_offset
        self._create_empire_inputs()

        # Calculate button position at bottom
        button_y = container.get_size()[1] - 60
        button_width = 120

        self.btn_start = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, button_y, button_width, 40),
            text="Start Game",
            manager=self.ui_manager,
            container=container
        )

        self.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - button_width + 10, button_y, button_width, 40),
            text="Cancel",
            manager=self.ui_manager,
            container=container
        )

        # Error label (hidden by default)
        self.error_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, button_y - 30, content_width, 25),
            text="",
            manager=self.ui_manager,
            container=container
        )
        self.error_label.text_colour = pygame.Color(*TEXT_ERROR)

    def _create_empire_inputs(self) -> None:
        """Create empire name input fields with race selection for each player slot."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        y_offset = self.empire_inputs_start_y

        # Clear existing elements
        for inp in self.empire_name_inputs:
            inp.kill()
        for lbl in self.theme_labels:
            lbl.kill()
        for lbl in self.num_labels:
            lbl.kill()
        for lbl in self.race_preview_labels:
            lbl.kill()
        for btn in self.load_race_buttons:
            btn.kill()
        for btn in self.setup_race_buttons:
            btn.kill()

        self.empire_name_inputs = []
        self.theme_labels = []
        self.num_labels = []
        self.race_preview_labels = []
        self.load_race_buttons = []
        self.setup_race_buttons = []

        # Row height for each player (name row + race row + spacing)
        row_height = 95

        # Create inputs for each potential player
        for i in range(4):
            row_y = y_offset + (i * row_height)

            # Player number label
            num_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, row_y, 80, 30),
                text=f"Player {i + 1}:",
                manager=self.ui_manager,
                container=container
            )
            self.num_labels.append(num_label)

            # Name input (hidden when race selected - race name becomes empire name)
            name_input = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(90, row_y, 200, 30),
                manager=self.ui_manager,
                container=container,
                placeholder_text=f"Empire {i + 1}"
            )
            self.empire_name_inputs.append(name_input)

            # Theme label (auto-assigned, shows race theme when selected)
            theme_name = THEME_DEFAULTS[i][0]
            theme_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(300, row_y, 200, 30),
                text=f"Theme: {theme_name}",
                manager=self.ui_manager,
                container=container
            )
            self.theme_labels.append(theme_label)

            # Race selection row (below name row)
            race_row_y = row_y + 35

            # Race preview label (shows selected race name or instruction)
            race_preview = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(90, race_row_y, 280, 30),
                text="No species selected (using defaults)",
                manager=self.ui_manager,
                container=container
            )
            self.race_preview_labels.append(race_preview)

            # Load Race button
            load_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(380, race_row_y, 100, 30),
                text="Load Species",
                manager=self.ui_manager,
                container=container
            )
            self.load_race_buttons.append(load_btn)

            # Setup Race button
            setup_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(490, race_row_y, 110, 30),
                text="Setup Species",
                manager=self.ui_manager,
                container=container
            )
            self.setup_race_buttons.append(setup_btn)

        # Update visibility based on current player count
        self._update_empire_visibility()

    def _update_empire_visibility(self) -> None:
        """Show/hide empire inputs based on player count."""
        for i in range(4):
            visible = i < self.player_count
            elements = [
                self.empire_name_inputs[i],
                self.theme_labels[i],
                self.num_labels[i],
                self.race_preview_labels[i],
                self.load_race_buttons[i],
                self.setup_race_buttons[i]
            ]
            for elem in elements:
                if visible:
                    elem.show()
                else:
                    elem.hide()

            # Clear race selection for hidden players
            if not visible and self.player_races[i] is not None:
                self.player_races[i] = None
                self._update_race_display(i)

    def _update_race_display(self, player_index: int) -> None:
        """Update the race preview display for a player."""
        race = self.player_races[player_index]

        if race:
            # Race selected - show faction name (or race name fallback)
            display_name = race.faction_name if race.faction_name else race.name
            self.race_preview_labels[player_index].set_text(f"Species: {display_name}")
            # Show government and society type if available
            details = []
            if race.government_type:
                details.append(race.government_type)
            if race.society_type:
                details.append(race.society_type)
            if details:
                self.theme_labels[player_index].set_text(" • ".join(details))
            else:
                self.theme_labels[player_index].set_text(f"Theme: {race.theme_id}")
            # Hide name input - race name will be used
            self.empire_name_inputs[player_index].hide()
        else:
            # No race - show default state
            self.race_preview_labels[player_index].set_text("No species selected (using defaults)")
            default_theme = THEME_DEFAULTS[player_index][0]
            self.theme_labels[player_index].set_text(f"Theme: {default_theme}")
            # Show name input for manual entry
            if player_index < self.player_count:
                self.empire_name_inputs[player_index].show()

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process pygame events."""
        # If a modal is active, let it handle events first
        if self.active_race_modal is not None:
            return super().process_event(event)

        handled = super().process_event(event)

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.player_count_dropdown:
                self.player_count = int(event.text)
                self._update_empire_visibility()
                handled = True
            elif event.ui_element == self.galaxy_type_dropdown:
                self.galaxy_type = event.text
                handled = True

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.system_count_slider:
                self.system_count = int(event.value)
                self.system_count_label.set_text(str(self.system_count))
                handled = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_start:
                self._on_start_clicked()
                handled = True
            elif event.ui_element == self.btn_cancel:
                self._on_cancel_clicked()
                handled = True
            else:
                # Check race buttons
                for i, btn in enumerate(self.load_race_buttons):
                    if event.ui_element == btn:
                        self._on_load_race_clicked(i)
                        handled = True
                        break

                for i, btn in enumerate(self.setup_race_buttons):
                    if event.ui_element == btn:
                        self._on_setup_race_clicked(i)
                        handled = True
                        break

        return handled

    def _on_load_race_clicked(self, player_index: int) -> None:
        """Handle Load Race button click - open race browser dialog."""
        logger.debug(f"Opening race browser for player {player_index + 1}")

        # Import here to avoid circular imports
        from game.ui.screens.race_setup_screen import RaceBrowserDialog

        # Get window position for dialog placement
        window_rect = self.get_abs_rect()
        dialog_width = 600
        dialog_height = 500

        # Center dialog over the main window
        dialog_x = window_rect.centerx - dialog_width // 2
        dialog_y = window_rect.centery - dialog_height // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

        # Create and show the race browser dialog
        self.active_race_modal = RaceBrowserDialog(
            rect=dialog_rect,
            manager=self.ui_manager,
            race_library=self.race_library,
            on_select_callback=lambda race: self._on_race_selected(player_index, race),
            on_cancel_callback=self._on_race_dialog_cancelled
        )
        self.race_modal_player_index = player_index

    def _on_setup_race_clicked(self, player_index: int) -> None:
        """Handle Setup Race button click - open race setup screen."""
        logger.debug(f"Opening race setup for player {player_index + 1}")

        # Import here to avoid circular imports
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        # Race setup is larger - center it on screen
        setup_width = 1800
        setup_height = 1200

        # Center on screen (use reasonable defaults)
        screen_width = 1920  # Fallback
        screen_height = 1080
        if self.ui_manager:
            screen_width = self.ui_manager.window_resolution[0]
            screen_height = self.ui_manager.window_resolution[1]

        setup_x = (screen_width - setup_width) // 2
        setup_y = (screen_height - setup_height) // 2

        setup_rect = pygame.Rect(setup_x, setup_y, setup_width, setup_height)

        # Create and show the race setup screen
        # BUG-92: Pass loaded race data so Setup Species edits existing selection
        self.active_race_modal = RaceSetupScreen(
            rect=setup_rect,
            manager=self.ui_manager,
            on_complete_callback=lambda race: self._on_race_created(player_index, race),
            on_cancel_callback=self._on_race_dialog_cancelled,
            race_to_edit=self.player_races[player_index]
        )
        self.race_modal_player_index = player_index

    def _on_race_selected(self, player_index: int, race_config: RaceConfig) -> None:
        """Handle race selection from browser dialog."""
        logger.info(f"Player {player_index + 1} selected race: {race_config.name}")
        self.player_races[player_index] = race_config
        self._update_race_display(player_index)
        self.active_race_modal = None
        self.race_modal_player_index = -1

    def _on_race_created(self, player_index: int, race_config: RaceConfig) -> None:
        """Handle race creation from setup screen."""
        logger.info(f"Player {player_index + 1} created race: {race_config.name}")
        self.player_races[player_index] = race_config
        self._update_race_display(player_index)
        self.active_race_modal = None
        self.race_modal_player_index = -1

    def _on_race_dialog_cancelled(self) -> None:
        """Handle race dialog cancellation."""
        logger.debug("Race dialog cancelled")
        self.active_race_modal = None
        self.race_modal_player_index = -1

    def _on_start_clicked(self) -> None:
        """Handle Start Game button click."""
        save_name = self.save_name_input.get_text().strip()

        # Validate save name
        saves_folder = Paths.SAVES_DIR
        is_valid, error = self.validate_save_name(save_name, saves_folder)

        if not is_valid:
            self.error_label.set_text(error)
            return

        # Collect empire names (from race or manual input)
        empire_names = []
        for i in range(self.player_count):
            if self.player_races[i]:
                # Use race name as empire name
                name = self.player_races[i].name
            else:
                # Use manual input or default
                name = self.empire_name_inputs[i].get_text().strip()
            empire_names.append(name)

        # Build config with race data
        try:
            config = self.build_game_config(
                save_name,
                self.player_count,
                empire_names,
                self.player_races[:self.player_count],
                self.galaxy_type,
                self.system_count
            )
        except ValueError as e:
            self.error_label.set_text(str(e))
            return

        logger.info(f"Starting new game: {save_name} with {self.player_count} players")
        self.on_start_callback(config)
        self.kill()

    def _on_cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        logger.debug("New game setup cancelled")
        self.on_cancel_callback()
        self.kill()

    @staticmethod
    def validate_save_name(name: str, saves_folder: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate a save name.

        Args:
            name: Save name to validate
            saves_folder: Optional path to saves folder for uniqueness check

        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Check for empty
        if not name or not name.strip():
            return False, "Save name cannot be empty"

        name = name.strip()

        # Check for invalid filesystem characters
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, name):
            return False, "Save name contains invalid characters"

        # Check for uniqueness if saves_folder provided
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
    def get_player_count_options() -> List[int]:
        """Get available player count options."""
        return [1, 2, 3, 4]

    @staticmethod
    def build_game_config(save_name: str, player_count: int,
                          empire_names: List[str],
                          race_configs: Optional[List[Optional[RaceConfig]]] = None,
                          galaxy_type: str = "spiral",
                          system_count: int = 50) -> GameConfig:
        """
        Build a GameConfig from setup screen values.

        Args:
            save_name: Name for the save folder
            player_count: Number of players (1-4)
            empire_names: List of empire names (may include empty strings)
            race_configs: Optional list of RaceConfig for each player (None = use defaults)
            galaxy_type: Galaxy layout type (default: "spiral")
            system_count: Number of star systems (25-150, default: 50)

        Returns:
            Configured GameConfig

        Raises:
            ValidationException: If player_count is invalid
        """
        if player_count < 1 or player_count > 4:
            raise ValidationException(
                f"Invalid player count: {player_count}",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"player_count": player_count, "valid_range": "1-4"}
            )

        players = []
        for i in range(player_count):
            race = race_configs[i] if race_configs and i < len(race_configs) else None

            # Get name: race name > manual input > default
            if race and race.name:
                name = race.name
            elif i < len(empire_names) and empire_names[i].strip():
                name = empire_names[i].strip()
            else:
                name = f"Empire {i + 1}"

            # Get theme and color: from race if available, otherwise defaults
            if race and race.theme_id:
                theme = race.theme_id
                logger.debug(f"Player {i} using race theme: {theme}")
            else:
                theme = THEME_DEFAULTS[i][0]
                logger.debug(f"Player {i} using default theme: {theme}")

            color = THEME_DEFAULTS[i][1]  # Color still comes from defaults

            # Get race visual identity
            flag_id = race.flag_id if race else ""
            portrait_id = race.portrait_id if race else ""
            race_id = race.race_id if race else None

            players.append(PlayerConfig(
                name=name,
                theme=theme,
                color=color,
                is_human=True,
                race_id=race_id,
                flag_id=flag_id,
                portrait_id=portrait_id,
                race_config=race
            ))

        return GameConfig(
            save_name=save_name,
            players=players,
            galaxy_type=galaxy_type,
            system_count=system_count
        )
