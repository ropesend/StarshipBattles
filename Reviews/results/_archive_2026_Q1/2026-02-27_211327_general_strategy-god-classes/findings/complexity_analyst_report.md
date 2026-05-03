# Complexity Analyst Report: Strategy God Classes

**Review Date:** 2026-02-27
**Scope:** Strategy domain models (~9,250 lines across 33 files)
**Focus:** God class accumulation, serialization complexity, branching depth, public API bloat

---

## Summary

- **Total issues found:** 15
- **Critical:** 3
- **Major:** 7
- **Minor:** 3
- **Info:** 2

### Key Findings

The primary complexity hotspots are concentrated in three god classes:
1. **Fleet.from_dict()** - 95 lines, 16 branches, 7 distinct target formats
2. **FleetNavigationService.project_path()** - 150 lines, 14 branches, state machine simulation
3. **FleetOrderProcessor.process_colonize()** - 109 lines, 9 branches, validation + mutation interleaving

Fleet extraction (PROJ-87 Phase 3-4) successfully reduced **direct** complexity but increased **compositional** complexity with 3 delegates, 13 pass-through methods, and 6 property aliases.

---

## Complexity Scorecards

### Fleet (fleet.py) - 552 lines

**Class-Level Metrics:**
- Total public methods: **37** (God class threshold: 30+)
- Private methods: 1
- Properties: 6
- Pass-through delegation methods: ~13 (35% of public API)
- Distinct responsibility domains: 6 (movement, orders, resources, cargo, capabilities, battle conversion)

**Method Complexity:**
- Longest method: `from_dict()` (95 lines)
- Methods > 30 lines: 3 (`from_dict`: 95, `resolve_order_references`: 56, `to_dict`: 39)
- Methods with CC > 10: 2 (`from_dict`: ~16 branches, `resolve_order_references`: 9 branches)
- Methods with nesting > 3: 1 (`from_dict`)
- Methods with > 4 params: 0

**Serialization Complexity (from_dict):**
- **95 lines, 16 conditional branches**
- Handles **7 distinct target formats**:
  1. `{'q': x, 'r': y}` - HexCoord for MOVE/WARP
  2. `{'type': 'fleet_ref', 'id': xxx}` - Fleet reference for MOVE_TO_FLEET
  3. `{'type': 'raw', 'value': str}` - Fallback string
  4. `{'type': 'transfer', 'value': {...}}` - TRANSFER params
  5. `{'type': 'planet_ref', 'id': xxx}` - Planet reference
  6. `{'type': 'ship_id_list', 'value': [...]}` - Ship IDs for SELF_DESTRUCT
  7. `{'type': 'warp_params', 'value': {...}}` - Warp parameters
- Lines 436-478: Nested if-elif chain (7 levels deep) for target resolution
- Error handling: Corrupt entries skipped with warnings (lines 419-423, 443-478)

**Delegate Impact (PROJ-87):**
- 3 delegate instances: `_resource_agg`, `_capabilities`, `_battle`
- 13 pass-through methods added to public API (lines 239-314)
- Delegate initialization in `__init__` (lines 137-144)
- **Observation:** Delegation reduced measured complexity within individual methods but did NOT reduce overall class responsibility count

**Public API Bloat:**
- 37 public methods across 6 domains
- Movement resource methods: 5 (lines 239-275)
- Cargo methods: 4 (lines 282-297)
- Capability queries: 3 (lines 203-237)
- Battle conversion: 3 (lines 299-321)
- Order management: 6 (lines 323-347)
- Core fleet methods: 16 (add_ship, remove_ship, merge_with, etc.)

---

### Planet (planet.py) - 499 lines

**Class-Level Metrics:**
- Total public methods: **10** (Below god class threshold)
- Private methods: 0
- Properties: 6
- Distinct responsibility domains: 5 (physics, grid, facilities, resources, population)
- Field count: **26 dataclass fields** (High - but dataclasses are designed for this)

**Method Complexity:**
- Longest method: `from_dict()` (94 lines)
- Methods > 30 lines: 2 (`from_dict`: 94, `to_dict`: 52)
- Methods with CC > 10: 0
- Methods with nesting > 3: 0
- Methods with > 4 params: 0

**Serialization Complexity (from_dict):**
- **94 lines, 0 conditional branches** (all validation is extracted)
- Uses validation helpers: `require_keys`, `validate_enum`, `validate_positive`, `validate_non_negative`
- Lines 424-458: 14 required keys validated upfront
- Lines 460-471: Resilient deserialization for facilities and populations (skip bad, log warning)
- **Observation:** Excellent example of validation extraction - no inline conditionals

**Field Responsibility Analysis:**
- Physics fields (9): mass, radius, surface_area, density, surface_gravity, surface_pressure, surface_temperature, surface_water, atmosphere
- Classification (2): planet_type, orbit_parent_name
- Empire (2): owner_id, construction_queue
- Resources (1): resources dict
- Facilities (1): facilities list
- Population (1): populations list
- Metadata (4): id, image_id, image_rotation, diameter_hexes
- Location (2): location, orbit_distance
- Internal (4): tectonic_activity, magnetic_field

**Properties (6):**
- `total_pressure_atm` (line 282) - Simple calculation
- `max_population` (line 287) - Derived from surface_area
- `total_population` (line 301) - Sum aggregation
- `has_space_shipyard` (line 306) - Facility query
- `context_type` (line 311) - Protocol compliance
- `occupied_hexes` (line 265) - Multi-hex zone support

**Cohesion Assessment:**
- **Low cohesion**: Methods touch different field clusters
- Physics calculations use: mass, radius, surface_area
- Empire methods use: owner_id, construction_queue, facilities
- Population methods use: populations list
- LCOM score would be high (many disjoint field sets)

---

### ShipInstance (ship_instance.py) - 741 lines

**Class-Level Metrics:**
- Total public methods: **43** (God class threshold: 30+)
- Private methods: 1
- Properties: 4
- Distinct responsibility domains: 6 (state, resources, cargo, combat, serialization, display)
- Delegate count: 3 (resource manager, cargo manager, display formatter)

