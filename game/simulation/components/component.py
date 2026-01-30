"""
Component System - Ship Component Model

This module defines the Component class, which represents individual parts
of a ship (engines, weapons, sensors, etc.) with their abilities and modifiers.

Component Lifecycle:
    1. CREATION: Component loaded from JSON definition via RegistryManager
       - Base stats initialized (mass, hp, cost)
       - Abilities instantiated from data
       - Default modifiers applied

    2. ATTACHMENT: Component added to Ship via add_component()
       - Layer assignment (CORE, INNER, OUTER)
       - Ship reference set for resource access
       - Stats recalculated with ship context

    3. SIMULATION: Component updated each tick
       - update() called: resource consumption, cooldowns
       - Abilities update their state
       - is_operational reflects resource availability

    4. DAMAGE: Component takes damage during combat
       - HP reduced, status updated (ACTIVE → DAMAGED → DESTROYED)
       - Below damage_threshold: component becomes inactive
       - Destroyed: removed from combat calculations

Ability System:
    Components have abilities that define their behavior:
    - WeaponAbility: Firing logic, damage, cooldowns
    - ThrustAbility: Engine thrust contribution
    - ResourceConsumption: Fuel/energy costs
    - SensorAbility: Detection bonuses
    - CapacityAbility: Cargo/hangar space

    Abilities are instantiated from the abilities dict and stored in
    ability_instances list. Access via get_ability(name) or get_abilities(name).

    Ability data flow:
    1. JSON definition → abilities dict
    2. _instantiate_abilities() → ability_instances list
    3. update() → each ability.update() called
    4. recalculate_stats() → ability contributions aggregated

Modifier System:
    Modifiers alter component stats (mass, damage, cooldown, etc.):
    - Loaded from component definition or applied at runtime
    - ApplicationModifier wraps ModifierDefinition with a value
    - Effects applied during recalculate_stats()

    Operations: 'add', 'multiply', 'set'
    Example: accuracy_mult * 1.1 increases accuracy by 10%

Key Classes:
    Component: The main component class
    ComponentStatus: Enum (ACTIVE, DAMAGED, DESTROYED)
    LayerType: Enum (CORE, INNER, OUTER)
    ApplicationModifier: Applied modifier with value
"""
import math
import threading
from game.simulation.formula_system import evaluate_math_formula
from typing import Optional, TYPE_CHECKING
from game.core.registry import get_default_registry_provider, get_default_registries
from game.core.json_utils import load_json_required
from game.core.logger import log_warning, log_error
from game.core.constants import CombatConstants
from .component_constants import ComponentStatus, Modifier, ApplicationModifier

if TYPE_CHECKING:
    from game.core.registry import GameRegistries

# Convenience aliases for registry data (read-only references)
# PROJ-42 Note: These module-level references are intentionally kept for UI hot-reload
# functionality (see builder/main.py _reload_data). They provide mutable dict refs
# that can be cleared. Internal Component methods should use _get_registries_fallback().
COMPONENT_REGISTRY = get_default_registry_provider().get_components()
MODIFIER_REGISTRY = get_default_registry_provider().get_modifiers()


def _get_registries_fallback() -> 'GameRegistries':
    """Get registries with fallback to legacy provider.

    PROJ-42: Helper for static paths and module-level functions.
    Tries get_default_registries() first (preferred), falls back to provider.
    Wraps provider in GameRegistries for consistent attribute access.

    Returns:
        GameRegistries instance
    """
    from game.core.registry import GameRegistries
    try:
        return get_default_registries()
    except RuntimeError:
        # Fall back to provider - wrap in GameRegistries for consistent interface
        # Note: Provider only has components/modifiers/vehicle_classes.
        # Resources is set to empty dict since this module doesn't use it.
        provider = get_default_registry_provider()
        return GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources={}
        )


