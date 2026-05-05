# PROJ-321 Post-Execution Review: Findings Report

**Review date:** 2026-05-04
**Project:** PROJ-321 — P0 dead-trivial test cleanup (CAT-1/2/3)
**Scope:** Spot-check deleted tests for genuine vacuity; verify no production coverage loss
**Method:** Examined 8 deletions across all 3 phases via `git show` on commits 148170d2f, 96f63d026, deed107b8

---

## Spot-Check Summary

| # | File | Test(s) | Phase | Category | Vacuity Confirmed? |
|---|------|---------|-------|----------|-------------------|
| 1 | `test_combat_types.py` | `test_import_path` | 1 | CAT-1 | Yes — import alias identity check, zero behavioral value |
| 2 | `test_event_log_window.py` | 8 tests (module_exists, hasattr, constant-value) | 1 | CAT-1 | Yes — all import-existence/hasattr/constant-value trivia |
| 3 | `test_ai_factory.py` | 5 existence/attribute tests | 1 | CAT-1 | Yes — `is not None` / `hasattr` checks; behavioral tests preserved in same file |
| 4 | `test_modifier_logic.py` | Entire file (103 LOC) | 2 | CAT-2 | Yes — tested locally-defined helper functions, not production code |
| 5 | `test_handle_command` | `test_handle_command` (body: `pass`) | 3 | CAT-3 | Yes — empty test body, zero assertions |
| 6 | `test_layout_scaling.py` | Entire file (22 LOC) | 1 | CAT-1 | Yes — `is not None` import checks only |
| 7 | `test_intercept_edge_cases.py` | Entire file (27 LOC) | 1 | CAT-1 | Yes — 3 import-existence checks only |
| 8 | `test_strategy_session_facade_public_api.py` | `TestPublicMethodSurface` + `PUBLIC_METHODS` frozenset (33 LOC) | 1 | CAT-1 | Partially — contract guard had real value (see FND-001) |
| 9 | `test_fleet_navigation_no_mock_hack.py` | Entire file (54 LOC) | 2 | CAT-2 | Yes — signature-scan + source-scan tests only |

---

## Findings

### FND-001: Facade public API contract guard deleted without confirmed replacement in PROJ-322

**Severity:** MAJOR
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
**Line:** Deleted lines 22-81 (PUBLIC_METHODS) and lines 122-154 (TestPublicMethodSurface)
**Description:** Task 1.14 deleted the `PUBLIC_METHODS` frozenset (~50 documented public methods) and the `TestPublicMethodSurface` class (3 tests: `test_every_public_method_present`, `test_every_public_method_callable`, `test_no_unexpected_public_methods_added`). These were not trivially-passing — they performed real set-difference computations and produced meaningful failure messages when the facade's public API surface drifted from the documented contract. The `test_no_unexpected_public_methods_added` test in particular caught silent additions of public methods via `inspect.getmembers()`. The original verification (S08-CAT1-003) recommended "Keep as a contract guard but rename and document; consider moving to a lint step." The P0 cleanup chose deletion with the callback: "If the contract-guard pattern is needed, recreate it as a proper behavioral test in PROJ-322." Whether PROJ-322 Phase 5 (APC-001) has actually recreated this guard is unverified.
**Recommendation:** Verify that PROJ-322/Phase 5 includes a recreated facade API surface contract guard. If not, file a follow-up to restore it — ideally as a CI/lint step rather than a runtime test, reducing pytest suite overhead while preserving the drift-detection value.

---

## Summary Table

| Severity | Count | IDs |
|----------|-------|-----|
| CRITICAL | 0 | — |
| MAJOR | 1 | FND-001 |
| MINOR | 0 | — |

### Verification Notes

- All 8 spot-checked deletions were genuinely vacuous by the CAT-1/2/3 classification criteria. No production-code behavior paths lost coverage from the deleted tests.
- The `test_strategy_session_facade_public_api.py` file was NOT fully deleted — the `TestProtectedSurface` class and `PROTECTED_CALLABLES` / `PROTECTED_ATTRS` frozensets were preserved (lines 42-62 kept).
- Phase 2 full-file deletions (`test_system_tree_panel.py`, `test_planet_selection_window.py`, `test_unified_entry_guard.py`) listed APC-001 cluster members — these were correctly **not** deleted per the checklist's deferral to PROJ-322 Phase 5.
- The Phase 3 `repro_load_cargo_bug.py` deletion (Task 3.3) did not document whether the underlying bug was verified as fixed before deletion. The verification report (S02-CAT3-002) classified this as MINOR severity and the file was a standalone repro script, not a pytest test, so production coverage impact is nil.
