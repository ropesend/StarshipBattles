# Phase 6: Document Intentional Broad Catches & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify all remaining `except Exception` sites are intentional and documented with inline comments.
**Tests:** `pytest tests/` (full suite)

---

## Tasks

### Task 6.1: Verify remaining broad catches [Simple]

Run `grep -rn "except Exception" game/` and confirm only these intentional sites remain:

- [ ] `game/app.py:745` — Top-level crash handler (re-raises)
- [ ] `game/core/logger.py:107` — Event handler isolation
- [ ] `game/core/screenshot_manager.py:134` — Tkinter clipboard (commented in Phase 1)
- [ ] `game/core/screenshot_manager.py:146` — Subprocess clipboard (commented in Phase 1)
- [ ] `game/simulation/formula_system.py:139` — Catch-and-convert to FormulaException
- [ ] `game/simulation/components/modifier_effects.py:178` — Catch-and-convert to FormulaException
- [ ] `game/simulation/entities/ship_serialization.py:107` — Safety net with re-raise (commented in Phase 1)
- [ ] `game/simulation/systems/persistence.py:20` — Tkinter init (commented in Phase 1)
- [ ] `game/ui/screens/builder/event_bus.py:55` — Event handler isolation (commented in Phase 4)
- [ ] `game/ui/screens/workshop_screen.py:930` — Tkinter dialog (commented in Phase 5)
- [ ] Verify NO unexpected `except Exception` sites exist

**Notes:**

---

### Task 6.2: Add comments to remaining un-commented sites [Simple]

Sites commented in earlier phases: screenshot_manager (2), persistence (1), ship_serialization (1), event_bus (1), workshop_screen (1).
These 4 still need comments:

- [ ] `game/app.py:745`: Add comment: `# Intentional broad catch: top-level crash handler, logs and re-raises`
- [ ] `game/core/logger.py:107`: Add comment: `# Intentional broad catch: event handler isolation, handler bugs must not crash callers`
- [ ] `game/simulation/formula_system.py:139`: Add comment: `# Intentional broad catch: catch-and-convert to FormulaException for any eval() error`
- [ ] `game/simulation/components/modifier_effects.py:178`: Add comment: `# Intentional broad catch: catch-and-convert to FormulaException for any eval() error`

**Notes:**

---

### Task 6.3: Final verification [Simple]

- [ ] Run full test suite: `pytest tests/` — all 6248+ tests pass
- [ ] Run: `grep -rn "except Exception" game/` — exactly ~10 intentional sites
- [ ] Run: `grep -rn "except Exception" game/ | grep -v "Intentional broad catch"` — should return 0 uncommented lines
- [ ] Run: `grep -rn "print(" game/ui/screens/builder/detail_panel.py game/ui/screens/builder/right_panel.py game/ui/screens/builder/stats_config.py game/ui/screens/test_lab.py` — no `print()` in error handlers
- [ ] Total reduction: 90 → ~10 (89% reduction)

**Notes:**

---

## Phase Completion Checklist (PROJECT FINAL)
When all tasks above are done:
- [ ] All intentional sites documented with comments
- [ ] Full test suite passes
- [ ] No un-documented broad catches remain
- [ ] No print() calls in error handlers
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md all phase statuses to `Complete`
