import pygame
import random
import math
import json
import os
from physics import PhysicsBody
from components import Component, LayerType, Bridge, Engine, Thruster, Tank, Armor, Weapon, Generator, BeamWeapon, ProjectileWeapon, CrewQuarters, LifeSupport, Sensor, Electronics, Shield, ShieldRegenerator
from logger import log_debug


# Load Vehicle Classes from JSON
VEHICLE_CLASSES = {}
SHIP_CLASSES = {}  # Legacy compatibility - maps class name to max_mass

def load_vehicle_classes(filepath="data/vehicleclasses.json"):
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

def initialize_ship_data(base_path=None):
    """Facade for initializing all ship-related data."""
    if base_path:
        path = os.path.join(base_path, "data", "vehicleclasses.json")
        load_vehicle_classes(path)
    else:
        load_vehicle_classes()

from ship_physics import ShipPhysicsMixin
from ship_combat import ShipCombatMixin

class Ship(PhysicsBody, ShipPhysicsMixin, ShipCombatMixin):
    def __init__(self, name, x, y, color, team_id=0, ship_class="Escort", theme_id="Federation"):
        super().__init__(x, y)
        self.name = name
        self.color = color
        self.team_id = team_id
        self.current_target = None
        self.secondary_targets = []  # List of additional targets
        self.max_targets = 1         # Default 1 target (primary only)
        self.ship_class = ship_class
        self.theme_id = theme_id
        
        # Get class definition
        class_def = VEHICLE_CLASSES.get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})

        # Initialize Layers dynamically from class definition
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
                print(f"Warning: Unknown LayerType {l_type_str} in class {ship_class}")

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
            # Distribute evenly? Or keep json defaults? 
            # If total is 0, we can't do math. Let's trust JSON defaults if they exist, or linear.
            pass
        
        # Stats
        self.mass = 0
        self.base_mass = class_def.get('hull_mass', 50)  # Hull/Structure mass from class
        self.vehicle_type = class_def.get('type', "Ship")
        self.total_thrust = 0
        self.max_speed = 0
        self.turn_speed = 0
        self.target_speed = 0 # New Target Speed Control
        
        # Budget
        self.max_mass_budget = SHIP_CLASSES.get(self.ship_class, 1000)
        
        self.radius = 40 # Will be recalculated
        
        # Resources (Capacities and Current) - start at 0, recalculate_stats sets them
        self.max_energy = 0
        self.current_energy = 0
        self.max_fuel = 0
        self.current_fuel = 0
        self.max_ammo = 0
        self.current_ammo = 0
        self.energy_gen_rate = 0
        
        # Shield Stats
        self.max_shields = 0
        self.current_shields = 0
        self.shield_regen_rate = 0
        self.shield_regen_cost = 0
        
        # Resource initialization tracking (distinguish between "never set" and "depleted to 0")
        self._resources_initialized = False
        
        # New Stats (from old init, but now calculated or managed differently)
        self.mass_limits_ok = True
        self.layer_status = {}
        
        # Old init values, now calculated or managed differently
        self.current_mass = 0 # Replaced by self.mass and self.base_mass
        
        self.is_alive = True
        self.is_derelict = False
        self.bridge_destroyed = False
        
        # AI Strategy
        self.ai_strategy = "optimal_firing_range"  # See combatstrategies.json for options
        self.source_file = None  # Path to the JSON file this ship was loaded from
        
        # Formation Attributes
        self.formation_master = None      # Reference to master ship object
        self.formation_offset = None      # Vector2 offset relative to master
        self.formation_rotation_mode = 'relative' # 'relative' or 'fixed'
        self.formation_members = []       # List of followers (if this is master)
        self.in_formation = True          # Flag to track if ship is currently holding formation
        self.turn_throttle = 1.0          # Multiplier for max speed (0.0 to 1.0)
        self.engine_throttle = 1.0        # Multiplier for max speed (0.0 to 1.0)
        
        # Arcade Physics
        self.current_speed = 0
        self.acceleration_rate = 0
        self.is_thrusting = False
        self.turn_throttle = 1.0 # Multiplier for turn speed (formations)
        
        # Aiming
        self.aim_point = None
        self.just_fired_projectiles = []
        self.total_shots_fired = 0
        
        # To-Hit Calculation Stats
        self.to_hit_profile = 1.0       # Defensive Multiplier (Lower is better for defender)
        self.baseline_to_hit_offense = 1.0 # Offensive Multiplier (Higher is better for attacker)

    def add_component(self, component: Component, layer_type: LayerType):
        if layer_type not in self.layers:
             print(f"Error: Layer {layer_type.name} does not exist on {self.ship_class}")
             return False

        if layer_type not in component.allowed_layers:
            # Special case: If the vehicle class has restricted layers, maybe we should allow it if valid?
            # But component.allowed_layers is strict.
            print(f"Error: {component.name} not allowed in {layer_type.name} (Component restriction)")
            return False

        if self.vehicle_type not in component.allowed_vehicle_types:
            print(f"Error: {component.name} not allowed on {self.vehicle_type}")
            return False

        # Check Restrictions from Vehicle Class
        reason = self._check_restrictions(component, self.layers[layer_type]['restrictions'])
        if reason:
             print(f"Error: Restriction: {reason}")
             return False

        if self.mass_budget_exceeded(component.mass, layer_type):
            print(f"Error: Mass budget exceeded for {layer_type.name}")
            return False

        if self.current_mass + component.mass > self.max_mass_budget:
            print(f"Error: Mass budget exceeded for {self.name}")
            return False
            
        self.layers[layer_type]['components'].append(component)
        component.layer_assigned = layer_type
        self.current_mass += component.mass
        
        # Update Stats
        self.recalculate_stats()
        return True
        
    def _check_restrictions(self, component, restrictions):
        """
        Check if component is blocked by any restriction strings.
        Returns failure reason string or None if allowed.
        """
        for r in restrictions:
            if r.startswith("block_classification:"):
                blocked_class = r.split(":")[1]
                if component.data.get('major_classification') == blocked_class:
                    return f"Classification '{blocked_class}' blocked in this layer"
            elif r.startswith("block_type:"):
                blocked_type = r.split(":")[1]
                if component.type_str == blocked_type:
                     return f"Type '{blocked_type}' blocked in this layer"
            elif r.startswith("block_id:"):
                blocked_id = r.split(":")[1]
                if component.id == blocked_id:
                     return f"Component '{blocked_id}' blocked in this layer"
        return None
        
    def remove_component(self, layer_type: LayerType, index: int):
        if 0 <= index < len(self.layers[layer_type]['components']):
            comp = self.layers[layer_type]['components'].pop(index)
            self.current_mass -= comp.mass
            self.recalculate_stats()
            return comp
        return None

    def mass_budget_exceeded(self, component_mass, layer_type):
        if layer_type in self.layers:
            layer_data = self.layers[layer_type]
            current_layer_mass = sum(c.mass for c in layer_data['components'])
            max_layer_mass = self.max_mass_budget * layer_data.get('max_mass_pct', 1.0)
            
            if current_layer_mass + component_mass > max_layer_mass:
                return True
        return False

    def recalculate_stats(self):
        """
        Recalculates derived stats. Delegates to ShipStatsCalculator.
        """
        if not hasattr(self, 'stats_calculator'):
             from ship_stats import ShipStatsCalculator
             self.stats_calculator = ShipStatsCalculator(VEHICLE_CLASSES)
        
        self.stats_calculator.calculate(self)

    def get_missing_requirements(self):
        """Check class requirements and return list of missing items based on abilities."""
        missing = []
        class_def = VEHICLE_CLASSES.get(self.ship_class, {})
        requirements = class_def.get('requirements', {})
        
        # Gather all components
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        
        # Calculate ability totals from all components
        if not hasattr(self, 'stats_calculator'):
             from ship_stats import ShipStatsCalculator
             self.stats_calculator = ShipStatsCalculator(VEHICLE_CLASSES)
        ability_totals = self.stats_calculator.calculate_ability_totals(all_components)
        
        # Check each requirement
        for req_name, req_def in requirements.items():
            ability_name = req_def.get('ability', '')
            min_value = req_def.get('min_value', 0)
            
            if not ability_name:
                continue
            
            current_value = ability_totals.get(ability_name, 0)
            
            # Handle boolean abilities
            if isinstance(min_value, bool):
                if min_value and not current_value:
                    nice_name = self._format_ability_name(ability_name)
                    missing.append(f"⚠ Needs {nice_name}")
            # Handle numeric abilities
            elif isinstance(min_value, (int, float)):
                if current_value < min_value:
                    nice_name = self._format_ability_name(ability_name)
                    # Generic missing ability check
                    missing.append(f"⚠ Needs {nice_name}")
        
        # Additional crew/life support validation
        # CrewRequired is now explicit
        crew_capacity = ability_totals.get('CrewCapacity', 0)
        # Handle case where CrewCapacity might still be negative in some legacy data (safety)
        if crew_capacity < 0:
             crew_capacity = 0
             
        life_support = ability_totals.get('LifeSupportCapacity', 0)
        crew_required = ability_totals.get('CrewRequired', 0)
        
        # Add legacy negative capacity to required if present
        legacy_req = abs(min(0, ability_totals.get('CrewCapacity', 0)))
        crew_required += legacy_req
        
        # Check if we have enough housing for the required crew
        if crew_capacity < crew_required:
             missing.append(f"⚠ Need {crew_required - crew_capacity} more crew housing")

        # If we have crew requiring components but not enough life support
        if crew_required > 0 and life_support < crew_required:
            missing.append(f"⚠ Need {crew_required - life_support} more life support")
        
        return missing
    
    def _format_ability_name(self, ability_name):
        """Convert ability ID to readable name."""
        # Insert spaces before capitals and title case
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', ability_name)
    
    def get_ability_total(self, ability_name):
        """Get total value of a specific ability across all components."""
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        
        if not hasattr(self, 'stats_calculator'):
             from ship_stats import ShipStatsCalculator
             self.stats_calculator = ShipStatsCalculator(VEHICLE_CLASSES)
             
        totals = self.stats_calculator.calculate_ability_totals(all_components)
        return totals.get(ability_name, 0)

    def check_validity(self):
        self.recalculate_stats()
        # Check requirements too
        if self.get_missing_requirements():
            return False
        return self.mass_limits_ok

    @property
    def hp(self):
        return sum(c.current_hp for layer in self.layers.values() for c in layer['components'])

    @property
    def max_hp(self):
        return sum(c.max_hp for layer in self.layers.values() for c in layer['components'])

    @property
    def max_weapon_range(self):
        max_rng = 0
        for layer in self.layers.values():
            for comp in layer['components']:
                if isinstance(comp, Weapon) and comp.is_active:
                    if comp.range > max_rng:
                        max_rng = comp.range
        return max_rng

    def update(self, context=None):
        if not self.is_alive: return

        # Delegate to Mixins
        self.update_combat_cooldowns()
        self.update_physics_movement()
        
        # Handle Firing
        self.just_fired_projectiles = []
        if getattr(self, 'comp_trigger_pulled', False):
             self.just_fired_projectiles = self.fire_weapons(context=context)

    def to_dict(self):
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
                "armor_hp_pool": self.layers[LayerType.ARMOR]['max_hp_pool']
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
    def from_dict(data):
        """Create ship from dictionary."""
        name = data.get("name", "Unnamed")
        color = data.get("color", (200, 200, 200))
        # Ensure color is tuple
        if isinstance(color, list): color = tuple(color)
        
        s = Ship(name, 0, 0, color, data.get("team_id", 0), ship_class=data.get("ship_class", "Escort"), theme_id=data.get("theme_id", "Federation"))
        s.ai_strategy = data.get("ai_strategy", "optimal_firing_range")
        
        from components import COMPONENT_REGISTRY, MODIFIER_REGISTRY
        
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
                    comp_id = c_entry.get("id")
                    modifiers_data = c_entry.get("modifiers", [])
                
                if comp_id in COMPONENT_REGISTRY:
                    new_comp = COMPONENT_REGISTRY[comp_id].clone()
                    
                    # Apply Modifiers
                    for m_dat in modifiers_data:
                        mid = m_dat['id']
                        mval = m_dat['value']
                        if mid in MODIFIER_REGISTRY:
                            new_comp.add_modifier(mid, mval)
                            
                    if isinstance(new_comp, Weapon):
                        # Use logger if needed, but avoid circular import if possible or lazy import
                        pass
                             
                    # Use add_component to validate and add
                    # But suppress errors if loading? No, we might want to know if invalid load.
                    # But for now, direct add might be cleaner IF we trust save data?
                    # No, use add_component to ensure consistency with new restrictions
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
