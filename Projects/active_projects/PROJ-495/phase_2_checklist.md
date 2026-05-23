# Phase 2: CAT-8 needless complexity (core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Flatten deeply-nested patch chains and oversized helpers in core-mechanical tests. Inherited from PROJ-480 Phase 2.

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 2.1: test_ai_controller_unit.py — 3 nested patches × multiple tests
**File:** `tests/unit/ai/test_ai_controller_unit.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`
**Origin:** PROJ-480 T2.5

- [ ] Extract the 3-nested patch + lambda capture stack (PROJ-480 cited lines 284-325) into a shared context-manager helper.
- [ ] Address the 4-nested patches (PROJ-480 cited lines 367-420) — apply same extraction.
- [ ] Refactor TestNavigateTo cluster (PROJ-480 cited lines 623-809, 12 test methods each rebuild AIController with slight variations) — extract `_make_ai_controller(**overrides)` helper.
- [ ] Verify: passes; LOC delta ≈ -80.

### Task 2.2: test_ship_stats.py — 43-line setup for 8-line test body
**File:** `tests/unit/simulation/entities/test_ship_stats.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_stats.py`
**Origin:** PROJ-480 T2.8

- [ ] Compress the `_TL_ABILITY`/`_VS_ABILITY` SimpleNamespace + `_HangarComponent` class + 9-attribute MagicMock ship setup (PROJ-480 cited lines 12-55) into a fixture; per-test setup drops dramatically.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.3: test_container.py — 5 trivial wrapper functions
**File:** `tests/unit/strategy/data/test_container.py` (retargeted from PROJ-480's `tests/unit/strategy/test_container.py`)
**Tests:** `pytest tests/unit/strategy/data/test_container.py`
**Origin:** PROJ-480 T2.11

- [ ] Inline or use constants for the 5 single-line wrapper functions (PROJ-480 cited lines 38-63: `_any_policy`, `_metals`, `_energy`, `_human`, `_fighter`).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 2.4: test_resupply_engine.py — 9 module-level mock factories
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`
**Origin:** PROJ-480 T2.12

- [ ] Move the 9 module-level mock factory helpers (PROJ-480 cited lines 20-101, 306-379) to `tests/unit/strategy/engine/conftest.py`.
- [ ] _(coordination note: tied to DUP-005 / HLP-006 sweep in PROJ-479 Phase 5/6.)_
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 2.5: test_fleet_navigation_action_timing.py — 5 double-patch tests
**File:** `tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
**Origin:** PROJ-480 T2.23

- [ ] Extract the 2-level nested `with patch(find_hybrid_path)` pattern (PROJ-480 cited lines 66-308, 5 test methods) into a helper context manager. PROJ-323 Task 2.14 acknowledged the intent.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.6: test_tech_preset_loader.py — identical patch wrapper
**File:** `tests/unit/simulation/systems/test_tech_preset_loader.py` (retargeted from PROJ-480's `tests/unit/strategy/data/`)
**Tests:** `pytest tests/unit/simulation/systems/test_tech_preset_loader.py`
**Origin:** PROJ-480 T2.29

- [ ] Move the identical `with patch('TECH_PRESETS_DIR', str(temp_presets_dir))` wrapper (every test in 5+ class methods) to a `@pytest.fixture(autouse=True)` in the class. Codex spot-check 2026-05-23 confirmed pattern still pervasive at `:88-575`.
- [ ] Verify: passes; LOC delta ≈ -25.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3 (CAT-10 parametrize)
