import unittest
import sys
import os
import pygame

# Add game directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, create_component, LayerType
from game.simulation.entities.ship_stats import ShipStatsCalculator

class TestBug09Endurance(unittest.TestCase):


    def setUp(self):
        pygame.init()
        # Initialize shared data
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))
        self.ship = Ship("EnduranceRepro", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.calculator = ShipStatsCalculator(self.ship.vehicle_classes if hasattr(self.ship, 'vehicle_classes') else {})
        print(f"[DEBUG] Ship Layers keys: {list(self.ship.layers.keys())}")

    def test_fuel_endurance_infinite(self):
        """
        Reproduce BUG-09: Fuel Endurance is infinite despite having engine and fuel.
        """
        # 1. Add Fuel Tank (Capacity)
        tank = create_component('fuel_tank')
        self.ship.add_component(tank, LayerType.INNER)

        # 2. Add Standard Engine (Consumption)
        engine = create_component('standard_engine')
        self.ship.add_component(engine, LayerType.OUTER)
        
        
        # 3. Recalculate Stats
        self.ship.recalculate_stats()
        
        # 4. Inpsect Results (Ship Stats)
        print(f"\n[DEBUG] Fuel Consumption (Ship Prop): {self.ship.fuel_consumption}")
        print(f"[DEBUG] Fuel Endurance (Ship Prop): {self.ship.fuel_endurance}")
        
        # 5. Inspect UI Logic (Stats Config)
        import ui.builder.stats_config as stats_config
        ui_consumption = stats_config.get_resource_consumption(self.ship, 'fuel')
        print(f"[DEBUG] Fuel Consumption (UI Getter): {ui_consumption}")
        
        calculated_endurance = self.ship.fuel_endurance
        formatted_str = stats_config.fmt_time(calculated_endurance)
        print(f"[DEBUG] Formatted String: {formatted_str}")
        
        # Test the getter used by the UI row
        # Row definition: getter=lambda s, n=r_name: get_resource_consumption(s, n)
        
        # ASSERTIONS
        # Consumption should be > 0 for a standard engine
        self.assertGreater(self.ship.fuel_consumption, 0, "Ship.fuel_consumption should be positive")
        self.assertGreater(ui_consumption, 0, "UI get_resource_consumption should be positive")
        
        # Endurance should be finite
        import math
        self.assertNotEqual(self.ship.fuel_endurance, float('inf'), "Fuel endurance should not be infinite")
        self.assertFalse(math.isinf(self.ship.fuel_endurance), "Fuel endurance is infinite")
        
        # CRITICAL REPRO: exact string match for 'Infinite' when it should be finite
        # If this assertion PASSES, we have reproduced the bug (that it says Infinite when it shouldn't)
        # Wait, usually we write tests that FAIL when the bug is present.
        # But here I want to CONFIRM it says Infinite.
        
        # Correct logic for "Fail if bug is present":
        # self.assertNotEqual(formatted_str, "Infinite", "Endurance showed 'Infinite' but should be finite time")
        
        self.assertNotEqual(formatted_str, "Infinite", "Stats Panel shows 'Infinite' for finite fuel endurance")

if __name__ == '__main__':
    unittest.main()
