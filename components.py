import json
import math
from enum import Enum, auto
from formula_system import evaluate_math_formula

class ComponentStatus(Enum):
    ACTIVE = auto()
    DAMAGED = auto() # >50% damage
    NO_CREW = auto()
    NO_POWER = auto()
    NO_FUEL = auto()
    NO_AMMO = auto()

class LayerType(Enum):
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4

    @staticmethod
    def from_string(s):
        return getattr(LayerType, s.upper())

class Modifier:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type_str = data['type'] # 'boolean' or 'linear'
        self.description = data.get('description', '')
        self.effects = data.get('effects', {})
        self.restrictions = data.get('restrictions', {})
        self.param_name = data.get('param_name', 'value')
        self.min_val = data.get('min_val', 0)
        self.max_val = data.get('max_val', 100)
        self.default_val = data.get('default_val', self.min_val)
        self.readonly = data.get('readonly', False)

    def create_modifier(self, value=None):
        return ApplicationModifier(self, value)

MODIFIER_REGISTRY = {}

class ApplicationModifier:
    """Instance of a modifier applied to a component"""
    def __init__(self, mod_def, value=None):
        self.definition = mod_def
        self.value = value if value is not None else mod_def.default_val

from resources import ABILITY_REGISTRY, create_ability

class Component:
    def __init__(self, data):
        import copy
        self.data = copy.deepcopy(data) # Store raw data for reference/cloning
        self.id = data['id']
        self.name = data['name']
        self.base_mass = data['mass']
        self.mass = self.base_mass
        self.base_max_hp = data['hp']
        self.max_hp = self.base_max_hp
        self.current_hp = self.max_hp
        # allowed_layers removed in refactor
        # self.allowed_layers = [LayerType.from_string(l) for l in data['allowed_layers']]
        self.allowed_vehicle_types = data.get('allowed_vehicle_types', ["Ship"])
        self.major_classification = data.get('major_classification', "Unknown")
        self.is_active = True
        self.status = ComponentStatus.ACTIVE
        self.layer_assigned = None
        self.type_str = data['type']
        self.sprite_index = data.get('sprite_index', 0)
        self.cost = data.get('cost', 0)
        
        # Parse abilities from data
        self.abilities = self.data.get('abilities', {})
        self.base_abilities = copy.deepcopy(self.abilities)
        
        self.ship = None # Container reference
        
        self.stats = {} # Current stats dictionary (calcualted)
        self.modifiers = [] # list of ApplicationModifier
        
        # Ability Instances (New System)
        self.ability_instances = []
        self._is_operational = True # Tracks if component has resources to operate
        
        # Instantiate Abilities
        self._instantiate_abilities()
        
        # Load default modifiers from data definition
        if 'modifiers' in self.data:
            for mod_data in self.data['modifiers']:
                mod_id = mod_data['id']
                val = mod_data.get('value', None)
                # We need to access registry. BUT registry might not be fully loaded if simple import.
                # Assuming MODIFIER_REGISTRY is populated by load_modifiers globally.
                from components import MODIFIER_REGISTRY
                if mod_id in MODIFIER_REGISTRY:
                    mod_def = MODIFIER_REGISTRY[mod_id]
                    self.modifiers.append(mod_def.create_modifier(val))
                else:
                    # If modifiers loaded later, this might fail. 
                    # Ideally modifiers are loaded before components.
                    pass
                    
        # Parse Formulas
        self.formulas = {}
        for key, value in self.data.items():
            if isinstance(value, str) and value.startswith("="):
                # It's a formula!
                self.formulas[key] = value[1:] # Store without '='
                # Initialize base value to something safe? Or keep it as is?
                # Probably keep undefined or 0 until recalculated? 
                # Better to set a default if possible, but hard to guess.
                # If it's mass/hp, 0 is safer than crashing.
                if key in ['mass', 'hp', 'damage', 'range', 'cost']:
                     setattr(self, f"base_{key}" if key in ['mass', 'hp'] else key, 0)
                     if key == 'mass': self.mass = 0
                     if key == 'hp': 
                         self.max_hp = 0
                         self.current_hp = 0

    def get_abilities(self, ability_name: str):
        """
        Get all abilities of a specific type (by registry name).
        Supports polymorphism if the registry entry is a class.
        """
        from abilities import ABILITY_REGISTRY
        
        target_class = None
        if ability_name in ABILITY_REGISTRY:
            val = ABILITY_REGISTRY[ability_name]
            if isinstance(val, type):
                target_class = val
        
        found = []
        for ab in self.ability_instances:
            # 1. Polymorphic check (preferred)
            if target_class and isinstance(ab, target_class):
                found.append(ab)
            # 2. Name check (fallback)
            elif ab.__class__.__name__ == ability_name:
                found.append(ab)
        return found

    def get_ability(self, ability_name: str):
        """Get first ability of type."""
        l = self.get_abilities(ability_name)
        return l[0] if l else None

    def has_ability(self, ability_name: str):
        """Check if component has ability."""
        return len(self.get_abilities(ability_name)) > 0

    def has_pdc_ability(self) -> bool:
        """Check if component has a Point Defense weapon ability.
        
        Supports both:
        - New system: 'pdc' in ability.tags
        - Legacy system: abilities.get('PointDefense', False)
        """
        # 1. Check new tag-based system
        for ab in self.ability_instances:
            if 'pdc' in ab.tags:
                return True
        
        # 2. Backward compatibility: check legacy abilities dict
        if self.abilities.get('PointDefense', False):
            return True
            
        return False

    def get_ui_rows(self):
        """Aggregate UI rows from all ability instances.
        
        Returns list of dicts: [{'label': 'Thrust', 'value': '1500 N'}, ...]
        Used by detail panels and capability scanners.
        """
        rows = []
        for ab in self.ability_instances:
            rows.extend(ab.get_ui_rows())
        return rows

    def _instantiate_abilities(self):
        """Instantiate Ability objects from self.abilities dict."""
        self.ability_instances = []
        
        # Standard Loading from abilities dict
        for name, data in self.abilities.items():
            if name not in ABILITY_REGISTRY:
                continue
            if isinstance(data, list):
                for item in data:
                    ab = create_ability(name, self, item)
                    if ab: self.ability_instances.append(ab)
            elif isinstance(data, dict) or isinstance(data, (int, float)):
                 ab = create_ability(name, self, data)
                 if ab: self.ability_instances.append(ab)
            
    def update(self):
        """Update component state for one tick (resource consumption, cooldowns)."""
        # 1. Update Abilities (Constant Consumption)
        all_satisfied = True
        
        for ability in self.ability_instances:
            if not ability.update():
                from resources import ResourceConsumption
                if isinstance(ability, ResourceConsumption) and ability.trigger == 'constant':
                     all_satisfied = False
        
        self._is_operational = all_satisfied and self.is_active

    @property
    def is_operational(self):
        return self._is_operational and self.is_active

    def can_afford_activation(self):
        """Check if component can afford activation costs."""
        from resources import ResourceConsumption
        for ability in self.ability_instances:
            if isinstance(ability, ResourceConsumption) and ability.trigger == 'activation':
                if not ability.check_available():
                    return False
        return True

    def consume_activation(self):
        """Consume activation costs."""
        from resources import ResourceConsumption
        for ability in self.ability_instances:
            if isinstance(ability, ResourceConsumption) and ability.trigger == 'activation':
                ability.check_and_consume()

    def try_activate(self):
        """Analyze if we can activate, and if so, consume and return True. (Legacy/Simple usage)"""
        if self.can_afford_activation():
            self.consume_activation()
            return True
        return False




    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_active = False
            return True # Destroyed
        return False

    def reset_hp(self):
        self.current_hp = self.max_hp
        self.is_active = True
        self.status = ComponentStatus.ACTIVE

    def add_modifier(self, mod_id, value=None):
        if mod_id not in MODIFIER_REGISTRY: return False
        
        # Check restrictions
        mod_def = MODIFIER_REGISTRY[mod_id]
        if 'deny_types' in mod_def.restrictions:
            if self.type_str in mod_def.restrictions['deny_types']:
                return False
        if 'allow_types' in mod_def.restrictions:
            if self.type_str not in mod_def.restrictions['allow_types']:
                return False
                
        # Remove existing if any (replace)
        self.remove_modifier(mod_id)
            
        app_mod = ApplicationModifier(mod_def, value)
        self.modifiers.append(app_mod)
        self.recalculate_stats()
        return True

    def remove_modifier(self, mod_id):
        self.modifiers = [m for m in self.modifiers if m.definition.id != mod_id]
        self.recalculate_stats()

    def get_modifier(self, mod_id):
        for m in self.modifiers:
            if m.definition.id == mod_id:
                return m
        return None
        


    def recalculate_stats(self):
        """Recalculate component stats with multiplicative modifier stacking."""
        # Capture old hp for current_hp logic at end
        old_max_hp = self.max_hp

        # 1. Reset and Evaluate Base Formulas
        self._reset_and_evaluate_base_formulas()
        
        # 1.5 Re-instantiate Abilities (Sync instances with new abilities dict)
        self._instantiate_abilities()

        # 2. Calculate Modifier Stats (Accumulate multipliers)
        stats = self._calculate_modifier_stats()
        self.stats = stats # Persist for introspection/ability access

        # 3. Apply Base Stats (Generic attributes)
        self._apply_base_stats(stats, old_max_hp)
        
        # 4. Apply Custom/Subclass Stats
        self._apply_custom_stats(stats)

    def _reset_and_evaluate_base_formulas(self):
        import copy
        # Reset abilities from raw data
        self.abilities = copy.deepcopy(self.data.get('abilities', {}))
        
        # Context building
        context = {
            'ship_class_mass': 1000 # Default fallback
        }
        if self.ship:
             context['ship_class_mass'] = getattr(self.ship, 'max_mass_budget', 1000)

        # Evaluate Formulas for attributes
        for attr, formula in self.formulas.items():
            val = evaluate_math_formula(formula, context)
            if attr == 'mass':
                self.base_mass = float(val)
                self.mass = self.base_mass # Reset to base
            elif attr == 'hp':
                self.base_max_hp = int(val)
                self.max_hp = self.base_max_hp # Reset to base
            else:
                 if hasattr(self, attr):
                     if isinstance(getattr(self, attr), int):
                         setattr(self, attr, int(val))
                     else:
                         setattr(self, attr, val)
        
        # Evaluate formulas in abilities
        for ability_name, val in self.abilities.items():
            if isinstance(val, str) and val.startswith("="):
                new_val = evaluate_math_formula(val[1:], context)
                self.abilities[ability_name] = new_val
            elif isinstance(val, dict):
                 if 'value' in val and isinstance(val['value'], str) and val['value'].startswith("="):
                     new_val = evaluate_math_formula(val['value'][1:], context)
                     val['value'] = new_val

    def _calculate_modifier_stats(self):
        from component_modifiers import apply_modifier_effects
        stats = {
            'mass_mult': 1.0,
            'hp_mult': 1.0,
            'damage_mult': 1.0,
            'range_mult': 1.0,
            'cost_mult': 1.0,
            'thrust_mult': 1.0,
            'turn_mult': 1.0,
            'energy_gen_mult': 1.0,
            'capacity_mult': 1.0,
            'crew_capacity_mult': 1.0,
            'life_support_capacity_mult': 1.0,
            'consumption_mult': 1.0,
            'mass_add': 0.0,
            'arc_add': 0.0,
            'accuracy_add': 0.0,
            'arc_set': None,
            'properties': {},
            # New Modifier Support
            'reload_mult': 1.0,
            'endurance_mult': 1.0,
            'projectile_hp_mult': 1.0,
            'projectile_damage_mult': 1.0,
            'projectile_stealth_level': 0.0,
            'crew_req_mult': 1.0
        }
        
        for m in self.modifiers:
            apply_modifier_effects(m.definition, m.value, stats, component=self)
            
        return stats

    def _apply_base_stats(self, stats, old_max_hp):
        # Helper to read weapon data from root OR ability dicts (Phase 6 migration)
        def get_weapon_data_for_stats(key, default=0):
            if key in self.data:
                return self.data[key]
            # Check in ability dicts
            abilities = self.data.get('abilities', {})
            for ab_name in ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility', 'WeaponAbility']:
                if ab_name in abilities:
                    ab_data = abilities[ab_name]
                    if isinstance(ab_data, dict) and key in ab_data:
                        return ab_data[key]
            return default

        # Apply specific property overrides
        for prop, val in stats['properties'].items():
            if hasattr(self, prop):
                setattr(self, prop, val)

        # Apply Arc effects
        if hasattr(self, 'firing_arc'):
            if stats['arc_set'] is not None:
                self.firing_arc = stats['arc_set']
            else:
                base = get_weapon_data_for_stats('firing_arc', 3)
                self.firing_arc = base + stats['arc_add']

        # Apply Base Multipliers
        self.mass = (self.base_mass + stats['mass_add']) * stats['mass_mult']
        
        # Note: old_max_hp is passed in, captured before base formula reset
        self.max_hp = int(self.base_max_hp * stats['hp_mult'])
        
        # Multipliers for generic attributes
        self.damage_multiplier = stats['damage_mult'] # Persist for get_damage
        
        if hasattr(self, 'damage'):
            # logic for handling formula-based damage is in Weapon subclass or get_damage usually,
            # but if 'damage' is a simple int attribute, we scale it.
            # However, Weapon class stores 'damage' as base int.
            # To handle non-Weapon components with damage:
            raw_damage = get_weapon_data_for_stats('damage', 0)
            if not (isinstance(raw_damage, str) and raw_damage.startswith("=")):
                 self.damage = int(raw_damage * stats['damage_mult'])

        if hasattr(self, 'range'):
            self.range = int(get_weapon_data_for_stats('range', 0) * stats['range_mult'])
        if hasattr(self, 'cost'):
            self.cost = int(self.data.get('cost', 0) * stats['cost_mult'])
        if hasattr(self, 'thrust_force'):
            self.thrust_force = self.data.get('thrust_force', 0) * stats['thrust_mult']
        if hasattr(self, 'turn_speed'):
            self.turn_speed = self.data.get('turn_speed', 0) * stats['turn_mult']

        if hasattr(self, 'reload_time'):
             self.reload_time = self.data.get('reload', 1.0) * stats.get('reload_mult', 1.0)

        # Crew Requirement Scaling
        # Rule: crew requirements should grow with the sqrt of mass of the component
        # We derive this from the total mass multiplier
        mass_scaling_factor = stats.get('mass_mult', 1.0)
        # Avoid complex numbers if somehow negative
        if mass_scaling_factor < 0: mass_scaling_factor = 0
        
        crew_mult = math.sqrt(mass_scaling_factor)
        
        # Apply to CrewRequired ability
        if 'CrewRequired' in self.abilities:
            val = self.abilities['CrewRequired']
            if isinstance(val, (int, float)):
                # If it's a raw number, scale it
                # Note: We should probably use the base value if we could, but abilities dict is reset in _reset_and_evaluate_base_formulas
                # So 'val' here is the base value from data/formula
                self.abilities['CrewRequired'] = int(math.ceil(val * crew_mult * stats.get('crew_req_mult', 1.0)))

        # Handle HP update (healing/new component logic)
        if old_max_hp == 0:
            self.current_hp = self.max_hp
        elif self.current_hp >= old_max_hp:
            self.current_hp = self.max_hp
            
        # Ensure cap
        self.current_hp = min(self.current_hp, self.max_hp)

        # Generic Sync: Update Activation Abilities if attributes changed
        from resources import ResourceConsumption, ResourceStorage, ResourceGeneration
        
        for ab in self.ability_instances:
            # General Recalculate (Protocol for active abilities to sync with stats)
            ab.recalculate()

            # ResourceConsumption (Base amount * consumption_mult)
            if isinstance(ab, ResourceConsumption):
                 base = ab.data.get('amount', 0.0)
                 ab.amount = base * stats.get('consumption_mult', 1.0)
            
            # ResourceStorage (Base amount * capacity_mult)
            elif isinstance(ab, ResourceStorage):
                 base = ab.data.get('amount', 0.0)
                 ab.max_amount = base * stats.get('capacity_mult', 1.0)
            
            # ResourceGeneration (Base amount * energy_gen_mult)
            elif isinstance(ab, ResourceGeneration):
                 # Apply energy_gen_mult only if resource is energy, or generic 'generation_mult' if we had one.
                 # Modifiers like "High Output Generator" affect energy_gen_mult.
                 if ab.resource_type == 'energy':
                     base = ab.data.get('amount', 0.0)
                     ab.rate = base * stats.get('energy_gen_mult', 1.0)
        
        # Sync Core Ability Values with Modifiers (Phase 3 Pre-requisite)
        from abilities import CombatPropulsion, ManeuveringThruster, ShieldProjection, ShieldRegeneration, WeaponAbility
        
        for ab in self.ability_instances:
            if isinstance(ab, CombatPropulsion):
                base = ab.data.get('value', ab.data) if isinstance(ab.data, dict) else ab.data
                if isinstance(base, (int, float)):
                    ab.thrust_force = float(base) * stats.get('thrust_mult', 1.0)
            elif isinstance(ab, ManeuveringThruster):
                base = ab.data.get('value', ab.data) if isinstance(ab.data, dict) else ab.data
                if isinstance(base, (int, float)):
                    ab.turn_rate = float(base) * stats.get('turn_mult', 1.0)
            elif isinstance(ab, ShieldProjection):
                base = ab.data.get('value', ab.data) if isinstance(ab.data, dict) else ab.data
                if isinstance(base, (int, float)):
                    ab.capacity = float(base) * stats.get('capacity_mult', 1.0)
            elif isinstance(ab, ShieldRegeneration):
                base = ab.data.get('value', ab.data) if isinstance(ab.data, dict) else ab.data
                if isinstance(base, (int, float)):
                    ab.rate = float(base) * stats.get('capacity_mult', 1.0)  # Regen scales with capacity
            elif isinstance(ab, WeaponAbility):
                # Use already-evaluated base values from ability (formulas handled in constructor)
                base_damage = getattr(ab, '_base_damage', ab.damage)
                base_range = getattr(ab, '_base_range', ab.range)
                base_reload = getattr(ab, '_base_reload', ab.reload_time)
                ab.damage = float(base_damage) * stats.get('damage_mult', 1.0)
                ab.range = float(base_range) * stats.get('range_mult', 1.0)
                ab.reload_time = float(base_reload) * stats.get('reload_mult', 1.0)
        
        # Ensure cap
        self.current_hp = min(self.current_hp, self.max_hp)

    def _apply_custom_stats(self, stats):
        """Hook for subclasses to apply specific stats."""
        # Base implementation handles Crew/LifeSupport as they are somewhat generic in this system
        if 'CrewCapacity' in self.abilities:
            val = self.abilities['CrewCapacity']
            if isinstance(val, (int, float)):
                self.abilities['CrewCapacity'] = int(val * stats['crew_capacity_mult'])
        
        if hasattr(self, 'crew_capacity'):
             base = self.data.get('crew_capacity', 10)
             self.crew_capacity = int(base * stats['crew_capacity_mult'])

        if 'LifeSupportCapacity' in self.abilities:
            val = self.abilities['LifeSupportCapacity']
            if isinstance(val, (int, float)):
                self.abilities['LifeSupportCapacity'] = int(val * stats['life_support_capacity_mult'])
        
        if hasattr(self, 'life_support_capacity'):
             base = self.data.get('life_support_capacity', 10)
             self.life_support_capacity = int(base * stats['life_support_capacity_mult'])

    def clone(self):
        # Create a new instance with the same data
        # We need a Factory, but since we are refactoring, we can just make a new instance of the same class.
        # But we need to know the class.
        return self.__class__(self.data)

