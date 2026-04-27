# Phase 2: Decomposition design (10 files)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** For each of the 10 target files, produce a per-file decomposition design. Each design lives at `findings/<filename>_decomposition.md` and answers: what sub-modules emerge, what each owns, public API choices, caller-update strategy, test plan.

**Prerequisites:** Phase 1 complete — convention is documented.

---

## Per-file design template

Each design doc must answer:

```markdown
# Decomposition Design: <filename>

**Current size:** N lines
**Target post-split:** every resulting module <500 lines

## Current responsibilities
List every distinct thing this module does (often 5+).

## Proposed sub-modules
For each new module:
- Path
- Responsibilities (one bullet)
- Symbols it owns
- Estimated LOC

## Public API surface
Which symbols must remain importable from the original module name?

## Caller-update strategy
- Option A (re-export shim): _why_
- Option B (caller migration): _why_

## Test plan
- Existing tests likely affected
- New tests required (e.g., a test verifying the public API contract is preserved)

## Risks
- Import cycles?
- Hidden coupling between proposed sub-modules?
- Anything that prevents this from being a clean split?
```

---

## Tasks

### Task 2.1: Design `race_setup_screen.py` decomposition [Medium]
**File:** `Projects/active_projects/PROJ-309/findings/race_setup_screen_decomposition.md` (NEW)
**Tests:** None — design step.

- [ ] Read `game/ui/screens/race_setup_screen.py` (1588 lines)
- [ ] Identify distinct responsibilities (genome editing, traits, preview, controls, etc.)
- [ ] Propose sub-module layout under `game/ui/screens/race_setup/`
- [ ] Document caller-update strategy
- [ ] Save to `findings/race_setup_screen_decomposition.md`

**Notes:**

---

### Task 2.2: Design `strategy_renderer.py` decomposition [Medium]
**File:** `findings/strategy_renderer_decomposition.md`
**Tests:** None.

- [ ] Read `game/ui/screens/strategy_renderer.py` (1205 lines)
- [ ] Identify render-layer concerns
- [ ] Propose sub-module layout
- [ ] Save to `findings/strategy_renderer_decomposition.md`

**Notes:**

---

### Task 2.3: Design `test_lab/renderer.py` decomposition [Medium]
**File:** `findings/test_lab_renderer_decomposition.md`
**Tests:** None.

- [ ] Read `game/ui/screens/test_lab/renderer.py` (1193 lines)
- [ ] Save to `findings/test_lab_renderer_decomposition.md`

**Notes:**

---

### Task 2.4: Design `core/protocols.py` decomposition [Medium]
**File:** `findings/core_protocols_decomposition.md`
**Tests:** None.

- [ ] Read `game/core/protocols.py` (1087 lines)
- [ ] Group protocols by domain (combat / strategy / AI / UI / registry)
- [ ] Propose package layout: `game/core/protocols/__init__.py` (re-export) + per-domain files
- [ ] **Caller-update strategy: Option A is mandatory** — too many callers
- [ ] Save to `findings/core_protocols_decomposition.md`

**Notes:** Heavy import surface. Re-export from package `__init__.py` is the only viable strategy.

---

### Task 2.5: Design `command_handlers.py` decomposition [Medium]
**File:** `findings/command_handlers_decomposition.md`
**Tests:** None.

- [ ] Read `game/strategy/engine/command_handlers.py` (1072 lines)
- [ ] One handler-class-per-file under `game/strategy/engine/handlers/`
- [ ] Save to `findings/command_handlers_decomposition.md`

**Notes:** PROJ-298 just touched this file (renamed handler classes). Confirm latest state before designing.

---

### Task 2.6: Design `test_run_details.py` decomposition [Medium]
**File:** `findings/test_run_details_decomposition.md`
**Tests:** None.

- [ ] Read `game/ui/screens/test_lab/test_run_details.py` (957 lines)
- [ ] Save to `findings/test_run_details_decomposition.md`

**Notes:**

---

### Task 2.7: Design `strategy_session_facade.py` decomposition [Medium]
**File:** `findings/strategy_session_facade_decomposition.md`
**Tests:** None.

- [ ] Read `game/strategy/facade/strategy_session_facade.py` (922 lines)
- [ ] Per-domain slices (fleet, planet, research, economy, ...)
- [ ] Save to `findings/strategy_session_facade_decomposition.md`

**Notes:**

---

### Task 2.8: Design `workshop_viewmodel.py` decomposition [Medium]
**File:** `findings/workshop_viewmodel_decomposition.md`
**Tests:** None.

- [ ] Read `game/ui/screens/workshop_viewmodel.py` (873 lines)
- [ ] Save to `findings/workshop_viewmodel_decomposition.md`

**Notes:**

---

### Task 2.9: Design `app.py` decomposition [Medium]
**File:** `findings/app_decomposition.md`
**Tests:** None.

- [ ] Read `game/app.py` (849 lines)
- [ ] Bootstrap / run-loop / screen management probably the three concerns
- [ ] Save to `findings/app_decomposition.md`

**Notes:**

---

### Task 2.10: Design `strategy_window_manager.py` decomposition [Medium]
**File:** `findings/strategy_window_manager_decomposition.md`
**Tests:** None.

- [ ] Read `game/ui/screens/strategy_window_manager.py` (817 lines)
- [ ] Save to `findings/strategy_window_manager_decomposition.md`

**Notes:**

---

### Task 2.11: Cross-design review [Simple]
**File:** None — review step.
**Tests:** None.

- [ ] Read all 10 design docs back-to-back
- [ ] Look for overlap (does the protocols split affect the renderer split?)
- [ ] Look for inconsistencies (one design uses Option A, similar file uses Option B — same reasons?)
- [ ] If any design has unanswered questions or weak risk analysis, send back

**Notes:**

---

## Phase Completion Checklist
- [ ] All 10 design docs exist in `findings/`
- [ ] Each design has all template sections filled
- [ ] Cross-design review complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3)
