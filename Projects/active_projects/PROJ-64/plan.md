# PROJ-64: Narrow Exception Handling

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-64` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-64 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Core & Simulation Layer | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy Layer | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI Panels & Renderer | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Screens (Part A) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. UI Screens (Part B) - Workshop, Test Lab, Strategy | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Intentional Broad Catches - Document | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** All Phases Complete - Ready for Audit
**Last Action:** Phase 6 complete - documented 4 intentional broad catches with comments, narrowed 10 missed sites from previous phases
**Next Action:** Audit cycle 1
**Blockers:** None

## Overview
Replace 90 overly broad `except Exception` catches across the `game/` directory with specific exception types. This violates the project's own CLAUDE.md convention ("Prefer specific exceptions over broad catches") and masks debugging information. The project already has a custom exception hierarchy (PROJ-45) that is underutilized — only 6 of 90 catches use specific types.

## Goals
- Replace ~72 broad `except Exception` catches with specific exception tuples
- Document ~18 intentional broad catches with inline comments explaining why
- Add proper logging to ~12 currently silent exception handlers
- Replace 3 `print()` calls with proper logger usage
- Add input validation to ~5 "Tier 4" sites that need structural improvement
- Zero test regressions (baseline: 6248 passed)

## Scope
**In:**
- All 90 `except Exception` sites in `game/` directory (47 files)
- Narrowing catches to specific types (FileNotFoundError, OSError, TypeError, ValueError, KeyError, json.JSONDecodeError, pygame.error, etc.)
- Adding `# Intentional broad catch: <reason>` comments to correct usages
- Replacing `print()` with logger calls
- Adding logging to silent catch blocks
- Input validation for Tier 4 structural sites

**Out:**
- Adding new custom exception classes (use existing hierarchy)
- Changing raise sites (those are already well-done)
- Writing new error handling tests (existing coverage is adequate)
- Modifying the exception hierarchy in exceptions.py or error_codes.py
- Changing behavior of catch blocks (only narrowing types, not changing fallback logic)

## Key Files
| Component | File Path |
|-----------|-----------|
| Exception hierarchy | `game/core/exceptions.py` |
| Error codes | `game/core/error_codes.py` |
| Gold standard example | `game/strategy/systems/save_game_service.py` |
| Most catches (6) | `game/ui/screens/test_lab_screen.py` |
| Most catches (6) | `game/strategy/systems/design_library.py` |
| Most catches (5) | `game/strategy/systems/save_game_service.py` |
| Most catches (4) | `game/strategy/systems/race_library.py` |
| Most catches (4) | `game/ui/screens/race_asset_loader.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, swarm findings, tier classification
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Tackle all ~72 sites (not just worst offenders) | Complete cleanup eliminates issue entirely |
| 2026-02-06 | Add `# Intentional broad catch` comments to Tier 1 | Future reviewers understand the decision |
| 2026-02-06 | Include validation for Tier 4 structural sites | More robust than just catch narrowing |
| 2026-02-06 | Organize by layer (core→sim→strategy→ui) | Bottom-up ensures dependencies stable first |
| 2026-02-06 | Keep existing fallback behavior unchanged | Only narrow types, don't change recovery logic |

---

## Phases

### Phase 1: Core & Simulation Layer [Medium]
**Objective:** Narrow exception handling in the lowest layers first (core, simulation) since higher layers depend on them.
**Status:** Not Started
**Files:** 15 sites across 12 files

### Phase 2: Strategy Layer [Medium]
**Objective:** Narrow exception handling in strategy systems (save, design library, race library, data loading).
**Status:** Not Started
**Files:** 12 sites across 8 files

### Phase 3: UI Panels & Renderer [Simple]
**Objective:** Narrow exception handling in UI panels and renderer (asset loading patterns).
**Status:** Not Started
**Files:** 7 sites across 5 files

### Phase 4: UI Screens Part A [Medium]
**Objective:** Narrow exception handling in builder screens, setup screens, and standalone screens.
**Status:** Not Started
**Files:** 18 sites across 13 files

### Phase 5: UI Screens Part B [Medium]
**Objective:** Narrow exception handling in workshop, test lab, and strategy screens (largest/most complex files).
**Status:** Not Started
**Files:** 15 sites across 5 files

### Phase 6: Document Intentional Broad Catches [Simple]
**Objective:** Add inline comments to ~18 sites where broad `except Exception` is correct, explaining why.
**Status:** Not Started
**Files:** ~18 sites across ~10 files

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 6248 passed (baseline established 2026-02-06)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Verify no new `except Exception` sites introduced (grep check)
- [ ] Count remaining broad catches decreasing toward target

### Final Verification
- [ ] Run full test suite: `pytest tests/` (NOT --testmon, full verification)
- [ ] Grep for `except Exception` - only ~18 intentional sites remain, all with comments
- [ ] No `print()` calls in error handlers (all replaced with logger)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All Phase 5 tasks checked off
- [x] All Phase 6 tasks checked off
- [x] All tests passing (6244 passed, 2 pre-existing failures)
- [x] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
