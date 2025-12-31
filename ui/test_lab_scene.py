import pygame
import os
import glob
import importlib.util
import importlib
import sys

from game_constants import WHITE, BLACK, BLUE, WIDTH, HEIGHT, FONT_MAIN
from ui.components import Button
from test_framework.runner import TestRunner
from test_framework.scenario import CombatScenario

class TestLabScene:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.sys_font(FONT_MAIN, 24)
        self.title_font = pygame.font.sys_font(FONT_MAIN, 48)
        
        self.scenarios = []
        self.selected_index = -1
        self.buttons = []
        self.output_log = ["Select a scenario to run..."]
        
        self.scan_scenarios()
        self._create_ui()
        
    def scan_scenarios(self):
        """Scan test_framework/scenarios for valid scenario classes."""
        self.scenarios = []
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scenarios_dir = os.path.join(base_dir, "test_framework", "scenarios")
        
        files = glob.glob(os.path.join(scenarios_dir, "*.py"))
        for f in files:
            if "__init__" in f: continue
            
            # Load Module
            try:
                module_name = "test_framework.scenarios." + os.path.basename(f)[:-3]
                spec = importlib.util.spec_from_file_location(module_name, f)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find Classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, CombatScenario) and attr is not CombatScenario:
                        # Instantiate to get name/desc
                        try:
                            instance = attr()
                            self.scenarios.append({
                                "name": instance.name,
                                "desc": instance.description,
                                "class": attr,
                                "file": os.path.basename(f)
                            })
                        except Exception as e:
                            print(f"Failed to instantiate scenario {attr_name}: {e}")
            except Exception as e:
                print(f"Failed to load scenario file {f}: {e}")

    def _create_ui(self):
        self.buttons = []
        
        # Back Button
        self.btn_back = Button(20, 20, 100, 40, "Back", self._on_back)
        self.buttons.append(self.btn_back)
        
        # Run Button
        self.btn_run = Button(WIDTH - 150, HEIGHT - 80, 120, 50, "RUN TEST", self._on_run)
        self.buttons.append(self.btn_run)
        
        # Scenario List Base Pos
        self.list_x = 50
        self.list_y = 100
        
    def _on_back(self):
        self.game.state = "MENU" # Assuming main.py uses string or int constant? 
        # main.py constants: MENU=0
        from main import MENU
        self.game.state = MENU
        self.game.menu_screen.create_particles() # Reset menu particles if needed

    def _on_run(self):
        if self.selected_index >= 0 and self.selected_index < len(self.scenarios):
            scen_data = self.scenarios[self.selected_index]
            self.output_log.append(f"Running {scen_data['name']}...")
            
            # Run the scenario visually!
            # We need to switch game state to BATTLE but configured for this test
            # The TestRunner logic in runner.py handles data loading.
            
            runner = TestRunner()
            # 1. Load Data
            try:
                instance = scen_data['class']()
                runner.load_data_for_scenario(instance)
                
                # 2. Configure Game Battle Scene
                # We need to essentially "inject" the engine or setup into battle_scene
                # But main.py manages battle_scene.
                
                # Hack: Use the runner's engine setup logic to populate a NEW engine, 
                # then swap main.battle_scene.engine? 
                # Or just use scenario.setup(game.battle_scene.engine)
                
                # Re-init engine to clear old state
                self.game.battle_scene.engine.start([], []) # clear
                
                # Setup
                instance.setup(self.game.battle_scene.engine)
                
                # Start
                # main.py start_battle expects lists of ships... 
                # usage: self.game.start_battle(team1, team2)
                # But instance.setup ALREADY called engine.start() with ships!
                
                # So we just switch state.
                self.game.state = 3 # BATTLE constant? Need to import.
                from main import BATTLE
                self.game.state = BATTLE
                
                # Ensure battle scene knows it is not headless?
                self.game.battle_scene.headless_mode = False
                
            except Exception as e:
                self.output_log.append(f"ERROR: {e}")
                import traceback
                traceback.print_exc()

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check list selection
                mx, my = pygame.mouse.get_pos()
                for i, s in enumerate(self.scenarios):
                    rect = pygame.Rect(self.list_x, self.list_y + i*60, 400, 50)
                    if rect.collidepoint(mx, my):
                        self.selected_index = i
                        
            for btn in self.buttons:
                btn.handle_event(event)

    def draw(self, screen):
        screen.fill((30, 30, 40))
        
        # Title
        title = self.title_font.render("COMBAT LAB", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        # List
        for i, s in enumerate(self.scenarios):
            color = (50, 60, 70)
            if i == self.selected_index:
                color = (0, 100, 200)
                
            rect = pygame.Rect(self.list_x, self.list_y + i*60, 400, 50)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, rect, 1, border_radius=5)
            
            name_txt = self.font.render(s["name"], True, WHITE)
            screen.blit(name_txt, (rect.x + 10, rect.y + 10))
            
        # Description Panel
        desc_rect = pygame.Rect(500, 100, WIDTH - 550, 400)
        pygame.draw.rect(screen, (20, 20, 25), desc_rect, border_radius=5)
        pygame.draw.rect(screen, (50, 50, 60), desc_rect, 1, border_radius=5)
        
        if self.selected_index >= 0:
            s_data = self.scenarios[self.selected_index]
            desc_txt = self.font.render(f"Description: {s_data['desc']}", True, (200, 200, 200))
            screen.blit(desc_txt, (desc_rect.x + 20, desc_rect.y + 20))
            
            file_txt = self.font.render(f"File: {s_data['file']}", True, (150, 150, 150))
            screen.blit(file_txt, (desc_rect.x + 20, desc_rect.y + 60))

        # Log
        for i, msg in enumerate(self.output_log[-5:]):
            txt = self.font.render(msg, True, (255, 100, 100) if "ERROR" in msg else WHITE)
            screen.blit(txt, (20, HEIGHT - 150 + i*25))

        for btn in self.buttons:
            btn.draw(screen)
