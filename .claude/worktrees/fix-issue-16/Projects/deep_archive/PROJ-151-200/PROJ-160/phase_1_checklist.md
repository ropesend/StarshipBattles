# Phase 1: Add Galaxy Method

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-160 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `get_planet_global_hex()` method with unit tests

---

## Tasks

### Task 1.1: Add `get_planet_global_hex()` method [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v`

- [x] Add method after `get_planets_at_global_hex()` (after line 204):
  ```python
  def get_planet_global_hex(self, planet: 'Planet') -> Optional[HexCoord]:
      """O(1) lookup: get the global hex coordinate of a planet.

      Args:
          planet: Planet to get location for.

      Returns:
          Global HexCoord of the planet, or None if planet not registered.
      """
      system = self._planet_to_system.get(planet)
      if system:
          return system.global_location + planet.location
      return None
  ```
- [x] Verify no import changes needed (HexCoord already imported)

**Notes:** Implemented at lines 206-218 of galaxy.py

---

### Task 1.2: Add unit tests for new method [Simple]
**File:** `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py::TestGalaxyPlanetGlobalHex -v`

- [x] Add new test class after `TestGalaxySystemLookup` (after line 173)
- [x] Test: registered planet returns correct global hex
- [x] Test: unregistered planet returns None

**Notes:** Used simpler test approach using real Galaxy/StarSystem/Planet objects instead of mocks. HexCoord was already imported.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests pass: `pytest tests/unit/strategy/data/test_galaxy.py -v`
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
