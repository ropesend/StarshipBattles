
import sys
import os
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from game.simulation.entities.ship import Ship
from game.simulation.components.component import COMPONENT_REGISTRY, Component, load_components, load_modifiers
from game.simulation.entities.ship import Ship, load_vehicle_classes

class TestBug06CombatPropulsion:
    """
    Reproduction test for BUG-06: Combat Propulsion Validation Error.
    """

    @classmethod
    def setup_class(cls):
        # Initialize registries
        load_modifiers()
        # Ensure we point to the correct data directory relative to project root
        # Assuming test is run from project root, default paths work.
        # But force it just in case:
        import os
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        data_dir = os.path.join(base_dir, 'data')
        
        load_components(os.path.join(data_dir, 'components.json'))
        load_vehicle_classes(os.path.join(data_dir, 'vehicleclasses.json'))
        
        # Reload ship_stats to ensure changes are picked up
        import ship_stats
        import ship_validator
        import game.simulation.entities.ship
        import importlib
        importlib.reload(ship_stats)
        importlib.reload(ship_validator)
        importlib.reload(game.simulation.entities.ship)

    def test_combat_propulsion_validation(self):
        # Re-import Ship to get the refreshed class with fresh _VALIDATOR
        from game.simulation.entities.ship import Ship
        
        import traceback
        try:
            # 1. Create a minimal valid ship (Escort)
            ship = Ship(name="Test Ship", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
            
            # 2. Add required components to satisfy *other* requirements
            # Escort requires: CommandAndControl (Bridge), FuelStorage (Fuel Tank), CombatPropulsion (Engine)
            
            # Add Bridge (CommandAndControl)
            if "bridge" in COMPONENT_REGISTRY:
                bridge = COMPONENT_REGISTRY["bridge"].clone()
                layer_key = list(ship.layers.keys())[0] # CORE
                ship.add_component(bridge, layer_key)
            else:
                pytest.fail("Registry missing 'bridge' component")

            # Add Fuel Tank (FuelStorage)
            if "fuel_tank" in COMPONENT_REGISTRY:
                fuel = COMPONENT_REGISTRY["fuel_tank"].clone()
                layer_key = list(ship.layers.keys())[1] # INNER
                ship.add_component(fuel, layer_key)
            else:
                pytest.fail("Registry missing 'fuel_tank' component")
                
            # 3. Add Engine (CombatPropulsion) - The component under test
            if "standard_engine" in COMPONENT_REGISTRY:
                engine = COMPONENT_REGISTRY["standard_engine"].clone()
                # Standard engine provides "CombatPropulsion": 150
                layer_key = list(ship.layers.keys())[2] # OUTER
                ship.add_component(engine, layer_key)
            else:
                pytest.fail("Registry missing 'standard_engine' component")

            # 4. Validate
            # Force stats recalculation just to be sure
            ship.recalculate_stats()
            
            # Check requirements directly
            missing_reqs = ship.get_missing_requirements()
            
            # DEBUG: Print missing requirements if any
            if missing_reqs:
                print(f"\nMissing Requirements: {missing_reqs}")
                
            # 5. Assert uniqueness of failure
            # We expect NO "Needs Combat Propulsion" error.
            # Other errors (like Crew Housing) are expected since we didn't add Crew Quarters.
            
            errors = [str(e) for e in missing_reqs]
            combat_prop_errors = [e for e in errors if "Combat Propulsion" in e]
            
            if combat_prop_errors:
                pytest.fail(f"Validation failed with: {combat_prop_errors}")
                
            # Optional: Assert that we DO have other errors (sanity check that validation ran)
            # assert len(errors) > 0 
            
        except Exception:
            with open("traceback.txt", "w") as f:
                traceback.print_exc(file=f)
            raise
