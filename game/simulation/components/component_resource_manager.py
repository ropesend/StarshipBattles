"""
ComponentResourceManager - Resource activation cost management.

Extracted from Component class to handle resource-related operations:
- can_afford_activation: Check if resources available
- consume_activation: Consume activation-triggered resources
- try_activate: Atomic check-and-consume operation
- get_resource_cost: Calculate resource costs with formulas/multipliers

PROJ-88: God Class Decomposition - Simulation Core Tier
"""
from typing import TYPE_CHECKING, Optional

from game.simulation.formula_system import safe_evaluate_math_formula

if TYPE_CHECKING:
    from game.simulation.components.component import Component


class ComponentResourceManager:
    """Manages resource activation costs for a Component.

    This is a helper class that handles resource consumption logic,
    extracted from Component to reduce class complexity.

    The manager holds a reference to the component and operates on
    its ability_instances and stats.
    """

    __slots__ = ('_component',)

    def __init__(self, component: 'Component'):
        """Initialize with a component reference.

        Args:
            component: The Component instance to manage resources for.
        """
        self._component = component

    def can_afford_activation(self) -> bool:
        """Check if component can afford activation costs.

        Iterates through ability_instances looking for activation-triggered
        resource consumption abilities and checks if resources are available.

        Returns:
            True if all activation costs can be afforded, False otherwise.
        """
        for ability in self._component.ability_instances:
            # Use duck typing to check for activation-triggered resource consumption
            trigger = getattr(ability, 'trigger', None)
            check_fn = getattr(ability, 'check_available', None)
            if trigger == 'activation' and check_fn is not None:
                if not check_fn():
                    return False
        return True

    def consume_activation(self) -> None:
        """Consume activation costs.

        Iterates through ResourceConsumption abilities with trigger='activation'
        and calls their check_and_consume method.
        """
        for ability in self._component.get_abilities('ResourceConsumption'):
            if ability.trigger == 'activation':
                ability.check_and_consume()

    def try_activate(self) -> bool:
        """Check and consume activation costs atomically.

        First checks if activation can be afforded, then consumes
        the resources if available.

        Returns:
            True if activation succeeded (resources consumed),
            False if resources were unavailable.
        """
        if self.can_afford_activation():
            self.consume_activation()
            return True
        return False

    def get_resource_cost(self, context: Optional[dict] = None) -> dict:
        """Returns the current resource costs, including modifier multipliers.

        Args:
            context: Optional dict with context for formula evaluation.
                     Expected keys: 'ship_class_mass' (float).
                     If not provided, falls back to component.ship reference.

        Returns:
            Dict mapping resource type to integer cost.
        """
        component = self._component
        base_costs = (
            getattr(component, 'evaluated_resource_cost', None)
            or component.data.get("resource_cost", {})
        )
        multiplier = component.stats.get('cost_mult', 1.0)

        # Build context for formula evaluation
        # Priority: explicit context > ship reference > default
        eval_context = {'ship_class_mass': 1000}
        if context and 'ship_class_mass' in context:
            eval_context['ship_class_mass'] = context['ship_class_mass']
        elif component.ship:
            eval_context['ship_class_mass'] = getattr(
                component.ship, 'max_mass_budget', 1000
            )

        result = {}
        for res, amount in base_costs.items():
            if isinstance(amount, str) and amount.startswith("="):
                # Evaluate formula on-demand
                amount = safe_evaluate_math_formula(
                    amount[1:], eval_context, default=0
                )
            result[res] = int(amount * multiplier)
        return result
