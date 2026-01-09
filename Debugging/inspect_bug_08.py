
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.simulation.entities.ship import Ship, LayerType, load_vehicle_classes
from game.simulation.components.component import load_components, create_component
from ship_validator import ShipDesignValidator

def inspect_bug_08():
    load_components("data/components.json")
    load_vehicle_classes("data/vehicleclasses.json")
    
    # Use 'Cruiser' which is type 'Ship' and allows 'Fuel Tank'
    ship = Ship("Debug Cruiser", 0, 0, (255, 255, 255), ship_class="Cruiser")
    
    # Add Bridge (Requirement)
    bridge = create_component("bridge")
    print(f"Adding Bridge: {ship.add_component(bridge, LayerType.CORE)}")
    
    # Add Engine (Consumes fuel) - Put in OUTER to avoid CORE/INNER blocks
    engine = create_component("standard_engine")
    print(f"Adding Engine: {ship.add_component(engine, LayerType.OUTER)}")
    
    # Add Fuel Tank - Put in OUTER to be safe
    tank = create_component("fuel_tank")
    print(f"Adding Fuel Tank: {ship.add_component(tank, LayerType.OUTER)}")
    
    ship.recalculate_stats()
    
    print(f"\nFinal State for {ship.ship_class}:")
    print(f"Missing Requirements (Errors): {ship.get_missing_requirements()}")
    print(f"Validation Warnings: {ship.get_validation_warnings()}")
    
    # Check ability totals
    from ship_stats import ShipStatsCalculator
    from game.simulation.entities.ship import VEHICLE_CLASSES
    calc = ShipStatsCalculator(VEHICLE_CLASSES)
    comps = [c for l in ship.layers.values() for c in l['components']]
    totals = calc.calculate_ability_totals(comps)
    print(f"\nAbility Totals: {totals}")
    
    # Check specifically for FuelStorage
    print(f"FuelStorage in totals: {totals.get('FuelStorage', 'MISSING')}")
    
    # Manually check ResourceDependencyRule
    from ship_validator import ResourceDependencyRule
    rule = ResourceDependencyRule()
    res = rule.validate(ship)
    print(f"\nResourceDependencyRule result: {res.warnings}")

if __name__ == '__main__':
    inspect_bug_08()
