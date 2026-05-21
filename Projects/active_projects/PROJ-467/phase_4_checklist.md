# Phase 4: Codex-audit remediation [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-467 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Revision Reason:** Added after the one-round Codex audit (`AgentCoordination/Scratchpad/Consult/proj467_audit/`). Codex returned 4 findings; all 4 were independently VERIFIED against live code/docs (0 rejected). They are incomplete-cleanup gaps in files Phase 1-3 already touched, not new regressions.
**Objective:** Close the 4 verified Codex findings.

---

## Tasks

### Task 4.1: Bump `Last verified:` stamps on the three touched `docs/0N_*.md` files [Simple]
**File:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
**Verification:** header line shows 2026-05-20 with a PROJ-467 summary.
**Codex finding:** (a)(1) — Phase 1-3 edited these files but left the `Last verified:` header at the pre-PROJ-467 date (`01_ARCHITECTURE.md:3`=2026-05-18, `02_PATTERNS.md:3`=2026-05-18, `03_CONVENTIONS.md:3`=2026-05-17); the per-file checklist verification text required bumping it.

- [x] Bump `docs/01_ARCHITECTURE.md` Last verified to 2026-05-20 with PROJ-467 note (galaxy_protocols prefix + pathfinding layer move)
- [x] Bump `docs/02_PATTERNS.md` Last verified to 2026-05-20 with PROJ-467 note (commands/ package path + Registry value-kinds wording)
- [x] Bump `docs/03_CONVENTIONS.md` Last verified to 2026-05-20 with PROJ-467 note (pathfinding service path + hardcoded-checkout-path removal)

### Task 4.2: Finish the retired-Protocol-08 cleanup in WORKER_TEMPLATE.md [Simple]
**File:** `Projects/protocols/WORKER_TEMPLATE.md`
**Verification:** no live instruction points workers at retired Protocol 08; audit cap matches Protocol 04.
**Codex findings:** (a)(2)/(c)(1) — line 63 "Follow audit workflow (Protocol 08)" still points at the retired protocol (Phase 3 fixed only line 37); (c)(2) — line 64/67 say "Maximum 5 audit cycles" but `04_audit_project.md:32-33` caps at 3 cycles then escalate.

- [x] Line 63: change "Follow audit workflow (Protocol 08)" to point at the active audit protocol (Protocol 04, `04_audit_project.md`)
- [x] Line 64 / line 67: change "Maximum 5 audit cycles" / "After 5 cycles" to "3 cycles" to match `04_audit_project.md:32-33`
- [x] Verify: no remaining live (non-historical-note) "Protocol 08" instruction in the file

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source: one-round Codex audit, `AgentCoordination/Scratchpad/Consult/proj467_audit/audit.md.invalid-output-*.txt`._
