# Phase 1: Quick Wins — Slider, Deprecation, Clamping

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-83 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix 3 warning categories with precise, localized fixes (~35 warnings)

---

## Tasks

### Task 1.1: Fix Slider Value Out of Range [Simple]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py -W error`

- [ ] Line 220-221: Swap order — set `value_range` BEFORE `set_current_value`:
  ```python
  # Current (broken order):
  self.slider_amount.set_current_value(max_val)
  self.slider_amount.value_range = (0, max_val)

  # Fixed:
  self.slider_amount.value_range = (0, max_val)
  self.slider_amount.set_current_value(max_val)
  ```
- [ ] Verify: Run `pytest tests/unit/ui/screens/test_transfer_dialog.py -W error` — no "value not in range" warning

**Notes:**

---

### Task 1.2: Fix BattleEngine Deprecation Warnings [Medium]
**Tests:** `pytest tests/unit/combat/ tests/integration/fleet_combat/ tests/unit/fixtures/ -W error::DeprecationWarning`

#### 1.2a: Fix `create_battle_engine()` fixture
**File:** `tests/fixtures/battle.py`

- [ ] Add import: `from game.simulation.factories.ai_factory import AIControllerFactory` (near line 32)
- [ ] In `create_battle_engine()` (line 40-54), after creating engine, add:
  ```python
  factory = AIControllerFactory(engine.grid)
  engine._ai_factory = factory
  ```
- [ ] This auto-fixes callers: `test_service_integration.py` (5 tests) and `test_battle_fixtures.py` (3 tests)

#### 1.2b: Fix `test_battle_engine_core.py`
**File:** `tests/unit/combat/test_battle_engine_core.py`

- [ ] `test_remove_ship_removes_ai_controller` (line ~140): After creating engine at line 140, add ai_factory:
  ```python
  engine = BattleEngine(logger=mock_logger)
  from game.simulation.factories.ai_factory import AIControllerFactory
  engine._ai_factory = AIControllerFactory(engine.grid)
  ```
- [ ] Delete `test_start_without_ai_controllers_uses_legacy_path` (lines 207-225) — per user decision
- [ ] `test_add_ship_mid_battle_with_precreated_controller` (line ~227): Add ai_factory to engine at line 234 (same pattern)
- [ ] Delete `test_add_ship_mid_battle_without_controller_uses_legacy_path` (lines 255-276) — per user decision

#### 1.2c: Fix `test_fighter_launch.py`
**File:** `tests/unit/combat/test_fighter_launch.py`

- [ ] `test_battle_engine_launch_processing` (line ~85): Before `engine.start()` at line 96, add:
  ```python
  from game.simulation.factories.ai_factory import AIControllerFactory
  engine._ai_factory = AIControllerFactory(engine.grid)
  ```
- [ ] `test_fighter_launch_speed_uses_config` (line ~165): Same pattern before `engine.start()` at line 179

- [ ] Verify: Run `pytest tests/unit/combat/ tests/integration/fleet_combat/ tests/unit/fixtures/ -W error::DeprecationWarning` — zero deprecation warnings

**Notes:**

---

### Task 1.3: Add Warning Filters for pygame_gui Cosmetic Warnings [Simple]
**File:** `pytest.ini`
**Tests:** `pytest tests/ -n 12 --tb=short -q`

- [ ] Add `filterwarnings` section to `pytest.ini`:
  ```ini
  filterwarnings =
      ignore:Clamping shadow_width:UserWarning
      ignore:Clamping border_width:UserWarning
      ignore:Finding font with id.*not already loaded:UserWarning
  ```
- [ ] Verify: Run `pytest tests/ -n 12 --tb=short -q` — shadow, border, and font warnings gone

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 --tb=short` — warning count significantly reduced from 299
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
