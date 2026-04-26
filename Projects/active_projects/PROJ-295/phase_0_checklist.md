# Phase 0: User Decision Gate

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. All 6 decision questions in [decisions.md](decisions.md) must have user answers
> 2. Update plan.md phase table AND Current State

**Status:** Blocking — needs user input
**Objective:** Lock in three decisions that affect the whole plan: target Python version, drop-3.10 strategy, and timing.

---

## Tasks

### Task 0.1: Capture user answers to decision questions [Simple]
**File:** [decisions.md](decisions.md) (Phase 0 Decision Questions table at the bottom)
**Tests:** N/A — decision capture only

- [ ] Question 1: target version (3.11 / 3.12 / 3.13) → record answer
- [ ] Question 2: drop 3.10 entirely vs. multi-version → record answer
- [ ] Question 3: target completion date → record answer
- [ ] Question 4: pyaudio fallback acceptable → record answer
- [ ] Question 5: introduce `.venv` + `pyproject.toml` → record answer
- [ ] Question 6: contributor impact (likely solo) → record answer

**Notes:** [Filled with the user's actual answers verbatim]

---

### Task 0.2: Update plan based on answers [Simple]
**File:** [plan.md](plan.md), [phase_1_checklist.md](phase_1_checklist.md), [phase_2_checklist.md](phase_2_checklist.md)
**Tests:** N/A

- [ ] If user said NOT to introduce `.venv` / `pyproject.toml`, strike those steps from Phase 2 and Phase 3
- [ ] If user said to KEEP 3.10 multi-version compat, expand Phase 2 to include a 3.10 + target compat matrix (this materially increases scope — flag the change in the next stand-up if so)
- [ ] If user picked 3.13, add an explicit Phase 1 callout: "verify pyaudio + dearpygui wheels are published for 3.13"
- [ ] Update [plan.md](plan.md) Current State to "Phase 1 — wheel validation"

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All 6 decision questions answered
- [ ] Plan adjusted if any answer departs from the architect's recommendation
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Phase 1 — wheel validation"
