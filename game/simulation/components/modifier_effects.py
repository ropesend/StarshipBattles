"""
Modifier Effect System.

This module provides:
- ModifierEffect: A concrete, evaluated effect from a modifier
- ModifierEffectEvaluator: Evaluates modifier definitions to produce effects

These classes enable:
1. Data-driven modifier formulas (JSON instead of Python handlers)
2. UI introspection (what does this modifier affect?)
3. Multi-ability targeting (one modifier affects different abilities differently)

PROJ-45: Error handling updated to raise FormulaException for formula evaluation errors.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import logging
from game.core.exceptions import FormulaException
from game.core.formula_evaluator import FormulaEvaluator

logger = logging.getLogger(__name__)


@dataclass
class ModifierEffect:
    """
    A single evaluated effect from a modifier, ready to apply.

    This is a first-class object that:
    - Stores the concrete value (already evaluated from formula)
    - Can be queried by UI for tooltips
    - Can target specific abilities

    Example:
        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability=None,  # Affects all abilities consuming this stat
            source_modifier_id='hardened_mount',
            source_modifier_name='Hardened',
            formula_str='param',
            param_value=1.5
        )
    """
    stat_key: str
    value: float
    operation: str  # "multiply", "add", "set"
    target_ability: Optional[str]  # None = all abilities that consume this stat
    source_modifier_id: str
    source_modifier_name: str
    formula_str: str  # For UI display: "2 ^ param"
    param_value: float  # The param value used

    def describe(self) -> str:
        """
        Human-readable description for UI.

        Examples:
            "damage_mult x1.50"
            "accuracy_add +0.50"
            "arc_set =90.00"
            "damage_mult x1.50 (on WeaponAbility)"
        """
        op_symbol = {
            'multiply': 'x',
            'add': '+',
            'set': '='
        }.get(self.operation, '?')

        desc = f"{self.stat_key} {op_symbol}{self.value:.2f}"

        if self.target_ability:
            desc += f" (on {self.target_ability})"

        return desc

    def is_targeted(self) -> bool:
        """Returns True if this effect targets a specific ability."""
        return self.target_ability is not None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization/introspection."""
        return {
            'stat_key': self.stat_key,
            'value': self.value,
            'operation': self.operation,
            'target_ability': self.target_ability,
            'source_modifier_id': self.source_modifier_id,
            'source_modifier_name': self.source_modifier_name,
            'formula_str': self.formula_str,
            'param_value': self.param_value,
            'description': self.describe(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModifierEffect":
        """Reconstruct a ModifierEffect from its `to_dict` form.

        PROJ-312: needed by replay capture/playback so a captured
        ``ModifierEntry`` can round-trip through JSON. The `description`
        field is derived (via `describe()`) and is ignored on read.
        """
        return cls(
            stat_key=data['stat_key'],
            value=float(data['value']),
            operation=data['operation'],
            target_ability=data.get('target_ability'),
            source_modifier_id=data['source_modifier_id'],
            source_modifier_name=data['source_modifier_name'],
            formula_str=data['formula_str'],
            param_value=float(data['param_value']),
        )


class ModifierEffectEvaluator:
    """
    Evaluates modifier definitions to produce ModifierEffect instances.

    This class:
    1. Parses formula strings from modifier JSON
    2. Evaluates formulas with the given parameter value
    3. Returns concrete ModifierEffect objects

    Supports formulas like:
    - "param" - Direct parameter value
    - "param ^ 2" - Power
    - "2 ^ param" - Exponential
    - "1.0 + param * 0.5" - Linear scaling
    - "1.0 + 0.514 * ln(1 + param / 30)" - Logarithmic scaling
    - "1.0 + (mass_mult - 1.0) * 0.5" - References to other stats (requires stats context)
    """

    @staticmethod
    def evaluate_formula(formula: str, context: Dict[str, float]) -> float:
        """Evaluate a formula string with the given context.

        Delegates to FormulaEvaluator with modifier-specific context
        (caret substitution enabled).

        Args:
            formula: Formula string like "param ^ 2" or "2 ^ param"
            context: Dictionary of variable values (e.g., {'param': 2.0})

        Returns:
            Evaluated result as float

        Raises:
            FormulaException: If formula cannot be evaluated.
        """
        result = FormulaEvaluator.evaluate(
            formula, context, FormulaEvaluator.MODIFIER_CONTEXT
        )
        return float(result)

    @classmethod
    def evaluate_modifier(
        cls,
        mod_def: Dict[str, Any],
        param_value: float,
        stats_context: Optional[Dict[str, float]] = None
    ) -> List[ModifierEffect]:
        """
        Evaluate a modifier definition with a given parameter value.

        Args:
            mod_def: Modifier definition dict (from JSON)
            param_value: The parameter value (e.g., 2.0 for level 2)
            stats_context: Optional dict of already-computed stats for dependency resolution

        Returns:
            List of ModifierEffect objects

        Example mod_def (new format):
            {
                "id": "hardened_mount",
                "name": "Hardened",
                "effects": [
                    {"stat": "mass_mult", "formula": "param", "operation": "multiply"},
                    {"stat": "hp_mult", "formula": "param ^ 2", "operation": "multiply"}
                ]
            }
        """
        effects = []
        modifier_id = mod_def.get('id', 'unknown')
        modifier_name = mod_def.get('name', 'Unknown')

        # Build context for formula evaluation
        context = {'param': param_value}
        if stats_context:
            context.update(stats_context)

        # Check for new format (effects array)
        if 'effects' in mod_def and isinstance(mod_def['effects'], list):
            for effect_def in mod_def['effects']:
                stat_key = effect_def.get('stat')
                formula = effect_def.get('formula', 'param')
                operation = effect_def.get('operation', 'multiply')
                target_ability = effect_def.get('target_ability')

                try:
                    value = cls.evaluate_formula(formula, context)
                except FormulaException as e:
                    # Log error and fallback to param value
                    logger.error(
                        f"Formula evaluation failed for modifier '{modifier_id}': "
                        f"formula='{formula}', param={param_value}, error={e}"
                    )
                    value = param_value

                effects.append(ModifierEffect(
                    stat_key=stat_key,
                    value=value,
                    operation=operation,
                    target_ability=target_ability,
                    source_modifier_id=modifier_id,
                    source_modifier_name=modifier_name,
                    formula_str=formula,
                    param_value=param_value,
                ))

        return effects

    @classmethod
    def validate_formula(cls, formula: str) -> List[str]:
        """Validate a formula string without evaluating it.

        Delegates to FormulaEvaluator with modifier-specific context.

        Args:
            formula: Formula string to validate

        Returns:
            List of error messages (empty if valid)
        """
        # Modifier formulas only allow 'param' plus math functions
        return FormulaEvaluator.validate(
            formula, ['param'], FormulaEvaluator.MODIFIER_CONTEXT
        )

    @classmethod
    def validate_modifier_definition(cls, mod_def: Dict[str, Any]) -> List[str]:
        """
        Validate all formulas in a modifier definition.

        Args:
            mod_def: Modifier definition dict

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        modifier_id = mod_def.get('id', 'unknown')

        if 'effects' not in mod_def:
            return errors

        effects = mod_def.get('effects', [])
        if not isinstance(effects, list):
            errors.append(f"Modifier '{modifier_id}': effects must be a list")
            return errors

        for i, effect in enumerate(effects):
            formula = effect.get('formula', 'param')
            formula_errors = cls.validate_formula(formula)
            for err in formula_errors:
                errors.append(f"Modifier '{modifier_id}' effect {i}: {err}")

        return errors

