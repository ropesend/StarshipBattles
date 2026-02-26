# Phase 5: Planet Report + Ship Stats Renderer [21 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Type planet_report_panel.py with `IPlanet`, ship_stats_renderer.py with `ICombatShip`/ShipDTO.

---

## Tasks

### Task 5.1: planet_report_panel.py remaining [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [x] Add TYPE_CHECKING import: `from game.core.protocols import IPlanet, IFacility`
- [x] Type `self.planet` as `'IPlanet'` where assigned/used
- [x] Line 339: Replace `getattr(self.planet, 'resources', {})` → `self.planet.resources`
- [x] Line 465: Replace `getattr(planet, 'owner_id', None)` → `planet.owner_id`
- [x] Lines 478-491: Type facility/planet params in `compute_planet_production()` with `'IFacility'`/`'IPlanet'`
- [x] Lines 510-511: `getattr(comp_def, 'abilities', {})` — **kept** (component registry objects are dict-like, not Protocol-typed)
- [x] Verify: Run tests

**Notes:**
- Added TYPE_CHECKING import for IPlanet, IFacility
- Typed compute_planet_production with IPlanet parameter
- Added inline type hint `facility: 'IFacility'` in loop
- Replaced 4 getattr calls with direct Protocol access

### Task 5.2: ship_stats_renderer.py [Medium]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [x] Audit which functions receive ShipDTO vs simulation Ship
- [x] For ShipDTO paths: type with `ShipDTO` (already has all fields)
- [x] For simulation Ship paths: type with `'ICombatShip'` (add TYPE_CHECKING import from protocols)
- [x] Replace: `getattr(ship, 'secondary_targets', [])` → `ship.secondary_targets` (Ship always has this after init)
- [x] Replace: `getattr(ship, 'max_targets', N)` → `ship.max_targets` (Ship always has this after init)
- [x] **Kept** `getattr` for dynamically-injected attributes:
  - `getattr(ship, 'crew_onboard', 0)` — set by ShipStatsCalculator.recalculate()
  - `getattr(ship, 'crew_required', 0)` — set by ShipStatsCalculator.recalculate()
  - `getattr(ship, 'shots_fired', 0)` — set during combat
  - `getattr(ship, 'shots_hit', 0)` — set during combat
- [x] Kept target name access defensive (`current_target` may be None/dead reference)
- [x] Verify: Run tests

**Notes:**
- Added TYPE_CHECKING import for ICombatShip
- Typed 6 functions with ICombatShip parameter
- Replaced 2 getattr (secondary_targets, max_targets) with direct access
- Replaced hasattr(ship, 'resources') with direct check (resources can be None per Protocol)
- Kept 4 getattr for dynamically-injected attributes (crew_onboard, crew_required, shots_fired, shots_hit)
- Kept 2 getattr on target name (target may be dead reference or varying type)

### Task 5.3: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [x] Run: `pytest tests/unit/ui/panels/` — all pass (332 passed)
- [x] Run: `pytest tests/unit/ui/ -n 4` — all pass (3148 passed)

**Notes:**
- Full suite: 12711 passed, 1 skipped

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
