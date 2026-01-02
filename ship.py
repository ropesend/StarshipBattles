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
    Sensor, Electronics, Shield, ShieldRegenerator, SeekerWeapon,
    COMPONENT_REGISTRY, MODIFIER_REGISTRY
)
from logger import log_debug
from ship_validator import ShipDesignValidator, ValidationResult
from ship_stats import ShipStatsCalculator
from ship_physics import ShipPhysicsMixin
from ship_combat import ShipCombatMixin
from resources import ResourceRegistry

if TYPE_CHECKING:
    pass

# Module-level validator constant
_VALIDATOR = ShipDesignValidator()
# Deprecated global access for backward compatibility (lazy usage preferred)
VALIDATOR = _VALIDATOR 

# Load Vehicle Classes from JSON
VEHICLE_CLASSES: Dict[str, Any] = {}
SHIP_CLASSES: Dict[str, float] = {}  # Legacy compatibility - maps class name to max_mass

def load_vehicle_classes(filepath: str = "data/vehicleclasses.json", layers_filepath: Optional[str] = None) -> None:
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

    # Try to load layer definitions
    layer_definitions = {}
    
    if layers_filepath:
        layers_path = layers_filepath
    else:
        layers_path = os.path.join(os.path.dirname(filepath), "vehiclelayers.json")
        
    if os.path.exists(layers_path):
        try:
            with open(layers_path, 'r') as f:
                layer_data = json.load(f)
                layer_definitions = layer_data.get('definitions', {})
                print(f"Loaded {len(layer_definitions)} layer configurations from {os.path.basename(layers_path)}.")
        except Exception as e:
            print(f"Error loading layers from {layers_path}: {e}")
            
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Update in place to preserve references
            VEHICLE_CLASSES.clear()
            
            raw_classes = data.get('classes', {})
            
            # Post-process to resolve layer configurations
            for cls_name, cls_def in raw_classes.items():
                if 'layer_config' in cls_def:
                     config_id = cls_def['layer_config']
                     if config_id in layer_definitions:
                         cls_def['layers'] = layer_definitions[config_id]
                     else:
                         print(f"Warning: Class {cls_name} references unknown layer config {config_id}")
            
            VEHICLE_CLASSES.update(raw_classes)
            
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
        
        # Resources (New System)
        self.resources = ResourceRegistry()
        
        # Resource initialization tracking
        self._resources_initialized: bool = False
        
        self.baseline_to_hit_offense = 0.0 # Score
        self.to_hit_profile = 0.0 # Score
        self.total_defense_score = 0.0 # Score (Size + Maneuver + ECM)
        self.emissive_armor = 0
        self.crystalline_armor = 0
        
        # Shield Stats (Still specific for now)
        self.max_shields: int = 0
        self.current_shields: float = 0.0
        self.shield_regen_rate: float = 0.0
        self.shield_regen_cost: float = 0.0
        self.repair_rate: float = 0.0
        
        # New Stats
        self.mass_limits_ok: bool = True
        self.layer_status: Dict[LayerType, Dict[str, Any]] = {}
        self._loading_warnings: List[str] = []
        
        # Old init values
        self.current_mass: float = 0.0 
        
        self.is_alive: bool = True
        self.is_derelict: bool = False
        self.bridge_destroyed: bool = False
        
        # AI Strategy
        self.ai_strategy: str = "standard_ranged"
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
        self.comp_trigger_pulled: bool = False
        
        # Aiming
        self.aim_point: Optional[Any] = None
        self.just_fired_projectiles: List[Any] = []
        self.total_shots_fired: int = 0
        
        # To-Hit Calculation Stats
        self.to_hit_profile: float = 1.0       # Defensive Multiplier
        self.baseline_to_hit_offense: float = 1.0 # Offensive Multiplier
        
        # Initialize helper (lazy or eager)
        self.stats_calculator: Optional[ShipStatsCalculator] = None



    @property
    def max_hp(self) -> int:
        """Total HP of all components."""
        total = 0
        for layer in self.layers.values():
            for c in layer['components']:
                total += c.max_hp
        return total

    @property
    def hp(self) -> int:
        """Current HP of all components."""
        total = 0
        for layer in self.layers.values():
            for c in layer['components']:
                total += c.current_hp
        return total

    @property
    def max_weapon_range(self) -> float:
        """Calculate maximum range of all equipped weapons (Phase 4: ability-based with legacy fallback)."""
        from abilities import SeekerWeaponAbility
        max_rng = 0.0
        for layer in self.layers.values():
            for comp in layer['components']:
                # 1. Check WeaponAbility instances (new system)
                for ab in comp.get_abilities('WeaponAbility'):
                    rng = ab.range
                    # For SeekerWeapons, range is function of speed * endurance
                    if isinstance(ab, SeekerWeaponAbility):
                        rng = ab.projectile_speed * ab.endurance
                    if rng > max_rng:
                        max_rng = rng
                
                # 2. Fallback: Legacy Weapon components with direct range attribute
                if max_rng == 0.0 and hasattr(comp, 'range') and hasattr(comp, 'damage'):
                    rng = getattr(comp, 'range', 0)
                    if hasattr(comp, 'projectile_speed') and hasattr(comp, 'endurance'):
                        # SeekerWeapon fallback
                        rng = comp.projectile_speed * comp.endurance
                    if rng > max_rng:
                        max_rng = rng
        return max_rng if max_rng > 0 else 0.0

    def update(self, dt: float = 0.01, context: Optional[dict] = None) -> None:
        """
        Update ship state (physics, combat, resources).
        """
        if not self.is_alive:
            return

        # 1. Update Resources (Regeneration) - Tick-based
        if self.resources:
             self.resources.update()

        # 2. Update Components (Consumption, Cooldowns) - Tick-based
        for layer in self.layers.values():
            for comp in layer['components']:
                if comp.is_active:
                    comp.update()
        
        # 3. Physics (Thrust calc handling operational engines)
        self.update_physics_movement()
        
        # PhysicsBody.update() (Applies velocity to position)
        super().update(dt)
        
        # 4. Combat Cooldowns (Shields/Repair/Custom Logic)
        self.update_combat_cooldowns()

        # 5. Firing Logic (Link AI trigger to Combat System)
        if self.comp_trigger_pulled:
            new_attacks = self.fire_weapons(context)
            if new_attacks:
                self.just_fired_projectiles.extend(new_attacks)

    def update_derelict_status(self) -> None:
        """
        Update is_derelict status based on vehicle class requirements.
        If essential components (e.g. Bridge) are destroyed, ship becomes derelict.
        """
        # 1. Get Requirements
        class_def = VEHICLE_CLASSES.get(self.ship_class, {})
        requirements = class_def.get('requirements', {})
        
        # 2. If no requirements, never derelict (unless dead)
        if not requirements:
            self.is_derelict = False
            return

        # 3. Calculate Current Active Abilities
        active_components = []
        for layer in self.layers.values():
            for c in layer['components']:
                if c.is_active and c.current_hp > 0:
                     active_components.append(c)
        
        if not self.stats_calculator:
             self.stats_calculator = ShipStatsCalculator(VEHICLE_CLASSES)
             
        # Recalculate abilities based on currently living components
        totals = self.stats_calculator.calculate_ability_totals(active_components)
        
        # 4. Check Requirements
        is_derelict = False
        for req_ability, min_val in requirements.items():
            # Support boolean requirements (True means > 0)
            current_val = totals.get(req_ability, 0)
            
            if isinstance(min_val, bool):
                if min_val and not current_val:
                    is_derelict = True
                    break
            elif isinstance(min_val, (int, float)):
                 if current_val < min_val:
                     is_derelict = True
                     break
        
        if is_derelict and not self.is_derelict:
            print(f"{self.name} has become DERELICT (Requirements not met)")
            
        self.is_derelict = is_derelict

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
                
                # 2. If failed, try all other layers in the new ship
                if not added:
                    for layer_type in self.layers.keys():
                        if layer_type == old_layer: continue 
                        
                        if self.add_component(comp, layer_type):
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

    def add_components_bulk(self, component: Component, layer_type: LayerType, count: int) -> int:
        """
        Add multiple copies of a component to the specified layer.
        Performs validation for each addition but defers full ship stat recalculation until the end.
        Returns the number of components successfully added.
        """
        added_count = 0
        
        # Loop to add
        for _ in range(count):
            # Must clone for each new instance
            new_comp = component.clone()
            
            # Use the global validator
            result = _VALIDATOR.validate_addition(self, new_comp, layer_type)
            if not result.is_valid:
                # Stop adding if we hit a limit
                if added_count == 0:
                    # If the very first one fails, print errors
                    for err in result.errors:
                        print(f"Error: {err}")
                break
                
            self.layers[layer_type]['components'].append(new_comp)
            new_comp.layer_assigned = layer_type
            new_comp.ship = self
            new_comp.recalculate_stats()
            self.current_mass += new_comp.mass
            added_count += 1
            
        if added_count > 0:
            self.recalculate_stats()
            
        return added_count

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
    
    def get_total_ability_value(self, ability_name: str, operational_only: bool = True) -> float:
        """
        Sum values from all matching abilities across all components.
        Uses ability_instances (Phase 3+ API) instead of abilities dict.
        
        Args:
            ability_name: Name of ability class to sum (e.g., 'CombatPropulsion')
            operational_only: If True, only count abilities from operational components
            
        Returns:
            Sum of primary value attribute from all matching abilities
        """
        total = 0.0
        for layer in self.layers.values():
            for comp in layer['components']:
                if operational_only and not comp.is_operational:
                    continue
                for ab in comp.get_abilities(ability_name):
                    # Get the primary value attribute based on ability type
                    if hasattr(ab, 'thrust_force'):
                        total += ab.thrust_force
                    elif hasattr(ab, 'turn_rate'):
                        total += ab.turn_rate
                    elif hasattr(ab, 'capacity'):
                        total += ab.capacity
                    elif hasattr(ab, 'rate'):
                        total += ab.rate
                    elif hasattr(ab, 'value'):
                        total += ab.value
        return total
    
    def get_total_sensor_score(self) -> float:
        """Calculate total Targeting Score from all active sensors."""
        total_score = 0.0
        for layer in self.layers.values():
            for comp in layer['components']:
                if isinstance(comp, Sensor) and comp.is_active:
                     total_score += comp.attack_modifier
        return total_score

    def get_total_ecm_score(self) -> float:
        """Calculate total Evasion/Defense Score from all active ECM/Electronics."""
        total_score = 0.0
        for layer in self.layers.values():
            for comp in layer['components']:
                if isinstance(comp, Electronics) and comp.is_active:
                     total_score += comp.defense_modifier
                # Also include Armor passive defense (Scattering, Stealth)
                if isinstance(comp, Armor) and comp.is_active:
                     # Check for ToHitDefenseModifier ability which might be in generic abilities
                     # New Armor logic might have it in abilities dict directly
                     val = comp.abilities.get('ToHitDefenseModifier', None)
                     if val:
                         if isinstance(val, dict):
                             total_score += val.get('value', 0.0)
                         else:
                             total_score += float(val)
        return total_score

    def check_validity(self) -> bool:
        """Check if the current ship design is valid."""
        self.recalculate_stats()
        result = _VALIDATOR.validate_design(self)
        # Check for mass errors specifically for UI feedback flag
        self.mass_limits_ok = not any("Mass budget exceeded" in e for e in result.errors)
        return result.is_valid

    @property
    def layers_dict(self) -> Dict[str, List[Any]]:
        """Helper for JSON serialization."""
        d = {}
        for l_type, data in self.layers.items():
            d[l_type.name] = []
            for comp in data['components']:
                # Minimal serialization: ID + Modifiers
                c_data = {
                    "id": comp.id,
                    "modifiers": []
                }
                for m_id, m_val in comp.modifiers.items():
                    c_data["modifiers"].append({"id": m_id, "value": m_val})
                d[l_type.name].append(c_data)
        return d

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ship to dictionary."""
        data = {
            "name": self.name,
            "ship_class": self.ship_class,
            "theme_id": self.theme_id,
            "team_id": self.team_id,
            "color": self.color,
            "ai_strategy": self.ai_strategy,
            "layers": {},
            "expected_stats": {
                "max_hp": self.max_hp,
                "max_fuel": self.resources.get_max_value("fuel"),
                "max_energy": self.resources.get_max_value("energy"),
                "max_ammo": self.resources.get_max_value("ammo"),
                "max_speed": self.max_speed,
                "acceleration_rate": self.acceleration_rate,
                "turn_speed": self.turn_speed,
                "total_thrust": self.total_thrust,
                "mass": self.mass,
                "armor_hp_pool": self.layers[LayerType.ARMOR]['max_hp_pool'] if LayerType.ARMOR in self.layers else 0
            }
        }
        
        for ltype, layer_data in self.layers.items():
            filter_comps = []
            for comp in layer_data['components']:
                # Save as dict with modifiers
                c_obj = {"id": comp.id}
                if comp.modifiers:
                    c_obj["modifiers"] = [{"id": k, "value": v} for k, v in comp.modifiers.items()]
                filter_comps.append(c_obj)
                
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
        s.ai_strategy = data.get("ai_strategy", "standard_ranged")
        
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
            
            val = s.resources.get_max_value("fuel")
            if expected.get('max_fuel') and abs(val - expected['max_fuel']) > 1:
                mismatches.append(f"max_fuel: got {val}, expected {expected['max_fuel']}")
            
            val = s.resources.get_max_value("energy")
            if expected.get('max_energy') and abs(val - expected['max_energy']) > 1:
                mismatches.append(f"max_energy: got {val}, expected {expected['max_energy']}")
            
            val = s.resources.get_max_value("ammo")
            if expected.get('max_ammo') and abs(val - expected['max_ammo']) > 1:
                mismatches.append(f"max_ammo: got {val}, expected {expected['max_ammo']}")
            if expected.get('max_speed') and abs(s.max_speed - expected['max_speed']) > 0.1:
                mismatches.append(f"max_speed: got {s.max_speed:.1f}, expected {expected['max_speed']:.1f}")
            if expected.get('acceleration_rate') and abs(s.acceleration_rate - expected['acceleration_rate']) > 0.001:
                mismatches.append(f"acceleration_rate: got {s.acceleration_rate:.3f}, expected {expected['acceleration_rate']:.3f}")
            if expected.get('turn_speed') and abs(s.turn_speed - expected['turn_speed']) > 0.1:
                mismatches.append(f"turn_speed: got {s.turn_speed:.1f}, expected {expected['turn_speed']:.1f}")
            if expected.get('total_thrust') and abs(s.total_thrust - expected['total_thrust']) > 1:
                mismatches.append(f"total_thrust: got {s.total_thrust}, expected {expected['total_thrust']}")
            if expected.get('mass') and abs(s.mass - expected['mass']) > 1:
                mismatches.append(f"mass: got {s.mass}, expected {expected['mass']}")
            armor_hp = s.layers[LayerType.ARMOR]['max_hp_pool'] if LayerType.ARMOR in s.layers else 0
            if expected.get('armor_hp_pool') and abs(armor_hp - expected['armor_hp_pool']) > 1:
                mismatches.append(f"armor_hp_pool: got {armor_hp}, expected {expected['armor_hp_pool']}")
            
            s._loading_warnings = mismatches
            
            if mismatches:
                print(f"WARNING: Ship '{s.name}' stats mismatch after loading!")
                for m in mismatches:
                    print(f"  - {m}")
        
        return s


    @property
    def ammo_gen_rate(self) -> float:
        res = self.resources.get_resource("ammo")
        return res.regen_rate if res else 0.0

    @ammo_gen_rate.setter
    def ammo_gen_rate(self, value):
        res = self.resources.get_resource("ammo")
        if res: res.regen_rate = value
