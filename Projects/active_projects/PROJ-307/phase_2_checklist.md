# Phase 2: Establish convention in CLAUDE.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-307 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make the timestamp convention enforceable by adding it to CLAUDE.md (Rule 2: Documentation) and `docs/03_CONVENTIONS.md`. Future doc edits MUST update the timestamp.

**Prerequisites:** Phase 1 complete — every doc has a baseline timestamp.

---

## Tasks

### Task 2.1: Add timestamp rule to CLAUDE.md Rule 2 [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual verification

CLAUDE.md "Rule 2: Documentation — CHECK Before, UPDATE After" already has a "DO NOT" list and a "DO" list. Add the timestamp requirement.

- [ ] Read CLAUDE.md Rule 2 section (currently spans lines ~75-105 approximately — verify on read)
- [ ] In the "DO" list, add: `- Update the **Last verified:** date at the top of any doc you verify or substantively edit. Format: \`> **Last verified:** YYYY-MM-DD — <one-sentence summary>\`. The date represents an intentional accuracy check, not a cosmetic edit.`
- [ ] In the "DO NOT" list, add: `- DO NOT bump the **Last verified:** date for cosmetic edits (typos, formatting). Bump only when you've actually re-read the file and confirmed it matches current code.`
- [ ] **Verification:** `grep -n "Last verified" CLAUDE.md` returns ≥ 2 hits (the DO and DO NOT lines)

**Notes:**

---

### Task 2.2: Add Documentation Freshness section to docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** Manual verification

- [ ] Read `docs/03_CONVENTIONS.md` to find the right section to add this under (likely a top-level §"Documentation Conventions" or similar)
- [ ] Add a §"Documentation Freshness" subsection with:
  ```markdown
  ## Documentation Freshness

  Every file under `docs/` must carry a verification timestamp directly below its H1:

  > **Last verified:** YYYY-MM-DD — <one-sentence summary of what was verified>

  Rules:
  - **Date format:** `YYYY-MM-DD` (ISO 8601)
  - **"Verified" means:** the maintainer read the file and confirmed it matches current code/behavior — not that they made a cosmetic edit
  - **Bump the date when:** you substantively edit the doc, or you re-read it and confirm current accuracy
  - **Don't bump:** for typo/formatting fixes that don't reflect any verification work

  See PROJ-307 for the backfill that established this convention.
  ```
- [ ] **Verification:** `grep -n "Documentation Freshness" docs/03_CONVENTIONS.md` returns 1 hit
- [ ] Bump the doc's own `Last verified:` date now (you just edited it)

**Notes:**

---

### Task 2.3: Verify the convention reads correctly [Simple]
**File:** None — review step
**Tests:** None.

- [ ] Read CLAUDE.md Rule 2 end-to-end — does the timestamp rule fit naturally?
- [ ] Read `docs/03_CONVENTIONS.md` Documentation Freshness section — clear?
- [ ] If awkward, polish wording

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] CLAUDE.md mentions "Last verified" in both DO and DO NOT lists
- [ ] `docs/03_CONVENTIONS.md` has a Documentation Freshness section
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — pending archive"
