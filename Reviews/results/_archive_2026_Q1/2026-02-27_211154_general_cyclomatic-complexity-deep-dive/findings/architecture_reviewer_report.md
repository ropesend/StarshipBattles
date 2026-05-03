# Architecture Review: Cyclomatic Complexity Deep-Dive

**Reviewer:** Architecture Reviewer (Claude Opus 4.6)
**Date:** 2026-02-27
**Scope:** 4 high-CC functions in the Strategy layer

---

## Summary

- **Total issues found:** 18
- **Critical:** 2, **Major:** 7, **Minor:** 6, **Info:** 3

---

## Function 1: `ProductionEngine._process_queue_tick_dynamic` (CC=27)

**File:** `game/strategy/engine/production_engine.py` (lines 177-351)

### Dependency Map

| Dependency | Type | Layer |
|---|---|---|
| `Fleet` (isinstance check) | Data class | Strategy |
| `empire.has_resources(dict)` | Method call | Strategy |
| `empire.consume_resources(str, float)` | Method call | Strategy |
| `galaxy.get_planets_at_global_hex(HexCoord)` | Method call | Strategy |
| `self._calculate_design_cost(item)` | Internal method | Strategy |
| `self._complete_item(...)` | Internal method (7 params) | Strategy |
| `DesignCostCalculator.calculate_total_cost()` | Static call | Strategy |
| `DesignLibrary(save_path, empire.id)` | Constructor | Strategy |
| `PlanetaryFacility(...)` | Data class | Strategy |
| `ShipInstance.create(...)` | Factory method | Strategy |
| `log_event(...)` | Utility | Strategy |

**External dependency count:** 11 direct dependencies. All within Strategy layer -- no layer violations.

### Coupling Assessment

The function accesses `item` dict keys extensively (`design_id`, `type`, `total_cost`, `resources_consumed`, `turns_remaining`, `resources_consumed`, `target_planet_id`). This item dict is an **implicit data contract** -- there is no dataclass or schema enforcing the shape.

The function mutates `item` in-place (setting `resources_consumed`, `turns_remaining`) and mutates `empire` via `consume_resources`. It also pops from `queue`. These side effects are appropriate for an engine method but make the function hard to test in isolation.

**Inappropriate intimacy:** The function directly accesses `item['resources_consumed']` to accumulate, then later re-reads `item['resources_consumed']` to check completion. The dict is both input and working storage.

### Interface Contract Analysis

**Inputs:** `queue` (List[Dict]), `empire`, `tick` (int), `galaxy`, `save_path` (Optional[str]), `production_rate` (Dict[str,float]), `colony_or_fleet`, `is_complex_only` (bool) -- **8 parameters**.

**Implicit contracts:**
- `item` must have `design_id` key (KeyError if missing, line 231)
- `item` should have `total_cost` dict, but fallback attempts `_calculate_design_cost(item)` which expects `design_data` format, not queue item format -- **latent bug** (line 255: `self._calculate_design_cost(item)` passes queue item where design_data is expected)
- `empire` must implement `has_resources()`, `consume_resources()`
- `galaxy` can be None (checked for Fleet complex production)

**Outputs:** None (mutates queue, item, and empire in-place)

### Proposed Decomposition Assessment

**`_validate_queue_item(item, colony_or_fleet, galaxy, is_complex_only)`** -- Good boundary. The validation logic (lines 226-249) is a natural responsibility: type checks, filter checks, fleet location checks. Would reduce CC by ~5. The parameter list (4 params) is reasonable. Independently testable.

**`_calculate_tick_expenditure(item, tick_capacity, production_rate)`** -- Good boundary. Lines 251-316 are pure math: remaining cost calculation, limiting resource determination, cost-per-step calculation. Could be a pure function returning `(ticks_to_spend, cost_this_step, max_ticks_needed)`. Excellent testability. Reduces coupling -- no `empire` or `galaxy` needed.

