# PROJ-14: Legacy Cleanup Phase 1 - Delete Dead Code

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-14` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-14 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Directories and Files | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Remove Commented/Dead Code | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Main Menu Buttons | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate Test Lab Buttons | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Tests and Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-25
**Active Phase:** Phase 3 Complete - Manual Testing Required
**Last Action:** Completed Phase 1 (deletions), Phase 2 (dead code removal), Phase 3 (UIButton migration)
**Next Action:** Manual verification of main menu, then Phase 4 (Test Lab migration)
**Blockers:** None - all implementation complete
**Context for Next Agent:**
- Phases 1-3 implemented: Deleted 2 directories, 5 log files, 14 debug tools. Removed 95+ lines of dead code. Migrated 10 menu buttons from legacy Button to pygame_gui UIButton.
- **CRITICAL**: User must manually verify main menu works before proceeding to Phase 4:
  - Launch game (`python main.py`)
  - Verify all 10 menu buttons are visible with pygame_gui styling
  - Click each button to verify state transitions
  - Test resize behavior and hover states
- Tests pass: testmon shows 2 tests affected (integration tests), all passing
- Pre-existing failure unchanged: `test_intercept_integration` (unrelated mock issue)

## Overview
Phase 1 of the 8-phase legacy cleanup effort. This phase deletes dead code, removes commented debug code, and migrates the legacy Button class to pygame_gui UIButton.

## Goals
- Delete files/directories marked for deletion
- Remove log files from repo and update .gitignore
- Delete debug tools from Tools/ directory
- Remove commented/dead code from production files
- Migrate legacy Button class to pygame_gui UIButton
- Delete ui/components.py after migration

## Scope
**In Scope:**
- Directory deletion: `Marked_For_Deletion_2026-01-21_07-33/`, `MagicMock/`
- Log file cleanup + .gitignore update
- 15 debug tools in Tools/ directory
- Commented code in 6 files
- Button migration in `game/app.py` (10 buttons) and `ui/test_lab_scene.py` (4 buttons)
- Test file deletion: `tests/unit/ui/test_ui_widgets.py`

**Out of Scope:**
- `Debugging/Marked_for_Deletion_2026-01-20/` (doesn't exist - already cleaned)
- `game/core/logger.py` line 38 (already refactored)
- Tools/ Button classes in `component_manager.py`, `component_graphic_picker.py` (tool-specific)
- Phases 2-8 of legacy cleanup

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Legacy Button | `ui/components.py` | `Button`, `Label`, `Slider` |
| Main Menu | `game/app.py:125-137` | `update_menu_buttons()` |
| Test Lab Scene | `ui/test_lab_scene.py:18,113,2321` | `JSONPopup`, `ConfirmationDialog`, `btn_back` |
| Widget Tests | `tests/unit/ui/test_ui_widgets.py` | `TestButton`, `TestLabel`, `TestSlider` |
| UI Package | `ui/__init__.py:2` | Button re-export |
| Theme | `data/builder_theme.json` | Button styling |
| Pattern Example | `game/ui/screens/save_selection_window.py` | UIButton event handling |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Delete logs AND add to .gitignore | Prevent future tracking of regenerated logs |
| 2026-01-25 | Include Button migration in Phase 1 | Keep cleanup comprehensive as originally planned |
| 2026-01-25 | Skip missing items silently | Directory/code already cleaned up |
| 2026-01-25 | Delete test_ui_widgets.py rather than migrate | Tests become obsolete; integration tests cover behavior |

## Initial Analysis
- **Test Baseline:** 4561 passed, 1 failed (pre-existing), 1 skipped
- **Directories verified:** `Marked_For_Deletion_2026-01-21_07-33/` (45MB), `MagicMock/` (4KB) exist and are safe to delete
- **Debug tools verified:** All 15 files exist with no dependencies
- **Button usage found:** 10 in `game/app.py`, 4 in `ui/test_lab_scene.py`

## Swarm Findings Summary
### Architecture
- Main menu uses legacy Button with direct callbacks
- pygame_gui already used extensively (86 files) with UIManager pattern
- Event handling: Legacy uses `handle_event()` → callback(); pygame_gui uses `UI_BUTTON_PRESSED` events

### Key Patterns to Reuse
- **UIButton Creation**: `game/ui/screens/save_selection_window.py:80-85` - standard button pattern
- **Event Handling**: `game/ui/screens/save_selection_window.py:198-210` - UI_BUTTON_PRESSED pattern
- **Theme Styling**: `data/builder_theme.json:39-55` - button color/shape definitions

### Risks Identified
1. **Main menu critical path (HIGH)** - Menu is first thing users see; if migration fails, game unplayable
   - Mitigation: Test thoroughly after Phase 3; have rollback plan (`git revert`)
2. **Test Lab dialogs (MEDIUM)** - If buttons fail, dialogs can't be dismissed
   - Mitigation: Test each dialog after Phase 4
3. **Log file regeneration (LOW)** - Deleted logs will regenerate on next run
   - Mitigation: Already adding to .gitignore

---

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - baseline established (4561 passed, 1 failed pre-existing)

### After Phase 1 (Deletions)
- [x] Run `pytest tests/ --testmon` - no import errors
- [x] Verify application launches: `python -c "from game.app import Game"`

### After Phase 2 (Commented Code)
- [x] Run `pytest tests/ --testmon` - all tests pass
- [x] No functionality changes

### After Phase 3 (Main Menu Migration) - CRITICAL
- [x] Run `pytest tests/ --testmon`
- [ ] Manual: Launch game - menu displays
- [ ] Manual: All 10 buttons visible
- [ ] Manual: Click each button - correct state transition
- [ ] Manual: Resize window - buttons reposition
- [ ] Manual: Hover states work

### After Phase 4 (Test Lab Migration)
- [ ] Run `pytest tests/ --testmon`
- [ ] Manual: Combat Lab loads
- [ ] Manual: Back button works
- [ ] Manual: JSON popup close works
- [ ] Manual: Confirmation dialog confirm/cancel work

### Final Verification
- [ ] Run full test suite: `pytest tests/` (NOT --testmon)
- [ ] Manual: Complete flow through all scenes
- [ ] No import errors or deprecation warnings

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing (4561+ passed, same pre-existing failure allowed)
- [ ] Manual verification complete
- [ ] Audit passed
- [ ] User verified
