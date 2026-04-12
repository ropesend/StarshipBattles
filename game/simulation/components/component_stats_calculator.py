"""
ComponentStatsCalculator - Stats calculation for components.

PROJ-44 Phase 4: Extracted from Component god class to reduce complexity.

This module provides utility functions for:
- Calculating modifier effects on component stats
- Evaluating formulas with context
- Applying stats to component properties

Usage:
    The Component class delegates stats calculation to this module.
    Methods are implemented as static methods for flexibility.
"""
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from game.core.formula_evaluator import FormulaEvaluator
from game.core.exceptions import FormulaException
from game.simulation.components.modifiers import (
    apply_modifier_effects,
    get_default_stat_multipliers
)

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.components.component_constants import ApplicationModifier


class ComponentStatsCalculator:
    """
    Utility class for component stats calculation.

    All methods are static - this is a namespace for calculation functions.
    """

    # PROJ-241: Data-driven mapping for formula default values.
    # When a component has a formula for these keys, the corresponding
    # attributes are initialized to safe defaults before formula evaluation.
    FORMULA_DEFAULTS = {
        'mass': [('base_mass', 0), ('mass', 0)],
        'hp':   [('base_max_hp', 0), ('max_hp', 0), ('current_hp', 0)],
        'cost': [('cost', 0)],
    }

    @staticmethod
    def parse_formulas(data: dict) -> dict:
        """Extract formula definitions from component data.

        Scans data dict for string values starting with '=', skipping
        any keys that start with '_' (metadata like _comment).

        Args:
            data: Component data dictionary.

        Returns:
            Dict mapping attribute name to formula string (without '=').
        """
        formulas = {}
        for key, value in data.items():
            if key.startswith('_'):
                continue
            if isinstance(value, str) and value.startswith("="):
                formulas[key] = value[1:]
        return formulas

    @staticmethod
    def apply_formula_defaults(component: 'Component', formulas: dict) -> None:
        """Set safe default values for formula-driven attributes.

        Uses the FORMULA_DEFAULTS mapping to determine which attributes
        need default values for each formula key (mass, hp, cost).

        Args:
            component: The component to set defaults on.
            formulas: Dict of formula key -> formula string.
        """
        for key in formulas:
            if key in ComponentStatsCalculator.FORMULA_DEFAULTS:
                for attr, default in ComponentStatsCalculator.FORMULA_DEFAULTS[key]:
                    setattr(component, attr, default)

    @staticmethod
    def calculate_modifier_stats(
        modifiers: List['ApplicationModifier'],
        component: 'Component' = None
    ) -> Dict[str, Any]:
        """
        Calculate combined stats from all modifiers.

        Aggregates modifier effects using multiplicative stacking for multipliers
        and additive stacking for adds.

        Args:
            modifiers: List of ApplicationModifier to process
            component: Optional component reference for targeted effects

        Returns:
            Dict with calculated stats including:
                - mass_mult, mass_add, hp_mult, cost_mult
                - properties dict for direct property overrides
        """
        # Use shared function for canonical default stats
        stats = get_default_stat_multipliers()

        # Apply modifiers with component reference for targeted effects
        for m in modifiers:
            apply_modifier_effects(m.definition, m.value, stats, component=component)

        return stats

    @staticmethod
    def apply_base_stats(
        component: 'Component',
        stats: Dict[str, Any],
        old_max_hp: int
    ) -> None:
        """
        Apply calculated stats to component properties.

        Handles mass, HP, cost, and ability recalculation.

        Args:
            component: The component to update
            stats: Stats dict from calculate_modifier_stats
            old_max_hp: Previous max HP for current_hp adjustment
        """
        # Apply specific property overrides
        # These are dynamic properties from modifier definitions (arc, facing_angle, etc.)
        for prop, val in stats['properties'].items():
            setattr(component, prop, val)

        # Apply Base Multipliers
        component.mass = (component.base_mass + stats['mass_add']) * stats['mass_mult']

        # Note: old_max_hp is passed in, captured before base formula reset
        component.max_hp = int(component.base_max_hp * stats['hp_mult'])

        # IComponent protocol guarantees cost attribute exists
        component.cost = int(component.data.get('cost', 0) * stats['cost_mult'])

        # Handle HP update (healing/new component logic)
        hp_changed = False
        if old_max_hp == 0:
            component.current_hp = component.max_hp
            hp_changed = True
        elif component.current_hp >= old_max_hp:
            component.current_hp = component.max_hp
            hp_changed = True

        # Ensure cap
        new_hp = min(component.current_hp, component.max_hp)
        if new_hp != component.current_hp:
            component.current_hp = new_hp
            hp_changed = True

        # PROJ-49: Mark HP ratio cache dirty if HP changed
        if hp_changed:
            component._hp_ratio_dirty = True

        # Recalculate all abilities with updated stats from modifiers
        for ab in component.ability_instances:
            ab.recalculate()

    @staticmethod
    def reset_and_evaluate_formulas(
        component: 'Component',
        context: Dict[str, Any] = None
    ) -> None:
        """
        Reset component to base values and evaluate all formulas.

        Evaluates formulas in:
        - Component attributes (mass, hp, etc.)
        - Ability definitions
        - Resource costs

        Args:
            component: The component to update
            context: Optional dict with context for formula evaluation
                     Expected keys: 'ship_class_mass' (float)
        """
        import copy

        # Reset abilities from raw data
        component.abilities = copy.deepcopy(component.data.get('abilities', {}))

        # Context building - Priority: explicit context > ship reference > default
        eval_context = {
            'ship_class_mass': 1000  # Default fallback
        }
        if context and 'ship_class_mass' in context:
            eval_context['ship_class_mass'] = context['ship_class_mass']
        elif component.ship:
            # Ships have max_mass_budget set by ShipStatsCalculator
            eval_context['ship_class_mass'] = getattr(component.ship, 'max_mass_budget', 1000)

        # Evaluate Formulas for attributes
        for attr, formula in component.formulas.items():
            try:
                val = FormulaEvaluator.evaluate(formula, eval_context)
            except FormulaException as e:
                raise FormulaException(
                    f"Component '{getattr(component, 'id', '?')}' has invalid "
                    f"formula in field '{attr}': {e}",
                    code=getattr(e, 'code', None),
                    context=getattr(e, 'context', {}),
                ) from e
            if attr == 'mass':
                component.base_mass = float(val)
                component.mass = component.base_mass  # Reset to base
            elif attr == 'hp':
                component.base_max_hp = int(val)
                component.max_hp = component.base_max_hp  # Reset to base
            else:
                # Dynamic formula attributes (not mass/hp) - set directly
                current = getattr(component, attr, None)
                if current is not None and isinstance(current, int):
                    setattr(component, attr, int(val))
                else:
                    setattr(component, attr, val)

        # Evaluate formulas in abilities
        # NOTE: Abilities may contain runtime formulas (e.g. damage formulas
        # referencing range_to_target) that cannot be resolved at load time.
        # These are intentionally evaluated with safe_evaluate so they degrade
        # to 0; the weapon ability will re-parse the raw formula string from
        # component.data at init time and evaluate it at runtime.
        ComponentStatsCalculator._evaluate_formulas_in_abilities(
            component.abilities,
            eval_context
        )

        # Evaluate formulas in resource_cost
        raw_costs = component.data.get("resource_cost", {})
        component.evaluated_resource_cost = {}
        for res, amount in raw_costs.items():
            if isinstance(amount, str) and amount.startswith("="):
                formula_str = amount[1:]
                try:
                    component.evaluated_resource_cost[res] = FormulaEvaluator.evaluate(
                        formula_str, eval_context
                    )
                except FormulaException as e:
                    raise FormulaException(
                        f"Component '{getattr(component, 'id', '?')}' has invalid "
                        f"formula in resource_cost '{res}': {e}",
                        code=getattr(e, 'code', None),
                        context=getattr(e, 'context', {}),
                    ) from e
            else:
                component.evaluated_resource_cost[res] = amount

    @staticmethod
    def _evaluate_formulas_in_abilities(
        abilities: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """
        Recursively evaluate formulas in ability definitions.

        Args:
            abilities: Dict of ability definitions to update in-place
            context: Context for formula evaluation
        """
        # Runtime variables that are only available during combat, not at load time.
        # Formulas referencing these must be preserved as strings for the ability
        # to evaluate at runtime (e.g., damage formulas with range_to_target).
        _RUNTIME_VARIABLES = {'range_to_target', 'target_mass', 'target_speed'}

        def evaluate_recursive(obj, ctx):
            """Recursively evaluate formulas in nested structures."""
            if isinstance(obj, str) and obj.startswith("="):
                # Preserve formulas that reference runtime variables
                formula_str = obj[1:]
                if any(var in formula_str for var in _RUNTIME_VARIABLES):
                    return obj  # Keep as formula string for runtime evaluation
                return FormulaEvaluator.safe_evaluate(formula_str, ctx)
            elif isinstance(obj, dict):
                for key, sub_val in obj.items():
                    obj[key] = evaluate_recursive(sub_val, ctx)
                return obj
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    obj[i] = evaluate_recursive(item, ctx)
                return obj
            return obj

        for ability_name, val in abilities.items():
            abilities[ability_name] = evaluate_recursive(val, context)

    @staticmethod
    def recalculate(
        component: 'Component',
        context: Dict[str, Any] = None
    ) -> None:
        """
        Full stats recalculation for a component.

        Orchestrates the three-phase recalculation:
        1. Reset and evaluate base formulas
        2. Calculate modifier stats
        3. Apply stats to component

        Args:
            component: The component to recalculate
            context: Optional context for formula evaluation
        """
        # Capture old hp for current_hp logic at end
        old_max_hp = component.max_hp

        # 1. Reset and Evaluate Base Formulas
        ComponentStatsCalculator.reset_and_evaluate_formulas(component, context)

        # 1.5 Re-instantiate Abilities (Sync instances with new abilities dict)
        component._instantiate_abilities()

        # 2. Calculate Modifier Stats (Accumulate multipliers)
        stats = ComponentStatsCalculator.calculate_modifier_stats(
            component.modifiers,
            component
        )
        component.stats = stats  # Persist for introspection/ability access

        # 3. Apply Base Stats (Generic attributes)
        ComponentStatsCalculator.apply_base_stats(component, stats, old_max_hp)
