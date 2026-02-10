"""
Deep reproduction tests for BUG-05: Energy consumption rows in logistics UI.

Updated for PROJ-50 (Strict DI) - uses fresh_registries fixture.
"""
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.ui.screens.builder.stats_config import get_logistics_rows
from game.simulation.entities.layer_data import LayerData

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
        "ResourceConsumption": [{"resource": "energy", "amount": 2.0, "trigger": "constant"}]
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
            "reload": 0.2,  # Rate = 5 / 0.2 = 25/s
            "damage": 10
        }
    }
}


def test_shield_regen_consumption(fresh_registries):
    """
    Verify Shield Regen (using ResourceConsumption)
    1. Registers Energy resource
    2. Calculates correctly in ship.energy_consumption
    3. Shows up in Logistics Rows
    """
    # Setup test vehicle class
    fresh_registries.vehicle_classes["TestClass"] = {'max_mass': 1000, 'type': 'Ship'}

    ship = Ship(
        name="TestShipSC",
        x=0, y=0,
        color=(255, 255, 255),
        ship_class="TestClass",
        registries=fresh_registries
    )

    # Create Component from Dict (simulating load_components)
    comp = Component(MOCK_SHIELD_REGEN_DATA, registries=fresh_registries)
    ship.layers[LayerType.INNER].components.append(comp)

    calc = ShipStatsCalculator(fresh_registries.vehicle_classes)
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

    assert "energy_max_usage" in row_keys, f"Energy Max Usage row missing. Found: {row_keys}"

    # Check Values
    max_use_row = next(r for r in rows if r.key == 'energy_max_usage')
    val = max_use_row.get_value(ship)
    print(f"Max Usage Row Value: {val}")
    assert val == ship.energy_consumption


def test_laser_cannon_consumption(fresh_registries):
    """
    Verify Laser Cannon (Active Consumption)
    1. Registers Energy resource
    2. Calculates max usage (activation rate)
    3. Shows up in Logistics Rows
    """
    # Setup test vehicle class
    fresh_registries.vehicle_classes["TestClass"] = {'max_mass': 1000, 'type': 'Ship'}

    ship = Ship(
        name="TestShipLC",
        x=0, y=0,
        color=(255, 255, 255),
        ship_class="TestClass",
        registries=fresh_registries
    )

    comp = Component(MOCK_LASER_DATA, registries=fresh_registries)
    comp.debug_log = True
    # Ensure correct instantiation of abilities
    assert comp.has_ability('ResourceConsumption')
    assert comp.has_ability('WeaponAbility')  # BeamWeaponAbility inherits

    ship.layers[LayerType.INNER].components.append(comp)

    calc = ShipStatsCalculator(fresh_registries.vehicle_classes)
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
    assert "energy_max_usage" in row_keys, f"Energy Max Usage row missing. Found: {row_keys}"

    # Check 4: Value from Row (Should use potential)
    max_row = next(r for r in rows if r.key == "energy_max_usage")
    val = max_row.get_value(ship)
    assert val == 25.0, f"Row Value Expected 25.0, got {val}"