**`_apply_production_progress(item, ticks_to_spend, production_rate)`** -- Reasonable but the current logic interleaves affordability checks (`empire.has_resources`) with resource consumption (`empire.consume_resources`). The proposed extraction would need to either include `empire` as parameter (adding coupling) or split into calculate + apply phases. Splitting into calculate + apply is architecturally cleaner.

---

## Function 2: `ShipStatsCalculator.calculate_stats` (CC=26)

**File:** `game/strategy/services/ship_stats_calculator.py` (lines 87-297)

### Dependency Map

| Dependency | Type | Layer |
|---|---|---|
| `GameRegistries` | DI container | Core |
| `self._registries.vehicle_classes` | Registry access | Core |
| `self._registries.modifiers` | Registry access | Core |
| `self._registries.components` | Registry access (via _iterate_design_components) | Core |
| `calculate_stat_multipliers()` | Function | Simulation |
| `safe_evaluate_math_formula()` | Function | Simulation |
| `iter_layers_and_components()` | Utility | Core |
| `get_component_id()` | Utility | Core |
| `get_component_abilities()` | Utility | Strategy |
| `get_component_type()` | Utility | Strategy |
| `get_component_threshold()` | Utility | Strategy |

**External dependency count:** 11. Cross-layer dependencies: Core (5), Simulation (2), Strategy (3).

### Coupling Assessment

**Layer compliance:** Strategy depends on Core and Simulation -- this is valid per the architecture. No violations.

**Dependency Injection:** Excellent. `GameRegistries` is injected via constructor with strict validation. No singleton access.

**Data coupling:** The function processes `design_data` (a dict) and reads 9 different ability types (`ResourceStorage`, `CargoStorage`, `StrategicMovement`, `ResourceConsumption`, `WarpJump`, `Armor`). Each ability type has its own dict shape. This creates a high degree of **data coupling** with the component JSON schema.

**Inappropriate intimacy:** The function directly interprets the internal structure of ability data dicts (e.g., `ability_data.get('resource', '')`, `ability_data.get('trigger', 'constant')`). This is appropriate for a stats calculator -- it is _the_ component that should know these structures.

### Interface Contract Analysis

**Inputs:** `design_data` (Dict), `component_damage` (Optional Dict), `component_toggles` (Optional Dict) -- **3 parameters**. Clean.

**Implicit contracts:**
- `design_data` must have `layers` dict with components in list or dict format
- Component entries must have `id` key for registry lookup
- Ability dicts follow specific schemas per ability type
- `vehicle_classes` registry keyed by `ship_class` string

**Output:** Dict with 9 keys (max_hp, mass, resource_storage, cargo_storage, resource_consumption_per_hex, resource_consumption_per_turn, warp_resource_costs, strategic_movement, warp_max_tonnage). Well-documented in docstring.

### Proposed Decomposition Assessment

**`_initialize_base_stats(design_data, vehicle_classes)`** -- Reasonable extraction for lines 119-159 (formula context setup + empty component fallback). However, the "fallback to expected_stats" at lines 147-159 is inherently coupled to the iteration result, making the boundary slightly awkward: you'd need to run iteration first, then decide to fall back. A better boundary might be `_build_formula_context(design_data, vehicle_classes)` which is purely initialization.

**`_accumulate_component_stats(components, modifiers, damage)`** -- This is essentially the entire for-loop (lines 161-284). Extracting it would move 120+ lines into a helper but wouldn't materially reduce CC because the branching is inherent to the different ability types. The helper would still have CC ~20.

**Registry of Policy objects** -- This is the most architecturally sound proposal. Each ability type (ResourceStorage, CargoStorage, StrategicMovement, ResourceConsumption, WarpJump) maps to a `StatAccumulator` policy that knows how to aggregate its contribution. Benefits:
- Each policy is independently testable
- Adding new ability types doesn't modify `calculate_stats`
- Open/Closed principle compliance
- Natural responsibility boundaries

