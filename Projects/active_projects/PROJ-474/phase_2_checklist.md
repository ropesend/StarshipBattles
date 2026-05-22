# Phase 2: Codex exec-audit follow-ups

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-474 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve the VERIFIED findings from the one-round Codex execution
audit (`AgentCoordination/Scratchpad/Consult/proj474_exec_audit/audit.md`). The
audit found NO correctness defects in `_UISAFE_SYMBOLS`, the parity test, the
no-misfile invariant, or the `EmpireEconomySnapshot` deletion, and confirmed no
live-domain symbol was wrongly promoted. Two test-strength / doc-drift items
were verified and fixed; the rest were rejected.

**Audit verdict (verified against live code):**
- **Finding 1 — VERIFIED:** the guard's failure message + `test_no_unallowlisted_strategy_imports_in_ui`
  docstring still told maintainers to add UI-safe symbols to `_IMPORT_ALLOWLIST`
  (the pre-PROJ-474 misfile pattern). Was `imports_guard.py:365-368`, `:349-352`.
- **Finding 2 — VERIFIED:** the no-misfile RED proof existed only as a manual
  Task 1.4 step, with no durable test pinning the detection logic.
- **Risk: parity parser robustness — VERIFIED (minor):** parser did not assert a
  closing fence was seen.
- **Risk: `get_default_economy_config` returns a cached singleton with a mutable
  `Dict` field — REJECTED:** Codex itself recommended keeping the promotion (no
  session/domain reach; convention-safe per the design's static-config-loader
  criterion). No change.
- **Risk: stale bookkeeping — VERIFIED:** addressed by the Phase 1/Phase 2
  bookkeeping update (this is the closing step, not a code defect).
- **Open questions: none.**

---

## Tasks

### Task 2.1: Fix the misleading guard guidance (Finding 1) [Simple]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -q`

- [x] Rewrite the `pytest.fail` message so a UI-safe symbol is routed to
  `_UISAFE_SYMBOLS` + the Pattern #5 token block (NOT a file-scoped triple),
  with the no-misfile invariant called out; transitional/live reads still go to
  `_IMPORT_ALLOWLIST`.
- [x] Update `test_no_unallowlisted_strategy_imports_in_ui` docstring to describe
  the two-tier classification (`_UISAFE_SYMBOLS` symbol-level vs `_IMPORT_ALLOWLIST`
  file-scoped).
- [x] Verify: full guard module green.

### Task 2.2: Durable non-vacuity proof for the no-misfile invariant (Finding 2) [Simple]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k non_vacuous -q`

- [x] Extract the intersection logic into `_misfiled_symbols(uisafe, transitional)`;
  have the live invariant test call it.
- [x] Add `test_no_misfile_invariant_is_non_vacuous`: a synthetic UI-safe symbol
  duplicated as a transitional triple IS reported; a non-colliding triple is NOT;
  the clean case returns `[]`.
- [x] Verify: green; would fail if `_misfiled_symbols` were made vacuous.

### Task 2.3: Harden the parity parser (parser-robustness risk) [Simple]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k parity -q`

- [x] Assert the canonical token fence was both opened AND closed (reject an
  unterminated block).
- [x] Verify: parity test green.

### Task 2.4: Re-validate [Simple]
- [x] `pytest tests/static_guards/ -q` green (1399 passed).
- [x] `python Tools/test_sharded/test_sharded.py` green (24243 passed, 0 failed).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to user verification
