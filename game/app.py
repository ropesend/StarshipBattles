"""Main game entry point - coordinates scenes and game loop."""
import argparse
import pygame
import os

from game.core.logger import log_debug, log_info, log_error
from game.core.config import DisplayConfig

# Parse command line arguments
parser = argparse.ArgumentParser(description="Starship Battles")
parser.add_argument('--force-resolution', action='store_true',
                    help='Force 2560x1600 resolution regardless of monitor size')
args, _ = parser.parse_known_args()

from game.simulation.components.component import load_components, load_modifiers
from ui import Button
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.ui.renderer.sprites import SpriteManager
from game.ui.screens.battle_scene import BattleScene
from game.ui.screens.setup_screen import BattleSetupScreen
from game.ui.screens.strategy_scene import StrategyScene
from Tools.formation_editor import FormationEditorScene
from ui.test_lab_scene import TestLabScene
from game.core.profiling import PROFILER, profile_action
from game.battle_coordinator import (
    update_battle_headless, update_battle_visual,
    draw_battle_hud, update_tick_rate
)
from game.exit_dialog import (
    draw_exit_dialog, handle_exit_dialog_click, handle_exit_dialog_cancel
)

# Constants
DEFAULT_WIDTH, DEFAULT_HEIGHT = DisplayConfig.default_resolution()
WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT
FPS = 60
BG_COLOR = (10, 10, 20)

# Scene States
from game.core.constants import GameState
from game.core.input_handler import InputHandler

# Scene States (Aliased for compatibility)
MENU = GameState.MENU
BUILDER = GameState.BUILDER
BATTLE = GameState.BATTLE
BATTLE_SETUP = GameState.BATTLE_SETUP
FORMATION = GameState.FORMATION
TEST_LAB = GameState.TEST_LAB
STRATEGY = GameState.STRATEGY

# Initialize fonts
pygame.font.init()
font_small = pygame.font.SysFont("arial", 12)
font_med = pygame.font.SysFont("arial", 20)
font_large = pygame.font.SysFont("arial", 32)