# Phase 7: Bridge is now an alias for Component (backward compatibility)
Bridge = Component

from logger import log_event

# Phase 7: Weapon is now an alias for Component (backward compatible)
# All weapon stats and methods are now in WeaponAbility/ProjectileWeaponAbility/BeamWeaponAbility
Weapon = Component

# Phase 7: ProjectileWeapon is now an alias for Component
# All projectile stats are in ProjectileWeaponAbility
ProjectileWeapon = Component

# Phase 7: Engine, Thruster are now aliases for Component (backward compatible)
# All thrust/turn stats are now managed via CombatPropulsion/ManeuveringThruster abilities
Engine = Component
Thruster = Component

# Phase 7: Tank, Armor, Generator are now aliases for Component (backward compatible)
Tank = Component
Armor = Component
Generator = Component

# Phase 7: BeamWeapon is now an alias for Component
# All beam accuracy stats and calculate_hit_chance are in BeamWeaponAbility
BeamWeapon = Component

# Phase 7: SeekerWeapon is now an alias for Component
# All seeker stats are in SeekerWeaponAbility
SeekerWeapon = Component

# Phase 7: CrewQuarters is now an alias for Component
# crew_capacity was never used in the codebase; abilities handle crew via 'CrewCapacity'
CrewQuarters = Component

