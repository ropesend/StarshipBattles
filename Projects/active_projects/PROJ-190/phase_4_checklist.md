# Phase 4: Replace Combat/Entity Duck Typing (~35 instances)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace combat and entity duck typing with protocol-typed access in targeting, battle state, weapon firing, physics, formation, and remaining files.

---

## Tasks

### Task 4.1: targeting_system.py [Medium]
**File:** `game/simulation/combat/targeting_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_targeting_system.py`

- [ ] Add import: `ICombatShip`, `IProjectile` from interfaces
- [ ] Line ~101: Replace `getattr(candidate, 'is_alive', True)` → `candidate.is_alive` (ICombatShip typed)
- [ ] Line ~104: Replace `getattr(candidate, 'team_id', -1)` → `candidate.team_id`
- [ ] Line ~152: Replace `getattr(candidate, 'is_alive', True)` → `candidate.is_alive`
- [ ] Line ~154: Replace `getattr(candidate, 'team_id', -1)` → `candidate.team_id`
- [ ] Line ~159: Replace `getattr(candidate, 'type', None)` → `candidate.type` (IProjectile typed)
- [ ] Line ~200: Replace `getattr(target, 'velocity', Vector2(0, 0))` → `target.velocity`
- [ ] Update function signatures to use `ICombatShip` / `IProjectile` types
- [ ] Verify: tests pass (expect some mock failures — defer to Phase 5)

**Notes:** May need to run Phase 5 mock updates concurrently if tests fail.

---

### Task 4.2: battle_state.py [Medium]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/test_battle_state.py`

- [ ] Add imports: `ICombatShip`, `IProjectile`, `IComponent`
- [ ] Line ~91: Replace `getattr(component, 'modifiers', [])` → `component.modifiers` (IComponent typed)
- [ ] Line ~296: Replace `hasattr(ship, 'current_target') and ship.current_target` → `ship.current_target is not None`
- [ ] Line ~298: Replace `getattr(ship.current_target, 'name', None)` → `ship.current_target.name`
- [ ] Line ~500: Replace `hasattr(proj, 'target') and proj.target` → `proj.target is not None`
- [ ] Line ~505: Replace `hasattr(proj_type, 'value')` → `isinstance(proj_type, AttackType)` or direct access
- [ ] Lines ~517-524: Replace all `getattr(proj, ...)` for projectile state → direct `proj.attr` (IProjectile typed)
- [ ] Lines ~697, 701: Replace `hasattr(engine, 'end_condition')` → direct access or typed check
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.3: weapon_firing_system.py [Simple]
**File:** `game/simulation/combat/weapon_firing_system.py`
**Tests:** `pytest tests/unit/simulation/combat/ -n 12`

- [ ] Line ~151: Replace `hasattr(comp, 'shots_fired')` → direct `comp.shots_fired` (initialized in Phase 2)
- [ ] Line ~249: Replace `getattr(comp, 'facing_angle', 0)` → access via weapon ability
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.4: ship_physics.py [Simple]
**File:** `game/simulation/entities/ship_physics.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [ ] Line ~28: Replace `getattr(self, 'is_thrusting', False)` → `self.is_thrusting`
- [ ] Line ~34: Replace `getattr(self, 'engine_throttle', 1.0)` → `self.engine_throttle`
- [ ] Line ~82: Replace `getattr(self, 'turn_throttle', 1.0)` → `self.turn_throttle`
- [ ] Verify these fields are initialized in `Ship.__init__` (should be — verify)
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.5: ship_formation.py [Simple]
**File:** `game/simulation/entities/ship_formation.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_formation.py`

- [ ] Add import: `IFormationHost` from interfaces
- [ ] Line ~63: Replace `hasattr(master, 'formation')` → `isinstance(master, IFormationHost)`
- [ ] Line ~70: Replace `hasattr(self.master, 'formation')` → `isinstance(self.master, IFormationHost)`
- [ ] Line ~91: Replace `hasattr(ship, 'formation')` → `isinstance(ship, IFormationHost)`
- [ ] Line ~109: Replace `hasattr(ship, 'formation')` → `isinstance(ship, IFormationHost)`
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.6: Remaining files [Simple]
**Files:** Multiple — see list below
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [ ] `ship_serialization.py` line ~67: Replace `getattr(ship, 'total_strategic_movement', 0)` → `ship.total_strategic_movement`
- [ ] `ship_serialization.py` lines ~70-71: Replace `getattr(ship, 'warp_max_tonnage', 0)` and `warp_energy_cost` → direct access
- [ ] `ship_combat_engine.py` line ~180: Replace `hasattr(ship, 'resources')` → `ship.resources is not None`
- [ ] `ship_combat_engine.py` line ~194: Replace `getattr(ship, 'repair_rate', 0)` → `ship.repair_rate`
- [ ] `ship_stat_querier.py` line ~130: Replace `getattr(ab, 'range', 0.0)` → `ab.range` (IWeaponAbility typed)
- [ ] `ship_stat_querier.py` line ~133: Replace `hasattr(ab, 'projectile_speed') and hasattr(ab, 'endurance')` → `isinstance(ab, ISeekerWeaponAbility)`
- [ ] `projectile_manager.py` line ~139: Replace `hasattr(p, 'source_weapon') and p.source_weapon` → `p.source_weapon is not None`
- [ ] `projectile_manager.py` line ~141: Replace `hasattr(weapon_ab, 'get_damage')` → `isinstance(weapon_ab, IWeaponAbility)`
- [ ] `projectile_manager.py` line ~174: Same as line 139
- [ ] `battle_engine.py` line ~425: Replace `getattr(attack, 'target', 'unknown')` → `attack.target`
- [ ] `ship_validator.py` line ~362: Replace `getattr(ab, 'max_amount', 0)` → `isinstance(ab, IResourceStorageAbility)` then `ab.max_amount`
- [ ] `battle_state_manager.py` lines ~137, 139: Replace `hasattr(state, 'mode')` / `hasattr(state, 'ships')` → typed check or direct access
- [ ] `projectile.py` line ~23: Replace `getattr(owner, 'team_id', -1)` → typed access or keep defensive (owner from external)
- [ ] `projectile.py` line ~143: Replace `hasattr(self.owner, 'combat_engine')` → `isinstance(self.owner, ICombatShip)`
- [ ] `ship.py` line ~576: Replace `getattr(comp, 'ship', None)` → `comp.ship` (IComponent typed)
- [ ] `component.py` line ~329: Replace `getattr(ability, 'trigger', None)` → isinstance check or direct access
- [ ] `stat_keys.py` line ~164: Replace `getattr(ability, base_attr, None)` → direct access or keep (meta-programming)
- [ ] Verify: `pytest tests/unit/simulation/ -n 12` — all pass (some failures expected, fixed in Phase 5)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `getattr`/`hasattr` calls remain in game/simulation/ (except formula_system.py, and legitimate meta-programming in abilities/base.py)
- [ ] `pytest tests/unit/simulation/ -n 12` — note any failures for Phase 5
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
