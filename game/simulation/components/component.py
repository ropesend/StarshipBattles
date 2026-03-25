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
import json
import logging
from game.simulation.formula_system import safe_evaluate_math_formula
from game.core.singleton import SingletonMeta
from typing import Optional, TYPE_CHECKING
# PROJ-211: Removed get_default_registry_provider import - DI is now required
from game.core.json_utils import load_json_required
from game.core.constants import CombatConstants
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)
from .component_constants import ComponentStatus, Modifier, ApplicationModifier
from .ability_manager import AbilityManager
from .modifier_manager import ModifierManager
from .component_stats_calculator import ComponentStatsCalculator
from .component_resource_manager import ComponentResourceManager
from .component_health_manager import ComponentHealthManager

if TYPE_CHECKING:
    from game.core.registry import GameRegistries

class Component:
    def __init__(self, data, *, registries: 'GameRegistries'):
        """
        Initialize Component with data and registries.

        PROJ-50: Strict DI - registries is required.

        Args:
            data: Component definition dictionary
            registries: GameRegistries for DI (required).

        Raises:
            ValidationException: If registries is None
        """
        if registries is None:
            raise ValidationException(
                "registries is required for Component initialization",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "Component", "parameter": "registries"}
            )
        import copy
        # PERF-ANALYSIS: deepcopy required - data contains nested mutable structures
        # (abilities dict with lists and sub-dicts). Shallow copy would cause shared
        # references, breaking clone() and modifier isolation.
        self.data = copy.deepcopy(data)

        # PROJ-50: Store registries for modifier operations (strict DI)
        self._registries = registries
        self.id = data['id']
        self.name = data['name']
        self.base_mass = data['mass']
        self.mass = self.base_mass
        self.base_max_hp = data['hp']
        self.max_hp = self.base_max_hp
        self.current_hp = self.max_hp

        # PROJ-49: HP ratio caching - reduces division operations in hot paths
        self._hp_ratio_dirty: bool = True
        self._cached_hp_ratio: float = 1.0

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
        


        
        # PERF-ANALYSIS: deepcopy required - abilities dict has nested mutable values
        # (ResourceConsumption lists, ability config dicts). Used to restore original
        # state after runtime modifications.
        self.base_abilities = copy.deepcopy(self.abilities)
        
        self.ship = None # Container reference

        self.stats = {} # Current stats dictionary (calcualted)
        self.ability_stats = {}  # Stats keyed by ability class name for targeted modifier effects
        self.modifiers = [] # list of ApplicationModifier

        # Ability Instances (New System)
        self.ability_instances = []
        self._ability_index = {}  # PERF: Fast lookup by ability class name
        self._is_operational = True # Tracks if component has resources to operate

        # Combat statistics (weapons)
        self.shots_fired = 0
        self.shots_hit = 0

        # Instantiate Abilities
        self._instantiate_abilities()

        # Lazy-initialized helper managers (PROJ-88)
        self._resource_mgr: ComponentResourceManager | None = None
        self._health_mgr: ComponentHealthManager | None = None

        # Load default modifiers from data definition
        # PROJ-50: self._registries is now always required via constructor
        if 'modifiers' in self.data:
            mods = self._registries.modifiers
            for mod_data in self.data['modifiers']:
                mod_id = mod_data['id']
                val = mod_data.get('value', None)
                if mod_id in mods:
                    mod_def = mods[mod_id]
                    self.modifiers.append(mod_def.create_modifier(val))
                else:
                    logger.warning(f"Component '{self.id}': Modifier '{mod_id}' not found in registry, skipping")
                    
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

        PERF: Uses indexed lookup when available, falls back to AbilityManager.
        """
        # Fast path: use pre-built index (includes MRO for polymorphism)
        if ability_name in self._ability_index:
            return list(self._ability_index[ability_name])  # Return copy

        # Fallback: delegate to AbilityManager (for edge cases)
        return AbilityManager.get_abilities(ability_name, self.ability_instances)

    def get_ability(self, ability_name: str):
        """Get first ability of type. Uses indexed lookup when available."""
        # Fast path: use pre-built index
        if ability_name in self._ability_index:
            abilities = self._ability_index[ability_name]
            return abilities[0] if abilities else None

        # Fallback: delegate to AbilityManager
        return AbilityManager.get_ability(ability_name, self.ability_instances)

    def has_ability(self, ability_name: str):
        """Check if component has ability. Uses indexed lookup when available."""
        # Fast path: use pre-built index
        if ability_name in self._ability_index:
            return len(self._ability_index[ability_name]) > 0

        # Fallback: delegate to AbilityManager
        return AbilityManager.has_ability(ability_name, self.ability_instances, self.abilities)

    def has_pdc_ability(self) -> bool:
        """Check if component has a Point Defense weapon ability.

        Returns True if any ability has 'pdc' in its tags.
        Delegates to AbilityManager.
        """
        return AbilityManager.has_pdc_ability(self.ability_instances)



    @property
    def resource_manager(self) -> ComponentResourceManager:
        """Lazy-initialized resource manager. PROJ-88."""
        if self._resource_mgr is None:
            self._resource_mgr = ComponentResourceManager(self)
        return self._resource_mgr

    @property
    def health_manager(self) -> ComponentHealthManager:
        """Lazy-initialized health manager. PROJ-88."""
        if self._health_mgr is None:
            self._health_mgr = ComponentHealthManager(self)
        return self._health_mgr

    def mark_hp_cache_dirty(self) -> None:
        """Mark HP ratio cache as dirty for recalculation.

        Public API for external code to invalidate the HP ratio cache
        without accessing the private _hp_ratio_dirty attribute.
        """
        self._hp_ratio_dirty = True

    @property
    def hp_ratio(self) -> float:
        """Get current HP as ratio of max HP. Cached with dirty flag.

        PROJ-49: Caches the division result to avoid repeated calculations
        in hot paths like damage threshold checks.

        Returns:
            float: HP ratio (0.0 to 1.0), returns 1.0 if max_hp is 0
        """
        return self.health_manager.hp_ratio

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
        Delegates to AbilityManager.
        """
        return AbilityManager.get_ui_rows(self.ability_instances)

    def _instantiate_abilities(self):
        """Instantiate or Sync Ability objects from self.abilities dict.

        Preserves existing instances to maintain runtime state (cooldowns, energy).
        Delegates to AbilityManager. Also builds index for fast lookup.
        """
        self.ability_instances = AbilityManager.instantiate_abilities(
            self.abilities,
            self.ability_instances,
            self
        )
        # PERF: Build ability index for O(1) lookup by class name
        self._ability_index = {}
        for ab in self.ability_instances:
            # Index by class name and all parent class names (for polymorphism)
            for cls in ab.__class__.mro():
                cls_name = cls.__name__
                if cls_name == 'object':
                    break
                if cls_name not in self._ability_index:
                    self._ability_index[cls_name] = []
                self._ability_index[cls_name].append(ab)
            
    def update(self):
        """Update component state for one tick (resource consumption, cooldowns)."""
        # 1. Update Abilities (Constant Consumption)
        all_satisfied = True

        for ability in self.ability_instances:
            if not ability.update():
                # Check if this is a constant resource consumption ability
                # ResourceConsumption has trigger attr; other abilities don't
                # Using safe access since trigger is not on IAbility protocol
                trigger = getattr(ability, 'trigger', None)
                if trigger == 'constant':
                    all_satisfied = False

        self._is_operational = all_satisfied and self.is_active

    @property
    def is_operational(self):
        return self._is_operational and self.is_active

    def can_afford_activation(self):
        """Check if component can afford activation costs. Delegates to resource_manager."""
        return self.resource_manager.can_afford_activation()

    def consume_activation(self):
        """Consume activation costs. Delegates to resource_manager."""
        self.resource_manager.consume_activation()

    def try_activate(self):
        """Check and consume activation costs atomically. Delegates to resource_manager."""
        return self.resource_manager.try_activate()




    def take_damage(self, amount: float) -> bool:
        """Apply damage to component. Delegates to health_manager."""
        return self.health_manager.take_damage(amount)

    def reset_hp(self):
        """Restore component to full HP. Delegates to health_manager."""
        self.health_manager.reset_hp()

    def get_resource_cost(self, context: dict = None):
        """Returns the current resource costs. Delegates to resource_manager."""
        return self.resource_manager.get_resource_cost(context)

    def add_modifier(self, mod_id, value=None):
        """Add a modifier to this component. Delegates to ModifierManager."""
        result = ModifierManager.add_modifier(
            self.modifiers,
            mod_id,
            value,
            self._registries,
            self.type_str
        )
        if result:
            self.recalculate_stats()
        return result

    def remove_modifier(self, mod_id):
        """Remove a modifier from this component. Delegates to ModifierManager."""
        self.modifiers = ModifierManager.remove_modifier(self.modifiers, mod_id)
        self.recalculate_stats()

    def get_modifier(self, mod_id):
        """Get a modifier by ID. Delegates to ModifierManager."""
        return ModifierManager.get_modifier(self.modifiers, mod_id)

    def get_all_modifier_effects(self):
        """Get all evaluated effects from all applied modifiers.

        Delegates to ModifierManager.

        Returns:
            List[ModifierEffect]: All effects from all modifiers on this component
        """
        return ModifierManager.get_all_effects(self.modifiers)

    def get_modifier_stat_summary(self):
        """Get summary grouped by stat with net values and contributors.

        Delegates to ModifierManager.

        Returns:
            Dict[str, Dict]: Mapping from stat_key to summary info
        """
        return ModifierManager.get_stat_summary(self.modifiers)

    def recalculate_stats(self, context: dict = None):
        """Recalculate component stats with multiplicative modifier stacking.

        Delegates to ComponentStatsCalculator for the multi-phase calculation.

        Args:
            context: Optional dict with context for formula evaluation.
                     Expected keys: 'ship_class_mass' (float).
                     If not provided, falls back to component.ship reference.
        """
        ComponentStatsCalculator.recalculate(self, context)

    def _reset_and_evaluate_base_formulas(self, context: dict = None):
        """Reset to base values and evaluate formulas. Delegates to ComponentStatsCalculator."""
        ComponentStatsCalculator.reset_and_evaluate_formulas(self, context)

    def _calculate_modifier_stats(self):
        """Calculate modifier stats. Delegates to ComponentStatsCalculator."""
        return ComponentStatsCalculator.calculate_modifier_stats(self.modifiers, self)

    def _apply_base_stats(self, stats, old_max_hp):
        """Apply stats to component. Delegates to ComponentStatsCalculator."""
        ComponentStatsCalculator.apply_base_stats(self, stats, old_max_hp)

    def clone(self):
        # Create a new instance with the same data
        # PROJ-38: Pass registries to the clone for DI consistency
        return self.__class__(self.data, registries=self._registries)


