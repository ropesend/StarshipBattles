# Phase 1: AI Protocols (Foundation)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Define the Protocol type vocabulary for grid entities, projectiles, formation masters, and component health.

---

## Tasks

### Task 1.1: Create `game/ai/protocols.py` [Simple]
**File:** `game/ai/protocols.py` (NEW)
**Reference:** `game/core/protocols.py` for pattern

- [ ] Create file with module docstring explaining purpose
- [ ] Import `Protocol`, `runtime_checkable`, `TypeGuard`, `Any` from typing
- [ ] Create `IGridEntity(Protocol)` with `@runtime_checkable`:
  - `position` property (Any/Vector2)
  - `is_alive` property (bool)
  - `team_id` property (int)
  - `radius` property (float)
- [ ] Create `IProjectile(IGridEntity, Protocol)` with `@runtime_checkable`:
  - `type` property (for AttackType enum matching)
- [ ] Create `IFormationMaster(Protocol)` with `@runtime_checkable`:
  - `position`, `angle: float`, `is_alive: bool`, `is_derelict: bool`
  - `is_thrusting: bool`, `max_speed: float`, `engine_throttle: float`, `current_speed: float`
  - `formation` (Any — ShipFormation), `current_target` (Optional[Any])
- [ ] Create `IComponentHealth(Protocol)` with `@runtime_checkable`:
  - `current_hp: float`, `max_hp: float`
- [ ] Add TypeGuard functions: `is_grid_entity()`, `is_projectile()`, `is_formation_master()`, `is_component_health()`
- [ ] Export from `game/ai/interfaces/__init__.py`

**Notes:**

### Task 1.2: Write Protocol compliance tests [Simple]
**File:** `tests/unit/ai/test_ai_protocols.py` (NEW)
**Tests:** `pytest tests/unit/ai/test_ai_protocols.py`

- [ ] Test `Ship` satisfies `IGridEntity` via `isinstance()`
- [ ] Test `Projectile` satisfies `IGridEntity` and `IProjectile`
- [ ] Test `Ship` satisfies `IFormationMaster`
- [ ] Test `Component` satisfies `IComponentHealth`
- [ ] Test TypeGuard functions return correct booleans
- [ ] Test non-matching objects (plain dict, int, etc.) return `False`

**Notes:**

### Task 1.3: Verify no regressions [Simple]
- [ ] `pytest tests/unit/ai/ -v` — all pass
- [ ] `pytest tests/ -n 12` — 12705+ pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
