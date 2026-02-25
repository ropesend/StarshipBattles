# Phase 2: Controller + Target Evaluator Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace duck typing in `controller.py` (8 instances) and `target_evaluator.py` (5 instances including the armor HP bug fix).

---

## Tasks

### Task 2.1: `controller.py` grid entity typing (lines 125-128) [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [ ] Import `is_projectile`, `IGridEntity` from `game.ai.protocols`
- [ ] `_find_enemies_in_radius()` (L125-128): Replace `getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE` with `is_projectile(obj) and obj.type == AttackType.MISSILE`
- [ ] Same block: Replace `getattr(obj, 'team_id', -1)` with `obj.team_id` (grid entities always have it)

**Notes:**

### Task 2.2: `controller.py` remaining getattr (lines 156, 199, 391, 411, 420) [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [ ] `_build_capabilities_cache()` (L156): Replace `getattr(ship, 'id', None)` with `ship.name` (Ship uses `name` as identifier; `.id` doesn't exist on Ship)
- [ ] `_score_and_sort_enemies()` (L199): Replace `getattr(e, 'position', None)` with `e.position` (IGridEntity guarantees it)
- [ ] `_check_formation_integrity()` (L391): Replace `getattr(comp, 'current_hp', 1) < getattr(comp, 'max_hp', 1)` with `comp.current_hp < comp.max_hp`
- [ ] `check_avoidance()` (L411): Replace `getattr(self.ship, 'ship', self.ship)` with `self.ship.ship if isinstance(self.ship, ShipControllableAdapter) else self.ship`
- [ ] `check_avoidance()` (L420): Replace `getattr(obj, 'radius', 40)` with `obj.radius`

**Notes:**

### Task 2.3: `target_evaluator.py` cleanup (5 instances) [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/test_target_evaluator_rules.py tests/unit/ai/target_evaluator/`

- [ ] `_eval_mass_rule()` (L87): Replace `getattr(candidate, 'mass', 100)` with `candidate.mass` (PhysicsBody always has `.mass`)
- [ ] `_eval_speed_rule()` (L118): Replace `getattr(candidate, 'velocity', Vector2(0,0)).length()` with `candidate.velocity.length()` (PhysicsBody always has `.velocity`)
- [ ] `_eval_has_weapons_rule()` (L166): Replace `getattr(candidate, 'id', None)` with `getattr(candidate, 'name', None)` (Ships use `.name`; keep getattr for Projectiles which may lack `.name`)
- [ ] `_eval_pdc_arc_rule()` (L194): Replace `getattr(candidate, 'type', '')` check with `is_projectile(candidate)` guard, then `candidate.type`
- [ ] **Bug fix:** `_eval_least_armor_rule()` (L184): Replace `getattr(c, 'hp', 0)` with `c.current_hp` — Component has no `.hp`, this always returned 0

**Notes:**

### Task 2.4: Update test mocks if needed [Simple]
- [ ] Update mocks in `test_ai_controller_unit.py` that relied on getattr defaults
- [ ] Update mocks in `test_target_evaluator_rules.py` — ensure mock components have `current_hp`
- [ ] `pytest tests/unit/ai/ -v` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
