# Phase 2: Replace getattr in Engines [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace ~53 `getattr(obj, 'attr', default)` calls with direct attribute access in engine/service/validator files.

---

## Tasks

### Task 2.1: empire_economy_calculator.py (14 instances) [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [x] L128: `getattr(empire, 'resource_pool', {})` → `empire.resource_pool`
- [x] L129: `getattr(empire, 'max_storage', {})` → `empire.max_storage`
- [x] L150: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [x] L152: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [x] L155: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [x] L158: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [x] L178: `getattr(colony, 'resources', {})` → `colony.resources`
- [x] L203: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [x] L205: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [x] L208: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [x] L211: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [x] L218: `getattr(empire, 'fleets', [])` → `empire.fleets`
- [x] L220: `getattr(fleet, 'ships', [])` → `fleet.ships`
- [x] L222: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [x] Run tests — fix any test failures from bare Mock() usage

**Notes:** 15 tests passed

### Task 2.2: harvesting_engine.py (10 instances) [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [x] L144: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [x] L146: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [x] L148: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [x] L159: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [x] L226: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [x] L238: `getattr(colony, 'facilities', [])` → `colony.facilities`
- [x] L240: `getattr(facility, 'is_operational', True)` → `facility.is_operational`
- [x] L259: `getattr(facility, 'design_data', {})` → `facility.design_data`
- [x] L322: `getattr(colony, 'resources', {})` → `colony.resources`
- [x] L345: `getattr(colony, 'name', 'unknown')` → `colony.name`
- [x] Run tests — fix any mock failures

**Notes:** 32 tests passed. Preserved L74, L213 (`getattr(comp_def, 'abilities', {})`) — these are legitimate dual-format access.

### Task 2.3: population_engine.py (5 instances) [Simple]
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [x] L52: `getattr(empire, 'colonies', [])` → `empire.colonies`
- [x] L64: `getattr(colony, 'populations', [])` → `colony.populations`
- [x] L95: `getattr(colony, 'max_population', 0)` → `colony.max_population`
- [x] L103: `getattr(race_config, 'aptitude_population_growth', 50)` → `race_config.aptitude_population_growth`
- [x] L141-146: `getattr(empire, 'race_config', None)` → `empire.race_config`; `getattr(race_config, 'race_id', '')` → `race_config.race_id`
- [x] Run tests

**Notes:** 15 tests passed

### Task 2.4: superweapon_order_processor.py (10 instances) [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/ -k superweapon`

- [x] L119: `getattr(empire, 'id', 0)` → `empire.id`
- [x] L194: `getattr(empire, 'id', 0)` → `empire.id`
- [x] L297: `getattr(empire, 'id', 0)` → `empire.id`
- [x] L372: `getattr(empire, 'id', 0)` → `empire.id`
- [x] L511: `getattr(empire, 'id', 0)` → `empire.id`
- [x] L580: `getattr(empire, 'id', 0)` → `empire.id`
- [x] L454: `getattr(empire, 'race_config', None)` → `empire.race_config`
- [x] L423: `getattr(primary_star, 'location', HexCoord(0, 0))` → `primary_star.location`
- [x] L563: `getattr(ship, 'name', None)` → `ship.name`
- [x] Run tests

**Notes:** 116 superweapon tests passed

### Task 2.5: Remaining engine/service/validator files (6 instances) [Simple]
**Files:** `fleet_order_processor.py`, `component_inspector.py`, `colonize_validator.py`, `action_time_resolver.py`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [x] `fleet_order_processor.py` L544: `getattr(empire, 'race_config', None)` → `empire.race_config`
- [x] `fleet_order_processor.py` L548-549: Simplify `hasattr(race_config, 'race_id') and isinstance(getattr(race_config, 'race_id', None), str)` → `race_config is not None and isinstance(race_config.race_id, str)`
- [x] `component_inspector.py` L107: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [x] `component_inspector.py` L154: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [x] `colonize_validator.py` L29: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [x] `colonize_validator.py` L244: `getattr(fleet, 'orders', [])` → `fleet.orders`
- [x] `action_time_resolver.py` L122: `getattr(ship, 'design_data', {})` → `ship.design_data`
- [x] Run tests

**Notes:** Deleted 2 obsolete duck typing edge case tests:
- `test_handles_ship_without_design_data` (testing Mock without design_data - no longer valid)
- `test_get_committed_no_orders_attribute` (testing Mock without orders - no longer valid)

### Task 2.6: Full test suite verification [Simple]
- [x] Run `pytest tests/ -n 12` — verify no regressions beyond pre-existing 6 failures

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` — baseline maintained (12702 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
