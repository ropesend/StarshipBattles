
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.simulation.components.component import load_components, create_component
from ship_stats import ShipStatsCalculator
from game.simulation.entities.ship import load_vehicle_classes, VEHICLE_CLASSES

def test_stats():
    load_components("data/components.json")
    load_vehicle_classes("data/vehicleclasses.json")
    
    calc = ShipStatsCalculator(VEHICLE_CLASSES)
    tank = create_component("fuel_tank")
    
    print(f"Component: {tank.name}")
    print(f"Abilities: {[type(ab).__name__ for ab in tank.ability_instances]}")
    for ab in tank.ability_instances:
        print(f"  Instance {type(ab).__name__} attrs: {dir(ab)}")
        if hasattr(ab, 'max_amount'):
            print(f"  max_amount: {ab.max_amount}")
        if hasattr(ab, 'resource_type'):
            print(f"  resource_type: {ab.resource_type}")

    totals = calc.calculate_ability_totals([tank])
    print(f"\nTotals: {totals}")

if __name__ == '__main__':
    test_stats()
