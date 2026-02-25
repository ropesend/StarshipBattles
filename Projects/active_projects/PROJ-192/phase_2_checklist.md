# Phase 2: Controller + Target Evaluator Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace duck typing in `controller.py` (8 instances) and `target_evaluator.py` (5 instances including the armor HP bug fix).

---

## Tasks

### Task 2.1: `controller.py` grid entity typing (lines 125-128) [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [x] Import `is_projectile`, `IGridEntity` from `game.ai.protocols`
- [x] `_find_enemies_in_radius()` (L125-128): Replace `getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE` with `is_projectile(obj) and obj.type == AttackType.MISSILE`
- [x] Same block: Replace `getattr(obj, 'team_id', -1)` with `obj.team_id` (grid entities always have it)

**Notes:** Imported is_projectile; IProjectile protocol check now used for missile detection.

### Task 2.2: `controller.py` remaining getattr (lines 156, 199, 391, 411, 420) [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [x] `_build_capabilities_cache()` (L156): Replace `getattr(ship, 'id', None)` with `ship.name` (Ship uses `name` as identifier; `.id` doesn't exist on Ship)
- [x] `_score_and_sort_enemies()` (L199): Replace `getattr(e, 'position', None)` with `e.position` (IGridEntity guarantees it)
- [x] `_check_formation_integrity()` (L391): Replace `getattr(comp, 'current_hp', 1) < getattr(comp, 'max_hp', 1)` with `comp.current_hp < comp.max_hp`
- [x] `check_avoidance()` (L411): Replace `getattr(self.ship, 'ship', self.ship)` with `self.ship.ship if isinstance(self.ship, ShipControllableAdapter) else self.ship`
- [x] `check_avoidance()` (L420): Replace `getattr(obj, 'radius', 40)` with `obj.radius`

**Notes:** Also imported ShipControllableAdapter for isinstance check; simplified position distance calculation.

### Task 2.3: `target_evaluator.py` cleanup (5 instances) [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/test_target_evaluator_rules.py tests/unit/ai/target_evaluator/`

- [x] `_eval_mass_rule()` (L87): Replace `getattr(candidate, 'mass', 100)` with `candidate.mass` (PhysicsBody always has `.mass`)
- [x] `_eval_speed_rule()` (L118): Replace `getattr(candidate, 'velocity', Vector2(0,0)).length()` with `candidate.velocity.length()` (PhysicsBody always has `.velocity`)
- [x] `_eval_has_weapons_rule()` (L166): Replace `getattr(candidate, 'id', None)` with `getattr(candidate, 'name', None)` (Ships use `.name`; keep getattr for Projectiles which may lack `.name`)
- [x] `_eval_pdc_arc_rule()` (L194): Replace `getattr(candidate, 'type', '')` check with `is_projectile(candidate)` guard, then `candidate.type`
- [x] **Bug fix:** `_eval_least_armor_rule()` (L184): Replace `getattr(c, 'hp', 0)` with `c.current_hp` — Component has no `.hp`, this always returned 0

**Notes:** Bug fixed! The least_armor targeting rule was always evaluating to 0 because Component has `current_hp` not `hp`.

### Task 2.4: Update test mocks if needed [Simple]
- [x] Update mocks in `test_ai_controller_unit.py` that relied on getattr defaults
- [x] Update mocks in `test_target_evaluator_rules.py` — ensure mock components have `current_hp`
- [x] `pytest tests/unit/ai/ -v` — all pass

**Notes:**
- Deleted obsolete test: `test_component_missing_hp_attributes` (tested invalid getattr fallback)
- Deleted obsolete tests: `test_missing_mass_attribute`, `test_missing_velocity_attribute`
- Updated test_avoidance_skips_self_via_adapter to use spec=ShipControllableAdapter
- Updated mock missiles to satisfy IProjectile protocol (position, is_alive, team_id, radius, type)
- Updated cache tests to use `.name` instead of `.id` (Ship uses .name as identifier)
- Fixed 15+ test files for .id → .name change

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
