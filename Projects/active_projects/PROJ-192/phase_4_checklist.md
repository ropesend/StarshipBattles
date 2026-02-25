# Phase 4: combat_utils.py Refactoring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the 12 dual-path hasattr/getattr chains in `combat_utils.py` with typed approaches.

---

## Tasks

### Task 4.1: `is_vector2_like()` simplification (lines 34-47) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [ ] Replace duck-typed Vector2 check (`hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'distance_to')`) with `isinstance(obj, Vector2)` — codebase always uses `game.core.math.Vector2`
- [ ] Keep mock detection (`_mock_name`, `assert_called`) as a separate early return

**Notes:**

### Task 4.2: `get_position()` and `get_rotation()` typed paths (lines 82-125) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [ ] `get_position()`: Check `isinstance(entity, IControllable)` → `entity.get_position()`, else `entity.position`
- [ ] `get_rotation()`: Check `isinstance(entity, IControllable)` → `entity.get_rotation()`, else `entity.angle`
- [ ] Remove try/except/hasattr/callable chains

**Notes:**

### Task 4.3: `get_entity_id()` and `get_all_components()` (lines 63, 128-139) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [ ] `get_entity_id()`: Replace cascading getattr with `entity.name if hasattr(entity, 'name') else str(id(entity))` — Ships have `.name`, Projectiles don't, neither has `.id`
- [ ] `get_all_components()`: Replace hasattr/callable chain with `isinstance` check or direct call (Ships always have this method)

**Notes:**

### Task 4.4: `get_hp_percent()` and `is_in_pdc_arc()` (lines 180-213) [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [ ] `get_hp_percent()` (L180-181): Replace `getattr(c, 'max_hp', 0)` with `c.max_hp` and `getattr(c, 'current_hp', ...)` with `c.current_hp`
- [ ] `is_in_pdc_arc()` (L207): Replace `getattr(ship, 'get_components_by_ability', None)` with direct call
- [ ] `is_in_pdc_arc()` (L212): Replace `getattr(comp, 'has_pdc_ability', None)` with direct `comp.has_pdc_ability()`

**Notes:**

### Task 4.5: Update combat_utils tests [Simple]
**File:** `tests/unit/ai/test_combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py -v`

- [ ] Update mocks to match new isinstance-based paths
- [ ] Ensure test coverage for both IControllable and raw-entity paths in `get_position()`/`get_rotation()`
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
