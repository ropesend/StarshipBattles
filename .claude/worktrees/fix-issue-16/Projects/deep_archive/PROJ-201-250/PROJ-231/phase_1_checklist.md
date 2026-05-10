# Phase 1: Data Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make enriched star data available to the UI through the CQRS-lite DTO pattern.

---

## Tasks

### Task 1.1: Expand StarInfo DTO [Simple]
**File:** `game/strategy/facade/dto/system_dto.py`
**Tests:** `python -m pytest tests/unit/strategy/facade/ -q`

- [x] Add fields to `StarInfo` frozen dataclass (after existing `location` field):
  - `mass: float = 0.0` (solar masses)
  - `radius_hexes: int = 1`
  - `temperature: float = 0.0` (Kelvin)
  - `luminosity: float = 0.0` (solar luminosity)
  - `age: float = 0.0` (years)
  - `system_name: str = ""`
  - `system_global_location: Optional[HexCoord] = None`
  - `planet_count: int = 0`
  - `companion_star_count: int = 0`
- [x] Add flattened spectrum fields (after star attributes):
  - `spectrum_gamma_ray: float = 0.0`
  - `spectrum_xray: float = 0.0`
  - `spectrum_ultraviolet: float = 0.0`
  - `spectrum_blue: float = 0.0`
  - `spectrum_green: float = 0.0`
  - `spectrum_red: float = 0.0`
  - `spectrum_infrared: float = 0.0`
  - `spectrum_microwave: float = 0.0`
  - `spectrum_radio: float = 0.0`
- [x] Update `from_star()` signature to accept kwargs: `system_name: str = ""`, `system_global_location: Optional[HexCoord] = None`, `planet_count: int = 0`, `total_star_count: int = 1`
- [x] Populate all new fields in `from_star()` body (spectrum from `star.spectrum.*`, companion_star_count = `total_star_count - 1`)
- [x] Verify existing call in `SystemInfo.from_star_system()` (line 95) still works — it passes only `star`, new params have defaults

**Notes:** 8 new tests in `tests/unit/strategy/facade/test_star_info_dto.py`. All 91 facade tests pass.

---

### Task 1.2: Add `get_all_stars()` to Facade [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `python -m pytest tests/unit/strategy/facade/ -q`

- [x] Add `StarInfo` to the `from game.strategy.facade.dto import (...)` block
- [x] Add `get_all_stars(self) -> List[StarInfo]` method
- [x] Verify: run existing facade tests pass (95 total, all passing)

**Notes:** Added between `get_all_systems()` and `get_system_at_hex()`. 4 new tests in TestFacadeGetAllStars class.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python -m pytest tests/unit/strategy/facade/ -q` passes (95 passed)
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