# All component types use Component directly via the ability system.
# Type-specific behavior is handled by ability instances (WeaponAbility, etc.)


# PROJ-225: Migrated to SingletonMeta (consistent with all other singletons in codebase)
class ComponentCacheManager(metaclass=SingletonMeta):
    """Thread-safe singleton manager for component and modifier caches."""

    def __init__(self):
        self.component_cache = None
        self.modifier_cache = None
        self.last_component_file = None
        self.last_modifier_file = None


def reset_component_caches():
    """
    Reset all caches for test isolation.
    This ensures clean state between tests in parallel execution.
    PROJ-225: Now uses SingletonMeta.reset() which destroys the instance entirely.
    """
    ComponentCacheManager.reset()

def load_components_data(
    file_path: str = "data/components.json",
    *,
    registries: 'GameRegistries'
) -> dict:
    """
    Pure function to load components from JSON file.

    PROJ-211: registries is now required (no fallback).

    Args:
        file_path: Path to the components JSON file
        registries: GameRegistries for DI. Required.

    Returns:
        Dict[str, Component]: Component objects keyed by their ID
    """
    import os
    from game.core.registry import GameRegistries

    # Try absolute path based on this file if CWD fails
    if not os.path.exists(file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, file_path)
        if os.path.exists(abs_path):
            file_path = abs_path
        else:
            logger.error(f"components file not found at {abs_path}")
            return {}

    try:
        data = load_json_required(file_path)

        result = {}
        errors = []
        for comp_def in data['components']:
            comp_id = comp_def.get('id', 'unknown')
            try:
                # PROJ-50: Pass registries to Component
                obj = Component(comp_def, registries=registries)
                result[comp_id] = obj
            except (KeyError, TypeError, ValueError, ValidationException) as e:
                # Schema/data issues - log and continue (collect errors)
                logger.error(f"Component '{comp_id}': invalid data - {e}")
                errors.append(comp_id)
            except (AttributeError, ImportError) as e:
                # Unexpected error - log with full context
                logger.error(f"Component '{comp_id}': unexpected error - {type(e).__name__}: {e}")
                errors.append(comp_id)

        if errors:
            logger.warning(f"Loaded {len(result)} components, {len(errors)} failed: {errors[:5]}{'...' if len(errors) > 5 else ''}")

        return result

    except KeyError as e:
        logger.error(f"Missing required key in components JSON: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in components file: {e}")
        return {}
    except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.error(f"loading/parsing components json: {type(e).__name__}: {e}")
        return {}


