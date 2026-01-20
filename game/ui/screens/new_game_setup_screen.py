"""
New Game Setup Screen - UI for configuring a new game.

Allows users to:
- Enter a save name
- Select number of players (1-4)
- Name each empire
- Start the game with auto-assigned themes
"""
import os
import re
import pygame
import pygame_gui
from typing import Callable, Optional, Tuple, List

from game.core.logger import log_debug, log_info
from game.strategy.engine.game_config import GameConfig, PlayerConfig, THEME_DEFAULTS


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
        self.empire_name_inputs = []  # List of UITextEntryLine
        self.theme_labels = []  # List of UILabel showing assigned theme

        self._create_ui()

    def _create_ui(self):
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

        # Empire name section header
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, content_width, 25),
            text="Empire Names:",
            manager=self.ui_manager,
            container=container
        )
        y_offset += 30

        # Create empire name inputs (4 max, hide unused)
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
        self.error_label.text_colour = pygame.Color(255, 100, 100)

    def _create_empire_inputs(self):
        """Create empire name input fields for each player slot."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        y_offset = self.empire_inputs_start_y

        # Clear existing
        for inp in self.empire_name_inputs:
            inp.kill()
        for lbl in self.theme_labels:
            lbl.kill()
        self.empire_name_inputs = []
        self.theme_labels = []

        # Create inputs for each potential player
        for i in range(4):
            # Empire number label
            num_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y_offset, 80, 30),
                text=f"Player {i + 1}:",
                manager=self.ui_manager,
                container=container
            )

            # Name input
            name_input = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(90, y_offset, 200, 30),
                manager=self.ui_manager,
                container=container,
                placeholder_text=f"Empire {i + 1}"
            )

            # Theme label (auto-assigned)
            theme_name = THEME_DEFAULTS[i][0]
            theme_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(300, y_offset, 150, 30),
                text=f"({theme_name})",
                manager=self.ui_manager,
                container=container
            )

            self.empire_name_inputs.append(name_input)
            self.theme_labels.append(theme_label)

            # Also store the number label for visibility toggling
            if not hasattr(self, 'num_labels'):
                self.num_labels = []
            if len(self.num_labels) <= i:
                self.num_labels.append(num_label)
            else:
                self.num_labels[i] = num_label

            y_offset += 40

        # Update visibility based on current player count
        self._update_empire_visibility()

    def _update_empire_visibility(self):
        """Show/hide empire inputs based on player count."""
        for i in range(4):
            visible = i < self.player_count
            if visible:
                self.empire_name_inputs[i].show()
                self.theme_labels[i].show()
                if hasattr(self, 'num_labels') and i < len(self.num_labels):
                    self.num_labels[i].show()
            else:
                self.empire_name_inputs[i].hide()
                self.theme_labels[i].hide()
                if hasattr(self, 'num_labels') and i < len(self.num_labels):
                    self.num_labels[i].hide()

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process pygame events."""
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.player_count_dropdown:
                self.player_count = int(event.text)
                self._update_empire_visibility()
                handled = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_start:
                self._on_start_clicked()
                handled = True
            elif event.ui_element == self.btn_cancel:
                self._on_cancel_clicked()
                handled = True

        return handled

    def _on_start_clicked(self):
        """Handle Start Game button click."""
        save_name = self.save_name_input.get_text().strip()

        # Validate save name
        saves_folder = os.path.join(os.getcwd(), "saves")
        is_valid, error = self.validate_save_name(save_name, saves_folder)

        if not is_valid:
            self.error_label.set_text(error)
            return

        # Collect empire names
        empire_names = []
        for i in range(self.player_count):
            name = self.empire_name_inputs[i].get_text().strip()
            empire_names.append(name)

        # Build config
        try:
            config = self.build_game_config(save_name, self.player_count, empire_names)
        except ValueError as e:
            self.error_label.set_text(str(e))
            return

        log_info(f"Starting new game: {save_name} with {self.player_count} players")
        self.on_start_callback(config)
        self.kill()

    def _on_cancel_clicked(self):
        """Handle Cancel button click."""
        log_debug("New game setup cancelled")
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
    def get_player_count_options() -> List[int]:
        """Get available player count options."""
        return [1, 2, 3, 4]

    @staticmethod
    def build_game_config(save_name: str, player_count: int,
                          empire_names: List[str]) -> GameConfig:
        """
        Build a GameConfig from setup screen values.

        Args:
            save_name: Name for the save folder
            player_count: Number of players (1-4)
            empire_names: List of empire names (may include empty strings)

        Returns:
            Configured GameConfig

        Raises:
            ValueError: If player_count is invalid
        """
        if player_count < 1 or player_count > 4:
            raise ValueError(f"Invalid player count: {player_count} (must be 1-4)")

        players = []
        for i in range(player_count):
            # Get name, use default if empty
            name = empire_names[i] if i < len(empire_names) and empire_names[i].strip() else f"Empire {i + 1}"

            # Auto-assign theme and color from THEME_DEFAULTS
            theme = THEME_DEFAULTS[i][0]
            color = THEME_DEFAULTS[i][1]

            players.append(PlayerConfig(
                name=name,
                theme=theme,
                color=color,
                is_human=True  # All players are human in new game
            ))

        return GameConfig(
            save_name=save_name,
            players=players
        )
