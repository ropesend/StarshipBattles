"""
Save Selection Window - UI for browsing and loading save games.

Supports:
- Listing all saves with metadata
- Expanding a save to show its turn history
- Loading a specific turn from a save
- Deleting saves

PROJ-329B Phase 1: two-stage construction. Cheap state (callbacks,
saves_list, list_item_mapping, selection trackers) lives before the
``UIWindow`` shell; widget construction is behind
``SaveSelectionUiBuilder`` so tests can swap in a Mock under
``bypass_init``. Direct UIWindow subclass — bypass guard inlined per
PROJ-328 Phase B pattern.
"""
from __future__ import annotations

from typing import Optional

import pygame
import pygame_gui
from game.ui.config import UIConfig
import logging

logger = logging.getLogger(__name__)


class SaveSelectionUiBuilder:
    """Production widget builder. Constructs saves_listbox, info_label,
    btn_load, btn_expand, btn_delete, btn_cancel and disables the action
    buttons. Reads ``screen.get_container()`` for layout sizing.
    """

    def build(self, screen: "SaveSelectionWindow") -> None:
        container = screen.get_container()
        content_width = container.get_size()[0] - 20
        content_height = container.get_size()[1] - 110  # Room for buttons and info

        # Save list (scrollable)
        screen.saves_listbox = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(10, 10, content_width, content_height),
            item_list=[],
            manager=screen.ui_manager,
            container=container,
            allow_multi_select=False,
        )

        # Info label showing selected save details
        info_y = content_height + 15
        screen.info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, info_y, content_width, 25),
            text="Select a save to load",
            manager=screen.ui_manager,
            container=container,
        )

        # Button panel at bottom
        button_y = content_height + 45
        button_width = 100

        screen.btn_load = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, button_y, button_width, 40),
            text="Load",
            manager=screen.ui_manager,
            container=container,
        )

        screen.btn_expand = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + button_width + 10, button_y, button_width, 40),
            text="Show Turns",
            manager=screen.ui_manager,
            container=container,
        )

        screen.btn_delete = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + (button_width + 10) * 2, button_y, button_width, 40),
            text="Delete",
            manager=screen.ui_manager,
            container=container,
        )

        screen.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - button_width + 10, button_y, button_width, 40),
            text="Cancel",
            manager=screen.ui_manager,
            container=container,
        )

        # Disable action buttons initially
        screen.btn_load.disable()
        screen.btn_expand.disable()
        screen.btn_delete.disable()