def load_components(file_path="data/components.json", *, registry_provider=None):
    """
    Load components from JSON and populate the global registry.

    Wrapper around load_components_data() that also populates the registry.

    PROJ-211: registry_provider is now required (no fallback).

    Args:
        file_path: Path to the components JSON file.
        registry_provider: IRegistryProvider for DI. Required.
    """
    import os
    import copy
    from game.core.registry import GameRegistries

    if registry_provider is None:
        raise ValueError("registry_provider is required (PROJ-211: no fallback)")

    cache_mgr = ComponentCacheManager.instance()
    comps = registry_provider.get_components()

    # If cache exists and matches file_path, hydrate Registry from cache (Fast Path)
    if cache_mgr.component_cache is not None and cache_mgr.last_component_file == file_path:
        for c_id, comp in cache_mgr.component_cache.items():
            comps[c_id] = comp.clone()
        return

    # Slow Path: Load from Disk using pure function with explicit registries
    registries = GameRegistries(
        components=comps,
        modifiers=registry_provider.get_modifiers(),
        vehicle_classes=registry_provider.get_vehicle_classes(),
        resources={}
    )
    result = load_components_data(file_path, registries=registries)
    if not result:
        return

    # Populate Cache
    cache_mgr.component_cache = result
    cache_mgr.last_component_file = file_path

    # Populate Registry from Cache
    for c_id, comp in cache_mgr.component_cache.items():
        comps[c_id] = comp.clone()