However, this is a **Complex** effort refactor and introduces abstraction overhead for what is currently 6 distinct cases. It would be justified if new ability types are expected to be added frequently.

---

## Function 3: `SaveGameService.load_game` (CC=26)

**File:** `game/strategy/systems/save_game_service.py` (lines 112-221)

### Dependency Map

| Dependency | Type | Layer |
|---|---|---|
| `Paths.SAVES_DIR` | Constant | Core |
| `load_json_required()` | Utility | Core |
| `GameSession.from_dict()` | Factory (lazy import) | Strategy |
| `SaveGameService._validate_save()` | Internal static | Strategy |
| `SaveGameService._is_compatible_version()` | Internal static | Strategy |
| `os.path.*` (6 calls) | stdlib | N/A |

**External dependency count:** 6. Minimal coupling -- this is well-isolated.

### Coupling Assessment

**Layer compliance:** Perfect. Only depends on Core utilities and its own internal methods. The `GameSession` import is lazy (line 195) to avoid circular dependencies -- this is a recognized pattern.

**Inappropriate intimacy:** None. The function interacts with `GameSession` only through its public `from_dict()` factory and `save_path` attribute. It does not reach into GameSession internals.

**Key observation:** The function is a **static method** operating on file paths. It has no instance state and no dependency injection. This is appropriate for a service that manages file I/O.

### Interface Contract Analysis

**Inputs:** `save_path` (str), `turn_number` (Optional[int]) -- **2 parameters**. Clean.

**Implicit contracts:**
- `save_path` may be relative (resolved against `Paths.SAVES_DIR`)
- Save folder must contain `save_metadata.json` and `turns/` subfolder
- Metadata must have `version`, `timestamp`, `player_name`
- Turn JSON must have `turn_number`, `config`, `galaxy`, `empires`

**Output:** `Tuple[Optional[GameSession], str]` -- clear success/failure contract.

### Proposed Decomposition Assessment

**`_load_save_metadata(save_path)`** -- Excellent boundary (lines 134-158). Self-contained: validate folder, load JSON, check required keys, verify version. Returns `(metadata, error_msg)` or raises. Zero new coupling. Independently testable with test files on disk. **Simple effort.**

**`_load_turn_data(save_path, turn_number)`** -- Excellent boundary (lines 162-191). Self-contained: resolve turn file path, load JSON, validate required keys. Returns `(game_state, error_msg)` or raises. Zero new coupling. **Simple effort.**

**`_reconstruct_game_session(game_state, save_path)`** -- Good boundary (lines 194-208). Wraps `GameSession.from_dict()` with error handling. The lazy import of `GameSession` stays localized in this method, which is cleaner than having it in the main function. **Simple effort.**

**Overall assessment:** This is the best candidate for decomposition among the four functions. The high CC comes almost entirely from defensive error handling (9 distinct `except` clauses). The proposed three-method split follows the natural phases of load_game: (1) validate & load metadata, (2) load turn data, (3) reconstruct session. Each phase has clear inputs/outputs and no shared mutable state.

---

## Function 4: `FleetNavigationService.project_path` (CC=22)

**File:** `game/strategy/services/fleet_navigation_service.py` (lines 413-562)

### Dependency Map

| Dependency | Type | Layer |
|---|---|---|
| `NavigationState.from_fleet()` | Factory | Strategy (same file) |
| `Fleet` | Data class | Strategy |
| `FleetOrder` | Data class | Strategy |
| `OrderType`, `MOVEMENT_ORDER_TYPES` | Enum/frozenset | Strategy |
| `HexCoord`, `hex_distance()` | Utility | Core |
| `self.get_destination()` | Internal method | Strategy |
| `self.compute_path()` | Internal method | Strategy |
| `self.compute_path_for_warp()` | Internal method | Strategy |
| `self._get_action_time_for_projection()` | Internal method | Strategy |
| `ActionTimeResolver.resolve_action_time()` | Static call (lazy) | Strategy |
| `find_hybrid_path()` | Pathfinding | Strategy |
| `PathSegment` | Data class | Strategy (same file) |

