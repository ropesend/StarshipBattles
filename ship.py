import pygame
import random
import math
import json
import os
import typing
from typing import List, Dict, Tuple, Optional, Any, Union, Set, TYPE_CHECKING

from physics import PhysicsBody
from components import (
    Component, LayerType, Bridge, Engine, Thruster, Tank, Armor, Weapon, 
    Generator, BeamWeapon, ProjectileWeapon, CrewQuarters, LifeSupport, 
    Sensor, Electronics, Shield, ShieldRegenerator,
    COMPONENT_REGISTRY, MODIFIER_REGISTRY
)
from logger import log_debug
from ship_validator import ShipDesignValidator, ValidationResult
from ship_stats import ShipStatsCalculator
from ship_physics import ShipPhysicsMixin
from ship_combat import ShipCombatMixin

if TYPE_CHECKING:
    pass

# Module-level validator constant
_VALIDATOR = ShipDesignValidator()
# Deprecated global access for backward compatibility (lazy usage preferred)
VALIDATOR = _VALIDATOR 

# Load Vehicle Classes from JSON
VEHICLE_CLASSES: Dict[str, Any] = {}
SHIP_CLASSES: Dict[str, float] = {}  # Legacy compatibility - maps class name to max_mass

def load_vehicle_classes(filepath: str = "data/vehicleclasses.json") -> None:
    """
    Load vehicle class definitions from JSON.
    This should be called explicitly during game initialization.
    """
    global VEHICLE_CLASSES, SHIP_CLASSES
    # Check if we need to resolve path relative to this file
    if not os.path.exists(filepath):
        # Try finding it relative to module
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)
        if os.path.exists(abs_path):
            filepath = abs_path
            
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Update in place to preserve references
            VEHICLE_CLASSES.clear()
            VEHICLE_CLASSES.update(data.get('classes', {}))
            
            # Build legacy SHIP_CLASSES dict for backward compatibility
            SHIP_CLASSES.clear()
            SHIP_CLASSES.update({name: cls['max_mass'] for name, cls in VEHICLE_CLASSES.items()})
            print(f"Loaded {len(VEHICLE_CLASSES)} vehicle classes.")
    except FileNotFoundError:
        print(f"Warning: {filepath} not found, using defaults")
        defaults = {
            "Escort": {"hull_mass": 50, "max_mass": 1000, "requirements": {}},
            "Frigate": {"hull_mass": 100, "max_mass": 2000, "requirements": {}},
            "Destroyer": {"hull_mass": 200, "max_mass": 4000, "requirements": {}},
            "Cruiser": {"hull_mass": 400, "max_mass": 8000, "requirements": {}},
            "Battlecruiser": {"hull_mass": 800, "max_mass": 16000, "requirements": {}},
            "Battleship": {"hull_mass": 1600, "max_mass": 32000, "requirements": {}},
            "Dreadnought": {"hull_mass": 3200, "max_mass": 64000, "requirements": {}}
        }
        VEHICLE_CLASSES.clear()
        VEHICLE_CLASSES.update(defaults)
        
        SHIP_CLASSES.clear()
        SHIP_CLASSES.update({name: cls['max_mass'] for name, cls in VEHICLE_CLASSES.items()})

def initialize_ship_data(base_path: Optional[str] = None) -> None:
    """Facade for initializing all ship-related data."""
    if base_path:
        path = os.path.join(base_path, "data", "vehicleclasses.json")
        load_vehicle_classes(path)
    else:
        load_vehicle_classes()

