# PROJ-08: Strategy Layer Data-Driven Resource System

## Overview
Refactor the strategy layer resource system to be fully data-driven. Any resource type defined in JSON (fuel, energy, ammo, or custom types like "glag") should work seamlessly without Python code changes. This includes movement costs, warp costs, and per-turn passive consumption.

## Goals
- Remove all hardcoded resource names ('fuel', 'energy', 'ammo') from Python code
- Support arbitrary resource types defined in JSON
- Add new trigger types: `per_turn` (spread over 100 ticks) and `warp_jump`
- Add component toggle (enable/disable) with auto-disable on resource depletion
- Maintain backward compatibility with existing saves and tests

## Scope
**In Scope:**
- `game/strategy/` layer refactoring
- Resource registry creation (`data/resources.json`)
- Generic resource methods in ShipInstance and Fleet
- TurnEngine per-tick resource processing
- Component toggle state tracking
- Backward-compatible wrapper methods

**Out of Scope:**
- Simulation layer (`game/simulation/`) - separate future project
- UI display configuration (colors, priorities) - separate concern
- Combat resource consumption - handled by simulation layer
- Resource generation (regeneration) - future enhancement

## Current State
**Last Updated:** 2026-01-21 15:30
**Current Phase:** Planning Complete - Awaiting Approval
**Last Agent Action:** Completed swarm analysis with 6 specialized agents
**Next Action:** User approval, then begin Phase 1 implementation
**Blockers:** None
**Context for Next Agent:** Comprehensive analysis complete. Critical bug found in ship_stats_service.py (uninitialized variables). Plan accounts for this fix in Phase 2.

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Resource Registry | `game/core/registry.py` | `RegistryManager.resources` |
| Stats Calculation | `game/strategy/services/ship_stats_service.py` | `ShipStatsService.calculate_stats()` |
| Ship Resources | `game/strategy/data/ship_instance.py` | `ShipInstance.resource_levels` |
| Fleet Resources | `game/strategy/data/fleet.py` | `Fleet.consume_*` methods |
| Turn Processing | `game/strategy/engine/turn_engine.py` | `TurnEngine._process_tick()` |
| Mobility Service | `game/strategy/services/fleet_mobility_service.py` | `FleetMobilityService` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Per-turn consumption spread across 100 ticks (amount/100 per tick) | Smoother depletion, consistent with tick-based architecture |
| 2026-01-21 | Auto-disable components when out of resources | Ships continue operating, just lose capability |
| 2026-01-21 | Player can manually toggle components + auto-disable | Full control plus automatic safety |
| 2026-01-21 | Resource registry in `data/resources.json` (no display metadata) | Separation of concerns - UI config is separate |
| 2026-01-21 | Warp costs via `ResourceConsumption` with `trigger: 'warp_jump'` | Consistent with other trigger patterns |
| 2026-01-21 | Keep backward-compatible wrapper methods temporarily | Gradual migration, avoid breaking changes |

## Initial Analysis
The strategy layer is well-organized with clean separation between services and data. Key findings:
- `ShipStatsService` is stateless and isolated (only imports from `game.core.registry`)
- `ShipInstance.resource_levels` is already a generic `Dict[str, float]`
- Fleet operations use atomic check-then-consume patterns
- TurnEngine has 4-phase tick processing with clear extension points

## Swarm Findings Summary

### Architecture
- **Clean boundaries:** ShipStatsService only imports from `game.core.registry`
- **Data flow:** Fleet → ShipInstance → ShipStatsService → Component Registry
- **Caching:** ShipInstance uses `_cached_stats` with explicit invalidation
- **Coupling issue:** TurnEngine imports from simulation layer for battle resolution (acceptable, out of scope)

### Key Patterns to Reuse
- **RegistryManager pattern** (`game/core/registry.py:4-185`): Singleton with in-place dict updates
- **Ability Registry pattern** (`game/simulation/components/abilities/__init__.py:52-97`): Factory with class map
- **Multi-format handling** (`game/simulation/components/abilities/resources.py:30-40`): Dict or primitive input
- **Stat binding pattern** (`game/simulation/components/abilities/stat_keys.py:100-136`): Declarative bindings

### Risks Identified
1. **CRITICAL BUG:** `ship_stats_service.py` has uninitialized variables (`total_fuel_storage`, `total_energy_storage`, `total_ammo_storage`, `warp_energy_cost`, `warp_fuel_cost`) - will crash on first use. **Must fix in Phase 2.**
2. **Backward compatibility:** Old saves missing `component_toggles` field - mitigated by defaulting to `{}`
3. **Cache invalidation:** Component toggle must invalidate `_cached_stats`
4. **Atomic operations:** Partial consumption risk if exception mid-loop - mitigated by two-phase pattern