**External dependency count:** 12. All within Strategy layer or Core utilities.

### Coupling Assessment

**Layer compliance:** Perfect. No layer violations.

**Internal cohesion:** High. The method delegates to `get_destination()`, `compute_path()`, `compute_path_for_warp()`, and `_get_action_time_for_projection()` -- all methods on the same class. This is good: the class is the "single source of truth" for navigation.

**Inappropriate intimacy:** The method accesses `fleet.orders[0].execution_progress` directly (line 452). This reaches into the Fleet's order list and the FleetOrder's internal state. A cleaner approach would be `fleet.get_current_order_progress()` or passing the progress as part of `NavigationState`.

**Private attribute access in `_resolve_warp_exit`:** Line 272 accesses `galaxy._global_hex_warp_points` -- a private attribute prefixed with underscore. This is **inappropriate intimacy** with Galaxy's internals. Should use a public method like `galaxy.get_warp_point_at_hex()`.

### Interface Contract Analysis

**Inputs:** `fleet` (Fleet), `galaxy`, `max_turns` (int), `component_registry` (optional) -- **4 parameters**. Acceptable.

**Implicit contracts:**
- `fleet.orders` is a list of `FleetOrder` objects
- `fleet.speed` translates to integer moves per turn
- `fleet.orders[0].execution_progress` is accessible
- `galaxy` supports `get_planets_at_global_hex()`, `_global_hex_warp_points`, `get_system_by_name()`
- `component_registry` is optional but needed for accurate action_time projection

**Output:** `list[PathSegment]` -- clean, well-typed output.

### Proposed Decomposition Assessment

**`_project_action_order(state, order, moves_left_in_turn, turns_left)`** -- Excellent boundary. Lines 470-498 handle the action order branch: look up action_time, consume ticks across turns, advance state. This is a distinct responsibility from movement projection. Returns `(new_state, moves_left_in_turn, current_turn)`. 4 parameters + 3 return values is reasonable. **Independently testable** with mock orders.

**`_resolve_path_for_order(state, order, galaxy)`** -- Good boundary. Lines 501-519 resolve a movement order into a computed path and update state. Returns `Optional[NavigationState]`. Clean. However, it overlaps with existing `compute_path()` and `compute_path_for_warp()`, so this might be more of a coordinator than a distinct computation.

**`_advance_tick(state)`** -- Unclear boundary. The "tick" in this context is consuming one step of path + creating a PathSegment + updating state + decrementing moves. This involves both state transition and segment creation, which are tightly coupled. Extracting this might create a method with too many out-parameters. A better alternative: extract the **entire movement simulation loop** body as `_project_one_step(state, moves_left, current_turn, segments)` returning updated values.

---

## Findings

### Critical

#### CRITICAL: Latent Bug in Production Cost Fallback
**ID:** AR-01
**Location:** `game/strategy/engine/production_engine.py:255`
**Issue:** When `total_cost` is missing from a queue item, `self._calculate_design_cost(item)` is called, passing the queue item dict where the method expects a `design_data` dict (with `layers` containing components). A queue item has `design_id`, `type`, `turns_remaining` -- it does not have `layers`. This means `DesignCostCalculator.calculate_total_cost()` would iterate an empty `layers` dict and return `{}`, making the item appear free. The `pass` on line 260 suggests the author recognized this but left it as a known gap.
**Impact:** A queue item without pre-calculated `total_cost` would complete instantly at zero cost, duplicating ships/facilities for free. This is a data integrity vulnerability in the production pipeline.
**Recommendation:** Load the design data from `DesignLibrary` using `design_id` and `save_path`, then calculate cost from the actual design data. Add explicit error handling if design cannot be loaded.
**Effort:** Medium

