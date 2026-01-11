"""
Integration tests for modifier stacking behavior.
Ensures identical components do NOT stack (MAX within stack_group),
but dissimilar components DO stack (MULTIPLY across stack_groups).
"""
import unittest

from game.simulation.components.component import Component, LayerType
from game.simulation.entities.ship import Ship


class TestStackingIntegration(unittest.TestCase):
    """Test that ship helper methods correctly use stack_group rules."""

    def setUp(self):
        self.ship = Ship("Test Ship", 0, 0, (255, 0, 0), ship_class="Cruiser")
        # Mock layers
        self.ship.layers[LayerType.OUTER] = {
            'components': [], 'radius_pct': 1.0, 'restrictions': [],
            'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100
        }
        self.ship.layers[LayerType.ARMOR] = {
            'components': [], 'radius_pct': 1.0, 'restrictions': [],
            'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100
        }

    def _make_comp(self, data):
        return Component(data)

    # =========================================================================
    # ToHitAttackModifier (Sensors) Tests
    # =========================================================================

    def test_get_total_sensor_score_identical_sensors_do_not_stack(self):
        """Two identical sensors (same stack_group) should NOT stack - only MAX counts."""
        sensor_data = {
            "id": "sensor_1", "name": "Sensor", "type": "Sensor",
            "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitAttackModifier": {"value": 2.0, "stack_group": "Sensor"}}
        }
        c1 = self._make_comp(sensor_data)
        c2 = self._make_comp(sensor_data)
        self.ship.add_component(c1, LayerType.OUTER)
        self.ship.add_component(c2, LayerType.OUTER)

        # Should be MAX(2.0, 2.0) = 2.0, NOT 2.0 + 2.0 = 4.0
        self.assertAlmostEqual(self.ship.get_total_sensor_score(), 2.0)

    def test_get_total_sensor_score_different_value_sensors_take_max(self):
        """Sensors with different values in same stack_group take MAX."""
        sensor1 = {
            "id": "sensor_1", "name": "Big Sensor", "type": "Sensor",
            "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitAttackModifier": {"value": 3.0, "stack_group": "Sensor"}}
        }
        sensor2 = {
            "id": "sensor_2", "name": "Small Sensor", "type": "Sensor",
            "mass": 5, "hp": 5, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitAttackModifier": {"value": 1.5, "stack_group": "Sensor"}}
        }
        self.ship.add_component(self._make_comp(sensor1), LayerType.OUTER)
        self.ship.add_component(self._make_comp(sensor2), LayerType.OUTER)

        # MAX(3.0, 1.5) = 3.0
        self.assertAlmostEqual(self.ship.get_total_sensor_score(), 3.0)

    # =========================================================================
    # ToHitDefenseModifier (ECM) Tests
    # =========================================================================

    def test_get_total_ecm_score_identical_ecm_do_not_stack(self):
        """Two identical ECM (same stack_group) should NOT stack - only MAX counts."""
        ecm_data = {
            "id": "ecm_1", "name": "ECM Suite", "type": "Electronics",
            "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitDefenseModifier": {"value": 1.0, "stack_group": "ECM"}}
        }
        c1 = self._make_comp(ecm_data)
        c2 = self._make_comp(ecm_data)
        self.ship.add_component(c1, LayerType.OUTER)
        self.ship.add_component(c2, LayerType.OUTER)

        # Should be MAX(1.0, 1.0) = 1.0, NOT 1.0 + 1.0 = 2.0
        self.assertAlmostEqual(self.ship.get_total_ecm_score(), 1.0)

    def test_different_defense_stack_groups_multiply(self):
        """ECM (stack_group: ECM) and Scattering Armor (stack_group: Scattering) should MULTIPLY."""
        ecm_data = {
            "id": "ecm_1", "name": "ECM Suite", "type": "Electronics",
            "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitDefenseModifier": {"value": 2.0, "stack_group": "ECM"}}
        }
        scattering_data = {
            "id": "scat_1", "name": "Scattering Armor", "type": "Armor",
            "mass": 10, "hp": 10, "allowed_layers": ["ARMOR"],
            "abilities": {"ToHitDefenseModifier": {"value": 1.5, "stack_group": "Scattering"}}
        }
        self.ship.add_component(self._make_comp(ecm_data), LayerType.OUTER)
        self.ship.add_component(self._make_comp(scattering_data), LayerType.ARMOR)

        # Different stack_groups: 2.0 * 1.5 = 3.0
        self.assertAlmostEqual(self.ship.get_total_ecm_score(), 3.0)

    # =========================================================================
    # Integration: baseline_to_hit_offense
    # =========================================================================

    def test_baseline_to_hit_offense_uses_stacking_rules(self):
        """The ship's baseline_to_hit_offense property should respect stack_group rules."""
        sensor_data = {
            "id": "sensor_1", "name": "Sensor", "type": "Sensor",
            "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitAttackModifier": {"value": 2.0, "stack_group": "Sensor"}}
        }
        c1 = self._make_comp(sensor_data)
        c2 = self._make_comp(sensor_data)
        self.ship.add_component(c1, LayerType.OUTER)
        self.ship.add_component(c2, LayerType.OUTER)

        # Should be 2.0 (MAX), not 4.0 (SUM)
        self.assertAlmostEqual(self.ship.baseline_to_hit_offense, 2.0)


if __name__ == '__main__':
    unittest.main()
