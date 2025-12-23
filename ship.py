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
        
        # Layers
        self.layers = {
            LayerType.CORE:  {'components': [], 'radius_pct': 0.2, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0},
            LayerType.INNER: {'components': [], 'radius_pct': 0.5, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0},
            LayerType.OUTER: {'components': [], 'radius_pct': 0.8, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0},
            LayerType.ARMOR: {'components': [], 'radius_pct': 1.0, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0}
        }
        
        # Stats
        self.mass = 0
        # Get hull mass from vehicle class definition
        class_def = VEHICLE_CLASSES.get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})
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
        
        # Arcade Physics
        self.current_speed = 0
        self.acceleration_rate = 0
        self.is_thrusting = False
        
        # Aiming
        self.aim_point = None
        self.just_fired_projectiles = []
        self.total_shots_fired = 0
        
        # To-Hit Calculation Stats
        self.to_hit_profile = 1.0       # Defensive Multiplier (Lower is better for defender)
        self.baseline_to_hit_offense = 1.0 # Offensive Multiplier (Higher is better for attacker)

    def add_component(self, component: Component, layer_type: LayerType):
        if layer_type not in component.allowed_layers:
            print(f"Error: {component.name} not allowed in {layer_type}")
            return False

        if self.vehicle_type not in component.allowed_vehicle_types:
            print(f"Error: {component.name} not allowed on {self.vehicle_type}")
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
        
    def remove_component(self, layer_type: LayerType, index: int):
        if 0 <= index < len(self.layers[layer_type]['components']):
            comp = self.layers[layer_type]['components'].pop(index)
            self.current_mass -= comp.mass
            self.recalculate_stats()
            return comp
        return None

    def recalculate_stats(self):
        from components import LayerType, Engine, Thruster, Generator, Tank, Armor, Shield, ShieldRegenerator, ComponentStatus, Weapon
        
        # 1. Reset Base Calculations
        self.current_mass = 0
        self.layer_status = {}
        self.mass_limits_ok = True
        self.drag = 0.5 
        
        # Calculate Mass (Mass never changes due to damage/status in this model, dead weight remains)
        for layer_type, layer_data in self.layers.items():
            l_mass = sum(c.mass for c in layer_data['components'])
            layer_data['mass'] = l_mass
            self.current_mass += l_mass
            
        self.mass = self.current_mass + self.base_mass

        # Base Stats Reset
        self.total_thrust = 0
        self.turn_speed = 0
        self.max_fuel = 0
        self.max_ammo = 0
        self.max_energy = 0
        self.energy_gen_rate = 0
        self.max_shields = 0
        self.shield_regen_rate = 0
        self.shield_regen_cost = 0
        self.layers[LayerType.ARMOR]['max_hp_pool'] = 0
        
        # 2. Phase 1: Damage Check & Resource Supply Gathering
        # ----------------------------------------------------
        available_crew = 0     # From Crew Quarters
        available_life_support = 0 # From Life Support
        
        component_pool = [] # List of (comp, layer_type) for next phases
        
        for layer_type, layer_data in self.layers.items():
            for comp in layer_data['components']:
                # Reset Status Assumption
                comp.is_active = True
                comp.status = ComponentStatus.ACTIVE
                
                # Check Damage Threshold (ignore Armor)
                if not isinstance(comp, Armor):
                     if comp.max_hp > 0 and (comp.current_hp / comp.max_hp) <= 0.5:
                         comp.is_active = False
                         comp.status = ComponentStatus.DAMAGED
                
                # If armor is dead (0 hp), it's inactive (though armor usually works tll 0)
                if isinstance(comp, Armor) and comp.current_hp <= 0:
                    comp.is_active = False
                    comp.status = ComponentStatus.DAMAGED
                
                # Gather Supply from FUNCTIONAL components
                if comp.is_active:
                    abilities = comp.abilities
                    # Crew Provided (Positive CrewCapacity)
                    c_cap = abilities.get('CrewCapacity', 0)
                    if c_cap > 0:
                        available_crew += c_cap
                        
                    # Life Support Provided
                    ls_cap = abilities.get('LifeSupportCapacity', 0)
                    if ls_cap > 0:
                        available_life_support += ls_cap

                component_pool.append(comp)

        # 3. Phase 2: Resource Allocation (Crew & Life Support)
        # -----------------------------------------------------
        # Store for UI
        self.crew_onboard = available_crew
        self.crew_required = 0
        self.max_targets = 1 # Reset to default

        
        # Effective Crew is limited by Life Support
        effective_crew = min(available_crew, available_life_support)
        
        # Priority: Bridge > Engine > Weapon > Others
        def priority_sort(c):
            t = c.type_str
            # Bridge (Command)
            if t == "Bridge": return 0
            # Engines (Movement)
            if t == "Engine" or t == "Thruster": return 1
            # Weapons (Offense)
            if isinstance(c, Weapon): return 2
            # Others
            return 3
            
        component_pool.sort(key=priority_sort)
        
        for comp in component_pool:
            if not comp.is_active: continue # Already damaged
            
            # Check Crew Requirement (Use positive CrewRequired)
            req_crew = comp.abilities.get('CrewRequired', 0)
            
            # Satellite Exception: Satellites ignore crew requirements
            if self.vehicle_type == "Satellite":
                req_crew = 0
            
            # Legacy fallback: Check for negative CrewCapacity if CrewRequired missing
            # (Though we updated JSON, this is safe for any custom mods)
            if req_crew == 0:
                 req_crew = abs(min(0, comp.abilities.get('CrewCapacity', 0)))

            self.crew_required += req_crew
            
            if req_crew > 0:
                if effective_crew >= req_crew:
                    effective_crew -= req_crew
                else:
                    comp.is_active = False
                    comp.status = ComponentStatus.NO_CREW
        
        # 4. Phase 3: Stats Aggregation (Active Components Only)
        # ------------------------------------------------------
        # Also check for runtime resource starvations (No Fuel/Energy) if we simulate them here.
        # Note: Simulation of current_fuel vs max_fuel happens in update(), but we can flag stats here.
        
        for comp in component_pool:
            if not comp.is_active: continue
            
            if isinstance(comp, Engine):
                self.total_thrust += comp.thrust_force
            elif isinstance(comp, Thruster):
                self.turn_speed += comp.turn_speed
            elif isinstance(comp, Generator):
                self.energy_gen_rate += comp.energy_generation_rate
            elif isinstance(comp, Tank):
                if comp.resource_type == 'fuel':
                    self.max_fuel += comp.capacity
                elif comp.resource_type == 'ammo':
                    self.max_ammo += comp.capacity
                elif comp.resource_type == 'energy':
                    self.max_energy += comp.capacity
            elif isinstance(comp, Armor):
                # Armor contributes to pool regardless of active status generally, 
                # but we marked it inactive if 0 HP above.
                self.layers[LayerType.ARMOR]['max_hp_pool'] += comp.max_hp
            elif isinstance(comp, Shield):
                self.max_shields += comp.shield_capacity
            elif isinstance(comp, ShieldRegenerator):
                self.shield_regen_rate += comp.regen_rate
                self.shield_regen_cost += comp.energy_cost
            
            # Check for generic abilities that affect stats
            # MultiplexTracking
            mt = comp.abilities.get('MultiplexTracking', 0)
            if mt > 0:
                # We take the best tracking computer's val (or sum? implementation plan implied capability)
                # Let's say it doesn't stack, or stacks?
                # "Ability to target up to 10" implies replacing the default 1.
                # If we have 2 computers (10 each), do we get 20? 
                # Let's assume max(existing, new) or just overwrite if higher? 
                # Let's simple sum for now or max. Let's use max to avoid 100 targets.
                if mt > self.max_targets:
                    self.max_targets = mt


        # 5. Phase 4: Physics & Limits
        # ----------------------------
        
        # Derelict Check
        # Condition: No functional Bridge OR No functional Engines (Thrust <= 0)
        has_active_bridge = False
        for c in component_pool:
            if isinstance(c, Bridge) and c.is_active:
                has_active_bridge = True
                break
        
        if self.vehicle_type == "Satellite":
            if not has_active_bridge:
                self.is_derelict = True
            else:
                self.is_derelict = False
        else:
            if (not has_active_bridge) or (self.total_thrust <= 0):
                self.is_derelict = True
                self.total_thrust = 0 # Ensure 0
            else:
                self.is_derelict = False
        
        # Physics Stats - INVERSE MASS SCALING
        K_THRUST = 2500
        K_TURN = 25000
        
        if self.mass > 0:
            if self.is_derelict:
                self.acceleration_rate = 2.0 # Allow deceleration to stop
                self.turn_speed = 0
                self.max_speed = 0
            else:
                self.acceleration_rate = (self.total_thrust * K_THRUST) / (self.mass * self.mass)
                raw_turn_speed = self.turn_speed
                self.turn_speed = (raw_turn_speed * K_TURN) / (self.mass ** 1.5)
                
                K_SPEED = 25
                self.max_speed = (self.total_thrust * K_SPEED) / self.mass if self.total_thrust > 0 else 0
        else:
            self.acceleration_rate = 0
            self.max_speed = 0
            
        # Limit Checks (Budget)
        self.mass_limits_ok = True
        self.layer_limits = {
            LayerType.ARMOR: 0.30,
            LayerType.CORE: 0.30,
            LayerType.OUTER: 0.50,
            LayerType.INNER: 0.50
        }
        
        # Budget check (Max Mass)
        self.max_mass_budget = 1000 # Default
        from ship import SHIP_CLASSES
        if self.ship_class in SHIP_CLASSES:
             self.max_mass_budget = SHIP_CLASSES[self.ship_class]

        for layer_type, layer_data in self.layers.items():
            limit_ratio = self.layer_limits.get(layer_type, 1.0)
            ratio = layer_data['mass'] / self.max_mass_budget
            is_ok = ratio <= limit_ratio
            self.layer_status[layer_type] = {
                'mass': layer_data['mass'],
                'ratio': ratio,
                'limit': limit_ratio,
                'ok': is_ok
            }
            if not is_ok: self.mass_limits_ok = False
        
        if self.mass > self.max_mass_budget:
            self.mass_limits_ok = False
    
        # Radius Calculation
        base_radius = 40
        ref_mass = 1000
        actual_mass = max(self.mass, 100)
        ratio = actual_mass / ref_mass
        self.radius = base_radius * (ratio ** (1/3.0))

        # 6. Phase 5: To-Hit & Electronic Warfare Stats
        # ---------------------------------------------
        
        # Defensive Profile (Odds of being hit)
        # Factor 1: Size (Cross Section) - Diameter Squared
        # Normalized to a standard frigate/destroyer size (~80 diameter)
        diameter = self.radius * 2
        size_factor = (diameter / 80.0) ** 2
        
        # Factor 2: Maneuverability
        # Higher turn and acceleration reduces profile
        # Turn Speed is deg/s (e.g., 30-60), Accel is units/s^2 (e.g., 2-5)
        # Base denominator starts at 1.0
        maneuver_bonus = 1.0 + (self.turn_speed / 45.0) + (self.acceleration_rate / 4.0)
        maneuver_factor = 1.0 / maneuver_bonus
        
        # Factor 3: Electronic Defense (ECM)
        # This is multiplicative divisor (e.g. 2.0 defense mod = 0.5 odds to hit)
        defense_mods = self.get_ability_total('ToHitDefenseModifier')
        # If no defensive mods, default to 1.0 (no effect). 
        # get_ability_total returns 0 if not found for additive, but 1.0 for multiplicative? 
        # _calculate_ability_totals logic for multiplicative starts at 1.0 if key exists?
        # Let's check _calculate_ability_totals. It creates entry if it sees it.
        # But if no component has it, it returns 0 from .get().
        if defense_mods < 0.01: defense_mods = 1.0
        
        self.to_hit_profile = size_factor * maneuver_factor / defense_mods
        
        # Offensive Baseline (Sensor Strength)
        attack_mods = self.get_ability_total('ToHitAttackModifier')
        if attack_mods < 0.01: attack_mods = 1.0
        
        self.baseline_to_hit_offense = attack_mods

        # Armor Pool Init (if starting)
        if self.layers[LayerType.ARMOR]['hp_pool'] == 0:
            self.layers[LayerType.ARMOR]['hp_pool'] = self.layers[LayerType.ARMOR]['max_hp_pool']

        # Resource Initialization (Auto-fill on first load only, or when capacity increases)
        # Track previous max values to detect capacity increases
        prev_max_fuel = getattr(self, '_prev_max_fuel', 0)
        prev_max_ammo = getattr(self, '_prev_max_ammo', 0)
        prev_max_energy = getattr(self, '_prev_max_energy', 0)
        prev_max_shields = getattr(self, '_prev_max_shields', 0)
        
        if not self._resources_initialized:
            if self.max_fuel > 0:
                self.current_fuel = self.max_fuel
            if self.max_ammo > 0:
                self.current_ammo = self.max_ammo
            if self.max_energy > 0:
                self.current_energy = self.max_energy
            if self.max_shields > 0:
                self.current_shields = self.max_shields
            self._resources_initialized = True
        else:
            # Handle capacity increases from new components
            if self.max_fuel > prev_max_fuel:
                self.current_fuel += (self.max_fuel - prev_max_fuel)
            if self.max_ammo > prev_max_ammo:
                self.current_ammo += (self.max_ammo - prev_max_ammo)
            if self.max_energy > prev_max_energy:
                self.current_energy += (self.max_energy - prev_max_energy)
            if self.max_shields > prev_max_shields:
                self.current_shields += (self.max_shields - prev_max_shields)
        
        # Remember current max for next recalculate
        self._prev_max_fuel = self.max_fuel
        self._prev_max_ammo = self.max_ammo
        self._prev_max_energy = self.max_energy
        self._prev_max_shields = self.max_shields

    def get_missing_requirements(self):
        """Check class requirements and return list of missing items based on abilities."""
        missing = []
        class_def = VEHICLE_CLASSES.get(self.ship_class, {})
        requirements = class_def.get('requirements', {})
        
        # Gather all components
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        
        # Calculate ability totals from all components
        ability_totals = self._calculate_ability_totals(all_components)
        
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
    
    def _calculate_ability_totals(self, components):
        """Calculate total values for all abilities from components."""
        totals = {}
        
        # Abilities that should multiply instead of sum
        MULTIPLICATIVE_ABILITIES = {'ToHitAttackModifier', 'ToHitDefenseModifier'}
        
        for comp in components:
            abilities = getattr(comp, 'abilities', {})
            for ability_name, value in abilities.items():
                if isinstance(value, bool):
                    # Boolean abilities: any True makes total True
                    if value:
                        totals[ability_name] = True
                elif isinstance(value, (int, float)):
                    if ability_name in MULTIPLICATIVE_ABILITIES:
                        # Multiplicative abilities: multiply values together
                        totals[ability_name] = totals.get(ability_name, 1.0) * value
                    else:
                        # Additive abilities: sum values
                        totals[ability_name] = totals.get(ability_name, 0) + value
        
        return totals
    
    def _format_ability_name(self, ability_name):
        """Convert ability ID to readable name."""
        # Insert spaces before capitals and title case
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', ability_name)
    
    def get_ability_total(self, ability_name):
        """Get total value of a specific ability across all components."""
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        totals = self._calculate_ability_totals(all_components)
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
            for l in LayerType:
                if l.name == l_name:
                    layer_type = l
                    break
            
            if not layer_type: continue
            
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
            armor_hp = s.layers[LayerType.ARMOR]['max_hp_pool']  
            if expected.get('armor_hp_pool') and abs(armor_hp - expected['armor_hp_pool']) > 1:
                mismatches.append(f"armor_hp_pool: got {armor_hp}, expected {expected['armor_hp_pool']}")
            
            if mismatches:
                print(f"WARNING: Ship '{s.name}' stats mismatch after loading!")
                for m in mismatches:
                    print(f"  - {m}")
        
        return s



