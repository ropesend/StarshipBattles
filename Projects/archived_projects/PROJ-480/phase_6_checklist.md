# Phase 6: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-480 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address Codex audit finding F1 (Task 5.14 wrongly marked done via subsume claim). See `findings/audit_verification.md`.

This is a single-task status-correction phase. The much larger ~100-task scope deferred at the mid-project stop remains deferred and is already enumerated in plan.md Current State.

---

## Tasks

### Task 6.1: Reclassify Task 5.14 from done to pending (F1) [Simple]
**File:** `Projects/active_projects/PROJ-480/phase_5_checklist.md`

- [x] Line 111 currently reads: `- [x] _(coordination note: addressed via Task 3.21 in PROJ-479 Phase 3 CAT-6 — split into tests/static_guards/ directory.)_`
- [x] Change to: `- [ ] _(coordination note: PROJ-480 originally expected Task 3.21 in PROJ-479 Phase 3 CAT-6 to split this into tests/static_guards/. That PROJ-479 task was NOT completed — it's in the NEEDS_REWORK list per PROJ-479/phase_3_checklist.md:156-162. Both the inspect.getsource() guard (lines 219-251) and the AST-parsing guard (lines 262-288) are still present in test_turn_engine_lazy_properties.py. Re-pending.)_`
- [x] Update Phase 5 task count if it tracks done/pending totals. (Phase 5 checklist does not maintain a numeric done/pending counter — no action needed.)
- [x] Verify: `grep -n "static_guards\|getsource\|ast.parse" tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` still shows both guards present.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row for Phase 6 to `Complete`
- [x] Update plan.md Current State Watchouts list — append: "Task 5.14 was wrongly marked done via PROJ-479 subsume claim; now correctly pending (Codex audit, Phase 6)."
