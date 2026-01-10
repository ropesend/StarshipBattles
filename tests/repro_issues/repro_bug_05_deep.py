import pytest
import sys
import json
import pygame

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component, load_components, load_modifiers
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.core.registry import RegistryManager
from ui.builder.stats_config import get_logistics_rows

# Mock Data simulating components.json entries
MOCK_SHIELD_REGEN_DATA = {
    "id": "shield_regen",
    "name": "Shield Regen",
    "type": "ShieldRegenerator",
    "mass": 40,
    "hp": 80,
    "allowed_vehicle_types": ["Ship"],
    "abilities": {
        "ShieldRegeneration": 5.0,
        "EnergyConsumption": 2.0
    }
}

MOCK_LASER_DATA = {
    "id": "laser_cannon",
    "name": "Laser Cannon",
    "type": "BeamWeapon",
    "mass": 20,
    "hp": 40,
    "allowed_vehicle_types": ["Ship"],
    "abilities": {
        "CrewRequired": 1,
        "ResourceConsumption": [
            {
                "resource": "energy",
                "amount": 5,
                "trigger": "activation"
            }
        ],
        "BeamWeaponAbility": {
            "reload": 0.2, # Rate = 5 / 0.2 = 25/s
            "damage": 10
        }
    }
}

def setup_test_state():
    pygame.init()
    RegistryManager.instance().clear()

def teardown_test_state():
    pygame.quit()
    RegistryManager.instance().clear()

def test_shield_regen_consumption():
    """
    Verify Shield Regen (using EnergyConsumption alias) 
    1. Registers Energy resource
    2. Calculates correctly in ship.energy_consumption
    3. Shows up in Logistics Rows
    """
    setup_test_state()
    try:
        ship = Ship(name="TestShipSC", x=0, y=0, color=(255, 255, 255))
        ship.ship_class = "TestClass"
        vehicle_classes = {"TestClass": {'max_mass': 1000, 'type': 'Ship'}}
        
        # Inject mock vehicle class into registry
        RegistryManager.instance().vehicle_classes.update(vehicle_classes)
        # Re-init layers since we changed class data
        ship._initialize_layers()
        
        # Create Component from Dict (simulating load_components)
        comp = Component(MOCK_SHIELD_REGEN_DATA)
        ship.layers[LayerType.INNER]['components'].append(comp)
        
        calc = ShipStatsCalculator(RegistryManager.instance().vehicle_classes)
        calc.calculate(ship)
        
        # Check 1: Energy Registered?
        assert 'energy' in ship.resources._resources, "Energy not registered in ship resources"
        
        # Check 2: Consumption Calculation
        print(f"Energy Consumption: {ship.energy_consumption}")
        assert ship.energy_consumption > 0, "Energy Consumption is 0, should be at least 2.0"
        
        # Check 3: Rows
        rows = get_logistics_rows(ship)
        row_keys = [r.key for r in rows]
        print(f"Row Keys: {row_keys}")
        
        assert "energy_max_usage" in row_keys, "Energy Max Usage row missing"
        
        # Check Values
        max_use_row = next(r for r in rows if r.key == 'energy_max_usage')
        val = max_use_row.get_value(ship)
        print(f"Max Usage Row Value: {val}")
        assert val == ship.energy_consumption
    finally:
        teardown_test_state()

def test_laser_cannon_consumption():
    """
    Verify Laser Cannon (Active Consumption)
    1. Registers Energy resource
    2. Calculates max usage (activation rate)
    3. Shows up in Logistics Rows
    """
    setup_test_state()
    try:
        ship = Ship(name="TestShipLC", x=0, y=0, color=(255, 255, 255))
        ship.ship_class = "TestClass"
        vehicle_classes = {"TestClass": {'max_mass': 1000, 'type': 'Ship'}}
        
        RegistryManager.instance().vehicle_classes.update(vehicle_classes)
        ship._initialize_layers()
        
        comp = Component(MOCK_LASER_DATA)
        comp.debug_log = True
        # Ensure correct instantiation of abilities
        assert comp.has_ability('ResourceConsumption')
        assert comp.has_ability('WeaponAbility') # BeamWeaponAbility inherits
        
        ship.layers[LayerType.INNER]['components'].append(comp)
        
        calc = ShipStatsCalculator(RegistryManager.instance().vehicle_classes)
        calc.calculate(ship)
        
        # Check 1: Energy
        assert 'energy' in ship.resources._resources
        
        # Check 2: Max Usage Calculation
        # Cost 5, unit per shot. Reload 0.2s.
        # Rate = 5 / 0.2 = 25.0 per sec.
        print(f"Energy Consump: {ship.energy_consumption}")
        assert ship.energy_consumption == 0.0, f"Expected 0.0 (inactive), got {ship.energy_consumption}"

        # NEW CHECK: potential_energy_consumption should be 25.0
        potential = getattr(ship, 'potential_energy_consumption', 0.0)
        print(f"Potential Energy: {potential}")
        assert potential == 25.0, f"Expected Potential 25.0, got {potential}"
        
        # Check 3: Rows
        rows = get_logistics_rows(ship)
        row_keys = [r.key for r in rows]
        assert "energy_max_usage" in row_keys

        # Check 4: Value from Row (Should use potential)
        max_row = next(r for r in rows if r.key == "energy_max_usage")
        val = max_row.get_value(ship)
        assert val == 25.0, f"Row Value Expected 25.0, got {val}"
    finally:
        teardown_test_state()

if __name__ == "__main__":
    try:
        print("Running tests...")
        test_shield_regen_consumption()
        print("test_shield_regen_consumption PASSED")
        test_laser_cannon_consumption()
        print("test_laser_cannon_consumption PASSED")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
