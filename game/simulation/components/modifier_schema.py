"""
Modifier Schema Validation for V2 Format.

This module provides validation functions for the V2 JSON-based modifier format
that uses formula expressions. All modifiers are now required to be in V2 format.

V1 format (dict-based effects with 'special' handlers) is no longer supported.

Functions:
- is_v2_format: Validates that a modifier uses the V2 array-based effects format
- validate_effect_v2: Validates a single effect object
- validate_param_v2: Validates a parameter definition
- validate_restrictions_v2: Validates restriction rules
- validate_modifier_v2: Validates a complete modifier definition
- normalize_effect_v2: Applies defaults to an effect object
"""
from typing import Dict, Any, List

from game.simulation.components.modifier_effects import ModifierEffectEvaluator


def is_v2_format(modifier: Dict[str, Any]) -> bool:
    """
    Validate that a modifier uses V2 format.

    V2 format: 'effects' is an array of effect objects with 'stat' and 'formula'
    V1 format is no longer supported.

    Args:
        modifier: The modifier definition dict

    Returns:
        True if V2 format

    Raises:
        ValueError: If modifier uses deprecated V1 format (dict-based effects)
    """
    effects = modifier.get('effects')
    if effects is None:
        return False

    # V2 format: effects is a list of dicts with 'stat' and 'formula'
    if isinstance(effects, list):
        return True

    # V1 format is no longer supported - raise error to surface data issues
    if isinstance(effects, dict):
        mod_id = modifier.get('id', 'unknown')
        raise ValueError(
            f"Modifier '{mod_id}' uses deprecated V1 format (dict-based effects). "
            f"V1 format is no longer supported. Convert to V2 array format."
        )

    return False


def validate_effect_v2(effect: Dict[str, Any]) -> bool:
    """
    Validate a single effect in V2 format.

    Required fields:
    - stat: The stat key to modify
    - formula: The formula string to evaluate

    Optional fields:
    - operation: 'multiply', 'add', or 'set' (defaults to 'multiply')
    - target_ability: Ability class name to target specifically
    - depends_on: List of stat keys this formula depends on

    Args:
        effect: The effect dict to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(effect, dict):
        return False

    # Required fields
    if 'stat' not in effect:
        return False
    if 'formula' not in effect:
        return False

    # Validate types
    if not isinstance(effect['stat'], str):
        return False
    if not isinstance(effect['formula'], str):
        return False

    # Optional field validation
    if 'operation' in effect:
        if effect['operation'] not in ('multiply', 'add', 'set', 'add_to_mult'):
            return False

    if 'target_ability' in effect:
        if not isinstance(effect['target_ability'], str):
            return False

    if 'depends_on' in effect:
        if not isinstance(effect['depends_on'], list):
            return False
        for dep in effect['depends_on']:
            if not isinstance(dep, str):
                return False

    return True


def normalize_effect_v2(effect: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize an effect by applying defaults.

    Args:
        effect: The effect dict to normalize

    Returns:
        New dict with defaults applied
    """
    normalized = dict(effect)

    # Default operation to 'multiply'
    if 'operation' not in normalized:
        normalized['operation'] = 'multiply'

    return normalized


def validate_param_v2(param: Dict[str, Any]) -> bool:
    """
    Validate a parameter definition in V2 format.

    Required fields:
    - name: Display name for the parameter
    - type: Parameter type ('linear', 'boolean', etc.)
    - min: Minimum value
    - max: Maximum value
    - default: Default value

    Args:
        param: The param dict to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(param, dict):
        return False

    required_fields = ['name', 'type', 'min', 'max', 'default']
    for field in required_fields:
        if field not in param:
            return False

    # Validate types
    if not isinstance(param['name'], str):
        return False
    if not isinstance(param['type'], str):
        return False

    # min, max, default should be numbers
    for field in ['min', 'max', 'default']:
        if not isinstance(param[field], (int, float)):
            return False

    return True


def validate_restrictions_v2(restrictions: Dict[str, Any]) -> bool:
    """
    Validate restrictions in V2 format.

    Supported fields:
    - allow_abilities: List of ability class names that must be present
    - deny_abilities: List of ability class names that must NOT be present
    - require_mode: 'any' or 'all' for allow_abilities (default 'any')

    Args:
        restrictions: The restrictions dict to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(restrictions, dict):
        return False

    # Validate allow_abilities
    if 'allow_abilities' in restrictions:
        if not isinstance(restrictions['allow_abilities'], list):
            return False
        for ability in restrictions['allow_abilities']:
            if not isinstance(ability, str):
                return False

    # Validate deny_abilities
    if 'deny_abilities' in restrictions:
        if not isinstance(restrictions['deny_abilities'], list):
            return False
        for ability in restrictions['deny_abilities']:
            if not isinstance(ability, str):
                return False

    # Validate require_mode
    if 'require_mode' in restrictions:
        if restrictions['require_mode'] not in ('any', 'all'):
            return False

    return True


def validate_modifier_v2(modifier: Dict[str, Any]) -> bool:
    """
    Validate a complete modifier definition in V2 format.

    Required fields:
    - id: Unique modifier identifier
    - effects: Array of effect objects

    Optional fields:
    - name: Display name
    - description: Human-readable description
    - param: Parameter definition
    - restrictions: Component/ability restrictions

    Args:
        modifier: The modifier definition dict

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(modifier, dict):
        return False

    # Required: id
    if 'id' not in modifier:
        return False
    if not isinstance(modifier['id'], str):
        return False

    # Required: effects as non-empty array
    if 'effects' not in modifier:
        return False
    if not isinstance(modifier['effects'], list):
        return False
    if not modifier['effects']:
        # Empty effects array is invalid - modifiers should have at least one effect
        return False

    # Validate each effect (structural validation)
    for effect in modifier['effects']:
        if not validate_effect_v2(effect):
            return False
        # Delegate formula validation to modifier_effects (semantic validation)
        # This prevents drift between structural and semantic checks
        formula_errors = ModifierEffectEvaluator.validate_formula(effect['formula'])
        if formula_errors:
            return False

    # Optional: param
    if 'param' in modifier:
        if not validate_param_v2(modifier['param']):
            return False

    # Optional: restrictions
    if 'restrictions' in modifier:
        if not validate_restrictions_v2(modifier['restrictions']):
            return False

    return True
