import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UISelectionList, UIButton, UILabel

from game.assets.asset_manager import AssetManager
from game.core.logger import log_debug
from game.ui.panels.planet_report_panel import PlanetReportPanel

class PlanetSelectionWindow(UIWindow):
    def __init__(self, rect, manager, planets, on_selection_callback):
        # Enforce minimum size for full planet report display
        if rect.width < 950: rect.width = 950
        if rect.height < 650: rect.height = 650

        super().__init__(rect, manager, window_display_title="Select Planet to Colonize")
        self.planets = planets
        self.callback = on_selection_callback
        self.current_selection_name = None

        # Planet detail panel (PROJ-54)
        self.planet_detail_panel = None  # Created when planet selected
        self.selected_planet = None      # Track current selection
        
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

        # Planet detail panel will be created dynamically on selection (PROJ-54)
        # Details area dimensions: x=details_x (320), y=45, width=details_w, height=rect.height-120
        
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

        # Check for selection change (PROJ-54)
        selected_name = self.selection_list.get_single_selection()
        if selected_name != self.current_selection_name:
            self.current_selection_name = selected_name

            # Find planet object
            planet = None
            if selected_name:
                planet = next((p for p in self.planets if p.name == selected_name), None)

            # Check if actual planet object changed
            if planet != self.selected_planet:
                # Kill old panel if exists
                if self.planet_detail_panel:
                    self.planet_detail_panel.kill()
                    self.planet_detail_panel = None

                if planet:
                    # Create planet report panel
                    list_width = 300
                    details_x = list_width + 20
                    details_y = 45
                    details_width = self.rect.width - list_width - 30
                    # Leave room for buttons at bottom (buttons at rect.height - 60, so stop at -80)
                    details_height = self.rect.height - 130

                    # Load planet portrait image
                    portrait_surface = None
                    if hasattr(planet, 'image_id') and planet.image_id:
                        am = AssetManager.instance()
                        portrait_surface = am.load_planet_image(planet.image_id, requested_size=512)
                        # Apply rotation if specified
                        if portrait_surface and hasattr(planet, 'image_rotation') and planet.image_rotation:
                            portrait_surface = pygame.transform.rotate(portrait_surface, planet.image_rotation)

                    self.planet_detail_panel = PlanetReportPanel(
                        manager=self.ui_manager,
                        rect=pygame.Rect(details_x, details_y, details_width, details_height),
                        planet=planet,
                        container=self,
                        portrait_surface=portrait_surface,
                        show_complexes=False    # Match strategy UI - no separate complexes column
                    )

                self.selected_planet = planet
        
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

    def kill(self):
        """Clean up resources when window is closed. (PROJ-54)"""
        # Clean up planet detail panel
        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        # Call parent cleanup
        super().kill()
