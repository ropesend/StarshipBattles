import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UISelectionList, UIButton, UILabel, UITextBox

from game.core.logger import log_debug

class PlanetSelectionWindow(UIWindow):
    def __init__(self, rect, manager, planets, on_selection_callback, formatter_callback):
        # Enforce minimum size if rect is too small
        if rect.width < 700: rect.width = 700
        if rect.height < 400: rect.height = 400
        
        super().__init__(rect, manager, window_display_title="Select Planet to Colonize")
        self.planets = planets
        self.callback = on_selection_callback
        self.formatter = formatter_callback
        self.current_selection_name = None
        
        # Left Side: List
        list_width = 300
        
        self.label = UILabel(
             pygame.Rect(10, 10, list_width, 30),
             "Habitable bodies:",
             self.ui_manager,
             container=self
        )
        
        self.selection_list = UISelectionList(
            pygame.Rect(10, 45, list_width, rect.height - 120),
            item_list=[p.name for p in planets],
            manager=self.ui_manager,
            container=self
        )
        
        # Right Side: Details
        details_x = list_width + 20
        details_w = rect.width - list_width - 30
        
        self.lbl_details = UILabel(
             pygame.Rect(details_x, 10, details_w, 30),
             "Planet Report",
             self.ui_manager,
             container=self
        )
        
        self.details_text = UITextBox(
            html_text="Select a planet to view details.",
            relative_rect=pygame.Rect(details_x, 45, details_w, rect.height - 120),
            manager=self.ui_manager,
            container=self
        )
        
        self.btn_select = UIButton(
            pygame.Rect(10, rect.height - 60, 120, 30),
            "Confirm",
            self.ui_manager,
            container=self
        )
        
        self.btn_any = UIButton(
            pygame.Rect(rect.width - 140, rect.height - 60, 130, 30),
            "Any Planet",
            self.ui_manager,
            container=self
        )
        
    def update(self, time_delta):
        super().update(time_delta)
        
        # Check for selection change
        selected_name = self.selection_list.get_single_selection()
        if selected_name != self.current_selection_name:
            self.current_selection_name = selected_name
            if selected_name:
                 planet = next((p for p in self.planets if p.name == selected_name), None)
                 if planet:
                     html = self.formatter(planet)
                     self.details_text.html_text = html
                     self.details_text.rebuild()
            else:
                 self.details_text.html_text = "Select a planet to view details."
                 self.details_text.rebuild()
        
        if self.btn_select.check_pressed():
            selected_name = self.selection_list.get_single_selection()
            log_debug(f"PlanetSelectionWindow: Confirm Pressed. Selection: {selected_name}")
            if selected_name:
                # Find planet
                choice = next((p for p in self.planets if p.name == selected_name), None)
                if choice:
                     log_debug(f"PlanetSelectionWindow: Calling callback with {choice.name}")
                     self.callback(choice)
                     self.kill()
            else:
                log_debug("PlanetSelectionWindow: No selection made.")

        if self.btn_any.check_pressed():
            # "Any Planet" -> Return None to defer selection to arrival
            self.callback(None)
            self.kill()
