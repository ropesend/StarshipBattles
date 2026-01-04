import json
import math
from enum import Enum, auto
from formula_system import evaluate_math_formula
from game.core.registry import RegistryManager

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

# MODIFIER_REGISTRY = {} 
# Aliased to RegistryManager for backward compatibility (but prefer Manager access)
MODIFIER_REGISTRY = RegistryManager.instance().modifiers

class ApplicationModifier:
    """Instance of a modifier applied to a component"""
    def __init__(self, mod_def, value=None):
        self.definition = mod_def
        self.value = value if value is not None else mod_def.default_val

# IMPORTS MOVED TO LOCAL SCOPE TO PREVENT CIRCULAR DEPENDENCY
# from game.simulation.systems.resource_manager import ABILITY_REGISTRY, create_ability

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
                from game.core.registry import RegistryManager
                mods = RegistryManager.instance().modifiers
                if mod_id in mods:
                    mod_def = mods[mod_id]
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
                if key in ['mass', 'hp', 'cost']:
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
        from game.simulation.components.abilities import ABILITY_REGISTRY
        
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
            # Lazy import to avoid circular dependency
            from game.simulation.systems.resource_manager import ABILITY_REGISTRY, create_ability
            
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
                from game.simulation.systems.resource_manager import ResourceConsumption
                if isinstance(ability, ResourceConsumption) and ability.trigger == 'constant':
                     all_satisfied = False
        
        self._is_operational = all_satisfied and self.is_active

    @property
    def is_operational(self):
        return self._is_operational and self.is_active

    def can_afford_activation(self):
        """Check if component can afford activation costs."""
        from game.simulation.systems.resource_manager import ResourceConsumption
        for ability in self.ability_instances:
            if isinstance(ability, ResourceConsumption) and ability.trigger == 'activation':
                if not ability.check_available():
                    return False
        return True

    def consume_activation(self):
        """Consume activation costs."""
        from game.simulation.systems.resource_manager import ResourceConsumption
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
        mods = RegistryManager.instance().modifiers
        if mod_id not in mods: return False
        
        # Check restrictions
        mod_def = mods[mod_id]
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
        from game.simulation.components.modifiers import apply_modifier_effects
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
        # Apply specific property overrides
        for prop, val in stats['properties'].items():
            if hasattr(self, prop):
                setattr(self, prop, val)

        # Apply Base Multipliers
        self.mass = (self.base_mass + stats['mass_add']) * stats['mass_mult']
        
        # Note: old_max_hp is passed in, captured before base formula reset
        self.max_hp = int(self.base_max_hp * stats['hp_mult'])
        
        if hasattr(self, 'cost'):
            self.cost = int(self.data.get('cost', 0) * stats['cost_mult'])



        # Handle HP update (healing/new component logic)
        if old_max_hp == 0:
            self.current_hp = self.max_hp
        elif self.current_hp >= old_max_hp:
            self.current_hp = self.max_hp
            
        # Ensure cap
        self.current_hp = min(self.current_hp, self.max_hp)

        # Generic Sync: Update Activation Abilities if attributes changed
        from game.simulation.systems.resource_manager import ResourceConsumption, ResourceStorage, ResourceGeneration
        
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



    def _apply_custom_stats(self, stats):
        """Hook for subclasses to apply specific stats."""
        # Base implementation handles Crew/LifeSupport as they are somewhat generic in this system
        pass

    def clone(self):
        # Create a new instance with the same data
        # We need a Factory, but since we are refactoring, we can just make a new instance of the same class.
        # But we need to know the class.
        return self.__class__(self.data)


# Legacy Aliases - REMOVED / Mapped to Manager

COMPONENT_REGISTRY = RegistryManager.instance().components
# Phase 7 Simplified: Aliased types now use Component directly
# Types with custom logic (Shield, Hangar, etc.) are now also aliases
# as their logic has been unified into the Ability system.

COMPONENT_TYPE_MAP = {
    # All types map to generic Component
    "Bridge": Component,
    "Weapon": Component,
    "ProjectileWeapon": Component,
    "BeamWeapon": Component,
    "SeekerWeapon": Component,
    "Engine": Component,
    "Thruster": Component,
    "ManeuveringThruster": Component,
    "Shield": Component,
    "ShieldRegenerator": Component,
    "Generator": Component,
    "Hangar": Component,
    "Armor": Component,
    "Sensor": Component,
    "Electronics": Component,
    "Tank": Component,
    "CrewQuarters": Component,
    "LifeSupport": Component
}

# Caching for performance (Phase 2 Test Stabilization)
_COMPONENT_CACHE = None
_MODIFIER_CACHE = None

def load_components(filepath="data/components.json"):
    global _COMPONENT_CACHE
    import os
    import copy
    from game.core.registry import RegistryManager

    # If cache exists, hydrate Registry from cache (Fast Path)
    if _COMPONENT_CACHE is not None:
        mgr = RegistryManager.instance()
        for c_id, comp in _COMPONENT_CACHE.items():
            mgr.components[c_id] = comp.clone()
        return

    # Slow Path: Load from Disk
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
            import json
            data = json.load(f)
            
        temp_cache = {}
        for comp_def in data['components']:
            c_type = comp_def['type']
            try:
                cls = COMPONENT_TYPE_MAP.get(c_type, Component)
                obj = cls(comp_def)
                temp_cache[comp_def['id']] = obj
            except Exception as e:
                print(f"ERROR creating component {comp_def.get('id')}: {e}")
        
        # Populate Cache
        _COMPONENT_CACHE = temp_cache
        
        # Populate Registry from Cache
        mgr = RegistryManager.instance()
        for c_id, comp in _COMPONENT_CACHE.items():
            mgr.components[c_id] = comp.clone()
            
    except Exception as e:
        print(f"ERROR loading/parsing components json: {e}")

def load_modifiers(filepath="data/modifiers.json"):
    global _MODIFIER_CACHE
    import os
    import copy
    from game.core.registry import RegistryManager
    
    # Fast Path
    if _MODIFIER_CACHE is not None:
        mgr = RegistryManager.instance()
        for m_id, mod in _MODIFIER_CACHE.items():
            mgr.modifiers[m_id] = copy.deepcopy(mod)
        return

    # Slow Path
    if not os.path.exists(filepath):
         base_dir = os.path.dirname(os.path.abspath(__file__))
         filepath = os.path.join(base_dir, filepath)
    
    try:
        with open(filepath, 'r') as f:
            import json
            data = json.load(f)
            
        temp_cache = {}
        for mod_def in data['modifiers']:
            mod = Modifier(mod_def)
            temp_cache[mod.id] = mod
        
        _MODIFIER_CACHE = temp_cache
        
        mgr = RegistryManager.instance()
        for m_id, mod in _MODIFIER_CACHE.items():
            mgr.modifiers[m_id] = copy.deepcopy(mod)
            
    except Exception as e:
        print(f"ERROR loading modifiers: {e}")

def create_component(component_id):
    # Use RegistryManager instance instead of alias if possible, but alias is still mapped
    from game.core.registry import RegistryManager
    comps = RegistryManager.instance().components
    if component_id in comps:
        return comps[component_id].clone()
    print(f"Error: Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    from game.core.registry import RegistryManager
    return list(RegistryManager.instance().components.values())
