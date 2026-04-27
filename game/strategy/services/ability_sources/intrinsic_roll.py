"""Shared roll helper for intrinsic ability templates (PROJ-300 D15).

Used by PROJ-301..304 generators. Converts registry templates with
`{"min": x, "max": y}` ranges into instance dicts with rolled scalars.
PROJ-301..304 are pure consumers — they do NOT reimplement this logic.
"""
import copy
import random
from typing import Any, Dict


def roll_intrinsic_abilities(
    template: Dict[str, Any],
    rng: random.Random,
) -> Dict[str, Any]:
    """Materialize an instance abilities dict from a registry template.

    For each ability in `template`, copies the ability data verbatim except:
    - any field with shape `{"min": x, "max": y}` is rolled to a scalar via
      `rng.uniform(x, y)` for floats or `rng.randint(x, y)` for ints (decided
      by the values' types).
    - `damage_type`, `scope`, `stack_group`, and other string fields pass through.

    Returns a fresh dict (input is not mutated).

    Args:
        template: Per-type abilities template from a JSON registry.
        rng: Seeded random source — caller controls determinism.

    Returns:
        Materialized abilities dict in components.json shape, ready to drop
        on an entity instance.
    """
    if not template:
        return {}

    result: Dict[str, Any] = {}
    for ability_name, ability_data in template.items():
        if not isinstance(ability_data, dict):
            # Primitive/scalar shape (e.g. `"ColonizePlanet": 1`) — passes through.
            result[ability_name] = copy.deepcopy(ability_data)
            continue

        rolled: Dict[str, Any] = {}
        for key, value in ability_data.items():
            if (
                isinstance(value, dict)
                and 'min' in value
                and 'max' in value
                and len(value) == 2
            ):
                lo, hi = value['min'], value['max']
                if isinstance(lo, int) and isinstance(hi, int):
                    rolled[key] = rng.randint(lo, hi)
                else:
                    rolled[key] = rng.uniform(float(lo), float(hi))
            else:
                rolled[key] = copy.deepcopy(value)
        result[ability_name] = rolled

    return result
