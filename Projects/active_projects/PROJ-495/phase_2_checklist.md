# Phase 2: CAT-8 needless complexity (core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Flatten deeply-nested patch chains and oversized helpers in core-mechanical tests. Inherited from PROJ-480 Phase 2.

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 2.1: test_ai_controller_unit.py — 3 nested patches × multiple tests — DROPPED `[~]`
**Reason:** `AIController(mock_ship, mock_grid, enemy_team_id=1)` is a one-line construction; the nested patches target different functions per test (each test patches a different module path / object, so a single helper context manager wouldn't fit). The 11 TestNavigateTo methods each set 3-4 ship attrs that vary per test; a `_make_ai_controller()` helper saves ~1-2 LOC per test at the cost of indirection.

- [~] Out of scope (CAT-8 not justified)

### Task 2.2: test_ship_stats.py — 43-line setup for 8-line test body — DROPPED `[~]`
**Reason:** File is 55 LOC with a **single** test method using the SimpleNamespace + class + MagicMock setup. Extracting a fixture for one consumer adds indirection without reducing complexity.

- [~] Out of scope (single-consumer setup)

### Task 2.3: test_container.py — 5 trivial wrapper functions — DROPPED `[~]`
**Reason:** The 5 wrappers (`_any_policy`, `_metals`, `_energy`, `_human`, `_fighter`) are called 83 times across the file. Inlining would explode LOC; the wrappers function as named factories / constants.

- [~] Out of scope (inlining would increase LOC, not reduce)

### Task 2.4: test_resupply_engine.py — 9 module-level mock factories — DROPPED
**Reason:** Absorbed by PROJ-479 DUP-005 / Task 5.4: `_make_empire` was migrated to `make_mock_empire` in `tests/unit/strategy/engine/conftest.py`, leaving only a thin local wrapper. The remaining 8 helpers (`_make_mock_registries`, `_make_fuel_facility`, `_make_energy_facility`, `_make_colony`, `_make_mock_ship`, `_make_mock_fleet`, `_make_mock_galaxy`, `_make_planet_with_fuel`) are file-specific fuel/resupply scaffolding; moving them to engine/conftest.py would pollute the shared conftest with single-file symbols.

- [ ] ~~Move the 9 module-level mock factory helpers (PROJ-480 cited lines 20-101, 306-379) to `tests/unit/strategy/engine/conftest.py`.~~ Absorbed by PROJ-479 (`_make_empire`); remaining 8 are file-specific.
- [ ] ~~Verify: passes; LOC delta ≈ -50.~~
- **Phase 5 follow-through (2026-05-23):** Colony-side helper wrapping landed in Phase 2 (PROJ-479 DUP-005); fleet-side cleanup landed in Phase 5 — 7 ad-hoc MagicMock empire stubs replaced with `_make_empire(fleets=...)`.

### Task 2.5: test_fleet_navigation_action_timing.py — 5 double-patch tests
**File:** `tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
**Origin:** PROJ-480 T2.23

- [x] Extract the 2-level nested `with patch(find_hybrid_path)` pattern (PROJ-480 cited lines 66-308, 5 test methods) into a helper context manager. PROJ-323 Task 2.14 acknowledged the intent.
- [x] Verify: 16 tests pass; added `patched_pathing(*, hybrid_path_return, action_time_return)` context manager and converted 5 nested patch sites.

### Task 2.6: test_tech_preset_loader.py — identical patch wrapper
**File:** `tests/unit/simulation/systems/test_tech_preset_loader.py` (retargeted from PROJ-480's `tests/unit/strategy/data/`)
**Tests:** `pytest tests/unit/simulation/systems/test_tech_preset_loader.py`
**Origin:** PROJ-480 T2.29

- [x] Move the identical `with patch('TECH_PRESETS_DIR', str(temp_presets_dir))` wrapper (every test in 5+ class methods) to a `@pytest.fixture(autouse=True)` in the class. Codex spot-check 2026-05-23 confirmed pattern still pervasive at `:88-575`. Implemented by folding the patch into the `temp_presets_dir` fixture itself (any test that requests the temp dir auto-gets the patch).
- [x] Verify: 44 tests pass; 26 wrapper sites removed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (CAT-10 parametrize)
