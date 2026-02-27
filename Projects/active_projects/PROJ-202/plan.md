# PROJ-202: Reduce complexity: StrategyRenderer._draw_systems (CC 29)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-202` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-202 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Control Flow | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-27 04:15
**Active Phase:** Phase 1
**Last Action:** Analysis complete - plan written
**Next Action:** Add tests for star color classification
**Blockers:** None

## Overview
Refactor `StrategyRenderer._draw_systems()` to reduce cyclomatic complexity from 29 to below 20. The function renders star systems on the galaxy map including stars, colony markers, labels, and selection highlights. Analysis identified clear extraction candidates: star color classification (pure function), colony marker rendering (self-contained block), and star rendering (loop body extraction).

## Goals
- Reduce CC from 29 to below 20 (target: ~10)
- Extract star color classification to a testable pure function
- Extract colony marker rendering to a dedicated helper
- Replace magic numbers with named constants
- All existing tests must pass with no behavioral changes

## Scope
**In:**
- `_draw_systems()` method (lines 306-376)
- New helper methods in same class
- Named constants for zoom thresholds
- Test coverage for refactored code

**Out:**
- `_draw_system_details()` (CC 24) - separate project
- `_draw_storms()` (CC 23) - separate project
- Any behavioral changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/strategy_renderer.py:306-376` |
| Existing Tests | `tests/unit/ui/screens/test_strategy_renderer.py` |
| New Tests | `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py` |

## Complexity Breakdown
| Source | Lines | CC Contribution |
|--------|-------|-----------------|
| System loop + viewport culling | 315-320 | 3 |
| Colony marker (3 nested conditions) | 325-336 | 5 |
| Star rendering loop + color conditions | 339-367 | 12 |
| Label rendering (zoom + primary checks) | 369-373 | 3 |
| System details delegation | 375-376 | 1 |
| **Total** | | **~24-29** |

## Extraction Strategy
1. **`_classify_star_color(color: tuple) -> str`** - Pure function, zero risk
2. **`_draw_colony_marker(screen, sys, world_pos)`** - Self-contained block
3. **`_draw_system_stars(screen, sys, world_pos)`** - Main loop body
4. **Named constant: `ZOOM_DETAIL_THRESHOLD = 0.5`** - Replace magic number

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety analysis

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified via radon
- [ ] User verified
