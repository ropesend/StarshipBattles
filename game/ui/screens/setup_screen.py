"""Battle setup screen module for configuring teams before battle."""
import os
import uuid
import pygame
import tkinter as tk
from tkinter import filedialog

from game.core.logger import log_error
from game.simulation.entities.ship import Ship
from game.ai.controller import StrategyManager
from game.core.json_utils import load_json_required
from game.ui.screens.setup_data_io import (
    get_base_path, scan_ship_designs, scan_formations,
    load_ships_from_entries, save_battle_setup, load_battle_setup
)
from game.ui.screens.setup_renderer import (
    draw_title, draw_available_ships, draw_load_save_buttons,
    draw_team, draw_action_buttons, draw_ai_dropdown
)


class BattleSetupScreen:
    """Manages the battle setup screen for selecting teams and AI strategies."""

    def __init__(self):
        self.available_ship_designs = []
        self.available_formations = []
        self.team1 = []
        self.team2 = []
        self.scroll_offset = 0
        self.ai_dropdown_open = None
        self.ai_strategies = list(StrategyManager.instance().strategies.keys())

        # Action flags for Game class to check
        self.action_start_battle = False
        self.action_start_headless = False
        self.action_return_to_menu = False

    def start(self, preserve_teams=False):
        """Initialize or reset the setup screen."""
        self.available_ship_designs = scan_ship_designs()
        self.available_formations = scan_formations()

        if not preserve_teams:
            self.team1 = []
            self.team2 = []

        self.scroll_offset = 0
        self.ai_dropdown_open = None
        self.action_start_battle = False
        self.action_start_headless = False
        self.action_return_to_menu = False

    def get_ships(self):
        """Load and return ships for both teams."""
        team1_ships = load_ships_from_entries(self.team1, team_id=0, start_x=20000, start_y=30000, facing_angle=0)
        team2_ships = load_ships_from_entries(self.team2, team_id=1, start_x=80000, start_y=30000, facing_angle=180)
        return team1_ships, team2_ships

    def save_setup(self):
        """Open dialog to save current setup to JSON."""
        root = tk.Tk()
        root.withdraw()
        base_path = get_base_path()
        battles_dir = os.path.join(base_path, "data", "battles")
        if not os.path.exists(battles_dir):
            os.makedirs(battles_dir)

        filepath = filedialog.asksaveasfilename(
            initialdir=battles_dir,
            title="Save Battle Setup",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            defaultextension=".json"
        )
        root.destroy()

        if filepath:
            save_battle_setup(filepath, self.team1, self.team2)

    def load_setup(self):
        """Open dialog to load a battle setup."""
        root = tk.Tk()
        root.withdraw()
        base_path = get_base_path()
        battles_dir = os.path.join(base_path, "data", "battles")

        filepath = filedialog.askopenfilename(
            initialdir=battles_dir,
            title="Load Battle Setup",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        root.destroy()

        if not filepath:
            return

        new_team1, new_team2 = load_battle_setup(filepath, self.available_ship_designs)
        if new_team1 is not None:
            self.team1 = new_team1
            self.team2 = new_team2
            self.ai_dropdown_open = None

    def add_formation_to_team(self, formation, team_idx):
        """Add a formation to a specific team with a selected ship design."""
        root = tk.Tk()
        root.withdraw()

        base_path = get_base_path()
        ships_dir = os.path.join(base_path, "ships")

        ship_path = filedialog.askopenfilename(
            initialdir=ships_dir,
            title=f"Select Ship for {formation['name']}",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        root.destroy()

        if not ship_path:
            return

        try:
            arrows = formation['arrows']
            if not arrows:
                return

            ship_data = load_json_required(ship_path)
            temp_ship = Ship.from_dict(ship_data)
            temp_ship.recalculate_stats()
            diameter = temp_ship.radius * 2

            design_entry = self._find_or_create_design(ship_path, ship_data)
            self._add_formation_entries(arrows, design_entry, diameter, formation['name'], team_idx)
        except Exception as e:
            log_error(f"Error adding formation: {e}")

    def _find_or_create_design(self, ship_path, ship_data):
        """Find existing design entry or create new one."""
        for d in self.available_ship_designs:
            if os.path.normpath(d['path']) == os.path.normpath(ship_path):
                return d
        return {
            'path': ship_path,
            'name': ship_data.get('name', 'Unknown'),
            'ship_class': ship_data.get('ship_class', 'Unknown'),
            'ai_strategy': ship_data.get('ai_strategy', 'standard_ranged')
        }

    def _add_formation_entries(self, arrows, design_entry, diameter, formation_name, team_idx):
        """Add formation entries to the appropriate team."""
        positions = [item['pos'] if isinstance(item, dict) else item for item in arrows]
        min_x, max_x = min(p[0] for p in positions), max(p[0] for p in positions)
        min_y, max_y = min(p[1] for p in positions), max(p[1] for p in positions)
        center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2

        formation_id = str(uuid.uuid4())
        GRID_UNIT = 50.0
        target_list = self.team1 if team_idx == 1 else self.team2

        for item in arrows:
            if isinstance(item, dict):
                ax, ay = item['pos']
                rot_mode = item.get('rotation_mode', 'relative')
            else:
                ax, ay = item
                rot_mode = 'relative'

            world_x = ((ax - center_x) / GRID_UNIT) * diameter
            world_y = ((ay - center_y) / GRID_UNIT) * diameter

            target_list.append({
                'design': design_entry,
                'strategy': design_entry.get('ai_strategy', 'standard_ranged'),
                'relative_position': (world_x, world_y),
                'formation_id': formation_id,
                'formation_name': formation_name,
                'rotation_mode': rot_mode
            })

    def get_team_display_groups(self, team_list):
        """Group team entries for display."""
        display_items = []
        processed_formation_ids = set()

        for i, entry in enumerate(team_list):
            f_id = entry.get('formation_id')
            if f_id:
                if f_id in processed_formation_ids:
                    continue
                member_indices = [idx for idx, e in enumerate(team_list) if e.get('formation_id') == f_id]
                display_items.append({
                    'type': 'formation',
                    'name': f"{entry.get('formation_name', 'Formation')}: {entry['design']['name']}",
                    'count': len(member_indices),
                    'indices': member_indices,
                    'strategy': entry['strategy'],
                    'entry_ref': entry
                })
                processed_formation_ids.add(f_id)
            else:
                display_items.append({
                    'type': 'ship',
                    'name': entry['design']['name'],
                    'index': i,
                    'strategy': entry['strategy'],
                    'entry_ref': entry
                })
        return display_items

    def update(self, events, screen_size):
        """Handle input events."""
        sw, sh = screen_size
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.pos[0], event.pos[1], event.button, sw, sh)

    def _handle_click(self, mx, my, button, sw, sh):
        """Handle mouse click at position."""
        col1_x, col2_x, col3_x = 50, sw // 3 + 50, 2 * sw // 3 + 50
        btn_y = sh - 80

        # Available Ships column
        if col1_x <= mx < col1_x + 250:
            if self._handle_ships_click(mx, my, button):
                return

        # Load/Save buttons
        if pygame.Rect(50, btn_y, 120, 50).collidepoint(mx, my):
            self.load_setup()
            return
        if pygame.Rect(180, btn_y, 120, 50).collidepoint(mx, my):
            self.save_setup()
            return

        # Team columns
        if col2_x <= mx < col2_x + 350:
            self._handle_team_click(mx, my, col2_x, self.team1, 1)
            return
        if col3_x <= mx < col3_x + 350:
            self._handle_team_click(mx, my, col3_x, self.team2, 2)
            return

        # Action buttons
        self._handle_action_buttons(mx, my, sw, btn_y)

        # AI dropdown
        if self.ai_dropdown_open is not None:
            self._handle_dropdown_click(mx, my, col2_x, col3_x)

    def _handle_ships_click(self, mx, my, button):
        """Handle click on available ships/formations column."""
        ships_end_y = 150
        for i, design in enumerate(self.available_ship_designs):
            y = 150 + i * 40
            ships_end_y = y + 40
            if y <= my < y + 35:
                target = self.team1 if button == 1 else self.team2
                target.append({'design': design, 'strategy': design.get('ai_strategy', 'standard_ranged')})
                return True

        form_start_y = ships_end_y + 40
        for i, form in enumerate(self.available_formations):
            y = form_start_y + i * 40
            if y <= my < y + 35:
                self.add_formation_to_team(form, 1 if button == 1 else 2)
                return True
        return False

    def _handle_action_buttons(self, mx, my, sw, btn_y):
        """Handle clicks on action buttons."""
        if sw // 2 - 100 <= mx < sw // 2 + 100 and btn_y <= my < btn_y + 50:
            if self.team1 and self.team2:
                self.action_start_battle = True
        elif sw // 2 + 120 <= mx < sw // 2 + 240 and btn_y <= my < btn_y + 50:
            self.action_return_to_menu = True
        elif sw // 2 - 300 <= mx < sw // 2 - 180 and btn_y <= my < btn_y + 50:
            self.team1, self.team2 = [], []
            self.ai_dropdown_open = None
        elif sw // 2 + 260 <= mx < sw // 2 + 400 and btn_y <= my < btn_y + 50:
            if self.team1 and self.team2:
                self.action_start_headless = True

    def _handle_team_click(self, mx, my, col_x, team_list, team_idx):
        """Handle click on team column."""
        display_list = self.get_team_display_groups(team_list)
        for i, item in enumerate(display_list):
            y = 150 + i * 35
            if y <= my < y + 30:
                if mx >= col_x + 300:  # X Button
                    if item['type'] == 'ship':
                        team_list.pop(item['index'])
                    else:
                        for idx in sorted(item['indices'], reverse=True):
                            team_list.pop(idx)
                    return
                elif col_x + 150 <= mx < col_x + 280:  # AI dropdown
                    self.ai_dropdown_open = (team_idx, i)
                    return

    def _handle_dropdown_click(self, mx, my, col2_x, col3_x):
        """Handle click on AI strategy dropdown."""
        team_idx, display_idx = self.ai_dropdown_open
        team_list = self.team1 if team_idx == 1 else self.team2
        base_col_x = col2_x if team_idx == 1 else col3_x

        display_list = self.get_team_display_groups(team_list)
        if display_idx < len(display_list):
            item = display_list[display_idx]
            dropdown_x = base_col_x + 150
            ship_y = 150 + display_idx * 35 + 30
            dropdown_h = len(self.ai_strategies) * 22

            if dropdown_x <= mx < dropdown_x + 180 and ship_y <= my < ship_y + dropdown_h:
                option_idx = (my - ship_y) // 22
                if 0 <= option_idx < len(self.ai_strategies):
                    new_strat = self.ai_strategies[option_idx]
                    if item['type'] == 'ship':
                        team_list[item['index']]['strategy'] = new_strat
                    else:
                        for idx in item['indices']:
                            team_list[idx]['strategy'] = new_strat

        self.ai_dropdown_open = None

    def draw(self, screen):
        """Draw the battle setup screen."""
        screen.fill((20, 25, 35))
        sw, sh = screen.get_size()

        label_font = pygame.font.Font(None, 36)
        item_font = pygame.font.Font(None, 28)
        col1_x, col2_x, col3_x = 50, sw // 3 + 50, 2 * sw // 3 + 50
        btn_y = sh - 80

        draw_title(screen, sw)
        draw_available_ships(screen, col1_x, self.available_ship_designs, self.available_formations, label_font, item_font)
        draw_load_save_buttons(screen, btn_y, label_font)
        draw_team(screen, self.get_team_display_groups(self.team1), col2_x, "Team 1", (100, 200, 255), label_font, item_font)
        draw_team(screen, self.get_team_display_groups(self.team2), col3_x, "Team 2", (255, 100, 100), label_font, item_font)
        draw_action_buttons(screen, sw, btn_y, bool(self.team1 and self.team2), label_font)

        if self.ai_dropdown_open is not None:
            draw_ai_dropdown(screen, self.ai_strategies, self.ai_dropdown_open[0], self.ai_dropdown_open[1], col2_x, col3_x, item_font)
