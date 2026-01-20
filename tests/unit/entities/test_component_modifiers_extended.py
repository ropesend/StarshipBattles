"""Extended tests for component modifier effects.

Tests modifier stacking and integration on actual components.
V1 handler tests removed in Phase 7 - those behaviors are now tested
via the V2 formula system in tests/unit/refactor/.
"""
import unittest

from game.simulation.components.component import load_components, load_modifiers, create_component
from tests.fixtures.paths import get_data_dir


class TestModifierStackingIntegration(unittest.TestCase):
    """Test modifier stacking on actual components."""

    def setUp(self):
        data_dir = get_data_dir()
        load_components(str(data_dir / "components.json"))
        load_modifiers(str(data_dir / "modifiers.json"))

    def test_range_mount_increases_component_mass(self):
        """Range mount modifier should increase component mass."""
        # Create base railgun
        railgun_base = create_component('railgun')
        base_mass = railgun_base.mass

        # Create railgun with range modifier
        railgun_range = create_component('railgun')
        railgun_range.add_modifier('range_mount', 1)
        railgun_range.recalculate_stats()

        # Range mount should increase mass
        self.assertGreater(railgun_range.mass, base_mass)

    def test_multiple_modifiers_order_independent(self):
        """Adding modifiers in different order should give same result."""
        # Create two weapons, add modifiers in different order
        w1 = create_component('railgun')
        w1.add_modifier('size_mount', 2)
        w1.add_modifier('range_mount', 1)
        w1.recalculate_stats()

        w2 = create_component('railgun')
        w2.add_modifier('range_mount', 1)
        w2.add_modifier('size_mount', 2)
        w2.recalculate_stats()

        self.assertEqual(w1.mass, w2.mass)
        self.assertEqual(w1.max_hp, w2.max_hp)


if __name__ == '__main__':
    unittest.main()
