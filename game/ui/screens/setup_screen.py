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


class BattleSetupScreen:
    """Manages the battle setup screen for selecting teams and AI strategies."""

    def __init__(self):
        self.available_ship_designs = []
        self.available_formations = []
        self.team1 = []  # List of {'design': design_dict, 'strategy': str, 'relative_position': (x,y)}
        self.team2 = []
        self.scroll_offset = 0
        self.ai_dropdown_open = None  # (team_idx, ship_idx) or None
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

        # Reset actions
        self.action_start_battle = False
        self.action_start_headless = False
        self.action_return_to_menu = False

    def get_ships(self):
        """Load and return ships for both teams. Returns (team1_ships, team2_ships)."""
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

            # Find existing design entry or create new one
            design_entry = None
            for d in self.available_ship_designs:
                if os.path.normpath(d['path']) == os.path.normpath(ship_path):
                    design_entry = d
                    break

            if not design_entry:
                design_entry = {
                    'path': ship_path,
                    'name': ship_data.get('name', 'Unknown'),
                    'ship_class': ship_data.get('ship_class', 'Unknown'),
                    'ai_strategy': ship_data.get('ai_strategy', 'standard_ranged')
                }

            # Calculate Center
            positions = []
            for item in arrows:
                if isinstance(item, dict):
                    positions.append(item['pos'])
                else:
                    positions.append(item)

            min_x = min(p[0] for p in positions)
            max_x = max(p[0] for p in positions)
            min_y = min(p[1] for p in positions)
            max_y = max(p[1] for p in positions)

            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2

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

                dx = ax - center_x
                dy = ay - center_y

                world_x = (dx / GRID_UNIT) * diameter
                world_y = (dy / GRID_UNIT) * diameter

                target_list.append({
                    'design': design_entry,
                    'strategy': design_entry.get('ai_strategy', 'standard_ranged'),
                    'relative_position': (world_x, world_y),
                    'formation_id': formation_id,
                    'formation_name': formation['name'],
                    'rotation_mode': rot_mode
                })
        except Exception as e:
            log_error(f"Error adding formation: {e}")

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
                count = len(member_indices)
                design_name = entry['design']['name']
                form_name = entry.get('formation_name', 'Formation')

                display_items.append({
                    'type': 'formation',
                    'name': f"{form_name}: {design_name}",
                    'count': count,
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
                mx, my = event.pos
                self._handle_click(mx, my, event.button, sw, sh)

    def _handle_click(self, mx, my, button, sw, sh):
        """Handle mouse click at position."""
        col1_x = 50
        col2_x = sw // 3 + 50
        col3_x = 2 * sw // 3 + 50

        ships_end_y = 150

        # Available Ships column
        if col1_x <= mx < col1_x + 250:
            found_click = False
            for i, design in enumerate(self.available_ship_designs):
                y = 150 + i * 40
                ships_end_y = y + 40
                if y <= my < y + 35:
                    if button == 1:
                        self.team1.append({
                            'design': design,
                            'strategy': design.get('ai_strategy', 'standard_ranged')
                        })
                    elif button == 3:
                        self.team2.append({
                            'design': design,
                            'strategy': design.get('ai_strategy', 'standard_ranged')
                        })
                    found_click = True
                    return

            # Formations
            if not found_click:
                form_start_y = ships_end_y + 40
                for i, form in enumerate(self.available_formations):
                    y = form_start_y + i * 40
                    if y <= my < y + 35:
                        if button == 1:
                            self.add_formation_to_team(form, 1)
                        elif button == 3:
                            self.add_formation_to_team(form, 2)
                        return

        btn_y = sh - 80

        # Load/Save buttons
        btn_load_rect = pygame.Rect(50, btn_y, 120, 50)
        btn_save_rect = pygame.Rect(180, btn_y, 120, 50)

        if btn_load_rect.collidepoint(mx, my):
            self.load_setup()
            return

        if btn_save_rect.collidepoint(mx, my):
            self.save_setup()
            return

        # Team 1 clicks
        if col2_x <= mx < col2_x + 350:
            self._handle_team_click(mx, my, col2_x, self.team1, 1)
            return

        # Team 2 clicks
        if col3_x <= mx < col3_x + 350:
            self._handle_team_click(mx, my, col3_x, self.team2, 2)
            return

        # Action buttons
        if sw // 2 - 100 <= mx < sw // 2 + 100 and btn_y <= my < btn_y + 50:
            if self.team1 and self.team2:
                self.action_start_battle = True

        if sw // 2 + 120 <= mx < sw // 2 + 240 and btn_y <= my < btn_y + 50:
            self.action_return_to_menu = True

        if sw // 2 - 300 <= mx < sw // 2 - 180 and btn_y <= my < btn_y + 50:
            self.team1 = []
            self.team2 = []
            self.ai_dropdown_open = None

        if sw // 2 + 260 <= mx < sw // 2 + 400 and btn_y <= my < btn_y + 50:
            if self.team1 and self.team2:
                self.action_start_headless = True

        # AI dropdown handling
        if self.ai_dropdown_open is not None:
            self._handle_dropdown_click(mx, my, col2_x, col3_x)

    def _handle_team_click(self, mx, my, col_x, team_list, team_idx):
        """Handle click on team column."""
        display_list = self.get_team_display_groups(team_list)
        for i, item in enumerate(display_list):
            y = 150 + i * 35
            if y <= my < y + 30:
                ai_btn_x = col_x + 150
                if mx >= col_x + 300:  # X Button
                    if item['type'] == 'ship':
                        team_list.pop(item['index'])
                    else:
                        indices = sorted(item['indices'], reverse=True)
                        for idx in indices:
                            team_list.pop(idx)
                    return
                elif ai_btn_x <= mx < ai_btn_x + 130:  # AI dropdown
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
            dropdown_height = len(self.ai_strategies) * 22

            if dropdown_x <= mx < dropdown_x + 180 and ship_y <= my < ship_y + dropdown_height:
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

        title_font = pygame.font.Font(None, 64)
        title = title_font.render("BATTLE SETUP", True, (200, 200, 255))
        screen.blit(title, (sw // 2 - title.get_width() // 2, 30))

        label_font = pygame.font.Font(None, 36)
        item_font = pygame.font.Font(None, 28)

        col1_x = 50
        col2_x = sw // 3 + 50
        col3_x = 2 * sw // 3 + 50

        # Available Ships
        self._draw_available_ships(screen, col1_x, label_font, item_font)

        btn_y = sh - 80

        # Load/Save buttons
        self._draw_load_save_buttons(screen, btn_y, label_font)

        # Team columns
        self._draw_team(screen, self.team1, col2_x, "Team 1", (100, 200, 255), label_font, item_font)
        self._draw_team(screen, self.team2, col3_x, "Team 2", (255, 100, 100), label_font, item_font)

        # Action buttons
        self._draw_action_buttons(screen, sw, sh, btn_y, label_font)

        # AI dropdown overlay
        if self.ai_dropdown_open is not None:
            self._draw_ai_dropdown(screen, col2_x, col3_x, item_font)

    def _draw_available_ships(self, screen, col_x, label_font, item_font):
        """Draw the available ships and formations list."""
        lbl = label_font.render("Ships (L/R click)", True, (150, 150, 200))
        screen.blit(lbl, (col_x, 110))

        ships_end_y = 150
        for i, design in enumerate(self.available_ship_designs):
            y = 150 + i * 40
            ships_end_y = y + 40
            text = item_font.render(f"{design['name']} ({design['ship_class']})", True, (200, 200, 200))
            pygame.draw.rect(screen, (40, 45, 55), (col_x, y, 250, 35))
            pygame.draw.rect(screen, (80, 80, 100), (col_x, y, 250, 35), 1)
            screen.blit(text, (col_x + 10, y + 8))

        # Formations
        form_header_y = ships_end_y + 10
        lbl_form = label_font.render("Formations", True, (150, 200, 150))
        screen.blit(lbl_form, (col_x, form_header_y))

        form_start_y = form_header_y + 35
        for i, form in enumerate(self.available_formations):
            y = form_start_y + i * 40
            text = item_font.render(f"{form['name']}", True, (200, 255, 200))
            pygame.draw.rect(screen, (35, 50, 35), (col_x, y, 250, 35))
            pygame.draw.rect(screen, (80, 120, 80), (col_x, y, 250, 35), 1)
            screen.blit(text, (col_x + 10, y + 8))

    def _draw_load_save_buttons(self, screen, btn_y, label_font):
        """Draw load and save buttons."""
        pygame.draw.rect(screen, (60, 60, 80), (50, btn_y, 120, 50))
        pygame.draw.rect(screen, (100, 100, 150), (50, btn_y, 120, 50), 2)
        lid_text = label_font.render("LOAD", True, (200, 200, 255))
        screen.blit(lid_text, (50 + 60 - lid_text.get_width() // 2, btn_y + 12))

        pygame.draw.rect(screen, (60, 60, 80), (180, btn_y, 120, 50))
        pygame.draw.rect(screen, (100, 100, 150), (180, btn_y, 120, 50), 2)
        sav_text = label_font.render("SAVE", True, (200, 200, 255))
        screen.blit(sav_text, (180 + 60 - sav_text.get_width() // 2, btn_y + 12))

    def _draw_team(self, screen, team_list, col_x, title_text, color, label_font, item_font):
        """Draw a team column."""
        lbl = label_font.render(title_text, True, color)
        screen.blit(lbl, (col_x, 110))

        display_list = self.get_team_display_groups(team_list)

        for i, item in enumerate(display_list):
            y = 150 + i * 35
            name = item['name']
            strategy = item['strategy']
            strat_name = StrategyManager.instance().strategies.get(strategy, {}).get('name', strategy)[:12]

            is_formation = (item['type'] == 'formation')

            bg_color = (30, 60, 50) if is_formation else ((30, 50, 70) if "Team 1" in title_text else (70, 30, 30))
            border_color = (100, 200, 150) if is_formation else ((100, 150, 200) if "Team 1" in title_text else (200, 100, 100))

            pygame.draw.rect(screen, bg_color, (col_x, y, 350, 30))
            pygame.draw.rect(screen, border_color, (col_x, y, 350, 30), 1)

            name_text = item_font.render(name[:25], True, (255, 255, 255))
            screen.blit(name_text, (col_x + 5, y + 5))

            ai_btn_x = col_x + 150
            pygame.draw.rect(screen, (40, 60, 90), (ai_btn_x, y + 2, 130, 26))
            pygame.draw.rect(screen, (80, 120, 180), (ai_btn_x, y + 2, 130, 26), 1)
            ai_text = item_font.render(strat_name + " ▼", True, (150, 200, 255))
            screen.blit(ai_text, (ai_btn_x + 5, y + 5))

            x_text = item_font.render("[X]", True, (255, 100, 100))
            screen.blit(x_text, (col_x + 315, y + 5))

    def _draw_action_buttons(self, screen, sw, sh, btn_y, label_font):
        """Draw the main action buttons."""
        # Begin Battle
        btn_color = (50, 150, 50) if (self.team1 and self.team2) else (50, 50, 50)
        pygame.draw.rect(screen, btn_color, (sw // 2 - 100, btn_y, 200, 50))
        pygame.draw.rect(screen, (100, 200, 100), (sw // 2 - 100, btn_y, 200, 50), 2)
        btn_text = label_font.render("BEGIN BATTLE", True, (255, 255, 255))
        screen.blit(btn_text, (sw // 2 - btn_text.get_width() // 2, btn_y + 12))

        # Return
        pygame.draw.rect(screen, (80, 80, 80), (sw // 2 + 120, btn_y, 120, 50))
        pygame.draw.rect(screen, (150, 150, 150), (sw // 2 + 120, btn_y, 120, 50), 2)
        ret_text = label_font.render("RETURN", True, (200, 200, 200))
        screen.blit(ret_text, (sw // 2 + 180 - ret_text.get_width() // 2, btn_y + 12))

        # Clear All
        pygame.draw.rect(screen, (120, 50, 50), (sw // 2 - 300, btn_y, 120, 50))
        pygame.draw.rect(screen, (200, 100, 100), (sw // 2 - 300, btn_y, 120, 50), 2)
        clr_text = label_font.render("CLEAR ALL", True, (255, 200, 200))
        screen.blit(clr_text, (sw // 2 - 240 - clr_text.get_width() // 2, btn_y + 12))

        # Quick Battle
        quick_color = (80, 50, 120) if (self.team1 and self.team2) else (40, 40, 40)
        pygame.draw.rect(screen, quick_color, (sw // 2 + 260, btn_y, 140, 50))
        pygame.draw.rect(screen, (150, 100, 200), (sw // 2 + 260, btn_y, 140, 50), 2)
        quick_text = label_font.render("QUICK BATTLE", True, (220, 200, 255))
        screen.blit(quick_text, (sw // 2 + 330 - quick_text.get_width() // 2, btn_y + 12))

    def _draw_ai_dropdown(self, screen, col2_x, col3_x, item_font):
        """Draw AI strategy dropdown overlay."""
        team_idx, display_idx = self.ai_dropdown_open
        col_x = col2_x if team_idx == 1 else col3_x
        ship_y = 150 + display_idx * 35 + 30
        col_x = col_x + 150

        dropdown_w = 180
        dropdown_h = len(self.ai_strategies) * 22

        pygame.draw.rect(screen, (30, 30, 40), (col_x, ship_y, dropdown_w, dropdown_h))
        pygame.draw.rect(screen, (100, 100, 150), (col_x, ship_y, dropdown_w, dropdown_h), 1)

        for idx, strat_id in enumerate(self.ai_strategies):
            strat_name = StrategyManager.instance().strategies.get(strat_id, {}).get('name', strat_id)
            opt_y = ship_y + idx * 22
            text_color = (220, 220, 220)
            opt_text = item_font.render(strat_name, True, text_color)
            screen.blit(opt_text, (col_x + 5, opt_y + 3))
