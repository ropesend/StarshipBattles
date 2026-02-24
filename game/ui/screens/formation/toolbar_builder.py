"""
Formation Toolbar Builder - Creates toolbar UI for the formation editor.

Extracts toolbar construction from FormationEditorScreen to reduce class complexity.
This builder creates all buttons, sliders, labels, and entry fields for the toolbar.
"""
from dataclasses import dataclass
from typing import Any

import pygame
import pygame_gui


@dataclass
class ToolbarWidgets:
    """
    Container holding references to all toolbar UI elements.

    These references are needed by FormationEditorScreen for event handling
    and state updates.
    """
    # Row 1: Main toolbar buttons
    clear_btn: Any
    snap_btn: Any
    clone_btn: Any
    delete_btn: Any
    save_btn: Any
    load_btn: Any
    rotation_mode_btn: Any
    info_label: Any

    # Row 2: Shape generation and renumber controls
    count_slider: Any
    count_entry: Any
    circle_btn: Any
    disc_btn: Any
    x_btn: Any
    line_btn: Any
    renumber_mode_btn: Any
    renumber_slider: Any
    renumber_entry: Any
    return_btn: Any


class FormationToolbarBuilder:
    """
    Builder for formation editor toolbar UI elements.

    Creates all toolbar widgets and returns a ToolbarWidgets container
    with references to each element for event handling.
    """

    # Layout constants
    BTN_WIDTH = 110
    BTN_HEIGHT = 30
    SPACING = 5
    START_X = 10
    ROT_BTN_WIDTH = 140
    INFO_LABEL_WIDTH = 250
    SHAPE_BTN_WIDTH = 80
    RENUMBER_BTN_WIDTH = 110
    RENUMBER_SLIDER_WIDTH = 100
    RENUMBER_ENTRY_WIDTH = 40
    COUNT_SLIDER_WIDTH = 150
    COUNT_ENTRY_WIDTH = 50
    RETURN_BTN_WIDTH = 110

    def build_toolbar(
        self,
        ui_manager: pygame_gui.UIManager,
        screen_width: int,
        screen_height: int,
        toolbar_height: int = 80
    ) -> ToolbarWidgets:
        """
        Build the complete toolbar UI.

        Args:
            ui_manager: The pygame_gui UIManager to create elements with
            screen_width: Width of the screen for positioning
            screen_height: Height of the screen for positioning
            toolbar_height: Height of the toolbar area (default 80)

        Returns:
            ToolbarWidgets dataclass with references to all created elements
        """
        row1_y = screen_height - 70
        row2_y = row1_y + 35

        # Build both rows
        row1_widgets = self._build_row1(ui_manager, row1_y)
        row2_widgets = self._build_row2(ui_manager, row2_y, screen_width)

        return ToolbarWidgets(
            # Row 1
            clear_btn=row1_widgets['clear_btn'],
            snap_btn=row1_widgets['snap_btn'],
            clone_btn=row1_widgets['clone_btn'],
            delete_btn=row1_widgets['delete_btn'],
            save_btn=row1_widgets['save_btn'],
            load_btn=row1_widgets['load_btn'],
            rotation_mode_btn=row1_widgets['rotation_mode_btn'],
            info_label=row1_widgets['info_label'],
            # Row 2
            count_slider=row2_widgets['count_slider'],
            count_entry=row2_widgets['count_entry'],
            circle_btn=row2_widgets['circle_btn'],
            disc_btn=row2_widgets['disc_btn'],
            x_btn=row2_widgets['x_btn'],
            line_btn=row2_widgets['line_btn'],
            renumber_mode_btn=row2_widgets['renumber_mode_btn'],
            renumber_slider=row2_widgets['renumber_slider'],
            renumber_entry=row2_widgets['renumber_entry'],
            return_btn=row2_widgets['return_btn'],
        )

    def _build_row1(self, ui_manager: pygame_gui.UIManager, btn_y: int) -> dict:
        """Build the first row of toolbar buttons."""
        current_x = self.START_X
        widgets = {}

        # Clear All button
        widgets['clear_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.BTN_WIDTH, self.BTN_HEIGHT),
            text="Clear All",
            manager=ui_manager
        )
        current_x += self.BTN_WIDTH + self.SPACING

        # Snap toggle button
        widgets['snap_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.BTN_WIDTH, self.BTN_HEIGHT),
            text="Snap: ON",
            manager=ui_manager
        )
        current_x += self.BTN_WIDTH + self.SPACING

        # Clone Group button
        widgets['clone_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.BTN_WIDTH, self.BTN_HEIGHT),
            text="Clone Group",
            manager=ui_manager
        )
        current_x += self.BTN_WIDTH + self.SPACING

        # Delete button
        widgets['delete_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.BTN_WIDTH, self.BTN_HEIGHT),
            text="Delete",
            manager=ui_manager
        )
        current_x += self.BTN_WIDTH + self.SPACING

        # Save button
        widgets['save_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.BTN_WIDTH, self.BTN_HEIGHT),
            text="Save",
            manager=ui_manager
        )
        current_x += self.BTN_WIDTH + self.SPACING

        # Load button
        widgets['load_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.BTN_WIDTH, self.BTN_HEIGHT),
            text="Load",
            manager=ui_manager
        )
        current_x += self.BTN_WIDTH + self.SPACING

        # Rotation mode button (wider)
        widgets['rotation_mode_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.ROT_BTN_WIDTH, self.BTN_HEIGHT),
            text="Rot: Relative",
            manager=ui_manager
        )
        current_x += self.ROT_BTN_WIDTH + self.SPACING

        # Info label
        widgets['info_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(current_x, btn_y, self.INFO_LABEL_WIDTH, self.BTN_HEIGHT),
            text="Arrows: 0",
            manager=ui_manager
        )

        return widgets

    def _build_row2(
        self,
        ui_manager: pygame_gui.UIManager,
        btn_y: int,
        screen_width: int
    ) -> dict:
        """Build the second row of toolbar (shape generation and renumber controls)."""
        current_x = self.START_X
        widgets = {}

        # "Shape Gen:" label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(current_x, btn_y, 80, self.BTN_HEIGHT),
            text="Shape Gen:",
            manager=ui_manager
        )
        current_x += 80 + self.SPACING

        # Count slider
        widgets['count_slider'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, btn_y, self.COUNT_SLIDER_WIDTH, self.BTN_HEIGHT),
            start_value=5,
            value_range=(2, 50),
            manager=ui_manager
        )
        current_x += self.COUNT_SLIDER_WIDTH + self.SPACING

        # Count entry
        widgets['count_entry'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(current_x, btn_y, self.COUNT_ENTRY_WIDTH, self.BTN_HEIGHT),
            manager=ui_manager
        )
        widgets['count_entry'].set_text("5")
        current_x += self.COUNT_ENTRY_WIDTH + self.SPACING

        # Circle button
        widgets['circle_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.SHAPE_BTN_WIDTH, self.BTN_HEIGHT),
            text="Circle",
            manager=ui_manager
        )
        current_x += self.SHAPE_BTN_WIDTH + self.SPACING

        # Disc button
        widgets['disc_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.SHAPE_BTN_WIDTH, self.BTN_HEIGHT),
            text="Disc",
            manager=ui_manager
        )
        current_x += self.SHAPE_BTN_WIDTH + self.SPACING

        # X Shape button
        widgets['x_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.SHAPE_BTN_WIDTH, self.BTN_HEIGHT),
            text="X Shape",
            manager=ui_manager
        )
        current_x += self.SHAPE_BTN_WIDTH + self.SPACING

        # Line button
        widgets['line_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.SHAPE_BTN_WIDTH, self.BTN_HEIGHT),
            text="Line",
            manager=ui_manager
        )
        current_x += self.SHAPE_BTN_WIDTH + self.SPACING

        # Renumber mode button
        widgets['renumber_mode_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, self.RENUMBER_BTN_WIDTH, self.BTN_HEIGHT),
            text="Renumber: OFF",
            manager=ui_manager
        )
        current_x += self.RENUMBER_BTN_WIDTH + self.SPACING

        # Renumber slider
        widgets['renumber_slider'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, btn_y, self.RENUMBER_SLIDER_WIDTH, self.BTN_HEIGHT),
            start_value=1,
            value_range=(1, 50),
            manager=ui_manager
        )
        current_x += self.RENUMBER_SLIDER_WIDTH + self.SPACING

        # Renumber entry
        widgets['renumber_entry'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(current_x, btn_y, self.RENUMBER_ENTRY_WIDTH, self.BTN_HEIGHT),
            manager=ui_manager
        )
        widgets['renumber_entry'].set_text("1")

        # Return button (right-aligned)
        widgets['return_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                screen_width - 120,
                btn_y,
                self.RETURN_BTN_WIDTH,
                self.BTN_HEIGHT
            ),
            text="Return",
            manager=ui_manager
        )

        return widgets