### Dependency Map
- **31 files** in dependency chain for resource handling
- **Zero circular dependencies** (safe architecture)
- **4 locations** with hardcoded resource strings (all in core files)
- **Modification order:** ship_stats_service → ship_instance → fleet → turn_engine → tests

### Test Impact
- **10 critical test files** require updates
- **87 files** contain resource references (search scope)
- **5-7 hours** estimated test update time
- **New tests needed:** Resource constants, ability binding, edge cases, migration

---

## Phases

### Phase 1: Resource Registry Infrastructure [Simple]
**Objective:** Create resource registry and loading mechanism
**Status:** Not Started

#### Task 1.1: Create Resource Registry JSON [Simple]
**File:** `data/resources.json` (NEW)
**Tests:** Manual verification - file loads without error
- [ ] Create `data/resources.json` with initial content:
  ```json
  {
    "resources": [
      {"id": "fuel"},
      {"id": "energy"},
      {"id": "ammo"}
    ]
  }
  ```
**Notes:**

#### Task 1.2: Add Resource Registry to RegistryManager [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/` (if exists) or manual import test
- [ ] Add `self.resources: Dict[str, Any] = {}` to `__init__` (after line 54)
- [ ] Add to `hydrate()` method - add `resources_data` parameter and `self.resources.update(resources_data)` (line 125)
- [ ] Add to `clear()` method - add `self.resources.clear()` (after line 141)
- [ ] Add utility function after line 180:
  ```python
  def get_resource_registry() -> Dict[str, Any]:
      """Get the resource registry dictionary."""
      return RegistryManager.instance().resources
  ```
**Notes:**

#### Task 1.3: Create Resource Loading Function [Simple]
**File:** `game/simulation/components/component.py` (or new file)
**Tests:** Unit test that loading succeeds
- [ ] Add `load_resources()` function (pattern: follow `load_components` at line ~50):
  ```python
  def load_resources(filepath="data/resources.json"):
      """Load resource definitions from JSON."""
      from game.core.registry import RegistryManager
      import os

      if not os.path.exists(filepath):
          # Default resources if file doesn't exist
          default = {'fuel': {}, 'energy': {}, 'ammo': {}}
          RegistryManager.instance().resources.update(default)
          return

      data = load_json_required(filepath)
      for res_def in data.get('resources', []):
          res_id = res_def['id']
          RegistryManager.instance().resources[res_id] = res_def
  ```
**Notes:**

#### Task 1.4: Integrate Resource Loading in App [Simple]
**File:** `game/app.py`
**Tests:** Run game, verify no errors on startup
- [ ] Find where `load_components()` is called
- [ ] Add `load_resources()` call after `load_components()` and `load_modifiers()`
- [ ] Import `load_resources` from appropriate module
**Notes:**

---

### Phase 2: ShipStatsService Generic Refactor [Complex]
**Objective:** Replace hardcoded resource handling with generic dict accumulation
**Status:** Not Started

#### Task 2.1: Fix Uninitialized Variable Bug [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`
- [ ] Add missing initializations after line 73:
  ```python
  total_fuel_storage = 0.0
  total_energy_storage = 0.0
  total_ammo_storage = 0.0
  warp_energy_cost = 0.0
  warp_fuel_cost = 0.0
  ```
**Notes:** CRITICAL - This bug will crash stats calculation. Fix FIRST before any other changes.

#### Task 2.2: Refactor to Generic Dict Accumulators [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`
- [ ] Replace specific accumulators with generic dicts (after fixing 2.1):
  ```python
  # Replace:
  total_fuel_storage = 0.0
  total_energy_storage = 0.0
  total_ammo_storage = 0.0

  # With:
  resource_storage: Dict[str, float] = {}
  resource_consumption_per_hex: Dict[str, float] = {}
  resource_consumption_per_turn: Dict[str, float] = {}
  ```
- [ ] Remove if-elif chains at lines 132-137, replace with:
  ```python
  for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceStorage'):
      resource_type = ability_data.get('resource', '')
      max_amount = ability_data.get('max_amount') or ability_data.get('amount', 0)
      if resource_type:
          resource_storage[resource_type] = resource_storage.get(resource_type, 0) + max_amount * effectiveness
  ```
