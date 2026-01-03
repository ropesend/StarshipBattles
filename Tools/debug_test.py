
import sys
import os
import pygame
sys.path.append(os.getcwd())

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, create_component

def run():
    pygame.init()
    initialize_ship_data(os.getcwd())
    load_components("data/components.json")
    
    ship = Ship("DebugShip", 0, 0, (255,255,255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('fuel_tank'), LayerType.INNER) # Tank 1
    ship.recalculate_stats()
    
    print(f"Step1: Max={ship.max_fuel}, Cur={ship.current_fuel}")
    
    # Set current to 50
    ship.current_fuel = 50
    print(f"Step1b: Set Cur to {ship.current_fuel}")
    
    ship.add_component(create_component('fuel_tank'), LayerType.INNER) # Tank 2
    ship.recalculate_stats()
    
    diff = 50000 # Expected diff
    expected = 50 + diff
    print(f"Step2: Max={ship.max_fuel}, Cur={ship.current_fuel}. Expected={expected}")
    
    if ship.current_fuel != expected:
        print(f"FAIL: Got {ship.current_fuel}, Expected {expected}")
    else:
        print("PASS")

if __name__ == "__main__":
    run()
