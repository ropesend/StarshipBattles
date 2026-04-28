# Phase 2: R6 — Architecture docs service-count fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-318 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update the 3 stale architecture docs to reflect the
actual ApplicationContext service count (10, not 9) and document the
new `ImageProvider`. `docs/01_ARCHITECTURE.md` was correctly updated
by PROJ-314 — verify and don't double-update.

---

## Tasks

### Task 2.1: Update docs/02_PATTERNS.md [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** None (doc change). Run `pytest tests/ --testmon -n 12` for safety.

- [ ] Read the Singleton-Free DI / ApplicationContext section (around lines 60-95)
- [ ] In the services-managed table, add a row for `ImageProvider` with file location `game/ui/services/image/provider.py` and layer `UI`
- [ ] Update the count line "Services Managed (9 total)" → "Services Managed (10 total)"
- [ ] Update the code-example comment `# all 9 services` → `# all 10 services`
- [ ] Bump `Last verified:` date at the top of the file to today (2026-04-28)
- [ ] Verify: `grep -n "9 services\|all 9 " docs/02_PATTERNS.md` returns no matches

**Notes:**

### Task 2.2: Update docs/README.md [Simple]
**File:** `docs/README.md`
**Tests:** None.

- [ ] Find the line that says "ApplicationContext manages 9 services" (around line 4)
- [ ] Change to "ApplicationContext manages 10 services" (or similar phrasing matching the existing prose)
- [ ] Bump `Last verified:` date if the file has one
- [ ] Verify: `grep -n "9 services" docs/README.md` returns no matches

**Notes:**

### Task 2.3: Update AGENTS.md [Simple]
**File:** `AGENTS.md` (repo root)
**Tests:** None.

- [ ] Find the line that says "ApplicationContext manages 9 services" (around line 51)
- [ ] Change to "ApplicationContext manages 10 services"
- [ ] Verify: `grep -n "9 services" AGENTS.md` returns no matches

**Notes:**

### Task 2.4: Verify docs/01_ARCHITECTURE.md does NOT need updating [Simple]
**File:** `docs/01_ARCHITECTURE.md` (read-only)
**Tests:** None.

- [ ] Read line 3 — should already say `Last verified: 2026-04-28 — PROJ-314 added game/ui/services/image/...`
- [ ] Confirm `image_provider` is mentioned in the package directory map / services section
- [ ] If both are true: leave the file alone; if either is false: add a sub-task here to fix it

**Notes:**

### Task 2.5: Run full test suite [Simple]
**File:** None.
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Confirm 15959 / 15959 still passing (no doc-only test impact)
- [ ] If any pre-existing failures appear, capture them in `decisions.md` as "pre-existing failures, not caused by PROJ-318" with the test names

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] No `9 services` references remain in `docs/`, `AGENTS.md`, or `README.md`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
- [ ] Commit: `docs(PROJ-318 Phase 2): bump ApplicationContext service count 9→10 + ImageProvider`