class Game:
    """Main game class coordinating scenes and game loop."""

    def __init__(self):
        pygame.init()

        # Monitor detection and resolution setup
        info = pygame.display.Info()
        monitor_w = info.current_w
        monitor_h = info.current_h

        global WIDTH, HEIGHT

        if args.force_resolution:
            WIDTH, HEIGHT = DisplayConfig.default_resolution()
        elif monitor_w >= 3840 and monitor_h >= 2160:
            WIDTH, HEIGHT = 3840, 2160
        elif monitor_w >= 2560 and monitor_h >= 1600:
            WIDTH, HEIGHT = 2560, 1600
        else:
            WIDTH, HEIGHT = int(monitor_w * 0.9), int(monitor_h * 0.9)

        if not pygame.display.get_surface():
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.get_surface()

        pygame.display.set_caption(f"Starship Battles ({WIDTH}x{HEIGHT})")

        self.clock = pygame.time.Clock()
        self.running = True
        self.show_exit_dialog = False
        self.state = MENU

        # Load game data
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_components(os.path.join(base_path, "data", "components.json"))
        load_modifiers(os.path.join(base_path, "data", "modifiers.json"))

        # Initialize ship data
        from game.simulation.entities.ship import initialize_ship_data
        initialize_ship_data(base_path)

        # Load sprites
        sprite_mgr = SpriteManager.get_instance()
        sprite_mgr.load_sprites(base_path)

        # Menu UI
        self.update_menu_buttons()

        # Scene objects
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)
        self.battle_setup = BattleSetupScreen()
        self.battle_scene = BattleScene(WIDTH, HEIGHT)
        self.strategy_scene = StrategyScene(WIDTH, HEIGHT)
        self.formation_scene = FormationEditorScene(WIDTH, HEIGHT, self.on_formation_return)
        self.test_lab_scene = TestLabScene(self)

    def update_menu_buttons(self):
        self.menu_buttons = [
            Button(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 50, "Ship Builder", self.start_builder),
            Button(WIDTH // 2 - 100, HEIGHT // 2 - 10, 200, 50, "Battle Setup", self.start_battle_setup),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, "Strategy Layer", self.start_strategy_layer),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 130, 200, 50, "Formation Editor", self.start_formation_editor),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 200, 200, 50, "Combat Lab", self.start_test_lab)
        ]

    @profile_action("App: Start Builder")
    def start_builder(self, return_to=None):
        """Enter ship builder."""
        self.state = BUILDER
        self.builder_return_state = return_to
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)

    def on_builder_return(self, custom_ship=None):
        """Return from builder to caller or main menu."""
        if self.builder_return_state == STRATEGY:
            self.state = STRATEGY
            if hasattr(self.strategy_scene, 'handle_resize'):
                self.strategy_scene.handle_resize(WIDTH, HEIGHT)
        else:
            self.state = MENU
        self.builder_return_state = None

    @profile_action("App: Start Battle Setup")
    def start_battle_setup(self, preserve_teams=False):
        """Enter battle setup screen."""
        self.state = BATTLE_SETUP
        self.return_state = BATTLE_SETUP
        self.battle_setup.start(preserve_teams=preserve_teams)

    def start_strategy_layer(self):
        """Enter strategy layer."""
        self.state = STRATEGY
        if hasattr(self.strategy_scene, 'handle_resize'):
            self.strategy_scene.handle_resize(WIDTH, HEIGHT)

    @profile_action("App: Start Formation Editor")
    def start_formation_editor(self):
        """Enter formation editor."""
        self.state = FORMATION
        self.formation_scene.handle_resize(WIDTH, HEIGHT)

    def on_formation_return(self):
        """Return from formation editor."""
        self.state = MENU

    def start_test_lab(self):
        """Enter Combat Lab."""
        self.state = TEST_LAB
        self.return_state = TEST_LAB

    def start_battle(self, team1_ships, team2_ships, headless=False):
        """Start a battle with the given ships."""
        self.state = BATTLE
        if self.battle_scene.screen_width != WIDTH or self.battle_scene.screen_height != HEIGHT:
            self.battle_scene.handle_resize(WIDTH, HEIGHT)
        self.battle_scene.start(team1_ships, team2_ships, headless=headless)

    def run(self):
        """Main game loop."""
        while self.running:
            frame_time = self.clock.tick(0) / 1000.0
            if frame_time > 0.1:
                frame_time = 0.1

            events = pygame.event.get()

            if self.show_exit_dialog:
                self._handle_exit_dialog_events(events)
            else:
                self._handle_normal_events(events)

            self._update_and_draw(frame_time, events)
            pygame.display.flip()

        pygame.quit()

    def _handle_exit_dialog_events(self, events):
        """Handle events when exit dialog is shown."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_exit_dialog = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if handle_exit_dialog_click(event.pos):
                    self.running = False
                elif handle_exit_dialog_cancel(event.pos):
                    self.show_exit_dialog = False

    def _handle_normal_events(self, events):
        """Handle events during normal gameplay."""
        for event in events:
            state_before = self.state

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_x and (event.mod & pygame.KMOD_ALT):
                self.show_exit_dialog = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                active = PROFILER.toggle()
                log_info(f"Profiling {'ENABLED' if active else 'DISABLED'}")
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event)
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_scroll(event)

            # Forward events to current scene only if state didn't change
            if self.state != state_before:
                log_debug(f"State changed from {state_before} to {self.state}")
                continue

            self._forward_event_to_scene(event)

    def _forward_event_to_scene(self, event):
        """Forward event to the current active scene."""
        if self.state == MENU:
            for btn in self.menu_buttons:
                btn.handle_event(event)
        elif self.state == BUILDER:
            self.builder_scene.handle_event(event)
        elif self.state == BATTLE_SETUP:
            self.battle_setup.update([event], self.screen.get_size())
        elif self.state == FORMATION:
            self.formation_scene.handle_event(event)
        elif self.state == STRATEGY:
            self.strategy_scene.handle_event(event)
        elif self.state == TEST_LAB:
            self.test_lab_scene.handle_input([event])

    def _handle_resize(self, w, h):
        """Handle window resize."""
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = w, h
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        if self.state == MENU:
            self.update_menu_buttons()
        elif self.state == BATTLE:
            self.battle_scene.handle_resize(w, h)
        elif self.state == BUILDER:
            if hasattr(self.builder_scene, 'handle_resize'):
                self.builder_scene.handle_resize(w, h)
        elif self.state == FORMATION:
            self.formation_scene.handle_resize(w, h)
        elif self.state == TEST_LAB:
            self.test_lab_scene._create_ui()
        elif self.state == STRATEGY:
            self.strategy_scene.handle_resize(w, h)

    def _handle_keydown(self, event):
        """Handle key press events."""
        InputHandler.handle_keydown(self, event)

    def _handle_click(self, event):
        """Handle mouse click events."""
        mx, my = event.pos

        if self.state == BATTLE:
            if self.battle_scene.handle_click(mx, my, event.button, self.screen.get_size()):
                self._handle_battle_actions()
        elif self.state == STRATEGY:
            self.strategy_scene.handle_click(mx, my, event.button)

    def _handle_battle_actions(self):
        """Handle action flags from battle scene."""
        if self.battle_scene.action_return_to_test_lab:
            log_debug("Returning to Combat Lab from test")
            self.battle_scene.action_return_to_test_lab = False
            self.battle_scene.test_mode = False
            self.test_lab_scene.reset_selection()
            self.start_test_lab()
        elif self.battle_scene.action_return_to_setup:
            log_debug("Returning to battle setup")
            self.battle_scene.action_return_to_setup = False
            if hasattr(self, 'return_state') and self.return_state == TEST_LAB:
                self.start_test_lab()
            else:
                self.start_battle_setup(preserve_teams=True)

    def _handle_scroll(self, event):
        """Handle mouse wheel events."""
        if self.state == BATTLE:
            mx, my = pygame.mouse.get_pos()
            sw = self.screen.get_size()[0]
            if mx >= sw - self.battle_scene.stats_panel_width or mx < self.battle_scene.ui.seeker_panel.rect.width:
                self.battle_scene.handle_scroll(event.y, self.screen.get_size()[1])
        elif self.state == STRATEGY and hasattr(self.strategy_scene, 'handle_scroll'):
            self.strategy_scene.handle_scroll(event.y, self.screen.get_size()[1])

    def _update_and_draw(self, frame_time, events):
        """Update logic and draw current scene."""
        if self.state == MENU:
            self._draw_menu()
        elif self.state == BUILDER:
            self.builder_scene.update(frame_time)
            self.builder_scene.draw(self.screen)
        elif self.state == BATTLE_SETUP:
            self._update_battle_setup()
        elif self.state == BATTLE:
            self._update_battle(frame_time, events)
        elif self.state == FORMATION:
            self.formation_scene.update(frame_time)
            self.formation_scene.draw(self.screen)
        elif self.state == STRATEGY:
            self.strategy_scene.update_input(frame_time, events)
            self.strategy_scene.update(frame_time)
            self.strategy_scene.draw(self.screen)
            if self.strategy_scene.action_open_design:
                self.strategy_scene.action_open_design = False
                self.start_builder(return_to=STRATEGY)
        elif self.state == TEST_LAB:
            self.test_lab_scene.update()
            self.test_lab_scene.draw(self.screen)

        if self.show_exit_dialog:
            draw_exit_dialog(self.screen, font_large, font_med)

    def _draw_menu(self):
        """Draw main menu."""
        self.screen.fill((20, 20, 30))
        for btn in self.menu_buttons:
            btn.draw(self.screen)

    def _update_battle_setup(self):
        """Update and draw battle setup, handle actions."""
        self.battle_setup.draw(self.screen)

        if self.battle_setup.action_start_battle:
            self.battle_setup.action_start_battle = False
            team1, team2 = self.battle_setup.get_ships()
            self.start_battle(team1, team2)
        elif self.battle_setup.action_start_headless:
            self.battle_setup.action_start_headless = False
            team1, team2 = self.battle_setup.get_ships()
            log_info(f"Team 1: {len(team1)} ships ({sum(s.max_hp for s in team1):.0f} total HP)")
            log_info(f"Team 2: {len(team2)} ships ({sum(s.max_hp for s in team2):.0f} total HP)")
            log_info("Running simulation...")
            self.start_battle(team1, team2, headless=True)
        elif self.battle_setup.action_return_to_menu:
            self.battle_setup.action_return_to_menu = False
            self.state = MENU

    def _update_battle(self, frame_time, events):
        """Update and draw battle scene."""
        if self.battle_scene.headless_mode:
            update_battle_headless(self, self.battle_scene)
        else:
            update_battle_visual(self, self.battle_scene, frame_time, events)
            self.battle_scene.draw(self.screen)
            update_tick_rate(self.battle_scene, frame_time)
            draw_battle_hud(self.screen, self.battle_scene, font_med, PROFILER.is_active())


def main():
    game = Game()

    from game.core.registry import RegistryManager
    RegistryManager.instance().freeze()

    try:
        game.run()
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        log_error("CRITICAL CRASH CAUGHT:")
        log_error(error_msg)
        with open("crash_log.txt", "w") as f:
            f.write(error_msg)
        raise e

    PROFILER.save_history()


if __name__ == "__main__":
    main()
