# Phase 5: ShipCombatEngine Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Break down combat responsibilities into focused strategies.

---

## Tasks

### Task 5.1: Extract TargetingSystem [Medium]
**File:** Create `game/simulation/combat/targeting_system.py`
**Issue:** CQ-005 - Targeting mixed with firing and damage
**Tests:** `pytest tests/unit/simulation/test_ship_combat_engine.py`

- [ ] Create `TargetingSystem` class with:
  - `select_target(ship, candidates) -> Optional[Ship]`
  - `find_valid_target(ship, primary, secondaries, weapon) -> Optional[Ship]`
  - `calculate_firing_solution(ship, target, weapon) -> Tuple[Vector2, Vector2]`
  - `solve_lead(target_pos, target_vel, ship_pos, projectile_speed) -> float`
- [ ] Move methods from `ship_combat_engine.py` lines 47-189, 298-354
- [ ] Verify: Target selection works in combat

**Notes:**

---

### Task 5.2: Extract DamageCalculator [Medium]
**File:** Create `game/simulation/combat/damage_calculator.py`
**Issue:** CQ-005 - Damage application complex
**Tests:** `pytest tests/unit/simulation/test_ship_combat_engine.py`

- [ ] Create `DamageCalculator` class with:
  - `apply_damage(ship, damage, damage_type) -> int`
  - `_process_armor_absorption(ship, damage) -> int`
  - `_process_shield_absorption(ship, damage) -> int`
  - `_damage_layer(ship, layer_type, damage) -> int`
- [ ] Move methods from `ship_combat_engine.py` lines 485-581
- [ ] Verify: Damage application works correctly

**Notes:**

---

### Task 5.3: Extract WeaponFiringSystem [Medium]
**File:** Create `game/simulation/combat/weapon_firing_system.py`
**Issue:** CQ-005 - Firing logic mixed with other concerns
**Tests:** `pytest tests/unit/simulation/test_ship_combat_engine.py`

- [ ] Create `WeaponFiringSystem` class with:
  - `fire_weapons(ship, targeting_system) -> List[Attack]`
  - `_process_weapon_fire(ship, component, target) -> Optional[Attack]`
  - `_create_attack(ship, target, weapon, solution) -> Attack`
  - `_create_seeker_projectile(ship, target, weapon) -> Attack`
  - `_create_standard_projectile(ship, target, weapon) -> Attack`
- [ ] Move methods from `ship_combat_engine.py` lines 195-479
- [ ] Verify: Weapons fire correctly

**Notes:**

---

### Task 5.4: Simplify ShipCombatEngine [Medium]
**File:** `game/simulation/entities/ship_combat_engine.py`
**Issue:** CQ-005 - Reduce to coordinator
**Tests:** `pytest tests/unit/simulation/test_ship_combat_engine.py`

- [ ] ShipCombatEngine now coordinates: TargetingSystem, DamageCalculator, WeaponFiringSystem
- [ ] Keep: `__init__`, `update_combat_cooldowns`, `_apply_repair`
- [ ] Should be ~200-250 lines
- [ ] Verify: Full combat integration works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