class Component:
    def __init__(self, data, *, registries: Optional['GameRegistries'] = None):
        """
        Initialize Component with data and optional registries.

        PROJ-38: Supports constructor-based dependency injection.

        Args:
            data: Component definition dictionary
            registries: Optional GameRegistries for DI. If None, falls back to
                       get_default_registries() or legacy get_modifier_registry().
        """
        import copy
        self.data = copy.deepcopy(data) # Store raw data for reference/cloning

        # PROJ-38/PROJ-42: Store registries for modifier operations
        # Uses _get_registries_fallback() pattern for consistent DI behavior
        if registries is not None:
            self._registries = registries
        else:
            self._registries = _get_registries_fallback()
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
        # Default: 50% - components fail when damaged to half HP
        # Can be configured per-component (fragile sensors: 0.8, robust armor: 0.1)
        self.damage_threshold = data.get('damage_threshold', CombatConstants.DEFAULT_DAMAGE_THRESHOLD)

        # Parse abilities from data
        self.abilities = self.data.get('abilities', {})
        


        
        self.base_abilities = copy.deepcopy(self.abilities)
        
        self.ship = None # Container reference

        self.stats = {} # Current stats dictionary (calcualted)
        self.ability_stats = {}  # Stats keyed by ability class name for targeted modifier effects
        self.modifiers = [] # list of ApplicationModifier

        # Ability Instances (New System)
        self.ability_instances = []
        self._is_operational = True # Tracks if component has resources to operate
        
        # Instantiate Abilities
        self._instantiate_abilities()
        
        # Load default modifiers from data definition
        # PROJ-42: self._registries is always set via _get_registries_fallback()
        if 'modifiers' in self.data:
            mods = self._registries.modifiers
            for mod_data in self.data['modifiers']:
                mod_id = mod_data['id']
                val = mod_data.get('value', None)
                if mod_id in mods:
                    mod_def = mods[mod_id]
                    self.modifiers.append(mod_def.create_modifier(val))
                else:
                    log_warning(f"Component '{self.id}': Modifier '{mod_id}' not found in registry, skipping")
                    
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
                # Check if this is a constant resource consumption ability
                # Use duck typing to avoid importing from systems layer
                trigger = getattr(ability, 'trigger', None)
                if trigger == 'constant':
                    all_satisfied = False

        self._is_operational = all_satisfied and self.is_active

    @property
    def is_operational(self):
        return self._is_operational and self.is_active

    def can_afford_activation(self):
        """Check if component can afford activation costs."""
        for ability in self.ability_instances:
            # Use duck typing to check for activation-triggered resource consumption
            trigger = getattr(ability, 'trigger', None)
            check_fn = getattr(ability, 'check_available', None)
            if trigger == 'activation' and check_fn is not None:
                if not check_fn():
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

    def get_resource_cost(self, context: dict = None):
        """Returns the current resource costs, including modifier multipliers.

        Args:
            context: Optional dict with context for formula evaluation.
                     Expected keys: 'ship_class_mass' (float).
                     If not provided, falls back to component.ship reference.
        """
        base_costs = getattr(self, 'evaluated_resource_cost', None) or self.data.get("resource_cost", {})
        multiplier = self.stats.get('cost_mult', 1.0)

        # Build context for formula evaluation
        # Priority: explicit context > ship reference > default
        eval_context = {'ship_class_mass': 1000}
        if context and 'ship_class_mass' in context:
            eval_context['ship_class_mass'] = context['ship_class_mass']
        elif self.ship:
            eval_context['ship_class_mass'] = getattr(self.ship, 'max_mass_budget', 1000)

        result = {}
        for res, amount in base_costs.items():
            if isinstance(amount, str) and amount.startswith("="):
                # Evaluate formula on-demand
                amount = evaluate_math_formula(amount[1:], eval_context)
            result[res] = int(amount * multiplier)
        return result

    def add_modifier(self, mod_id, value=None):
        # PROJ-42: self._registries is always set via _get_registries_fallback()
        mods = self._registries.modifiers
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

    def get_all_modifier_effects(self):
        """Get all evaluated effects from all applied modifiers.

        Returns:
            List[ModifierEffect]: All effects from all modifiers on this component
        """
        all_effects = []
        for app_mod in self.modifiers:
            effects = app_mod.definition.evaluate_effects(app_mod.value)
            all_effects.extend(effects)
        return all_effects

    def get_modifier_stat_summary(self):
        """Get summary grouped by stat with net values and contributors.

        Returns:
            Dict[str, Dict]: Mapping from stat_key to:
                {
                    'net_value': float,  # Combined value for this stat
                    'operation': str,    # 'multiply', 'add', or 'set'
                    'contributors': [    # List of contributing modifiers
                        {
                            'modifier_id': str,
                            'modifier_name': str,
                            'value': float,
                            'formula': str
                        },
                        ...
                    ]
                }
        """
        summary = {}

        all_effects = self.get_all_modifier_effects()

        for effect in all_effects:
            stat_key = effect.stat_key

            if stat_key not in summary:
                # Initialize based on operation type
                default_value = 1.0 if effect.operation == 'multiply' else 0.0
                summary[stat_key] = {
                    'net_value': default_value,
                    'operation': effect.operation,
                    'contributors': []
                }

            entry = summary[stat_key]

            # Add contributor info
            entry['contributors'].append({
                'modifier_id': effect.source_modifier_id,
                'modifier_name': effect.source_modifier_name,
                'value': effect.value,
                'formula': effect.formula_str
            })

            # Calculate net value based on operation
            if effect.operation == 'multiply':
                entry['net_value'] *= effect.value
            elif effect.operation == 'add':
                entry['net_value'] += effect.value
            elif effect.operation == 'set':
                entry['net_value'] = effect.value  # Last set wins

        return summary

    def recalculate_stats(self, context: dict = None):
        """Recalculate component stats with multiplicative modifier stacking.

        Args:
            context: Optional dict with context for formula evaluation.
                     Expected keys: 'ship_class_mass' (float).
                     If not provided, falls back to component.ship reference.
        """
        # Capture old hp for current_hp logic at end
        old_max_hp = self.max_hp

        # 1. Reset and Evaluate Base Formulas
        self._reset_and_evaluate_base_formulas(context)

        # 1.5 Re-instantiate Abilities (Sync instances with new abilities dict)
        self._instantiate_abilities()

        # 2. Calculate Modifier Stats (Accumulate multipliers)
        stats = self._calculate_modifier_stats()
        self.stats = stats # Persist for introspection/ability access

        # 3. Apply Base Stats (Generic attributes)
        self._apply_base_stats(stats, old_max_hp)



    def _reset_and_evaluate_base_formulas(self, context: dict = None):
        import copy
        # Reset abilities from raw data
        self.abilities = copy.deepcopy(self.data.get('abilities', {}))

        # Context building - Priority: explicit context > ship reference > default
        eval_context = {
            'ship_class_mass': 1000 # Default fallback
        }
        if context and 'ship_class_mass' in context:
            eval_context['ship_class_mass'] = context['ship_class_mass']
        elif self.ship:
            eval_context['ship_class_mass'] = getattr(self.ship, 'max_mass_budget', 1000)

        # Evaluate Formulas for attributes
        for attr, formula in self.formulas.items():
            val = evaluate_math_formula(formula, eval_context)
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
        def evaluate_formulas_recursive(obj, ctx):
            """Recursively evaluate formulas in nested structures (dicts and lists)."""
            if isinstance(obj, str) and obj.startswith("="):
                return evaluate_math_formula(obj[1:], ctx)
            elif isinstance(obj, dict):
                for key, sub_val in obj.items():
                    obj[key] = evaluate_formulas_recursive(sub_val, ctx)
                return obj
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    obj[i] = evaluate_formulas_recursive(item, ctx)
                return obj
            return obj

        for ability_name, val in self.abilities.items():
            self.abilities[ability_name] = evaluate_formulas_recursive(val, eval_context)

        # Evaluate formulas in resource_cost
        raw_costs = self.data.get("resource_cost", {})
        self.evaluated_resource_cost = {}
        for res, amount in raw_costs.items():
            if isinstance(amount, str) and amount.startswith("="):
                self.evaluated_resource_cost[res] = evaluate_math_formula(amount[1:], eval_context)
            else:
                self.evaluated_resource_cost[res] = amount

    def _calculate_modifier_stats(self):
        from game.simulation.components.modifiers import (
            apply_modifier_effects,
            get_default_stat_multipliers
        )

        # Use shared function for canonical default stats
        stats = get_default_stat_multipliers()

        # Apply modifiers with component reference for targeted effects
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

        # Recalculate all abilities with updated stats from modifiers
        for ab in self.ability_instances:
            ab.recalculate()

    def clone(self):
        # Create a new instance with the same data
        # PROJ-38: Pass registries to the clone for DI consistency
        return self.__class__(self.data, registries=self._registries)


