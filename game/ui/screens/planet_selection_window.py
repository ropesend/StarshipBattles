import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UISelectionList, UIButton, UILabel

class PlanetSelectionWindow(UIWindow):
    def __init__(self, rect, manager, planets, on_selection_callback):
        super().__init__(rect, manager, window_display_title="Select Planet to Colonize")
        self.planets = planets
        self.callback = on_selection_callback
        
        self.label = UILabel(
             pygame.Rect(10, 10, rect.width - 20, 30),
             "Multiple habitable bodies detected:",
             self.ui_manager,
             container=self
        )
        
        self.selection_list = UISelectionList(
            pygame.Rect(10, 45, rect.width - 20, rect.height - 100),
            item_list=[p.name for p in planets],
            manager=self.ui_manager,
            container=self
        )
        
        self.btn_select = UIButton(
            pygame.Rect((rect.width - 120 )/ 2, rect.height - 45, 120, 30),
            "Confirm",
            self.ui_manager,
            container=self
        )
        
    def update(self, time_delta):
        super().update(time_delta)
        
        if self.btn_select.check_pressed():
            selected_name = self.selection_list.get_single_selection()
            if selected_name:
                # Find planet
                choice = next((p for p in self.planets if p.name == selected_name), None)
                if choice:
                     self.callback(choice)
                     self.kill()
