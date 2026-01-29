# Phase 3: Simulation Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-47 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Document complex simulation systems with usage-focused explanations

---

## Tasks

### Task 3.1: WeaponAbility Formula Documentation (DOC-04) [Medium]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `python -m py_compile game/simulation/components/abilities/weapons.py`

- [ ] Add/expand class docstring (line 10) explaining formula parsing:
  ```
  Formulas: Values starting with '=' are evaluated at runtime.
  Example: damage="=10 + range_to_target * 0.1"
  Context variables: range_to_target (float)
  ```
- [ ] Add docstring to `get_damage()` (line 169) - when formula vs static value used
- [ ] Verify: Run py_compile

**Notes:**

---

### Task 3.2: BattleController Results Documentation (DOC-09) [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `python -m py_compile game/simulation/battle_controller.py`

- [ ] Expand `get_results()` docstring (line 584) documenting BattleResults structure:
  - winner: int (0, 1 for teams, -1 for draw, None if not over)
  - tick_count: int (simulation ticks elapsed)
  - seed: Optional[int] (random seed for replay)
  - initial_state, final_state: BattleState
  - surviving_ships, destroyed_ships, escaped_ships, captured_ships: List[ShipState]
- [ ] Verify: Run py_compile

**Notes:**

---

### Task 3.3: ModifierService Dual-Pattern Documentation (DOC-10) [Medium]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `python -m py_compile game/simulation/services/modifier_service.py`

- [ ] Expand class docstring (lines 15-31) with dual-pattern usage examples:
  ```python
  # Instance pattern (preferred for new code):
  service = ModifierService(modifier_registry=registries.modifiers)
  if service.is_modifier_allowed('turret_mount', component):
      service.ensure_mandatory_modifiers(component)

  # Static pattern (legacy, still supported):
  if ModifierService.is_modifier_allowed('turret_mount', component):
      ModifierService.ensure_mandatory_modifiers(component)
  ```
- [ ] Verify: Run py_compile

**Notes:**

---

### Task 3.4: solve_lead Algorithm Documentation (DOC-11, SIM-019) [Medium]
**File:** `game/simulation/entities/ship_combat_engine.py`
**Tests:** `python -m py_compile game/simulation/entities/ship_combat_engine.py`

- [ ] Add usage-focused docstring to `solve_lead()` (line 47):
  ```
  Calculates intercept time for projectile to hit moving target.

  Usage:
      t = engine.solve_lead(pos, vel, t_pos, t_vel, p_speed)
      if t > 0:
          aim_point = target.position + target.velocity * t

  When to use: Projectile weapons, seeker missiles, AI aim prediction
  Returns 0 if no valid intercept exists.
  ```
- [ ] Add inline comment (line 72) explaining quadratic formula purpose:
  ```python
  # Quadratic solution: Find t where |D + V*t| = p_speed * t
  ```
- [ ] Verify: Run py_compile

**Notes:**

---

### Task 3.5: Ship Physics Comments (SIM-019) [Simple]
**File:** `game/simulation/entities/ship_physics.py`
**Tests:** `python -m py_compile game/simulation/entities/ship_physics.py`

- [ ] Add inline comment to `update_physics_movement()` (line 13) explaining thrust model:
  ```python
  # Thrust-based movement model:
  # acceleration = (thrust * K_THRUST) / mass^2
  # max_speed = (thrust * K_SPEED) / mass
  # Uses arcade physics: velocity direction always matches heading
  ```
- [ ] Verify: Run py_compile

**Notes:**

---

### Task 3.6: Create Component System Documentation (SIM-026) [Medium]
**File:** `docs/component_system.md` (NEW FILE)
**Tests:** N/A (markdown)

- [ ] Create new file with the following sections:
  - Overview of Component System
  - Component Lifecycle (Creation -> Attachment -> Simulation -> Damage)
  - Ability System overview (with key classes)
  - Modifier System overview (operations: add, multiply, set)
  - Key Classes reference table
  - Usage Examples (common operations)
- [ ] Link from docs/ARCHITECTURE.md if appropriate
- [ ] Verify: File renders correctly in markdown viewer

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
