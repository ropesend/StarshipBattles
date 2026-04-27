"""Pure helpers for Combat Lab renderer. No pygame dependency.

Extracted from `renderer.py` by PROJ-309 sub-phase 3.3. These functions are
covered by `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py`,
which still exercises them via the class-attribute aliases on
`TestLabRenderer` (see `orchestrator.py`).

Future contributors: any new mapping rules / value-formatting decisions go
HERE — they must not leak into draw code.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


def is_condition_verified(condition_text: str, validation_results: List[Dict]) -> bool:
    """
    Check if a condition is verified by a passing validation.

    Args:
        condition_text: Text like "Beam Damage: 5 per hit"
        validation_results: List of validation result dicts

    Returns:
        True if condition matches a PASS validation
    """
    # Map condition text patterns to validation rule names
    mappings = {
        # Beam weapon mappings
        'Beam Damage': 'Beam Weapon Damage',
        'Base Accuracy': 'Base Accuracy',
        'Accuracy Falloff': 'Accuracy Falloff',
        'Weapon Max Range': 'Weapon Range',
        'Distance': None,  # Distance is test setup, not component property
        'Net Score': None,  # Calculated value, complex validation
        'Test Duration': None,  # Test parameter, not validated
        'Test duration': None,  # Test parameter, not validated

        # Propulsion test mappings
        'Engine thrust': 'Engine Thrust',
        'Ship mass': 'Ship Mass',
        'Expected max_speed': 'Max Speed (Formula)',
        'Expected acceleration_rate': 'Acceleration Rate (Formula)',
        'Initial velocity': 'Initial Velocity',
        'Initial angle': 'Initial Angle',
        'Total thrust': 'Total Thrust',
        'turn_speed': 'Turn Speed',
        'Turn speed': 'Turn Speed (Formula)',
        'raw_turn_rate': 'Raw Turn Rate',
        'Expected turn_speed': 'Turn Speed (Formula)',
        'No engine component': 'Total Thrust (Should be 0)',
        'No thruster component': None,  # Not directly validated
        'thrust = 0': 'Total Thrust (Should be 0)',
        'Expected: No movement': 'Distance Traveled',
        'Expected: Rotation but no translation': 'Final Velocity',
    }

    # Check direct validations
    for pattern, validation_name in mappings.items():
        if validation_name and pattern in condition_text:
            # Find matching validation result
            for vr in validation_results:
                if vr['name'] == validation_name and vr['status'] == 'PASS':
                    return True

    # Special case: Range Penalty (calculated from distance x accuracy_falloff)
    if 'Range Penalty' in condition_text:
        # Extract values from condition text like "Range Penalty: 50 * 0.002 = 0.1"
        try:
            # Match pattern: "Range Penalty: {distance} * {falloff} = {result}"
            match = re.search(
                r'Range Penalty:\s*(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)',
                condition_text
            )
            if match:
                distance_stated = float(match.group(1))
                falloff_stated = float(match.group(2))
                penalty_stated = float(match.group(3))

                # Check if falloff is verified
                falloff_verified = False
                falloff_actual = None
                for vr in validation_results:
                    if vr['name'] == 'Accuracy Falloff' and vr['status'] == 'PASS':
                        falloff_verified = True
                        falloff_actual = vr['actual']
                        break

                if falloff_verified and falloff_actual is not None:
                    # Verify the calculation is correct
                    calculated_penalty = distance_stated * falloff_actual
                    if abs(calculated_penalty - penalty_stated) < 0.0001:  # Float comparison
                        return True
        except (ValueError, TypeError):
            pass  # If parsing fails, don't show V

    return False


def format_check_pair(expected: Any, actual: Any) -> Tuple[str, str]:
    """Format expected and actual values with identical precision.

    Both values get the same number of decimal places so they
    visually align when stacked vertically.
    """
    if expected is None and actual is None:
        return "—", "—"

    # Booleans — no formatting needed
    if isinstance(expected, bool) or isinstance(actual, bool):
        return str(expected), str(actual)

    # Both numeric — format to matching decimal places
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        # Determine best precision from whichever has more
        # meaningful decimals
        exp_f = float(expected)
        act_f = float(actual)

        # Pick precision: use more decimals for small values
        max_abs = max(abs(exp_f), abs(act_f), 1e-12)
        if max_abs >= 10000:
            decimals = 1
        elif max_abs >= 1:
            decimals = 4
        else:
            decimals = 6

        # If either is an exact integer, still match the other's format
        fmt = f",.{decimals}f"
        return format(exp_f, fmt), format(act_f, fmt)

    # Mixed or string types — just stringify
    return str(expected) if expected is not None else "—", \
           str(actual) if actual is not None else "—"
