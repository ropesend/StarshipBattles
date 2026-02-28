# Phase 1: Pure File Deletions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete remaining dead files and clean up re-export (~505 lines removed)
**Priority:** High — safest operations, zero migration needed

**Note:** PROJ-157 already deleted 5 of the original 8 files. Only 3 files + 1 __init__ cleanup remain.

---

## Tasks

### Task 1.1: Delete UI dead mock file [Simple]
**Files:**
- `tests/unit/ui/mocks/mock_battle_ui_service.py` (256 lines) — UI-3

**Tests:** `pytest tests/unit/ui/ -n 12 --tb=short -q`

- [x] ~~Delete `tests/unit/ui/test_overlay.py`~~ (done by PROJ-157)
- [x] ~~Delete `tests/unit/ui/test_slider_snap_logic.py`~~ (done by PROJ-157)
- [x] Delete `tests/unit/ui/mocks/mock_battle_ui_service.py`
- [x] Edit `tests/unit/ui/mocks/__init__.py`: remove line 6 (`from tests.unit.ui.mocks.mock_battle_ui_service import MockBattleUIService`) and line 8 (`__all__ = ['MockBattleUIService']`). Replace with empty `__all__ = []` or leave just the module docstring.
- [x] Run `pytest tests/unit/ui/ -n 12 --tb=short -q` — verify no NEW failures (20 failed = pre-existing)

**Notes:**

### Task 1.2: Delete Strategy stub and duplicate files [Simple]
**Files:**
- `tests/unit/strategy/conflict_resolution/test_conflict_core.py` (23 lines) — STR-4
- `tests/unit/strategy/data/test_build_queue_source_errors.py` (29 lines) — STR-6
- `tests/unit/strategy/test_fleet_resource_aggregator.py` (196 lines) — STR-2 (subset of `tests/unit/strategy/data/test_fleet_resource_aggregator.py`)

**Tests:** `pytest tests/unit/strategy/ -n 12 --tb=short -q`

- [x] Delete `tests/unit/strategy/conflict_resolution/test_conflict_core.py`
- [x] ~~Delete `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py`~~ (done by PROJ-157)
- [x] Delete `tests/unit/strategy/data/test_build_queue_source_errors.py`
- [x] ~~Delete `tests/unit/strategy/test_ship_display_formatter_edge_cases.py`~~ (done by PROJ-157)
- [x] ~~Delete `tests/unit/strategy/test_hex_math.py`~~ (done by PROJ-157)
- [x] Delete `tests/unit/strategy/test_fleet_resource_aggregator.py`
- [x] Run `pytest tests/unit/strategy/ -n 12 --tb=short -q` — verify no NEW failures (92 failed = pre-existing)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
