# Phase 4: CAT-7 Sleep/Latency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-322 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace `time.sleep()` with deterministic waits or remove latency-based assertions for the 9 verified CAT-7 cases.

---

## Tasks

### Task 4.1: Document data-contract coupling for pipeline-unification tests [Simple]
**File:** `tests/integration/data/test_pipeline_unification.py`
**Tests:** `pytest tests/integration/data/test_pipeline_unification.py`

- [ ] S11-CAT7-001: keep the 4 data-driven tests (lines 13-92) - acceptable as data-contract tests. Add a docstring to the module/class explicitly documenting the coupling to `components.json` balance values.
- [ ] Verify: `pytest tests/integration/data/test_pipeline_unification.py` passes; LOC delta approximately 0 (documentation only)

---

### Task 4.2: Use os.utime for component-derivatives mtime test [Simple]
**File:** `tests/unit/assets/test_component_derivatives.py`
**Tests:** `pytest tests/unit/assets/test_component_derivatives.py`

- [ ] S06-CAT7-001: replace `time.sleep(0.01)` between writes (line 68) with explicit `os.utime()` calls to set mtime in `test_regenerates_when_master_hash_changes`.
- [ ] Verify: `pytest tests/unit/assets/test_component_derivatives.py` passes; LOC delta approximately -1

---

### Task 4.3: Replace LLM background polling sleeps with mocked clock [Complex]
**File:** `tests/unit/services/llm/test_background.py`
**Tests:** `pytest tests/unit/services/llm/test_background.py`

_(Plan-review M-005 (2026-05-03): original Event-sync proposal required production change. Mocked clock keeps the fix in test scope.)_

- [ ] S12-CAT7-001: **Replace the polling sleep loops with a mocked clock** (e.g., `freezegun.freeze_time` or a manual `time.monotonic` patch). Do NOT modify `game/services/llm/background.py` to add a `threading.Event` — that's a production change out of P1 test-cleanup scope. Keep deadlines as safety nets where they remain meaningful under a mocked clock.
- [ ] Fallback: if mocked clock is infeasible (e.g., the polling logic uses a non-monotonic clock), skip the test with `@pytest.mark.skip(reason="Polling-loop test pending production-side Event API; tracked in PROJ-XXX")` and create a follow-up project for the production change.
- [ ] Verify: `pytest tests/unit/services/llm/test_background.py` passes; LOC delta approximately -20

---

### Task 4.4: Mock clock for decorator duration assertion [Simple]
**File:** `tests/unit/services/llm/test_decorators.py`
**Tests:** `pytest tests/unit/services/llm/test_decorators.py`

- [ ] S03-CAT7-001: replace `time.sleep(0.02)` (line 142) and the `duration_ms > 15` assertion with a mocked clock or `freezegun`.
- [ ] Verify: `pytest tests/unit/services/llm/test_decorators.py` passes; LOC delta approximately -2

---

### Task 4.5: Mock clock for persistence both-bound assertion [Simple]
**File:** `tests/unit/services/llm/test_persistence.py`
**Tests:** `pytest tests/unit/services/llm/test_persistence.py`

- [ ] S03-CAT7-002: replace `time.sleep(0.05)` (line 96) and the `45 < duration < 100` two-bound assertion with a mocked clock; both bounds can fail under heavy CI load or Windows 15.6ms timer resolution.
- [ ] Verify: `pytest tests/unit/services/llm/test_persistence.py` passes; LOC delta approximately -2

---

### Task 4.6a: S08-CAT7-002 — race-description LLM controller test_sleep replacements [Medium]
**File:** `tests/unit/services/llm/test_race_description_llm_controller.py`
**Tests:** `pytest tests/unit/services/llm/test_race_description_llm_controller.py`

_(Plan-review N-003 (2026-05-03): split from original Task 4.6 because the two sub-findings have different remediation shapes. Stay consistent with M-005 — prefer test-only changes; if Event sync requires production changes, swap to mocked clock with a TODO.)_

- [ ] S08-CAT7-002: replace the 4 `time.sleep(0.02)` calls (lines 135, 139, 325, 343) with **Event-based synchronization** in the test (test-side helper, not a production change). The `_wait_until` spin-loop using `time.sleep(0.01)` should use the same helper.
- [ ] Verify: `pytest tests/unit/services/llm/test_race_description_llm_controller.py` passes; LOC delta approximately -5

---

### Task 4.6b: S08-CAT7-003 — _BlockingProvider polling replacement [Medium]
**File:** `tests/unit/services/llm/test_race_description_llm_controller.py`
**Tests:** `pytest tests/unit/services/llm/test_race_description_llm_controller.py`

_(Plan-review N-003 (2026-05-03): split from original Task 4.6.)_

- [ ] S08-CAT7-003: replace the `_BlockingProvider.complete` polling (lines 82-91) — `while time.monotonic() < end` with `time.sleep(0.005)` — with a **mocked clock** (`freezegun` or a manual `time.monotonic`/`time.sleep` patch). Current shape can take up to 5 seconds. If mocked-clock is infeasible, fall back to the M-005 skip pattern with a follow-up project tracker.
- [ ] Verify: `pytest tests/unit/services/llm/test_race_description_llm_controller.py` passes; LOC delta approximately -3

---

### Task 4.7: Use os.utime for auto-save mtime test [Simple]
**File:** `tests/unit/strategy/data/test_auto_save.py`
**Tests:** `pytest tests/unit/strategy/data/test_auto_save.py`

- [ ] S08-CAT7-001: replace `time.sleep(0.01)` (line 124) with explicit `os.utime()` to set mtime for the save-file immutability check.
- [ ] Verify: `pytest tests/unit/strategy/data/test_auto_save.py` passes; LOC delta approximately -1

---

### Task 4.8: Deterministic timestamps for save-selection ordering test [Simple]
**File:** `tests/unit/ui/screens/test_save_selection.py`
**Tests:** `pytest tests/unit/ui/screens/test_save_selection.py`

- [ ] S09-CAT7-001: replace the arbitrary `time.sleep(0.1)` (line 204) with `os.utime()` or a seeded clock to control timestamps deterministically.
- [ ] Verify: `pytest tests/unit/ui/screens/test_save_selection.py` passes; LOC delta approximately -1

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
