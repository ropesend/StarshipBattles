import math
import threading
from game.simulation.formula_system import evaluate_math_formula
from game.core.registry import get_component_registry, get_modifier_registry
from game.core.json_utils import load_json_required
from game.core.logger import log_warning, log_error

# Re-export from component_constants for backward compatibility
from .component_constants import (
    ComponentStatus,
    LayerType,
    Modifier,
    ApplicationModifier,
)


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

        # Damage threshold: HP percentage at which component becomes inactive
        # Default: 0.5 (50%) - components fail when damaged to half HP
        # Can be configured per-component:
        #   - Fragile sensors: 0.8 (fail at 80% damage)
        #   - Robust armor: 0.1 (fail at 90% damage)
        self.damage_threshold = data.get('damage_threshold', 0.5)

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
                # We need to access modifier registry.
                from game.core.registry import get_modifier_registry
                mods = get_modifier_registry()
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
            # [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
            # When test modules reload ability classes, isinstance() fails due to
            # different class objects. This __name__ check provides test isolation.
            # Ref: Phase 2 Task 2.5 audit - documented as intentional tech debt.
            else:
                for cls in ab.__class__.mro():
                    if cls.__name__ == ability_name:
                        found.append(ab)
                        break
        return found

    def get_ability(self, ability_name: str):
        """Get first ability of type."""
        l = self.get_abilities(ability_name)
        return l[0] if l else None

    def has_ability(self, ability_name: str):
        # 1. Direct check (fast)
        if ability_name in self.abilities:
            return True
        # 2. Polymorphic check (e.g. asking for 'WeaponAbility' when we have 'ProjectileWeaponAbility')
        return len(self.get_abilities(ability_name)) > 0

    def has_pdc_ability(self) -> bool:
        """Check if component has a Point Defense weapon ability.
        
        Returns True if any ability has 'pdc' in its tags.
        """
        # 1. Check new tag-based system
        for ab in self.ability_instances:
            if 'pdc' in ab.tags:
                return True
        

        return False



    @property
    def cooldown_timer(self):
        # Map to first weapon ability if present
        ab = self.get_ability('WeaponAbility')
        if ab: return ab.cooldown_timer
        return 0.0
        
    @cooldown_timer.setter
    def cooldown_timer(self, value):
        ab = self.get_ability('WeaponAbility')
        if ab: ab.cooldown_timer = float(value)

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
        """Instantiate or Sync Ability objects from self.abilities dict."""
        # We want to preserve existing instances to maintain runtime state (cooldowns, energy)
        # but also add new ones or remove obsolete ones.
        
        # 1. Map existing instances for quick lookup
        # Key: (ability_type_name, index_in_that_type)
        existing_map = {}
        for ab in self.ability_instances:
            # We track by class name
            cls_name = ab.__class__.__name__
            if cls_name not in existing_map:
                existing_map[cls_name] = []
            existing_map[cls_name].append(ab)

        new_instances = []
        
        # Standard Loading from abilities dict
        from game.simulation.systems.resource_manager import ABILITY_REGISTRY, create_ability
        
        for name, data in self.abilities.items():
            if name not in ABILITY_REGISTRY:
                continue
            
            items = data if isinstance(data, list) else [data]
            
        # Get the target class for this registry entry (could be class or lambda)
            target = ABILITY_REGISTRY[name]
            target_cls_name = None
            if isinstance(target, type):
                target_cls_name = target.__name__
            else:
                # Use centralized map for shortcut factories (lambdas)
                from game.simulation.components.abilities import ABILITY_CLASS_MAP
                target_cls_name = ABILITY_CLASS_MAP.get(name)

            for item in items:
                # Heuristic: Match by Target Class Name if known, otherwise fallback to registry name
                match_name = target_cls_name or name
                
                found_existing = False
                if match_name in existing_map and existing_map[match_name]:
                    ab = existing_map[match_name].pop(0)
                    # Support live data sync if ability supports it
                    if hasattr(ab, 'sync_data'):
                        ab.sync_data(item)
                    new_instances.append(ab)
                    found_existing = True
                
                if not found_existing:
                    ab = create_ability(name, self, item)
                    if ab: new_instances.append(ab)
        
        self.ability_instances = new_instances
            
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
        for ability in self.get_abilities('ResourceConsumption'):
            if ability.trigger == 'activation':
                ability.check_and_consume()

    def try_activate(self):
        """Check if component can afford activation costs, consume them if available, and return True on success."""
        if self.can_afford_activation():
            self.consume_activation()
            return True
        return False




    def take_damage(self, amount: float) -> None:
        if not isinstance(amount, (int, float)):
            raise TypeError(f"amount must be numeric, got {type(amount).__name__}")

        self.current_hp -= amount

        # Update Status
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_active = False
            return True # Destroyed
        
        # Update status to DAMAGED if below damage threshold (default 50%)
        if self.current_hp < (self.max_hp * self.damage_threshold):
            self.status = ComponentStatus.DAMAGED

        return False

    def reset_hp(self):
        self.current_hp = self.max_hp
        self.is_active = True
        self.status = ComponentStatus.ACTIVE

    def add_modifier(self, mod_id, value=None):
        mods = get_modifier_registry()
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
                 # Phase 7: Generically evaluate formulas in any key of the ability dict
                 for key, sub_val in val.items():
                     if isinstance(sub_val, str) and sub_val.startswith("="):
                         new_val = evaluate_math_formula(sub_val[1:], context)
                         val[key] = new_val

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
            
            ab_cls = ab.__class__.__name__
            ab_data = ab.data
            
            # Helper to get base value safely from dict or primitive
            def get_base(data, key, default=0.0):
                if isinstance(data, dict):
                    return data.get(key, default)
                if isinstance(data, (int, float)):
                    return float(data)
                return default

            # ResourceConsumption (Base amount * consumption_mult)
            if ab_cls == 'ResourceConsumption':
                 base = get_base(ab_data, 'amount')
                 ab.amount = base * stats.get('consumption_mult', 1.0)
            
            # ResourceStorage (Base amount * capacity_mult)
            elif ab_cls == 'ResourceStorage':
                 base = get_base(ab_data, 'amount')
                 ab.max_amount = base * stats.get('capacity_mult', 1.0)
            
            # ResourceGeneration (Base amount * energy_gen_mult)
            elif ab_cls == 'ResourceGeneration':
                 # Apply energy_gen_mult only if resource is energy, or generic 'generation_mult' if we had one.
                 if getattr(ab, 'resource_type', '') == 'energy':
                     base = get_base(ab_data, 'amount')
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


