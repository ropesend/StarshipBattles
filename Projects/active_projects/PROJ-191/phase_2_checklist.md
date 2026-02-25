# Phase 2: Replace getattr in Engines [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace ~53 `getattr(obj, 'attr', default)` calls with direct attribute access in engine/service/validator files.

---

## Tasks

### Task 2.1: empire_economy_calculator.py (14 instances) [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [ ] L128: `getattr(empire, 'resource_pool', {})` → `empire.resource_pool`
- [ ] L129: `getattr(empire, 'max_storage', {})` → `empire.max_storage`
- [ ] L150: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [ ] L152: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [ ] L155: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [ ] L158: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [ ] L178: `getattr(colony, 'resources', {})` → `colony.resources`
- [ ] L203: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [ ] L205: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [ ] L208: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [ ] L211: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [ ] L218: `getattr(empire, 'fleets', [])` → `empire.fleets`
- [ ] L220: `getattr(fleet, 'ships', [])` → `fleet.ships`
- [ ] L222: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [ ] Run tests — fix any test failures from bare Mock() usage

**Notes:**

### Task 2.2: harvesting_engine.py (10 instances) [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] L144: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [ ] L146: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [ ] L148: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [ ] L159: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [ ] L226: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [ ] L238: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [ ] L240: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [ ] L259: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [ ] L322: `getattr(colony, 'resources', {})` → `colony.resources`
- [ ] L345: `getattr(colony, 'name', 'unknown')` → `colony.name`
- [ ] Run tests — fix any mock failures

**Notes:** Do NOT touch L74, L213 (`getattr(comp_def, 'abilities', {})`) — these are legitimate dual-format access.

### Task 2.3: population_engine.py (5 instances) [Simple]
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [ ] L52: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [ ] L64: `getattr(colony, 'populations', [])` → `colony.populations`
- [ ] L95: `getattr(colony, 'max_population', 0)` → `colony.max_population`
- [ ] L103: `getattr(race_config, 'aptitude_population_growth', 50)` → `race_config.aptitude_population_growth`
- [ ] L141-146: `getattr(empire, 'race_config', None)` → `empire.race_config`; `getattr(race_config, 'race_id', '')` → `race_config.race_id`
- [ ] Run tests

**Notes:**

### Task 2.4: superweapon_order_processor.py (10 instances) [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/ -k superweapon`

- [ ] L119: `getattr(empire, 'id', 0)` → `empire.id`
- [ ] L194: `getattr(empire, 'id', 0)` → `empire.id`
- [ ] L297: `getattr(empire, 'id', 0)` → `empire.id`
- [ ] L372: `getattr(empire, 'id', 0)` → `empire.id`
- [ ] L511: `getattr(empire, 'id', 0)` → `empire.id`
- [ ] L580: `getattr(empire, 'id', 0)` → `empire.id`
- [ ] L454: `getattr(empire, 'race_config', None)` → `empire.race_config`
- [ ] L423: `getattr(primary_star, 'location', HexCoord(0, 0))` → `primary_star.location`
- [ ] L563: `getattr(ship, 'name', None)` → `ship.name`
- [ ] Run tests

**Notes:**

### Task 2.5: Remaining engine/service/validator files (6 instances) [Simple]
**Files:** `fleet_order_processor.py`, `component_inspector.py`, `colonize_validator.py`, `action_time_resolver.py`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] `fleet_order_processor.py` L544: `getattr(empire, 'race_config', None)` → `empire.race_config`
- [ ] `fleet_order_processor.py` L548-549: Simplify `hasattr(race_config, 'race_id') and isinstance(getattr(race_config, 'race_id', None), str)` → `race_config is not None and isinstance(race_config.race_id, str)`
- [ ] `component_inspector.py` L107: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [ ] `component_inspector.py` L154: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [ ] `colonize_validator.py` L29: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [ ] `colonize_validator.py` L244: `getattr(fleet, 'orders', [])` → `fleet.orders`
- [ ] `action_time_resolver.py` L122: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [ ] Run tests

**Notes:**

### Task 2.6: Full test suite verification [Simple]
- [ ] Run `pytest tests/ -n 12` — verify no regressions beyond pre-existing 6 failures

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` — baseline maintained (12699+ passed)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
