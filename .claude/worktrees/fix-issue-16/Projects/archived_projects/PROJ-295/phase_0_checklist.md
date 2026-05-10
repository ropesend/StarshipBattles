# Phase 0: User Decision Gate

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. All 6 decision questions in [decisions.md](decisions.md) must have user answers
> 2. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Lock in three decisions that affect the whole plan: target Python version, drop-3.10 strategy, and timing.

---

## Tasks

### Task 0.1: Capture user answers to decision questions [Simple]
**File:** [decisions.md](decisions.md) (Phase 0 Decision Questions table at the bottom)
**Tests:** N/A — decision capture only

- [x] Question 1: target version (3.11 / 3.12 / 3.13) → record answer
- [x] Question 2: drop 3.10 entirely vs. multi-version → record answer
- [x] Question 3: target completion date → record answer
- [x] Question 4: pyaudio fallback acceptable → record answer
- [x] Question 5: introduce `.venv` + `pyproject.toml` → record answer
- [x] Question 6: contributor impact (likely solo) → record answer

**Notes:** All 6 resolved on 2026-04-26. User selected Python 3.13, drop 3.10, today, MIGRATE pyaudio (not drop), .venv + pyproject.toml yes, solo. Verified PyPI directly that all C-ext deps have 3.13 wheels — sounddevice, numpy, scipy, Pillow, opencv-python (cp37-abi3), dearpygui, watchdog, pygame-ce, pygame_gui, google-cloud-speech all good. See decisions.md.

---

### Task 0.2: Update plan based on answers [Simple]
**File:** [plan.md](plan.md), [phase_1_checklist.md](phase_1_checklist.md), [phase_2_checklist.md](phase_2_checklist.md)
**Tests:** N/A

- [x] If user said NOT to introduce `.venv` / `pyproject.toml`, strike those steps from Phase 2 and Phase 3
- [x] If user said to KEEP 3.10 multi-version compat, expand Phase 2 to include a 3.10 + target compat matrix (this materially increases scope — flag the change in the next stand-up if so)
- [x] If user picked 3.13, add an explicit Phase 1 callout: "verify pyaudio + dearpygui wheels are published for 3.13"
- [x] Update [plan.md](plan.md) Current State to "Phase 1 — wheel validation"

**Notes:** Adjusted plan: 4→6 phases. Inserted new Phase 1 (pyaudio→sounddevice migration) as the 3.13 unblocker. Original Phase 1 (wheel dry-run) became Phase 2; original Phase 2 (live install) became Phase 3; etc. plan.md and decisions.md updated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All 6 decision questions answered
- [x] Plan adjusted if any answer departs from the architect's recommendation
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Phase 1 — pyaudio migration"