# Phase 7 Simplified: Aliased types now use Component directly
# Types with custom logic (Shield, Hangar, etc.) are now also aliases
# as their logic has been unified into the Ability system.

# Export types for compatibility (Phase 6 Regression Triage)


# Caching for performance (Phase 2 Test Stabilization)
# Refactored to thread-safe singleton pattern (Code Review Phase 0)
class ComponentCacheManager:
    """Thread-safe singleton manager for component and modifier caches."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.component_cache = None
        self.modifier_cache = None
        self.last_component_file = None
        self.last_modifier_file = None

    @classmethod
    def instance(cls):
        """Get the singleton instance with thread-safe initialization."""
        if cls._instance is None:
            with cls._lock:
                # Double-check after acquiring lock
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset all caches for test isolation."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.component_cache = None
                cls._instance.modifier_cache = None
                cls._instance.last_component_file = None
                cls._instance.last_modifier_file = None


def reset_component_caches():
    """
    Reset all caches for test isolation.
    This ensures clean state between tests in parallel execution.
    """
    ComponentCacheManager.reset()

def load_components(filepath="data/components.json"):
    import os
    import copy
    from game.core.registry import get_component_registry

    cache_mgr = ComponentCacheManager.instance()

    # If cache exists and matches filepath, hydrate Registry from cache (Fast Path)
    if cache_mgr.component_cache is not None and cache_mgr.last_component_file == filepath:
        comps = get_component_registry()
        for c_id, comp in cache_mgr.component_cache.items():
            comps[c_id] = comp.clone()
        return

    # Slow Path: Load from Disk
    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
        log_warning(f"{filepath} not found in CWD ({os.getcwd()}).")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)

        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            log_error(f"components file not found at {abs_path}")
            return

    try:
        data = load_json_required(filepath)

        temp_cache = {}
        for comp_def in data['components']:
            c_type = comp_def['type']
            try:
                cls = Component
                obj = cls(comp_def)
                temp_cache[comp_def['id']] = obj
            except Exception as e:
                log_error(f"creating component {comp_def.get('id')}: {e}")

        # Populate Cache
        cache_mgr.component_cache = temp_cache
        cache_mgr.last_component_file = filepath

        # Populate Registry from Cache
        comps = get_component_registry()
        for c_id, comp in cache_mgr.component_cache.items():
            comps[c_id] = comp.clone()

    except Exception as e:
        log_error(f"loading/parsing components json: {e}")

def load_modifiers(filepath="data/modifiers.json"):
    import os
    import copy
    from game.core.registry import get_modifier_registry

    cache_mgr = ComponentCacheManager.instance()

    # Fast Path
    if cache_mgr.modifier_cache is not None and cache_mgr.last_modifier_file == filepath:
        mods = get_modifier_registry()
        for m_id, mod in cache_mgr.modifier_cache.items():
            mods[m_id] = copy.deepcopy(mod)
        return

    # Slow Path
    if not os.path.exists(filepath):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, filepath)

    try:
        data = load_json_required(filepath)

        temp_cache = {}
        for mod_def in data['modifiers']:
            mod = Modifier(mod_def)
            temp_cache[mod.id] = mod

        cache_mgr.modifier_cache = temp_cache
        cache_mgr.last_modifier_file = filepath

        mods = get_modifier_registry()
        for m_id, mod in cache_mgr.modifier_cache.items():
            mods[m_id] = copy.deepcopy(mod)

    except Exception as e:
        log_error(f"loading modifiers: {e}")

def create_component(component_id):
    """Create a clone of a component from the registry by ID."""
    comps = get_component_registry()
    if component_id in comps:
        return comps[component_id].clone()
    log_error(f"Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    """Get a list of all components in the registry."""
    return list(get_component_registry().values())

