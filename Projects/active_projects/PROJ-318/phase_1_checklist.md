# Phase 1: R1 — Audit-gate hygiene (PROJ-314 phase checklists)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-318 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make `validate_audit_ready.py PROJ-314` exit 0 by
creating the 5 missing phase-checklist files retroactively
documenting each PROJ-314 commit, and flipping every existing
checklist's `Status:` and checkboxes to `Complete` / checked. PROJ-314
shipped on main; this phase brings its tracking artifacts into
alignment.

---

## Tasks

### Task 1.1: Update PROJ-314 Phase 1 checklist [Simple]
**File:** `Projects/active_projects/PROJ-314/phase_1_checklist.md`
**Tests:** Visual review — no automated test for tracking files.

- [ ] Change `**Status:** Not Started` to `**Status:** Complete` at line 8
- [ ] Check all 34 task boxes (`- [ ]` → `- [x]`) across Tasks 1.1 through 1.5
- [ ] In each task's `**Notes:**` line, add a one-line attribution: `Shipped via commit 0ec916cae (PROJ-314 Phase 1).`
- [ ] At the bottom of the Phase Completion Checklist section, check all 4 boxes
- [ ] Verify: `git log -1 0ec916cae` shows the expected commit summary

**Notes:**

### Task 1.2: Create PROJ-314 Phase 2 checklist [Simple]
**File:** `Projects/active_projects/PROJ-314/phase_2_checklist.md` (NEW)
**Tests:** Visual review.

The file should mirror the shape of `phase_1_checklist.md`, but
**with status already `Complete`** since the work shipped via
commit `62a7c05af`.

- [ ] Create file with header `# Phase 2: New game/ui/services/image/ service`
- [ ] Add `**Status:** Complete` and `**Objective:** Create the new image-generation service mirroring game/services/llm/.`
- [ ] Add a "Tasks" section listing the 7 service files and 5 test files PROJ-314 actually shipped (cross-reference `Projects/active_projects/PROJ-314/manifest.md`):
  - Task 2.1: `provider.py`, `types.py`, `openai_provider.py`, `null_provider.py`, `factory.py`, `defaults.py`, `background.py` — all checkboxes pre-checked
  - Task 2.2: 5 test files in `tests/unit/ui/services/image/` — all checkboxes pre-checked
  - Task 2.3: `game/context.py` wiring of `image_provider` — pre-checked
  - Task 2.4: `tests/conftest.py` autouse fixture — pre-checked
- [ ] Add `**Notes:** Shipped via commit 62a7c05af.` to each task
- [ ] Phase Completion Checklist at the bottom — all boxes checked

**Notes:**

### Task 1.3: Create PROJ-314 Phase 3 checklist [Simple]
**File:** `Projects/active_projects/PROJ-314/phase_3_checklist.md` (NEW)
**Tests:** Visual review.

Document Phase 3 (Loader rewrite) work that shipped via commit
`48de788da`. Same pre-completed shape as Task 1.2.

- [ ] Create file with header `# Phase 3: Loader rewrite`
- [ ] `**Status:** Complete`
- [ ] Tasks listing the actual changes:
  - 3.1: `game/ui/assets/ship_theme_manager.py` rewrite (new `assets:` schema, deleted `_ship_class_to_portrait_name()`, unified `get_portrait_image()` return contract, added `_validate_image_size()`)
  - 3.2: Updated `tests/unit/ui/test_ship_theme_logic.py` and `test_theme_discovery.py` for new schema; deleted `TestShipClassToPortraitName`
  - 3.3: New contract tests for the new schema
- [ ] All boxes checked; `**Notes:** Shipped via commit 48de788da.`

**Notes:**

### Task 1.4: Create PROJ-314 Phase 4 checklist [Simple]
**File:** `Projects/active_projects/PROJ-314/phase_4_checklist.md` (NEW)
**Tests:** Visual review.

Document Phase 4 (regenerate tool + asset prep) work that shipped
via commit `d000acc5a`.

- [ ] Header `# Phase 4: Image generation tool + asset prep`
- [ ] Status `Complete`
- [ ] Tasks: CLI tool creation, audit script, prompt templates, 151 .jpg→.png conversions, filename normalization across 8 themes, Atlantians typo fix, Thoraliens path mismatch fix
- [ ] All boxes checked; `**Notes:** Shipped via commit d000acc5a. AI portrait generation deferred — user runs CLI with their OPENAI_API_KEY.`

**Notes:**

### Task 1.5: Create PROJ-314 Phase 5 checklist [Simple]
**File:** `Projects/active_projects/PROJ-314/phase_5_checklist.md` (NEW)
**Tests:** Visual review.

Document Phase 5 (atomic schema migration) work that shipped via
commit `0bbf9c36d`.

- [ ] Header `# Phase 5: Atomic schema migration`
- [ ] Status `Complete`
- [ ] Tasks: 9 theme.json files migrated to new schema; 4 hardcoded-convention sites updated; new integration smoke test added
- [ ] All boxes checked; `**Notes:** Shipped via commit 0bbf9c36d.`

**Notes:**

### Task 1.6: Create PROJ-314 Phase 6 checklist [Simple]
**File:** `Projects/active_projects/PROJ-314/phase_6_checklist.md` (NEW)
**Tests:** Visual review.

Document Phase 6 (cleanup + docs) work that shipped via commit
`e26f00f74`.

- [ ] Header `# Phase 6: Cleanup + documentation`
- [ ] Status `Complete`
- [ ] Tasks: legacy .jpg deletions, `docs/01_ARCHITECTURE.md` updated, `docs/03_CONVENTIONS.md` §11 added, `Last verified:` dates bumped
- [ ] All boxes checked; `**Notes:** Shipped via commit e26f00f74. Note: docs/02_PATTERNS.md, docs/README.md, AGENTS.md were not updated; this is addressed by PROJ-318 Phase 2.`

**Notes:**

### Task 1.7: Verify the audit gate now passes [Simple]
**File:** None (verification only).
**Tests:** `python Projects/scripts/validate_audit_ready.py PROJ-314`

- [ ] Run the script with the venv Python (`.venv/Scripts/python.exe`)
- [ ] Capture the full output
- [ ] Confirm exit code 0 and zero errors
- [ ] If any failures remain, iterate on the previous tasks

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-314` exits 0
- [ ] PROJ-314 plan.md Current State updated to acknowledge PROJ-318 closeout
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Commit: `chore(PROJ-318 Phase 1): retroactive PROJ-314 phase checklists + audit-gate fix`
