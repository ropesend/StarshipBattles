# Phase 9: Add line-budget convention to docs/03_CONVENTIONS.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Document the anti-rebloat line-budget convention that makes the MVVM pattern durable. Without a documented rule, future contributors will pile UI logic back into the screen.

---

## Tasks

### Task 9.1: Add "UI screen line budget" section to docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** N/A

- [ ] Find the right location — probably near existing UI-layer conventions or file-organization rules
- [ ] Add a subsection:
  ```markdown
  ### UI screen line budgets (PROJ-282)

  UI screen classes (anything implementing `IScene`) should stay **under 300 lines**.

  Logic for mutation, derived view state, rendering, and event handling should
  live in sibling delegate classes (Controller, ViewModel, Renderer, InputHandler)
  following the MVVM pattern established by `TestLabScreen` and
  `FleetBattleSetupScreen` (post-PROJ-282).

  If you find yourself adding a method to a screen class that has more than
  300 lines, stop and identify which delegate it belongs in.

  Sibling delegate classes should also stay under 300 lines each. A Controller
  over 300 lines suggests the mutation surface is too large — consider extracting
  a sub-service (e.g. `FleetHierarchyEditor` in Battle Setup).
  ```
- [ ] Cross-link from [docs/02_PATTERNS.md](../../../docs/02_PATTERNS.md) if MVVM is listed there

**Notes:** This is a SOFT limit — the goal is to make rebloat visible to reviewers, not to enforce a brittle cap.

### Task 9.2: Add cross-references in screen files [Simple]
**File:** `game/ui/screens/battle_setup/screen.py`, `game/ui/screens/test_lab/screen.py`
**Tests:** N/A

- [ ] Add a module docstring note pointing at the conventions doc: "This screen follows the MVVM pattern documented in `docs/03_CONVENTIONS.md § UI screen line budgets`. Keep the class under 300 lines — delegate logic to ViewModel/Renderer/InputHandler/Controller."
- [ ] If TestLabScreen didn't have such a note, add it so both exemplars point at the same rule

**Notes:**

### Task 9.3: Document FleetHierarchyEditor as reusable [Simple]
**File:** `docs/systems/strategy_layer.md` (or wherever fleet-hierarchy editing is documented)
**Tests:** N/A

- [ ] Note that `FleetHierarchyEditor` can be reused by future screens that edit fleet hierarchy (e.g. fleet-orders window)
- [ ] Low-priority polish; only do if there's a natural section to drop it into

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `docs/03_CONVENTIONS.md` has the line-budget section
- [ ] Screen files cross-reference the convention
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 10 (manual smoke)
