"""Battle setup screen module for configuring teams before battle."""
import pygame
import json
import os
import glob
import tkinter as tk
from tkinter import filedialog

from ship import Ship
from ai import COMBAT_STRATEGIES


def scan_ship_designs():
    """Scan for available ship design JSON files in ships/ folder."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    ships_folder = os.path.join(base_path, "ships")
    json_files = glob.glob(os.path.join(ships_folder, "*.json"))
    
    designs = []
    for filepath in json_files:
        filename = os.path.basename(filepath)
        # Skip config files
        if filename in ['builder_theme.json', 'component_presets.json']:
            continue
        # Try to load and verify it's a ship design
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            if 'name' in data and 'layers' in data:
                designs.append({
                    'path': filepath,
                    'name': data.get('name', filename),
                    'ship_class': data.get('ship_class', 'Unknown'),
                    'ai_strategy': data.get('ai_strategy', 'optimal_firing_range')
                })
        except Exception:
            pass  # Skip invalid ship files
    return designs


def load_ships_from_entries(team_entries, team_id, start_x, start_y, facing_angle=0):
    """Load ships from team entry list. Returns list of Ship objects."""
    ships = []
    for i, entry in enumerate(team_entries):
        with open(entry['design']['path'], 'r') as f:
            data = json.load(f)
        ship = Ship.from_dict(data)
        ship.position = pygame.math.Vector2(start_x, start_y + i * 5000)
        ship.angle = facing_angle
        ship.ai_strategy = entry['strategy']
        ship.source_file = os.path.basename(entry['design']['path'])
        ship.team_id = team_id
        ship.recalculate_stats()
        ships.append(ship)
    return ships


class BattleSetupScreen:
    """Manages the battle setup screen for selecting teams and AI strategies."""
    
    def __init__(self):
        self.available_ship_designs = []
        self.team1 = []  # List of {'design': design_dict, 'strategy': str}
        self.team2 = []
        self.scroll_offset = 0
        self.ai_dropdown_open = None  # (team_idx, ship_idx) or None
        self.ai_strategies = list(COMBAT_STRATEGIES.keys())
        
        # Action flags for Game class to check
        self.action_start_battle = False
        self.action_start_headless = False
        self.action_return_to_menu = False
    
    def start(self, preserve_teams=False):
        """Initialize or reset the setup screen."""
        self.available_ship_designs = scan_ship_designs()
        
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
        base_path = os.path.dirname(os.path.abspath(__file__))
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
        
        if not filepath:
            return

        data = {
            "name": os.path.basename(filepath).replace(".json", ""),
            "team1": [],
            "team2": []
        }
        
        for entry in self.team1:
            data["team1"].append({
                "design_file": os.path.basename(entry['design']['path']),
                "strategy": entry['strategy']
            })
            
        for entry in self.team2:
            data["team2"].append({
                "design_file": os.path.basename(entry['design']['path']),
                "strategy": entry['strategy']
            })
            
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved battle setup to {filepath}")
        except Exception as e:
            print(f"Error saving setup: {e}")

    def load_setup(self):
        """Open dialog to load a battle setup."""
        if self.team1 or self.team2:
             # Maybe confirm overwrite? For now just do it.
             pass
             
        root = tk.Tk()
        root.withdraw()
        base_path = os.path.dirname(os.path.abspath(__file__))
        battles_dir = os.path.join(base_path, "data", "battles")
        
        filepath = filedialog.askopenfilename(
            initialdir=battles_dir,
            title="Load Battle Setup",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        root.destroy()
        
        if not filepath:
            return
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Helper to find design by filename
            def find_design(filename):
                for d in self.available_ship_designs:
                    if os.path.basename(d['path']) == filename:
                        return d
                return None
            
            new_team1 = []
            new_team2 = []
            
            for item in data.get('team1', []):
                d = find_design(item['design_file'])
                if d:
                    new_team1.append({
                        'design': d,
                        'strategy': item['strategy']
                    })
                else:
                    print(f"Warning: Design {item['design_file']} not found")

            for item in data.get('team2', []):
                d = find_design(item['design_file'])
                if d:
                    new_team2.append({
                        'design': d,
                        'strategy': item['strategy']
                    })
                else:
                    print(f"Warning: Design {item['design_file']} not found")
            
            self.team1 = new_team1
            self.team2 = new_team2
            self.ai_dropdown_open = None
            print(f"Loaded setup from {filepath}")
            
        except Exception as e:
            print(f"Error loading setup: {e}")

    
    def update(self, events, screen_size):
        """Handle input events. Returns action string or None."""
        sw, sh = screen_size
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                col1_x = 50  # Available ships
                col2_x = sw // 3 + 50  # Team 1
                col3_x = 2 * sw // 3 + 50  # Team 2
                
                # Check available ships list (left column)
                if col1_x <= mx < col1_x + 250:
                    for i, design in enumerate(self.available_ship_designs):
                        y = 150 + i * 40
                        if y <= my < y + 35:
                            if event.button == 1:  # Left click - add to team 1
                                self.team1.append({
                                    'design': design,
                                    'strategy': design.get('ai_strategy', 'optimal_firing_range')
                                })
                            elif event.button == 3:  # Right click - add to team 2
                                self.team2.append({
                                    'design': design,
                                    'strategy': design.get('ai_strategy', 'optimal_firing_range')
                                })
                            break
                
                # Check Save/Load Buttons (Top Right area? Or near Clear All?)
                # Let's put them near Clear All.
                
                # Save: sw/2 - 300 (Clear is -300 to -180). Let's put Save/Load to the left of Clear?
                # Or below the team lists?
                # Setup buttons row: [Clear] [Begin] [Return] [Quick]
                # Let's add [Load] [Save] to the far left or far right.
                
                # Let's put them under the "Available Ships" list?
                # Available ships list ends at logic ??? it renders infinite list?
                # No, we don't have scrolling yet, assumes fits.
                
                # Let's put small keys near the bottom left:
                # [Load Setup] [Save Setup]
                
                btn_load_rect = pygame.Rect(50, sh - 80, 120, 50)
                btn_save_rect = pygame.Rect(180, sh - 80, 120, 50)
                
                if btn_load_rect.collidepoint(mx, my):
                    self.load_setup()
                    return # Dialog blocks, so return after
                    
                if btn_save_rect.collidepoint(mx, my):
                    self.save_setup()
                    return

                
                # Check team 1 ships
                if col2_x <= mx < col2_x + 350:
                    for i, entry in enumerate(self.team1):
                        y = 150 + i * 35
                        if y <= my < y + 30:
                            ai_btn_x = col2_x + 150
                            if mx >= col2_x + 300:
                                self.team1.pop(i)
                                return
                            elif ai_btn_x <= mx < ai_btn_x + 130:
                                self.ai_dropdown_open = (1, i)
                                return
                
                # Check team 2 ships
                if col3_x <= mx < col3_x + 350:
                    for i, entry in enumerate(self.team2):
                        y = 150 + i * 35
                        if y <= my < y + 30:
                            ai_btn_x = col3_x + 150
                            if mx >= col3_x + 300:
                                self.team2.pop(i)
                                return
                            elif ai_btn_x <= mx < ai_btn_x + 130:
                                self.ai_dropdown_open = (2, i)
                                return
                
                # Buttons at bottom
                btn_y = sh - 80
                
                # Begin Battle button
                if sw // 2 - 100 <= mx < sw // 2 + 100 and btn_y <= my < btn_y + 50:
                    if self.team1 and self.team2:
                        self.action_start_battle = True
                
                # Return button
                if sw // 2 + 120 <= mx < sw // 2 + 240 and btn_y <= my < btn_y + 50:
                    self.action_return_to_menu = True
                
                # Clear All button
                if sw // 2 - 300 <= mx < sw // 2 - 180 and btn_y <= my < btn_y + 50:
                    self.team1 = []
                    self.team2 = []
                    self.ai_dropdown_open = None
                
                # Quick Battle (Headless) button
                if sw // 2 + 260 <= mx < sw // 2 + 400 and btn_y <= my < btn_y + 50:
                    if self.team1 and self.team2:
                        self.action_start_headless = True
                
                # Check for dropdown clicks
                if self.ai_dropdown_open is not None:
                    team_idx, ship_idx = self.ai_dropdown_open
                    team_list = self.team1 if team_idx == 1 else self.team2
                    base_col_x = col2_x if team_idx == 1 else col3_x
                    
                    dropdown_x = base_col_x + 150
                    ship_y = 150 + ship_idx * 35 + 30
                    dropdown_height = len(self.ai_strategies) * 22
                    
                    if dropdown_x <= mx < dropdown_x + 180 and ship_y <= my < ship_y + dropdown_height:
                        option_idx = (my - ship_y) // 22
                        if 0 <= option_idx < len(self.ai_strategies):
                            team_list[ship_idx]['strategy'] = self.ai_strategies[option_idx]
                    
                    self.ai_dropdown_open = None
    
    def draw(self, screen):
        """Draw the battle setup screen."""
        screen.fill((20, 25, 35))
        sw, sh = screen.get_size()
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("BATTLE SETUP", True, (200, 200, 255))
        screen.blit(title, (sw // 2 - title.get_width() // 2, 30))
        
        label_font = pygame.font.Font(None, 36)
        item_font = pygame.font.Font(None, 28)
        
        col1_x = 50
        col2_x = sw // 3 + 50
        col3_x = 2 * sw // 3 + 50
        
        # Available Ships (left column)
        lbl = label_font.render("Available Ships (L/R click to add)", True, (150, 150, 200))
        screen.blit(lbl, (col1_x, 110))
        
        for i, design in enumerate(self.available_ship_designs):
            y = 150 + i * 40
            text = item_font.render(f"{design['name']} ({design['ship_class']})", True, (200, 200, 200))
            pygame.draw.rect(screen, (40, 45, 55), (col1_x, y, 250, 35))
            pygame.draw.rect(screen, (80, 80, 100), (col1_x, y, 250, 35), 1)
            screen.blit(text, (col1_x + 10, y + 8))
            
        # Save/Load Buttons (Bottom Left)
        btn_y = sh - 80
        
        # Load Button
        pygame.draw.rect(screen, (60, 60, 80), (50, btn_y, 120, 50))
        pygame.draw.rect(screen, (100, 100, 150), (50, btn_y, 120, 50), 2)
        lid_text = label_font.render("LOAD", True, (200, 200, 255))
        screen.blit(lid_text, (50 + 60 - lid_text.get_width()//2, btn_y + 12))
        
        # Save Button
        pygame.draw.rect(screen, (60, 60, 80), (180, btn_y, 120, 50))
        pygame.draw.rect(screen, (100, 100, 150), (180, btn_y, 120, 50), 2)
        sav_text = label_font.render("SAVE", True, (200, 200, 255))
        screen.blit(sav_text, (180 + 60 - sav_text.get_width()//2, btn_y + 12))

        
        # Team 1 (middle column)
        lbl = label_font.render("Team 1", True, (100, 200, 255))
        screen.blit(lbl, (col2_x, 110))
        
        for i, entry in enumerate(self.team1):
            y = 150 + i * 35
            design = entry['design']
            strategy = entry['strategy']
            strat_name = COMBAT_STRATEGIES.get(strategy, {}).get('name', strategy)[:12]
            
            pygame.draw.rect(screen, (30, 50, 70), (col2_x, y, 350, 30))
            pygame.draw.rect(screen, (100, 150, 200), (col2_x, y, 350, 30), 1)
            
            name_text = item_font.render(design['name'][:15], True, (255, 255, 255))
            screen.blit(name_text, (col2_x + 5, y + 5))
            
            ai_btn_x = col2_x + 150
            pygame.draw.rect(screen, (40, 60, 90), (ai_btn_x, y + 2, 130, 26))
            pygame.draw.rect(screen, (80, 120, 180), (ai_btn_x, y + 2, 130, 26), 1)
            ai_text = item_font.render(strat_name + " ▼", True, (150, 200, 255))
            screen.blit(ai_text, (ai_btn_x + 5, y + 5))
            
            x_text = item_font.render("[X]", True, (255, 100, 100))
            screen.blit(x_text, (col2_x + 315, y + 5))
        
        # Team 2 (right column)
        lbl = label_font.render("Team 2", True, (255, 100, 100))
        screen.blit(lbl, (col3_x, 110))
        
        for i, entry in enumerate(self.team2):
            y = 150 + i * 35
            design = entry['design']
            strategy = entry['strategy']
            strat_name = COMBAT_STRATEGIES.get(strategy, {}).get('name', strategy)[:12]
            
            pygame.draw.rect(screen, (70, 30, 30), (col3_x, y, 350, 30))
            pygame.draw.rect(screen, (200, 100, 100), (col3_x, y, 350, 30), 1)
            
            name_text = item_font.render(design['name'][:15], True, (255, 255, 255))
            screen.blit(name_text, (col3_x + 5, y + 5))
            
            ai_btn_x = col3_x + 150
            pygame.draw.rect(screen, (90, 40, 40), (ai_btn_x, y + 2, 130, 26))
            pygame.draw.rect(screen, (180, 80, 80), (ai_btn_x, y + 2, 130, 26), 1)
            ai_text = item_font.render(strat_name + " ▼", True, (255, 150, 150))
            screen.blit(ai_text, (ai_btn_x + 5, y + 5))
            
            x_text = item_font.render("[X]", True, (255, 100, 100))
            screen.blit(x_text, (col3_x + 315, y + 5))
        
        # Buttons at bottom
        btn_y = sh - 80
        
        # Begin Battle button
        btn_color = (50, 150, 50) if (self.team1 and self.team2) else (50, 50, 50)
        pygame.draw.rect(screen, btn_color, (sw // 2 - 100, btn_y, 200, 50))
        pygame.draw.rect(screen, (100, 200, 100), (sw // 2 - 100, btn_y, 200, 50), 2)
        btn_text = label_font.render("BEGIN BATTLE", True, (255, 255, 255))
        screen.blit(btn_text, (sw // 2 - btn_text.get_width() // 2, btn_y + 12))
        
        # Return button
        pygame.draw.rect(screen, (80, 80, 80), (sw // 2 + 120, btn_y, 120, 50))
        pygame.draw.rect(screen, (150, 150, 150), (sw // 2 + 120, btn_y, 120, 50), 2)
        ret_text = label_font.render("RETURN", True, (200, 200, 200))
        screen.blit(ret_text, (sw // 2 + 180 - ret_text.get_width() // 2, btn_y + 12))
        
        # Clear All button
        pygame.draw.rect(screen, (120, 50, 50), (sw // 2 - 300, btn_y, 120, 50))
        pygame.draw.rect(screen, (200, 100, 100), (sw // 2 - 300, btn_y, 120, 50), 2)
        clr_text = label_font.render("CLEAR ALL", True, (255, 200, 200))
        screen.blit(clr_text, (sw // 2 - 240 - clr_text.get_width() // 2, btn_y + 12))
        
        # Quick Battle (Headless) button
        quick_color = (80, 50, 120) if (self.team1 and self.team2) else (40, 40, 40)
        pygame.draw.rect(screen, quick_color, (sw // 2 + 260, btn_y, 140, 50))
        pygame.draw.rect(screen, (150, 100, 200), (sw // 2 + 260, btn_y, 140, 50), 2)
        quick_text = label_font.render("QUICK BATTLE", True, (220, 200, 255))
        screen.blit(quick_text, (sw // 2 + 330 - quick_text.get_width() // 2, btn_y + 12))
        
        # Draw AI dropdown if open
        if self.ai_dropdown_open is not None:
            team_idx, ship_idx = self.ai_dropdown_open
            col_x = col2_x if team_idx == 1 else col3_x
            ship_y = 150 + ship_idx * 35 + 30
            col_x = col_x + 150
            
            dropdown_w = 180
            dropdown_h = len(self.ai_strategies) * 22
            
            pygame.draw.rect(screen, (30, 30, 40), (col_x, ship_y, dropdown_w, dropdown_h))
            pygame.draw.rect(screen, (100, 100, 150), (col_x, ship_y, dropdown_w, dropdown_h), 1)
            
            for idx, strat_id in enumerate(self.ai_strategies):
                strat_name = COMBAT_STRATEGIES.get(strat_id, {}).get('name', strat_id)
                opt_y = ship_y + idx * 22
                text_color = (220, 220, 220)
                opt_text = item_font.render(strat_name, True, text_color)
                screen.blit(opt_text, (col_x + 5, opt_y + 3))
