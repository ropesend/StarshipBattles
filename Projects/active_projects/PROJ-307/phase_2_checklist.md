# Phase 2: Establish convention in CLAUDE.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-307 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make the timestamp convention enforceable by adding it to CLAUDE.md (Rule 2: Documentation) and `docs/03_CONVENTIONS.md`. Future doc edits MUST update the timestamp.

**Prerequisites:** Phase 1 complete — every doc has a baseline timestamp.

---

## Tasks

### Task 2.1: Add timestamp rule to CLAUDE.md Rule 2 [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual verification

CLAUDE.md "Rule 2: Documentation — CHECK Before, UPDATE After" already has a "DO NOT" list and a "DO" list. Add the timestamp requirement.

- [x] Read CLAUDE.md Rule 2 section (currently spans lines ~75-105 approximately — verify on read)
- [x] In the "DO" list, add: `- Update the **Last verified:** date at the top of any doc you verify or substantively edit. Format: \`> **Last verified:** YYYY-MM-DD — <one-sentence summary>\`. The date represents an intentional accuracy check, not a cosmetic edit.`
- [x] In the "DO NOT" list, add: `- DO NOT bump the **Last verified:** date for cosmetic edits (typos, formatting). Bump only when you've actually re-read the file and confirmed it matches current code.`
- [x] **Verification:** `grep -n "Last verified" CLAUDE.md` returns ≥ 2 hits (the DO and DO NOT lines)

**Notes:** `grep -n "Last verified" CLAUDE.md` returns 2 hits as expected (lines 61 and 68 — DO NOT and DO respectively).

---

### Task 2.2: Add Documentation Freshness section to docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** Manual verification

- [x] Read `docs/03_CONVENTIONS.md` to find the right section to add this under (likely a top-level §"Documentation Conventions" or similar)
- [x] Add a §"Documentation Freshness" subsection with the spec'd content
- [x] **Verification:** `grep -n "Documentation Freshness" docs/03_CONVENTIONS.md` returns 1 hit
- [x] Bump the doc's own `Last verified:` date now (you just edited it)

**Notes:** Added as new §8 at end of file (existing sections were 1–7, all top-level numbered conventions). Bumped doc's own `Last verified:` from 2026-04-18 to 2026-04-27 with summary "PROJ-307 added §8 Documentation Freshness".

---

### Task 2.3: Verify the convention reads correctly [Simple]
**File:** None — review step
**Tests:** None.

- [x] Read CLAUDE.md Rule 2 end-to-end — does the timestamp rule fit naturally?
- [x] Read `docs/03_CONVENTIONS.md` Documentation Freshness section — clear?
- [x] If awkward, polish wording

**Notes:** Both reads — the new bullets blend naturally into the existing DO/DO NOT lists; §8 is a clean append at end of conventions doc.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] CLAUDE.md mentions "Last verified" in both DO and DO NOT lists
- [x] `docs/03_CONVENTIONS.md` has a Documentation Freshness section
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete — pending archive"