**Method Complexity:**
- Longest method: `to_ship()` (57 lines)
- Methods > 30 lines: 7 (avg 47 lines)
- Methods with CC > 10: 0
- Methods with nesting > 3: 1 (`to_ship()`)
- Methods with > 4 params: 1 (`create()` - 6 params, but 3 optional)

**Complex Methods:**
1. `to_ship()` - 57 lines, 9 branches - Converts strategy instance to simulation Ship
2. `create()` - 55 lines, 1 branch - Factory method with empire serial tracking
3. `get_damaged_components_by_layer()` - 43 lines, 6 branches - Layer matching algorithm
4. `from_dict()` - 43 lines, 4 branches - Deserialization with validation
5. `from_ship()` - 42 lines, 4 branches - Reverse conversion from simulation
6. `update_from_ship()` - 34 lines, 5 branches - Battle result sync
7. `get_calculated_stats()` - 33 lines, 1 branch - Lazy stats calculation with caching

**Delegate Impact (PROJ-86/87):**
- 3 delegate instances: `_resource_mgr`, `_cargo_mgr`, `_display_fmt`
- Pass-through methods: ~15 (resource: 5, cargo: 5, display: 5)
- **Observation:** Delegates encapsulate implementation but public API remains large

**Public API by Domain:**
- Resource methods (9): get_resource_capacity, get_current_resource, consume_resource, get_all_resource_costs_per_hex, etc.
- Cargo methods (5): get_cargo_capacity, load_cargo, unload_cargo, etc.
- State queries (6): is_damaged, is_combat_capable, get_hp_percentage, etc.
- Display methods (7): get_display_id, get_status_text, get_hp_display, etc.
- Serialization (4): to_dict, from_dict, to_json, from_json
- Component management (4): set_component_enabled, is_component_enabled, invalidate_stats_cache, etc.
- Combat conversion (3): to_ship, from_ship, update_from_ship
- Factories (2): create, clone
- Repair/resupply (2): repair, resupply

---

### FleetResourceAggregator (fleet_resource_aggregator.py) - 333 lines

**Class-Level Metrics:**
- Total public methods: **13** (Focused delegate)
- Private methods: 2 (helper consolidation in PROJ-204)
- Properties: 0
- Responsibility: Resource aggregation across fleet ships

**Method Complexity:**
- Longest method: `get_capability_summary()` (17 lines)
- Methods > 30 lines: 0
- Methods with CC > 10: 0
- All methods under 40 lines, low branching

**Cohesion:**
- **High cohesion** - all methods aggregate ship resources
- Two helper patterns (PROJ-204):
  - `_accumulate_ship_costs()` - DRY cost collection
  - `_verify_and_consume_resources()` - Atomic verify+consume

**Complexity Assessment:**
- **Well-focused delegate** - single responsibility, low complexity
- No god class indicators

---

### FleetOrderProcessor (fleet_order_processor.py) - 648 lines

**Class-Level Metrics:**
- Total public methods: 6 (process_join_fleet, process_colonize, process_transfer, execute_action_order, process_end_turn_orders, process_instant_orders)
- Private methods: 4 (_execute_fleet_transfer, _execute_load, _execute_unload, _transfer_founding_population)
- Properties: 0
- Responsibility: Order lifecycle management

**Method Complexity:**
- Longest method: `process_colonize()` (109 lines, 9 branches)
- Methods > 30 lines: 9
- Methods with CC > 10: 0 (highest is 15 branches in process_transfer)
- Methods with > 4 params: 6 (parameter count 5-7)

**Complex Methods:**
1. `process_colonize()` - **109 lines, 9 branches** - Validation + mutation interleaving
2. `process_transfer()` - 89 lines, **15 branches** - Multi-target transfer handling
3. `execute_action_order()` - 78 lines, 5 branches - Handler registry dispatch
4. `_transfer_founding_population()` - 66 lines, 2 branches - Population seeding logic
5. `_execute_unload()` - 48 lines, 5 branches - Fleet → colony transfer
6. `_execute_load()` - 47 lines, 4 branches - Colony → fleet transfer
7. `process_join_fleet()` - 41 lines, 3 branches - Fleet merge validation
8. `_execute_fleet_transfer()` - 38 lines, 2 branches - Fleet → fleet cargo transfer
9. `process_instant_orders()` - 35 lines, 6 branches - Co-located JOIN_FLEET processing

**Parameter Count Issues:**
- 6 methods with 5-7 parameters (smell: excessive coupling)
- Worst offenders:
  - `_execute_fleet_transfer()` - 7 params
  - `_execute_load()` - 7 params
  - `_execute_unload()` - 7 params
  - `execute_action_order()` - 6 params

**process_colonize() Deep Dive (109 lines):**
- Lines 145-162: Validation via ColonizeValidator
- Lines 164-188: Target planet resolution (7 branches for "Any" case)
- Lines 190-200: Pre-check colony ship availability (defensive)
- Lines 202-227: Execute colonization (mutation phase)
- **Issue:** Validation, resolution, and mutation are interleaved (hard to test independently)

---

### FleetNavigationService (fleet_navigation_service.py) - 653 lines

**Class-Level Metrics:**
- Total public methods: 9
- Private methods: 3
- Properties: 0
- Responsibility: Pure navigation calculations + projection

**Method Complexity:**
- Longest method: `project_path()` (**150 lines, 14 branches**)
- Methods > 30 lines: 7
- Methods with CC > 10: 2 (`project_path`: 14, `compute_next_step`: 11)
- Methods with nesting > 3: 1 (`project_path`)

**Complex Methods:**
1. `project_path()` - **150 lines, 14 branches** - Multi-turn path simulation with action time accounting
2. `compute_next_step()` - 107 lines, 11 branches - Pure state machine for single step
3. `_resolve_warp_exit()` - 48 lines, 7 branches - Warp point resolution logic
4. `calculate_fleet_next_hex()` - 44 lines, 5 branches - Mutation bridge wrapper
5. `compute_path_for_warp()` - 37 lines, 4 branches - Warp-specific path calculation
6. `compute_path()` - 36 lines, 2 branches - Standard pathfinding
7. `get_destination()` - 34 lines, 4 branches - Order → destination resolution

