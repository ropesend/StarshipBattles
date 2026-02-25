# Phase 5: Planet Report + Ship Stats Renderer [21 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Type planet_report_panel.py with `IPlanet`, ship_stats_renderer.py with `ICombatShip`/ShipDTO.

---

## Tasks

### Task 5.1: planet_report_panel.py remaining [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [ ] Add TYPE_CHECKING import: `from game.core.protocols import IPlanet, IFacility`
- [ ] Type `self.planet` as `'IPlanet'` where assigned/used
- [ ] Line 339: Replace `getattr(self.planet, 'resources', {})` → `self.planet.resources`
- [ ] Line 465: Replace `getattr(planet, 'owner_id', None)` → `planet.owner_id`
- [ ] Lines 478-491: Type facility/planet params in `compute_planet_production()` with `'IFacility'`/`'IPlanet'`
- [ ] Lines 510-511: `getattr(comp_def, 'abilities', {})` — **keep** (component registry objects are dict-like, not Protocol-typed)
- [ ] Verify: Run tests

**Notes:**

### Task 5.2: ship_stats_renderer.py [Medium]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [ ] Audit which functions receive ShipDTO vs simulation Ship
- [ ] For ShipDTO paths: type with `ShipDTO` (already has all fields)
- [ ] For simulation Ship paths: type with `'ICombatShip'` (add TYPE_CHECKING import from protocols)
- [ ] Replace: `getattr(ship, 'secondary_targets', [])` → `ship.secondary_targets` (Ship always has this after init)
- [ ] Replace: `getattr(ship, 'max_targets', N)` → `ship.max_targets` (Ship always has this after init)
- [ ] **Keep** `getattr` for dynamically-injected attributes:
  - `getattr(ship, 'crew_onboard', 0)` — set by ShipStatsCalculator.recalculate()
  - `getattr(ship, 'crew_required', 0)` — set by ShipStatsCalculator.recalculate()
  - `getattr(ship, 'shots_fired', 0)` — set during combat
  - `getattr(ship, 'shots_hit', 0)` — set during combat
- [ ] Keep target name access defensive (`current_target` may be None/dead reference)
- [ ] Verify: Run tests

**Notes:**

### Task 5.3: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Run: `pytest tests/unit/ui/panels/` — all pass
- [ ] Run: `pytest tests/unit/ui/ -n 4` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
