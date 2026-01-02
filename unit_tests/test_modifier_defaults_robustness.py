import unittest
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from components import load_components, load_modifiers, COMPONENT_REGISTRY, MODIFIER_REGISTRY, create_component
from ui.builder.modifier_logic import ModifierLogic

class TestModifierDefaultsRobustness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_modifiers()
        load_components()

    def test_railgun_defaults_robustness(self):
        """
        Verify that get_initial_value returns the BASE firing arc (1.0) 
        even if the component's runtime firing_arc has been modified/corrupted.
        """
        # 1. Get a Railgun
        if 'railgun' not in COMPONENT_REGISTRY:
            self.skipTest("Railgun not found in registry")
            
        comp = create_component('railgun')
        
        # Base value check (JSON should have 1)
        self.assertEqual(comp.data.get('firing_arc'), 1, "Base JSON firing_arc should be 1")
        
        # 2. Simulate the 'corruption' or modification
        # e.g. a previous modifier calc set it to 22.5 or 45
        comp.firing_arc = 22.5
        
        # 3. Ask Logic for initial value for Turret Mount
        # It should ignore the current 22.5 and return 1.0 from data
        initial_val = ModifierLogic.get_initial_value('turret_mount', comp)
        self.assertEqual(initial_val, 1.0, f"Expected 1.0 default, got {initial_val}")
        
    def test_pdc_defaults_robustness(self):
        """
        Verify PDC defaults (180) are robust against runtime changes.
        """
        if 'point_defence_cannon' not in COMPONENT_REGISTRY:
            self.skipTest("PDC not found")
            
        comp = create_component('point_defence_cannon')
        self.assertEqual(comp.data.get('firing_arc'), 180, "Base JSON firing_arc should be 180")
        
        # Simulate corruption
        comp.firing_arc = 90
        
        initial_val = ModifierLogic.get_initial_value('turret_mount', comp)
        self.assertEqual(initial_val, 180.0, f"Expected 180.0 default, got {initial_val}")
        
    def test_pdc_min_constraint_robustness(self):
        """
        Verify PDC minimum constraint respects the base hull limit (180).
        """
        comp = create_component('point_defence_cannon')
        
        # Simulate corruption
        comp.firing_arc = 90
        
        min_val, max_val = ModifierLogic.get_local_min_max('turret_mount', comp)
        self.assertEqual(min_val, 180.0, f"Expected min constraint 180.0, got {min_val}")

if __name__ == "__main__":
    unittest.main()
