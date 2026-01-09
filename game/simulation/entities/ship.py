import pygame
import random
import math
import json
import os
import typing
from typing import List, Dict, Tuple, Optional, Any, Union, Set, TYPE_CHECKING

from game.engine.physics import PhysicsBody
from game.simulation.components.component import (
    Component, LayerType, create_component
)
from game.core.logger import log_debug
from game.core.registry import RegistryManager, get_vehicle_classes, get_validator, get_component_registry, get_modifier_registry
from game.simulation.ship_validator import ShipDesignValidator, ValidationResult
from .ship_stats import ShipStatsCalculator
from .ship_physics import ShipPhysicsMixin
from .ship_combat import ShipCombatMixin
from game.simulation.systems.resource_manager import ResourceRegistry

if TYPE_CHECKING:
    pass

def get_or_create_validator():
    val = get_validator()
    if not val:
        val = ShipDesignValidator()
        RegistryManager.instance().set_validator(val)
    return val
 



def load_vehicle_classes(filepath: str = "data/vehicleclasses.json", layers_filepath: Optional[str] = None) -> None:
    """
    Load vehicle class definitions from JSON.
    This should be called explicitly during game initialization.
    """
    
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
            classes = get_vehicle_classes()
            classes.clear()
            
            raw_classes = data.get('classes', {})
            
            # Post-process to resolve layer configurations
            for cls_name, cls_def in raw_classes.items():
                if 'layer_config' in cls_def:
                     config_id = cls_def['layer_config']
                     if config_id in layer_definitions:
                         cls_def['layers'] = layer_definitions[config_id]
                     else:
                         print(f"Warning: Class {cls_name} references unknown layer config {config_id}")
            
            classes.update(raw_classes)
            

            print(f"Loaded {len(classes)} vehicle classes.")
    except FileNotFoundError:
        raise RuntimeError(f"Critical Error: {filepath} not found. Vehicle class data is required for game operation.")
        


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
        
        # Get class definition (no fallback - data must be present)
        class_def = get_vehicle_classes().get(self.ship_class, {})

        # Initialize Layers dynamically from class definition
        self._initialize_layers()
        
        # Auto-equip default Hull component if defined for this class
        default_hull_id = class_def.get('default_hull_id')
        hull_equipped = False
        if default_hull_id:
            hull_component = create_component(default_hull_id)
            if hull_component:
                # Direct append to avoid validation during init
                self.layers[LayerType.HULL]['components'].append(hull_component)
                hull_component.layer_assigned = LayerType.HULL
                hull_component.ship = self
                hull_equipped = True
        
        # Stats - Cached values (populated by ShipStatsCalculator.calculate())
        self._cached_mass: float = 0.0
        self._cached_max_hp: int = 0
        self._cached_hp: int = 0
        # base_mass is always 0.0 - Hull component provides all base mass via ShipStatsCalculator
        self.base_mass: float = 0.0
        self.vehicle_type: str = class_def.get('type', "Ship")
        self.total_thrust: float = 0.0
        self.max_speed: float = 0.0
        self.turn_speed: float = 0.0
        self.target_speed: float = 0.0 # New Target Speed Control
        
        # Budget
        self.max_mass_budget: float = class_def.get('max_mass', 1000)
        
        # Stats initialized to 0.0 - Recalculate will populate these
        self.current_mass: float = 0.0 
        self.radius: float = 0.0 
        
        # Resources (New System)
        from game.simulation.systems.resource_manager import ResourceRegistry
        self.resources = ResourceRegistry()
        
        # Resource initialization tracking
        self._resources_initialized: bool = False
        
        # To-Hit stats
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
        self._cached_summary = {}  # Performance optimization for UI
        self._loading_warnings: List[str] = []
        
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
    def mass(self) -> float:
        """Total mass (cached, updated by recalculate_stats)."""
        return self._cached_mass
    
    @mass.setter
    def mass(self, value: float) -> None:
        """Set cached mass value (used by ShipStatsCalculator and tests)."""
        self._cached_mass = value

    @property
    def max_hp(self) -> int:
        """Total HP of all components (cached, updated by recalculate_stats)."""
        return self._cached_max_hp
    
    @max_hp.setter
    def max_hp(self, value: int) -> None:
        """Set cached max_hp value."""
        self._cached_max_hp = value

    @property
    def hp(self) -> int:
        """Current HP of all components (cached, updated by recalculate_stats)."""
        return self._cached_hp
    
    @hp.setter
    def hp(self, value: int) -> None:
        """Set cached hp value."""
        self._cached_hp = value

    @property
    def max_weapon_range(self) -> float:
        """Calculate maximum range of all equipped weapons."""
        from game.simulation.components.abilities import SeekerWeaponAbility, WeaponAbility
        max_rng = 0.0
        for layer in self.layers.values():
            for comp in layer['components']:
                for ab in comp.ability_instances:
                    # Polymorphic check using isinstance (Phase 2 Task 2.5)
                    if not isinstance(ab, WeaponAbility):
                        continue
                    
                    rng = getattr(ab, 'range', 0.0)
                    # For SeekerWeapons, calculate range from endurance if not set
                    if isinstance(ab, SeekerWeaponAbility):
                        if rng <= 0 and hasattr(ab, 'projectile_speed') and hasattr(ab, 'endurance'):
                            rng = ab.projectile_speed * ab.endurance
                             
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
        Update derelict status based on CommandAndControl and CrewCapacity abilities.
        Ship becomes derelict when:
        1. No operational component has CommandAndControl ability (bridge destroyed)
        2. CrewRequired exceeds CrewCapacity (insufficient crew quarters)
        """
        # Check 1: CommandAndControl capability (essential for command)
        has_command = any(
            c.is_operational and c.has_ability('CommandAndControl')
            for layer in self.layers.values()
            for c in layer['components']
        )
        
        if not has_command:
            if not self.is_derelict:
                print(f"{self.name} has become DERELICT (Bridge destroyed)")
            self.is_derelict = True
            self.bridge_destroyed = True
            return
        
        # Check 2: Crew capacity (resource capability)
        crew_capacity = self.get_total_ability_value('CrewCapacity')
        crew_required = self.get_total_ability_value('CrewRequired')
        
        if crew_required > crew_capacity:
            if not self.is_derelict:
                print(f"{self.name} has become DERELICT (Insufficient crew capacity)")
            self.is_derelict = True
            return
        
        # All checks passed - ship is operational
        self.is_derelict = False
        self.bridge_destroyed = False

    def _initialize_layers(self) -> None:
        """Initialize or Re-initialize layers based on current ship_class."""
        class_def = get_vehicle_classes().get(self.ship_class, {})
        self.layers = {}
        layer_defs = class_def.get('layers', [])
        
        # Fallback if no layers defined in vehicle class
        if not layer_defs:
            layer_defs = [
                { "type": "CORE", "radius_pct": 0.2, "restrictions": [] },
                { "type": "INNER", "radius_pct": 0.5, "restrictions": [] },
                { "type": "OUTER", "radius_pct": 0.8, "restrictions": [] },
                { "type": "ARMOR", "radius_pct": 1.0, "restrictions": [] }
            ]
            
        # [NEW] Force HULL layer existence (Index 0)
        self.layers[LayerType.HULL] = {
            'components': [],
            'radius_pct': 0.0,
            'restrictions': ['HullOnly'],
            'max_mass_pct': 100.0,
            'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0
        }

        for l_def in layer_defs:
            l_type_str = l_def.get('type')
            try:
                l_type = LayerType[l_type_str]
                # Avoid overwriting HULL if it was somehow in data
                if l_type == LayerType.HULL: continue
                
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
        # Sort layers: HULL -> CORE -> INNER -> OUTER -> ARMOR
        layer_order = [LayerType.HULL, LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]
        
        # Filter layers present in this ship
        present_layers = [l for l in layer_order if l in self.layers]
        
        # Calculate total mass capacity (sum of max_mass_pct)
        # HULL is structural (radius 0), so excluded from area-proportional calculation
        total_capacity_pct = sum(self.layers[l]['max_mass_pct'] for l in present_layers if l != LayerType.HULL)
        
        if total_capacity_pct > 0:
            cumulative_mass_pct = 0.0
            for l_type in present_layers:
                if l_type == LayerType.HULL:
                    self.layers[l_type]['radius_pct'] = 0.0
                    continue
                cumulative_mass_pct += self.layers[l_type]['max_mass_pct']
                # Area = pi * r^2. Mass proportional to Area.
                self.layers[l_type]['radius_pct'] = math.sqrt(cumulative_mass_pct / total_capacity_pct)
        else:
            # Fallback if no mass limits defined
            pass

    def change_class(self, new_class: str, migrate_components: bool = False) -> None:
        """
        Change the ship class and optionally migrate components.
        
        Args:
            new_class: The new class name (e.g. "Cruiser")
            migrate_components: If True, attempts to keep components and fit them into new layers.
                                If False, clears all components.
        """
        if new_class not in get_vehicle_classes():
            print(f"Error: Unknown class {new_class}")
            return

        old_components = []
        if migrate_components:
            # Flatten all components with their original layer
            for l_type, data in self.layers.items():
                for comp in data['components']:
                    # DON'T migrate the hull! New class gets its own new hull.
                    # This matches the to_dict() logic and Task 2.1 intent.
                    if l_type == LayerType.HULL or comp.id.startswith('hull_'):
                        continue
                    old_components.append((comp, l_type))
        
        # Update Class
        self.ship_class = new_class
        class_def = get_vehicle_classes()[self.ship_class]
        self.base_mass = 0.0  # Hull component provides mass via ShipStatsCalculator
        self.vehicle_type = class_def.get('type', "Ship")
        self.max_mass_budget = class_def.get('max_mass', 1000)
        
        # Re-initialize Layers (clears self.layers)
        self._initialize_layers()
        
        # Auto-equip default Hull component for the NEW class (BUG-11 Fix)
        default_hull_id = class_def.get('default_hull_id')
        if default_hull_id:
            hull_component = create_component(default_hull_id)
            if hull_component:
                # Direct append to avoid validation during class change
                self.layers[LayerType.HULL]['components'].append(hull_component)
                hull_component.layer_assigned = LayerType.HULL
                hull_component.ship = self
        
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
        if component is None:
             print("Error: Attempted to add None component to ship")
             return False

        result = get_or_create_validator().validate_addition(self, component, layer_type)
        
        if not result.is_valid:
             for err in result.errors:
                 print(f"Error: {err}")
             return False

        self.layers[layer_type]['components'].append(component)
        component.layer_assigned = layer_type
        component.ship = self
        component.recalculate_stats()
        self._cached_summary = {}  # Invalidate cache
        
        # Update Stats
        self.recalculate_stats()
        return True

    @property
    def cached_summary(self):
        """Cached dictionary of high-level ship stats (DPS, Speed, etc)."""
        return self._cached_summary

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
            result = get_or_create_validator().validate_addition(self, new_comp, layer_type)
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
            added_count += 1
            
        if added_count > 0:
            self.recalculate_stats()
            
        return added_count

    def remove_component(self, layer_type: LayerType, index: int) -> Optional[Component]:
        """Remove a component from the specified layer by index."""
        if 0 <= index < len(self.layers[layer_type]['components']):
            comp = self.layers[layer_type]['components'].pop(index)
            self.recalculate_stats()
            return comp
        return None

    def recalculate_stats(self) -> None:
        """
        Recalculates derived stats. Delegates to ShipStatsCalculator.
        """
        # 1. Update components with current ship context
        for layer_data in self.layers.values():
            for comp in layer_data['components']:
                # Ensure ship ref is set
                if not getattr(comp, 'ship', None): comp.ship = self
                comp.recalculate_stats()

        if not self.stats_calculator:
             from .ship_stats import ShipStatsCalculator
             self.stats_calculator = ShipStatsCalculator(get_vehicle_classes())
        
        self.stats_calculator.calculate(self)

    def get_missing_requirements(self) -> List[str]:
        """Check class requirements and return list of missing items based on abilities."""
        # Use centralized validator
        result = get_or_create_validator().validate_design(self)
        if result.is_valid:
            return []
        # Return all errors as list of strings
        return [f"⚠ {err}" for err in result.errors]

    def get_validation_warnings(self) -> List[str]:
        """Check class requirements and return list of warnings (soft requirements)."""
        result = get_or_create_validator().validate_design(self)
        return result.warnings
    
    def _format_ability_name(self, ability_name: str) -> str:
        """Convert ability ID to readable name."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', ability_name)
    
    def get_ability_total(self, ability_name: str) -> Union[float, int, bool]:
        """Get total value of a specific ability across all components."""
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        
        if not self.stats_calculator:
             self.stats_calculator = ShipStatsCalculator(get_vehicle_classes())
             
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
                # Phase 7: Use ability-based check
                for ab in comp.get_abilities('ToHitAttackModifier'):
                    total_score += ab.value
        return total_score

    def get_total_ecm_score(self) -> float:
        """Calculate total Evasion/Defense Score from all active ECM/Electronics."""
        total_score = 0.0
        for layer in self.layers.values():
            for comp in layer['components']:
                # Phase 7: Use ability-based check
                for ab in comp.get_abilities('ToHitDefenseModifier'):
                    total_score += ab.value
        return total_score

    def check_validity(self) -> bool:
        """Check if the current ship design is valid."""
        self.recalculate_stats()
        result = get_or_create_validator().validate_design(self)
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
            "resources": {
                "fuel": self.resources.get_value("fuel"),
                "energy": self.resources.get_value("energy"),
                "ammo": self.resources.get_value("ammo"),
            },
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
            # [NEW] Skip HULL layer from explicit serialization
            if ltype == LayerType.HULL:
                continue
                
            filter_comps = []
            for comp in layer_data['components']:
                # Skip Hull components as safety (HULL layer already skipped)
                if comp.id.startswith('hull_'):
                    continue
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
                
            # Skip if this layer is not defined in the ship's class
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
                
                comps = get_component_registry()
                if comp_id in comps:
                    new_comp = comps[comp_id].clone()
                    
                    # Apply Modifiers
                    mods = get_modifier_registry()
                    for m_dat in modifiers_data:
                        mid = m_dat['id']
                        mval = m_dat['value']
                        if mid in mods:
                            new_comp.add_modifier(mid, mval)

                    s.add_component(new_comp, layer_type)
        
        s.recalculate_stats()
    
        # Restore resource values if saved
        saved_resources = data.get('resources', {})
        if saved_resources:
            for resource_name, value in saved_resources.items():
                if value is not None:
                    s.resources.set_value(resource_name, value)
        
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




    

