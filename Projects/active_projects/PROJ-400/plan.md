# PROJ-400: Tier 1 B-01 — NewGameSetupScreen `_create_ui()` calls deleted wrapper

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix call site + add coverage | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Closeout
**Last Action:** Phase 1 complete — `_create_ui()` now calls `NewGameSetupController.generate_default_save_name()`; regression test class `TestCreateUiConstructionPath` (2 tests) added; focused suite 104 passed.
**Next Action:** User verification of "New Game" UI launch. Awaiting confirmation to archive.
**Blockers:** None

## Overview
PROJ-392 Task 2.9 deleted `NewGameSetupScreen.generate_default_save_name` (a static wrapper) but missed an unmigrated production caller in the same file. `_create_ui()` line 348 still reads `self.save_name_input.set_text(self.generate_default_save_name())`, which raises `AttributeError` when the live New Game UI is constructed. This project fixes that single call site and adds coverage that exercises `_create_ui()` end-to-end so the same blind spot doesn't recur.

## Goals
- Replace `self.generate_default_save_name()` at `new_game_setup_screen.py:348` with a call routed through the controller (same call PROJ-392 used everywhere else).
- Add a regression test that constructs `NewGameSetupScreen` (or builds it via `NewGameSetupUiBuilder`) far enough to traverse `_create_ui()` so any remaining missing-static blind spot is caught.

## Scope
**In:**
- One production call site fix in `game/ui/screens/new_game_setup_screen.py`.
- One regression test exercising the production construction path.

**Out:**
- The PROJ-392 test polish referenced as INFO/MINOR in the consolidated review.
- Any other PROJ-392 deferrals.

## Key Files
| Component | File Path |
|-----------|-----------|
| Production caller | `game/ui/screens/new_game_setup_screen.py` |
| Controller (canonical) | `game/ui/screens/new_game_setup_controller.py` |
| Regression coverage | `tests/unit/ui/screens/test_new_game_setup_screen.py` (likely) |

## Source Evidence (REMEDIATION_PLAN B-01)
- `game/ui/screens/new_game_setup_screen.py:348` — `self.save_name_input.set_text(self.generate_default_save_name())`
- `hasattr(NewGameSetupScreen, "generate_default_save_name") == False`
- `hasattr(NewGameSetupController, "generate_default_save_name") == True`
- PROJ-392 review (`Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-392_report.md`)

## Verification
- [ ] Phase 1 checklist complete
- [ ] `pytest tests/unit/ui/screens/test_new_game_setup_screen.py -v` passes including new regression
- [ ] `pytest tests/ -k new_game_setup` passes (focused suite from PROJ-392)
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-400` passes
- [ ] User verified