#### CRITICAL: Private Attribute Access on Galaxy Object
**ID:** AR-02
**Location:** `game/strategy/services/fleet_navigation_service.py:272`
**Issue:** `_resolve_warp_exit` accesses `galaxy._global_hex_warp_points` -- a private attribute (underscore-prefixed). This creates tight coupling between FleetNavigationService and Galaxy's internal implementation. Any refactoring of Galaxy's warp point storage would break this service.
**Impact:** Fragile coupling that violates encapsulation. The Galaxy class could not safely refactor its warp point index without auditing FleetNavigationService. This also appears in 2 other files according to grep results.
**Recommendation:** Add a public method `galaxy.get_system_at_warp_point(hex_coord)` to Galaxy and use it here. The 15 usages across the codebase should all migrate.
**Effort:** Medium

---

### Major

#### MAJOR: Implicit Dict Contract for Queue Items (No Type Safety)
**ID:** AR-03
**Location:** `game/strategy/engine/production_engine.py:177-351`
**Issue:** Queue items are untyped `Dict[str, Any]` with 8+ expected keys (`design_id`, `type`, `total_cost`, `cost_per_tick`, `resources_consumed`, `ticks_in_current_turn`, `turns_remaining`, `target_planet_id`). There is no dataclass, TypedDict, or schema enforcing this shape. Keys are accessed via `.get()` with various defaults.
**Impact:** Any caller constructing queue items can silently omit required fields, leading to subtle bugs (like AR-01). Refactoring is risky because the expected shape is spread across multiple files.
**Recommendation:** Create a `QueueItem` dataclass or `TypedDict` that makes the contract explicit. This is orthogonal to the CC decomposition but would dramatically improve maintainability of any extracted methods.
**Effort:** Medium

#### MAJOR: 8-Parameter Method Signature
**ID:** AR-04
**Location:** `game/strategy/engine/production_engine.py:177`
**Issue:** `_process_queue_tick_dynamic` takes 8 parameters (self + 7). This is a code smell indicating the method is doing too much. The `_complete_item` helper also takes 7 parameters.
**Impact:** Difficult to call correctly, easy to mix up positional arguments, and hard to test (requires constructing 7+ mocks/fixtures).
**Recommendation:** The proposed decomposition naturally addresses this. `_validate_queue_item` needs 4 params, `_calculate_tick_expenditure` needs 3 params. Additionally, consider grouping `empire`, `galaxy`, `save_path` into a `ProductionContext` object.
**Effort:** Simple (as part of decomposition)

#### MAJOR: Fake Fleet Object in compute_path
**ID:** AR-05
**Location:** `game/strategy/services/fleet_navigation_service.py:185-188`
**Issue:** `compute_path()` creates a fake fleet-like object using `type('Fleet', (), {...})()` to satisfy `find_hybrid_path`'s `fleet` parameter. This is a hack that bypasses type safety and creates a hidden dependency on `find_hybrid_path`'s expectations.
**Impact:** If `find_hybrid_path` ever accesses other Fleet attributes (location, path, etc.), this fake object will silently return `None` via `AttributeError` being swallowed or crash. The fake object also has a hardcoded `id=-1` which could cause issues in logging or debugging.
**Recommendation:** Refactor `find_hybrid_path` to accept a `can_warp: bool` parameter directly instead of requiring a Fleet-like object. The NavigationState already has `can_warp`.
**Effort:** Medium

#### MAJOR: Interleaved Validation and Mutation in Production Loop
**ID:** AR-06
**Location:** `game/strategy/engine/production_engine.py:221-351`
**Issue:** The while-loop interleaves: (1) item validation, (2) cost calculation, (3) affordability check, (4) resource consumption, (5) progress tracking, (6) completion check, (7) spawning. This makes the control flow hard to follow and means a failure at step 4 leaves the item in an inconsistent state (remaining_cost was calculated but not consumed).
**Impact:** Makes the proposed decomposition harder because the phases share state through the `item` dict. Testing any single phase requires setting up the full production context.
**Recommendation:** Restructure into explicit phases: validate -> calculate -> check affordability -> commit (consume + update). The calculate phase should be a pure function returning a "plan" that the commit phase executes.
**Effort:** Medium

