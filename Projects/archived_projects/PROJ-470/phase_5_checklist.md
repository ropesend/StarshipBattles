# Phase 5: Codex-Audit Remediation (4 verified findings)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-470 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve the 4 VERIFIED findings from the one-round Codex audit of the PROJ-470 implementation. (2 further Codex items were its own "Not Confirmed"/REJECTED — no isinstance->TypeGuard regression, no SettingsWindow lifecycle break.) Audit report recovered from `AgentCoordination/Scratchpad/Consult/proj470_audit/log.txt` (Codex output failed the consult/v1 frontmatter schema; findings intact).

---

## Tasks

### Task 5.1: Make PROJ-470 audit-ready (Finding 1, MAJOR) [Simple]
**File:** `Projects/active_projects/PROJ-470/phase_1_checklist.md`, `phase_3_checklist.md`
**Tests:** `python Projects/scripts/validate_audit_ready.py PROJ-470`

- [x] Extracted Phase 1's task boxes resolved-by-deferral (`- [x] (Deferred -> PROJ-472)`) so the validator no longer counts them as pending PROJ-470 work
- [x] Checked off Phase 3 Task 3.2 trailing verify box (targeted suites green)
- [x] Fixed the stale characterization-test path in phase_3 checklist (`test_system_slice_storm_names.py` → `tests/unit/strategy/facade/slices/test_system_slice.py::test_get_storm_names_at_hex_excludes_abilities_carrying_non_storm`)
- [x] Verify: `validate_audit_ready.py PROJ-470` → PASSED (2 advisory WARNs only: PROJ-472 active by design; index status)

### Task 5.2: Characterize SettingsWindow modality via the production path (Finding 2, MEDIUM) [Medium]
**File:** `tests/unit/ui/screens/test_settings_window_modal.py`
**Tests:** `pytest tests/unit/ui/screens/test_settings_window_modal.py`

- [x] Added `_build_settings_through_production_path` (stubs `UIWindow.__init__` + the Stage-3 widget element classes) so `StrategyModalWindow.__init__`'s production side-effects run for the SettingsWindow subclass
- [x] `test_settings_window_registers_as_live_modal_on_construction`: asserts `win in mgr._modals` (production `register_modal`), not via `bypass_init`
- [x] `test_settings_window_is_blocking_on_construction`: asserts `win.is_blocking is True` (background hover/click block)
- [x] Verify: 5 passed

### Task 5.3: Characterize source_kind payload + serialization (Finding 3, MEDIUM) [Medium]
**File:** `tests/unit/core/protocols/test_source_kind_enum.py`
**Tests:** `pytest tests/unit/core/protocols/test_source_kind_enum.py`

- [x] Replaced the weak text-grep adapter test with `test_adapters_return_typed_source_kind_equal_to_raw_string`: instantiates the REAL adapters and asserts `isinstance(..., SourceKind)` AND `== raw string`
- [x] Added `test_source_kind_payload_survives_consumer_comparisons_and_serialization`: builds the collector payload from a real `StormAbilitySource`, exercises the exact live consumer expressions (`== 'storm'`, `!= 'star'`, `f"sector:{...}"`), and asserts `json.dumps` → bare string
- [x] Verify: 9 passed

### Task 5.4: Modern typing syntax in SettingsWindow (Finding 4, MINOR) [Simple]
**File:** `game/ui/screens/settings_window.py`
**Tests:** N/A (type/convention)

- [x] Changed `Optional[Callable[[], None]]` → `Callable[[], None] | None`; dropped the unused `Optional` import (3.13 convention)
- [x] Verify: module imports clean; UI-screens suite green

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes checked
- [x] Status set to `Complete`
- [x] plan.md phase table row updated
- [x] plan.md Current State updated
