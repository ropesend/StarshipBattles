"""Fleet-based battle setup screen.

Replaces the old simple BattleSetupScreen with full fleet organization:
- Multiple fleets per side, each with TaskForce/Squadron hierarchy
- System-scope and sector-scope complex effects
- Design library browser for adding ships
- Save/load setup and individual fleets

IScene protocol: handle_event(), update(dt), draw(screen), handle_resize(w, h)
"""

import logging
import os
import json

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UIDropDownMenu, UITextEntryLine
from pygame_gui.windows import UIConfirmationDialog

from game.core.paths import Paths
from game.core.json_utils import load_json, save_json
from game.ui.colors import BG_PANEL_DARK, TEAM_1_TEXT, TEAM_2_TEXT
from game.ui.fonts import get_default_font
from game.ui.screens.battle_setup_state import BattleSetupState

logger = logging.getLogger(__name__)


class FleetBattleSetupScreen:
    """Fleet-based battle setup screen.

    Three-panel layout:
    - Left: Side selector, fleet list, complex toggles
    - Center: Active fleet ship list
    - Right: Design library browser
    - Bottom: Action buttons
    """

    def __init__(self, width: int, height: int, scene_callback=None):
        self.screen_width = width
        self.screen_height = height
        self.scene_callback = scene_callback

        self.state = BattleSetupState()
        self.active_side = 0  # 0 or 1
        self.active_fleet_index = 0  # Index into active side's fleet list
        self.available_designs = []  # Loaded design dicts

        self._ui_manager = None
        self._panels_built = False

    # === IScene Protocol ===

    def handle_event(self, event):
        """Handle pygame events."""
        if self._ui_manager:
            self._ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button(event)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            self._handle_dropdown(event)

    def update(self, dt: float):
        """Update UI manager."""
        if self._ui_manager:
            self._ui_manager.update(dt)

    def draw(self, screen):
        """Draw the screen."""
        screen.fill((20, 25, 35))
        if self._ui_manager:
            self._ui_manager.draw_ui(screen)

    def handle_resize(self, width: int, height: int):
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height
        if self._ui_manager:
            self._ui_manager.set_window_resolution((width, height))
        self._rebuild_ui()

    # === Lifecycle ===

    def start(self, preserve_teams=False):
        """Initialize or reset the setup screen."""
        if not preserve_teams:
            self.state.clear()
            # Create default fleets
            self.state.side_0.create_fleet("Fleet Alpha")
            self.state.side_1.create_fleet("Fleet Beta")
            self.active_side = 0
            self.active_fleet_index = 0

        self._scan_designs()
        self._rebuild_ui()

    # === Design Library ===

    def _scan_designs(self):
        """Scan for available ship designs."""
        self.available_designs = []
        designs_dir = Paths.STARTER_DESIGNS_DIR

        if not os.path.exists(designs_dir):
            return

        for filename in sorted(os.listdir(designs_dir)):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(designs_dir, filename)
            try:
                data = load_json(filepath, default=None)
                if data and data.get('vehicle_type') == 'Ship':
                    data['_filepath'] = filepath
                    data['_design_id'] = filename.replace('.json', '')
                    self.available_designs.append(data)
            except Exception as e:
                logger.warning(f"Failed to load design {filename}: {e}")

    # === UI Construction ===

    def _rebuild_ui(self):
        """Rebuild all UI elements."""
        if self._ui_manager:
            self._ui_manager.clear_and_reset()

        self._ui_manager = pygame_gui.UIManager(
            (self.screen_width, self.screen_height)
        )

        w = self.screen_width
        h = self.screen_height
        left_w = 220
        right_w = 280
        center_w = w - left_w - right_w
        bottom_h = 60

        # Left panel — side selector + fleet list
        self._build_left_panel(left_w, h - bottom_h)

        # Center panel — active fleet ships
        self._build_center_panel(left_w, center_w, h - bottom_h)

        # Right panel — design library
        self._build_right_panel(left_w + center_w, right_w, h - bottom_h)

        # Bottom bar — action buttons
        self._build_bottom_bar(w, h, bottom_h)

        self._panels_built = True

    def _build_left_panel(self, width, height):
        """Build the left panel with side selector and fleet list."""
        panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, width, height),
            manager=self._ui_manager,
            object_id='#left_panel'
        )

        y = 10
        UILabel(pygame.Rect(10, y, width - 20, 30), "Battle Setup",
                manager=self._ui_manager, container=panel)
        y += 40

        # Side selector
        UILabel(pygame.Rect(10, y, 50, 25), "Side:",
                manager=self._ui_manager, container=panel)
        self._side_dropdown = UIDropDownMenu(
            ["Side 0 (Left)", "Side 1 (Right)"],
            f"Side {self.active_side} ({'Left' if self.active_side == 0 else 'Right'})",
            pygame.Rect(60, y, width - 70, 30),
            manager=self._ui_manager, container=panel
        )
        y += 40

        # Fleet list header
        UILabel(pygame.Rect(10, y, width - 20, 25), "Fleets:",
                manager=self._ui_manager, container=panel)
        y += 30

        # Fleet buttons
        side = self.state.get_side(self.active_side)
        self._fleet_buttons = []
        for i, fleet in enumerate(side.fleets):
            name = getattr(fleet, '_battle_setup_name', f"Fleet {fleet.id}")
            ship_count = len(fleet.ships)
            btn_text = f"{name} ({ship_count})"

            btn = UIButton(
                pygame.Rect(10, y, width - 20, 30),
                btn_text,
                manager=self._ui_manager, container=panel,
                object_id='#fleet_btn_active' if i == self.active_fleet_index else '#fleet_btn'
            )
            btn._fleet_index = i
            self._fleet_buttons.append(btn)
            y += 35

        # Add/remove fleet buttons
        y += 10
        self._add_fleet_btn = UIButton(
            pygame.Rect(10, y, (width - 30) // 2, 30),
            "Add Fleet",
            manager=self._ui_manager, container=panel
        )
        self._remove_fleet_btn = UIButton(
            pygame.Rect(10 + (width - 30) // 2 + 10, y, (width - 30) // 2, 30),
            "Remove Fleet",
            manager=self._ui_manager, container=panel
        )

    def _build_center_panel(self, x, width, height):
        """Build the center panel showing active fleet's ships."""
        panel = UIPanel(
            relative_rect=pygame.Rect(x, 0, width, height),
            manager=self._ui_manager,
            object_id='#center_panel'
        )

        y = 10
        side = self.state.get_side(self.active_side)
        fleet = side.fleets[self.active_fleet_index] if self.active_fleet_index < len(side.fleets) else None

        fleet_name = getattr(fleet, '_battle_setup_name', "No Fleet") if fleet else "No Fleet"
        UILabel(pygame.Rect(10, y, width - 20, 30), f"Fleet: {fleet_name}",
                manager=self._ui_manager, container=panel)
        y += 40

        if fleet:
            # Ship list
            UILabel(pygame.Rect(10, y, width - 20, 25), f"Ships ({len(fleet.ships)}):",
                    manager=self._ui_manager, container=panel)
            y += 30

            self._ship_buttons = []
            for i, ship in enumerate(fleet.ships):
                hull = ship.design_data.get('ship_class', '?')
                btn = UIButton(
                    pygame.Rect(10, y, width - 80, 28),
                    f"{ship.name} ({hull})",
                    manager=self._ui_manager, container=panel
                )
                btn._ship_index = i

                remove_btn = UIButton(
                    pygame.Rect(width - 65, y, 55, 28),
                    "Remove",
                    manager=self._ui_manager, container=panel
                )
                remove_btn._remove_ship_index = i

                self._ship_buttons.append((btn, remove_btn))
                y += 32

    def _build_right_panel(self, x, width, height):
        """Build the right panel with design library."""
        panel = UIPanel(
            relative_rect=pygame.Rect(x, 0, width, height),
            manager=self._ui_manager,
            object_id='#right_panel'
        )

        y = 10
        UILabel(pygame.Rect(10, y, width - 20, 30), "Available Designs",
                manager=self._ui_manager, container=panel)
        y += 40

        self._design_buttons = []
        for i, design in enumerate(self.available_designs):
            name = design.get('name', '?')
            ship_class = design.get('ship_class', '')
            btn = UIButton(
                pygame.Rect(10, y, width - 20, 30),
                f"{name} ({ship_class})",
                manager=self._ui_manager, container=panel
            )
            btn._design_index = i
            self._design_buttons.append(btn)
            y += 35

    def _build_bottom_bar(self, width, height, bar_height):
        """Build the bottom action bar."""
        panel = UIPanel(
            relative_rect=pygame.Rect(0, height - bar_height, width, bar_height),
            manager=self._ui_manager,
            object_id='#bottom_bar'
        )

        btn_w = 150
        spacing = 20
        total = 4 * btn_w + 3 * spacing
        x = (width - total) // 2

        self._start_btn = UIButton(
            pygame.Rect(x, 10, btn_w, 40),
            "Start Battle",
            manager=self._ui_manager, container=panel
        )
        x += btn_w + spacing

        self._headless_btn = UIButton(
            pygame.Rect(x, 10, btn_w, 40),
            "Start Headless",
            manager=self._ui_manager, container=panel
        )
        x += btn_w + spacing

        self._save_btn = UIButton(
            pygame.Rect(x, 10, btn_w, 40),
            "Save Setup",
            manager=self._ui_manager, container=panel
        )
        x += btn_w + spacing

        self._return_btn = UIButton(
            pygame.Rect(x, 10, btn_w, 40),
            "Return to Menu",
            manager=self._ui_manager, container=panel
        )

    # === Event Handlers ===

    def _handle_button(self, event):
        """Handle button press events."""
        element = event.ui_element

        # Fleet selection buttons
        if hasattr(element, '_fleet_index'):
            self.active_fleet_index = element._fleet_index
            self._rebuild_ui()
            return

        # Design buttons — add ship to active fleet
        if hasattr(element, '_design_index'):
            self._add_ship_from_design(element._design_index)
            return

        # Remove ship button
        if hasattr(element, '_remove_ship_index'):
            self._remove_ship(element._remove_ship_index)
            return

        # Action buttons
        if element == self._start_btn:
            self._start_battle(headless=False)
        elif element == self._headless_btn:
            self._start_battle(headless=True)
        elif element == self._save_btn:
            self._save_setup()
        elif element == self._return_btn:
            if self.scene_callback:
                self.scene_callback("return_to_menu")
        elif element == self._add_fleet_btn:
            side = self.state.get_side(self.active_side)
            side.create_fleet(f"Fleet {len(side.fleets) + 1}")
            self._rebuild_ui()
        elif element == self._remove_fleet_btn:
            side = self.state.get_side(self.active_side)
            if len(side.fleets) > 1 and self.active_fleet_index < len(side.fleets):
                side.fleets.pop(self.active_fleet_index)
                self.active_fleet_index = min(self.active_fleet_index, len(side.fleets) - 1)
                self._rebuild_ui()

    def _handle_dropdown(self, event):
        """Handle dropdown changes."""
        if event.ui_element == self._side_dropdown:
            text = event.text
            self.active_side = 1 if "1" in text else 0
            self.active_fleet_index = 0
            self._rebuild_ui()

    # === Ship Management ===

    def _add_ship_from_design(self, design_index: int):
        """Add a ship to the active fleet from a design."""
        if design_index >= len(self.available_designs):
            return

        side = self.state.get_side(self.active_side)
        if self.active_fleet_index >= len(side.fleets):
            return

        fleet = side.fleets[self.active_fleet_index]
        design_data = self.available_designs[design_index]

        # Get registries for ShipInstance creation
        try:
            from game.core.registry import get_default_registry_provider, GameRegistries
            provider = get_default_registry_provider()
            registries = GameRegistries(
                components=provider.get_components(),
                modifiers=provider.get_modifiers(),
                vehicle_classes=provider.get_vehicle_classes(),
                resources=provider.get_resources(),
                resource_catalog=provider.get_resource_catalog(),
            )
        except Exception:
            registries = None

        self.state.add_ship_from_design(fleet, design_data, registries=registries)
        self._rebuild_ui()

    def _remove_ship(self, ship_index: int):
        """Remove a ship from the active fleet."""
        side = self.state.get_side(self.active_side)
        if self.active_fleet_index >= len(side.fleets):
            return

        fleet = side.fleets[self.active_fleet_index]
        if ship_index < len(fleet.ships):
            ship = fleet.ships[ship_index]
            fleet.remove_ship(ship)
            self._rebuild_ui()

    # === Battle Start ===

    def _start_battle(self, headless: bool = False):
        """Convert setup state to battle ships and start battle."""
        try:
            from game.core.registry import get_default_registry_provider, GameRegistries
            provider = get_default_registry_provider()
            registries = GameRegistries(
                components=provider.get_components(),
                modifiers=provider.get_modifiers(),
                vehicle_classes=provider.get_vehicle_classes(),
                resources=provider.get_resources(),
                resource_catalog=provider.get_resource_catalog(),
            )
        except Exception:
            registries = None

        team0_ships = []
        team1_ships = []

        # Convert each fleet's ships to simulation Ship objects
        for fleet in self.state.side_0.fleets:
            team0_ships.extend(
                fleet.battle.to_battle_ships(team_id=0, registries=registries)
            )

        for fleet in self.state.side_1.fleets:
            team1_ships.extend(
                fleet.battle.to_battle_ships(team_id=1, registries=registries)
            )

        if not team0_ships or not team1_ships:
            logger.warning("Cannot start battle: both sides need ships")
            return

        if self.scene_callback:
            action = "start_headless" if headless else "start_battle"
            self.scene_callback(action, team0=team0_ships, team1=team1_ships)

    # === Save/Load ===

    def _save_setup(self):
        """Save the full battle setup to a file."""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()

        filepath = filedialog.asksaveasfilename(
            initialdir=Paths.OUTPUT_DIR,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Battle Setup"
        )
        root.destroy()

        if filepath:
            data = self.state.to_dict()
            save_json(filepath, data)
            logger.info(f"Saved battle setup to {filepath}")
