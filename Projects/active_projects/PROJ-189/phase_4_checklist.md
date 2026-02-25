# Phase 4: AreaEffectManager Service

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create a service that aggregates environmental effects from storms at a given hex location and integrate with fleet speed calculation.

---

## Tasks

### Task 4.1: Create AreaEffectManager [Medium]
**File:** `game/strategy/services/area_effect_manager.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_area_effect_manager.py`

- [x] Create `EnvironmentalEffects` dataclass:
  ```python
  @dataclass
  class EnvironmentalEffects:
      shield_capacity_mult: float = 1.0
      thrust_mult: float = 1.0
      strategic_mult: float = 1.0
      damage_per_tick: float = 0.0
      fuel_drain_per_tick: float = 0.0
      in_storm: bool = False
      storm_names: List[str] = field(default_factory=list)
  ```
- [x] Create `AreaEffectManager` class:
  - `get_effects_at_global_hex(self, galaxy, global_hex: HexCoord) -> EnvironmentalEffects`:
    - Query `galaxy.get_zones_at_global_hex(global_hex)` (existing O(1) spatial index)
    - Filter to `Storm` instances only (using `isinstance(zone, Storm)` - skip stars, planets, Dyson Spheres)
    - For each storm found:
      - Multiply multiplicative effects: `result.shield_capacity_mult *= storm.effects.shield_capacity_mult`
      - Multiply: `result.thrust_mult *= storm.effects.thrust_mult`
      - Multiply: `result.strategic_mult *= storm.effects.strategic_mult`
      - Sum additive effects: `result.damage_per_tick += storm.effects.damage_per_tick`
      - Sum: `result.fuel_drain_per_tick += storm.effects.fuel_drain_per_tick`
    - Set `result.in_storm = True` and collect `storm_names` if any storms found
    - Return result
- [x] Write tests:
  - [x] Empty hex returns neutral EnvironmentalEffects (all defaults)
  - [x] Single storm at hex returns that storm's effects
  - [x] Two overlapping storms: multiplicative effects stack multiplicatively, additive effects sum
  - [x] Non-storm zones (stars, planets) at hex are filtered out (not treated as storms)
  - [x] `in_storm` is True only when storms present, `storm_names` lists storm names

**Notes:** Import Storm type with `TYPE_CHECKING` to avoid circular imports if needed.

### Task 4.2: Integrate with fleet speed calculator [Simple]
**File:** `game/strategy/services/fleet_speed_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_speed_calculator.py`

- [x] Read current fleet speed calculation methods to understand the interface
- [x] Add optional `environmental_effects: Optional[EnvironmentalEffects] = None` parameter to the appropriate speed calculation method
- [x] When provided, multiply the calculated strategic movement value by `environmental_effects.strategic_mult` BEFORE the final `floor()` and clamping
- [x] Write test: fleet with `strategic_mult=0.5` has half the speed
- [x] Write test: fleet with `strategic_mult=1.0` (no storm) has unchanged speed
- [x] Write test: fleet with `strategic_mult=0.1` still has at least speed 0 (clamping works)
- [x] Run existing fleet speed tests to verify no regressions

**Notes:** Added `calculate_fleet_speed_with_environment()` method that applies strategic_mult after base calculation.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/ -n 12` (12,667 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
