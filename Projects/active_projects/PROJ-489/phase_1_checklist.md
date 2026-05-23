# Phase 1: Consolidate to `ModifierService` canonical

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-489 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate three duplicate modifier-validation implementations into a single canonical surface on `ModifierService`. Delegate from UI layer; eliminate inline duplication in `ModifierManager`.

---

## Tasks

### Task 1.1: Reconcile divergent behavior on `_has_arc_set_effect` vs hardcoded `turret_mount`
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_modifier_service.py`

- [x] Read `ModifierService.get_initial_value` (line 181) and `ModifierService.get_local_min_max` (line 239). These already use generic `_has_arc_set_effect`.
- [x] Read `ModifierLogicService.get_initial_value` (line 84) and `ModifierLogicService.get_local_min_max` (line 105). These hardcode `turret_mount` arc_set handling.
- [x] Confirm `_has_arc_set_effect` matches the `turret_mount` arc_set behavior for backwards compatibility. If not, fix in `ModifierService` first (additive — capture any missing cases).
- [x] Document in design.md any behavioral reconciliation decisions made here.

### Task 1.2: Consolidate `ModifierManager.add_modifier`'s inline restriction check
**File:** `game/simulation/components/modifier_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_manager.py`

- [x] Inline at lines 108-117 in `add_modifier()` — replace inline `deny_types`/`allow_types` check with a call to `ModifierService.is_modifier_allowed(mod_id, component)`
- [x] Ensure the `allow_abilities` check (missing from the inline version) is now correctly applied — verifier noted this was a gap
- [x] Inject `ModifierService` via DI or grab it from registry; do not construct a fresh instance per `add_modifier` call

### Task 1.3: Consolidate `ComponentService.is_modifier_allowed`
**File:** `game/ui/services/component_service.py`
**Tests:** `pytest tests/unit/ui/services/test_component_service.py`

- [x] Replace `ComponentService.is_modifier_allowed` body (line 88) with a delegate call to `ModifierService.is_modifier_allowed`
- [x] `ComponentService` retains its other helpers (`get_modifier_registry`, `get_modifier_definition`) unchanged

### Task 1.4: Have `ModifierLogicService` delegate shared methods to `ModifierService`
**File:** `game/ui/screens/builder/modifier_logic.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_logic.py`

- [x] `ModifierLogicService.is_modifier_allowed` (line 66) → delegate to `ModifierService.is_modifier_allowed` (instead of `ComponentService`)
- [x] `ModifierLogicService.get_mandatory_modifiers` (line 70) → delegate to `ModifierService.get_mandatory_modifiers`
- [x] `ModifierLogicService.is_modifier_mandatory` (line 80) → delegate to `ModifierService.is_modifier_mandatory`
- [x] `ModifierLogicService.get_initial_value` (line 84) → delegate to `ModifierService.get_initial_value`
- [x] `ModifierLogicService.get_local_min_max` (line 105) → delegate to `ModifierService.get_local_min_max`
- [x] `ModifierLogicService.ensure_mandatory_modifiers` (line 121) → delegate to `ModifierService.ensure_mandatory_modifiers`
- [x] Keep `calculate_snap_value` (UI-only — no simulation equivalent)
- [x] Delete `_get_base_firing_arc` and any other private helpers now made redundant by the delegation

### Task 1.5: Update UI callers to receive `ModifierService` directly (optional simplification)
**File:** `game/ui/screens/workshop_screen.py`, `game/ui/screens/builder/detail_panel.py`, `game/ui/screens/builder/modifier_row.py`, `game/ui/panels/builder_widgets.py`
**Tests:** affected UI tests

- [x] Decide: keep `ModifierLogicService` as a thin wrapper for UI ergonomics, or have callers receive `ModifierService` directly and call `calculate_snap_value` via a free function? **Decision: keep `ModifierLogicService` as facade (preserves `calculate_snap_value` as UI ergonomics helper; minimal caller churn).**
- [x] If keeping `ModifierLogicService`: ensure its constructor takes a `ModifierService` reference. Update callers to inject one.
- [ ] ~~If removing `ModifierLogicService` entirely~~ (not pursued — facade kept).

### Phase Verification
- [x] `pytest tests/ --testmon` passes
- [x] `grep -rn "is_modifier_allowed\b" game/` shows no more than 2 active definitions: `ModifierService.is_modifier_allowed` (canonical) and `ModifierLogicService.is_modifier_allowed` (thin delegate) — `ComponentService.is_modifier_allowed` should be a one-liner delegate
- [x] `ModifierManager.add_modifier` no longer contains inline `deny_types`/`allow_types`/`allow_abilities` check loops
- [x] No behavior regression: existing modifier-validation tests still pass; the previously-missing `allow_abilities` check in `ModifierManager` now correctly rejects mismatched modifier+component pairs. 7 regression-snapshot baselines that encoded the prior buggy behavior (`crew_quarters_automation_*` × 4, `generator_efficiency_*` × 3) were re-shot per user decision (2026-05-23) and now reflect the correct "modifier rejected, baseline stats preserved" behavior.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
