# Phase 4: ShipCombatMixin Elimination [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the ShipCombatMixin facade, redirect all callers to `ship.combat_engine.*`.

---

## Background
The ShipCombatMixin (`game/simulation/entities/ship_combat.py`) was created during PROJ-12 as a "thin facade" to maintain the `ship.method()` API while combat logic moved to ShipCombatEngine. Clean sheet approach: Ship is a data container, combat operations should go through `ship.combat_engine`.

## Key Method Mapping
| Mixin Method | Target | ShipCombatEngine Method |
|-------------|--------|------------------------|
| `ship.take_damage(damage, ...)` | Callers use engine | `ship.combat_engine.take_damage(damage, ...)` |
| `ship.fire_weapons(context)` | Internal only | `ship.combat_engine.fire_weapons(context)` |
| `ship.update_combat_cooldowns(dt)` | Internal only | `ship.combat_engine.update_combat_cooldowns(dt)` |
| `ship.solve_lead(target, ...)` | Multiple callers | `ship.combat_engine.solve_lead(target, ...)` |
| `ship._apply_repair(amount)` | Internal + tests | `ship.combat_engine._apply_repair(amount)` |

## Tasks

### Task 4.1: Inventory All Mixin Method Callers [Simple]
**Tests:** Research only
- [ ] Search for all callers of `.take_damage(` in production code (excluding mixin definition)
- [ ] Search for all callers of `.fire_weapons(` in production code
- [ ] Search for all callers of `.update_combat_cooldowns(` in production code
- [ ] Search for all callers of `.solve_lead(` in production code
- [ ] Search for all callers of `._apply_repair(` in production code
- [ ] Document complete caller list in Notes with file:line for each
**Notes:**

### Task 4.2: Update Production Callers of take_damage [Medium]
**Files:** `game/engine/collision.py`, `game/simulation/projectile_manager.py`, `game/simulation/combat/damage_calculator.py`, `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [ ] `game/engine/collision.py` - Change `target.take_damage(...)` → `target.combat_engine.take_damage(...)`
- [ ] `game/simulation/projectile_manager.py` - Change `s.take_damage(...)` → `s.combat_engine.take_damage(...)`
- [ ] `game/simulation/combat/damage_calculator.py` - Change `target.take_damage(...)` → `target.combat_engine.take_damage(...)` (if present)
- [ ] `game/strategy/data/ship_instance.py` - Change `ship.take_damage(...)` → `ship.combat_engine.take_damage(...)` (if present)
- [ ] Any other callers found in Task 4.1
- [ ] Run tests: `pytest tests/unit/combat/ tests/unit/simulation/ -x`
**Notes:**

### Task 4.3: Update Production Callers of solve_lead [Simple]
**Files:** `game/simulation/entities/projectile.py`, `game/simulation/combat/targeting_system.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [ ] `game/simulation/entities/projectile.py` - Change `ship.solve_lead(...)` → `ship.combat_engine.solve_lead(...)`
- [ ] `game/simulation/combat/targeting_system.py` - Change `ship.solve_lead(...)` → `ship.combat_engine.solve_lead(...)`
- [ ] Any other callers found in Task 4.1
- [ ] Run tests: `pytest tests/unit/combat/ -x`
**Notes:**

### Task 4.4: Update Ship.update() Internal Calls [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/combat/ -x`
- [ ] In `Ship.update()` method (~line 314): Change `self.update_combat_cooldowns(dt)` → `self.combat_engine.update_combat_cooldowns(dt)`
- [ ] In `Ship.update()` method (~line 318): Change `self.fire_weapons(context)` → `self.combat_engine.fire_weapons(context)`
- [ ] Any internal `self._apply_repair()` calls → `self.combat_engine._apply_repair()`
- [ ] Run tests: `pytest tests/unit/simulation/ tests/unit/combat/ -x`
**Notes:**

### Task 4.5: Update Test Callers [Medium]
**Files:** Multiple test files
**Tests:** `pytest tests/ --testmon`
- [ ] Search all test files for `.take_damage(`, `.fire_weapons(`, `.solve_lead(`, `.update_combat_cooldowns(`, `._apply_repair(`
- [ ] Update each test caller to use `.combat_engine.method()` pattern
- [ ] Pay special attention to mock/patch targets - they need to point to ShipCombatEngine
- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** Some tests may patch `Ship.take_damage` - these patches need to target `ShipCombatEngine.take_damage` instead.

### Task 4.6: Move combat_engine Property to Ship Class [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [ ] Copy the `combat_engine` property from `ship_combat.py` into the Ship class body in `ship.py`
- [ ] Ensure the lazy initialization pattern is preserved
- [ ] Verify import: `from game.simulation.entities.ship_combat_engine import ShipCombatEngine` stays lazy (inside property)
- [ ] Run tests: `pytest tests/ -x`
**Notes:** The property must be moved BEFORE the mixin is removed.

### Task 4.7: Remove ShipCombatMixin [Medium]
**File:** `game/simulation/entities/ship_combat.py`, `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [ ] In `ship.py`: Remove `ShipCombatMixin` from Ship's parent class list
- [ ] In `ship.py`: Remove `from game.simulation.entities.ship_combat import ShipCombatMixin` import
- [ ] Verify `ship_combat.py` can be deleted (no other imports from it)
- [ ] Delete `game/simulation/entities/ship_combat.py` entirely
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** This is the culmination of Phase 4. Only do after all callers are updated.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
- [ ] `ship_combat.py` is deleted
- [ ] No remaining `ShipCombatMixin` references in codebase
- [ ] All callers use `ship.combat_engine.*` pattern
