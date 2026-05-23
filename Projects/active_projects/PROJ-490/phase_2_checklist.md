# Phase 2: Audit remediation (Codex consult 2026-05-23)

**Status:** Complete
**Objective:** Tighten `mine_group_service.py` fallback comment to satisfy LEG-02-002's "dated TODO" requirement and reflect what the code actually does.

---

## Tasks

### Task 2.1: Add dated TODO + accurate rationale to mine_group_service fallback
**File:** `game/strategy/services/mine_group_service.py:128-130`

- [x] Rewrote the comment block to:
  - Keep the "Prefer typed ``deployed_groups``" rationale.
  - Replace the imprecise "older test stubs that have not migrated" wording with "empire-shaped fixtures that omit ``deployed_groups`` (e.g. minimal Mocks used in older tests)" — accurate to what the code actually catches.
  - Add `TODO 2026-05-23: audit + drop the ``fleets`` arm once all empire fixtures expose ``deployed_groups``.` — satisfies plan.md's "Add a dated TODO + PROJ reference rather than removing" guidance.
- [x] `pytest tests/unit/strategy/services/test_mine_group_service.py` 10 passed

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table to include Phase 2 as Complete

_Source: Codex audit at `AgentCoordination/Scratchpad/Consult/20260523T124002Z_audit-PROJ-490/response.md`. Verification table at `findings/audit_verification.md`._
