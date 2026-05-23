# Phase 1: Critical content errors

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-467 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Correct the 1 verified CRITICAL content error in foundation docs (Python baseline in `AGENTS.md`) against current code, identified by audit `2026-05-20_073330_docs-audit`.

> **REVISION (2026-05-20, protocol 06):** Task 1.2 (`DEAD-PAT-legacy`, remove deleted-file pattern examples at `docs/02_PATTERNS.md:818-827`) was DROPPED. Dual independent+Codex review verified those lines are explicitly marked as removed historical shims ("(Removed PROJ-417/416/383)") inside the Re-Export Shim section — they are NOT live pattern examples. Editing them is churn, not accuracy work. See decisions.md.

---

## Tasks

### Task 1.1: AGENTS.md Python baseline [Simple]
**File:** `AGENTS.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Correct Python baseline at line 52: change `Python 3.14` to `Python 3.13+` (canonical per `pyproject.toml` `requires-python = ">=3.13"` and `docs/03_CONVENTIONS.md`)
- [x] Verify: `grep -n "3.14" AGENTS.md` returns no baseline-version claim
- [x] Verify: baseline now matches `pyproject.toml:4` (`>=3.13`)

### Task 1.2: ~~02_PATTERNS.md deleted-file pattern examples~~ [DROPPED]
**DROPPED on revision (2026-05-20).** Finding `DEAD-PAT-legacy` was a false/stale positive. The lines at `docs/02_PATTERNS.md:818-827` are inside the "Re-Export Shim" section and are explicitly annotated "(Removed PROJ-417)", "(Removed PROJ-416)", "(Removed PROJ-383)" — they document deleted shims as removed, NOT as live pattern examples. Deleting them would erase intentional historical-shim documentation. No edit made. See decisions.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_073330_docs-audit/`. See `findings/source_audit.md` for the link._
