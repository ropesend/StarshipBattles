# Phase 3: Empire Panel + Race Config Typing [28 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Type-hint `race_config: RaceConfig` and `empire: IEmpire` in empire_panel_window.py, eliminating all 28 getattr calls. Highest single-file impact.

---

## Tasks

### Task 3.1: Add type hints to empire_panel_window.py [Medium]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add TYPE_CHECKING imports:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from game.strategy.data.race_config import RaceConfig
      from game.core.protocols import IEmpire
  ```
- [ ] Type `self.empire` as `'IEmpire'` where assigned
- [ ] Type `race_config` param in all 6 render methods:
  - `_render_species_card(race_config: 'RaceConfig')`
  - `_render_portrait_flag_row(race_config: 'RaceConfig')`
  - `_render_identity_section(race_config: 'RaceConfig')`
  - `_render_aptitudes_section(race_config: 'RaceConfig')`
  - `_render_environment_section(race_config: 'RaceConfig')`
  - `_render_descriptions_section(race_config: 'RaceConfig')`
- [ ] Line 213: Replace `getattr(self.empire, 'race_config', None)` → `self.empire.race_config` (Empire always has this field, may be None)
- [ ] Verify: Run tests

**Notes:**

### Task 3.2: Replace all 28 getattr calls with direct access [Medium]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Lines 277, 290: `getattr(self.empire, 'portrait_id', None)` → `self.empire.portrait_id`; `getattr(race_config, 'portrait_id', None)` → `race_config.portrait_id`
- [ ] Lines 319-325: 7 identity fields → direct `race_config.faction_name`, `race_config.race_name`, `race_config.government_type`, `race_config.government_organization`, `race_config.leader_title`, `race_config.leader_name`, `race_config.physical_type`
- [ ] Lines 354-362: 9 aptitude fields → direct `race_config.aptitude_strength`, `race_config.aptitude_intelligence`, `race_config.aptitude_constitution`, `race_config.aptitude_dexterity`, `race_config.aptitude_tolerance_other_species`, `race_config.aptitude_cooperation`, `race_config.aptitude_happiness`, `race_config.aptitude_population_growth`, `race_config.aptitude_conflict_tolerance`
- [ ] Lines 399-405: 7 environment fields → direct `race_config.gravity_ideal`, `race_config.gravity_tolerance`, `race_config.temperature_ideal`, `race_config.temperature_tolerance`, `race_config.water_ideal`, `race_config.water_tolerance`, `race_config.radiation_tolerance`
- [ ] Lines 433-434: 2 description fields → direct `race_config.bio_description`, `race_config.socio_description`
- [ ] Count: 28 getattr calls eliminated total
- [ ] Verify: Run tests

**Notes:**

### Task 3.3: Race panel type hints [Simple]
**Files:** `game/ui/panels/race_identity_panel.py`, `game/ui/panels/race_environment_panel.py`, `game/ui/panels/race_aptitudes_panel.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [ ] Add TYPE_CHECKING import for `RaceConfig` in each file
- [ ] Type `race_config` parameters with `'RaceConfig'`
- [ ] Replace getattr calls with direct access where race_config param is typed
- [ ] Verify: Run tests

**Notes:**

### Task 3.4: Run tests [Simple]
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
