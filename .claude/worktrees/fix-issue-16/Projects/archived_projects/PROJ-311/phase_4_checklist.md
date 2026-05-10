# Phase 4: CI enforcement (optional)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-311 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Land a coverage gate that prevents regression. This phase is OPTIONAL — the convention + post-backfill state achieve most of the value. CI enforcement is the belt-and-suspenders.

**Prerequisites:** Phase 3 complete — coverage ≥ 95% in `game/`.

---

## Decision

Two options:
- **Option A — Skip Phase 4** (defer to a follow-up project): the convention is documented, post-backfill coverage is high, future violations get caught in code review. Lower friction but slower-acting protection
- **Option B — Land a coverage gate now**: the audit script becomes a CI step that fails when coverage drops. Stronger protection but more setup

User decides at start of Phase 4. Default recommendation: **Option B** if it can be wired in <2 hours; otherwise Option A.

---

## Tasks (only if Option B)

### Task 4.1: Promote `annotation_audit.py` to a Tools script [Simple]
**File:** `Tools/check_annotation_coverage.py` (NEW)
**Tests:** Manual.

- [ ] Move/copy `Projects/active_projects/PROJ-311/findings/annotation_audit.py` to `Tools/check_annotation_coverage.py`
- [ ] Add a `--threshold` CLI flag (default 95)
- [ ] Exit with status 1 if overall coverage < threshold; 0 otherwise
- [ ] Print which subsystem dragged the average down

**Notes:**

---

### Task 4.2: Wire into a recommended CI step [Simple]
**File:** `.github/workflows/*.yml` or `Tools/test_sharded/test_sharded.py` (depending on existing CI shape)
**Tests:** Manual.

- [ ] Identify the project's CI pattern (workflow file or local script)
- [ ] Add a step that runs `python Tools/check_annotation_coverage.py --threshold 95`
- [ ] Test by intentionally removing one annotation and confirming the check fails

**Notes:**

---

### Task 4.3: Document in CLAUDE.md [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual.

- [ ] Add a one-liner under "Code Quality" mentioning the annotation-coverage check
- [ ] If applicable, link to the script

**Notes:**

---

### Task 4.4: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** None.

- [ ] After user verification, add an entry under "Recently Archived":
  - `- **PROJ-311** — Return Type Annotation Backfill + Convention (2026-MM-DD). All [3 or 4] phases complete. Post-backfill return-type coverage in game/: [N]%. CLAUDE.md "Code Quality" + docs/03_CONVENTIONS.md updated with the annotation requirement. [Optional: Tools/check_annotation_coverage.py + CI gate landed.] Sharded suite: [N]/[N] passing.`

**Notes:**

---

## Phase Completion Checklist
- [ ] If Option A: phase explicitly skipped; follow-up project tracked
- [ ] If Option B: all tasks above complete; coverage gate active
- [ ] Update status at top of this file to `Complete` (or `Skipped — see decisions.md`)
- [ ] Update plan.md phase table row to `Complete` or `Skipped`
- [ ] Update plan.md Current State to "Complete — pending archive"