#### MAJOR: Warp Jump Logic Embedded in Stats Calculator
**ID:** AR-07
**Location:** `game/strategy/services/ship_stats_calculator.py:252-284`
**Issue:** The WarpJump handling in `calculate_stats` is significantly more complex than other ability types. It has its own effectiveness calculation (`_get_warp_effectiveness`), nested iteration over `ResourceConsumption` abilities filtered by `trigger='warp_jump'`, and formula evaluation for `max_tonnage`. This is a sub-algorithm embedded within the main loop.
**Impact:** The WarpJump block adds ~6 to the CC score. It conflates two concerns: warp capability assessment and warp resource cost aggregation.
**Recommendation:** This is the strongest case for the Policy/Strategy pattern proposed in the decomposition. A `WarpJumpAccumulator` policy would encapsulate this logic cleanly and could be tested independently.
**Effort:** Medium

#### MAJOR: Excessive Exception Handling Breadth in load_game
**ID:** AR-08
**Location:** `game/strategy/systems/save_game_service.py:123-221`
**Issue:** The function has **14 except clauses** catching 12 distinct exception types. The outermost try/except (lines 123, 213-221) catches 7 exception types as a "catch-all" that overlaps with the inner handlers. The `ImportError` catch at line 203 and the outer line 219 means an import failure during GameSession reconstruction would be caught in two places.
**Impact:** Overlapping exception handlers create ambiguity about which handler fires. The outer catch-all at line 219 could mask bugs by catching `KeyError`, `TypeError`, `ValueError`, `AttributeError`, and `ImportError` that are not related to the specific file operations inside.
**Recommendation:** The proposed three-method decomposition elegantly solves this: each helper handles its own exceptions and returns a clear success/failure result. The main `load_game` method becomes a simple orchestrator with minimal error handling.
**Effort:** Simple (as part of decomposition)

---

### Minor

#### MINOR: NavigationState Missing execution_progress
**ID:** AR-09
**Location:** `game/strategy/services/fleet_navigation_service.py:39-70, 452`
**Issue:** `NavigationState` is a frozen dataclass capturing fleet state for pure calculations, but it omits `execution_progress` from the first order. Line 452 reaches back into `fleet.orders[0].execution_progress` to get this value separately.
**Impact:** Breaks the abstraction that NavigationState is a complete snapshot. Any function receiving NavigationState without the original Fleet cannot account for partial action progress.
**Recommendation:** Add `first_order_progress: int = 0` to NavigationState and populate it in `from_fleet()`.
**Effort:** Simple

#### MINOR: Redundant Completion Check in Production Loop
**ID:** AR-10
**Location:** `game/strategy/engine/production_engine.py:341-348`
**Issue:** After consuming resources and decrementing capacity (lines 323-329), the code re-iterates `total_cost` to check completion (lines 341-348). This is redundant because `ticks_to_spend == max_ticks_needed` already implies completion (within floating-point precision).
**Impact:** Unnecessary iteration over cost dict. More importantly, the epsilon check (`consumed < total - 0.001`) is a separate implicit contract from the tick calculation's precision, which could cause inconsistencies.
**Recommendation:** Derive completion from `ticks_to_spend >= max_ticks_needed - epsilon` rather than re-checking all resources. This also eliminates the redundant epsilon constant.
**Effort:** Simple

#### MINOR: Stats Calculator Fallback to expected_stats
**ID:** AR-11
**Location:** `game/strategy/services/ship_stats_calculator.py:147-159`
**Issue:** When no components are found in layers, the function falls back to reading `expected_stats` from `design_data`. This creates a hidden alternate code path where stats bypass dynamic calculation entirely.
**Impact:** Tests or designs that happen to have `expected_stats` but broken component references will silently use cached values rather than failing visibly. This masks component registry configuration errors.
**Recommendation:** Log a warning when falling back to `expected_stats` and consider making this an explicit mode rather than a silent fallback. In production, a design without resolvable components should be treated as an error.
**Effort:** Simple

