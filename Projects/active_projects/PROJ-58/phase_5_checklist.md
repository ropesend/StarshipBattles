# Phase 5: ShipCombatMixin Elimination [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Redirect all callers to `ship.combat_engine.*`, relocate `die()` method, delete mixin file.

---

## Method Mapping
| Mixin Method | Replacement |
|-------------|------------|
| `ship.take_damage(damage)` | `ship.combat_engine.take_damage(damage)` |
| `ship.fire_weapons(context)` | `ship.combat_engine.fire_weapons(context)` |
| `ship.update_combat_cooldowns()` | `ship.combat_engine.update_combat_cooldowns()` |
| `ship.solve_lead(pos, vel, t_pos, t_vel, speed)` | `ship.combat_engine.solve_lead(pos, vel, t_pos, t_vel, speed)` |
| `ship._apply_repair(amount)` | `ship.combat_engine._apply_repair(amount)` |
| `ship.die()` | Relocated to Ship class body or ShipCombatEngine |

## Tasks

### Task 5.1: Inventory All Callers (Verification) [Simple]
**Tests:** Research only
- [ ] Search for `.take_damage(` in production code - document all callers with file:line
- [ ] Search for `.fire_weapons(` in production code
- [ ] Search for `.update_combat_cooldowns(` in production code
- [ ] Search for `.solve_lead(` in production code
- [ ] Search for `.die(` on ship objects in production code
- [ ] Document complete caller list in Notes
**Notes:**

### Task 5.2: Relocate die() Method [Simple]
**Files:** `game/simulation/entities/ship_combat.py`, `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [ ] Read `die()` implementation in `ship_combat.py` (~lines 150-159) - understand its logic
- [ ] Copy `die()` method into Ship class body in `ship.py` (keep same signature and logic)
- [ ] Verify any imports needed by `die()` are available in `ship.py`
- [ ] Run tests: `pytest tests/unit/combat/ -x`
**Notes:** `die()` has real logic (not just delegation) - velocity reset, recalculate_stats. Must be in Ship class.

### Task 5.3: Update Production Callers of take_damage [Medium]
**Files:** `game/engine/collision.py`, `game/simulation/projectile_manager.py`, `game/simulation/combat/damage_calculator.py`, `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [ ] `game/engine/collision.py:129,163,164,167,168,171,172` - Change `target.take_damage(...)` / `s.take_damage(...)` → `.combat_engine.take_damage(...)`
- [ ] `game/simulation/projectile_manager.py:110,123` - Change `s.take_damage(...)` / `t_missile.take_damage(...)` → `.combat_engine.take_damage(...)`
- [ ] `game/simulation/combat/damage_calculator.py:126` - Change `target.take_damage(...)` → `target.combat_engine.take_damage(...)`
- [ ] `game/strategy/data/ship_instance.py:641,651` - Change → `.combat_engine.take_damage(...)`
- [ ] Run tests: `pytest tests/unit/combat/ tests/unit/simulation/ -x`

### Task 5.4: Update Production Callers of solve_lead [Simple]
**Files:** `game/simulation/entities/projectile.py`, `game/simulation/combat/targeting_system.py`
**Tests:** `pytest tests/unit/combat/ -x`
- [ ] `game/simulation/entities/projectile.py:140` - `self.owner.solve_lead(...)` → `self.owner.combat_engine.solve_lead(...)`
- [ ] `game/simulation/combat/targeting_system.py:209` - `self.solve_lead(...)` → check if this is called on the engine already or needs updating
- [ ] Run tests: `pytest tests/unit/combat/ -x`

### Task 5.5: Update Ship.update() Internal Calls [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/combat/ -x`
- [ ] Line 314: `self.update_combat_cooldowns()` → `self.combat_engine.update_combat_cooldowns()`
- [ ] Line 318: `self.fire_weapons(context)` → `self.combat_engine.fire_weapons(context)`
- [ ] Run tests: `pytest tests/unit/simulation/ tests/unit/combat/ -x`

### Task 5.6: Update Test Callers [Medium]
**Files:** 15+ test files (40+ occurrences)
**Tests:** `pytest tests/ --testmon`
- [ ] Search all test files for `.take_damage(`, `.fire_weapons(`, `.solve_lead(`, `.update_combat_cooldowns(`, `._apply_repair(`
- [ ] Update each test caller to use `.combat_engine.method()` pattern
- [ ] Check for mock/patch targets: `Ship.take_damage` patches need to target `ShipCombatEngine.take_damage`
- [ ] Update `tests/unit/simulation/ship_combat_engine/` tests if they reference mixin methods
- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** Mock patches are the biggest risk - any `@patch('game.simulation.entities.ship.Ship.take_damage')` must change.

### Task 5.7: Move combat_engine Property to Ship Class [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [ ] Copy the `combat_engine` property from `ship_combat.py` into Ship class body
- [ ] Preserve the lazy initialization pattern (import inside property getter)
- [ ] Run tests: `pytest tests/ -x`
**Notes:** Property must be moved BEFORE the mixin is removed.

### Task 5.8: Remove ShipCombatMixin and Delete File [Medium]
**Files:** `game/simulation/entities/ship_combat.py`, `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [ ] In `ship.py`: Remove `ShipCombatMixin` from Ship's parent class list
- [ ] In `ship.py`: Remove `from game.simulation.entities.ship_combat import ShipCombatMixin`
- [ ] Verify no other files import from `ship_combat.py`
- [ ] Delete `game/simulation/entities/ship_combat.py`
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** This is the culmination. Only proceed after ALL callers are updated.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
- [ ] `ship_combat.py` deleted
- [ ] No remaining `ShipCombatMixin` references
