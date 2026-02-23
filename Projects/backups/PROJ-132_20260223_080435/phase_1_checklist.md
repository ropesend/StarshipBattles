# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-132 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Foundation module (3 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 1.1: ADR-FND-001 - Research UI layer imports from game.ui [Medium]
**File:** `game/research/ui/research_scene.py`
**Tests:** `pytest tests/unit/research/test_research_scene_di.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Fixed by adding optional `camera` parameter to `ResearchTreeScene.__init__`. Camera import moved to `_create_default_camera()` factory function (late import). Module-level import removed. Tests added in `test_research_scene_di.py`. Existing tests updated to patch `_create_default_camera` instead of `Camera`.

### Task 1.2: ADR-FND-002 - IControllable interface exceeds god clas [Complex]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Accepted as-is. Interface is 477 lines but well-organized with 5 clear sections (Position/Movement Read, Movement Write, Identity/State, Combat, Formation). All 36 methods are cohesive - they all relate to controlling a ship. Splitting would create coupling issues where controllers need multiple interfaces. Documented in decisions.md.

### Task 1.3: ADR-FND-003 - protocols.py exceeds 500 lines [Simple]
**File:** `game/core/protocols.py:1-547`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Accepted as-is. File is 547 lines (marginal 47-line overage). Contains cohesive set of Protocol definitions for cross-layer type safety. Splitting would fragment protocol discovery. Well-organized with section comments. Documented in decisions.md.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
