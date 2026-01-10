import pytest

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component
from game.simulation.components.abilities import ResourceGeneration, ResourceStorage, ResourceConsumption, WeaponAbility
from ui.builder.stats_config import get_logistics_rows
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.simulation.entities.ship_stats import ShipStatsCalculator

class MockClass:
    def __init__(self, data):
        self.data = data
    def get(self, key, default=None):
        return self.data.get(key, default)

def test_missing_logistics_details():
    """
    Validation Test for BUG-05.
    Ensures that the Stats Panel Logistics section includes detailed breakdown:
    - Generation Rate
    - Constant Consumption Rate
    - Max Consumption Rate (if applicable)
    - Endurance estimates
    """
    # 1. Setup Ship and Registry
    from game.core.registry import RegistryManager
    mgr = RegistryManager.instance()
    # Ensure clean state for this specific test class setup
    mgr.vehicle_classes["TestClass"] = {'max_mass': 1000, 'type': 'Ship'}

    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")
    
    print(f"Ship Layers: {list(ship.layers.keys())}")
    
    # 2. Add Components
    # A. Battery (Storage)
    battery = Component({"id": "batt", "name": "Battery", "mass": 10, "hp": 20, "type": "Internal"})
    battery.ability_instances = [ResourceStorage(battery, {'resource': 'energy', 'amount': 100})]
    
    from game.simulation.components.component import LayerType as LT
    print(f"Test LayerType.INNER: {LayerType.INNER} (id: {id(LayerType.INNER)})")
    if ship.layers:
        first_key = list(ship.layers.keys())[0]
        print(f"Ship Layer Key type: {type(first_key)} (id: {id(first_key)})")

    ship.layers[LayerType.INNER]['components'].append(battery)

    # B. Reactor (Generation)
    reactor = Component({"id": "react", "name": "Reactor", "mass": 50, "hp": 100, "type": "Internal"})
    # Rate 5.0 per tick -> 500 per second (if 100hz) but UI usually shows per second or tick
    # Let's assume rate is per tick for now as per system norms
    reactor.ability_instances = [ResourceGeneration(reactor, {'resource': 'energy', 'amount': 5.0})]
    ship.layers[LayerType.INNER]['components'].append(reactor)

    # C. Life Support (Constant Consumption)
    life_support = Component({"id": "ls", "name": "LifeSupport", "mass": 20, "hp": 50, "type": "Internal"})
    life_support.ability_instances = [ResourceConsumption(life_support, {'resource': 'energy', 'amount': 2.0, 'trigger': 'constant'})]
    ship.layers[LayerType.INNER]['components'].append(life_support)

    # D. Weapon (Active Consumption)
    weapon = Component({"id": "laser", "name": "Laser", "mass": 10, "hp": 50, "type": "Internal"})
    # Reload 1.0, cost 5.0 -> 5.0/s
    weapon.ability_instances = [
        ResourceConsumption(weapon, {'resource': 'energy', 'amount': 5.0, 'trigger': 'activation'}),
        WeaponAbility(weapon, {'damage': 10, 'reload': 1.0}) 
    ]
    ship.layers[LayerType.INNER]['components'].append(weapon)

    # 3. Calculate Stats
    calc = ShipStatsCalculator(mgr.vehicle_classes)
    calc.calculate(ship)

    # 4. Get Logistics Rows (The function being tested)
    rows = get_logistics_rows(ship)
    
    # Extract keys and labels for debugging
    row_data = {r.key: r.label for r in rows}
    print(f"Generated Rows: {row_data}")

    # 5. Assertions (The Fail Conditions)
    # We check for Energy specific fields - All 6 rows required
    
    # 1. Capacity (Should exist already)
    assert "max_energy" in row_data, "Capacity row (1/6) missing"
    
    # 2. Generation (Missing in BUG-05)
    assert "energy_gen" in row_data, f"Generation row (2/6) missing. Found: {list(row_data.keys())}"

    # 3. Constant Consumption (Missing in BUG-05)
    assert "energy_constant" in row_data, f"Constant Use row (3/6) missing. Found: {list(row_data.keys())}"
    
    # 4. Max Usage (Missing in BUG-05)
    # Even if equal to constant, requirement implies checking for it.
    assert "energy_max_usage" in row_data, f"Max Usage row (4/6) missing. Found: {list(row_data.keys())}"

    # 5. Constant Endurance (Missing in BUG-05)
    assert "energy_endurance" in row_data, f"Constant Endurance row (5/6) missing. Found: {list(row_data.keys())}"

    # 6. Max Endurance (Missing in BUG-05)
    assert "energy_max_endurance" in row_data, f"Max Endurance row (6/6) missing. Found: {list(row_data.keys())}"
    
    # Optional Value Verification
    # We know specific values based on the components added:
    # Capacity: 100
    # Generation: 5.0
    # Constant: 2.0
    # Max Usage: 2.0 (Constant) + (5.0 / 1.0) = 7.0

