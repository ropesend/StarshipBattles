# PROJ-83: Eliminate Test Warning Noise

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-83` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-83 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins (Slider, Deprecation, Clamping) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Label Rect Fixes | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verification & Regression Guard | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-09
**Active Phase:** Phase 2
**Last Action:** Completed Phase 1 — slider fix, deprecation fixes, warning filters
**Next Action:** Begin Phase 2, Task 2.1 (abbreviate stats_layout.json labels)
**Blockers:** None
**Context for Next Agent:** 7351 passed, 148 warnings (down from 299). All remaining warnings are "Label Rect is too small" from pygame_gui. Phase 2 addresses these via label abbreviation and height fixes.

## Overview
The test suite emits 299 warnings across 5 categories (label overflow, BattleEngine deprecation, font preloading, shadow/border clamping, slider range). This project fixes all root causes and adds regression guards to keep warning count at zero.

## Goals
- Eliminate all 299 test warnings at their root causes
- Add pytest warning filters for unfixable pygame_gui internals
- Add DeprecationWarning enforcement to prevent regression
- Target: `7353+ passed, 0 warnings`

## Scope
**In:**
- Fix slider value_range ordering in transfer_dialog.py
- Migrate BattleEngine test calls to use AIControllerFactory
- Delete 2 legacy-path tests per user decision
- Abbreviate long stat labels in stats_layout.json
- Fix build queue label heights and truncation
- Fix section header label heights in design_stats_panel.py
- Add pytest filterwarnings for pygame_gui cosmetic warnings
- Add DeprecationWarning enforcement

**Out:**
- Removing the deprecated BattleEngine legacy path itself (that's a larger refactor)
- Changing font loading infrastructure
- Modifying pygame_gui source code
- Changing the builder_theme.json shadow/border values (affects real UI)

## Key Files
| Component | File Path | What Changes |
|---|---|---|
| Slider fix | `game/ui/screens/transfer_dialog.py` | Swap lines 220-221 |
| Battle fixture | `tests/fixtures/battle.py` | Add ai_factory to create_battle_engine() |
| Battle tests | `tests/unit/combat/test_battle_engine_core.py` | Add ai_factory, delete 2 legacy tests |
| Fighter tests | `tests/unit/combat/test_fighter_launch.py` | Add ai_factory before engine.start() |
| Pytest config | `pytest.ini` | Add filterwarnings section |
| Stat labels | `data/stats_layout.json` | Abbreviate ~20 label texts |
| Stats panel | `game/ui/panels/design_stats_panel.py` | Fix header label heights (lines 260, 262) |
| Build queue | `game/ui/screens/build_queue_screen.py` | Fix label height (839), truncation (831) |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Abbreviate labels, don't widen ratio | User preference — keeps layout ratios stable |
| 2026-02-09 | Delete legacy BattleEngine tests | User preference — legacy API is deprecated, tests unnecessary |
| 2026-02-09 | Filter pygame_gui cosmetic warnings | Cannot fix in project code; benign in test environments |
| 2026-02-09 | Use AIControllerFactory (not BattleOrchestrator) for tests | Tests are simulation-layer; factory is the simulation-layer tool |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Quick Wins — Slider, Deprecation, Clamping [Simple]
**Objective:** Fix the three categories with precise, localized fixes
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Label Rect Fixes [Medium]
**Objective:** Eliminate all label overflow warnings via abbreviation and height fixes
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Verification & Regression Guard [Simple]
**Objective:** Validate zero warnings and add enforcement
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - all tests pass (establishes baseline: 7353 passed, 299 warnings)

### After Each Phase
- [ ] Run `pytest tests/ -n 12 --tb=short` - all tests pass, warning count reduced
- [ ] Verify no functional regressions

### Final Verification
- [ ] Run `pytest tests/ -n 12` — 7353+ passed, 0 warnings (filtered ones silenced)
- [ ] Verify builder UI labels still readable in-game (visual spot check)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing
- [ ] Zero warnings in test output
- [ ] Audit passed (no significant issues)
- [ ] User verified
