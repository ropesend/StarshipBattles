# Phase 1: Delete deprecated `*_static` methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-384 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete 12 deprecated `@staticmethod` methods (166 LOC) left over from PROJ-241's instance-API migration. Zero production callers; the methods carry an explicit `# DEPRECATED — Use instance method instead` comment.

---

## Tasks

### Task 1.1: Delete `AbilityManager.*_static` methods
**File:** `game/simulation/components/ability_manager.py`
**Tests:** `pytest tests/ -k test_ability_manager`

- [x] Delete 6 deprecated static methods at lines 286-341 (`get_abilities_static`, `get_ability_static`, `has_ability_static`, `has_pdc_ability_static`, `get_ui_rows_static`, `instantiate_abilities_static`) (LEG-01-003) (0 call sites — single-PR deletion of 56 LOC)
- [x] Migrate the 3 test methods in `tests/.../test_ability_manager.py` that call these statics to the instance API (now use `component.ability_manager.get_abilities()` etc.)
- [x] Verify: `grep -rn "_static" game/simulation/components/ability_manager.py` shows zero hits

### Task 1.2: Delete `ModifierManager.*_static` methods
**File:** `game/simulation/components/modifier_manager.py`
**Tests:** `pytest tests/ -k test_modifier_manager`

- [x] Delete 6 deprecated static methods at lines 221-330 (`add_modifier_static`, `remove_modifier_static`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static`, `remove_modifier_inplace`) (LEG-01-004) (0 external call sites; 1 internal `remove_modifier_inplace` reference inside `add_modifier_static` is self-contained — single-PR deletion of 110 LOC)
- [x] Verify: `grep -rn "_static\|remove_modifier_inplace" game/ tests/ combat_lab/` shows zero hits in non-deleted code (only unrelated `mock_static` Mock-variable names + unrelated `_static` test-name suffixes in pathfinding/weapons remain)

### Task 1.3: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved (15405 passed) — **DEFERRED to orchestrator** (full sharded suite is the orchestrator's job per task brief). Focused regression `pytest tests/ -k "ability_manager or modifier_manager"` returned 63 passed.
- [x] Verify: pytest passes; no remaining references to any of the 12 deleted method names anywhere in the repo

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (full-sharded run delegated to orchestrator)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
