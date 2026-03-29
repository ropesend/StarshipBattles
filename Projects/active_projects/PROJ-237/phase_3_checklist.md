# Phase 3: Planet Energy Engine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-237 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create PlanetEnergyEngine that generates energy from generators, stores up to battery capacity, consumes energy for active shields, and auto-deactivates shields when energy runs out.

---

## Tasks

### Task 3.1: Create PlanetEnergyEngine [Complex]
**File:** `game/strategy/engine/planet_energy_engine.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/engine/test_planet_energy_engine.py -v`

Follow `game/strategy/engine/harvesting_engine.py` as template for component scanning pattern:

- [ ] Create new file `game/strategy/engine/planet_energy_engine.py`
- [ ] Create `IPlanetEnergyEngine` interface (or add to `interfaces/engines.py` — see Task 3.2)
- [ ] Create `PlanetEnergyEngine(IPlanetEnergyEngine)` class:
  ```python
  def __init__(self, *, registries: Optional[GameRegistries] = None): ...
  ```
- [ ] Implement `process_energy_tick(self, tick: int, empires: List) -> None`:
  - For each empire → each colony:
    1. **Recalculate capacity** — scan facilities for `PlanetaryEnergyStorage` abilities, sum `capacity` values → set `planet.energy_capacity`
    2. **Recalculate generation** — scan facilities for `PlanetaryEnergyGenerator` abilities, sum `generation_rate` values → set `planet.energy_generation`
    3. **Generate energy** — `planet.energy += planet.energy_generation / 100.0` (per tick)
    4. **Consume energy** — if `planet.shield_active`, find `PlanetaryShield` ability, `planet.energy -= energy_drain_rate / 100.0`
    5. **Auto-deactivate** — if `planet.energy <= 0` and `planet.shield_active`: set `planet.shield_active = False`, set `planet.energy = 0.0`, deactivate component state on facility, log event
    6. **Clamp** — `planet.energy = max(0.0, min(planet.energy, planet.energy_capacity))`
- [ ] Create helper functions (following `get_harvester_info()` pattern):
  - `get_energy_generator_info(comp, registries)` → returns dict with `generation_rate` or None
  - `get_energy_storage_info(comp, registries)` → returns dict with `capacity` or None
  - `get_shield_info(comp, registries)` → returns dict with `energy_drain_rate` or None
- [ ] Use `iter_components()` from `game.core.patterns.layer_iterator` for facility scanning
- [ ] Use `get_component_abilities()` from `game.strategy.services.component_inspector` for ability extraction

**Notes:** Recalculate capacity/generation each tick (like HarvestingEngine's `recalculate_storage()`) to handle mid-turn facility destruction.

---

### Task 3.2: Create Engine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** No direct test needed (interface only)

- [ ] Add `IPlanetEnergyEngine` ABC (after `IEnvironmentalHazardEngine`, ~line 553):
  ```python
  class IPlanetEnergyEngine(ABC):
      """Abstract interface for planet energy generation and consumption."""

      @abstractmethod
      def process_energy_tick(self, tick: int, empires: List) -> None:
          """Process energy generation/consumption for one tick."""
          pass
  ```
- [ ] Add `'IPlanetEnergyEngine'` to `__all__` list (line 29)

**Notes:**

---

### Task 3.3: Write Energy Engine Tests [Complex]
**File:** `tests/unit/strategy/engine/test_planet_energy_engine.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/engine/test_planet_energy_engine.py -v`

- [ ] Create test file
- [ ] Test: planet with generator → energy increases each tick
- [ ] Test: planet with battery → energy capped at capacity
- [ ] Test: planet with no generators → energy stays at 0
- [ ] Test: planet with active shield → energy decreases each tick
- [ ] Test: energy drain exceeds available → auto-deactivate shield, energy clamped to 0
- [ ] Test: generator destroyed (facility removed) mid-turn → generation rate recalculated
- [ ] Test: battery destroyed mid-turn → capacity recalculated, energy clamped
- [ ] Test: shield facility destroyed while active → shield deactivated
- [ ] Test: multiple generators stack additively
- [ ] Test: multiple batteries stack additively
- [ ] Test: energy generation with no shield → accumulates to capacity
- [ ] Test: tick_fraction (1/100th) applied correctly
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] PlanetEnergyEngine created with component scanning
- [ ] Interface defined in engines.py
- [ ] All energy engine tests pass
- [ ] `python -m pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