# All component types use Component directly via the ability system.
# Type-specific behavior is handled by ability instances (WeaponAbility, etc.)


# Thread-safe singleton for component and modifier caches
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

def load_components_data(filepath: str = "data/components.json") -> dict:
    """
    Pure function to load components from JSON file.

    PROJ-38: Returns a dictionary of Component objects keyed by ID without
    modifying any global state. Use this for DI patterns.

    Args:
        filepath: Path to the components JSON file

    Returns:
        Dict[str, Component]: Component objects keyed by their ID
    """
    import os

    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)
        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            log_error(f"components file not found at {abs_path}")
            return {}

    try:
        data = load_json_required(filepath)

        result = {}
        for comp_def in data['components']:
            try:
                obj = Component(comp_def)
                result[comp_def['id']] = obj
            except Exception as e:
                log_error(f"creating component {comp_def.get('id')}: {e}")

        return result

    except Exception as e:
        log_error(f"loading/parsing components json: {e}")
        return {}


def load_components(filepath="data/components.json"):
    """
    Load components from JSON and populate the global registry.

    This is a thin wrapper around load_components_data() for backward
    compatibility. New code should prefer DI via load_components_data().
    """
    import os
    import copy

    cache_mgr = ComponentCacheManager.instance()
    # PROJ-42: Use _get_registries_fallback() for consistent DI behavior
    comps = _get_registries_fallback().components

    # If cache exists and matches filepath, hydrate Registry from cache (Fast Path)
    if cache_mgr.component_cache is not None and cache_mgr.last_component_file == filepath:
        for c_id, comp in cache_mgr.component_cache.items():
            comps[c_id] = comp.clone()
        return

    # Slow Path: Load from Disk using pure function
    result = load_components_data(filepath)
    if not result:
        return

    # Populate Cache
    cache_mgr.component_cache = result
    cache_mgr.last_component_file = filepath

    # Populate Registry from Cache
    for c_id, comp in cache_mgr.component_cache.items():
        comps[c_id] = comp.clone()