**Notes:**

#### Task 2.3: Add Component Toggles Parameter [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`
- [ ] Add `component_toggles: Optional[Dict[str, bool]] = None` parameter to `calculate_stats()` (line 41)
- [ ] Add default: `if component_toggles is None: component_toggles = {}`
- [ ] In component loop (line 105), add toggle check:
  ```python
  # Check if component is toggled off
  if not component_toggles.get(comp_id, True):
      # Still count mass, skip abilities
      comp_mass = ShipStatsService._get_numeric_value(comp_def, 'mass', 0)
      total_mass += comp_mass
      continue
  ```
**Notes:**

#### Task 2.4: Add New Trigger Types [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`
- [ ] In ResourceConsumption processing (around line 156), add trigger handling:
  ```python
  for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceConsumption'):
      resource_type = ability_data.get('resource', '')
      amount = ability_data.get('amount', 0)
      trigger = ability_data.get('trigger', 'constant')

      if trigger == 'strategic_per_hex':
          resource_consumption_per_hex[resource_type] = (
              resource_consumption_per_hex.get(resource_type, 0) + amount * effectiveness
          )
      elif trigger == 'per_turn':  # NEW
          resource_consumption_per_turn[resource_type] = (
              resource_consumption_per_turn.get(resource_type, 0) + amount * effectiveness
          )
      elif trigger == 'warp_jump':  # NEW
          warp_resource_costs[resource_type] = (
              warp_resource_costs.get(resource_type, 0) + amount * effectiveness
          )
  ```
**Notes:**

#### Task 2.5: Update Return Structure [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`
- [ ] Update return dict (around line 184) to include new fields AND legacy fields:
  ```python
  return {
      'max_hp': int(total_hp),
      'mass': total_mass,
      # New generic fields
      'resource_storage': resource_storage,
      'resource_consumption_per_hex': resource_consumption_per_hex,
      'resource_consumption_per_turn': resource_consumption_per_turn,
      'warp_resource_costs': warp_resource_costs,
      'strategic_movement': total_strategic_movement,
      'warp_max_tonnage': warp_max_tonnage,
      # Legacy fields for backward compatibility
      'max_fuel': resource_storage.get('fuel', 0),
      'max_energy': resource_storage.get('energy', 0),
      'max_ammo': resource_storage.get('ammo', 0),
      'strategic_fuel_per_hex': resource_consumption_per_hex.get('fuel', 0),
      'warp_energy_cost': warp_resource_costs.get('energy', 0),
      'warp_fuel_cost': warp_resource_costs.get('fuel', 0),
  }
  ```
**Notes:**

#### Task 2.6: Update Fallback Logic [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`
- [ ] Update fallback return (lines 90-103) to include new fields:
  ```python
  # Add to fallback return:
  'resource_storage': {
      'fuel': expected.get('max_fuel', 0),
      'energy': expected.get('max_energy', 0),
      'ammo': expected.get('max_ammo', 0),
  },
  'resource_consumption_per_hex': {
      'fuel': expected.get('strategic_fuel_per_hex', 0),
  },
  'resource_consumption_per_turn': {},
  ```
**Notes:**

---

### Phase 3: ShipInstance Generic Methods [Medium]
**Objective:** Add generic resource methods and component toggle support
**Status:** Not Started

#### Task 3.1: Add Component Toggles Field [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance.py` (if exists)
- [ ] Add field to dataclass (after line 45):
  ```python
  component_toggles: Dict[str, bool] = field(default_factory=dict)
  ```
**Notes:**

#### Task 3.2: Add Generic Resource Methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Add after existing resource methods (around line 293):
  ```python
  def get_resource_capacity(self, resource_type: str) -> float:
      """Get maximum capacity for any resource type."""
      stats = self.get_calculated_stats()
      resource_storage = stats.get('resource_storage', {})
      return resource_storage.get(resource_type, 0)

  def get_current_resource(self, resource_type: str) -> float:
      """Get current level of any resource type."""
      max_val = self.get_resource_capacity(resource_type)
      return self.resource_levels.get(resource_type, max_val)

  def consume_resource(self, resource_type: str, amount: float) -> bool:
      """Consume resource. Returns True if successful."""
      max_val = self.get_resource_capacity(resource_type)
      current = self.resource_levels.get(resource_type, max_val)
      if current < amount:
          return False
      self.resource_levels[resource_type] = current - amount
      return True

  def get_all_resource_costs_per_hex(self) -> Dict[str, float]:
      """Get all per-hex consumption costs."""
      stats = self.get_calculated_stats()
      return stats.get('resource_consumption_per_hex', {})

  def get_all_resource_costs_per_turn(self) -> Dict[str, float]:
      """Get all per-turn consumption costs."""
      stats = self.get_calculated_stats()
      return stats.get('resource_consumption_per_turn', {})

  def get_warp_resource_costs(self) -> Dict[str, float]:
      """Get all resource costs for a warp jump."""
      stats = self.get_calculated_stats()
      return stats.get('warp_resource_costs', {})
  ```
