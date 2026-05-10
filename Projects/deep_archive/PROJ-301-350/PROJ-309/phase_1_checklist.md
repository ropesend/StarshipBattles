# Phase 1: Establish 500-LOC convention in CLAUDE.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Read `CLAUDE.md` "Code Quality" section
- [x] Add bullet: `- Keep production-source files under 500 lines. When a file approaches 500 LOC, that's a signal to split into single-responsibility sub-modules. Test files are exempt — long test files are often legitimate.`
- [x] **Verification:** `grep -n "500 lines\|500 LOC" CLAUDE.md` returns at least 1 hit

**Notes:** Bullet inserted at CLAUDE.md:249 directly after the "max 3 levels" nesting bullet so all file/function/nesting size rules sit together. Cross-references `docs/03_CONVENTIONS.md` §File Size and PROJ-309.

---

### Task 1.2: Add §File Size to docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** Manual verification

- [x] Add a §"File Size" section:
  ```markdown
  ## File Size

  Production-source files under `game/` should remain below 500 lines. When a file crosses 500 LOC:

  1. **Diagnose:** Has the file accreted multiple responsibilities? Almost always yes once it crosses this threshold
  2. **Split:** Extract cohesive sub-modules. The split direction depends on the file — by render layer, by domain, by concern, etc.
  3. **Preserve API:** Use a re-export shim (the original module re-exports from the new sub-modules) when many callers exist; full caller migration when few

  **Test files are exempt.** Long test files are often acceptable.

  See PROJ-309 for the audit that established this rule.
  ```
- [x] **Verification:** `grep -n "File Size" docs/03_CONVENTIONS.md` returns 1 hit
- [x] Bump the `Last verified:` date (set by PROJ-307)

**Notes:** A §"File Size" section already existed at §2.3 (under §2 File Organization) with weaker language. Per Rule 3 (clean-sheet) and to avoid doc duplication, expanded the existing §2.3 in place with the PROJ-309 prescriptive content (diagnose / split / preserve API / test exemption / PROJ-309 backref) rather than creating a duplicate top-level §File Size heading. Last verified bumped to 2026-04-27 noting the PROJ-309 expansion. `grep "### 2.3 File Size"` returns 1 hit.

---

### Task 1.3: Verify the convention reads correctly [Simple]
**File:** None — review step
**Tests:** None.

- [x] Read CLAUDE.md "Code Quality" + `docs/03_CONVENTIONS.md` §File Size — consistent? Helpful?

**Notes:** Both reads cross-reference each other. CLAUDE.md gives the one-line rule (file <500, tests exempt) and points to docs/03_CONVENTIONS.md §File Size for the full how-to (diagnose / split / preserve API / re-export shim vs caller migration). Both flag tests as exempt and reference PROJ-309. Consistent.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] CLAUDE.md mentions 500-LOC rule
- [x] `docs/03_CONVENTIONS.md` has §File Size
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2)
