# Phase 2: Apply per-site action

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-308 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Execute the action chosen in Phase 1 for each site: narrow the type, add a justification comment, or delete the handler.

**Prerequisites:** Phase 1 triage complete; `findings/triage.md` populated.

---

## Tasks

### Task 2.1: Apply NARROW actions [Simple]
**File:** Per Phase 1 triage (Choice 1 sites)
**Tests:** Targeted tests for each modified file

For each site marked **narrow** in `findings/triage.md`:
- [ ] Open the file at the line
- [ ] Replace `except Exception:` with the specific exception types from the triage decision (e.g., `except (json.JSONDecodeError, TypeError):`)
- [ ] If the new types require imports, add them at the top of the file
- [ ] Run the file's targeted test suite
- [ ] Mark the row in `findings/triage.md` as DONE

**Notes:**

---

### Task 2.2: Apply JUSTIFY actions [Simple]
**File:** Per Phase 1 triage (Choice 2 sites)
**Tests:** No code-behavior change — just verify the comment is in place

For each site marked **justify** in `findings/triage.md`:
- [ ] Open the file at the line
- [ ] Replace `except Exception:` with `except Exception:  # Intentional broad catch: <reason from triage>`
- [ ] (Or, if the line is already long, place the comment on the line immediately above)
- [ ] Mark the row in `findings/triage.md` as DONE

**Notes:** This task is mostly mechanical — the thinking happened in Phase 1 — but resist the urge to rubber-stamp. If a triage entry's reason looks weak, send it back to Phase 1.

---

### Task 2.3: Apply DELETE actions [Simple]
**File:** Per Phase 1 triage (Choice 3 sites)
**Tests:** Full targeted suite for each affected module — these changes can have downstream effects

For each site marked **delete** in `findings/triage.md`:
- [ ] Open the file at the line
- [ ] Remove the `try` / `except Exception:` wrapper, keeping the inner code
- [ ] If the except block had cleanup or logging, decide carefully whether that needs to live elsewhere
- [ ] Run the file's targeted test suite (this is the riskiest action — pay attention to test failures)
- [ ] If tests fail in a way that proves the catch was load-bearing, revert to Choice 2 (justify) and update the triage doc

**Notes:**

---

### Task 2.4: Final sweep [Simple]
**File:** All of `game/`
**Tests:** Full sharded suite

- [ ] `grep -rn "except Exception:" game/ | grep -v "Intentional"` — every remaining hit MUST have an "Intentional" comment within ±1 line
- [ ] Use a small Python AST script to verify: walk `game/`, for every `except Exception:` node, check that the line itself OR the preceding line contains the substring "Intentional"
- [ ] Run full sharded suite (`python Tools/test_sharded/test_sharded.py`) — confirm 15389+ baseline
- [ ] Investigate any new failures; revert problematic changes if needed

**Notes:**

---

## Phase Completion Checklist
- [ ] All triage actions applied
- [ ] `findings/triage.md` rows all marked DONE
- [ ] Final sweep returns zero un-justified broad excepts in `game/`
- [ ] Full sharded suite at 15389+
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3)
