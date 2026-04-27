# Phase 4: Final verification + tooling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify end-to-end. Optionally land a small tooling helper to keep the convention enforced.

**Prerequisites:** Phase 3 complete — all 10 files decomposed.

---

## Tasks

### Task 4.1: Top-10 sweep [Simple]
**File:** None — verification.
**Tests:** Manual.

- [ ] `find game -name "*.py" -type f -exec wc -l {} + | sort -rn | head -20` — confirm none of the new top-20 files exceed 500 lines
- [ ] If any do, document why (could be legitimate — e.g., a file just added by a different project) — but flag for follow-up

**Notes:**

---

### Task 4.2: Full sharded suite [Simple]
**File:** None.
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded suite
- [ ] Confirm 15389+ passing (no regressions introduced by decompositions)

**Notes:**

---

### Task 4.3: Manual smoke (everything touched) [Medium]
**File:** Game runtime.
**Tests:** Manual.

- [ ] Launch the game
- [ ] Race setup screen (3.1)
- [ ] Strategy screen — every render layer (3.2, 3.10)
- [ ] Issue commands — every handler kind (3.5)
- [ ] Workshop screen (3.8)
- [ ] Combat Lab — open, run a scenario, view details (3.3, 3.6)
- [ ] Sub-windows on strategy screen (3.10)
- [ ] Confirm no console errors / import errors / silent UI breakage

**Notes:**

---

### Task 4.4: (Optional) Add `Tools/check_file_size.py` [Simple]
**File:** `Tools/check_file_size.py` (NEW)
**Tests:** Manual.

- [ ] Decide whether to add the tooling now or capture as follow-up. If now:
  - Write a small script: walks `game/`, fails (exit 1) if any production file >500 lines (excluding test files via path filter)
  - Add it to a recommended pre-push hook or CI step (don't auto-install — just document)
- [ ] Smoke: `python Tools/check_file_size.py` — should report zero violations

**Notes:** If skipping, capture as follow-up project (PROJ-3xx).

---

### Task 4.5: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** None.

- [ ] After user verification, add an entry under "Recently Archived":
  - `- **PROJ-309** — Top-10 File Decomposition + 500-LOC Convention (2026-MM-DD). All 4 phases complete. Decomposed 10 files (totalling ~10,000 lines) into modules each <500 LOC. CLAUDE.md "Code Quality" + docs/03_CONVENTIONS.md updated with the rule. [Optional: Tools/check_file_size.py landed.] Sharded suite: [N]/[N] passing.`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] No production file in `game/` exceeds 500 lines (or any exceptions are documented)
- [ ] Full sharded suite passing
- [ ] Manual smoke passes
- [ ] User verified
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — pending archive"
