# Phase 1: Establish 500-LOC convention in CLAUDE.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Get the 500-LOC ceiling rule into CLAUDE.md and `docs/03_CONVENTIONS.md` BEFORE the first decomposition. Reasons:
- Future contributors land on a documented standard
- The decompositions in Phase 3 are guided by the rule (no resulting module >500 LOC)
- Subagent reviews catch the rule when it's violated

---

## Tasks

### Task 1.1: Add the rule to CLAUDE.md "Code Quality" [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual verification

CLAUDE.md "Key Conventions" → "Code Quality" already has:
> Keep functions focused and small (<50 lines preferred)

Add a parallel rule for files.

- [ ] Read `CLAUDE.md` "Code Quality" section
- [ ] Add bullet: `- Keep production-source files under 500 lines. When a file approaches 500 LOC, that's a signal to split into single-responsibility sub-modules. Test files are exempt — long test files are often legitimate.`
- [ ] **Verification:** `grep -n "500 lines\|500 LOC" CLAUDE.md` returns at least 1 hit

**Notes:**

---

### Task 1.2: Add §File Size to docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** Manual verification

- [ ] Add a §"File Size" section:
  ```markdown
  ## File Size

  Production-source files under `game/` should remain below 500 lines. When a file crosses 500 LOC:

  1. **Diagnose:** Has the file accreted multiple responsibilities? Almost always yes once it crosses this threshold
  2. **Split:** Extract cohesive sub-modules. The split direction depends on the file — by render layer, by domain, by concern, etc.
  3. **Preserve API:** Use a re-export shim (the original module re-exports from the new sub-modules) when many callers exist; full caller migration when few

  **Test files are exempt.** Long test files are often acceptable.

  See PROJ-309 for the audit that established this rule.
  ```
- [ ] **Verification:** `grep -n "File Size" docs/03_CONVENTIONS.md` returns 1 hit
- [ ] Bump the `Last verified:` date (set by PROJ-307)

**Notes:**

---

### Task 1.3: Verify the convention reads correctly [Simple]
**File:** None — review step
**Tests:** None.

- [ ] Read CLAUDE.md "Code Quality" + `docs/03_CONVENTIONS.md` §File Size — consistent? Helpful?

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] CLAUDE.md mentions 500-LOC rule
- [ ] `docs/03_CONVENTIONS.md` has §File Size
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2)