#### MINOR: Untyped `galaxy` Parameter Across All Functions
**ID:** AR-12
**Location:** All 4 functions
**Issue:** The `galaxy` parameter in `_process_queue_tick_dynamic`, `project_path`, `compute_path`, `_resolve_warp_exit`, and `compute_next_step` is untyped (no type hint). It is used for `get_planets_at_global_hex()`, `_global_hex_warp_points`, `get_system_by_name()`, and passed to `find_hybrid_path()`.
**Impact:** No IDE support for method discovery, no static analysis for incorrect usage, and the Galaxy interface contract is completely implicit.
**Recommendation:** Add `Galaxy` type hint (using `TYPE_CHECKING` import to avoid circular imports). This project already uses this pattern in `pathfinding.py`.
**Effort:** Simple

#### MINOR: Hardcoded Constants in Production Engine
**ID:** AR-13
**Location:** `game/strategy/engine/production_engine.py:217,221,344`
**Issue:** Magic numbers: `0.0001` (tick capacity epsilon, line 221), `10` (max iterations, line 221), `0.001` (completion epsilon, line 344), `100.0` (ticks per turn, lines 291, 309). These are repeated without named constants.
**Impact:** If the ticks-per-turn value changes, all three references must be updated. The two different epsilon values (0.0001 vs 0.001) suggest inconsistent precision requirements.
**Recommendation:** Define `TICKS_PER_TURN = 100`, `TICK_EPSILON = 0.0001`, `COMPLETION_EPSILON = 0.001`, `MAX_QUEUE_ITERATIONS = 10` as class or module constants. Unify the epsilon values if possible.
**Effort:** Simple

#### MINOR: Lazy Import Pattern Inconsistency
**ID:** AR-14
**Location:** `game/strategy/engine/production_engine.py:104`, `game/strategy/systems/save_game_service.py:195`, `game/strategy/services/fleet_navigation_service.py:156,583`
**Issue:** Some imports are lazy (inside functions) and others are at module level. In `production_engine.py`, `build_queue_source` functions are imported both at module level (line 28) and inside `process_construction_tick` (line 104). In `save_game_service.py`, `GameSession` is lazily imported to avoid circular dependency. In `fleet_navigation_service.py`, `calculate_intercept_point` and `ActionTimeResolver` are lazily imported.
**Impact:** Inconsistent import patterns make it harder to understand the dependency graph. The duplicate import in production_engine.py (module-level line 28 vs function-level line 104) is particularly confusing.
**Recommendation:** Standardize: use module-level imports where possible, lazy imports only for circular dependency breaking, and document why each lazy import is necessary. Remove the duplicate in production_engine.py.
**Effort:** Simple

---

### Info

#### INFO: SaveGameService is Well-Architected for Decomposition
**ID:** AR-15
**Location:** `game/strategy/systems/save_game_service.py:112-221`
**Issue:** The `load_game` function's high CC stems entirely from defensive error handling, not from inherent algorithmic complexity. The core logic is a simple 3-phase pipeline: load metadata -> load turn data -> reconstruct session.
**Impact:** Positive -- this means the proposed decomposition will dramatically reduce CC while being low-risk. Each extracted method is a natural, well-bounded responsibility.
**Recommendation:** Prioritize this decomposition as the easiest win. Consider also converting from `Tuple[Optional[object], str]` to a `Result` pattern or raising exceptions, which would further simplify calling code.
**Effort:** Simple

