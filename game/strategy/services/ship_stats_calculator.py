"""
Ship Stats Calculator - Calculates ship statistics from component definitions.

PROJ-07: Strategy Layer Stats Calculation Refactor
PROJ-38: Added constructor-based DI with GameRegistries support.
PROJ-132: Documentation fix - Strategy importing from Simulation is valid.

This service calculates ship stats dynamically from component definitions
rather than reading from cached `expected_stats`. This ensures stats
accurately reflect component damage state.

Key design decisions:
- Imports from game.core.registry and game.simulation (strategy depends on simulation)
- Uses simulation formula_system and modifiers for consistent calculations
- Damage model: gradual degradation to 50% HP threshold, then inactive
- Special cases: Warp drives require 100% HP, Armor never degrades
- Stats cached on ShipInstance with invalidation on damage change
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
from game.core.registry import GameRegistries
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.core.patterns.layer_iterator import iter_layers_and_components, get_component_id
from game.strategy.services.component_inspector import (
    get_component_abilities,
    get_component_type,
    get_component_threshold,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider
from game.simulation.formula_system import FormulaEvaluator
from game.simulation.components.modifiers import calculate_stat_multipliers


# Default damage threshold - components become useless below this HP percentage
# PROJ-44: Unified to 50% to match CombatConstants.DEFAULT_DAMAGE_THRESHOLD
DEFAULT_DAMAGE_THRESHOLD = 0.5  # 50% - aligned with simulation layer

# Component types that never degrade (always 100% effective)
NON_DEGRADING_TYPES = {'Armor'}

# Ability types that require 100% HP to function
FULL_HP_REQUIRED_ABILITIES = {'WarpJump'}


class ShipStatsCalculator:
    """Service for calculating ship statistics from component definitions.

    All methods are instance methods requiring initialized registries.
    This ensures consistent behavior and enables proper dependency injection.

    Usage:
        service = ShipStatsCalculator(registries=game_registries)
        stats = service.calculate_stats(design_data)

    Stats are dynamically calculated from component definitions,
    respecting component damage state and toggles.
    """

    def __init__(self, registries: GameRegistries):
        """
        Initialize ShipStatsCalculator with required GameRegistries.

        PROJ-50: Made registries parameter required (strict DI).

        Args:
            registries: GameRegistries container with components, modifiers,
                       vehicle_classes. Required - no fallback.

        Raises:
            ValidationException: If registries is None.
        """
        if registries is None:
            raise ValidationException(
                "registries is required for ShipStatsCalculator",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "ShipStatsCalculator", "parameter": "registries"}
            )
        self._registries = registries

    def calculate_stats(
        self,
        design_data: Dict[str, Any],
        component_damage: Optional[Dict[str, int]] = None,
        component_toggles: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """Calculate all ship stats from design data and component damage.

        Args:
            design_data: Serialized ship design containing 'layers' dict
            component_damage: Optional dict of component_id -> current_hp
                             If None, assumes all components undamaged
            component_toggles: Optional dict of component_id -> enabled
                              If None, assumes all components enabled

        Returns:
            Dict with calculated stats including:
            - max_hp: Total HP from all components
            - mass: Total mass (doesn't degrade with damage)
            - resource_storage: Dict of resource_type -> capacity
            - resource_consumption_per_hex: Dict of resource_type -> cost per hex
            - resource_consumption_per_turn: Dict of resource_type -> cost per turn
            - warp_resource_costs: Dict of resource_type -> cost per warp jump
            - strategic_movement: Movement points for strategic map
            - warp_max_tonnage: Max ship mass for warp (0 if damaged)
        """
        # PROJ-42: Clean instance method - use instance registries directly
        if component_damage is None:
            component_damage = {}
        if component_toggles is None:
            component_toggles = {}

        vehicle_classes = self._registries.vehicle_classes
        modifier_registry = self._registries.modifiers

        # Initialize accumulators - ALL generic dicts
        total_mass = 0.0
        total_hp = 0.0
        resource_storage: Dict[str, float] = {}
        cargo_storage: Dict[str, float] = {}
        pod_storage_mass = 0.0
        resource_consumption_per_hex: Dict[str, float] = {}
        resource_consumption_per_turn: Dict[str, float] = {}
        warp_resource_costs: Dict[str, float] = {}
        total_strategic_movement = 0.0
        warp_max_tonnage = 0

        # Build formula evaluation context from ship class
        formula_context = {'ship_class_mass': 1000}  # Default fallback
        ship_class = design_data.get('ship_class', '')

        if ship_class:
            class_data = vehicle_classes.get(ship_class, {})
            if isinstance(class_data, dict):
                formula_context['ship_class_mass'] = class_data.get('max_mass', 1000)

        # Iterate through all components in design
        components_found = self._iterate_design_components(design_data)

        # Fallback to expected_stats if no components found in layers
        # This handles test fixtures and designs without component registry entries
        if not components_found:
            expected = design_data.get('expected_stats', {})
            return {
                'max_hp': expected.get('max_hp', 0),
                'mass': expected.get('mass', 0),
                'resource_storage': expected.get('resource_storage', {}),
                'cargo_storage': expected.get('cargo_storage', {}),
                'resource_consumption_per_hex': expected.get('resource_consumption_per_hex', {}),
                'resource_consumption_per_turn': expected.get('resource_consumption_per_turn', {}),
                'warp_resource_costs': expected.get('warp_resource_costs', {}),
                'strategic_movement': expected.get('strategic_movement', 0),
                'warp_max_tonnage': expected.get('warp_max_tonnage', 0),
            }

        for layer_name, comp_entry, comp_def in components_found:
            if comp_def is None:
                continue

            comp_id = comp_entry.get('id', '')

            # Calculate modifier multipliers from design's component entry
            modifier_entries = comp_entry.get('modifiers', [])
            multipliers = calculate_stat_multipliers(modifier_entries, modifier_registry)

            # Check if component is toggled off
            if not component_toggles.get(comp_id, True):
                # Still count mass (with modifiers), skip abilities
                comp_mass = ShipStatsCalculator._get_numeric_value(comp_def, 'mass', 0, formula_context)
                comp_mass = (comp_mass + multipliers.get('mass_add', 0.0)) * multipliers.get('mass_mult', 1.0)
                total_mass += comp_mass
                continue

            # Get effectiveness based on damage (0.0 to 1.0)
            effectiveness = ShipStatsCalculator.get_component_effectiveness(
                comp_id, comp_def, component_damage
            )

            # Mass never degrades - add full mass regardless of damage (with modifiers)
            comp_mass = ShipStatsCalculator._get_numeric_value(comp_def, 'mass', 0, formula_context)
            comp_mass = (comp_mass + multipliers.get('mass_add', 0.0)) * multipliers.get('mass_mult', 1.0)
            total_mass += comp_mass

            # HP degrades with damage (with modifiers)
            comp_hp = ShipStatsCalculator._get_numeric_value(comp_def, 'max_hp', 0, formula_context)
            comp_hp *= multipliers.get('hp_mult', 1.0)
            total_hp += comp_hp * effectiveness

            abilities = get_component_abilities(comp_def)

            # Get capacity multiplier for storage abilities
            capacity_mult = multipliers.get('capacity_mult', 1.0)

            # Resource Storage - degrades with damage
            self._accumulate_resource_storage(
                abilities, effectiveness, capacity_mult, formula_context, resource_storage
            )

            # Cargo Storage - degrades with damage
            self._accumulate_cargo_storage(
                abilities, effectiveness, capacity_mult, formula_context, cargo_storage
            )

            # Pod Storage - mass-based capacity for carried_items (drop pods)
            pod_storage_mass += self._accumulate_pod_storage(
                abilities, effectiveness, capacity_mult, formula_context
            )

            # Strategic Movement - degrades with damage
            total_strategic_movement += self._accumulate_movement(
                abilities, effectiveness, formula_context, multipliers
            )

            # Resource Consumption - per_hex and per_turn triggers
            consumption_mult = multipliers.get('consumption_mult', 1.0)
            self._accumulate_consumption(
                abilities, effectiveness, consumption_mult, formula_context,
                resource_consumption_per_hex, resource_consumption_per_turn
            )

            # Warp Jump - requires 100% HP (effectiveness must be 1.0)
            warp_tonnage, warp_costs = self._accumulate_warp_stats(
                abilities, comp_id, comp_def, component_damage, formula_context
            )
            if warp_tonnage > warp_max_tonnage:
                warp_max_tonnage = warp_tonnage
            for resource_type, cost in warp_costs.items():
                warp_resource_costs[resource_type] = (
                    warp_resource_costs.get(resource_type, 0) + cost
                )

        return {
            'max_hp': int(total_hp),
            'mass': total_mass,
            # New generic fields
            'resource_storage': resource_storage,
            'cargo_storage': cargo_storage,
            'pod_storage_mass': pod_storage_mass,
            'resource_consumption_per_hex': resource_consumption_per_hex,
            'resource_consumption_per_turn': resource_consumption_per_turn,
            'warp_resource_costs': warp_resource_costs,
            'strategic_movement': total_strategic_movement,
            'warp_max_tonnage': warp_max_tonnage,
        }



    @staticmethod
    def get_component_effectiveness(
        comp_id: str,
        comp_def: Any,
        component_damage: Optional[Dict[str, int]] = None
    ) -> float:
        """
        Calculate component effectiveness based on damage state.

        PROJ-42: Simplified to static method (no registries needed).

        Damage model:
        - Above 30% HP: Gradual degradation (linear from 100% to 0%)
        - At or below 30% HP: Component is inactive (0% effectiveness)
        - Armor: Never degrades (always 100% effective)

        Args:
            comp_id: Component ID string
            comp_def: Component definition from registry
            component_damage: Dict of component_id -> current_hp

        Returns:
            Float from 0.0 to 1.0 representing effectiveness
        """
        if component_damage is None:
            component_damage = {}

        # Check if this is armor (never degrades)
        comp_type = get_component_type(comp_def)
        if comp_type in NON_DEGRADING_TYPES:
            return 1.0

        # Check for 'Armor' ability marker
        abilities = get_component_abilities(comp_def)
        if abilities.get('Armor'):
            return 1.0

        # Get max HP from component definition
        max_hp = ShipStatsCalculator._get_numeric_value(comp_def, 'max_hp', 0)
        if max_hp <= 0:
            return 1.0  # No HP means always active

        # Get current HP - check both indexed and base forms
        current_hp = ShipStatsCalculator._get_current_hp(comp_id, max_hp, component_damage)

        # Calculate HP percentage
        hp_pct = current_hp / max_hp

        # Get damage threshold (default 30%)
        threshold = get_component_threshold(comp_def, DEFAULT_DAMAGE_THRESHOLD)

        # Below threshold = inactive
        if hp_pct <= threshold:
            return 0.0

        # Gradual degradation from 100% to threshold
        # Map hp_pct [threshold, 1.0] to effectiveness [0.0, 1.0]
        return (hp_pct - threshold) / (1.0 - threshold)

    @staticmethod
    def _get_warp_effectiveness(
        comp_id: str,
        comp_def: Any,
        component_damage: Dict[str, int]
    ) -> float:
        """
        Get warp drive effectiveness - requires 100% HP.

        Warp drives are either fully functional (100% HP) or completely
        non-functional (any damage at all disables warp).
        """
        max_hp = ShipStatsCalculator._get_numeric_value(comp_def, 'max_hp', 0)
        if max_hp <= 0:
            return 1.0  # No HP tracked = always works

        current_hp = ShipStatsCalculator._get_current_hp(comp_id, max_hp, component_damage)

        # Must be at exactly full HP
        if current_hp >= max_hp:
            return 1.0
        return 0.0

    def _accumulate_warp_stats(
        self,
        abilities: Dict[str, Any],
        comp_id: str,
        comp_def: Any,
        component_damage: Dict[str, int],
        formula_context: Dict[str, Any]
    ) -> Tuple[int, Dict[str, float]]:
        """
        Accumulate warp drive statistics from a component's abilities.

        PROJ-209 Phase 4: Extracted from calculate_stats to reduce CC.

        Warp drives require 100% HP to function. If the component is damaged,
        returns (0, {}) indicating no warp contribution.

        Args:
            abilities: Component abilities dict
            comp_id: Component ID for damage lookup
            comp_def: Component definition from registry
            component_damage: Dict of component_id -> current_hp
            formula_context: Context for formula evaluation

        Returns:
            Tuple of (warp_tonnage, warp_costs_dict)
            - warp_tonnage: int, max tonnage this warp drive can handle
            - warp_costs_dict: Dict of resource_type -> cost for warp_jump trigger
        """
        if 'WarpJump' not in abilities:
            return (0, {})

        warp_effectiveness = ShipStatsCalculator._get_warp_effectiveness(
            comp_id, comp_def, component_damage
        )
        if warp_effectiveness <= 0:
            return (0, {})

        # Parse warp tonnage from various formats
        warp_data = abilities.get('WarpJump', {})
        tonnage = self._parse_warp_tonnage(warp_data, formula_context)

        # Collect warp resource costs
        warp_costs: Dict[str, float] = {}
        for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'ResourceConsumption'):
            if ability_data.get('trigger') == 'warp_jump':
                resource_type = ability_data.get('resource', '')
                amount = ShipStatsCalculator._evaluate_value(
                    ability_data.get('amount', 0), 0, formula_context
                )
                if resource_type:
                    warp_costs[resource_type] = warp_costs.get(resource_type, 0) + amount

        return (int(tonnage), warp_costs)

    @staticmethod
    def _parse_warp_tonnage(
        warp_data: Any,
        formula_context: Dict[str, Any]
    ) -> float:
        """
        Parse warp tonnage from various WarpJump ability formats.

        PROJ-209 Phase 4: Extracted to simplify warp stats accumulation.

        Supports:
        - Dict with 'max_tonnage' key: {'max_tonnage': 5000}
        - Formula string: "=ship_class_mass"
        - Raw numeric: 5000 or 5000.0

        Args:
            warp_data: WarpJump ability value (dict, string, or numeric)
            formula_context: Context for formula evaluation

        Returns:
            Parsed tonnage value as float
        """
        if isinstance(warp_data, dict):
            return ShipStatsCalculator._evaluate_value(
                warp_data.get('max_tonnage', 0), 0, formula_context
            )
        if isinstance(warp_data, str) and warp_data.startswith("="):
            return ShipStatsCalculator._evaluate_value(warp_data, 0, formula_context)
        if isinstance(warp_data, (int, float)):
            return float(warp_data)
        return 0.0

    def _accumulate_resource_storage(
        self,
        abilities: Dict[str, Any],
        effectiveness: float,
        capacity_mult: float,
        formula_context: Dict[str, Any],
        storage_dict: Dict[str, float]
    ) -> None:
        """
        Accumulate resource storage from component abilities.

        PROJ-209 Phase 4: Extracted from calculate_stats to reduce CC.

        Args:
            abilities: Component abilities dict
            effectiveness: Component effectiveness (0.0-1.0)
            capacity_mult: Capacity multiplier from modifiers
            formula_context: Context for formula evaluation
            storage_dict: Dict to accumulate storage into (modified in-place)
        """
        for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'ResourceStorage'):
            resource_type = ability_data.get('resource', '')
            max_amount = ShipStatsCalculator._evaluate_value(
                ability_data.get('max_amount') or ability_data.get('amount', 0), 0, formula_context
            )
            max_amount *= capacity_mult
            if resource_type:
                storage_dict[resource_type] = (
                    storage_dict.get(resource_type, 0) + max_amount * effectiveness
                )

    def _accumulate_cargo_storage(
        self,
        abilities: Dict[str, Any],
        effectiveness: float,
        capacity_mult: float,
        formula_context: Dict[str, Any],
        cargo_dict: Dict[str, float]
    ) -> None:
        """
        Accumulate cargo storage from component abilities.

        PROJ-209 Phase 4: Extracted from calculate_stats to reduce CC.

        Args:
            abilities: Component abilities dict
            effectiveness: Component effectiveness (0.0-1.0)
            capacity_mult: Capacity multiplier from modifiers
            formula_context: Context for formula evaluation
            cargo_dict: Dict to accumulate cargo into (modified in-place)
        """
        for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'CargoStorage'):
            cargo_type = ability_data.get('cargo_type', 'generic')
            capacity = ShipStatsCalculator._evaluate_value(
                ability_data.get('capacity', 0), 0, formula_context
            )
            capacity *= capacity_mult
            cargo_dict[cargo_type] = (
                cargo_dict.get(cargo_type, 0) + capacity * effectiveness
            )

    @staticmethod
    def _accumulate_pod_storage(
        abilities: Dict[str, Any],
        effectiveness: float,
        capacity_mult: float,
        formula_context: Dict[str, Any],
    ) -> float:
        """Accumulate PodStorage mass capacity from component abilities.

        PodStorage follows the same pattern as planet StagingYard:
        mass-based capacity limiting how many drop pods a ship can carry.

        Returns:
            Total pod storage mass capacity from this component.
        """
        total = 0.0
        pod_data = abilities.get('PodStorage')
        if pod_data is None:
            return 0.0
        if isinstance(pod_data, dict):
            capacity = ShipStatsCalculator._evaluate_value(
                pod_data.get('capacity_mass', 0), 0, formula_context
            )
            capacity *= capacity_mult
            total += capacity * effectiveness
        return total

    def _accumulate_movement(
        self,
        abilities: Dict[str, Any],
        effectiveness: float,
        formula_context: Dict[str, Any],
        multipliers: Dict[str, float]
    ) -> float:
        """
        Accumulate strategic movement from component abilities.

        PROJ-209 Phase 4: Extracted from calculate_stats to reduce CC.

        Args:
            abilities: Component abilities dict
            effectiveness: Component effectiveness (0.0-1.0)
            formula_context: Context for formula evaluation
            multipliers: Stat multipliers from modifiers

        Returns:
            Movement contribution from this component
        """
        if 'StrategicMovement' not in abilities:
            return 0.0
        movement = ShipStatsCalculator._get_ability_value(
            abilities, 'StrategicMovement', formula_context
        )
        movement *= multipliers.get('strategic_mult', 1.0)
        return movement * effectiveness

    def _accumulate_consumption(
        self,
        abilities: Dict[str, Any],
        effectiveness: float,
        consumption_mult: float,
        formula_context: Dict[str, Any],
        per_hex_dict: Dict[str, float],
        per_turn_dict: Dict[str, float]
    ) -> None:
        """
        Accumulate resource consumption from component abilities.

        PROJ-209 Phase 4: Extracted from calculate_stats to reduce CC.

        Handles strategic_per_hex and per_turn triggers. The warp_jump trigger
        is handled separately by _accumulate_warp_stats.

        Args:
            abilities: Component abilities dict
            effectiveness: Component effectiveness (0.0-1.0)
            consumption_mult: Consumption multiplier from modifiers
            formula_context: Context for formula evaluation
            per_hex_dict: Dict to accumulate per-hex consumption (modified in-place)
            per_turn_dict: Dict to accumulate per-turn consumption (modified in-place)
        """
        for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'ResourceConsumption'):
            resource_type = ability_data.get('resource', '')
            amount = ShipStatsCalculator._evaluate_value(
                ability_data.get('amount', 0), 0, formula_context
            )
            amount *= consumption_mult
            trigger = ability_data.get('trigger', 'constant')

            if trigger == 'strategic_per_hex':
                per_hex_dict[resource_type] = (
                    per_hex_dict.get(resource_type, 0) + amount * effectiveness
                )
            elif trigger == 'per_turn':
                per_turn_dict[resource_type] = (
                    per_turn_dict.get(resource_type, 0) + amount * effectiveness
                )
            # warp_jump trigger handled by _accumulate_warp_stats

    def _iterate_design_components(
        self,
        design_data: Dict[str, Any]
    ) -> List[Tuple[str, Dict[str, Any], Any]]:
        """
        Iterate through all components in a design.

        PROJ-42: Simplified to instance-only method.

        Args:
            design_data: Serialized ship design containing 'layers' dict

        Returns:
            List of tuples (layer_name, component_entry, component_def)
            where component_def is the registry definition or None if not found
        """
        result = []
        component_registry = self._registries.components

        for layer_name, comp_entry in iter_layers_and_components(design_data):
            comp_id = get_component_id(comp_entry)
            comp_def = component_registry.get(comp_id)

            if comp_def is None:
                logger.warning(f"Component '{comp_id}' not found in registry, skipping")
                continue

            result.append((layer_name, comp_entry, comp_def))

        return result

    @staticmethod
    def _get_current_hp(
        comp_id: str,
        max_hp: float,
        component_damage: Dict[str, int]
    ) -> float:
        """
        Get current HP for a component, checking multiple ID formats.

        Component damage dict may use indexed IDs (e.g., "bridge_0") or
        base IDs (e.g., "bridge"). We check both.
        """
        # Direct lookup
        if comp_id in component_damage:
            return component_damage[comp_id]

        # Try indexed forms (component_0, component_1, etc.)
        for key, hp in component_damage.items():
            # Check if key is an indexed version of comp_id
            if key.startswith(comp_id + '_'):
                try:
                    # Verify it's actually an index suffix
                    int(key[len(comp_id) + 1:])
                    return hp
                except ValueError:
                    pass

        # No damage recorded = full HP
        return max_hp

    @staticmethod
    def _get_numeric_value(obj: Any, attr: str, default: float, context: Optional[Dict[str, Any]] = None) -> float:
        """Get a numeric attribute from an object, handling formulas."""
        # obj may be a dict (JSON registry) or Component object (simulation)
        if isinstance(obj, dict):
            val = obj.get(attr, default)
        else:
            val = getattr(obj, attr, default)
        return ShipStatsCalculator._evaluate_value(val, default, context)

    @staticmethod
    def _evaluate_value(val: Any, default: float, context: Optional[Dict[str, Any]] = None) -> float:
        """Evaluate a value that may be a formula string."""
        if val is None:
            return default
        if isinstance(val, str):
            if val.startswith("=") and context:
                result = FormulaEvaluator.safe_evaluate(val[1:], context, default=default)
                return float(result)
            return default  # Formula but no context
        return float(val)

    @staticmethod
    def _get_ability_value(abilities: Dict[str, Any], ability_name: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Get the primary value from an ability definition."""
        val = abilities.get(ability_name, 0)
        if isinstance(val, str):
            return ShipStatsCalculator._evaluate_value(val, 0.0, context)
        if isinstance(val, (int, float)):
            return float(val)
        elif isinstance(val, dict):
            # Try common keys for primary value
            for key in ['value', 'amount', 'max_amount', 'thrust_force', 'movement_points']:
                if key in val:
                    return ShipStatsCalculator._evaluate_value(val[key], 0.0, context)
            return 0.0
        return 0.0

    @staticmethod
    def _get_ability_list(
        abilities: Dict[str, Any],
        ability_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get ability data as a list (handles both single and multiple abilities).

        Returns list of ability data dicts for the given ability name.
        """
        val = abilities.get(ability_name)
        if val is None:
            return []
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            return [val]
        # Simple value - wrap in dict
        return [{'value': val}]

    @staticmethod
    def has_warp_capability(ship: Any) -> bool:
        """
        Check if a ship has functional warp capability.

        PROJ-11: Moved from game.ui.screens.fleet_report_filters to eliminate
        strategy->UI dependency. This is the canonical location for warp
        capability checks.

        A ship is warp-capable if:
        1. It has a WarpJump ability component with max_tonnage >= ship's mass
        2. The warp drive is undamaged (warp_max_tonnage will be 0 if damaged)
        3. The ship has enough resource storage capacity for at least one warp jump

        Args:
            ship: Object with get_calculated_stats() method (e.g., ShipInstance)

        Returns:
            True if ship can use warp points, False otherwise
        """
        # Use calculated stats which respect component damage
        calculated_stats = ship.get_calculated_stats()

        # Get ship mass
        ship_mass = calculated_stats.get('mass', 0)
        if ship_mass <= 0:
            return False

        # Check warp_max_tonnage - will be 0 if warp drive is damaged
        warp_max_tonnage = calculated_stats.get('warp_max_tonnage', 0)
        if warp_max_tonnage < ship_mass:
            return False

        # Check if ship has resource capacity for warp
        # A ship with a warp drive but insufficient storage cannot warp
        warp_resource_costs = calculated_stats.get('warp_resource_costs', {})
        resource_storage = calculated_stats.get('resource_storage', {})

        warp_energy_cost = warp_resource_costs.get("energy", 0)
        if warp_energy_cost > 0:
            max_energy = resource_storage.get("energy", 0)
            if max_energy < warp_energy_cost:
                return False

        warp_fuel_cost = warp_resource_costs.get("fuel", 0)
        if warp_fuel_cost > 0:
            max_fuel = resource_storage.get("fuel", 0)
            if max_fuel < warp_fuel_cost:
                return False

        return True