**project_path() Deep Dive (150 lines):**
- Lines 413-457: Setup (state snapshot, turn tracking, safety limits)
- Lines 459-563: Main simulation loop (state machine advancement)
- Lines 466-499: Action order handling (action_time consumption) - PROJ-187
- Lines 500-520: Path recalculation for movement orders
- Lines 522-560: Step execution (segment generation, state update)
- **Cyclomatic Complexity:** ~14 (nested if statements, while loops)
- **Nesting Depth:** 4+ levels
- **Issue:** Single monolithic loop handles multiple order types and state transitions

---

### PlanetGenerator (planet_gen.py) - 544 lines

**Class-Level Metrics:**
- Total public methods: 1 (generate_system_bodies)
- Private methods: 9
- Properties: 0
- Responsibility: Procedural planet generation

**Method Complexity:**
- Longest method: `_generate_orbital_slots()` (87 lines, 11 branches)
- Methods > 30 lines: 7
- Methods with CC > 10: 2 (`_determine_type`: 14 branches, `_generate_orbital_slots`: 11 branches)
- Methods with > 4 params: 2 (`_create_single_planet`: 6 params, `_determine_type`: 7 params)

**Complex Methods:**
1. `_generate_orbital_slots()` - 87 lines, **11 branches** - Orbital distribution with constraints
2. `_determine_type()` - 78 lines, **14 branches** - Planet classification ladder
3. `_create_single_planet()` - 61 lines, 1 branch - Planet object construction
4. `generate_system_bodies()` - 46 lines, 4 branches - Top-level orchestration
5. `_generate_mass_constrained()` - 44 lines, 4 branches - Biased mass generation
6. `_generate_moons()` - 34 lines, 5 branches - Moon placement logic
7. `_generate_resources()` - 34 lines, 1 branch - Resource distribution

**_determine_type() Deep Dive (78 lines, 14 branches):**
- Classification ladder with 12 PlanetType outcomes
- Branching based on: mass thresholds, temperature ranges, pressure, water coverage, activity
- Lines 451-509: Cascading if-elif chain (12 levels deep conceptually)
- **Issue:** High cyclomatic complexity from classification tree
- **Mitigation:** Data-driven config via ClassificationConfig (good practice)

**Parameter Count Issues:**
- `_create_single_planet()` - 6 params (loc, orbit_dist, mass, base_temp, total_flux, image_registry)
- `_determine_type()` - 7 params (mass, temp, pressure, water, atmosphere, activity, cfg)
- **Smell:** Excessive coupling, consider parameter object pattern

---

## Findings

### Critical Issues

#### CX-001: CRITICAL: Fleet.from_dict() Polymorphic Serialization Hell
**Location:** `game/strategy/data/fleet.py:389-483`
**Lines:** 95 lines, 16 branches, 7 target formats

**Issue:**
The `from_dict()` method handles **7 distinct target formats** for FleetOrder deserialization:
1. HexCoord dict `{'q': x, 'r': y}`
2. Fleet reference `{'type': 'fleet_ref', 'id': xxx}`
3. Planet reference `{'type': 'planet_ref', 'id': xxx}`
4. TRANSFER params `{'type': 'transfer', 'value': {...}}`
5. Ship ID list `{'type': 'ship_id_list', 'value': [...]}`
6. Warp params `{'type': 'warp_params', 'value': {...}}`
7. Raw string fallback `{'type': 'raw', 'value': str}`

Lines 443-478 contain a 7-branch nested if-elif chain:
```python
if isinstance(target_data, dict):
    if 'q' in target_data and 'r' in target_data:
        target = HexCoord(...)
    elif target_data.get('type') == 'fleet_ref':
        target = {'_fleet_ref': ...}
    elif target_data.get('type') == 'transfer':
        target = target_data['value']
    elif target_data.get('type') == 'planet_ref':
        target = {'_planet_ref': ...}
    elif target_data.get('type') == 'ship_id_list':
        target = target_data['value']
    elif target_data.get('type') == 'warp_params':
        target = target_data['value']
    elif target_data.get('type') == 'raw':
        target = target_data['value']
```

**Impact:**
- Cyclomatic complexity: 16 (threshold: 10)
- Maintenance burden: Every new order type requires adding a new branch
- Testability: 7 code paths to test for a single method
- Readability: Dense nesting makes flow hard to follow
- Save format fragility: 7 formats must be maintained for backward compatibility

**Recommendation:**
Extract polymorphic deserialization to a **strategy pattern** or **factory**:
```python
class OrderTargetDeserializer:
    _handlers = {
        'fleet_ref': lambda data: {'_fleet_ref': data['id']},
        'planet_ref': lambda data: {'_planet_ref': data['id']},
        'transfer': lambda data: data['value'],
        'ship_id_list': lambda data: data['value'],
        'warp_params': lambda data: data['value'],
        'raw': lambda data: data['value'],
    }

    @classmethod
    def deserialize(cls, target_data):
        if isinstance(target_data, dict):
            if 'q' in target_data and 'r' in target_data:
                return HexCoord(target_data['q'], target_data['r'])
            target_type = target_data.get('type')
            handler = cls._handlers.get(target_type)
            if handler:
                return handler(target_data)
        return None
```

Then `from_dict()` becomes:
```python
target = OrderTargetDeserializer.deserialize(target_data)
```

**Effort:** Medium (1-2 days: extract, test 7 save formats, regression test)

---

#### CX-002: CRITICAL: FleetNavigationService.project_path() State Machine in 150 Lines
**Location:** `game/strategy/services/fleet_navigation_service.py:413-562`
**Lines:** 150 lines, 14 branches, 4+ nesting levels

**Issue:**
The `project_path()` method simulates multi-turn fleet movement in a single 150-line function:
- Lines 459-563: Main simulation loop (104 lines)
- Lines 466-499: Action order handling (33 lines nested)
- Lines 500-520: Path recalculation (20 lines nested)
- Lines 522-560: Step execution (38 lines nested)

Nested state machine logic:
```python
while (state.path or state.orders) and current_turn < max_turns:
    iterations += 1
    if iterations > max_steps:
        break

    if not state.path and state.orders:
        order = state.orders[0]

        if order.type not in MOVEMENT_ORDER_TYPES:
            # 33 lines: action_time consumption
            while action_time > 0 and current_turn < max_turns:
                # nested loop

        destination = self.get_destination(...)
        if destination is None:
            break

        # 20 lines: path calculation

    if not state.path:
        break

    # 38 lines: step execution
```

