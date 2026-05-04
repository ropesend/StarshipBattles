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
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from game.core.constants import CombatConstants
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)
from .component_constants import ComponentStatus
from .ability_manager import AbilityManager
from .modifier_manager import ModifierManager
from .component_stats_calculator import ComponentStatsCalculator
from .component_resource_manager import ComponentResourceManager
from .component_health_manager import ComponentHealthManager

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.components.abilities.base import Ability
    from game.simulation.components.component_constants import ApplicationModifier

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
        self._is_operational = True # Tracks if component has resources to operate

        # Combat statistics (weapons)
        self.shots_fired = 0
        self.shots_hit = 0

        # Helper managers (PROJ-88, PROJ-241)
        # AbilityManager is eager (abilities needed during construction)
        # Resource/Health/Modifier managers are lazy-initialized
        self._ability_mgr: AbilityManager = AbilityManager(self)
        self._resource_mgr: ComponentResourceManager | None = None
        self._health_mgr: ComponentHealthManager | None = None
        self._modifier_mgr: ModifierManager | None = None
                    
        # Parse formulas and set safe defaults for formula-driven attributes (PROJ-241)
        self.formulas = ComponentStatsCalculator.parse_formulas(self.data)
        ComponentStatsCalculator.apply_formula_defaults(self, self.formulas)

    @property
    def ability_manager(self) -> AbilityManager:
        """Ability manager delegate. PROJ-241."""
        return self._ability_mgr

    @property
    def ability_instances(self) -> List["Ability"]:
        """Facade: access ability instances through delegate. PROJ-241."""
        return self._ability_mgr.ability_instances

    @ability_instances.setter
    def ability_instances(self, value: List["Ability"]) -> None:
        """Facade: setter for backward compat (test code assigns lists). PROJ-241."""
        self._ability_mgr._instances = value

    def get_abilities(self, ability_name: str) -> List["Ability"]:
        """Get all abilities of a specific type. Delegates to ability_manager."""
        return self._ability_mgr.get_abilities(ability_name)

    def get_ability(self, ability_name: str) -> Optional["Ability"]:
        """Get first ability of type. Delegates to ability_manager."""
        return self._ability_mgr.get_ability(ability_name)

    def has_ability(self, ability_name: str) -> bool:
        """Check if component has ability. Delegates to ability_manager."""
        return self._ability_mgr.has_ability(ability_name)

    def has_pdc_ability(self) -> bool:
        """Check if component has a Point Defense weapon ability. Delegates to ability_manager."""
        return self._ability_mgr.has_pdc_ability()

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

    @property
    def modifier_manager(self) -> ModifierManager:
        """Lazy-initialized modifier manager. PROJ-241."""
        if self._modifier_mgr is None:
            self._modifier_mgr = ModifierManager(self)
        return self._modifier_mgr

    @property
    def modifiers(self) -> List["ApplicationModifier"]:
        """Facade: access modifier list through delegate. PROJ-241."""
        return self.modifier_manager.modifiers

    @modifiers.setter
    def modifiers(self, value: List["ApplicationModifier"]) -> None:
        """Facade: setter for backward compat during transition. PROJ-241."""
        self.modifier_manager._modifiers = value

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
    def cooldown_timer(self) -> float:
        # Map to first weapon ability if present
        ab = self.get_ability('WeaponAbility')
        if ab: return ab.cooldown_timer
        return 0.0

    @cooldown_timer.setter
    def cooldown_timer(self, value: float) -> None:
        ab = self.get_ability('WeaponAbility')
        if ab: ab.cooldown_timer = float(value)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        """Aggregate UI rows from all ability instances.

        Returns list of dicts: [{'label': 'Thrust', 'value': '1500 N'}, ...]
        Used by detail panels and capability scanners.
        Delegates to AbilityManager.
        """
        return self._ability_mgr.get_ui_rows()

    def _instantiate_abilities(self) -> None:
        """Re-instantiate and re-index abilities. Delegates to ability_manager.

        Called by ComponentStatsCalculator.recalculate to sync ability
        instances after data changes (e.g., modifier effects on abilities).
        """
        self._ability_mgr.instantiate_and_index()

    def update(self) -> None:
        """Update component state for one tick (resource consumption, cooldowns).

        Any ability returning False from update() marks the component as
        non-operational. This covers:
        - ResourceConsumption (constant trigger): resource starved
        - RequiresCommandAndControl: no C&C provider on ship
        - Any future requirement-style abilities
        """
        all_satisfied = True

        for ability in self.ability_instances:
            if not ability.update():
                # Activation-trigger resources (per-shot) don't affect
                # operational status — they're checked at fire time.
                trigger = getattr(ability, 'trigger', None)
                if trigger == 'activation':
                    continue
                all_satisfied = False

        self._is_operational = all_satisfied and self.is_active

    @property
    def is_operational(self) -> bool:
        return self._is_operational and self.is_active

    def can_afford_activation(self) -> bool:
        """Check if component can afford activation costs. Delegates to resource_manager."""
        return self.resource_manager.can_afford_activation()

    def consume_activation(self) -> None:
        """Consume activation costs. Delegates to resource_manager."""
        self.resource_manager.consume_activation()

    def try_activate(self) -> bool:
        """Check and consume activation costs atomically. Delegates to resource_manager."""
        return self.resource_manager.try_activate()




    def take_damage(self, amount: float) -> bool:
        """Apply damage to component. Delegates to health_manager."""
        return self.health_manager.take_damage(amount)

    def reset_hp(self) -> None:
        """Restore component to full HP. Delegates to health_manager."""
        self.health_manager.reset_hp()

    def get_resource_cost(self, context: Optional[dict] = None) -> dict:
        """Returns the current resource costs. Delegates to resource_manager."""
        return self.resource_manager.get_resource_cost(context)

    def add_modifier(self, mod_id: str, value: Optional[float] = None) -> bool:
        """Add a modifier to this component. Delegates to modifier_manager."""
        result = self.modifier_manager.add_modifier(mod_id, value)
        if result:
            self.recalculate_stats()
        return result

    def remove_modifier(self, mod_id: str) -> None:
        """Remove a modifier from this component. Delegates to modifier_manager."""
        self.modifier_manager.remove_modifier(mod_id)
        self.recalculate_stats()

    def get_modifier(self, mod_id: str) -> Optional["ApplicationModifier"]:
        """Get a modifier by ID. Delegates to modifier_manager."""
        return self.modifier_manager.get_modifier(mod_id)

    def get_all_modifier_effects(self) -> List[Any]:
        """Get all evaluated effects from all applied modifiers.

        Delegates to modifier_manager.

        Returns:
            List[ModifierEffect]: All effects from all modifiers on this component
        """
        return self.modifier_manager.get_all_effects()

    def get_modifier_stat_summary(self) -> Dict[str, Dict]:
        """Get summary grouped by stat with net values and contributors.

        Delegates to modifier_manager.

        Returns:
            Dict[str, Dict]: Mapping from stat_key to summary info
        """
        return self.modifier_manager.get_stat_summary()

    def recalculate_stats(self, context: Optional[dict] = None) -> None:
        """Recalculate component stats with multiplicative modifier stacking.

        Delegates to ComponentStatsCalculator for the multi-phase calculation.

        Args:
            context: Optional dict with context for formula evaluation.
                     Expected keys: 'ship_class_mass' (float).
                     If not provided, falls back to component.ship reference.
        """
        ComponentStatsCalculator.recalculate(self, context)

    def clone(self) -> "Component":
        # Propagate self.ship so clones of attached components evaluate
        # ship_class_mass formulas without callers having to set .ship
        # manually after every clone+recalc. Detached sources (ship is None,
        # e.g. registry templates and palette items) still produce detached
        # clones. See docs/guides/component_system.md.
        cloned = self.__class__(self.data, registries=self._registries)
        cloned.ship = self.ship
        return cloned


# All component types use Component directly via the ability system.
# Type-specific behavior is handled by ability instances (WeaponAbility, etc.)


# =============================================================================
# Re-exports from component_loader.py (extracted for module decomposition).
# Existing imports from this module continue to work.
# =============================================================================
from game.simulation.components.component_loader import (  # noqa: F401
    ComponentCacheManager,
    get_default_cache_manager,
    reset_component_caches,
    load_components_data,
    load_components,
    load_modifiers_data,
    load_modifiers,
    create_component,
    get_all_components,
)

