# Phase 1: Create ColonizePlanet Ability & Components

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Implement the ColonizePlanet ability class and define all 11 colony pod components in JSON

---

## Tasks

### Task 1.1: Create ColonizePlanet Ability Class [Simple]
**File:** `game/simulation/components/abilities/colonize.py` (new file)
**Tests:** `pytest tests/unit/simulation/components/abilities/test_colonize.py`

- [ ] Create new file `game/simulation/components/abilities/colonize.py`
- [ ] Import dependencies: `from typing import Dict, Any, List` and `from .base import Ability, AbilityLayer, AbilityScope`
- [ ] Define `ColonizePlanet` class extending `Ability`
- [ ] Set class attributes: `layer = AbilityLayer.STRATEGIC`, `allowed_scopes = [AbilityScope.SELF]`, `default_scope = AbilityScope.SELF`
- [ ] Implement `__init__(self, component, data: Dict[str, Any])`:
  - Call `super().__init__(component, data)`
  - Handle both dict format: `{"planet_type": "ICE_DWARF"}` and string shorthand: `"ICE_DWARF"`
  - Store `self.planet_type` as string (e.g., "CONTINENTAL", "ICE_DWARF")
- [ ] Implement `get_ui_rows(self) -> List[Dict[str, str]]`:
  - Return list with one row: `{'label': 'Colonizes', 'value': <formatted_planet_type>, 'color_hint': '#00FF00'}`
  - Format planet type: `self.planet_type.replace('_', ' ').title()`
- [ ] Verify: File saved and no syntax errors

**Notes:**

---

### Task 1.2: Register ColonizePlanet Ability [Simple]
**File:** `game/simulation/components/abilities/__init__.py`
**Tests:** Ability instantiation in next task's tests

- [ ] Open `game/simulation/components/abilities/__init__.py`
- [ ] Add import at top of file: `from .colonize import ColonizePlanet`
- [ ] Find `ABILITY_REGISTRY` dictionary (around line 30-60)
- [ ] Add entry: `"ColonizePlanet": ColonizePlanet,` (alphabetically sorted)
- [ ] Find `__all__` list (around line 100-130)
- [ ] Add entry: `"ColonizePlanet",` (alphabetically sorted)
- [ ] Verify: No import errors when loading abilities module

**Notes:**

---

### Task 1.3: Add 11 Colony Pod Components to JSON [Simple]
**File:** `data/components.json`
**Tests:** Component loading verification

- [ ] Open `data/components.json`
- [ ] Find appropriate location (near other infrastructure components, around line 1000+)
- [ ] Add component: `continental_colony_pod` with:
  - `"id": "continental_colony_pod"`, `"name": "Continental Colony Pod"`, `"type": "Colony"`
  - `"mass": 500`, `"hp": 300`, `"allowed_vehicle_types": ["Ship"]`, `"sprite_index": 210`
  - `"abilities": {"ColonizePlanet": "CONTINENTAL"}`
  - `"major_classification": "Infrastructure"`
  - `"resource_cost": {"Metals": 300, "Organics": 200, "Vapors": 100}`
- [ ] Add component: `arid_colony_pod` (same pattern, planet type "ARID", sprite_index 211)
- [ ] Add component: `pelagic_colony_pod` (planet type "PELAGIC", sprite_index 212)
- [ ] Add component: `magma_colony_pod` (planet type "MAGMA", sprite_index 213)
- [ ] Add component: `cryoplanet_colony_pod` (planet type "CRYOPLANET", sprite_index 214)
- [ ] Add component: `barren_colony_pod` (planet type "BARREN", sprite_index 215)
- [ ] Add component: `jovian_colony_pod` (planet type "JOVIAN", sprite_index 216, higher costs)
- [ ] Add component: `ice_giant_colony_pod` (planet type "ICE_GIANT", sprite_index 217, higher costs)
- [ ] Add component: `chthonian_colony_pod` (planet type "CHTHONIAN", sprite_index 218, higher costs)
- [ ] Add component: `ice_dwarf_colony_pod` (planet type "ICE_DWARF", sprite_index 219)
- [ ] Add component: `planetoid_colony_pod` (planet type "PLANETOID", sprite_index 220)
- [ ] Verify: JSON file is valid (no syntax errors, commas correct)
- [ ] Verify: All 11 planet types covered (CONTINENTAL, ARID, PELAGIC, MAGMA, CRYOPLANET, BARREN, JOVIAN, ICE_GIANT, CHTHONIAN, ICE_DWARF, PLANETOID)

**Notes:** Resource costs can be adjusted for balance - extreme environments (JOVIAN, ICE_GIANT, CHTHONIAN) should cost more

---

### Task 1.4: Write Unit Tests for ColonizePlanet Ability [Simple]
**File:** `tests/unit/simulation/components/abilities/test_colonize.py` (new file)
**Tests:** `pytest tests/unit/simulation/components/abilities/test_colonize.py -v`

- [ ] Create new file `tests/unit/simulation/components/abilities/test_colonize.py`
- [ ] Import pytest, Component class, and test fixtures
- [ ] Write test: `test_colonize_planet_ability_dict_format(mock_registries)`
  - Create component with ability: `"ColonizePlanet": {"planet_type": "ICE_DWARF"}`
  - Get ability: `component.get_ability('ColonizePlanet')`
  - Assert: `ability is not None`, `ability.planet_type == "ICE_DWARF"`
- [ ] Write test: `test_colonize_planet_ability_string_shorthand(mock_registries)`
  - Create component with ability: `"ColonizePlanet": "CONTINENTAL"`
  - Assert: `ability.planet_type == "CONTINENTAL"`
- [ ] Write test: `test_colonize_planet_ability_ui_display(mock_registries)`
  - Create component with ability for "ICE_DWARF"
  - Call `ability.get_ui_rows()`
  - Assert: Returns list with one dict containing 'label' and 'value' keys
  - Assert: Value contains formatted planet type (e.g., "Ice Dwarf")
- [ ] Write test: `test_all_11_planet_types_supported(mock_registries)`
  - Loop through all 11 planet types
  - Create component with ability for each type
  - Assert: Ability instantiates successfully for all types
- [ ] Run tests: `pytest tests/unit/simulation/components/abilities/test_colonize.py -v`
- [ ] Verify: All tests pass

**Notes:**

---

### Task 1.5: Verify Component Loading [Simple]
**File:** Manual verification
**Tests:** Run game startup or component registry test

- [ ] Run: `pytest tests/unit/builder/ -k component -v` (tests that load components.json)
- [ ] Verify: No errors loading component registry
- [ ] Verify: All 11 colony pod components appear in registry
- [ ] Optional: Launch game and open ship designer to verify pods appear in component list

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/simulation/components/abilities/test_colonize.py -v` - all tests pass
- [ ] Run `pytest tests/unit/builder/ -k component` - no errors loading components
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
