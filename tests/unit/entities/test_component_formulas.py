import pytest

from game.simulation.components.component import Component
from game.simulation.entities.ship import Ship


class MockShip:
    def __init__(self, max_mass):
        self.max_mass_budget = max_mass


class TestComponentFormulas:

    def test_mass_formula(self, fresh_registries):
        # Formula: M = 50 * sqrt(ClassMass / 1000)
        # 1000 -> 50 * 1 = 50
        # 4000 -> 50 * 2 = 100

        data = {
            "id": "test_comp",
            "name": "Test",
            "type": "Armor",
            "mass": "=50 * sqrt(ship_class_mass / 1000)",
            "hp": 100,
            "allowed_layers": ["ARMOR"],
            "allowed_vehicle_types": ["Ship"]
        }

        comp = Component(data, registries=fresh_registries)

        # Test Default Context (1000)
        comp.recalculate_stats()
        assert comp.mass == pytest.approx(50.0)

        # Test with Ship Context (4000)
        ship = MockShip(4000)
        comp.ship = ship
        comp.recalculate_stats()
        assert comp.mass == pytest.approx(100.0)

        # Test with Ship Context (16000) -> sqrt(16) = 4 -> 200
        ship.max_mass_budget = 16000
        comp.recalculate_stats()
        assert comp.mass == pytest.approx(200.0)

    def test_hp_formula(self, fresh_registries):
        # Formula: HP = floor(mass * 0.5) + 10
        # Let's say mass is 50 -> 25 + 10 = 35
        # Mass is 100 -> 50 + 10 = 60
        # Wait, can we reference self stats in formulas?
        # NOT YET IMPLEMENTED - Context only includes 'ship_class_mass' and math.
        # So we test direct formula: hp =ship_class_mass / 10

        data = {
            "id": "test_hp",
            "name": "TestHP",
            "type": "Armor",
            "mass": 10,
            "hp": "=ship_class_mass / 10",
            "allowed_layers": ["ARMOR"],
            "allowed_vehicle_types": ["Ship"]
        }

        comp = Component(data, registries=fresh_registries)
        ship = MockShip(500)
        comp.ship = ship

        comp.recalculate_stats()
        assert comp.max_hp == 50

        # Verify it cast to int (as per my code logic for HP)
        assert isinstance(comp.max_hp, int)