#### INFO: ShipStatsCalculator DI Pattern is Exemplary
**ID:** AR-16
**Location:** `game/strategy/services/ship_stats_calculator.py:66-85`
**Issue:** The constructor requires `GameRegistries` with explicit validation and raises `ValidationException` if None. This is the gold standard for DI in this codebase.
**Impact:** Positive -- makes the class testable with `TestRegistryProvider` and eliminates hidden singleton access.
**Recommendation:** Use this pattern as the template when refactoring the other three functions. Specifically, `ProductionEngine` could benefit from constructor-injected dependencies (currently stateless with `__init__` as `pass`).
**Effort:** N/A

#### INFO: FleetNavigationService Pure Function Architecture is Sound
**ID:** AR-17
**Location:** `game/strategy/services/fleet_navigation_service.py:1-24`
**Issue:** The documented architecture (pure core functions + mutation bridge) is well-designed. `NavigationState` being frozen ensures `compute_next_step` is side-effect-free. The mutation bridge (`calculate_fleet_next_hex`) is clearly separated.
**Impact:** Positive -- `project_path` benefits from this architecture because it can simulate forward without mutating any Fleet state. The proposed decomposition should preserve this purity.
**Recommendation:** Ensure extracted methods from `project_path` maintain the pure function property (no Fleet mutation, only NavigationState transitions).
**Effort:** N/A

---

### Additional Finding (Cross-Cutting)

#### MAJOR: ProductionEngine Has No Dependency Injection
**ID:** AR-18
**Location:** `game/strategy/engine/production_engine.py:56-58`
**Issue:** `ProductionEngine.__init__` is empty (`pass`). The class has no injected dependencies. Instead, it creates `DesignLibrary` instances on the fly (lines 400, 459, 518) and calls `DesignCostCalculator` statically. This makes it impossible to test without real file system access and makes the dependency graph invisible at construction time.
**Impact:** Testing `_process_queue_tick_dynamic` requires a real save path with design files on disk, or extensive mocking. Contrast with `ShipStatsCalculator` which cleanly injects its registries.
**Recommendation:** Inject `DesignLibrary` factory or a `DesignResolver` interface. At minimum, inject `save_path` at construction time rather than passing it through every method. This would also eliminate the repeated `DesignLibrary(save_path, empire.id)` construction pattern (4 occurrences).
**Effort:** Medium

---

## Top 5 Priority Issues

| Rank | ID | Severity | Title | Rationale |
|------|------|----------|-------|-----------|
| 1 | AR-01 | Critical | Latent Bug in Production Cost Fallback | Active data integrity risk -- a queue item without `total_cost` completes for free |
| 2 | AR-02 | Critical | Private Attribute Access on Galaxy | Encapsulation violation with 15 usages across codebase; any Galaxy refactor breaks multiple files |
| 3 | AR-18 | Major | ProductionEngine Has No DI | Blocks testability of the most complex function; should be addressed before or during decomposition |
| 4 | AR-06 | Major | Interleaved Validation and Mutation | Core architectural issue making decomposition harder; restructuring into phases enables cleaner extraction |
| 5 | AR-08 | Major | Excessive Exception Handling in load_game | Easiest win: decomposition directly solves this with minimal risk; do this first to build confidence |

---

## Decomposition Strategy Ranking

Based on architectural merit and effort/impact:

1. **SaveGameService.load_game** -- Best candidate. Natural phase boundaries, minimal coupling, Simple effort. Do first.
2. **FleetNavigationService.project_path** -- Good candidate. Action order extraction is clean. Medium effort. The `_advance_tick` proposal needs refinement.
3. **ProductionEngine._process_queue_tick_dynamic** -- Needs prerequisite work (AR-01 fix, AR-03 TypedDict, AR-18 DI). The decomposition itself is sound but depends on fixing the underlying structural issues first.
4. **ShipStatsCalculator.calculate_stats** -- The Policy object registry is the right long-term architecture but is Complex effort. The simpler extractions (`_initialize_base_stats`, `_accumulate_component_stats`) don't meaningfully reduce CC. Consider deferring unless new ability types are planned.
