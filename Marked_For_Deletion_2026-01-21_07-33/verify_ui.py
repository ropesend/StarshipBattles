
import pygame
import pygame_gui
import sys
import os

# Dummy video driver for headless
os.environ["SDL_VIDEODRIVER"] = "dummy"

import game.ui.screens.strategy_screen as strategy_screen
from game.ui.panels.system_tree_panel import SystemTreePanel

# Mock Classes
class MockObject:
    pass

class MockStar(MockObject):
    def __init__(self, name):
        self.name = name
        self.color = (255, 255, 0)
        self.mass = 2.0
        self.star_type = type('obj', (), {'name': 'G-Type'})
        self.temperature = 5778
        self.diameter_hexes = 1.0
        self.spectrum = type('obj', (), {
            'gamma_ray': 0.1, 'xray': 0.1, 'ultraviolet': 0.2,
            'blue': 0.5, 'green': 1.0, 'red': 0.8,
            'infrared': 0.4, 'microwave': 0.1, 'radio': 0.05
        })

class MockPlanet(MockObject):
    def __init__(self, name, size=1):
        self.name = name
        self.planet_type = type('obj', (), {'name': 'Terran', 'color': (0,100,255)})
        self.mass = 5.97e24 * size
        self.radius = 6371 * size
        self.orbit_distance = 1
        self.surface_gravity = 9.81
        self.surface_temperature = 288
        self.surface_water = 0.7
        self.total_pressure_atm = 1.0
        self.atmosphere = {'N2': 78000, 'O2': 21000}
        self.location = type('obj', (), {'q': 0, 'r': 0})

class MockWarpPoint(MockObject):
    def __init__(self, dest):
        self.destination_id = dest
        self.location = type('obj', (), {'q': 0, 'r': 0})

class MockSystem(MockObject):
    def __init__(self, name):
        self.name = name
        self.stars = []
        self.planets = []
        self.warp_points = []
        self.primary_star = None

class MockScene:
    def __init__(self):
        self.camera = type('obj', (), {'zoom': 1.0})
    def _get_label_for_obj(self, obj):
        return obj.name
    def _get_object_asset(self, obj):
        return None

def run_verification():
    pygame.init()
    pygame.display.set_mode((1600, 900))
    screen = pygame.display.get_surface()

    scene = MockScene()
    ui = strategy_screen.StrategyInterface(scene, 1600, 900)

    # Setup Data
    sol = MockSystem("Sol")
    sun = MockStar("Sun")
    sol.stars.append(sun) # Single star -> No Group
    sol.primary_star = sun
    
    earth = MockPlanet("Earth")
    mars = MockPlanet("Mars", size=0.5)
    
    # 2 Planets at SAME location to trigger stack logic?
    # Or just test grouping logic generally.
    # Grouping logic: Planets -> ALWAYS groups under "Planetary System" if set_items used that way.
    # User Request 1: "Single star... no pile".
    # I fixed Stars and Warp Points.
    # Planets grouping: My code has "Planetary System" header if not flat_view.
    # Wait, the user said "when a single star exists... that star is under a list".
    # Did they imply Planets too? "single star, or planet, or warpoint".
    # I fixed Starts and WarpPoints.
    # I need to check if "Planets" group is also created if only 1 planet?
    # In `SystemTreePanel`:
    # `if planets:` -> `largest = ...` -> `header = ...`.
    # Yes, it creates "Planetary System" header even if 1 planet.
    # Code:
    # `if flat_view: create_nodes...`
    # `else: header = ... create_nodes(header...)`
    # I should Fix Planets too if len(planets) == 1?
    # "Group all Planets into a single 'Planetary System' group... IF there are multiple." (Original plan).
    # Current User Request: "when there is only a single star, or planet, or warpoint then there should be not stack".
    # So I DO need to fix Planet grouping too! I missed that in execution!
    # I will do it in next step.
    
    # Verification of Stars Logic:
    # Sol has 1 star. Should show directly.
    
    sol.planets = [earth, mars]
    
    wp = MockWarpPoint("Alpha Centauri")
    sol.warp_points = [wp] # Single Warp Point -> No Group
    
    contents = [sun, earth, mars, wp]

    # 1. Verify System View (Grouping)
    print("Verifying System View (Single Object Logic)...")
    ui.show_system_info(sol, contents)
    
    # Expand groups manually (Planets should be grouped, Stars/WP not)
    for item in ui.system_tree.root_items:
        if hasattr(item, 'is_group'):
            item.expanded = True
    ui.system_tree.layout()
    
    ui.manager.update(0.1)
    screen.fill((0,0,0))
    ui.draw(screen)
    pygame.image.save(screen, "verify_system_view_single.png")

    # 2. Verify Detail Panel (Vertical Text)
    print("Verifying Detail View (Vertical Text)...")
    ui.show_detailed_report(sun)
    
    ui.manager.update(0.1)
    screen.fill((0,0,0))
    ui.draw(screen)
    pygame.image.save(screen, "verify_detail_vertical.png")

    print("Verification Complete. Artifacts generated.")
    pygame.quit()

if __name__ == "__main__":
    run_verification()