# Phase 7: LifeSupport is now an alias for Component
# life_support_capacity was never used; abilities handle it via 'LifeSupportCapacity'
LifeSupport = Component

# Phase 7: Sensor is now an alias for Component
# attack_modifier was never used; abilities handle it via 'ToHitAttackModifier'
Sensor = Component

# Phase 7: Electronics is now an alias for Component
# defense_modifier was never used; abilities handle it via 'ToHitDefenseModifier'
Electronics = Component

# Phase 7: Shield is now an alias for Component
# shield_capacity logic migrated to ShieldProjection.recalculate()
Shield = Component

# Phase 7: ShieldRegenerator is now an alias for Component
# regen_rate logic migrated to ShieldRegeneration.recalculate()
ShieldRegenerator = Component

# Phase 7: Hangar is now an alias for Component
# launch logic migrated to VehicleLaunchAbility usage in ship_combat.py
Hangar = Component

COMPONENT_REGISTRY = {}
# Phase 7 Simplified: Aliased types now use Component directly
# Types with custom logic (Shield, Hangar, etc.) are now also aliases
# as their logic has been unified into the Ability system.
COMPONENT_TYPE_MAP = {
    # Aliased types (all behaviors now in abilities)
    "Bridge": Component,
    "Weapon": Component,
    "ProjectileWeapon": Component,
    "Engine": Component,
    "Thruster": Component,
    "Tank": Component,
    "Armor": Component,
    "Generator": Component,
    "BeamWeapon": Component,
    "SeekerWeapon": Component,
    # Also aliased (simple classes)
    "CrewQuarters": Component,
    "LifeSupport": Component,
    "Sensor": Component,
    "Electronics": Component,
    "Shield": Component,
    "ShieldRegenerator": Component,
    "Hangar": Component
}

