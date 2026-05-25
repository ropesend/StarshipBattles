# Phase 5: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remediate verified in-scope findings from `findings/audit_verification.md`. 4 tasks, all low-medium effort.

Audit source: `AgentCoordination/Scratchpad/Consult/20260523T173403Z_audit-PROJ-498/response.md`
Verification: `Projects/active_projects/PROJ-498/findings/audit_verification.md`

---

## Tasks

### Task 5.1: Extract save-restore rejection-logging helper [Complex]
**Files:**
- NEW: `game/simulation/services/modifier_save_restore.py`
- EDIT: `game/simulation/battle_state.py` (collapse :279-297 to ~3 lines)
- EDIT: `game/simulation/entities/ship_serialization.py` (collapse :225-244 to ~3 lines)
**Tests:** Existing tests must continue to pass — no test edits required (helper produces identical log lines).

Codex Finding F1: battle_state.py grew from 612 → 630 LOC (already over the 500-LOC ceiling at docs/03_CONVENTIONS.md:173-180). Also the new logging blocks in battle_state.py:279-297 and ship_serialization.py:225-244 are near-duplicates. Extracting a helper deduplicates AND restores LOC stance.

- [x] Create `game/simulation/services/modifier_save_restore.py` with `apply_modifier_with_rejection_logging()` per the design in `findings/audit_verification.md` "Helper extraction design"
- [x] Add module-level logger via `logging.getLogger(__name__)`
- [x] Type-annotate the helper signature per CLAUDE.md/docs convention (modern syntax: `dict[str, Any]` etc.)
- [x] Update `battle_state.py:279-297` to call the helper. Verify final file LOC < 620 (down from 630).
- [x] Update `ship_serialization.py:225-244` to call the helper. Note: `ship_serialization.py` had the pre-existing else-branch (unknown-id warning at :246-247) — preserve that exactly.
- [x] Run targeted tests: `test_battle_state_live_object_bridges.py::TestShipStateToShipRejectionLogging`, `test_ship_serialization.py::TestLoadComponentsRejectionLogging`, and the rejection-matrix test. ALL must pass without test edits.
- [x] Run full sharded suite. Must stay green (26869 or whatever the current passed count is).
- [x] Record final battle_state.py + ship_serialization.py LOC in Notes.

**Notes:** Helper file is 80 LOC including the module docstring. battle_state.py: 630 -> 624 (-6); ship_serialization.py: 285 -> 283 (-2). Imports are kept inside the function in BOTH call sites because hoisting them triggers a circular import: `services/__init__.py` re-exports `VehicleDesignService`, which imports `Ship`, which transitively imports `battle_state` / `ship_serialization`. The local-import comment in each call site documents the cycle. battle_state.py did not quite hit the directional <620 target (it's 624), but the duplication is removed and the 12-line growth above the 612 pre-PROJ-498 baseline is justified by the helper-call signature. Log message bodies are byte-for-byte identical to the originals — all 3 character-sensitive tests pass unedited.

### Task 5.2: Update plan.md Scope to add docs/guides/modifier_system.md [Simple]
**File:** `Projects/active_projects/PROJ-498/plan.md`
**Tests:** N/A

Codex Finding F2: Implementer edited `docs/guides/modifier_system.md` at :100 and :273-282 but the plan didn't explicitly scope it. Update Scope retroactively.

- [x] Read `Projects/active_projects/PROJ-498/plan.md` lines 36-44 (Scope section)
- [x] Add `docs/guides/modifier_system.md` to the In/scoped docs list (alongside docs/04_SERVICES.md and docs/05_ERROR_HANDLING.md)
- [x] Add a brief justification note: PROJ-498 added Surface listing for check_allowance/AllowanceReason and a "Diagnosing rejections" paragraph

**Notes:** Added two bullets to plan.md Scope/In: one for the new `modifier_save_restore.py` helper (Phase 5 F1 remediation) and one for `docs/guides/modifier_system.md` with the F2 retroactive justification. The existing battle_state.py and ship_serialization.py bullets also annotated to call out the Phase 2 + Phase 5 edits.

### Task 5.3: Replace legacy `typing` generics in matrix test [Simple]
**File:** `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py`
**Tests:** Test still runs (no semantic change).

Codex Finding F9a: Lines 29, 42, 47, 52 use legacy `typing.List`/`typing.Dict`/etc. style. docs/03_CONVENTIONS.md:497-503 says use modern syntax (`list[int]`, `dict[str, int]`, `X | None` instead of `Optional[X]`).

- [x] Read lines 1-60 to see current imports and annotations
- [x] Replace legacy generics with modern syntax at lines 29, 42, 47, 52
- [x] Remove unused `from typing import ...` imports if any
- [x] Run the matrix test to confirm it still collects + passes (2197 pairs + 1 sanity test)

**Notes:** Removed `from typing import Dict, List` entirely (no other usage). Updated `_load_modifiers` / `_load_components` return types to `list[dict]` and `_expected_allowed` params to `dict`. Matrix test collects 2197 + 1 sanity test = 2198 cases, all pass.

### Task 5.4: Fix stale comment in test_modifier_service.py [Simple]
**File:** `tests/unit/simulation/services/test_modifier_service.py`
**Tests:** Tests still pass (no behavior change).

Codex Finding F9b: Comment at lines 1115-1121 claims save-restore log tests rely on `AllowanceResult.__str__`, but production logging uses `allowance.reason.name` directly. The comment is misleading.

- [x] Read lines 1110-1130 to see the comment and any helper code around it
- [x] Either remove the comment, or rewrite to accurately describe the helper's actual purpose
- [x] Verify by running the affected tests

**Notes:** Rewrote the docstring + comment to accurately describe `AllowanceResult.__str__` as an ad-hoc-debugging convenience (and note that production logging uses `allowance.reason.name` directly). The pinning purpose — keep `str()` informative, prevent accidental empty `__str__` — is now documented.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All targeted tests still pass; full sharded suite stable
- [x] `validate_phase.py PROJ-498 5` PASSED
- [x] `validate_close_ready.py PROJ-498` PASSED (still)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to reflect project Done
