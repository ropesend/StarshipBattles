"""
Save Selection Window - UI for browsing and loading save games.
"""
import pygame
import pygame_gui
from game.core.logger import log_debug, log_info


class SaveSelectionWindow(pygame_gui.elements.UIWindow):
    """Window for selecting a save game to load."""

    def __init__(self, rect, manager, on_load_callback, on_cancel_callback):
        """
        Create save selection window.

        Args:
            rect: Window rectangle
            manager: pygame_gui UIManager
            on_load_callback: Callback(save_path) when user selects a save
            on_cancel_callback: Callback() when user cancels
        """
        super().__init__(
            rect,
            manager,
            window_display_title="Load Game",
            object_id="#save_selection_window",
            resizable=True
        )

        self.on_load_callback = on_load_callback
        self.on_cancel_callback = on_cancel_callback

        # List of saves with metadata
        self.saves_list = []
        self.selected_save = None

        # Create UI elements
        self._create_ui()
        self._load_saves()

    def _create_ui(self):
        """Create UI elements."""
        # Calculate layout
        content_width = self.get_container().get_size()[0] - 20
        content_height = self.get_container().get_size()[1] - 70

        # Save list (scrollable)
        self.saves_listbox = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(10, 10, content_width, content_height),
            item_list=[],
            manager=self.ui_manager,
            container=self.get_container(),
            allow_multi_select=False
        )

        # Button panel at bottom
        button_y = content_height + 20
        button_width = 120

        self.btn_load = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, button_y, button_width, 40),
            text="Load",
            manager=self.ui_manager,
            container=self.get_container()
        )

        self.btn_delete = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + button_width + 10, button_y, button_width, 40),
            text="Delete",
            manager=self.ui_manager,
            container=self.get_container()
        )

        self.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - button_width, button_y, button_width, 40),
            text="Cancel",
            manager=self.ui_manager,
            container=self.get_container()
        )

        # Disable load/delete initially
        self.btn_load.disable()
        self.btn_delete.disable()

    def _load_saves(self):
        """Load list of available saves from SaveGameService."""
        from game.strategy.systems.save_game_service import SaveGameService

        saves = SaveGameService.list_saves()

        if not saves:
            self.saves_listbox.set_item_list(["No save games found"])
            return

        # Format save entries
        self.saves_list = saves
        save_items = []

        for save in saves:
            player_name = save.get('player_name', 'Unknown')
            turn = save.get('turn_number', 0)
            timestamp = save.get('timestamp', '')

            # Format timestamp for display
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = timestamp[:16] if len(timestamp) >= 16 else timestamp

            entry = f"{player_name} - Turn {turn} ({time_str})"
            save_items.append(entry)

        self.saves_listbox.set_item_list(save_items)

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process pygame events."""
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.saves_listbox:
                # Enable load/delete buttons when selection made
                selected_item = self.saves_listbox.get_single_selection()

                # get_single_selection() returns the selected string, not the index
                # We need to find the index in the list
                if selected_item is not None:
                    try:
                        # Find the save that matches the selected item text
                        for idx, save in enumerate(self.saves_list):
                            player_name = save.get('player_name', 'Unknown')
                            turn = save.get('turn_number', 0)
                            timestamp = save.get('timestamp', '')

                            # Format timestamp for display
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(timestamp)
                                time_str = dt.strftime("%Y-%m-%d %H:%M")
                            except:
                                time_str = timestamp[:16] if len(timestamp) >= 16 else timestamp

                            entry = f"{player_name} - Turn {turn} ({time_str})"

                            if entry == selected_item:
                                self.selected_save = save
                                self.btn_load.enable()
                                self.btn_delete.enable()
                                log_debug(f"Selected save: {save.get('save_name')}")
                                break
                    except Exception as e:
                        log_debug(f"Error processing selection: {e}")
                handled = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_load:
                self._on_load_clicked()
                handled = True
            elif event.ui_element == self.btn_delete:
                self._on_delete_clicked()
                handled = True
            elif event.ui_element == self.btn_cancel:
                self._on_cancel_clicked()
                handled = True

        return handled

    def _on_load_clicked(self):
        """Handle Load button click."""
        if self.selected_save:
            save_path = self.selected_save.get('save_path')
            log_info(f"Loading game from: {save_path}")
            self.on_load_callback(save_path)
            self.kill()

    def _on_delete_clicked(self):
        """Handle Delete button click."""
        if not self.selected_save:
            return

        save_name = self.selected_save.get('save_name', 'Unknown')

        # Show confirmation dialog
        confirm_rect = pygame.Rect(0, 0, 400, 200)
        confirm_rect.center = (self.rect.centerx, self.rect.centery)

        pygame_gui.windows.UIConfirmationDialog(
            rect=confirm_rect,
            action_long_desc=f"Are you sure you want to delete '{save_name}'?<br>This action cannot be undone.",
            manager=self.ui_manager,
            action_short_name="delete_save",
            window_title="Delete Save Game"
        )

    def _on_cancel_clicked(self):
        """Handle Cancel button click."""
        log_debug("Load game cancelled")
        self.on_cancel_callback()
        self.kill()

    def _handle_delete_confirmation(self):
        """Actually delete the selected save."""
        from game.strategy.systems.save_game_service import SaveGameService

        if not self.selected_save:
            return

        save_path = self.selected_save.get('save_path')
        save_name = self.selected_save.get('save_name', 'Unknown')

        success, message = SaveGameService.delete_save(save_path)

        if success:
            log_info(f"Deleted save: {save_name}")
            # Reload saves list
            self._load_saves()
            self.selected_save = None
            self.btn_load.disable()
            self.btn_delete.disable()
        else:
            log_debug(f"Failed to delete save: {message}")

            # Show error dialog
            error_rect = pygame.Rect(0, 0, 400, 200)
            error_rect.center = (self.rect.centerx, self.rect.centery)
            pygame_gui.windows.UIMessageWindow(
                rect=error_rect,
                html_message=f"<b>Delete Failed</b><br><br>{message}",
                manager=self.ui_manager,
                window_title="Error"
            )

    def update(self, time_delta):
        """Update window."""
        super().update(time_delta)

        # Check for confirmation dialog events
        for event in pygame.event.get(pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED):
            if event.ui_element.action_short_name == "delete_save":
                self._handle_delete_confirmation()