def load_modifiers_data(file_path: str = "data/modifiers.json") -> dict:
    """
    Pure function to load modifiers from JSON file.

    PROJ-38: Returns a dictionary of Modifier objects keyed by ID without
    modifying any global state. Use this for DI patterns.

    Args:
        file_path: Path to the modifiers JSON file

    Returns:
        Dict[str, Modifier]: Modifier objects keyed by their ID
    """
    import os
    import copy
    from game.simulation.components.modifier_schema import validate_modifier_v2

    # Try absolute path based on this file if CWD fails
    if not os.path.exists(file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, file_path)
        if os.path.exists(abs_path):
            file_path = abs_path
        else:
            logger.error(f"modifiers file not found at {abs_path}")
            return {}

    try:
        data = load_json_required(file_path)

        result = {}
        errors = []
        for mod_def in data['modifiers']:
            mod_id = mod_def.get('id', 'unknown')
            # Validate modifier schema (graceful degradation - warn but continue)
            if not validate_modifier_v2(mod_def):
                logger.warning(f"Modifier '{mod_id}' failed schema validation, loading anyway")
            try:
                mod = Modifier(mod_def)
                result[mod.id] = copy.deepcopy(mod)
            except (KeyError, TypeError, ValueError) as e:
                logger.error(f"Modifier '{mod_id}': invalid data - {e}")
                errors.append(mod_id)

        if errors:
            logger.warning(f"Loaded {len(result)} modifiers, {len(errors)} failed: {errors[:5]}{'...' if len(errors) > 5 else ''}")

        return result

    except KeyError as e:
        logger.error(f"Missing required key in modifiers JSON: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in modifiers file: {e}")
        return {}
    except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
        logger.error(f"loading modifiers: {type(e).__name__}: {e}")
        return {}


def load_modifiers(file_path="data/modifiers.json", *, registry_provider=None):
    """
    Load modifiers from JSON and populate the global registry.

    Wrapper around load_modifiers_data() that also populates the registry.

    PROJ-211: registry_provider is now required (no fallback).

    Args:
        file_path: Path to the modifiers JSON file.
        registry_provider: IRegistryProvider for DI. Required.
    """
    import os
    import copy

    if registry_provider is None:
        raise ValueError("registry_provider is required (PROJ-211: no fallback)")

    cache_mgr = ComponentCacheManager.instance()
    mods = registry_provider.get_modifiers()

    # Fast Path
    if cache_mgr.modifier_cache is not None and cache_mgr.last_modifier_file == file_path:
        for m_id, mod in cache_mgr.modifier_cache.items():
            mods[m_id] = copy.deepcopy(mod)
        return

    # Slow Path: Load using pure function
    result = load_modifiers_data(file_path)
    if not result:
        return

    cache_mgr.modifier_cache = result
    cache_mgr.last_modifier_file = file_path

    for m_id, mod in cache_mgr.modifier_cache.items():
        mods[m_id] = copy.deepcopy(mod)

def create_component(component_id, *, registries: 'GameRegistries'):
    """Create a clone of a component from the registry by ID.

    PROJ-50: Strict DI - registries is required.

    Args:
        component_id: The ID of the component to create
        registries: GameRegistries for DI (required).

    Returns:
        Component clone or None if not found

    Raises:
        ValidationException: If registries is None
    """
    if registries is None:
        raise ValidationException(
            "registries is required for create_component",
            code=ErrorCode.MISSING_DEPENDENCY.value,
            context={"function": "create_component", "parameter": "registries"}
        )
    comps = registries.components

    if component_id in comps:
        clone = comps[component_id].clone()
        # PROJ-50: Ensure clone has correct registries
        clone._registries = registries
        return clone
    logger.error(f"Component ID {component_id} not found in registry.")
    return None

def get_all_components(*, registries: 'GameRegistries'):
    """Get a list of all components in the registry.

    PROJ-50: Strict DI - registries is required.

    Args:
        registries: GameRegistries for DI (required).

    Returns:
        List of all Component instances in the registry.

    Raises:
        ValidationException: If registries is None
    """
    if registries is None:
        raise ValidationException(
            "registries is required for get_all_components",
            code=ErrorCode.MISSING_DEPENDENCY.value,
            context={"function": "get_all_components", "parameter": "registries"}
        )
    return list(registries.components.values())

