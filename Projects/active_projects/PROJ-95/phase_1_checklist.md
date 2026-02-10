# Phase 1: Add ResourceType Constants

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-95 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create `ResourceType` constants class and replace all magic strings `'fuel'`, `'energy'`, `'ammo'` in production and test code. No behavioral changes.

---

## Tasks

### Task 1.1: Create ResourceType class [Simple]
**File:** `game/core/constants.py`
**Tests:** `python -c "from game.core.constants import ResourceType"`

- [ ] Add `ResourceType` class after `PLANET_RESOURCES` (after line 91):
  ```python
  class ResourceType:
      """Ship resource type constants."""
      FUEL = 'fuel'
      ENERGY = 'energy'
      AMMO = 'ammo'

      @classmethod
      def all(cls) -> list:
          """Return all resource types in display order."""
          return [cls.FUEL, cls.ENERGY, cls.AMMO]
  ```
- [ ] Add `'ResourceType'` to `__all__` list (line 3-17)
- [ ] Verify: `python -c "from game.core.constants import ResourceType; print(ResourceType.all())"`

**Notes:**

---

### Task 1.2: Replace magic strings in core layer [Simple]
**Files:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/ --testmon`

- [ ] Add import: `from game.core.constants import ResourceType` at top
- [ ] Replace `_get_default_resources()` dict keys (lines 23-27):
  ```python
  # OLD:
  return {
      'fuel': {'id': 'fuel'},
      'energy': {'id': 'energy'},
      'ammo': {'id': 'ammo'},
  }
  # NEW:
  return {
      ResourceType.FUEL: {'id': ResourceType.FUEL},
      ResourceType.ENERGY: {'id': ResourceType.ENERGY},
      ResourceType.AMMO: {'id': ResourceType.AMMO},
  }
  ```
- [ ] Verify: `python -c "from game.core.resources import load_resources_data; print(load_resources_data())"`

**Notes:**

---

### Task 1.3: Replace magic strings in simulation layer [Medium]
**Files:** ~8 files in `game/simulation/`
**Tests:** `pytest tests/unit/simulation/ --testmon`

- [ ] `game/simulation/entities/ship_stats.py` (~21 occurrences) -- add import, replace all `'fuel'`, `'energy'`, `'ammo'` string literals
- [ ] `game/simulation/entities/ship_serialization.py` (~10 occurrences) -- add import, replace all
- [ ] `game/simulation/entities/combat_endurance.py` (~10 occurrences) -- add import, replace all
- [ ] `game/simulation/components/abilities/resources.py` (~7 occurrences) -- add import, replace all
- [ ] `game/simulation/systems/resource_manager.py` (~5 occurrences) -- add import, replace all
- [ ] `game/simulation/systems/battle_engine.py` (~1 occurrence) -- add import, replace
- [ ] `game/simulation/entities/ship_combat_engine.py` (~1 occurrence) -- add import, replace
- [ ] Verify: `python -c "from game.simulation.entities.ship_stats import ShipStats"` (no import errors)
- [ ] Run: `pytest tests/unit/simulation/ --testmon`

**Notes:** ship_stats.py has the highest count (21). Work through each file carefully. Skip occurrences in docstrings/comments.

---

### Task 1.4: Replace magic strings in strategy layer [Medium]
**Files:** ~6 files in `game/strategy/`
**Tests:** `pytest tests/unit/strategy/ --testmon`

- [ ] `game/strategy/data/ship_resource_manager.py` (~8 occurrences after PROJ-94) -- add import, replace all
- [ ] `game/strategy/engine/resupply_engine.py` (~10 occurrences) -- add import, replace all
- [ ] `game/strategy/data/planet.py` (~6 occurrences) -- add import, replace all
- [ ] `game/strategy/data/fleet_resource_aggregator.py` (~4 occurrences after PROJ-94) -- add import, replace all
- [ ] `game/strategy/data/ship_instance.py` (~2 occurrences, docstrings) -- add import, replace
- [ ] `game/strategy/services/ship_stats_calculator.py` (~2 occurrences) -- add import, replace
- [ ] Verify: no import errors across strategy layer
- [ ] Run: `pytest tests/unit/strategy/ --testmon`

**Notes:** Occurrence counts assume PROJ-94 already deleted dead type-specific methods. If PROJ-94 not yet complete, counts will be higher.

---

### Task 1.5: Replace magic strings in UI layer [Medium]
**Files:** ~7 files in `game/ui/`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [ ] `game/ui/screens/builder/stats_config.py` (~9 occurrences) -- add import, replace all
- [ ] `game/ui/screens/fleet_report_filters.py` (~5 occurrences) -- add import, replace all
- [ ] `game/ui/panels/ship_stats_renderer.py` (~6 occurrences) -- add import, replace all
- [ ] `game/ui/panels/ship_detail_panel.py` (~3 occurrences) -- add import, replace all
- [ ] `game/ui/renderer/game_renderer.py` (~5 occurrences) -- add import, replace all
- [ ] `game/ui/screens/battle_screen.py` (~1 occurrence) -- add import, replace
- [ ] `game/ui/interfaces/battle_ui.py` (~2 occurrences, docstrings) -- add import, replace
- [ ] Run: `pytest tests/unit/ui/ --testmon`

**Notes:**

---

### Task 1.6: Bulk replace in test files [Medium]
**Files:** ~163 test files in `tests/`
**Tests:** `pytest tests/ -n 12`

- [ ] Strategy: Use search/replace to change `'fuel'` to `ResourceType.FUEL`, `'energy'` to `ResourceType.ENERGY`, `'ammo'` to `ResourceType.AMMO` across all test files
- [ ] Add `from game.core.constants import ResourceType` import to every affected test file
- [ ] Be careful with: string literals in `assert` messages, docstrings, test names (don't replace those)
- [ ] Run: `pytest tests/ -n 12` to catch any breakage
- [ ] Fix any import errors or missed replacements

**Notes:** This is the highest-volume task (~1037 occurrences). Consider doing in batches by test directory (unit/simulation, unit/strategy, unit/ui, integration, simulation_tests).

---

### Task 1.7: Verification [Simple]
- [ ] Grep: No bare `'fuel'` in `game/` (except ResourceType.FUEL definition and docstring examples)
- [ ] Grep: No bare `'energy'` in `game/` (except ResourceType.ENERGY definition and docstring examples)
- [ ] Grep: No bare `'ammo'` in `game/` (except ResourceType.AMMO definition and docstring examples)
- [ ] Full test suite: `pytest tests/ -n 12` -- all pass
- [ ] Record test count

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
