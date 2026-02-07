# Phase 6: Document Intentional Broad Catches & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Verify all remaining `except Exception` sites are intentional and documented with inline comments.
**Tests:** `pytest tests/` (full suite)

---

## Tasks

### Task 6.1: Verify remaining broad catches [Simple]

Run `grep -rn "except Exception" game/` and confirm only these intentional sites remain:

- [x] `game/app.py:745` — Top-level crash handler (re-raises)
- [x] `game/core/logger.py:107` — Event handler isolation
- [x] `game/core/screenshot_manager.py:134` — Tkinter clipboard (commented in Phase 1)
- [x] `game/core/screenshot_manager.py:146` — Subprocess clipboard (commented in Phase 1)
- [x] `game/simulation/formula_system.py:139` — Catch-and-convert to FormulaException
- [x] `game/simulation/components/modifier_effects.py:178` — Catch-and-convert to FormulaException
- [x] `game/simulation/entities/ship_serialization.py:107` — Safety net with re-raise (commented in Phase 1)
- [x] `game/simulation/systems/persistence.py:20` — Tkinter init (commented in Phase 1)
- [x] `game/ui/screens/builder/event_bus.py:55` — Event handler isolation (commented in Phase 4)
- [x] `game/ui/screens/workshop_ship_io.py:259` — Tkinter dialog (added in Phase 6)
- [x] `game/ui/screens/workshop_data_reloader.py:20` — Tkinter init (added in Phase 6)
- [x] `game/ui/screens/planet_list_window.py:418` — UI toast (commented in earlier phase)
- [x] Verify NO unexpected `except Exception` sites exist

**Notes:**
- Several sites from previous phases were missed and had to be narrowed in Phase 6:
  - build_queue_portraits.py:96 → pygame.error
  - workshop_ship_io.py:163 → (OSError, ValueError, KeyError)
  - build_queue_controller.py:183 → (OSError, ValueError, KeyError)
  - workshop_data_reloader.py:152 → (OSError, ValueError, KeyError)
  - test_lab/screen.py: 6 sites → narrowed to specific exceptions

---

### Task 6.2: Add comments to remaining un-commented sites [Simple]

Sites commented in earlier phases: screenshot_manager (2), persistence (1), ship_serialization (1), event_bus (1).
These still needed comments (added in Phase 6):

- [x] `game/app.py:745`: Add comment: `# Intentional broad catch: top-level crash handler, logs and re-raises`
- [x] `game/core/logger.py:107`: Add comment: `# Intentional broad catch: event handler isolation prevents handler bugs from crashing callers`
- [x] `game/simulation/formula_system.py:139`: Add comment: `# Intentional broad catch: catch-and-convert to FormulaException for any eval() error`
- [x] `game/simulation/components/modifier_effects.py:178`: Add comment: `# Intentional broad catch: catch-and-convert to FormulaException for any eval() error`

**Notes:**

---

### Task 6.3: Final verification [Simple]

- [x] Run full test suite: `pytest tests/` — 6244 passed (2 pre-existing failures unrelated to this project)
- [x] Run: `grep -rn "except Exception" game/` — exactly 12 intentional sites
- [x] Run: `grep -rn "except Exception" game/ | grep -v "Intentional broad catch"` — returns 0 lines (all documented)
- [x] Total reduction: 90 → 12 (87% reduction)

**Notes:**
- 2 test failures are pre-existing screenshot-related issues unrelated to PROJ-64
- All 12 remaining sites have "Intentional broad catch" comments

---

## Phase Completion Checklist (PROJECT FINAL)
When all tasks above are done:
- [x] All intentional sites documented with comments
- [x] Full test suite passes (6244 passed, 2 pre-existing failures)
- [x] No un-documented broad catches remain
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md Current State to `Complete`
- [x] Update plan.md all phase statuses to `Complete`