**Impact:**
- Cyclomatic complexity: 14 (threshold: 10)
- Nesting depth: 4+ (threshold: 3)
- Single Responsibility violation: handles action time, path calculation, step execution, turn accounting
- Testability: Hard to test individual state transitions in isolation
- Maintenance: Any change to turn mechanics requires editing this monolith

**Recommendation:**
Extract state transition logic into separate methods:
```python
def project_path(self, fleet, galaxy, max_turns=10, component_registry=None):
    sim = PathSimulator(fleet, galaxy, max_turns, component_registry)
    return sim.simulate()

class PathSimulator:
    def simulate(self):
        while self._should_continue():
            self._advance_tick()
        return self.segments

    def _should_continue(self):
        return (self.state.path or self.state.orders) and self.current_turn < self.max_turns

    def _advance_tick(self):
        if not self.state.path:
            self._handle_order()
        if self.state.path:
            self._execute_step()

    def _handle_order(self):
        # Extract action order handling (lines 466-499)
        ...

    def _execute_step(self):
        # Extract step execution (lines 522-560)
        ...
```

**Effort:** Medium (2-3 days: extract simulator class, preserve behavior, test all order types)

---

#### CX-003: CRITICAL: FleetOrderProcessor.process_colonize() Validation/Mutation Interleaving
**Location:** `game/strategy/engine/fleet_order_processor.py:120-228`
**Lines:** 109 lines, 9 branches

**Issue:**
The `process_colonize()` method interleaves validation, resolution, and mutation phases:
- Lines 145-162: Validation via ColonizeValidator
- Lines 164-188: Target planet resolution ("Any" case handling)
- Lines 190-200: Pre-check colony ship availability (defensive)
- Lines 202-204: **Mutation begins** (empire.add_colony, fleet.pop_order)
- Lines 206-210: More mutation (_transfer_founding_population, fleet.remove_ship)
- Lines 212-216: Cleanup mutation (empire.remove_fleet if empty)

**Problem:** Mutation scattered across 26 lines makes rollback impossible and testing hard:
```python
# Validation phase
validation = ColonizeValidator.validate(...)
if not validation.is_valid:
    fleet.pop_order()
    return ColonizeResult(colonized=False)

# Resolution phase (25 lines)
if target_planet is not None:
    final_planet = target_planet
else:
    # 18 lines: pick matching candidate
    ...

# Pre-check phase
colony_ship = ColonizeValidator.find_ship_with_colony_pod(...)
if colony_ship is None:
    fleet.pop_order()
    return ColonizeResult(colonized=False)

# MUTATION PHASE (scattered)
empire.add_colony(final_planet)  # Line 203
fleet.pop_order()  # Line 204
self._transfer_founding_population(...)  # Line 207
fleet.remove_ship(colony_ship)  # Line 210
if len(fleet.ships) == 0:
    empire.remove_fleet(fleet)  # Line 215
```

**Impact:**
- Testability: Can't test validation without mutation side effects
- Atomicity: No rollback if later mutations fail
- Readability: Validation scattered across 67 lines before first mutation
- Maintenance: Hard to reason about preconditions vs. postconditions

**Recommendation:**
Separate into **validate → resolve → mutate** phases:
```python
def process_colonize(self, fleet, empire, galaxy, component_registry):
    # Phase 1: Validate (pure, no mutations)
    validation = self._validate_colonization(fleet, galaxy, component_registry)
    if not validation.is_valid:
        fleet.pop_order()
        return ColonizeResult(colonized=False)

    # Phase 2: Resolve (pure, returns final_planet and colony_ship)
    resolution = self._resolve_colonization_targets(
        fleet, validation.target, galaxy, component_registry
    )
    if not resolution.valid:
        fleet.pop_order()
        return ColonizeResult(colonized=False)

    # Phase 3: Mutate (all mutations in one atomic block)
    self._execute_colonization(
        fleet, empire, resolution.planet, resolution.colony_ship
    )

    return ColonizeResult(colonized=True, planet_name=resolution.planet.name)

def _execute_colonization(self, fleet, empire, planet, colony_ship):
    """Atomic mutation block."""
    empire.add_colony(planet)
    fleet.pop_order()
    self._transfer_founding_population(fleet, planet, empire)
    fleet.remove_ship(colony_ship)
    if len(fleet.ships) == 0:
        empire.remove_fleet(fleet)
```

**Effort:** Medium (2 days: extract phases, test all edge cases, regression test)

---

### Major Issues

#### CX-004: MAJOR: Fleet Public API Bloat (37 Methods)
**Location:** `game/strategy/data/fleet.py`
**Metrics:** 37 public methods, 6 responsibility domains, 13 pass-through delegations

**Issue:**
Fleet class has 37 public methods across 6 distinct domains:
1. **Movement resources** (5 methods): get_movement_resource_costs, has_resources_for_movement, consume_movement_resources, get_warp_resource_costs, has_resources_for_warp, consume_warp_resources
2. **Cargo** (4 methods): get_fleet_cargo_capacity, get_fleet_cargo_current, load_cargo_to_fleet, unload_cargo_from_fleet
3. **Capabilities** (3 methods): can_build_type, can_use_warp, get_warp_limiting_ship, fuel_endurance, warp_jumps_remaining, get_capability_summary
4. **Battle conversion** (3 methods): to_battle_ships, _default_formation_positions, update_from_battle_results
5. **Order management** (6 methods): add_order, clear_orders, get_current_order, pop_order, merge_with
6. **Core fleet** (16 methods): add_ship, remove_ship, get_ship_names, get_combat_capable_ships, etc.

**Impact:**
- God class indicator: 37 methods exceeds threshold of 30
- Low cohesion: 6 domains touch different collaborators
- Facade bloat: 13 methods are pass-throughs to delegates (35% of API)
- Test surface: Large public API increases test complexity

**Recommendation:**
Create **domain-specific facades** to reduce direct API exposure:
```python
fleet.movement.get_resource_costs()  # Instead of fleet.get_movement_resource_costs()
fleet.movement.has_resources()       # Instead of fleet.has_resources_for_movement()
fleet.cargo.capacity('passengers')   # Instead of fleet.get_fleet_cargo_capacity('passengers')
fleet.capabilities.can_warp()        # Instead of fleet.can_use_warp()
```

