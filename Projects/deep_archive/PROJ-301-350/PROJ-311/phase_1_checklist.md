# Phase 1: Establish convention in CLAUDE.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-311 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Document the requirement that every new public function carries a return annotation. Get this in place BEFORE backfill starts so the rule is enforceable.

---

## Tasks

### Task 1.1: Update CLAUDE.md "Code Quality" [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual verification

CLAUDE.md "Code Quality" already says "Use type hints for function signatures." Strengthen this for return types specifically.

- [x] Read CLAUDE.md "Key Conventions" → "Code Quality" section
- [x] Replace the existing line with:
  ```
  - **Return-type annotations are required on every public function/method.** Use modern syntax (PEP 604 unions like `int | None`, native generics like `list[int]`). `__init__` and other dunders are exempt (PEP 484). Functions with no `return` statement annotate `-> None` explicitly.
  - Use type hints for function parameters where they aid clarity (parameter coverage is not yet enforced project-wide; return coverage is).
  ```
- [x] **Verification:** `grep -n "Return-type annotations" CLAUDE.md` returns 1 hit

**Notes:** Replacement landed at CLAUDE.md line 241. Single grep hit confirmed.

---

### Task 1.2: Add §Type Annotations to docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** Manual verification

- [x] Add a §"Type Annotations" section:
  ```markdown
  ## Type Annotations

  ### Return types (required)
  Every public function/method must carry a return-type annotation.

  - **Modern syntax only:** `int | None`, `list[int]`, `dict[str, T]` — not `Optional[int]`/`List[int]`/`Dict[str, T]`. Python 3.13+ baseline (PROJ-295) means we don't need legacy syntax
  - **No `return` statement:** annotate `-> None` explicitly
  - **`__init__` and other dunders:** exempt per PEP 484
  - **Forward references:** add `from __future__ import annotations` at the top of the file if needed (or use string literals in the annotation)
  - **Don't lie:** if the function returns `Any`, annotate `Any`. Don't make up a more specific type the code doesn't enforce

  ### Parameter types (encouraged)
  Parameter annotations are encouraged but not project-wide-mandatory yet. Add them where they improve clarity.

  ### Generics and protocols
  Prefer `Protocol` (from `game.core.protocols.*`) over concrete types when the function only needs duck-typed surface. Use `TypeVar` for generic helpers.

  See PROJ-311 for the audit that established the return-type requirement.
  ```
- [x] **Verification:** `grep -n "Type Annotations" docs/03_CONVENTIONS.md` returns 1 hit
- [x] Bump the doc's `Last verified:` date (set by PROJ-307)

**Notes:** Added as §8 (renumbered the existing Documentation Freshness section to §9). Last verified bumped to 2026-04-27 with summary "PROJ-311 added §Type Annotations".

---

### Task 1.3: Verify the convention reads correctly [Simple]
**File:** None — review step.
**Tests:** None.

- [x] Read CLAUDE.md and `docs/03_CONVENTIONS.md` Type Annotations section back-to-back
- [x] Polish if awkward

**Notes:** Reads cleanly. CLAUDE.md is the short-form rule; docs/03 is the long-form guidance. Both reference PROJ-311 for traceability.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] CLAUDE.md mentions return-type requirement
- [x] `docs/03_CONVENTIONS.md` has §Type Annotations
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2)
