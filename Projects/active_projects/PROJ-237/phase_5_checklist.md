# Phase 5: Integration & Shield Blocking

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-237 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Wire PlanetEnergyEngine and PlanetActionEngine into TurnEngine, add shield blocking to superweapon processor, add event types.

---

## Tasks

### Task 5.1: Wire Engines into TurnEngine [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `python -m pytest tests/integration/strategy/turn_engine/ -v`

- [ ] Add TYPE_CHECKING imports (~line 66):
  ```python
  from game.strategy.interfaces.engines import (
      ...,
      IPlanetEnergyEngine,
      IPlanetActionEngine,
  )
  ```
- [ ] Add constructor parameters (after `environmental_engine`, ~line 123):
  ```python
  planet_energy_engine: Optional['IPlanetEnergyEngine'] = None,
  planet_action_engine: Optional['IPlanetActionEngine'] = None,
  ```
- [ ] Store in `__init__` (after `self._environmental_engine`, ~line 181):
  ```python
  self._planet_energy_engine: Optional['IPlanetEnergyEngine'] = planet_energy_engine
  self._planet_action_engine: Optional['IPlanetActionEngine'] = planet_action_engine
  ```
- [ ] Add lazy properties (after `environmental_engine` property, ~line 329):
  ```python
  @property
  def planet_energy_engine(self) -> 'IPlanetEnergyEngine':
      if self._planet_energy_engine is None:
          from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine
          self._planet_energy_engine = PlanetEnergyEngine(registries=self._registries)
      return self._planet_energy_engine

  @property
  def planet_action_engine(self) -> 'IPlanetActionEngine':
      if self._planet_action_engine is None:
          from game.strategy.engine.planet_action_engine import PlanetActionEngine
          from game.strategy.services.planet_action_time_resolver import PlanetActionTimeResolver
          self._planet_action_engine = PlanetActionEngine(
              registries=self._registries,
              action_time_resolver=PlanetActionTimeResolver()
          )
      return self._planet_action_engine
  ```
- [ ] Add Phase 0c1 to `_process_tick()` (after fuel gen phase 0c, ~line 450):
  ```python
  # --- Phase 0c1: Planet Energy (generation, consumption, auto-deactivation) ---
  self._time_phase('planet_energy', self.planet_energy_engine.process_energy_tick, tick, empires)
  ```
- [ ] Add Phase 1.6 to `_process_tick()` (after fleet actions phase 1.5, ~line 472):
  ```python
  # --- Phase 1.6: Planet Action Orders (shield activation, etc.) ---
  self._time_phase('planet_actions', self.planet_action_engine.process_planet_actions_tick,
                   tick, empires, component_registry=self._registries.components)
  ```
- [ ] Add to `_reset_phase_times()` (~line 194):
  ```python
  'planet_energy': 0.0, 'planet_actions': 0.0,
  ```
- [ ] Update perf logging in `process_turn()` (~line 377) to include new phases

**Notes:**

---

### Task 5.2: Add Shield Blocking to Superweapon Processor [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `python -m pytest tests/unit/strategy/engine/test_superweapon_order_processor.py -v`

- [ ] In `process_implode_planet()`, after target planet validation (~line 155), before finding ship with ability (~line 160):
  ```python
  # PROJ-237: Check for active planetary shield
  if target_planet.shield_active:
      logger.info(f"Planet {target_planet.name} protected by planetary shield, canceling IMPLODE_PLANET")
      fleet.pop_order()
      return SuperweaponResult(
          success=False,
          message=f"Planet {target_planet.name} is protected by a planetary shield"
      )
  ```
- [ ] Write test: planet with `shield_active=True` → `process_implode_planet()` returns failure
- [ ] Write test: planet with `shield_active=False` → normal destruction proceeds

**Notes:**

---

### Task 5.3: Add Event Types [Simple]
**File:** `game/strategy/events/event_types.py`
**Tests:** `python -m pytest tests/unit/strategy/events/ -v`

- [ ] Add to `EventType` enum (after `FLEET_JOIN_CANCELLED`, line 22):
  ```python
  # Planet operations (PROJ-237)
  SHIELD_ACTIVATED = "shield_activated"
  SHIELD_DEACTIVATED = "shield_deactivated"
  SHIELD_AUTO_DEACTIVATED = "shield_auto_deactivated"
  ```
- [ ] Add to `EventCategory` enum (after `FLEET_OPERATIONS`, line 32):
  ```python
  PLANET_OPERATIONS = "planet_operations"
  ```
- [ ] Update any tests that assert on `len(EventType)` (search for hardcoded count)

**Notes:**

---

### Task 5.4: Write Integration Tests [Complex]
**File:** `tests/integration/strategy/test_planet_shield_integration.py` (NEW)
**Tests:** `python -m pytest tests/integration/strategy/test_planet_shield_integration.py -v`

- [ ] Test full turn cycle with shield complex:
  1. Create planet with shield + generator + battery facilities
  2. Process turn → energy generates
  3. Issue ACTIVATE_SHIELD order → activation progresses over ticks
  4. After activation_time ticks → shield is active
  5. Energy drains each tick while shield active
  6. Planet destroyer order → blocked by shield
  7. Remove generators → energy depletes → shield auto-deactivates
  8. Planet destroyer order → succeeds (no shield)
- [ ] Test multi-turn activation (action_time > 100 ticks)
- [ ] Test energy balance: generation rate > drain rate → shield sustains
- [ ] Test energy balance: generation rate < drain rate → shield eventually auto-deactivates
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] TurnEngine processes planet energy and actions per tick
- [ ] Superweapon processor blocks destruction of shielded planets
- [ ] Event types defined
- [ ] Integration tests verify full lifecycle
- [ ] `python -m pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
