# Phase 3: Add convention to CLAUDE.md / 05_ERROR_HANDLING.md

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-308 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Codify the convention so future broad excepts get justification comments without needing another cleanup project.

**Prerequisites:** Phase 2 complete — every site is narrow / justified / deleted.

---

## Tasks

### Task 3.1: Add the rule to CLAUDE.md "Long-Term Quality" [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual verification

CLAUDE.md "Long-Term Quality" already contains the line:
> Specific exceptions over broad catches

Make this stronger.

- [ ] Read the surrounding section in CLAUDE.md (search for "Specific exceptions over broad catches")
- [ ] Replace the bullet with a more concrete rule:
  ```
  - **Specific exceptions over broad catches.** When a broad catch is genuinely necessary (e.g., third-party callback dispatch, platform-dependent init, fire-and-forget event emission), it MUST carry an `# Intentional broad catch: <specific reason>` comment on the same line or the line above. A broad catch without a justification comment is a code-review failure.
  ```
- [ ] **Verification:** `grep -n "Intentional broad catch" CLAUDE.md` returns at least 1 hit

**Notes:**

---

### Task 3.2: Document in `docs/05_ERROR_HANDLING.md` [Simple]
**File:** `docs/05_ERROR_HANDLING.md`
**Tests:** Manual verification

- [ ] Read `docs/05_ERROR_HANDLING.md` to find the right section (likely a §"Exception Handling" or similar)
- [ ] Add a §"Broad Catches" subsection:
  ```markdown
  ## Broad Catches

  Prefer narrowed exception types. When a broad `except Exception:` is genuinely necessary, it MUST carry a justification comment.

  **Format:**

  ```python
  except Exception:  # Intentional broad catch: <specific reason>
  ```

  **Legitimate reasons:**
  - Third-party callback dispatch (handler may raise anything)
  - Platform-dependent init (Tkinter, audio, GPU — exception types vary by OS)
  - Defensive UI updates (a failed redraw shouldn't crash the session)
  - Telemetry / event emission (instrumentation must never break the host)

  **Not legitimate (don't write these):**
  - "general defensive code"
  - "third-party stuff"
  - any comment that doesn't say *what* failures are expected and *why* fire-and-forget is correct

  See PROJ-308 for the audit that established this convention.
  ```
- [ ] **Verification:** `grep -n "Broad Catches" docs/05_ERROR_HANDLING.md` returns 1 hit
- [ ] Bump the doc's `Last verified:` date (it will exist after PROJ-307 lands)

**Notes:**

---

### Task 3.3: Final verification [Simple]
**File:** None — verification step
**Tests:** None.

- [ ] Read CLAUDE.md "Long-Term Quality" and `docs/05_ERROR_HANDLING.md` Broad Catches section back-to-back. Do they say the same thing? Format consistent?
- [ ] If awkward, polish

**Notes:**

---

### Task 3.4: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** None.

- [ ] After user verification, add an entry under "Recently Archived":
  - `- **PROJ-308** — Broad Exception Handler Justifications (2026-MM-DD). All 3 phases complete. Triaged 24 broad-except sites: [N] narrowed, [N] justified, [N] deleted. CLAUDE.md "Long-Term Quality" + docs/05_ERROR_HANDLING.md updated with the comment requirement.`

**Notes:** Do this AFTER user verifies, not during implementation.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] CLAUDE.md mentions "Intentional broad catch"
- [ ] docs/05_ERROR_HANDLING.md has a Broad Catches section
- [ ] User verified
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — pending archive"
