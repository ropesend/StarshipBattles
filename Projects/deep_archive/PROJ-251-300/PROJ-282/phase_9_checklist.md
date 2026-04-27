# Phase 9: Add line-budget convention to docs/03_CONVENTIONS.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Document the anti-rebloat line-budget convention that makes the MVVM pattern durable. Without a documented rule, future contributors will pile UI logic back into the screen.

---

## Tasks

### Task 9.1: Add "UI screen line budget" section to docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** N/A

- [x] Added as [§ 2.4 UI Screen Line Budget (PROJ-282)](../../../docs/03_CONVENTIONS.md) — placed under "2. File Organization" next to the existing § 2.3 File Size rule
- [x] Content lists the full MVVM delegate roster (Controller / ViewModel / Renderer / InputHandler / domain helpers), cross-references the two exemplars (`TestLabScreen`, `FleetBattleSetupScreen`), and frames the ≤300 LOC limit as a **review signal, not a blocker** — matches the Phase 1 audit's recommendation
- [x] Didn't add to docs/02_PATTERNS.md — 03_CONVENTIONS.md is the better home per the docs/README.md reading-order guidance
- [x] Added a subsection (the example text below is preserved as the design reference; the actual section wording matches with minor wording polish):
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
- [x] Cross-link from docs/02_PATTERNS.md skipped — MVVM isn't currently listed there as a first-class pattern entry; adding it would be scope creep. The convention's placement in 03_CONVENTIONS.md § 2.4 is discoverable via the doc index's reading order.

**Notes:** The added section explicitly frames the 300-line rule as a **soft review signal**, not a blocker. Cites that "a Controller over 300 lines is a review signal — not a blocker" so reviewers have grounds to push back without turning the convention into a brittle gate. Concentrated single-responsibility cases (our `controller.py` at 523 LOC after Phase 7) are explicitly acknowledged as acceptable.

### Task 9.2: Add cross-references in screen files [Simple]
**File:** `game/ui/screens/battle_setup/screen.py`, `game/ui/screens/test_lab/screen.py`
**Tests:** N/A

- [x] Added a module docstring paragraph in [battle_setup/screen.py](../../../game/ui/screens/battle_setup/screen.py) pointing at `docs/03_CONVENTIONS.md § 2.4 UI Screen Line Budget` and naming `TestLabScreen` as the sibling exemplar
- [x] Added the symmetric cross-reference to [test_lab/screen.py](../../../game/ui/screens/test_lab/screen.py) naming `FleetBattleSetupScreen` as the sibling exemplar
- [x] Both paragraphs say "Target: keep the class under 300 lines" — consistent with the convention

**Notes:** Both screens now anchor the MVVM pattern at the module-docstring level. A reader opening either screen file finds the convention reference immediately.

### Task 9.3: Document FleetHierarchyEditor as reusable [Simple]
**File:** N/A — skipped (low-priority polish per checklist)
**Tests:** N/A

- [x] Skipped per Task 9.3's "Low-priority polish; only do if there's a natural section to drop it into" clause. `docs/systems/strategy_layer.md` doesn't currently have a fleet-editing section to extend, and adding one is scope creep. The editor's docstring at [fleet_hierarchy_editor.py](../../../game/ui/screens/battle_setup/fleet_hierarchy_editor.py) already notes its reusability ("can be used by other screens that want to edit fleet hierarchies (e.g. a future fleet-orders window)").

**Notes:** When a future fleet-orders screen actually uses `FleetHierarchyEditor`, that's the right time to add a strategy_layer.md section — documented as seen, not speculated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `docs/03_CONVENTIONS.md` has the line-budget section (§ 2.4)
- [x] Both MVVM screens (battle_setup + test_lab) cross-reference the convention in their module docstrings
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 10 (manual smoke)