Reduce Fleet public API to core operations only:
- add_ship, remove_ship (core composition)
- orders, path (movement state)
- movement, cargo, capabilities, battle (domain facades)

**Effort:** Complex (4-5 days: extract facades, update 50+ call sites, regression test)

---

#### CX-005: MAJOR: ShipInstance Public API Bloat (43 Methods)
**Location:** `game/strategy/data/ship_instance.py`
**Metrics:** 43 public methods, 6 responsibility domains, 15 pass-through delegations

**Issue:**
ShipInstance has 43 public methods across 6 domains:
1. **Resources** (9 methods): get_resource_capacity, get_current_resource, consume_resource, get_all_resource_costs_per_hex, get_all_resource_costs_per_turn, get_warp_resource_costs, resupply
2. **Cargo** (5 methods): get_cargo_capacity, get_current_cargo, get_cargo_space_available, load_cargo, unload_cargo
3. **Display** (7 methods): get_display_id, get_status_text, get_hp_display, get_resource_display, get_resource_percentage, get_component_damage_summary, get_damaged_component_count
4. **Combat** (6 methods): to_ship, from_ship, update_from_ship, is_damaged, is_combat_capable, get_hp_percentage
5. **Serialization** (4 methods): to_dict, from_dict, to_json, from_json
6. **State management** (12 methods): get_calculated_stats, invalidate_stats_cache, set_component_enabled, is_component_enabled, repair, clone, etc.

**Impact:**
- God class indicator: 43 methods exceeds threshold of 30
- Facade bloat: 15 methods delegate to `_resource_mgr`, `_cargo_mgr`, `_display_fmt`
- Mixed abstraction levels: Low-level (get_cargo_space_available) + high-level (to_ship) in same class
- Test surface: 43 public methods = 43+ test scenarios

**Recommendation:**
Same as CX-004: Extract domain facades:
```python
ship.resources.capacity('fuel')
ship.resources.consume('fuel', 100)
ship.cargo.load('passengers', 50)
ship.display.status_text()
ship.display.hp_percentage()
```

**Effort:** Complex (4-5 days: extract facades, update call sites, regression test)

---

#### CX-006: MAJOR: Planet Low Cohesion (26 Fields, 5 Domains)
**Location:** `game/strategy/data/planet.py`
**Metrics:** 26 dataclass fields, 5 distinct responsibility domains

**Issue:**
Planet has 26 fields across 5 domains that rarely interact:
- **Physics** (9 fields): mass, radius, surface_area, density, surface_gravity, surface_pressure, surface_temperature, surface_water, atmosphere
- **Classification** (2 fields): planet_type, orbit_parent_name
- **Empire** (2 fields): owner_id, construction_queue
- **Resources** (1 field): resources dict
- **Facilities** (2 fields): facilities list, populations list

LCOM (Lack of Cohesion of Methods) would be high:
- `max_population` only uses: surface_area
- `total_population` only uses: populations
- `has_space_shipyard` only uses: facilities
- `can_build_type` only uses: facilities
- `add_production` only uses: construction_queue

**Impact:**
- Low cohesion: Methods touch disjoint field sets
- Mixed responsibilities: Physics + empire + resources in one class
- Change cascades: Adding empire features may trigger physics recalculation tests

**Recommendation:**
Split into **data tier** (physics) + **gameplay tier** (empire/facilities):
```python
@dataclass
class PlanetBody:
    """Pure physical properties."""
    mass: float
    radius: float
    surface_area: float
    density: float
    surface_gravity: float
    # ... 9 physics fields

@dataclass
class Colony:
    """Empire-owned planet gameplay state."""
    planet_body: PlanetBody  # Reference to physical data
    owner_id: int
    facilities: List[PlanetaryFacility]
    populations: List[SpeciesPopulation]
    construction_queue: List
    resources: Dict
```

**Effort:** Complex (5+ days: split class, migrate 200+ references, test physics vs. empire isolation)

---

#### CX-007: MAJOR: FleetOrderProcessor Excessive Parameter Counts (6 Methods with 5-7 Params)
**Location:** `game/strategy/engine/fleet_order_processor.py`
**Methods:** _execute_fleet_transfer (7), _execute_load (7), _execute_unload (7), execute_action_order (6), process_colonize (5), process_transfer (4)

**Issue:**
Six methods have 5-7 parameters, indicating excessive coupling:

```python
def _execute_fleet_transfer(
    self,
    fleet: Fleet,
    target_fleet: Fleet,
    cargo_type: str,
    direction: str,
    amount: int,
    species_id: str = None  # 7 params
) -> int:

def _execute_load(
    self,
    fleet: Fleet,
    planet: 'Planet',
    cargo_type: str,
    amount: int,
    empire: 'Empire',
    species_id: str = None  # 7 params
) -> int:

def execute_action_order(
    self,
    fleet: Fleet,
    empire: 'Empire',
    galaxy: 'Galaxy',
    component_registry: Optional[Dict[str, Any]] = None,
    empires: Optional[List['Empire']] = None  # 6 params
) -> bool:
```

**Impact:**
- Coupling: 7 dependencies per method
- Testability: Need to mock 7 objects per test
- Maintainability: Adding a parameter requires updating all call sites
- Readability: Long parameter lists are hard to scan

**Recommendation:**
Use **parameter object pattern**:
```python
@dataclass
class TransferContext:
    fleet: Fleet
    target: Union[Fleet, Planet]
    cargo_type: str
    direction: str
    amount: int
    species_id: Optional[str] = None
    empire: Optional[Empire] = None

def _execute_transfer(self, ctx: TransferContext) -> int:
    if is_fleet(ctx.target):
        return self._execute_fleet_transfer(ctx)
    elif is_planet(ctx.target):
        if ctx.direction == "load":
            return self._execute_load(ctx)
        else:
            return self._execute_unload(ctx)
```

**Effort:** Medium (2-3 days: create context objects, refactor signatures, update call sites)

---

#### CX-008: MAJOR: PlanetGenerator._determine_type() Classification Tree Hell (78 Lines, 14 Branches)
**Location:** `game/strategy/data/planet_gen.py:432-509`
**Lines:** 78 lines, 14 branches