class Ship(PhysicsBody, ShipPhysicsMixin, ShipCombatMixin):
    def __init__(self, name: str, x: float, y: float, color: Union[Tuple[int, int, int], List[int]], 
                 team_id: int = 0, ship_class: str = "Escort", theme_id: str = "Federation"):
        super().__init__(x, y)
        self.name: str = name
        self.color: Union[Tuple[int, int, int], List[int]] = color
        self.team_id: int = team_id
        self.current_target: Optional[Any] = None
        self.secondary_targets: List[Any] = []  # List of additional targets
        self.max_targets: int = 1         # Default 1 target (primary only)
        self.ship_class: str = ship_class
        self.theme_id: str = theme_id
        
        # Get class definition
        class_def = VEHICLE_CLASSES.get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})

        # Initialize Layers dynamically from class definition
        self._initialize_layers()
        
        # Stats
        self.mass: float = 0.0
        self.base_mass: float = class_def.get('hull_mass', 50)  # Hull/Structure mass from class
        self.vehicle_type: str = class_def.get('type', "Ship")
        self.total_thrust: float = 0.0
        self.max_speed: float = 0.0
        self.turn_speed: float = 0.0
        self.target_speed: float = 0.0 # New Target Speed Control
        
        # Budget
        self.max_mass_budget: float = SHIP_CLASSES.get(self.ship_class, 1000)
        
        self.radius: float = 40.0 # Will be recalculated
        
        # Resources (Capacities and Current) - start at 0, recalculate_stats sets them
        self.max_energy: int = 0
        self.current_energy: float = 0.0
        self.max_fuel: int = 0
        self.current_fuel: float = 0.0
        self.max_ammo: int = 0
        self.current_ammo: int = 0
        self.energy_gen_rate: float = 0.0
        
        # Shield Stats
        self.max_shields: int = 0
        self.current_shields: float = 0.0
        self.shield_regen_rate: float = 0.0
        self.shield_regen_cost: float = 0.0
        
        # Resource initialization tracking
        self._resources_initialized: bool = False
        
        # New Stats
        self.mass_limits_ok: bool = True
        self.layer_status: Dict[LayerType, Dict[str, Any]] = {}
        
        # Old init values
        self.current_mass: float = 0.0 
        
        self.is_alive: bool = True
        self.is_derelict: bool = False
        self.bridge_destroyed: bool = False
        
        # AI Strategy
        self.ai_strategy: str = "optimal_firing_range"
        self.source_file: Optional[str] = None
        
        # Formation Attributes
        self.formation_master: Optional[Any] = None      # Reference to master ship object
        self.formation_offset: Optional[Any] = None      # Vector2 offset relative to master
        self.formation_rotation_mode: str = 'relative' # 'relative' or 'fixed'
        self.formation_members: List[Any] = []       # List of followers (if this is master)
        self.in_formation: bool = True          # Flag to track if ship is currently holding formation
        self.turn_throttle: float = 1.0          # Multiplier for max speed (0.0 to 1.0)
        self.engine_throttle: float = 1.0        # Multiplier for max speed (0.0 to 1.0)
        
        # Arcade Physics
        self.current_speed: float = 0.0
        self.acceleration_rate: float = 0.0
        self.is_thrusting: bool = False
        
        # Aiming
        self.aim_point: Optional[Any] = None
        self.just_fired_projectiles: List[Any] = []
        self.total_shots_fired: int = 0
        
        # To-Hit Calculation Stats
        self.to_hit_profile: float = 1.0       # Defensive Multiplier
        self.baseline_to_hit_offense: float = 1.0 # Offensive Multiplier
        
        # Initialize helper (lazy or eager)
        self.stats_calculator: Optional[ShipStatsCalculator] = None

    def _initialize_layers(self) -> None:
        """Initialize or Re-initialize layers based on current ship_class."""
        class_def = VEHICLE_CLASSES.get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})
        self.layers = {}
        layer_defs = class_def.get('layers', [])
        
        # Fallback if no layers defined (Legacy compatibility)
        if not layer_defs:
            layer_defs = [
                { "type": "CORE", "radius_pct": 0.2, "restrictions": [] },
                { "type": "INNER", "radius_pct": 0.5, "restrictions": [] },
                { "type": "OUTER", "radius_pct": 0.8, "restrictions": [] },
                { "type": "ARMOR", "radius_pct": 1.0, "restrictions": [] }
            ]
            
        for l_def in layer_defs:
            l_type_str = l_def.get('type')
            try:
                l_type = LayerType[l_type_str]
                self.layers[l_type] = {
                    'components': [],
                    'radius_pct': l_def.get('radius_pct', 0.5),
                    'restrictions': l_def.get('restrictions', []),
                    'max_mass_pct': l_def.get('max_mass_pct', 1.0),
                    'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0
                }
            except KeyError:
                print(f"Warning: Unknown LayerType {l_type_str} in class {self.ship_class}")

        # Recalculate layer radii based on max_mass_pct (Area proportional to mass capacity)
        # Sort layers: CORE -> INNER -> OUTER -> ARMOR
        layer_order = [LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]
        
        # Filter layers present in this ship
        present_layers = [l for l in layer_order if l in self.layers]
        
        # Calculate total mass capacity (sum of max_mass_pct)
        total_capacity_pct = sum(self.layers[l]['max_mass_pct'] for l in present_layers)
        
        if total_capacity_pct > 0:
            cumulative_mass_pct = 0.0
            for l_type in present_layers:
                cumulative_mass_pct += self.layers[l_type]['max_mass_pct']
                # Area = pi * r^2. Mass proportional to Area.
                # Mass_ratio = Current_Cumulative / Total
                # Radius_ratio = sqrt(Mass_ratio)
                self.layers[l_type]['radius_pct'] = math.sqrt(cumulative_mass_pct / total_capacity_pct)
        else:
            # Fallback if no mass limits defined (shouldn't happen with new data)
            pass

    def change_class(self, new_class: str, migrate_components: bool = False) -> None:
        """
        Change the ship class and optionally migrate components.
        
        Args:
            new_class: The new class name (e.g. "Cruiser")
            migrate_components: If True, attempts to keep components and fit them into new layers.
                                If False, clears all components.
        """
        if new_class not in VEHICLE_CLASSES:
            print(f"Error: Unknown class {new_class}")
            return

        old_components = []
        if migrate_components:
            # Flatten all components with their original layer
            for l_type, data in self.layers.items():
                for comp in data['components']:
                    old_components.append((comp, l_type))
        
        # Update Class
        self.ship_class = new_class
        class_def = VEHICLE_CLASSES[self.ship_class]
        self.base_mass = class_def.get('hull_mass', 50)
        self.vehicle_type = class_def.get('type', "Ship")
        self.max_mass_budget = class_def.get('max_mass', 1000)
        
        # Re-initialize Layers (clears self.layers)
        self._initialize_layers()
        self.current_mass = 0.0 # Reset mass accumulator
        
        if migrate_components:
            # Attempt to restore components
            for comp, old_layer in old_components:
                added = False
                
                # 1. Try original layer
                if old_layer in self.layers:
                    if self.add_component(comp, old_layer):
                         added = True
                
                # 2. If failed, try allowed layers for this component
                if not added:
                    # Sort allowed layers by preference? (e.g. Core -> Inner -> Outer)
                    # Just try all allowed that are present in ship
                    for allowed in comp.allowed_layers:
                        if allowed == old_layer: continue # Already tried
                        if allowed in self.layers:
                            if self.add_component(comp, allowed):
                                added = True
                                break
                
                if not added:
                    print(f"Warning: Could not fit component {comp.name} during refit to {new_class}")
        
        # Finally recalculate stats
        self.recalculate_stats()

    def add_component(self, component: Component, layer_type: LayerType) -> bool:
        """Validate and add a component to the specified layer."""
        result = _VALIDATOR.validate_addition(self, component, layer_type)
        
        if not result.is_valid:
             for err in result.errors:
                 print(f"Error: {err}")
             return False

        self.layers[layer_type]['components'].append(component)
        component.layer_assigned = layer_type
        component.ship = self
        component.recalculate_stats()
        self.current_mass += component.mass
        
        # Update Stats
        self.recalculate_stats()
        return True

    def remove_component(self, layer_type: LayerType, index: int) -> Optional[Component]:
        """Remove a component from the specified layer by index."""
        if 0 <= index < len(self.layers[layer_type]['components']):
            comp = self.layers[layer_type]['components'].pop(index)
            self.current_mass -= comp.mass
            self.recalculate_stats()
            return comp
        return None

    def recalculate_stats(self) -> None:
        """
        Recalculates derived stats. Delegates to ShipStatsCalculator.
        """
        # 1. Update Base Class Specs (ensure budget is fresh for scaling modifiers)
        if self.ship_class in VEHICLE_CLASSES:
             cdef = VEHICLE_CLASSES[self.ship_class]
             self.max_mass_budget = cdef.get('max_mass', 1000)

        # 2. Update components with current ship context
        for layer_data in self.layers.values():
            for comp in layer_data['components']:
                # Ensure ship ref is set (legacy check)
                if not getattr(comp, 'ship', None): comp.ship = self
                comp.recalculate_stats()

        if not self.stats_calculator:
             self.stats_calculator = ShipStatsCalculator(VEHICLE_CLASSES)
        
        self.stats_calculator.calculate(self)

    def get_missing_requirements(self) -> List[str]:
        """Check class requirements and return list of missing items based on abilities."""
        # Use centralized validator
        result = _VALIDATOR.validate_design(self)
        if result.is_valid:
            return []
        # Return all errors as list of strings
        return [f"⚠ {err}" for err in result.errors]

    def get_validation_warnings(self) -> List[str]:
        """Check class requirements and return list of warnings (soft requirements)."""
        result = _VALIDATOR.validate_design(self)
        return result.warnings
    
    def _format_ability_name(self, ability_name: str) -> str:
        """Convert ability ID to readable name."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', ability_name)
    
    def get_ability_total(self, ability_name: str) -> Union[float, int, bool]:
        """Get total value of a specific ability across all components."""
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        
        if not self.stats_calculator:
             self.stats_calculator = ShipStatsCalculator(VEHICLE_CLASSES)
             
        totals = self.stats_calculator.calculate_ability_totals(all_components)
        return totals.get(ability_name, 0)

    def check_validity(self) -> bool:
        """Check if the current ship design is valid."""
        self.recalculate_stats()
        result = _VALIDATOR.validate_design(self)
        # Check for mass errors specifically for UI feedback flag
        self.mass_limits_ok = not any("Mass budget exceeded" in e for e in result.errors)
        return result.is_valid

    @property
    def hp(self) -> int:
        return sum(c.current_hp for layer in self.layers.values() for c in layer['components'])

    @property
    def max_hp(self) -> int:
        return sum(c.max_hp for layer in self.layers.values() for c in layer['components'])

    @property
    def max_weapon_range(self) -> int:
        max_rng = 0
        for layer in self.layers.values():
            for comp in layer['components']:
                if isinstance(comp, Weapon) and comp.is_active:
                    if comp.range > max_rng:
                        max_rng = comp.range
        return max_rng

    def update(self, context: Optional[Dict[str, Any]] = None) -> None:
        if not self.is_alive: return

        # Delegate to Mixins
        self.update_combat_cooldowns()
        self.update_physics_movement()
        
        # Handle Firing
        self.just_fired_projectiles = []
        if getattr(self, 'comp_trigger_pulled', False):
             self.just_fired_projectiles = self.fire_weapons(context=context)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ship to dictionary."""
        # Recalculate stats to ensure they're current
        self.recalculate_stats()
        
        data = {
            "name": self.name,
            "color": self.color,
            "team_id": self.team_id,
            "ship_class": self.ship_class,
            "theme_id": getattr(self, 'theme_id', 'Federation'),
            "ai_strategy": self.ai_strategy,
            "layers": {},
            # Save expected stats for verification when loading
            "expected_stats": {
                "max_hp": self.max_hp,
                "max_fuel": self.max_fuel,
                "max_ammo": self.max_ammo,
                "max_energy": self.max_energy,
                "max_speed": self.max_speed,
                "turn_speed": self.turn_speed,
                "total_thrust": self.total_thrust,
                "mass": self.mass,
                "armor_hp_pool": self.layers[LayerType.ARMOR]['max_hp_pool'] if LayerType.ARMOR in self.layers else 0
            }
        }
        
        for ltype, layer_data in self.layers.items():
            filter_comps = []
            for c in layer_data['components']:
                # Save component ID and Modifiers
                c_data = {
                    "id": c.id,
                    "modifiers": []
                }
                for m in c.modifiers:
                    c_data['modifiers'].append({
                        "id": m.definition.id,
                        "value": m.value
                    })
                filter_comps.append(c_data)
                
            data["layers"][ltype.name] = filter_comps
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ship':
        """Create ship from dictionary."""
        name = data.get("name", "Unnamed")
        color_val = data.get("color", (200, 200, 200))
        # Ensure color is tuple
        color: tuple
        if isinstance(color_val, list): 
            color = tuple(color_val)
        else:
            color = color_val # type: ignore
        
        s = Ship(name, 0, 0, color, data.get("team_id", 0), ship_class=data.get("ship_class", "Escort"), theme_id=data.get("theme_id", "Federation"))
        s.ai_strategy = data.get("ai_strategy", "optimal_firing_range")
        
        for l_name, comps_list in data.get("layers", {}).items():
            layer_type = None
            try:
                layer_type = LayerType[l_name]
            except KeyError:
                continue
                
            # If ship definition doesn't have this layer, skip it (maybe legacy import)
            if layer_type not in s.layers:
                 continue
            
            for c_entry in comps_list:
                comp_id = ""
                modifiers_data = []
                
                if isinstance(c_entry, str):
                    comp_id = c_entry
                elif isinstance(c_entry, dict):
                    comp_id = c_entry.get("id", "")
                    modifiers_data = c_entry.get("modifiers", [])
                
                if comp_id in COMPONENT_REGISTRY:
                    new_comp = COMPONENT_REGISTRY[comp_id].clone()
                    
                    # Apply Modifiers
                    for m_dat in modifiers_data:
                        mid = m_dat['id']
                        mval = m_dat['value']
                        if mid in MODIFIER_REGISTRY:
                            new_comp.add_modifier(mid, mval)

                    s.add_component(new_comp, layer_type)
        
        s.recalculate_stats()
        
        # Verify loaded stats match expected stats (if saved)
        expected = data.get('expected_stats', {})
        if expected:
            mismatches = []
            if expected.get('max_hp') and abs(s.max_hp - expected['max_hp']) > 1:
                mismatches.append(f"max_hp: got {s.max_hp}, expected {expected['max_hp']}")
            if expected.get('max_fuel') and abs(s.max_fuel - expected['max_fuel']) > 1:
                mismatches.append(f"max_fuel: got {s.max_fuel}, expected {expected['max_fuel']}")
            if expected.get('max_energy') and abs(s.max_energy - expected['max_energy']) > 1:
                mismatches.append(f"max_energy: got {s.max_energy}, expected {expected['max_energy']}")
            if expected.get('max_ammo') and abs(s.max_ammo - expected['max_ammo']) > 1:
                mismatches.append(f"max_ammo: got {s.max_ammo}, expected {expected['max_ammo']}")
            if expected.get('max_speed') and abs(s.max_speed - expected['max_speed']) > 0.1:
                mismatches.append(f"max_speed: got {s.max_speed:.1f}, expected {expected['max_speed']:.1f}")
            if expected.get('turn_speed') and abs(s.turn_speed - expected['turn_speed']) > 0.1:
                mismatches.append(f"turn_speed: got {s.turn_speed:.1f}, expected {expected['turn_speed']:.1f}")
            if expected.get('total_thrust') and abs(s.total_thrust - expected['total_thrust']) > 1:
                mismatches.append(f"total_thrust: got {s.total_thrust}, expected {expected['total_thrust']}")
            if expected.get('mass') and abs(s.mass - expected['mass']) > 1:
                mismatches.append(f"mass: got {s.mass}, expected {expected['mass']}")
            armor_hp = s.layers[LayerType.ARMOR]['max_hp_pool'] if LayerType.ARMOR in s.layers else 0
            if expected.get('armor_hp_pool') and abs(armor_hp - expected['armor_hp_pool']) > 1:
                mismatches.append(f"armor_hp_pool: got {armor_hp}, expected {expected['armor_hp_pool']}")
            
            if mismatches:
                print(f"WARNING: Ship '{s.name}' stats mismatch after loading!")
                for m in mismatches:
                    print(f"  - {m}")
        
        return s
