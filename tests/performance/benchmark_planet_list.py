
import time
import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.ui.screens.planet_list_window import PlanetListWindow

# Mock Classes
class MockPlanet:
    def __init__(self, i):
        self.name = f"Planet {i}"
        self.planet_type = MagicMock()
        self.planet_type.name = "Terran"
        self.surface_gravity = 9.81
        self.surface_temperature = 288
        self.mass = 5.97e24
        self.image = pygame.Surface((32, 32)) # Mock image
        self.owner_id = 1
        self.surface_water = 0.7
        self.total_pressure_atm = 1.0

class MockSystem:
    def __init__(self, i):
        self.name = f"System {i}"
        self.planets = [MockPlanet(f"{i}-{j}") for j in range(5)] # 5 planets per system

class MockGalaxy:
    def __init__(self, num_systems=200):
        # 200 systems * 5 planets = 1000 planets
        self.systems = {}
        for i in range(num_systems):
            self.systems[f"Hex({i})"] = MockSystem(i)

class MockEmpire:
    def __init__(self):
        self.id = 1

def benchmark_planet_list_performance():
    pygame.init()
    pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
    
    manager = pygame_gui.UIManager((800, 600))
    rect = pygame.Rect(50, 50, 700, 500)
    galaxy = MockGalaxy(num_systems=100) # 500 planets
    empire = MockEmpire()
    
    print(f"\n--- Benchmarking PlanetListWindow with ~2500 planets ---")
    
    # Measure Init Time
    t0 = time.perf_counter()
    window = PlanetListWindow(rect, manager, galaxy, empire)
    t1 = time.perf_counter()
    print(f"Initialization Time: {(t1-t0)*1000:.2f} ms")
    
    # Measure Update Time (simulating frames)
    # We want to measure the cost of 'refresh_list' primarily if it was called,
    # but also general update overhead.
    
    # Force a refresh
    t_refresh_start = time.perf_counter()
    window.refresh_list()
    t_refresh_end = time.perf_counter()
    print(f"Refresh List Time: {(t_refresh_end - t_refresh_start)*1000:.2f} ms")
    
    # Measure 60 frames of updates
    t_update_start = time.perf_counter()
    for _ in range(60):
        manager.update(0.016)
        window.update(0.016)
    t_update_end = time.perf_counter()
    
    avg_update = ((t_update_end - t_update_start) / 60) * 1000
    print(f"Avg Frame Update Time: {avg_update:.2f} ms")
    
    # Check if virtualized?
    # We can inspect internal state if we know what to look for, 
    # but for now raw timing is the metric.
    
    pygame.quit()

if __name__ == "__main__":
    benchmark_planet_list_performance()
