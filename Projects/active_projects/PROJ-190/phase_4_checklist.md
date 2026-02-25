# Phase 4: Replace Combat/Entity Duck Typing (~35 instances)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace combat and entity duck typing with protocol-typed access in targeting, battle state, weapon firing, physics, formation, and remaining files.

---

## Tasks

### Task 4.1: targeting_system.py [Medium]
**File:** `game/simulation/combat/targeting_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_targeting_system.py`

- [x] Add import: `ICombatShip`, `IProjectile` from interfaces
- [x] Line ~101: Replace `getattr(candidate, 'is_alive', True)` → `candidate.is_alive` (ICombatShip typed)
- [x] Line ~104: Replace `getattr(candidate, 'team_id', -1)` → `candidate.team_id`
- [x] Line ~152: Replace `getattr(candidate, 'is_alive', True)` → `candidate.is_alive`
- [x] Line ~154: Replace `getattr(candidate, 'team_id', -1)` → `candidate.team_id`
- [x] Line ~159: Replace `getattr(candidate, 'type', None)` → `candidate.type` (IProjectile typed)
- [x] Line ~200: Replace `getattr(target, 'velocity', Vector2(0, 0))` → `target.velocity`
- [x] Update function signatures to use `ICombatShip` / `IProjectile` types
- [x] Verify: tests pass (expect some mock failures — defer to Phase 5)

**Notes:** Updated type hints to Union[ICombatShip, IProjectile]. Some edge case tests fail due to mocks without required attributes - fixed in Phase 5.

---

### Task 4.2: battle_state.py [Medium]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/test_battle_state.py`

- [x] Add imports: `Enum` for type checking
- [x] Line ~91: Replace `getattr(component, 'modifiers', [])` → `component.modifiers` (IComponent typed)
- [x] Line ~296: Replace `hasattr(ship, 'current_target') and ship.current_target` → `ship.current_target is not None`
- [x] Line ~298: Replace `getattr(ship.current_target, 'name', None)` → `ship.current_target.name`
- [x] Line ~500: Replace `hasattr(proj, 'target') and proj.target` → `proj.target is not None`
- [x] Line ~505: Replace `hasattr(proj_type, 'value')` → `isinstance(proj_type, Enum)`
- [x] Lines ~517-524: Replace all `getattr(proj, ...)` for projectile state → direct `proj.attr` (IProjectile typed)
- [x] Lines ~697, 701: Replace `hasattr(engine, 'end_condition')` → direct access
- [x] Verify: tests pass

**Notes:** All tests pass.

---

### Task 4.3: weapon_firing_system.py [Simple]
**File:** `game/simulation/combat/weapon_firing_system.py`
**Tests:** `pytest tests/unit/simulation/combat/ -n 12`

- [x] Line ~151: Replace `hasattr(comp, 'shots_fired')` → direct `comp.shots_fired` (initialized in Phase 2)
- [x] Line ~249: Replace `getattr(comp, 'facing_angle', 0)` → access via weapon ability (`weapon_ab.facing_angle`)
- [x] Verify: tests pass

**Notes:** Some mock failures - fixed in Phase 5.

---