class SaveSelectionWindow(pygame_gui.elements.UIWindow):
    """Window for selecting a save game to load."""

    def __init__(
        self,
        rect,
        manager,
        on_load_callback,
        on_cancel_callback,
        *,
        ui_builder: Optional[SaveSelectionUiBuilder] = None,
    ):
        """
        Create save selection window.

        Args:
            rect: Window rectangle
            manager: pygame_gui UIManager
            on_load_callback: Callback(save_path, turn_number=None) when user selects a save
            on_cancel_callback: Callback() when user cancels
            ui_builder: Optional UI builder override (test seam).
        """
        # ---- Stage 1: cheap state ----
        self.on_load_callback = on_load_callback
        self.on_cancel_callback = on_cancel_callback

        # List of saves with metadata
        self.saves_list = []
        self.selected_save = None
        self.selected_turn = None  # None means latest turn
        self.expanded_save_idx = None  # Index of expanded save showing turns

        # Track list items for mapping back to saves/turns
        self.list_item_mapping = []  # tuples: ('save', save_idx) or ('turn', save_idx, turn_num)

        # PROJ-347 T4.3 (Pattern §33 widget-ref placeholders): set widget
        # slots populated by the production builder to None up front, so a
        # NullSaveSelectionWindowUiBuilder test can safely call
        # ``process_event()`` without AttributeError on
        # ``self.btn_load``/``self.saves_listbox``/etc. The production
        # builder overwrites these in Stage 3.
        self.saves_listbox = None
        self.info_label = None
        self.btn_load = None
        self.btn_expand = None
        self.btn_delete = None
        self.btn_cancel = None

        # ---- Stage 2: UIWindow shell (skipped under bypass_init) ----
        # PROJ-324 / PROJ-328 / PROJ-329B test escape hatch.
        if getattr(type(self), 'bypass_init', False):
            self.ui_manager = manager
            self._window_init_bypassed = True
            # NOTE: do not assign ``self.rect`` (GUISprite descriptor).
            if ui_builder is not None:
                ui_builder.build(self)
            return

        super().__init__(
            rect,
            manager,
            window_display_title="Load Game",
            object_id="#save_selection_window",
            resizable=True,
        )

        # ---- Stage 3: widgets + initial save load ----
        (ui_builder or SaveSelectionUiBuilder()).build(self)
        self._load_saves()

    def _load_saves(self) -> None:
        """Load list of available saves from SaveGameService."""
        from game.strategy.systems.save_game_service import SaveGameService

        saves = SaveGameService.list_saves()

        if not saves:
            self.saves_listbox.set_item_list(["No save games found"])
            self.list_item_mapping = []
            return

        # Store saves
        self.saves_list = saves
        self._refresh_list_display()

    def _refresh_list_display(self) -> None:
        """Refresh the list display based on current state."""
        from game.strategy.systems.save_game_service import SaveGameService

        save_items = []
        self.list_item_mapping = []

        for idx, save in enumerate(self.saves_list):
            # Format main save entry
            save_name = save.get('save_name', 'Unknown')
            player_name = save.get('player_name', 'Unknown')
            latest_turn = save.get('latest_turn_number', save.get('turn_number', 0))
            empire_count = save.get('empire_count', 1)
            timestamp = save.get('timestamp', '')

            # Format timestamp for display
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except ValueError as e:
                logger.warning(f"Failed to parse save timestamp '{timestamp}': {e}")
                time_str = timestamp[:16] if len(timestamp) >= 16 else timestamp

            # Show empire count if > 1
            empire_info = f" ({empire_count}P)" if empire_count > 1 else ""

            entry = f"{save_name}{empire_info} - Turn {latest_turn} ({time_str})"
            save_items.append(entry)
            self.list_item_mapping.append(('save', idx))

            # If this save is expanded, show its turns
            if self.expanded_save_idx == idx:
                save_path = save.get('save_path')
                turns = SaveGameService.list_turns(save_path)

                for turn_info in turns:
                    turn_num = turn_info['turn_number']
                    turn_time = turn_info.get('timestamp', '')

                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(turn_time)
                        turn_time_str = dt.strftime("%m-%d %H:%M")
                    except ValueError as e:
                        logger.warning(f"Failed to parse turn timestamp '{turn_time}': {e}")
                        turn_time_str = ""

                    # Indent turn entries
                    turn_entry = f"    Turn {turn_num} ({turn_time_str})"
                    save_items.append(turn_entry)
                    self.list_item_mapping.append(('turn', idx, turn_num))

        self.saves_listbox.set_item_list(save_items)

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process pygame events."""
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.saves_listbox:
                self._handle_selection_change()
                handled = True

        elif event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if event.ui_element == self.saves_listbox:
                # Double-click loads immediately
                self._on_load_clicked()
                handled = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_load:
                self._on_load_clicked()
                handled = True
            elif event.ui_element == self.btn_expand:
                self._on_expand_clicked()
                handled = True
            elif event.ui_element == self.btn_delete:
                self._on_delete_clicked()
                handled = True
            elif event.ui_element == self.btn_cancel:
                self._on_cancel_clicked()
                handled = True

        return handled

    def _handle_selection_change(self) -> None:
        """Handle selection change in list."""
        selected_item = self.saves_listbox.get_single_selection()

        if selected_item is None:
            self.selected_save = None
            self.selected_turn = None
            self.btn_load.disable()
            self.btn_expand.disable()
            self.btn_delete.disable()
            self.info_label.set_text("Select a save to load")
            return

        # Find selection in mapping by matching text
        # UISelectionList.item_list returns dicts with "text", "selected", etc.
        items = self.saves_listbox.item_list
        selected_idx = None
        for i, item in enumerate(items):
            item_text = item["text"] if isinstance(item, dict) else str(item)

            if item_text == selected_item and i < len(self.list_item_mapping):
                selected_idx = i
                break

        if selected_idx is None:
            return

        mapping = self.list_item_mapping[selected_idx]

        if mapping[0] == 'save':
            # Selected a save (not a turn)
            save_idx = mapping[1]
            self.selected_save = self.saves_list[save_idx]
            self.selected_turn = None  # Will load latest

            # Update buttons
            self.btn_load.enable()
            self.btn_expand.enable()
            self.btn_delete.enable()

            # Update expand button text
            if self.expanded_save_idx == save_idx:
                self.btn_expand.set_text("Hide Turns")
            else:
                self.btn_expand.set_text("Show Turns")

            # Update info
            save_name = self.selected_save.get('save_name', 'Unknown')
            latest_turn = self.selected_save.get('latest_turn_number', self.selected_save.get('turn_number', 0))
            empire_names = self.selected_save.get('empire_names', [])
            empires_str = ", ".join(empire_names[:3])
            if len(empire_names) > 3:
                empires_str += "..."

            self.info_label.set_text(f"{save_name}: {empires_str} - Latest: Turn {latest_turn}")
            logger.debug(f"Selected save: {save_name}")

        elif mapping[0] == 'turn':
            # Selected a specific turn
            save_idx = mapping[1]
            turn_num = mapping[2]

            self.selected_save = self.saves_list[save_idx]
            self.selected_turn = turn_num

            # Update buttons
            self.btn_load.enable()
            self.btn_expand.disable()  # Can't expand from turn selection
            self.btn_delete.disable()  # Don't allow deleting individual turns

            # Update info
            save_name = self.selected_save.get('save_name', 'Unknown')
            self.info_label.set_text(f"Load {save_name} at Turn {turn_num}")
            logger.debug(f"Selected turn {turn_num} from {save_name}")

    def _on_load_clicked(self) -> None:
        """Handle Load button click."""
        if not self.selected_save:
            return

        save_path = self.selected_save.get('save_path')
        logger.info(f"Loading game from: {save_path}, turn: {self.selected_turn}")

        # Call with optional turn number
        self.on_load_callback(save_path, self.selected_turn)
        self.kill()

    def _on_expand_clicked(self) -> None:
        """Toggle turn list expansion for selected save."""
        if not self.selected_save:
            return

        # Find index of selected save
        save_idx = None
        for i, save in enumerate(self.saves_list):
            if save == self.selected_save:
                save_idx = i
                break

        if save_idx is None:
            return

        # Toggle expansion
        if self.expanded_save_idx == save_idx:
            self.expanded_save_idx = None
            self.btn_expand.set_text("Show Turns")
        else:
            self.expanded_save_idx = save_idx
            self.btn_expand.set_text("Hide Turns")

        self._refresh_list_display()

    def _on_delete_clicked(self) -> None:
        """Handle Delete button click."""
        if not self.selected_save:
            return

        save_name = self.selected_save.get('save_name', 'Unknown')

        # Show confirmation dialog
        confirm_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
        confirm_rect.center = (self.rect.centerx, self.rect.centery)

        pygame_gui.windows.UIConfirmationDialog(
            rect=confirm_rect,
            action_long_desc=f"Are you sure you want to delete '{save_name}'?<br>This will delete all turns. This action cannot be undone.",
            manager=self.ui_manager,
            action_short_name="delete_save",
            window_title="Delete Save Game"
        )

    def _on_cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        logger.debug("Load game cancelled")
        self.on_cancel_callback()
        self.kill()

    def _handle_delete_confirmation(self) -> None:
        """Actually delete the selected save."""
        from game.strategy.systems.save_game_service import SaveGameService

        if not self.selected_save:
            return

        save_path = self.selected_save.get('save_path')
        save_name = self.selected_save.get('save_name', 'Unknown')

        success, message = SaveGameService.delete_save(save_path)

        if success:
            logger.info(f"Deleted save: {save_name}")
            # Reload saves list
            self.expanded_save_idx = None
            self._load_saves()
            self.selected_save = None
            self.selected_turn = None
            self.btn_load.disable()
            self.btn_expand.disable()
            self.btn_delete.disable()
            self.info_label.set_text("Select a save to load")
        else:
            logger.debug(f"Failed to delete save: {message}")

            # Show error dialog
            error_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
            error_rect.center = (self.rect.centerx, self.rect.centery)
            pygame_gui.windows.UIMessageWindow(
                rect=error_rect,
                html_message=f"<b>Delete Failed</b><br><br>{message}",
                manager=self.ui_manager,
                window_title="Error"
            )

    def update(self, time_delta) -> None:
        """Update window."""
        super().update(time_delta)

        # Check for confirmation dialog events
        for event in pygame.event.get(pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED):
            if event.ui_element.action_short_name == "delete_save":
                self._handle_delete_confirmation()
