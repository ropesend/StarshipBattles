# Phase 6: Battle Panels [22 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix duck typing in battle_panels.py and battle_ui_service.py using `ICombatShip` Protocol and existing ShipDTO.

---

## Tasks

### Task 6.1: battle_panels.py [Medium]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/ -n 4`

- [x] Audit which code paths use ShipDTO vs raw simulation Ship
- [x] For ShipDTO paths: type with `ShipDTO`, access fields directly
- [x] For raw Ship paths: type with `'ICombatShip'` (add TYPE_CHECKING import)
- [x] Replace: `getattr(s, 'is_derelict', False)` → `s.is_derelict` (always present on Ship and in ICombatShip)
- [x] Replace projectile getattr calls where ProjectileDTO or concrete Projectile type is known
- [x] **Keep** scene capability checks (test_mode, is_battle_over) as-is — these are composite scene checks
- [x] Verify: Run tests

**Notes:**
- Replaced 6 instances of `getattr(s, 'is_derelict', False)` with direct `s.is_derelict` access
- Lines 115, 128, 149, 155, 489, 490 updated
- Kept projectile getattr calls (lines 352, 400, 406-407, 417-418, 433-434) for DTO compatibility
- Kept scene capability checks (test_mode, is_battle_over) as intended

### Task 6.2: battle_ui_service.py [Medium]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Add TYPE_CHECKING import: `from game.core.protocols import ICombatShip`
- [x] Type `_convert_ship(ship: 'ICombatShip')` parameter
- [x] Replace getattr calls where Ship always has the attribute:
  - `name`, `team_id`, `is_alive`, `is_derelict`, `hp`, `max_hp`
  - `layers`, `resources`, `current_target`
  - `secondary_targets`, `max_targets`, `total_defense_score`
- [x] **Keep** getattr for dynamically-injected attributes:
  - `getattr(ship, 'crew_onboard', 0)`
  - `getattr(ship, 'crew_required', 0)`
  - `getattr(ship, 'shots_fired', 0)`
  - `getattr(ship, 'shots_hit', 0)`
- [x] Type `_convert_projectile(proj)` with concrete Projectile type if feasible
- [x] Replace projectile getattr calls with direct access
- [x] Verify: Run tests

**Notes:**
- Added ICombatShip import to TYPE_CHECKING block
- Changed _convert_ship parameter type from 'Ship' to 'ICombatShip'
- Already using direct access for ship.resources, ship.layers, ship.current_target, ship.secondary_targets
- Kept getattr for: ship.id (not in Protocol), crew_onboard/crew_required (dynamically injected)
- Kept hasattr checks on target.name (targets are Optional[Any])
- Kept projectile getattr for DTO compatibility

### Task 6.3: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [x] Run: `pytest tests/unit/ui/ -n 4` — all pass

**Notes:**
- UI tests: 3148 passed
- Full suite: 12711 passed, 1 skipped

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
