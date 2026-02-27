# PROJ-203: Reduce complexity: StrategyRenderer._draw_systems (CC 29)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-203` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-203 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Star Color Mapping | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract Colony Marker | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Extract Star Rendering & Verify | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-27
**Active Phase:** 4 - Extract Star Rendering & Verify
**Last Action:** Phase 3 complete - Extracted `_draw_colony_marker()` helper, CC 20→13
**Next Action:** Begin Phase 4 - Extract `_draw_star()` helper and verify final CC
**Blockers:** None

## Overview

Reduce the cyclomatic complexity of `StrategyRenderer._draw_systems` from CC 29 to below CC 20 through extraction of helper methods. The function renders star systems on the strategy map and has several separable concerns: colony marker drawing, star color classification, and individual star rendering.

## Goals
- Reduce `_draw_systems` CC from 29 to below 20
- Maintain 100% behavioral compatibility
- Improve code readability through smaller, focused methods
- Add test coverage for edge cases before refactoring

## Scope
**In:**
- `game/ui/screens/strategy_renderer.py` - `_draw_systems` method (lines 306-376)
- Test file: `tests/unit/ui/screens/test_strategy_renderer.py`
- Extraction of 3 helper methods

**Out:**
- Other complex methods in same file (`_draw_system_details`, `_draw_storms`)
- Any behavioral changes
- Zoom threshold constant extraction
- Changes to color classification thresholds

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Method | `game/ui/screens/strategy_renderer.py:306-376` |
| Renderer Tests | `tests/unit/ui/screens/test_strategy_renderer.py` |
| Color Tests | `tests/unit/ui/test_star_color_mapping.py` |
| Animation Tests | `tests/unit/ui/screens/test_strategy_renderer_animation.py` |

## Phase Summaries

### Phase 1: Test Fortification
Add missing test coverage identified by safety analysis before any code changes. Critical for safe refactoring.

**Tests to add:**
- Colony marker edge cases (4 tests)
- Star rendering edge cases (3 tests)
- Viewport culling verification (2 tests)

### Phase 2: Extract Star Color Mapping
Extract the 5-branch if/elif color classification chain to `_get_star_asset_key(color)`.
- **Risk:** LOW (pure function, existing test coverage)
- **CC Impact:** -4

### Phase 3: Extract Colony Marker
Extract the 3-level nested colony marker block to `_draw_colony_marker(screen, sys, world_pos)`.
- **Risk:** LOW (self-contained block)
- **CC Impact:** -3

### Phase 4: Extract Star Rendering & Verify
Extract per-star rendering to `_draw_star(screen, star, ...)` and verify final CC.
- **Risk:** MEDIUM (coordinate conversion)
- **CC Impact:** -6
- **Target CC:** 16-18 (below 20)

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Control flow analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Call site analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Risk assessment

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Final CC below 20
- [ ] Audit passed
- [ ] User verified
