# Phase 6: Battle Panels [22 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix duck typing in battle_panels.py and battle_ui_service.py using `ICombatShip` Protocol and existing ShipDTO.

---

## Tasks

### Task 6.1: battle_panels.py [Medium]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Audit which code paths use ShipDTO vs raw simulation Ship
- [ ] For ShipDTO paths: type with `ShipDTO`, access fields directly
- [ ] For raw Ship paths: type with `'ICombatShip'` (add TYPE_CHECKING import)
- [ ] Replace: `getattr(s, 'is_derelict', False)` → `s.is_derelict` (always present on Ship and in ICombatShip)
- [ ] Replace projectile getattr calls where ProjectileDTO or concrete Projectile type is known
- [ ] **Keep** scene capability checks (test_mode, is_battle_over) as-is — these are composite scene checks
- [ ] Verify: Run tests

**Notes:**

### Task 6.2: battle_ui_service.py [Medium]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add TYPE_CHECKING import: `from game.core.protocols import ICombatShip`
- [ ] Type `_convert_ship(ship: 'ICombatShip')` parameter
- [ ] Replace getattr calls where Ship always has the attribute:
  - `name`, `team_id`, `is_alive`, `is_derelict`, `hp`, `max_hp`
  - `layers`, `resources`, `current_target`
  - `secondary_targets`, `max_targets`, `total_defense_score`
- [ ] **Keep** getattr for dynamically-injected attributes:
  - `getattr(ship, 'crew_onboard', 0)`
  - `getattr(ship, 'crew_required', 0)`
  - `getattr(ship, 'shots_fired', 0)`
  - `getattr(ship, 'shots_hit', 0)`
- [ ] Type `_convert_projectile(proj)` with concrete Projectile type if feasible
- [ ] Replace projectile getattr calls with direct access
- [ ] Verify: Run tests

**Notes:**

### Task 6.3: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Run: `pytest tests/unit/ui/ -n 4` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
