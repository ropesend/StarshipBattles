import os
import json
from typing import List, Dict, Any, Optional
from ship import Ship, initialize_ship_data
from components import load_components, load_modifiers
import pygame

class CombatScenario:
    """
    Base class for defining a reproducible combat test scenario.
    """
    def __init__(self):
        self.name = "Base Scenario"
        self.description = "Base description"
        self.max_ticks = 1000  # Default timeout
        self.sim_speed = 1.0   # Default speed multiplier
        
        # Paths to specific data for this scenario. 
        # If None, uses default game data.
        self.components_path: Optional[str] = None
        self.modifiers_path: Optional[str] = None
        self.vehicle_classes_path: Optional[str] = None
        
        # Results storage
        self.passed = False
        self.results: Dict[str, Any] = {}

    def get_data_paths(self) -> Dict[str, str]:
        """
        Return dictionary of data paths to load before running this scenario.
        Keys: 'components', 'modifiers', 'vehicle_classes'
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        paths = {}
        if self.components_path:
            paths['components'] = self.components_path
        else:
            paths['components'] = os.path.join(base_dir, "data", "components.json")
            
        if self.modifiers_path:
            paths['modifiers'] = self.modifiers_path
        else:
            paths['modifiers'] = os.path.join(base_dir, "data", "modifiers.json")
            
        # Vehicle Classes often depend on a specific directory structure, 
        # so we allow overriding the base path passed to initialize_ship_data
        if self.vehicle_classes_path:
             paths['vehicle_classes'] = self.vehicle_classes_path
        else:
             paths['vehicle_classes'] = os.path.join(base_dir, "data", "vehicleclasses.json")
             
        return paths

    def setup(self, battle_engine):
        """
        Configure the battle engine with ships and initial state.
        Must be implemented by subclasses.
        """
        pass

    def update(self, battle_engine):
        """
        Called every tick. Use this for dynamic test logic 
        (e.g. "if tick == 100, spawn reinforcement").
        """
        pass

    def verify(self, battle_engine):
        """
        Check conditions and return True/False.
        Called at end of simulation or periodically if needed.
        """
        return True

    def create_ship(self, name: str, team_id: int, x: float, y: float, 
                   design_path: str = None, 
                   ship_class: str = "TestClass",
                   components: List[str] = None) -> Ship:
        """
        Helper to create a ship quickly.
        """
        # Create base ship
        color = (0, 0, 255) if team_id == 1 else (255, 0, 0)
        ship = Ship(name, x, y, color, team_id, ship_class=ship_class)
        
        # Use design file if provided
        if design_path:
            with open(design_path, 'r') as f:
                data = json.load(f)
            # Use static method if possible or re-instantiate
            # Since create_ship is usually custom, we might just load components differently
            # For now, let's stick to the manual component list for flexibility
            pass
            
        # Add basic components if list provided
        if components:
            from components import create_component, LayerType
            # Need a smarter way to install components to valid layers if "TestClass" isn't standard
            # Assume TestClass has a CORE or INNER
            
            # Use 'bridge' as default required core if layer exists
            # REMOVED: No hardcoded bridge. Scenarios must specify components explicitely.
            # if LayerType.CORE in ship.layers:
            #    ship.add_component(create_component('test_bridge_basic'), LayerType.CORE)
            
            # Add generator to first available internal layer
            # REMOVED: No hardcoded generator.
            # gen_layer = None
            # if LayerType.INNER in ship.layers: gen_layer = LayerType.INNER
            # elif LayerType.CORE in ship.layers: gen_layer = LayerType.CORE
            
            # if gen_layer:
            #    ship.add_component(create_component('test_gen_fusion'), gen_layer)
            
            for comp_id in components:
                # Try adding to various layers
                c = create_component(comp_id)
                if not c: continue
                
                # Intelligent placement attempt
                added = False
                # Try preferred layers first based on component type
                # (Simple heuristic)
                if c.type_str in ["Weapon", "ProjectileWeapon", "BeamWeapon", "Shield"]:
                     # Try Outer, then Inner
                     if LayerType.OUTER in ship.layers and ship.add_component(c, LayerType.OUTER): added = True
                     elif LayerType.INNER in ship.layers and ship.add_component(c, LayerType.INNER): added = True
                
                if not added:
                    # Fallback generic placement
                    for l_type in [LayerType.OUTER, LayerType.INNER, LayerType.CORE, LayerType.ARMOR]:
                        if l_type in ship.layers:
                             # Re-clone if we are retrying? No, add_component handles logic but validator might fail
                             # We need fresh clones if add_component consumes it? 
                             # add_component appends it. If it fails, it's not appended.
                             # But `add_component` modifies `c.layer_assigned`. 
                             # Safer to just try.
                             if ship.add_component(c, l_type):
                                 added = True
                                 break
        
        ship.recalculate_stats()
        ship.current_hp = ship.max_hp
        ship.current_energy = ship.max_energy
        ship.current_fuel = ship.max_fuel
        ship.current_ammo = ship.max_ammo
        
        return ship
