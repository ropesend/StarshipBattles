# Phase 2: Decomposition design (10 files)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Read `game/ui/screens/race_setup_screen.py` (1588 lines)
- [x] Identify distinct responsibilities (genome editing, traits, preview, controls, etc.)
- [x] Propose sub-module layout under `game/ui/screens/race_setup/`
- [x] Document caller-update strategy
- [x] Save to `findings/race_setup_screen_decomposition.md`

**Notes:**

---

### Task 2.2: Design `strategy_renderer.py` decomposition [Medium]
**File:** `findings/strategy_renderer_decomposition.md`
**Tests:** None.

- [x] Read `game/ui/screens/strategy_renderer.py` (1205 lines)
- [x] Identify render-layer concerns
- [x] Propose sub-module layout
- [x] Save to `findings/strategy_renderer_decomposition.md`

**Notes:**

---

### Task 2.3: Design `test_lab/renderer.py` decomposition [Medium]
**File:** `findings/test_lab_renderer_decomposition.md`
**Tests:** None.

- [x] Read `game/ui/screens/test_lab/renderer.py` (1193 lines)
- [x] Save to `findings/test_lab_renderer_decomposition.md`

**Notes:**

---

### Task 2.4: Design `core/protocols.py` decomposition [Medium]
**File:** `findings/core_protocols_decomposition.md`
**Tests:** None.

- [x] Read `game/core/protocols.py` (1087 lines)
- [x] Group protocols by domain (combat / strategy / AI / UI / registry)
- [x] Propose package layout: `game/core/protocols/__init__.py` (re-export) + per-domain files
- [x] **Caller-update strategy: Option A is mandatory** — too many callers
- [x] Save to `findings/core_protocols_decomposition.md`

**Notes:** Heavy import surface — 132 import statements across 80 files. Option A re-export mandatory. Final layout (post-cross-review): 9 sub-modules — `__init__.py`, `common.py`, `registry.py`, `strategy_entities.py` (~340 LOC), `strategy_domain.py` (~180 LOC), `combat.py`, `boundary.py`, `ui.py`, `persistence.py`. The original "single `strategy.py`" estimate was ~520 LOC (over cap); cross-review locked the upfront entities/domain split per the natural source-file seam (lines 116–460 vs 467–625).

---

### Task 2.5: Design `command_handlers.py` decomposition [Medium]
**File:** `findings/command_handlers_decomposition.md`
**Tests:** None.

- [x] Read `game/strategy/engine/command_handlers.py` (1072 lines)
- [x] One handler-class-per-file under `game/strategy/engine/handlers/`
- [x] Save to `findings/command_handlers_decomposition.md`

**Notes:** PROJ-298 just touched this file (renamed handler classes). Confirm latest state before designing.

---

### Task 2.6: Design `test_run_details.py` decomposition [Medium]
**File:** `findings/test_run_details_decomposition.md`
**Tests:** None.

- [x] Read `game/ui/screens/test_lab/test_run_details.py` (957 lines)
- [x] Save to `findings/test_run_details_decomposition.md`

**Notes:**

---

### Task 2.7: Design `strategy_session_facade.py` decomposition [Medium]
**File:** `findings/strategy_session_facade_decomposition.md`
**Tests:** None.

- [x] Read `game/strategy/facade/strategy_session_facade.py` (922 lines)
- [x] Per-domain slices (fleet, planet, research, economy, ...)
- [x] Save to `findings/strategy_session_facade_decomposition.md`

**Notes:**

---

### Task 2.8: Design `workshop_viewmodel.py` decomposition [Medium]
**File:** `findings/workshop_viewmodel_decomposition.md`
**Tests:** None.

- [x] Read `game/ui/screens/workshop_viewmodel.py` (873 lines)
- [x] Save to `findings/workshop_viewmodel_decomposition.md`

**Notes:**

---

### Task 2.9: Design `app.py` decomposition [Medium]
**File:** `findings/app_decomposition.md`
**Tests:** None.

- [x] Read `game/app.py` (849 lines)
- [x] Bootstrap / run-loop / screen management probably the three concerns
- [x] Save to `findings/app_decomposition.md`

**Notes:**

---

### Task 2.10: Design `strategy_window_manager.py` decomposition [Medium]
**File:** `findings/strategy_window_manager_decomposition.md`
**Tests:** None.

- [x] Read `game/ui/screens/strategy_window_manager.py` (817 lines)
- [x] Save to `findings/strategy_window_manager_decomposition.md`

**Notes:**

---

### Task 2.11: Cross-design review [Simple]
**File:** None — review step.
**Tests:** None.

- [x] Read all 10 design docs back-to-back
- [x] Look for overlap (does the protocols split affect the renderer split?)
- [x] Look for inconsistencies (one design uses Option A, similar file uses Option B — same reasons?)
- [x] If any design has unanswered questions or weak risk analysis, send back

**Notes:** Review report at `findings/_cross_design_review.md`. Verdict: **APPROVE WITH FIXES**. All 10 docs are template-complete; no resends. Three fixes identified:
1. **Applied** — `core_protocols_decomposition.md` updated to commit upfront to the `strategy_entities.py` + `strategy_domain.py` split (avoids landing at ~520 LOC).
2. **Phase 3 prerequisite** — small note in `docs/03_CONVENTIONS.md` about renderer subpackage naming convention (capture during whichever sub-phase lands first; flagged in handoff).
3. **Phase 3 prerequisite** — `test_run_details/details/validation.py` should import shared draw helpers from the test_lab `renderer/_draw_helpers.py` rather than re-implementing (capture during sub-phase 6).

Phase 3 sequencing recommendation (lowest risk → highest): protocols → command_handlers → workshop_viewmodel → strategy_session_facade → test_lab/renderer → test_run_details → strategy_renderer → strategy_window_manager → race_setup_screen → app.py (last; entry-point).

---

## Phase Completion Checklist
- [x] All 10 design docs exist in `findings/`
- [x] Each design has all template sections filled
- [x] Cross-design review complete
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3)