**Notes:**

#### Task 3.3: Add Component Toggle Methods [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Add toggle methods:
  ```python
  def set_component_enabled(self, component_id: str, enabled: bool) -> None:
      """Enable or disable a component manually."""
      self.component_toggles[component_id] = enabled
      self.invalidate_stats_cache()

  def is_component_enabled(self, component_id: str) -> bool:
      """Check if a component is enabled."""
      return self.component_toggles.get(component_id, True)
  ```
**Notes:**

#### Task 3.4: Update get_calculated_stats to Pass Toggles [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Update `get_calculated_stats()` (around line 170):
  ```python
  self._cached_stats = ShipStatsService.calculate_stats(
      self.design_data,
      self.component_damage,
      self.component_toggles  # NEW parameter
  )
  ```
**Notes:**

#### Task 3.5: Update Serialization [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Add to `to_dict()` (around line 592):
  ```python
  'component_toggles': self.component_toggles,
  ```
- [ ] Add to `from_dict()` (around line 612):
  ```python
  instance.component_toggles = data.get('component_toggles', {})
  ```
**Notes:**

#### Task 3.6: Mark Legacy Methods as Deprecated [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** No test changes needed
- [ ] Update docstrings for `get_current_fuel()`, `consume_fuel()`, `get_current_energy()`, `consume_energy()`:
  ```python
  def get_current_fuel(self) -> float:
      """DEPRECATED: Use get_current_resource('fuel')."""
      return self.get_current_resource('fuel')
  ```
**Notes:** Keep implementations as wrappers for backward compatibility

---

### Phase 4: Fleet Generic Methods [Medium]
**Objective:** Add generic resource checking and consumption methods
**Status:** Not Started

#### Task 4.1: Add Generic Movement Resource Methods [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`
- [ ] Add after existing fuel methods (around line 221):
  ```python
  def get_movement_resource_costs(self) -> Dict[str, float]:
      """Get total fleet resource costs per hex of movement."""
      total_costs: Dict[str, float] = {}
      for ship in self.get_combat_capable_ships():
          ship_costs = ship.get_all_resource_costs_per_hex()
          for resource_type, cost in ship_costs.items():
              total_costs[resource_type] = total_costs.get(resource_type, 0) + cost
      return total_costs

  def has_resources_for_movement(self) -> bool:
      """Check if fleet has resources for at least one hex of movement."""
      for ship in self.get_combat_capable_ships():
          costs = ship.get_all_resource_costs_per_hex()
          for resource_type, cost in costs.items():
              if cost > 0:
                  current = ship.get_current_resource(resource_type)
                  if current < cost:
                      return False
      return True

  def consume_movement_resources(self, hexes: int = 1) -> bool:
      """Consume resources for movement. Atomic operation."""
      ships = self.get_combat_capable_ships()

      # Verify all ships have resources
      for ship in ships:
          costs = ship.get_all_resource_costs_per_hex()
          for resource_type, cost in costs.items():
              total_cost = cost * hexes
              if total_cost > 0:
                  if ship.get_current_resource(resource_type) < total_cost:
                      return False

      # Consume from all ships
      for ship in ships:
          costs = ship.get_all_resource_costs_per_hex()
          for resource_type, cost in costs.items():
              total_cost = cost * hexes
              if total_cost > 0:
                  ship.consume_resource(resource_type, total_cost)
      return True
  ```
**Notes:**

#### Task 4.2: Refactor Warp Resource Methods to Generic [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`
- [ ] Update `has_resources_for_warp()` (lines 249-275) to use generic methods:
  ```python
  def has_resources_for_warp(self) -> bool:
      """Check if fleet has all required resources for a warp jump."""
      for ship in self.get_combat_capable_ships():
          warp_costs = ship.get_warp_resource_costs()
          for resource_type, cost in warp_costs.items():
              if cost > 0:
                  current = ship.get_current_resource(resource_type)
                  if current < cost:
                      return False
      return True
  ```
