# Phase 5: ShipCombatMixin Elimination [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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
- [x] Search for `.take_damage(` in production code - document all callers with file:line
- [x] Search for `.fire_weapons(` in production code
- [x] Search for `.update_combat_cooldowns(` in production code
- [x] Search for `.solve_lead(` in production code
- [x] Search for `.die(` on ship objects in production code
- [x] Document complete caller list in Notes
**Notes:**
- `take_damage`: collision.py:129,163,164,167,168,171,172 (7), projectile_manager.py:110,123 (2), damage_calculator.py:126 (1), ship_instance.py:641 (1 ship caller; line 651 is comp.take_damage — Component, skip)
- `fire_weapons`: ship.py:269 (self call in update())
- `update_combat_cooldowns`: ship.py:265 (self call in update())
- `solve_lead`: projectile.py:140 (self.owner.solve_lead), targeting_system.py:209 (self.solve_lead — TargetingSystem own method, skip)
- `die()`: Never called from production code. Defined in mixin but unused.
- `_apply_repair`: Only called by combat_engine internally (ship_combat_engine.py:195). Mixin delegation unused.

### Task 5.2: Relocate die() Method [Simple]
**Files:** `game/simulation/entities/ship_combat.py`, `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [x] Read `die()` implementation in `ship_combat.py` (~lines 150-159) - understand its logic
- [x] Copy `die()` method into Ship class body in `ship.py` (keep same signature and logic)
- [x] Verify any imports needed by `die()` are available in `ship.py`
- [x] Run tests: `pytest tests/unit/combat/ -x`
**Notes:** `die()` has real logic (not just delegation) - velocity reset, recalculate_stats. Must be in Ship class.

### Task 5.3: Update Production Callers of take_damage [Medium]
**Files:** `game/engine/collision.py`, `game/simulation/projectile_manager.py`, `game/simulation/combat/damage_calculator.py`, `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [x] `game/engine/collision.py:129,163,164,167,168,171,172` - Change `target.take_damage(...)` / `s.take_damage(...)` → `.combat_engine.take_damage(...)`
- [x] `game/simulation/projectile_manager.py:110` - Change `s.take_damage(...)` → `.combat_engine.take_damage(...)`
- [x] `game/simulation/projectile_manager.py:123` - NOT changed: `t_missile.take_damage()` is on Projectile, not Ship
- [x] `game/simulation/combat/damage_calculator.py:126` - NOT changed: `target.take_damage()` is on Component, not Ship
- [x] `game/strategy/data/ship_instance.py:641` - Change → `.combat_engine.take_damage(...)` (line 651 is Component, skip)
- [x] Run tests: `pytest tests/unit/combat/ tests/unit/simulation/ -x`

### Task 5.4: Update Production Callers of solve_lead [Simple]
**Files:** `game/simulation/entities/projectile.py`, `game/simulation/combat/targeting_system.py`
**Tests:** `pytest tests/unit/combat/ -x`
- [x] `game/simulation/entities/projectile.py:140` - `self.owner.solve_lead(...)` → `self.owner.combat_engine.solve_lead(...)`
- [x] `game/simulation/combat/targeting_system.py:209` - This is TargetingSystem's own method, not a Ship mixin call. Skipped.
- [x] Run tests: `pytest tests/unit/combat/ -x`

### Task 5.5: Update Ship.update() Internal Calls [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/combat/ -x`
- [x] `self.update_combat_cooldowns()` → `self.combat_engine.update_combat_cooldowns()`
- [x] `self.fire_weapons(context)` → `self.combat_engine.fire_weapons(context)`
- [x] Run tests: `pytest tests/unit/simulation/ tests/unit/combat/ -x`

### Task 5.6: Update Test Callers [Medium]
**Files:** 15+ test files (40+ occurrences)
**Tests:** `pytest tests/ --testmon`
- [x] Search all test files for `.take_damage(`, `.fire_weapons(`, `.solve_lead(`, `.update_combat_cooldowns(`, `._apply_repair(`
- [x] Update each test caller to use `.combat_engine.method()` pattern
- [x] Check for mock/patch targets: `Ship.take_damage` patches need to target `ShipCombatEngine.take_damage`
- [x] Update `tests/unit/simulation/ship_combat_engine/` tests if they reference mixin methods
- [x] Run tests: `pytest tests/ --testmon`
**Notes:** Updated 15+ test files. Key patterns: patch.object targets changed, MagicMock(spec=[]) needed explicit combat_engine attribute, assertion paths updated.

### Task 5.7: Move combat_engine Property to Ship Class [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [x] Copy the `combat_engine` property from `ship_combat.py` into Ship class body
- [x] Preserve the lazy initialization pattern (import inside property getter)
- [x] Run tests: `pytest tests/ -x`
**Notes:** Property must be moved BEFORE the mixin is removed.

### Task 5.8: Remove ShipCombatMixin and Delete File [Medium]
**Files:** `game/simulation/entities/ship_combat.py`, `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [x] In `ship.py`: Remove `from game.simulation.entities.ship_combat import ShipCombatMixin`
- [x] In `ship.py`: Remove `ShipCombatMixin` from Ship's parent class list
- [x] Verify no other files import from `ship_combat.py`
- [x] Delete `game/simulation/entities/ship_combat.py`
- [x] Run full test suite: `pytest tests/ -x` → 6248 passed, 0 failed
**Notes:** This is the culmination. Only proceeded after ALL callers were updated.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
- [x] `ship_combat.py` deleted
- [x] No remaining `ShipCombatMixin` references