**Issue:**
The `_determine_type()` method is a 78-line cascading if-elif chain with 14 branches for planet classification:
```python
def _determine_type(self, mass, temp, pressure, water, atmosphere, activity=0.0):
    cfg = get_classification_config()

    # Branch 1-3: Gas Giants & Ice Giants
    if mass > cfg.giant_min:
        if temp > 600 and pressure < cfg.chthonian_max:
            return PlanetType.CHTHONIAN
        if mass > cfg.gas_giant_min:
            return PlanetType.JOVIAN
        return PlanetType.ICE_GIANT

    # Branch 4-5: Dwarf Planets
    if mass < cfg.dwarf_max:
        if temp < cfg.ice_dwarf_max:
            return PlanetType.ICE_DWARF
        return PlanetType.PLANETOID

    # Branch 6: Magma
    if temp > cfg.magma or (temp > cfg.magma_activity and activity > cfg.activity_magma_threshold):
        return PlanetType.MAGMA

    # Branch 7-9: Barren / Dead Worlds
    if pressure < cfg.vacuum:
        if temp < cfg.cold_limit:
            return PlanetType.CRYOPLANET
        return PlanetType.BARREN

    # Branch 10-14: Water / Ice
    if temp < cfg.cryo_max:
        return PlanetType.CRYOPLANET
    if water > cfg.ocean_world:
        return PlanetType.PELAGIC
    if water < cfg.arid:
        return PlanetType.ARID
    if cfg.continental_temp_min <= temp <= cfg.continental_temp_max and pressure > cfg.continental_pressure_min:
        return PlanetType.CONTINENTAL
    if temp < 350 and water > cfg.continental_water_min:
        return PlanetType.CONTINENTAL
    if temp >= 350:
        return PlanetType.ARID

    return PlanetType.BARREN
```

**Impact:**
- Cyclomatic complexity: 14 (threshold: 10)
- Maintenance: Any classification change requires editing this monolith
- Testability: 14 branches = 14+ test cases
- Readability: Hard to see decision tree structure

**Recommendation:**
Use **rule-based classification** with data-driven rules:
```python
@dataclass
class ClassificationRule:
    name: str
    planet_type: PlanetType
    conditions: List[Callable[[PlanetProps], bool]]

CLASSIFICATION_RULES = [
    ClassificationRule(
        name="Chthonian",
        planet_type=PlanetType.CHTHONIAN,
        conditions=[
            lambda p: p.mass > cfg.giant_min,
            lambda p: p.temp > 600,
            lambda p: p.pressure < cfg.chthonian_max,
        ]
    ),
    # ... 11 more rules
]

def _determine_type(self, mass, temp, pressure, water, atmosphere, activity):
    props = PlanetProps(mass, temp, pressure, water, atmosphere, activity)
    for rule in CLASSIFICATION_RULES:
        if all(cond(props) for cond in rule.conditions):
            return rule.planet_type
    return PlanetType.BARREN
```

**Effort:** Medium (2-3 days: extract rules, test all 12 classifications, regression test)

---

#### CX-009: MAJOR: FleetNavigationService.compute_next_step() State Machine Nesting (107 Lines, 11 Branches)
**Location:** `game/strategy/services/fleet_navigation_service.py:305-411`
**Lines:** 107 lines, 11 branches

**Issue:**
The `compute_next_step()` method is a pure state machine that handles:
- Order validation (lines 323-332)
- WARP order special case at warp point (lines 342-362)
- Arrival at destination (lines 364-374)
- Path calculation (lines 376-384)
- Step execution (lines 387-409)

**Nesting depth:** 3-4 levels:
```python
def compute_next_step(self, state, galaxy):
    if not state.orders:
        return NavigationStep(...)

    order = state.orders[0]
    destination = self.get_destination(...)

    if destination is None:
        return NavigationStep(...)

    current_path = list(state.path)
    if self._needs_path_recalculation(...):
        current_path = []

    if not current_path:
        if order.type == OrderType.WARP and state.location == destination:
            exit_hex = self._resolve_warp_exit(...)
            if exit_hex:
                # ... construct new state
                return NavigationStep(...)
            else:
                return NavigationStep(...)

        if state.location == destination:
            # ... construct new state
            return NavigationStep(...)

        if order.type == OrderType.WARP:
            current_path = self.compute_path_for_warp(...)
        else:
            current_path = self.compute_path(...)

        if not current_path:
            return NavigationStep(...)

    if current_path:
        next_hex = current_path[0]
        # ... construct new state
        return NavigationStep(...)

    return NavigationStep(...)
```

**Impact:**
- Cyclomatic complexity: 11 (threshold: 10)
- Nesting depth: 3-4 (threshold: 3)
- Readability: Hard to follow state transitions
- Testability: 11 branches = 11+ test scenarios

**Recommendation:**
Use **early returns** and extract substates:
```python
def compute_next_step(self, state, galaxy):
    if not state.orders:
        return self._no_orders(state)

    order = state.orders[0]
    destination = self.get_destination(state, order, galaxy)

    if destination is None:
        return self._non_movement_order(state)

    if self._at_warp_point(state, order, destination):
        return self._execute_warp_transit(state, destination, galaxy)

    if state.location == destination:
        return self._complete_order(state)

    path = self._get_or_calculate_path(state, order, destination, galaxy)
    if not path:
        return self._no_path(state)

    return self._advance_along_path(state, path)
```

**Effort:** Medium (2 days: extract substates, preserve behavior, regression test)

---

#### CX-010: MAJOR: Fleet Delegate Complexity Trade-off (3 Delegates, 13 Pass-throughs)
**Location:** `game/strategy/data/fleet.py`
**Delegates:** FleetResourceAggregator (lines 137-138), FleetCapabilityCalculator (lines 140-141), FleetBattleAdapter (lines 143-144)

**Issue:**
PROJ-87 Phase 3-4 extracted 3 delegates to reduce Fleet complexity, but:
- **13 pass-through methods added** to Fleet public API (lines 239-314)
- **Compositional complexity increased**: Clients still call `fleet.method()` instead of `fleet.delegate.method()`
- **Measured complexity reduced** in individual methods but **overall class complexity unchanged**