def load_components(filepath="data/components.json"):
    global COMPONENT_REGISTRY
    import os

    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
        print(f"WARN: {filepath} not found in CWD ({os.getcwd()}).")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)

        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            print(f"ERROR: components file not found at {abs_path}")
            return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        
        for comp_def in data['components']:
            c_type = comp_def['type']
            try:
                cls = COMPONENT_TYPE_MAP.get(c_type, Component)
                obj = cls(comp_def)
                COMPONENT_REGISTRY[comp_def['id']] = obj
            except Exception as e:
                print(f"ERROR creating component {comp_def.get('id')}: {e}")
                
    except Exception as e:
        print(f"ERROR loading/parsing components json: {e}")

def load_modifiers(filepath="data/modifiers.json"):
    global MODIFIER_REGISTRY
    import os
    if not os.path.exists(filepath):
         base_dir = os.path.dirname(os.path.abspath(__file__))
         filepath = os.path.join(base_dir, filepath)
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        for mod_def in data['modifiers']:
            mod = Modifier(mod_def)
            MODIFIER_REGISTRY[mod.id] = mod
            

    except Exception as e:
        print(f"ERROR loading modifiers: {e}")

def create_component(component_id):
    if component_id in COMPONENT_REGISTRY:
        return COMPONENT_REGISTRY[component_id].clone()
    print(f"Error: Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    return list(COMPONENT_REGISTRY.values())
