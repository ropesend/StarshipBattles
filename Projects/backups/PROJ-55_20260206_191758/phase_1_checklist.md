# Phase 1: Create ColonizePlanet Ability & Components

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Implement the ColonizePlanet ability class and define all 11 colony pod components in JSON

---

## Tasks

### Task 1.1: Create ColonizePlanet Ability Class [Simple]
**File:** `game/simulation/components/abilities/colonize.py` (new file)
**Tests:** `pytest tests/unit/abilities/test_colonize_planet.py`

- [x] Create new file `game/simulation/components/abilities/colonize.py`
- [x] Import dependencies: `from typing import Dict, Any, List` and `from .base import Ability, AbilityLayer, AbilityScope`
- [x] Define `ColonizePlanet` class extending `Ability`
- [x] Set class attributes: `layer = AbilityLayer.STRATEGIC`, `allowed_scopes = [AbilityScope.SELF]`, `default_scope = AbilityScope.SELF`
- [x] Implement `__init__(self, component, data: Dict[str, Any])`:
  - Call `super().__init__(component, data)`
  - Handle both dict format: `{"planet_type": "ICE_DWARF"}` and string shorthand: `"ICE_DWARF"`
  - Store `self.planet_type` as string (e.g., "CONTINENTAL", "ICE_DWARF")
- [x] Implement `get_ui_rows(self) -> List[Dict[str, str]]`:
  - Return list with one row: `{'label': 'Colonizes', 'value': <formatted_planet_type>, 'color_hint': '#00FF00'}`
  - Format planet type: `self.planet_type.replace('_', ' ').title()`
- [x] Verify: File saved and no syntax errors

**Notes:** Implemented with full docstrings and `get_primary_value()` returning 0.0 (marker ability).

---

### Task 1.2: Register ColonizePlanet Ability [Simple]
**File:** `game/simulation/components/abilities/__init__.py`
**Tests:** Ability instantiation in next task's tests

- [x] Open `game/simulation/components/abilities/__init__.py`
- [x] Add import at top of file: `from .colonize import ColonizePlanet`
- [x] Find `ABILITY_REGISTRY` dictionary (around line 30-60)
- [x] Add entry: `"ColonizePlanet": ColonizePlanet,` (alphabetically sorted)
- [x] Find `__all__` list (around line 100-130)
- [x] Add entry: `"ColonizePlanet",` (alphabetically sorted)
- [x] Verify: No import errors when loading abilities module

**Notes:** Added as first entry in registry and __all__ for clarity.

---

### Task 1.3: Add 11 Colony Pod Components to JSON [Simple]
**File:** `data/components.json`
**Tests:** Component loading verification

- [x] Open `data/components.json`
- [x] Find appropriate location (near other infrastructure components, around line 1000+)
- [x] Add component: `continental_colony_pod` with:
  - `"id": "continental_colony_pod"`, `"name": "Continental Colony Pod"`, `"type": "Colony"`
  - `"mass": 500`, `"hp": 300`, `"allowed_vehicle_types": ["Ship"]`, `"sprite_index": 210`
  - `"abilities": {"ColonizePlanet": "CONTINENTAL"}`
  - `"major_classification": "Infrastructure"`
  - `"resource_cost": {"Metals": 300, "Organics": 200, "Vapors": 100}`
- [x] Add component: `arid_colony_pod` (same pattern, planet type "ARID", sprite_index 211)
- [x] Add component: `pelagic_colony_pod` (planet type "PELAGIC", sprite_index 212)
- [x] Add component: `magma_colony_pod` (planet type "MAGMA", sprite_index 213)
- [x] Add component: `cryoplanet_colony_pod` (planet type "CRYOPLANET", sprite_index 214)
- [x] Add component: `barren_colony_pod` (planet type "BARREN", sprite_index 215)
- [x] Add component: `jovian_colony_pod` (planet type "JOVIAN", sprite_index 216, higher costs)
- [x] Add component: `ice_giant_colony_pod` (planet type "ICE_GIANT", sprite_index 217, higher costs)
- [x] Add component: `chthonian_colony_pod` (planet type "CHTHONIAN", sprite_index 218, higher costs)
- [x] Add component: `ice_dwarf_colony_pod` (planet type "ICE_DWARF", sprite_index 219)
- [x] Add component: `planetoid_colony_pod` (planet type "PLANETOID", sprite_index 220)
- [x] Verify: JSON file is valid (no syntax errors, commas correct)
- [x] Verify: All 11 planet types covered (CONTINENTAL, ARID, PELAGIC, MAGMA, CRYOPLANET, BARREN, JOVIAN, ICE_GIANT, CHTHONIAN, ICE_DWARF, PLANETOID)

**Notes:** Added at end of components.json after warp_drive. Extreme environments (JOVIAN, ICE_GIANT, CHTHONIAN) have higher mass (800) and costs including Radioactives/Exotics.

---

### Task 1.4: Write Unit Tests for ColonizePlanet Ability [Simple]
**File:** `tests/unit/abilities/test_colonize_planet.py` (new file)
**Tests:** `pytest tests/unit/abilities/test_colonize_planet.py -v`

- [x] Create new file `tests/unit/abilities/test_colonize_planet.py`
- [x] Import pytest, Component class, and test fixtures
- [x] Write test: `test_colonize_planet_dict_format(mock_component)`
  - Create component with ability: `"ColonizePlanet": {"planet_type": "ICE_DWARF"}`
  - Get ability: `component.get_ability('ColonizePlanet')`
  - Assert: `ability is not None`, `ability.planet_type == "ICE_DWARF"`
- [x] Write test: `test_colonize_planet_string_shorthand(mock_component)`
  - Create component with ability: `"ColonizePlanet": "CONTINENTAL"`
  - Assert: `ability.planet_type == "CONTINENTAL"`
- [x] Write test: `test_colonize_planet_ui_display_ice_dwarf(mock_component)`
  - Create component with ability for "ICE_DWARF"
  - Call `ability.get_ui_rows()`
  - Assert: Returns list with one dict containing 'label' and 'value' keys
  - Assert: Value contains formatted planet type (e.g., "Ice Dwarf")
- [x] Write test: `test_all_11_planet_types_supported(mock_component, planet_type)` - parametrized
  - Loop through all 11 planet types
  - Create component with ability for each type
  - Assert: Ability instantiates successfully for all types
- [x] Run tests: `pytest tests/unit/abilities/test_colonize_planet.py -v`
- [x] Verify: All tests pass (27 tests)

**Notes:** Tests placed in `tests/unit/abilities/` to match existing pattern. Used parametrized tests for the 11 planet types. Also tested registry, factory creation, scope validation, layer checks.

---

### Task 1.5: Verify Component Loading [Simple]
**File:** Manual verification
**Tests:** Run game startup or component registry test

- [x] Run: `pytest tests/unit/builder/ -k component -v` (tests that load components.json)
- [x] Verify: No errors loading component registry (27 tests passed)
- [x] Verify: All 11 colony pod components appear in registry (verified via Python script)
- [ ] Optional: Launch game and open ship designer to verify pods appear in component list

**Notes:** All 11 colony pods verified in components.json with correct planet types.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/abilities/test_colonize_planet.py -v` - all tests pass (27 passed)
- [x] Run `pytest tests/unit/builder/ -k component` - no errors loading components (27 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
