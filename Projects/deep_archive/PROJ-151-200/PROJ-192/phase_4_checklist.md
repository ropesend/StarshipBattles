# Phase 4: combat_utils.py Refactoring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the 12 dual-path hasattr/getattr chains in `combat_utils.py` with typed approaches.

---

## Tasks

### Task 4.1: `is_vector2_like()` simplification (lines 34-47) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [x] Replace duck-typed Vector2 check (`hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'distance_to')`) with `isinstance(obj, Vector2)` — codebase always uses `game.core.math.Vector2`
- [x] Keep mock detection (`_mock_name`, `assert_called`) as a separate early return

**Notes:** Simplified to use isinstance(obj, Vector2) directly.

### Task 4.2: `get_position()` and `get_rotation()` typed paths (lines 82-125) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [x] `get_position()`: Check `isinstance(entity, IControllable)` → `entity.get_position()`, else `entity.position`
- [x] `get_rotation()`: Check `isinstance(entity, IControllable)` → `entity.get_rotation()`, else `entity.angle`
- [x] Remove try/except/hasattr/callable chains

**Notes:** Replaced getattr/callable chains with isinstance(entity, IControllable) checks.

### Task 4.3: `get_entity_id()` and `get_all_components()` (lines 63, 128-139) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [x] `get_entity_id()`: Replace cascading getattr with `entity.name if hasattr(entity, 'name') else str(id(entity))` — Ships have `.name`, Projectiles don't, neither has `.id`
- [x] `get_all_components()`: Replace hasattr/callable chain with `isinstance` check or direct call (Ships always have this method)

**Notes:** Removed the .id check (no entities use it). Simplified to check .name then fallback to id().

### Task 4.4: `get_hp_percent()` and `is_in_pdc_arc()` (lines 180-213) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [x] `get_hp_percent()` (L180-181): Replace `getattr(c, 'max_hp', 0)` with `c.max_hp` and `getattr(c, 'current_hp', ...)` with `c.current_hp`
- [x] `is_in_pdc_arc()` (L207): Replace `getattr(ship, 'get_components_by_ability', None)` with direct call
- [x] `is_in_pdc_arc()` (L212): Replace `getattr(comp, 'has_pdc_ability', None)` with direct `comp.has_pdc_ability()`

**Notes:** Direct attribute access - components always have max_hp/current_hp/has_pdc_ability.

### Task 4.5: Update combat_utils tests [Simple]
**File:** `tests/unit/ai/test_combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py -v`

- [x] Update mocks to match new isinstance-based paths
- [x] Ensure test coverage for both IControllable and raw-entity paths in `get_position()`/`get_rotation()`
- [x] All tests pass

**Notes:** Updated all mocks to use Mock(spec=[...]) with direct attributes instead of method mocks. Removed 2 obsolete tests (test_with_id_attribute, test_with_object_id_fallback - get_entity_id now only checks .name). Tests: 32 passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
