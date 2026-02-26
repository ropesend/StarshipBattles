# Phase 3: CompDef Abilities Centralization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-199 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Route all 8 `getattr(comp_def, 'abilities', {})` call sites through the canonical `get_component_abilities()` helper in `component_inspector.py`.

---

## Tasks

### Task 3.1: Harvesting Engine [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k harvest --testmon`

- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L74-75: Replace comment + `abilities = getattr(comp_def, 'abilities', {}) or {}` with `abilities = get_component_abilities(comp_def)`
- [ ] L212-213: Same replacement

**Notes:**

### Task 3.2: Resource Management Engine [Simple]
**File:** `game/strategy/engine/resource_management_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k resource --testmon`

- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L140-141: Replace comment + `abilities = getattr(comp_def, 'abilities', {}) or {}` with `abilities = get_component_abilities(comp_def)`

**Notes:**

### Task 3.3: Resupply Engine [Simple]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k resupply --testmon`

- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L158-159: Replace comment + `abilities = getattr(comp_def, 'abilities', {}) or {}` with `abilities = get_component_abilities(comp_def)`

**Notes:**

### Task 3.4: Planet [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/ -k planet --testmon`

- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L93-94: Replace comment + `abilities = getattr(comp_def, 'abilities', {}) or {}` with `abilities = get_component_abilities(comp_def)`
- [ ] Verify no circular import issues (planet.py in strategy/data, inspector in strategy/services)

**Notes:**

### Task 3.5: Planet Report Panel [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L515-516: Replace `abilities = getattr(comp_def, 'abilities', {}) or {}` with `abilities = get_component_abilities(comp_def)`

**Notes:**

### Task 3.6: ShipStatsCalculator — Abilities Access [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ --testmon`

- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L188-192: Replace 4-line isinstance/getattr block with `abilities = get_component_abilities(comp_def)`
- [ ] L336-339: Same replacement

**Notes:** Same file also has Phase 4 changes — do these first

### Task 3.7: Run targeted tests [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] All affected tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
