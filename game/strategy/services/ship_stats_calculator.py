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

from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
from game.core.constants import ResourceType
from game.core.registry import GameRegistries
from game.core.logger import log_warning

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider
from game.simulation.formula_system import safe_evaluate_math_formula
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
            TypeError: If registries is None.
        """
        if registries is None:
            raise TypeError("registries is required for ShipStatsCalculator")
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

            # Get abilities from component definition
            abilities = getattr(comp_def, 'abilities', {}) or {}

            # Get capacity multiplier for storage abilities
            capacity_mult = multipliers.get('capacity_mult', 1.0)

            # Resource Storage - degrades with damage (generic handling)
            for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'ResourceStorage'):
                resource_type = ability_data.get('resource', '')
                max_amount = ShipStatsCalculator._evaluate_value(
                    ability_data.get('max_amount') or ability_data.get('amount', 0), 0, formula_context
                )
                # Apply capacity multiplier from design modifiers
                max_amount *= capacity_mult
                if resource_type:
                    resource_storage[resource_type] = (
                        resource_storage.get(resource_type, 0) + max_amount * effectiveness
                    )

            # Cargo Storage - degrades with damage (generic handling)
            for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'CargoStorage'):
                cargo_type = ability_data.get('cargo_type', 'generic')
                capacity = ShipStatsCalculator._evaluate_value(
                    ability_data.get('capacity', 0), 0, formula_context
                )
                # Apply capacity multiplier from design modifiers
                capacity *= capacity_mult
                cargo_storage[cargo_type] = (
                    cargo_storage.get(cargo_type, 0) + capacity * effectiveness
                )

            # Strategic Movement - degrades with damage (with modifiers)
            if 'StrategicMovement' in abilities:
                movement = ShipStatsCalculator._get_ability_value(abilities, 'StrategicMovement', formula_context)
                movement *= multipliers.get('strategic_mult', 1.0)
                total_strategic_movement += movement * effectiveness

            # Get consumption multiplier for resource consumption abilities
            consumption_mult = multipliers.get('consumption_mult', 1.0)

            # Resource Consumption - generic handling by trigger type
            for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'ResourceConsumption'):
                resource_type = ability_data.get('resource', '')
                amount = ShipStatsCalculator._evaluate_value(ability_data.get('amount', 0), 0, formula_context)
                # Apply consumption multiplier from design modifiers
                amount *= consumption_mult
                trigger = ability_data.get('trigger', 'constant')

                if trigger == 'strategic_per_hex':
                    resource_consumption_per_hex[resource_type] = (
                        resource_consumption_per_hex.get(resource_type, 0) + amount * effectiveness
                    )
                elif trigger == 'per_turn':
                    resource_consumption_per_turn[resource_type] = (
                        resource_consumption_per_turn.get(resource_type, 0) + amount * effectiveness
                    )
                # Note: warp_jump trigger handled below with warp effectiveness

            # Warp Jump - requires 100% HP (effectiveness must be 1.0)
            if 'WarpJump' in abilities:
                warp_effectiveness = ShipStatsCalculator._get_warp_effectiveness(
                    comp_id, comp_def, component_damage
                )
                if warp_effectiveness > 0:
                    warp_data = abilities.get('WarpJump', {})
                    if isinstance(warp_data, dict):
                        # Evaluate formulas for max_tonnage (e.g., "=ship_class_mass")
                        tonnage = ShipStatsCalculator._evaluate_value(
                            warp_data.get('max_tonnage', 0), 0, formula_context
                        )
                    else:
                        tonnage = ShipStatsCalculator._evaluate_value(
                            warp_data, 0, formula_context
                        ) if isinstance(warp_data, str) and warp_data.startswith("=") else (
                            warp_data if isinstance(warp_data, (int, float)) else 0
                        )

                    # Use largest warp drive tonnage
                    if tonnage > warp_max_tonnage:
                        warp_max_tonnage = int(tonnage)

                    # Warp resource costs from ResourceConsumption with trigger='warp_jump'
                    for ability_data in ShipStatsCalculator._get_ability_list(abilities, 'ResourceConsumption'):
                        if ability_data.get('trigger') == 'warp_jump':
                            resource_type = ability_data.get('resource', '')
                            # Evaluate formulas for amount (e.g., "=5 * (ship_class_mass ** (2/3))")
                            amount = ShipStatsCalculator._evaluate_value(
                                ability_data.get('amount', 0), 0, formula_context
                            )
                            warp_resource_costs[resource_type] = (
                                warp_resource_costs.get(resource_type, 0) + amount
                            )

        return {
            'max_hp': int(total_hp),
            'mass': total_mass,
            # New generic fields
            'resource_storage': resource_storage,
            'cargo_storage': cargo_storage,
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
        comp_type = getattr(comp_def, 'type_str', '')
        if comp_type in NON_DEGRADING_TYPES:
            return 1.0

        # Check for 'Armor' ability marker
        abilities = getattr(comp_def, 'abilities', {}) or {}
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
        threshold = getattr(comp_def, 'damage_threshold', DEFAULT_DAMAGE_THRESHOLD)

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
        layers = design_data.get('layers', {})
        component_registry = self._registries.components

        for layer_name, layer_components in layers.items():
            # Direct list format: layers[layer_name] = [comp1, comp2, ...]
            if not isinstance(layer_components, list):
                continue

            for comp_entry in layer_components:
                comp_id = comp_entry.get('id', '')
                comp_def = component_registry.get(comp_id)

                if comp_def is None:
                    log_warning(f"Component '{comp_id}' not found in registry, skipping")
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
        val = getattr(obj, attr, default)
        return ShipStatsCalculator._evaluate_value(val, default, context)

    @staticmethod
    def _evaluate_value(val: Any, default: float, context: Optional[Dict[str, Any]] = None) -> float:
        """Evaluate a value that may be a formula string."""
        if val is None:
            return default
        if isinstance(val, str):
            if val.startswith("=") and context:
                result = safe_evaluate_math_formula(val[1:], context, default=default)
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

        warp_energy_cost = warp_resource_costs.get(ResourceType.ENERGY, 0)
        if warp_energy_cost > 0:
            max_energy = resource_storage.get(ResourceType.ENERGY, 0)
            if max_energy < warp_energy_cost:
                return False

        warp_fuel_cost = warp_resource_costs.get(ResourceType.FUEL, 0)
        if warp_fuel_cost > 0:
            max_fuel = resource_storage.get(ResourceType.FUEL, 0)
            if max_fuel < warp_fuel_cost:
                return False

        return True
