# Complexity Reduction Target

## Primary Target
- **File:** `game/ui/screens/strategy_renderer.py`
- **Function:** `_draw_systems`
- **Line:** 306
- **Cyclomatic Complexity:** 29 (grade E)
- **Type:** method
- **Class:** `StrategyRenderer`
- **Length:** ~71 lines

## Goal
Reduce the cyclomatic complexity of `_draw_systems` to below 20.
If the function cannot be reduced below 20 without compromising
readability or correctness, document why and add to the skip list.

## Other Complex Functions in Same File
| Function | Line | CC | Grade |
|----------|------|----|-------|
| `StrategyRenderer._draw_systems` | 306 | 29 | E | **<-- TARGET**
| `StrategyRenderer._draw_system_details` | 378 | 24 | E |
| `StrategyRenderer._draw_storms` | 579 | 23 | E |

## Constraints
- All existing tests must continue to pass
- No behavioral changes — pure refactoring
- Prefer extracting helper methods over restructuring
- If the function is irreducibly complex, skip it rather than break it
- Document all decisions in decisions.md
