# PROJ-197: Duplication Consolidation Completion

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-197` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-197 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Expand colors.py palette | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Test Lab renderer fix | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Battle UI files | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Setup & strategy files | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Ship panels & widgets | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Builder, formation & remaining files | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Final audit & cleanup | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-25
**Active Phase:** Project Complete
**Last Action:** Phase 7 complete - Final audit passed, all phases complete
**Next Action:** Trigger audit
**Blockers:** None
**Context for Next Agent:** All 7 phases complete. Zero raw RGB tuples remain outside definition files (colors.py, theme.py). Phase 7 fixed ~15 remaining violations found in audit. Added ~20 more constants. All 12734 tests passing.

## Overview
Complete the color tuple consolidation that was left incomplete by the previous agent.
Every raw RGB tuple in `game/ui/` will be replaced with a named constant from `game/ui/colors.py`.
The test lab renderer.py will be fixed to use its existing theme.py constants.

## Goals
- Eliminate all ~412 raw color tuples across 48 files in `game/ui/`
- Add semantic color constants to `game/ui/colors.py` organized by domain
- Fix test lab renderer.py to use existing theme.py constants
- Normalize near-duplicate colors to existing palette constants where possible
- Zero visual regressions — color values stay the same (or normalize to existing constants)

## Scope
**In:**
- All raw RGB tuple literals in `game/ui/` files (excluding `colors.py` definitions and `test_lab/theme.py` definitions)
- Adding new semantic constants to `game/ui/colors.py`
- Adding missing constants to `game/ui/screens/test_lab/theme.py` for renderer.py
- Normalizing near-duplicate colors to existing constants

**Out:**
- Font consolidation (already complete)
- ValidationResult refactoring (not actual duplication — different classes)
- `scripts/visual_test_galaxy.py` (standalone script, not production UI)
- Color values in `game/ui/colors.py` definitions (these ARE the constants)
- Color values in `game/ui/screens/test_lab/theme.py` definitions (these ARE the constants)
- Any changes to non-UI code

## Key Files
| Component | File Path |
|-----------|-----------|
| Global color palette | `game/ui/colors.py` |
| Test Lab theme | `game/ui/screens/test_lab/theme.py` |
| Test Lab renderer (fix) | `game/ui/screens/test_lab/renderer.py` |
| Battle panels (38 tuples) | `game/ui/panels/battle_panels.py` |
| Setup renderer (40 tuples) | `game/ui/screens/setup_renderer.py` |
| Ship stats renderer (31 tuples) | `game/ui/panels/ship_stats_renderer.py` |
| Strategy renderer (28 tuples) | `game/ui/screens/strategy_renderer.py` |
| Strategy widgets (23 tuples) | `game/ui/panels/strategy_widgets.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log Summary
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-25 | ValidationResult left as-is | Different classes, not duplication |
| 2026-02-25 | Global colors.py strategy | One import source for all UI files |
| 2026-02-25 | Include test lab fix | Quick win, constants already exist |
| 2026-02-25 | Font work complete | Out of scope |
| 2026-02-25 | All tuples consolidated | Complete elimination of magic numbers |
| 2026-02-25 | Normalize to existing | Use existing constants where close match exists |

---

## Phases

### Phase 1: Expand colors.py Palette [Medium]
**Objective:** Add all new semantic constants to `game/ui/colors.py` in one organized pass
**Status:** Not Started

This phase adds constants ONLY — no substitutions yet. This ensures all subsequent phases
have the full palette available.

### Phase 2: Test Lab Renderer Fix [Simple]
**Objective:** Fix renderer.py to use existing theme.py constants + any new ones added to theme.py
**Status:** Not Started

Quick win — theme.py already has most constants, just needs substitution in renderer.py.

### Phase 3: Battle UI Files [Medium]
**Objective:** Consolidate all battle-related files (battle_panels, battle_screen, battle_ui, battle_state_viewer)
**Status:** Not Started

### Phase 4: Setup & Strategy Files [Medium]
**Objective:** Consolidate setup_renderer, setup_screen, strategy_renderer, strategy_widgets
**Status:** Not Started

### Phase 5: Ship Panels & Widgets [Medium]
**Objective:** Consolidate ship_stats_renderer, ship_detail_panel, scrollable_json_panel, modifier_impact_grid
**Status:** Not Started

### Phase 6: Builder, Formation & Remaining Files [Medium]
**Objective:** Consolidate all remaining files (~30 files with 1-18 tuples each)
**Status:** Not Started

### Phase 7: Final Audit & Cleanup [Simple]
**Objective:** Verify zero raw tuples remain, run full test suite, clean up any missed items
**Status:** Not Started

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — 12,734 passed, 1 skipped (baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Grep for remaining raw tuples to verify progress

### Final Verification
- [ ] `grep -rn "(\d\+,\s*\d\+,\s*\d\+)" game/ui/ --include="*.py"` shows ONLY definitions in colors.py/theme.py
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass
- [ ] Spot-check visual rendering in game (optional manual test)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-25 | All 5 goals verified PASSED | Project complete |

## Completion Checklist
- [x] Phase 1 complete — colors.py expanded
- [x] Phase 2 complete — test lab renderer fixed
- [x] Phase 3 complete — battle files consolidated
- [x] Phase 4 complete — setup & strategy files consolidated
- [x] Phase 5 complete — ship panels & widgets consolidated
- [x] Phase 6 complete — remaining files consolidated
- [x] Phase 7 complete — audit passed, zero raw tuples
- [x] All tests passing (12734 passed, 1 skipped)
- [x] Audit PASSED (Cycle 1)
