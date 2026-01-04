"""
Reproduction Test for BUG-10: Ship stats not updating for ammo/ordnance.
Uses 'Manual Headless Assembly' pattern for test isolation.
"""
import pytest
from game.simulation.entities.ship import Ship, LayerType, VEHICLE_CLASSES
from game.simulation.components.component import Component
from game.simulation.components.abilities import ResourceConsumption, WeaponAbility
from ui.builder.stats_config import get_logistics_rows
from ship_stats import ShipStatsCalculator


def _get_layer_key(ship, layer_name):
    """Robust lookup by name to handle potential Enum identity issues."""
    for k in ship.layers:
        if k.name == layer_name:
            return k
    return None


def test_ammo_usage_triggers_logistics_row():
    """
    Reproduction Test for BUG-10.
    Adding a component that consumes a resource (like a Railgun using Ammo)
    should trigger the display of that resource in the Logistics panel,
    even if there is no storage or generation for it yet.
    """
    # 1. Setup test-specific vehicle classes to ensure ship has expected layers
    test_vehicle_classes = {
        "TestClass": {
            "hull_mass": 50,
            "max_mass": 1000,
            "type": "Ship",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                {"type": "INNER", "radius_pct": 0.5, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.8, "restrictions": []},
                {"type": "ARMOR", "radius_pct": 1.0, "restrictions": []}
            ]
        }
    }
    
    # Temporarily set up VEHICLE_CLASSES for Ship initialization
    original_classes = dict(VEHICLE_CLASSES)
    VEHICLE_CLASSES.clear()
    VEHICLE_CLASSES.update(test_vehicle_classes)
    
    try:
        ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")
        
        # 2. Add a Weapon that uses Ammo
        # Railgun: Uses Ammo on activation
        railgun = Component({"id": "railgun", "name": "Railgun", "mass": 10, "hp": 50, "type": "Internal"})
        railgun.ability_instances = [
            ResourceConsumption(railgun, {'resource': 'ammo', 'amount': 1.0, 'trigger': 'activation'}),
            WeaponAbility(railgun, {'damage': 50, 'reload': 5.0, 'resource_cost': {'ammo': 1.0}}) 
        ]
        
        # Get layer key using robust lookup
        layer_key = _get_layer_key(ship, 'INNER')
        assert layer_key is not None, f"Ship should have INNER layer. Available: {[k.name for k in ship.layers]}"
        
        ship.layers[layer_key]['components'].append(railgun)
        railgun.ship = ship

        # 3. Calculate Stats
        calc = ShipStatsCalculator(test_vehicle_classes)
        calc.calculate(ship)
        
        # Debug: Check if consumption was calculated
        print(f"Ammo Consumption: {getattr(ship, 'ammo_consumption', 'N/A')}")
        print(f"Energy Consumption: {getattr(ship, 'energy_consumption', 'N/A')}")

        # 4. Get Logistics Rows
        rows = get_logistics_rows(ship)
        row_keys = [r.key for r in rows]
        print(f"Logistics Rows: {row_keys}")

        # 5. Assertions
        
        # Check Ammo Consumption Value
        # Railgun: Cost 1.0, Reload 5.0 -> 0.2 per second
        expected_rate = 0.2
        actual_rate = getattr(ship, 'ammo_consumption', 0)
        
        assert abs(actual_rate - expected_rate) < 0.001, f"Ammo consumption incorrect. Expected {expected_rate}, got {actual_rate}"

        # Check that ammo row appears in logistics
        has_ammo_row = any("ammo" in key for key in row_keys)
        assert has_ammo_row, "Logistics panel failed to show Ammo stats when Ammo consuming weapon is present."

        # Also test for Energy if we add a laser
        laser = Component({"id": "laser", "name": "Laser", "mass": 10, "hp": 50, "type": "Internal"})
        laser.ability_instances = [
            ResourceConsumption(laser, {'resource': 'energy', 'amount': 5.0, 'trigger': 'activation'}), 
            WeaponAbility(laser, {'damage': 10, 'reload': 2.0, 'resource_cost': {'energy': 5.0}})
        ]
        ship.layers[layer_key]['components'].append(laser)
        laser.ship = ship
        
        calc.calculate(ship)
        
        # Check Energy Consumption Value
        # Laser: Cost 5.0, Reload 2.0 -> 2.5 per second
        expected_energy_rate = 2.5
        actual_energy_rate = getattr(ship, 'energy_consumption', 0)
        assert abs(actual_energy_rate - expected_energy_rate) < 0.001, f"Energy consumption incorrect. Expected {expected_energy_rate}, got {actual_energy_rate}"

        rows = get_logistics_rows(ship)
        row_keys = [r.key for r in rows]
        
        has_energy_row = any("energy" in key for key in row_keys)
        assert has_energy_row, "Logistics panel failed to show Energy stats when Energy consuming weapon is present."
        
    finally:
        # Restore original classes to prevent pollution of subsequent tests
        VEHICLE_CLASSES.clear()
        VEHICLE_CLASSES.update(original_classes)