- [ ] Update `consume_warp_resources()` (lines 289-327) similarly
- [ ] Add `get_warp_resource_costs()` method:
  ```python
  def get_warp_resource_costs(self) -> Dict[str, float]:
      """Get total fleet resource costs for a warp jump."""
      total_costs: Dict[str, float] = {}
      for ship in self.get_combat_capable_ships():
          ship_costs = ship.get_warp_resource_costs()
          for resource_type, cost in ship_costs.items():
              total_costs[resource_type] = total_costs.get(resource_type, 0) + cost
      return total_costs
  ```
**Notes:**

#### Task 4.3: Keep Backward Compatibility Aliases [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** No changes needed
- [ ] Verify `has_fuel_for_movement()` exists as wrapper for `has_resources_for_movement()`
- [ ] Verify `consume_fleet_fuel()` wraps `consume_movement_resources()`
- [ ] Verify `has_energy_for_warp()` wraps `has_resources_for_warp()`
- [ ] Verify `consume_warp_energy()` wraps `consume_warp_resources()`
**Notes:** These already exist from previous work, just verify they still work

---

### Phase 5: TurnEngine Per-Tick Processing [Complex]
**Objective:** Add per-tick resource consumption for `per_turn` trigger
**Status:** Not Started

#### Task 5.1: Add Per-Turn Resource Processing Method [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/` + manual turn processing test
- [ ] Add new method after `_process_tick()`:
  ```python
  def _process_per_turn_resources(self, tick: int, empires) -> None:
      """Process per-turn resource consumption (1/100th per tick)."""
      for empire in empires:
          for fleet in empire.fleets:
              for ship in fleet.get_ship_instances():
                  if not ship.is_combat_capable():
                      continue

                  per_turn_costs = ship.get_all_resource_costs_per_turn()
                  for resource_type, total_cost in per_turn_costs.items():
                      if total_cost <= 0:
                          continue

                      tick_cost = total_cost / 100.0
                      if not ship.consume_resource(resource_type, tick_cost):
                          self._auto_disable_components_for_resource(ship, resource_type)
  ```
**Notes:**

#### Task 5.2: Add Auto-Disable Helper [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Add helper method:
  ```python
  def _auto_disable_components_for_resource(self, ship, resource_type: str) -> None:
      """Auto-disable components that require a depleted resource."""
      from game.core.registry import get_component_registry
      from game.strategy.services.ship_stats_service import ShipStatsService

      registry = get_component_registry()
      layers = ship.design_data.get('layers', {})

      for layer_name, components in layers.items():
          if isinstance(components, list):
              comp_list = components
          elif isinstance(components, dict):
              comp_list = components.get('components', [])
          else:
              continue

          for comp_entry in comp_list:
              comp_id = comp_entry.get('id', '')
              comp_def = registry.get(comp_id)
              if comp_def is None:
                  continue

              abilities = getattr(comp_def, 'abilities', {}) or {}
              for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceConsumption'):
                  if (ability_data.get('trigger') == 'per_turn' and
                      ability_data.get('resource') == resource_type):
                      ship.set_component_enabled(comp_id, False)
                      from game.core.logger import log_info
                      log_info(f"Ship {ship.name}: Auto-disabled {comp_id} - insufficient {resource_type}")
  ```
**Notes:**

#### Task 5.3: Integrate Per-Turn Processing into Tick Loop [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/` + manual testing
- [ ] In `_process_tick()` (around line 240), add call at start of tick:
  ```python
  def _process_tick(self, tick, empires, galaxy):
      # Phase 0: Per-turn resource consumption
      self._process_per_turn_resources(tick, empires)

      # Phase 1: Instant Orders (existing)
      # ...
  ```
**Notes:**

#### Task 5.4: Update Movement Processing to Use Generic Methods [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Update fuel check (line 282-284):
  ```python
  # Change from:
  if not fleet.has_fuel_for_movement():
  # To:
  if not fleet.has_resources_for_movement():
  ```
- [ ] Update fuel consumption (line 301):
  ```python
  # Change from:
  fleet.consume_fleet_fuel(1)
  # To:
  fleet.consume_movement_resources(1)
  ```
**Notes:** Warp methods already use generic versions from previous work

---

### Phase 6: Update Components JSON [Simple]
**Objective:** Migrate WarpJump costs to ResourceConsumption abilities
**Status:** Not Started

