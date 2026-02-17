# Phase 1: Pure File Deletions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete 8 confirmed-dead files and clean up 1 re-export (~1,082 lines removed)
**Priority:** High — safest operations, zero migration needed

---

## Tasks

### Task 1.1: Delete UI dead files [Simple]
**Files:**
- `tests/unit/ui/test_overlay.py` (127 lines) — UI-1
- `tests/unit/ui/test_slider_snap_logic.py` (96 lines) — UI-4
- `tests/unit/ui/mocks/mock_battle_ui_service.py` (256 lines) — UI-3

**Tests:** `pytest tests/unit/ui/ -n 12 --tb=short -q`

- [ ] Delete `tests/unit/ui/test_overlay.py`
- [ ] Delete `tests/unit/ui/test_slider_snap_logic.py`
- [ ] Delete `tests/unit/ui/mocks/mock_battle_ui_service.py`
- [ ] Edit `tests/unit/ui/mocks/__init__.py`: remove line 6 (`from tests.unit.ui.mocks.mock_battle_ui_service import MockBattleUIService`) and line 8 (`__all__ = ['MockBattleUIService']`). Replace with empty `__all__ = []` or leave just the module docstring.
- [ ] Run `pytest tests/unit/ui/ -n 12 --tb=short -q` — verify no NEW failures

**Notes:**

### Task 1.2: Delete Strategy stub and duplicate files [Simple]
**Files:**
- `tests/unit/strategy/conflict_resolution/test_conflict_core.py` (23 lines) — STR-4
- `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py` (27 lines) — STR-5
- `tests/unit/strategy/data/test_build_queue_source_errors.py` (29 lines) — STR-6
- `tests/unit/strategy/test_ship_display_formatter_edge_cases.py` (28 lines) — STR-7
- `tests/unit/strategy/test_hex_math.py` (299 lines) — STR-10 (strict subset of `tests/unit/core/test_hex_math_core.py`)
- `tests/unit/strategy/test_fleet_resource_aggregator.py` (196 lines) — STR-2 (subset of `tests/unit/strategy/data/test_fleet_resource_aggregator.py`)

**Tests:** `pytest tests/unit/strategy/ -n 12 --tb=short -q`

- [ ] Delete `tests/unit/strategy/conflict_resolution/test_conflict_core.py`
- [ ] Delete `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py`
- [ ] Delete `tests/unit/strategy/data/test_build_queue_source_errors.py`
- [ ] Delete `tests/unit/strategy/test_ship_display_formatter_edge_cases.py`
- [ ] Delete `tests/unit/strategy/test_hex_math.py`
- [ ] Delete `tests/unit/strategy/test_fleet_resource_aggregator.py`
- [ ] Run `pytest tests/unit/strategy/ -n 12 --tb=short -q` — verify no NEW failures

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