Example pass-throughs:
```python
# Lines 239-275: Movement resource delegation (6 methods)
def get_movement_resource_costs(self) -> Dict[str, float]:
    return self._resource_agg.get_movement_resource_costs()

def has_resources_for_movement(self) -> bool:
    return self._resource_agg.has_resources_for_movement()

# Lines 282-297: Cargo delegation (4 methods)
def get_fleet_cargo_capacity(self, cargo_type: str) -> int:
    return self._resource_agg.get_fleet_cargo_capacity(cargo_type)

# Lines 299-321: Battle conversion delegation (3 methods)
def to_battle_ships(...) -> List['Ship']:
    return self._battle.to_battle_ships(...)
```

**Impact:**
- **Facade bloat**: 13/37 public methods (35%) are one-line pass-throughs
- **False complexity reduction**: Delegates hide implementation but don't reduce API surface
- **Maintenance burden**: Two places to update (Fleet + delegate)
- **Test duplication**: Test Fleet method + delegate method

**Recommendation:**
Expose delegates directly instead of wrapping:
```python
# Before (pass-through)
fleet.get_movement_resource_costs()

# After (direct delegate access)
fleet.resources.get_movement_costs()

# Fleet class becomes:
class Fleet:
    def __init__(self, ...):
        self.resources = FleetResourceAggregator(self)
        self.capabilities = FleetCapabilityCalculator(self)
        self.battle = FleetBattleAdapter(self)

    # NO pass-through methods - clients use delegates directly
```

**Effort:** Complex (4-5 days: remove pass-throughs, update 100+ call sites, regression test)

---

### Minor Issues

#### CX-011: MINOR: Fleet.resolve_order_references() Nested Loops (56 Lines, 9 Branches)
**Location:** `game/strategy/data/fleet.py:485-541`
**Lines:** 56 lines, 9 branches

**Issue:**
The `resolve_order_references()` method resolves `_fleet_ref` and `_planet_ref` markers after deserialization. It has 3 nested loops:
1. Build fleet lookup (lines 500-504)
2. Iterate orders (lines 509-540)
3. Remove invalid orders (lines 539-540)

**Impact:**
- Cyclomatic complexity: 9 (close to threshold of 10)
- Nesting: 3 levels (at threshold)
- Performance: O(empires × fleets × orders)

**Recommendation:**
Extract lookup building and reference resolution:
```python
def resolve_order_references(self, galaxy, empires):
    fleet_lookup = self._build_fleet_lookup(empires)
    invalid_indices = []

    for i, order in enumerate(self.orders):
        if not self._resolve_order_target(order, fleet_lookup, galaxy):
            invalid_indices.append(i)

    self._remove_invalid_orders(invalid_indices)

def _build_fleet_lookup(self, empires):
    return {f.id: f for e in empires for f in e.fleets}

def _resolve_order_target(self, order, fleet_lookup, galaxy):
    if '_fleet_ref' in order.target:
        return self._resolve_fleet_ref(order, fleet_lookup)
    elif '_planet_ref' in order.target:
        return self._resolve_planet_ref(order, galaxy)
    return True
```

**Effort:** Simple (1 day: extract helpers, test reference resolution)

---

#### CX-012: MINOR: Planet.from_dict() Validation Ceremony (94 Lines)
**Location:** `game/strategy/data/planet.py:406-499`
**Lines:** 94 lines, 0 branches

**Issue:**
Planet.from_dict() is 94 lines but has **zero** conditional branches. All complexity is in validation ceremony:
- Lines 424-428: 14 required keys validated
- Lines 431: Enum validation
- Lines 434-438: 3 positive value validations
- Lines 441-443: 3 non-negative value validations
- Lines 446-458: Location deserialization with error context

**This is actually GOOD design** (validation extracted from logic), but the sheer length is a smell.

**Impact:**
- Readability: 94 lines is long for a function with no branches
- Maintenance: Adding a field requires updating 3 places (require_keys, validate_X, constructor)

**Recommendation:**
Use **schema validation** with a declarative spec:
```python
PLANET_SCHEMA = {
    'required': ['name', 'location', 'orbit_distance', ...],
    'positive': ['mass', 'radius', 'surface_area', ...],
    'non_negative': ['orbit_distance', 'surface_pressure', ...],
    'enum': {'planet_type': PlanetType},
    'complex': {'location': hex_from_dict},
}

@classmethod
def from_dict(cls, data):
    validate_schema(data, PLANET_SCHEMA, 'Planet')
    facilities = deserialize_list(data.get('facilities', []), ...)
    populations = deserialize_list(data.get('populations', []), ...)
    return cls(**data, facilities=facilities, populations=populations)
```

**Effort:** Simple (1-2 days: create schema validator, test all validations)

---

#### CX-013: MINOR: ShipInstance Delegate Initialization Ceremony (__post_init__)
**Location:** `game/strategy/data/ship_instance.py:82-86`
**Lines:** 5 lines

**Issue:**
ShipInstance uses `__post_init__()` to initialize 3 delegates, but this adds complexity:
```python
def __post_init__(self) -> None:
    """Initialize delegate managers after dataclass init."""
    self._resource_mgr = ShipResourceManager(self)
    self._cargo_mgr = ShipCargoManager(self)
    self._display_fmt = ShipDisplayFormatter(self)
```

**Impact:**
- Initialization order fragility: Delegates assume dataclass fields are set
- Testability: Mock delegates require patching `__post_init__`
- Magic: Delegates initialized implicitly (not in `__init__` signature)

**Recommendation:**
Use **lazy initialization** instead:
```python
@property
def _resource_mgr(self):
    if not hasattr(self, '_resource_mgr_cache'):
        self._resource_mgr_cache = ShipResourceManager(self)
    return self._resource_mgr_cache
```

Or use **factory method** instead of dataclass:
```python
@classmethod
def create_from_design(cls, design_data, owner_id, ...):
    instance = cls(...)
    instance._resource_mgr = ShipResourceManager(instance)
    instance._cargo_mgr = ShipCargoManager(instance)
    instance._display_fmt = ShipDisplayFormatter(instance)
    return instance
```

**Effort:** Simple (1 day: convert to lazy properties, test initialization order)

---

### Info