#### Task 6.1: Update Warp Drive Components [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/integration/test_strategic_abilities.py`
- [ ] For each warp drive (`warp_drive_light`, `warp_drive_standard`, `warp_drive_heavy`, `warp_drive_capital`), migrate energy_cost:
  ```json
  // Before:
  "WarpJump": {"max_tonnage": 2000, "energy_cost": 500}

  // After:
  "WarpJump": {"max_tonnage": 2000},
  "ResourceConsumption": [
    {"resource": "energy", "amount": 500, "trigger": "warp_jump"}
  ]
  ```
- [ ] Verify existing ResourceConsumption lists are preserved (some components have multiple)
**Notes:** Legacy `energy_cost` support in ShipStatsService ensures old saves still work

#### Task 6.2: Add Test Component with Per-Turn Consumption [Simple]
**File:** `data/components.json`
**Tests:** Manual verification
- [ ] Add test component for per_turn trigger (optional, for verification):
  ```json
  "test_sensor_array": {
    "name": "Test Sensor Array",
    "type_str": "Sensor",
    "max_hp": 10,
    "mass": 50,
    "abilities": {
      "ResourceConsumption": [
        {"resource": "energy", "amount": 10, "trigger": "per_turn"}
      ]
    }
  }
  ```
**Notes:** Can be removed after verification or kept as example

---

### Phase 7: Update Tests [Medium]
**Objective:** Update test files for new resource system
**Status:** Not Started

#### Task 7.1: Update ShipStatsService Tests [Medium]
**File:** `tests/unit/strategy/test_ship_stats_service.py`
**Tests:** Self-testing
- [ ] Update mock fixtures to include new return structure fields
- [ ] Add tests for generic `resource_storage` dict
- [ ] Add tests for `resource_consumption_per_turn` (new trigger)
- [ ] Add tests for `warp_resource_costs` dict
- [ ] Add tests for `component_toggles` parameter
**Notes:**

#### Task 7.2: Update Fleet Tests [Medium]
**File:** `tests/unit/strategy/test_fleet.py`
**Tests:** Self-testing
- [ ] Add tests for `has_resources_for_movement()`
- [ ] Add tests for `consume_movement_resources()`
- [ ] Add tests for generic `get_warp_resource_costs()`
- [ ] Verify backward compatibility wrappers still work
**Notes:**

#### Task 7.3: Update Integration Tests [Simple]
**File:** `tests/integration/test_strategic_abilities.py`
**Tests:** Self-testing
- [ ] Update any mocks that expect specific stat keys
- [ ] Add test for warp with `trigger: 'warp_jump'` ResourceConsumption
**Notes:**

#### Task 7.4: Add New Resource System Tests [Medium]
**File:** `tests/unit/strategy/test_resource_system.py` (NEW)
**Tests:** Self-testing
- [ ] Test adding custom resource type to registry
- [ ] Test ship tracks custom resource levels
- [ ] Test per-turn consumption over 100 ticks
- [ ] Test auto-disable on resource depletion
- [ ] Test component toggle affects stats
- [ ] Test backward compatibility with old save format
**Notes:**

---

## Verification Checklist

### After Each Phase
- [ ] Run `pytest tests/unit/strategy/` - all tests pass
- [ ] Run game, create fleet, move fleet - no crashes
- [ ] Check logs for warnings/errors

### Final Verification
1. **Existing functionality preserved:**
   - [ ] Run `pytest tests/` - full suite passes
   - [ ] Fleet movement consumes fuel correctly
   - [ ] Warp jumps consume energy correctly
   - [ ] Damaged ships have reduced stats

2. **Generic resources work:**
   - [ ] Add "glag" to `resources.json`
   - [ ] Add component with `ResourceStorage: {resource: "glag", amount: 100}`
   - [ ] Add component with `ResourceConsumption: {resource: "glag", trigger: "per_turn", amount: 10}`
   - [ ] Verify ship tracks glag levels
   - [ ] Verify glag consumed over turn

3. **Warp costs data-driven:**
   - [ ] Modify warp drive to use fuel instead of energy
   - [ ] Verify fleet checks fuel for warp capability

4. **Component toggle works:**
   - [ ] Disable a component manually via `set_component_enabled()`
   - [ ] Verify stats recalculate
   - [ ] Verify disabled component doesn't consume resources

5. **Auto-disable works:**
   - [ ] Create ship with per_turn consumption
   - [ ] Deplete the resource
   - [ ] Verify component auto-disables

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All Phase 7 tasks checked off
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Final verification complete
- [ ] Audit passed
- [ ] User verified