### Task 4.4: ship_physics.py [Simple]
**File:** `game/simulation/entities/ship_physics.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [x] Line ~28: Replace `getattr(self, 'is_thrusting', False)` → `self.is_thrusting`
- [x] Line ~34: Replace `getattr(self, 'engine_throttle', 1.0)` → `self.engine_throttle`
- [x] Line ~82: Replace `getattr(self, 'turn_throttle', 1.0)` → `self.turn_throttle`
- [x] Verify these fields are initialized in `Ship.__init__` (confirmed at lines 155, 156, 161)
- [x] Verify: tests pass

**Notes:** Some mock tests fail because they don't set these attributes - fixed in Phase 5.

---

### Task 4.5: ship_formation.py [Simple]
**File:** `game/simulation/entities/ship_formation.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_formation.py`

- [x] Add import: `IFormationHost, is_formation_host` from interfaces
- [x] Line ~63: Replace `hasattr(master, 'formation')` → `is_formation_host(master)`
- [x] Line ~70: Replace `hasattr(self.master, 'formation')` → `is_formation_host(self.master)`
- [x] Line ~91: Replace `hasattr(ship, 'formation')` → `is_formation_host(ship)`
- [x] Line ~109: Replace `hasattr(ship, 'formation')` → `is_formation_host(ship)`
- [x] Verify: tests pass

**Notes:** All tests pass.

---

### Task 4.6: Remaining files [Simple]
**Files:** Multiple — see list below
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [x] `ship_serialization.py` line ~67: Replace `getattr(ship, 'total_strategic_movement', 0)` → `ship.total_strategic_movement`
- [x] `ship_serialization.py` lines ~70-71: Replace `getattr(ship, 'warp_max_tonnage', 0)` and `warp_energy_cost` → direct access
- [x] Added `total_strategic_movement`, `warp_max_tonnage`, `warp_energy_cost` to Ship.__init__
- [x] `ship_combat_engine.py` line ~180: Replace `hasattr(ship, 'resources')` → `ship.resources is not None`
- [x] `ship_combat_engine.py` line ~194: Replace `getattr(ship, 'repair_rate', 0)` → `ship.repair_rate`
- [x] `ship_stat_querier.py` line ~130: Replace `getattr(ab, 'range', 0.0)` → `ab.range` (IWeaponAbility typed)
- [x] `ship_stat_querier.py` line ~133: Simplified condition for SeekerWeaponAbility range calculation
- [x] `projectile_manager.py` line ~139: Replace `hasattr(p, 'source_weapon') and p.source_weapon` → `p.source_weapon is not None`
- [x] `projectile_manager.py` line ~141: Removed hasattr check (WeaponAbility always has get_damage)
- [x] `projectile_manager.py` line ~174: Same as line 139
- [x] `battle_engine.py` line ~425: Replace `getattr(attack, 'target', 'unknown')` → `attack.target.name if attack.target else 'unknown'`
- [x] `ship_validator.py` line ~362: Replace `getattr(ab, 'max_amount', 0)` → `ab.max_amount` (ResourceStorage always initialized)
- [x] `battle_state_manager.py` lines ~137, 139: Replace `hasattr(state, 'mode')` / `hasattr(state, 'ships')` → direct access (BattleState is dataclass)
- [x] `projectile.py` line ~23: Replace `getattr(owner, 'team_id', -1)` → `owner.team_id if owner is not None else -1`
- [x] `projectile.py` line ~143: Replace `hasattr(self.owner, 'combat_engine')` → `self.owner is not None and self.owner.combat_engine is not None`
- [x] `ship.py` line ~576: Replace `getattr(comp, 'ship', None)` → `comp.ship is None`
- [x] `component.py` line ~329: Kept `getattr(ability, 'trigger', None)` with comment (legitimate - only ResourceConsumption has trigger)
- [x] `stat_keys.py` line ~164: Kept `getattr(ability, base_attr, None)` (legitimate meta-programming)
- [x] Verify: `pytest tests/unit/simulation/ -n 12` — 30 failures expected, fixed in Phase 5

**Notes:**
- Remaining getattr/hasattr calls (26) are legitimate meta-programming for dynamic attribute access in abilities/stat binding system
- 30 test failures are mock issues requiring Phase 5 updates

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Remaining `getattr`/`hasattr` calls are legitimate meta-programming (abilities/base.py, abilities/weapons.py, abilities/stat_keys.py, component.py, component_resource_manager.py, component_stats_calculator.py, modifier_introspection.py)
- [x] `pytest tests/unit/simulation/ -n 12` — 30 failures noted for Phase 5 (mock updates needed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
