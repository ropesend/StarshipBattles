# Complexity Reduction Target

## Primary Target
- **File:** `game/ui/screens/fleet_data_source.py`
- **Function:** `_get_column_value`
- **Line:** 130
- **Cyclomatic Complexity:** 29 (grade E)
- **Type:** method
- **Class:** `FleetDataSource`
- **Length:** ~104 lines

## Goal
Reduce the cyclomatic complexity of `_get_column_value` to below 20.
If the function cannot be reduced below 20 without compromising
readability or correctness, document why and add to the skip list.

## Other Complex Functions in Same File
No other complex functions in this file.

## Constraints
- All existing tests must continue to pass
- No behavioral changes — pure refactoring
- Prefer extracting helper methods over restructuring
- If the function is irreducibly complex, skip it rather than break it
- Document all decisions in decisions.md
