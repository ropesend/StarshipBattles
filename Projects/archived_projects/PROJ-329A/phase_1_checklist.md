# PROJ-329A Phase 1 — Inventory matrix

**Status:** Complete
**Goal:** Produce the canonical UIWindow / StrategyModalWindow subclass inventory that PROJ-329A/B/C and PROJ-330 will reference.

## Tasks

### Task 1.1: Build the matrix [Simple]

- [x] Run grep to enumerate all UIWindow + StrategyModalWindow subclasses: `grep -lE "class.*\(.*UIWindow\)|class.*\(.*StrategyModalWindow\)" game/ui/screens/ -r` (returns 24 paths).
- [x] For each class, capture: production file, LOC, test file(s) (or `none`), current test pattern (`__new__`/`bypass_init`/Compositional/two-stage/none), builder seam present?, Stage-1 side effects (yes/no + brief), risk tier, project assignment.
- [x] Verify the 6 already-done classes (PROJ-325/328) are marked done with project reference.
- [x] Verify the 2 deferred classes (DesignWorkshopScreen, SettingsWindow) are marked deferred with cross-ref to `docs/known-issues.md`.
- [x] Cross-project file-overlap verification table: confirm no production file appears in two projects.

### Task 1.2: Verify the 5 PROJ-329A fast-win targets [Simple]

- [x] FoodAllocationEditor — confirmed `class FoodAllocationEditor(StrategyModalWindow):` at `food_allocation_editor.py:158`. 360 LOC.
- [x] FleetSelectionWindow — confirmed `StrategyModalWindow` subclass. 123 LOC. No tests.
- [x] PlanetSelectionWindow — confirmed `StrategyModalWindow` subclass. 189 LOC. No tests.
- [x] MoveChoiceWindow — confirmed `StrategyModalWindow` subclass at `strategy_windows/move_choice_dialog.py`. 94 LOC. No tests.
- [x] PlanetTargetEditor — confirmed `class PlanetTargetEditor(RaceConfigResolverMixin, StrategyModalWindow):`. 63 LOC. No tests. (Multiple-inheritance — flag during Phase 2 retrofit.)

## Verification

- [x] Inventory matrix present at `findings/uiwindow_inventory.md`.
- [x] Row count = 25 (24 UIWindow subclasses + 1 deferred DesignWorkshopScreen for completeness).
- [x] Summary table sums to 7 done + 5 (329A) + 8 (329B) + 3 (329C) + 2 deferred = 25 ✓.

## Phase Completion

- [x] All Task 1.X complete.
- [ ] Commit Phase 0 + Phase 1 together as `docs(329A): UIWindow inventory matrix + deferral disposition`. _(Combined with Phase 0 per per-class commit discipline; setup docs land together.)_