#### CX-014: INFO: FleetResourceAggregator Well-Factored Delegate (333 Lines, 0 Methods > 30 Lines)
**Location:** `game/strategy/data/fleet_resource_aggregator.py`

**Observation:**
FleetResourceAggregator is a **well-designed delegate**:
- 13 public methods, all < 40 lines
- 2 helper methods consolidate loops (PROJ-204)
- High cohesion: All methods aggregate ship resources
- No god class indicators

**Metrics:**
- Longest method: `get_capability_summary()` (17 lines)
- Methods with CC > 10: 0
- Methods with nesting > 3: 0

**Example of good helper consolidation (PROJ-204):**
```python
def _accumulate_ship_costs(self, cost_getter):
    """Consolidate duplicated cost accumulation pattern."""
    total_costs = {}
    for ship in self._fleet.get_combat_capable_ships():
        ship_costs = cost_getter(ship)
        for resource_type, cost in ship_costs.items():
            total_costs[resource_type] = total_costs.get(resource_type, 0) + cost
    return total_costs
```

**Recommendation:**
This is a **model delegate** - use this pattern for other extractions.

**Effort:** N/A (informational)

---

#### CX-015: INFO: Planet Serialization Uses Validation Helpers (Good Practice)
**Location:** `game/strategy/data/planet.py:406-499`

**Observation:**
Planet.from_dict() demonstrates **excellent validation extraction**:
- Uses `require_keys()` for required field validation (line 424)
- Uses `validate_enum()` for enum validation (line 431)
- Uses `validate_positive()` for positive value validation (lines 434-438)
- Uses `validate_non_negative()` for non-negative validation (lines 441-443)
- Uses `deserialize_list()` for resilient list deserialization (lines 464-470)

**Result:** 94 lines but **0 conditional branches** in the method itself.

**Recommendation:**
Apply this pattern to Fleet.from_dict() to reduce its 16 branches.

**Effort:** N/A (informational)

---

## Top 5 Priority Issues

### 1. CX-001: Fleet.from_dict() Polymorphic Serialization Hell
**Impact:** Critical
**Complexity:** 95 lines, 16 branches, 7 target formats
**Fix Effort:** Medium (2 days)
**ROI:** High - reduces cyclomatic complexity from 16 → 4, improves maintainability

**Why prioritize:** This is the single most complex method in the entire scope. Every new order type adds a new branch. Fixing this prevents future accumulation.

---

### 2. CX-002: FleetNavigationService.project_path() State Machine in 150 Lines
**Impact:** Critical
**Complexity:** 150 lines, 14 branches, 4+ nesting
**Fix Effort:** Medium (3 days)
**ROI:** High - enables isolated testing of turn simulation logic

**Why prioritize:** This method simulates multi-turn movement and is critical for UI path projection. Extracting a PathSimulator class would make turn mechanics testable in isolation.

---

### 3. CX-003: FleetOrderProcessor.process_colonize() Validation/Mutation Interleaving
**Impact:** Critical
**Complexity:** 109 lines, validation scattered across 67 lines before mutation
**Fix Effort:** Medium (2 days)
**ROI:** High - enables atomic rollback, clearer validation → mutation separation

**Why prioritize:** Interleaved validation and mutation makes this method impossible to test in isolation and risky for refactoring.

---

### 4. CX-004: Fleet Public API Bloat (37 Methods)
**Impact:** Major
**Complexity:** 37 public methods, 13 pass-through delegations
**Fix Effort:** Complex (5 days)
**ROI:** Medium - reduces test surface, improves encapsulation

**Why prioritize:** God class with 37 methods is the root cause of many other issues (CX-010, CX-011). Fixing this via domain facades would simplify the entire Fleet API.

---

### 5. CX-007: FleetOrderProcessor Excessive Parameter Counts (6 Methods)
**Impact:** Major
**Complexity:** 6 methods with 5-7 parameters
**Fix Effort:** Medium (3 days)
**ROI:** Medium - reduces coupling, improves testability

**Why prioritize:** Parameter objects reduce coupling and make method signatures easier to evolve. This is a foundational refactor that would simplify many other issues.

---

## Ranked Complexity List

| Rank | Class | File | LOC | Public Methods | Longest Method | Max CC | Max Nesting |
|------|-------|------|-----|----------------|----------------|--------|-------------|
| 1 | **FleetNavigationService** | fleet_navigation_service.py | 653 | 9 | 150 lines | 14 | 4+ |
| 2 | **FleetOrderProcessor** | fleet_order_processor.py | 648 | 6 | 109 lines | 15 | 3 |
| 3 | **ShipInstance** | ship_instance.py | 741 | 43 | 57 lines | 9 | 3 |
| 4 | **Fleet** | fleet.py | 552 | 37 | 95 lines | 16 | 3 |
| 5 | **PlanetGenerator** | planet_gen.py | 544 | 1 | 87 lines | 14 | 3 |
| 6 | **Planet** | planet.py | 499 | 10 | 94 lines | 0 | 2 |
| 7 | **FleetResourceAggregator** | fleet_resource_aggregator.py | 333 | 13 | 17 lines | 2 | 2 |
| 8 | **BuildQueueSource** | build_queue_source.py | 255 | 0 | - | - | - |

---

## Conclusion

The strategy domain god classes exhibit three primary complexity anti-patterns:

1. **Polymorphic Serialization Explosion** (Fleet.from_dict): 7 target formats, 16 branches, 95 lines
2. **Monolithic State Machines** (FleetNavigationService.project_path): 150-line simulation loop
3. **Validation/Mutation Interleaving** (FleetOrderProcessor.process_colonize): 67 lines of validation before first mutation

**Key Observation:** Delegate extraction (PROJ-87) reduced **method-level** complexity but did NOT reduce **class-level** complexity:
- Fleet: 37 public methods (13 are pass-throughs to delegates)
- ShipInstance: 43 public methods (15 are pass-throughs to delegates)

**Recommendation:** Future god class decomposition should expose delegates directly rather than wrapping them in pass-through methods. This reduces API surface and eliminates facade bloat.

**Comparison:** FleetResourceAggregator (333 lines, 13 methods, all < 40 lines) is the **model delegate** - focused responsibility, high cohesion, no complexity hotspots.
