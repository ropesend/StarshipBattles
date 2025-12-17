import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import load_components, get_all_components, create_component, COMPONENT_REGISTRY, Tank, Weapon

class TestComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure we load from the main directory
        # logic in components.py might assume CWD, so we might need to chdir or fix path in load_components if run from tests/
        # But load_components defaults to "components.json".
        # If we run from c:/Dev/Starship Battles, it's fine.
        load_components("components.json")

    def test_load_components(self):
        """Verify components.json is loaded correctly."""
        comps = get_all_components()
        self.assertGreater(len(comps), 0, "No components loaded")
        
        bridge = create_component('bridge')
        self.assertIsNotNone(bridge)
        self.assertEqual(bridge.name, "Bridge")
        self.assertEqual(bridge.mass, 50)

    def test_create_component_types(self):
        railgun = create_component('railgun')
        self.assertIsInstance(railgun, Weapon)
        self.assertEqual(railgun.damage, 40)
        
        tank = create_component('fuel_tank')
        self.assertIsInstance(tank, Tank)
        self.assertEqual(tank.resource_type, 'fuel')

if __name__ == '__main__':
    unittest.main()
