# Phase 1: Data Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make enriched star data available to the UI through the CQRS-lite DTO pattern.

---

## Tasks

### Task 1.1: Expand StarInfo DTO [Simple]
**File:** `game/strategy/facade/dto/system_dto.py`
**Tests:** `python -m pytest tests/unit/strategy/facade/ -q`

- [ ] Add fields to `StarInfo` frozen dataclass (after existing `location` field):
  - `mass: float = 0.0` (solar masses)
  - `radius_hexes: int = 1`
  - `temperature: float = 0.0` (Kelvin)
  - `luminosity: float = 0.0` (solar luminosity)
  - `age: float = 0.0` (years)
  - `system_name: str = ""`
  - `system_global_location: Optional[HexCoord] = None`
  - `planet_count: int = 0`
  - `companion_star_count: int = 0`
- [ ] Add flattened spectrum fields (after star attributes):
  - `spectrum_gamma_ray: float = 0.0`
  - `spectrum_xray: float = 0.0`
  - `spectrum_ultraviolet: float = 0.0`
  - `spectrum_blue: float = 0.0`
  - `spectrum_green: float = 0.0`
  - `spectrum_red: float = 0.0`
  - `spectrum_infrared: float = 0.0`
  - `spectrum_microwave: float = 0.0`
  - `spectrum_radio: float = 0.0`
- [ ] Update `from_star()` signature to accept kwargs: `system_name: str = ""`, `system_global_location: Optional[HexCoord] = None`, `planet_count: int = 0`, `total_star_count: int = 1`
- [ ] Populate all new fields in `from_star()` body (spectrum from `star.spectrum.*`, companion_star_count = `total_star_count - 1`)
- [ ] Verify existing call in `SystemInfo.from_star_system()` (line 95) still works — it passes only `star`, new params have defaults

**Notes:**

---

### Task 1.2: Add `get_all_stars()` to Facade [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `python -m pytest tests/unit/strategy/facade/ -q`

- [ ] Add `StarInfo` to the `from game.strategy.facade.dto import (...)` block
- [ ] Add `get_all_stars(self) -> List[StarInfo]` method:
  ```python
  def get_all_stars(self) -> List['StarInfo']:
      """Get information about all stars in the galaxy."""
      results = []
      for system in self._session.galaxy.systems.values():
          for star in system.stars:
              results.append(StarInfo.from_star(
                  star,
                  system_name=system.name,
                  system_global_location=system.global_location,
                  planet_count=len(system.planets),
                  total_star_count=len(system.stars),
              ))
      return results
  ```
- [ ] Verify: run existing facade tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python -m pytest tests/unit/strategy/facade/ -q` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
