import pytest
import sys
import os
sys.path.append(os.getcwd())

from game.core.registry import RegistryManager

@pytest.fixture(autouse=True)
def cleanup_registry():
    yield
    RegistryManager.instance().clear()

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component
from game.simulation.components.abilities import ResourceGeneration, ResourceStorage, ResourceConsumption, WeaponAbility
from ui.builder.stats_config import get_logistics_rows
from game.simulation.entities.ship_stats import ShipStatsCalculator

class MockClass:
    def __init__(self, data):
        self.data = data
    def get(self, key, default=None):
        return self.data.get(key, default)

def test_usage_only_visibility():
    """
    Ensure logistics rows appear even if a resource is ONLY used (no storage/gen).
    Scenario: Ship with just a Weapon consuming Energy.
    """
    # 1. Setup Ship and Registry
    from game.core.registry import RegistryManager
    mgr = RegistryManager.instance()
    mgr.vehicle_classes["TestClass"] = {'max_mass': 1000, 'type': 'Ship'}

    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")
    
    # Weapon: Consumes 5 Energy per activation, Reload 1.0s (Max Usage = 5.0/s)
    weapon = Component({"id": "laser", "name": "Laser", "mass": 10, "hp": 50, "type": "Internal"})
    weapon.ability_instances = [
        ResourceConsumption(weapon, {'resource': 'energy', 'amount': 5.0, 'trigger': 'activation'}),
        WeaponAbility(weapon, {'damage': 10, 'reload': 1.0}) 
    ]
    ship.layers[LayerType.INNER]['components'].append(weapon)

    # Calc stats
    calc = ShipStatsCalculator(mgr.vehicle_classes)
    calc.calculate(ship)

    rows = get_logistics_rows(ship)
    row_keys = [r.key for r in rows]
    
    # BUG: If logic skips when storage/gen/const=0 and max_use not calc'd correctly, these will be missing.
    assert "energy_max_usage" in row_keys, f"Energy rows missing for usage-only component. Keys: {row_keys}"
    assert "energy_endurance" in row_keys

def test_max_usage_calculation():
    """
    Verify Max Usage includes active weapon consumption correctly.
    Max Rate = Constant Usage + Sum(Weapon Cost / Reload Time)
    """
    # 1. Setup Ship and Registry
    from game.core.registry import RegistryManager
    mgr = RegistryManager.instance()
    mgr.vehicle_classes["TestClass"] = {'max_mass': 1000, 'type': 'Ship'}

    ship = Ship(name="TestShip2", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")

    # 1. Constant Draw: 2.0/s
    life_support = Component({"id": "ls", "name": "LifeSupport", "mass": 20, "hp": 50, "type": "Internal"})
    life_support.ability_instances = [ResourceConsumption(life_support, {'resource': 'energy', 'amount': 2.0, 'trigger': 'constant'})]
    ship.layers[LayerType.INNER]['components'].append(life_support)

    # 2. Weapon 1: 5.0 cost / 1.0s reload -> 5.0/s
    w1 = Component({"id": "w1", "name": "W1", "mass": 10, "hp": 50, "type": "Internal"})
    w1.ability_instances = [
        ResourceConsumption(w1, {'resource': 'energy', 'amount': 5.0, 'trigger': 'activation'}),
        WeaponAbility(w1, {'damage': 10, 'reload': 1.0}) 
    ]
    ship.layers[LayerType.INNER]['components'].append(w1)

    # 3. Weapon 2: 10.0 cost / 2.0s reload -> 5.0/s
    w2 = Component({"id": "w2", "name": "W2", "mass": 10, "hp": 50, "type": "Internal"})
    w2.ability_instances = [
        ResourceConsumption(w2, {'resource': 'energy', 'amount': 10.0, 'trigger': 'activation'}),
        WeaponAbility(w2, {'damage': 10, 'reload': 2.0}) 
    ]
    ship.layers[LayerType.INNER]['components'].append(w2)

    # Total Expected: 2.0 + 5.0 + 5.0 = 12.0
    
    calc = ShipStatsCalculator(mgr.vehicle_classes)
    calc.calculate(ship)

    rows = get_logistics_rows(ship)
    
    # Find the max usage row
    max_usage_val = 0
    found = False
    for r in rows:
        if r.key == 'energy_max_usage':
            max_usage_val = r.get_value(ship)
            found = True
            break
            
    assert found, "Energy Max Usage row not found"
    assert max_usage_val == 12.0, f"Expected 12.0 Max Usage, got {max_usage_val}"
