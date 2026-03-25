# Complexity Reduction Target

## Primary Target
- **File:** `game/ui/screens/fleet_report_filters.py`
- **Function:** `filter_ships`
- **Line:** 124
- **Cyclomatic Complexity:** 36 (grade F)
- **Type:** function
- **Length:** ~99 lines

## Goal
Reduce the cyclomatic complexity of `filter_ships` to below 20.
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
