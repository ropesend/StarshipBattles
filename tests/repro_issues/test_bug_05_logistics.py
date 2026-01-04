import pytest
import sys
import os
sys.path.append(os.getcwd())
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component
from game.simulation.components.abilities import ResourceGeneration, ResourceStorage, ResourceConsumption, WeaponAbility
from ui.builder.stats_config import get_logistics_rows
from ship_stats import ShipStatsCalculator
from ship_stats import ShipStatsCalculator

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
    # 1. Setup Ship
    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255))
    ship.ship_class = "TestClass"
    
    # Mock Vehicle Classes for Calc
    vehicle_classes = {"TestClass": {'max_mass': 1000, 'type': 'Ship'}}
    
    # 2. Add Components
    # A. Battery (Storage)
    battery = Component({"id": "batt", "name": "Battery", "mass": 10, "hp": 20, "type": "Internal"})
    battery.ability_instances = [ResourceStorage(battery, {'resource': 'energy', 'amount': 100})]
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
    calc = ShipStatsCalculator(vehicle_classes)
    calc.calculate(ship)

    # 4. Get Logistics Rows (The function being tested)
    rows = get_logistics_rows(ship)
    
    # Extract keys and labels for debugging
    row_data = {r.key: r.label for r in rows}
    print(f"Generated Rows: {row_data}")

    # 5. Assertions (The Fail Conditions)
    # We check for Energy specific fields
    
    # Capacity (Should exist already)
    assert "max_energy" in row_data, "Capacity row missing (Regression?)"
    
    # Generation (Missing in BUG-05)
    assert f"energy_gen" in row_data, f"Missing Energy Generation Row. Found: {list(row_data.keys())}"

    # Constant Consumption (Missing in BUG-05)
    assert f"energy_constant" in row_data, f"Missing Energy Constant Row. Found: {list(row_data.keys())}"
    
    # Max Usage (Missing in BUG-05)
    # Weapon adds 5.0/s active cost. Total Max = 7.0. Constant = 2.0.
    assert f"energy_max_usage" in row_data, f"Missing Energy Max Usage Row. Found: {list(row_data.keys())}"
    # in this test case, constant = 2.0. Max = ?
    # Ship stats calculator should have run.
    # Life Support constant=2.0
    # No weapons. So max = constant = 2.0.
    # Logic says: "if consumption_max > consumption_constant: show max row".
    # Since they are equal, it might NOT show max row.
    # We should add a weapon to trigger max usage row.


    # Verify Values (Optional, but good for robust testing)
    # Get the row object to check value
    # We can't easily check formatted value without the row object, but existence is the primary bug.