def load_modifiers_data(filepath: str = "data/modifiers.json") -> dict:
    """
    Pure function to load modifiers from JSON file.

    PROJ-38: Returns a dictionary of Modifier objects keyed by ID without
    modifying any global state. Use this for DI patterns.

    Args:
        filepath: Path to the modifiers JSON file

    Returns:
        Dict[str, Modifier]: Modifier objects keyed by their ID
    """
    import os
    import copy
    from game.simulation.components.modifier_schema import validate_modifier_v2

    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)
        if os.path.exists(abs_path):
            filepath = abs_path
        else:
            log_error(f"modifiers file not found at {abs_path}")
            return {}

    try:
        data = load_json_required(filepath)

        result = {}
        for mod_def in data['modifiers']:
            # Validate modifier schema (graceful degradation - warn but continue)
            if not validate_modifier_v2(mod_def):
                mod_id = mod_def.get('id', 'unknown')
                log_warning(f"Modifier '{mod_id}' failed schema validation, loading anyway")
            mod = Modifier(mod_def)
            result[mod.id] = copy.deepcopy(mod)

        return result

    except Exception as e:
        log_error(f"loading modifiers: {e}")
        return {}


def load_modifiers(filepath="data/modifiers.json"):
    """
    Load modifiers from JSON and populate the global registry.

    This is a thin wrapper around load_modifiers_data() for backward
    compatibility. New code should prefer DI via load_modifiers_data().
    """
    import os
    import copy

    cache_mgr = ComponentCacheManager.instance()
    # PROJ-42: Use _get_registries_fallback() for consistent DI behavior
    mods = _get_registries_fallback().modifiers

    # Fast Path
    if cache_mgr.modifier_cache is not None and cache_mgr.last_modifier_file == filepath:
        for m_id, mod in cache_mgr.modifier_cache.items():
            mods[m_id] = copy.deepcopy(mod)
        return

    # Slow Path: Load using pure function
    result = load_modifiers_data(filepath)
    if not result:
        return

    cache_mgr.modifier_cache = result
    cache_mgr.last_modifier_file = filepath

    for m_id, mod in cache_mgr.modifier_cache.items():
        mods[m_id] = copy.deepcopy(mod)

def create_component(component_id, *, registries: Optional['GameRegistries'] = None):
    """Create a clone of a component from the registry by ID.

    PROJ-38/PROJ-42: Accepts optional registries parameter for DI.

    Args:
        component_id: The ID of the component to create
        registries: Optional GameRegistries for DI. If provided, uses
                   registries.components instead of global registry.

    Returns:
        Component clone or None if not found
    """
    # PROJ-42: Use _get_registries_fallback() for consistent DI behavior
    if registries is not None:
        regs = registries
    else:
        regs = _get_registries_fallback()
    comps = regs.components

    if component_id in comps:
        clone = comps[component_id].clone()
        # PROJ-42: Ensure clone has correct registries
        clone._registries = regs
        return clone
    log_error(f"Component ID {component_id} not found in registry.")
    return None

def get_all_components():
    """Get a list of all components in the registry."""
    # PROJ-42: Use _get_registries_fallback() for consistent DI behavior
    return list(_get_registries_fallback().components.values())

