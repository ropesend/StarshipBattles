# Phase 5: EnvironmentalHazardEngine (Turn Integration)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Process environmental damage and resource drain during the 100-tick turn loop. Wire into TurnEngine as Phase 0f.

---

## Tasks

### Task 5.1: Create EnvironmentalHazardEngine [Medium]
**File:** `game/strategy/engine/environmental_hazard_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_environmental_hazard_engine.py`

- [x] Create `EnvironmentalEvent` dataclass:
  ```python
  @dataclass
  class EnvironmentalEvent:
      fleet_id: int
      storm_name: str
      damage_dealt: float
      fuel_drained: float
      tick: int
  ```
- [x] Create `EnvironmentalHazardEngine` class:
  - `__init__(self, area_effect_manager: AreaEffectManager = None)` - lazy-create default if None
  - `process_environmental_tick(self, tick: int, empires, galaxy) -> List[EnvironmentalEvent]`:
    - For each empire, for each fleet in empire.fleets:
      - Query `area_effect_manager.get_effects_at_global_hex(galaxy, fleet.location)`
      - If `effects.in_storm`:
        - **Damage:** Apply `effects.damage_per_tick / 100` to fleet ships per tick
          - For each ship in fleet: roll random component, apply damage (respect shields first)
          - Track total damage dealt
        - **Fuel drain:** Subtract `effects.fuel_drain_per_tick / 100` from fleet fuel reserves
          - Use fleet resource management (find fleet fuel, subtract)
          - Track total fuel drained
        - Create EnvironmentalEvent with totals
    - Return list of events
- [x] Write tests:
  - [x] Fleet in storm hex takes damage over multiple ticks
  - [x] Fleet fuel drain accumulates over ticks
  - [x] Fleet outside storm is unaffected
  - [x] Fleet in storm with damage_per_tick=0 takes no damage
  - [x] Multiple fleets in same storm each take independent damage/drain
  - [x] Damage distributed across ships in fleet

**Notes:** Damage application to individual ship components needs to use the existing damage model. Research how fleet ships store component damage (likely `ship.component_damage` dict) and how to apply damage to random components.

### Task 5.2: Add IEnvironmentalHazardEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)

- [x] Read current `engines.py` to understand interface pattern
- [x] Add `IEnvironmentalHazardEngine(ABC)` with abstract method:
  ```python
  @abstractmethod
  def process_environmental_tick(self, tick: int, empires, galaxy) -> list:
      pass
  ```
- [x] Add to `__all__` exports if the file uses them

**Notes:**

### Task 5.3: Wire into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py`

- [x] Add `IEnvironmentalHazardEngine` to TYPE_CHECKING imports (~line 60-71)
- [x] Add `environmental_engine: Optional['IEnvironmentalHazardEngine'] = None` to `__init__()` params (~line 113)
- [x] Store as `self._environmental_engine` (~line 178)
- [x] Add lazy-init property (after `action_engine` property, ~line 269):
  ```python
  @property
  def environmental_engine(self) -> 'IEnvironmentalHazardEngine':
      if self._environmental_engine is None:
          from game.strategy.engine.environmental_hazard_engine import EnvironmentalHazardEngine
          self._environmental_engine = EnvironmentalHazardEngine()
      return self._environmental_engine
  ```
- [x] Add `self.last_environmental_events: list = []` to `__init__` (after `last_scuttle_events`)
- [x] Clear `self.last_environmental_events = []` at start of `process_turn()` (~line 284)
- [x] Add Phase 0f in `_process_tick()` after Phase 0e (~line 364):
  ```python
  # --- Phase 0f: Environmental Hazards (storm damage, fuel drain) ---
  # PROJ-189: Apply storm effects to fleets in hazard hexes
  env_events = self.environmental_engine.process_environmental_tick(tick, empires, galaxy)
  self.last_environmental_events.extend(env_events)
  ```
- [x] Update docstrings to document Phase 0f
- [x] Write test: verify Phase 0f is called each tick with mock environmental engine
- [x] Run existing turn engine tests to verify no regressions

**Notes:**

### Task 5.4: Integrate AreaEffectManager with FleetMovementEngine [Simple]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_movement_engine.py`

- [x] Read current FleetMovementEngine to understand movement interval calculation
- [x] Add optional `area_effect_manager` parameter to constructor or relevant method
- [x] When calculating fleet movement intervals in `collect_movements()`, query effects at fleet's current hex
- [x] Apply `strategic_mult` to effective fleet speed: if fleet is in storm, movement interval increases (fleet moves fewer hexes per turn)
- [x] Write test: fleet in storm hex with strategic_mult=0.5 moves at half speed (double interval)
- [x] Write test: fleet outside storm moves at normal speed
- [x] Run existing movement tests to verify no regressions

**Notes:** The movement system uses `interval = int(100 // fleet.speed)`. With storm mult, effective speed = `floor(base_speed * strategic_mult)`. If effective speed drops to 0, fleet cannot move.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
