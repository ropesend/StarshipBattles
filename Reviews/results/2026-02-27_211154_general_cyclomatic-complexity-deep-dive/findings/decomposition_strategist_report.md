# Decomposition Strategist Report

**Date:** 2026-02-27
**Reviewer:** Decomposition Strategist Agent
**Scope:** Four high-CC functions with proposed decomposition strategies

---

## Summary

- **Total issues found:** 18
- **Critical:** 2, **Major:** 7, **Minor:** 6, **Info:** 3

---

## Function 1: `ProductionEngine._process_queue_tick_dynamic` (CC=27)

**File:** `game/strategy/engine/production_engine.py` (lines 177-350)

### Code Structure Mapping

The function has these logical sections:
1. **Early return** (line 213-214): Empty queue guard
2. **Main while loop** (lines 221-350): Processes items while capacity > 0
3. **Validation block** (lines 226-228): Non-dict item removal
4. **Type/filter checks** (lines 230-241): vehicle_type filtering and is_complex_only
5. **Fleet location constraint** (lines 244-249): Fleet complex at planet check
6. **Cost initialization** (lines 252-260): Lazy total_cost fallback
7. **Remaining cost calculation** (lines 262-276): Loop computing what remains
8. **Limiting resource / ticks needed** (lines 281-294): Rate-to-ticks math
9. **Cost-this-step calculation** (lines 300-316): Per-resource cost for tick fraction
10. **Affordability check** (lines 318-320): Empire resource gate
11. **Resource consumption** (lines 323-326): Mutate empire + item
12. **Capacity decrement** (lines 329): tick_capacity reduction
13. **UI display update** (lines 332-337): turns_remaining estimate
14. **Completion check** (lines 341-350): Epsilon-based done check

### Evaluation of Proposed Extractions

**Proposed: `_validate_queue_item(item, colony_or_fleet, galaxy, is_complex_only)`**

Maps to lines 226-249 (sections 3, 4, 5). This is a reasonable extraction.

- **Signature assessment:** Sufficient parameters. Would also need `queue` parameter if the method is to pop invalid items (line 227), or the caller handles popping based on a return code.
- **Return type:** Would need to be a tri-state: `"valid"`, `"skip_item"` (pop and continue), or `"stop_queue"` (return). An enum or sentinel would be cleaner than a boolean.
- **Purity:** Not pure if it pops the queue (line 227). Could be made pure if it returns validation status and the caller handles mutation.
- **Estimated CC:** ~5 (isinstance check, is_complex_only check, isinstance Fleet check, galaxy None check, planets_at_hex check)

**Proposed: `_calculate_tick_expenditure(item, tick_capacity, production_rate)`**

Maps to lines 262-316 (sections 7, 8, 9). This is the mathematical core and a strong extraction candidate.

- **Signature assessment:** Missing `total_cost` and `resources_consumed` -- these come from the `item` dict, so the item parameter covers it, but the caller must have already extracted `total_cost`. Actually, the proposed signature is sufficient since `item` contains `total_cost` and `resources_consumed`.
- **Return type:** Should return a tuple/dataclass: `(remaining_cost, ticks_to_spend, cost_this_step, max_ticks_needed)` -- or a `TickExpenditure` result object.
- **Purity:** Can be fully pure (no mutation). This is the highest-value extraction.
- **Estimated CC:** ~6 (remaining_cost loop with conditional, rate loop with zero-rate early return, min/clamp logic)

**Proposed: `_apply_production_progress(item, ticks_to_spend, production_rate)`**

Maps to lines 318-350 (sections 10, 11, 12, 13, 14). This extraction conflates two concerns: mutation and completion checking.

- **Signature assessment:** Also needs `empire` (for has_resources, consume_resources), `tick_capacity` (to decrement), `max_ticks_needed` (for turns_remaining estimate), and the completion params `total_cost`/`cost_this_step`. The proposed signature is significantly insufficient.
- **Return type:** Would need to communicate: affordability failure, resources consumed, new tick_capacity, and whether item is complete. Too many outputs suggest this is too broad.
- **Purity:** Not pure -- mutates empire resources and item dict.
- **Estimated CC:** ~5 (has_resources check, resource consumption loop, turns_remaining conditional, completion loop with epsilon break)

### Findings for Function 1

#### MAJOR: Proposed `_apply_production_progress` conflates affordability, mutation, and completion
**ID:** DS-001
**Location:** `game/strategy/engine/production_engine.py:318-350`
**Issue:** The proposed `_apply_production_progress` tries to bundle three distinct responsibilities: affordability checking (line 318-320), resource mutation (lines 323-326), and completion detection (lines 341-350). The proposed signature `(item, ticks_to_spend, production_rate)` lacks `empire`, `tick_capacity`, `max_ticks_needed`, `cost_this_step`, and `total_cost` -- nearly all the state needed.
**Impact:** If implemented as proposed, it would either require passing 7+ parameters or accessing them through a shared context object, defeating the simplification goal.
**Recommendation:** Split into three smaller focused methods:
- `_check_affordability(empire, cost_this_step) -> bool` (trivial wrapper, CC=1)
- `_apply_resource_consumption(empire, item, cost_this_step) -> None` (mutation only, CC=2)
- `_check_item_completion(item, total_cost, epsilon=0.001) -> bool` (pure, CC=2)
This maps more naturally to the actual code structure and keeps each method focused.
**Effort:** Simple

#### MINOR: Free/zero-cost item completion path not covered by any extraction
**ID:** DS-002
**Location:** `game/strategy/engine/production_engine.py:274-276`
**Issue:** The "no remaining cost, complete immediately" path (line 274-276) sits between validation and expenditure calculation. None of the three proposed extractions cleanly owns this check.
**Impact:** The orchestrator would still need a special-case branch for zero-cost items, adding CC to the remaining code.
**Recommendation:** Include this as the first check in `_calculate_tick_expenditure` returning a sentinel (e.g., `ticks_to_spend=0, remaining_cost={}`) that the caller interprets as "immediately complete."
**Effort:** Simple

#### MINOR: Lazy cost initialization fallback is a smell
**ID:** DS-003
**Location:** `game/strategy/engine/production_engine.py:252-260`
**Issue:** Lines 252-260 attempt to lazily initialize `total_cost` if missing, but the implementation calls `_calculate_design_cost(item)` which expects `design_data`, not a queue item. The code then immediately falls through with `pass`, meaning items without `total_cost` get `{}` from `item.get('total_cost', {})` and complete instantly. This is dead/broken code.
**Impact:** Low immediate impact (controller always sets total_cost), but this code path is confusing and would be extracted into any validation method. The proposed `_validate_queue_item` should explicitly handle this edge case.
**Recommendation:** Remove the broken fallback (lines 254-260). If total_cost is missing, log a warning and skip the item. This simplifies both validation and the overall CC.
**Effort:** Simple

#### INFO: Orchestrator CC after proposed extractions
**ID:** DS-004
**Location:** `game/strategy/engine/production_engine.py:177-350`
**Issue:** After applying the three proposed extractions, the orchestrator while-loop would still have CC ~8-10 (while condition, iteration guard, validation result branching, zero-cost check, affordability return, completion branching). With the revised four-method split, the orchestrator drops to CC ~6-7, which is acceptable.
**Impact:** The strategy achieves meaningful reduction but is not transformative with the original three extractions alone.
**Recommendation:** Target orchestrator CC <= 8 after refactoring. The four-method alternative achieves this.
**Effort:** N/A

---

## Function 2: `ShipStatsCalculator.calculate_stats` (CC=26)

**File:** `game/strategy/services/ship_stats_calculator.py` (lines 87-297)

### Code Structure Mapping

The function has these logical sections:
1. **Parameter defaulting** (lines 114-117): None -> {}
2. **Registry access** (lines 119-120): Pull vehicle_classes and modifier_registry
3. **Accumulator initialization** (lines 123-131): Eight separate accumulators
4. **Formula context setup** (lines 133-140): ship_class_mass from vehicle_classes
5. **Component iteration** (line 143): Delegates to _iterate_design_components
6. **Fallback to expected_stats** (lines 147-159): When no components found
7. **Per-component loop** (lines 161-284): The main complexity driver
   - a. Toggle-off shortcut (lines 172-177): Mass only for disabled components
   - b. Effectiveness calculation (lines 180-182)
   - c. Mass accumulation (lines 185-187): Always full mass with modifiers
   - d. HP accumulation (lines 190-192): HP * effectiveness with modifiers
   - e. ResourceStorage ability (lines 200-210): Loop with capacity_mult
   - f. CargoStorage ability (lines 213-222): Loop with capacity_mult
   - g. StrategicMovement ability (lines 225-228): Single value with modifiers
   - h. ResourceConsumption ability (lines 234-249): Loop with trigger branching
   - i. WarpJump ability (lines 252-284): Complex nested block with warp_effectiveness check, tonnage evaluation, and warp resource costs
8. **Return dict construction** (lines 286-297)

### Evaluation of Proposed Extractions

**Proposed: `_initialize_base_stats(design_data, vehicle_classes)`**

Maps to lines 123-140 (sections 3, 4). Viable but low-value.

- **Signature assessment:** Adequate. Would return a tuple of (accumulators_dict, formula_context).
- **Return type:** Would need to return ~10 values (8 accumulators + formula_context). This screams for a dataclass.
- **Purity:** Yes, purely computational.
- **Estimated CC:** ~3 (ship_class check, class_data isinstance check)
- **Value assessment:** This only removes CC ~3 from a CC=26 function. Marginal value.

**Proposed: `_accumulate_component_stats(components, modifiers, damage)`**

Maps to lines 161-284 (section 7). This is essentially the entire body of the loop. Extracting the whole loop body into a single method doesn't decompose -- it just moves the problem.

- **Signature assessment:** Would need: component_found list, all 8 accumulators (by reference or returned), formula_context, component_damage, component_toggles, modifier_registry. This is 12+ parameters.
- **Return type:** Would need to return all 8 modified accumulators.
- **Estimated CC:** ~20 (nearly all the CC is in the loop body). This does not decompose the complexity.
- **Value assessment:** Very low. This is rename-and-move, not decomposition.

**Proposed: Registry of Policy objects (MassCalculator, HpCalculator, ResourceStorageCalculator)**

This is the boldest proposal and potentially the most valuable, but also the most speculative.

- **Assessment:** The per-component loop has a clear pattern: for each ability type, read values, apply modifiers/effectiveness, accumulate into a specific dict. A policy/strategy pattern could formalize this. Each "policy" would implement `accumulate(comp_def, comp_entry, effectiveness, multipliers, formula_context, accumulator)`.
- **Complexity fit:** This would split the CC across ~6 small policy classes (Mass, HP, ResourceStorage, CargoStorage, StrategicMovement, ResourceConsumption+WarpJump).
- **Risk:** High. The WarpJump block (lines 252-284) is the most complex piece and has tight coupling between ResourceConsumption (trigger=warp_jump) and WarpJump ability. Splitting these into separate policies requires careful interface design.
- **Reuse potential:** Low -- these policies are specific to ship stat calculation.

### Findings for Function 2

#### CRITICAL: Proposed `_accumulate_component_stats` does not actually decompose
**ID:** DS-005
**Location:** `game/strategy/services/ship_stats_calculator.py:161-284`
**Issue:** The proposed extraction `_accumulate_component_stats` would contain nearly all the cyclomatic complexity (CC ~20 of 26). It moves the code into a new method but does not reduce the complexity of any single function. The proposed signature `(components, modifiers, damage)` is also incomplete -- it's missing formula_context, component_toggles, modifier_registry, and all 8 accumulators.
**Impact:** Implementing this as proposed would be a refactoring that achieves nothing -- the complexity is just relocated, not reduced.
**Recommendation:** Decompose the per-component loop body into per-ability accumulator methods instead:
- `_accumulate_mass(comp_def, comp_entry, multipliers, formula_context) -> float` (CC=2)
- `_accumulate_hp(comp_def, effectiveness, multipliers, formula_context) -> float` (CC=1)
- `_accumulate_resource_storage(abilities, effectiveness, capacity_mult, formula_context, storage_dict)` (CC=3)
- `_accumulate_cargo_storage(abilities, effectiveness, capacity_mult, formula_context, storage_dict)` (CC=3)
- `_accumulate_movement(abilities, effectiveness, multipliers, formula_context) -> float` (CC=2)
- `_accumulate_consumption(abilities, effectiveness, consumption_mult, formula_context, per_hex_dict, per_turn_dict)` (CC=3)
- `_accumulate_warp(abilities, comp_id, comp_def, component_damage, formula_context, warp_tonnage, warp_costs_dict) -> int` (CC=5)
This makes each method small and testable, and reduces the orchestrator loop to CC ~8.
**Effort:** Medium

#### MAJOR: WarpJump block is the highest-CC section and has no targeted extraction
**ID:** DS-006
**Location:** `game/strategy/services/ship_stats_calculator.py:252-284`
**Issue:** The WarpJump block (lines 252-284) is the single most complex section, with nested conditionals for warp_effectiveness, dict vs. non-dict warp_data handling, formula evaluation, max tonnage tracking, AND a nested loop for warp resource costs from ResourceConsumption abilities. None of the three proposed extractions specifically targets this block.
**Impact:** This block alone contributes CC ~7 and is the primary complexity driver. Any decomposition that does not address it will leave the function substantially complex.
**Recommendation:** Extract `_accumulate_warp_stats(abilities, comp_id, comp_def, component_damage, formula_context) -> Tuple[int, Dict[str, float]]` returning (warp_tonnage_contribution, warp_cost_contribution). This isolates the most complex block and makes it independently testable.
**Effort:** Medium

#### MAJOR: Policy pattern is overengineered for this use case
**ID:** DS-007
**Location:** `game/strategy/services/ship_stats_calculator.py`
**Issue:** The proposed Registry of Policy objects (MassCalculator, HpCalculator, etc.) introduces an abstraction layer (interfaces, registration, polymorphic dispatch) for code that is called from exactly one place. The ability-type branching in the loop is not dynamic -- it's a known, fixed set of ability types.
**Impact:** Adds conceptual overhead and indirection without proportional benefit. Makes the codebase harder to understand for a pattern that won't be reused. Violates YAGNI.
**Recommendation:** Use simple method extraction (as in DS-005 recommendation) instead of a policy pattern. The methods can always be promoted to a pattern later if reuse appears. The private method approach achieves the same CC reduction with zero architectural complexity.
**Effort:** N/A (avoid this approach)

#### MINOR: `_initialize_base_stats` extraction has poor value-to-effort ratio
**ID:** DS-008
**Location:** `game/strategy/services/ship_stats_calculator.py:123-140`
**Issue:** Extracting accumulator initialization and formula context setup would save only CC ~3 but requires returning 9+ values, necessitating a dataclass or named tuple. The code is simple, readable, and not a complexity driver.
**Impact:** Low -- this extraction adds indirection without meaningful CC reduction.
**Recommendation:** Keep initialization inline. The complexity budget is better spent extracting the per-ability accumulators from the loop body. If a stats-accumulator dataclass is desired for clean code purposes, that can be done as a separate quality pass unrelated to CC reduction.
**Effort:** Simple but low value

---

## Function 3: `SaveGameService.load_game` (CC=26)

**File:** `game/strategy/systems/save_game_service.py` (lines 112-221)

### Code Structure Mapping

The function has these logical sections:
1. **Path resolution** (lines 124-126): isabs check, join with SAVES_DIR
2. **Save validation** (lines 128-131): Delegates to _validate_save
3. **Metadata loading** (lines 133-148): load_json_required with 4 exception handlers
4. **Metadata field validation** (lines 151-154): Required keys check
5. **Version compatibility** (lines 157-159): Delegates to _is_compatible_version
6. **Turn number resolution** (lines 162-163): Fallback logic
7. **Turn file path construction** (lines 166-167)
8. **Turn file existence check** (lines 169-170)
9. **Turn file loading** (lines 172-185): load_json_required with 4 exception handlers
10. **Game state field validation** (lines 188-191): Required keys check
11. **GameSession reconstruction** (lines 194-205): from_dict with 3 exception handlers
12. **Save path restoration** (line 208)
13. **Outer exception handlers** (lines 213-221): 3 broad catch blocks

### Evaluation of Proposed Extractions

**Proposed: `_load_save_metadata(save_path)`**

Maps to lines 124-159 (sections 1-5). Good extraction candidate.

- **Signature assessment:** Only needs save_path. Could include path resolution or expect pre-resolved path.
- **Return type:** `Tuple[Optional[dict], Optional[str]]` -- metadata or error message.
- **Purity:** Pure (reads file but no game state mutation).
- **Estimated CC:** ~9 (is_valid check, 4 exception handlers for metadata, missing_keys check, version check). This is still somewhat high.
- **Value assessment:** Removes ~9 CC from load_game, leaving the orchestrator at ~17. Not sufficient alone.

**Proposed: `_load_turn_data(save_path, turn_number)`**

Maps to lines 162-191 (sections 6-10). Good extraction candidate.

- **Signature assessment:** Needs save_path and turn_number. Also needs metadata to resolve turn_number if None. Suggest: pass resolved turn_number (caller extracts from metadata).
- **Return type:** `Tuple[Optional[dict], Optional[str]]` -- game_state or error message.
- **Purity:** Pure (reads file, no mutation).
- **Estimated CC:** ~7 (file exists check, 4 exception handlers, missing_keys check).
- **Value assessment:** Good. Removes another ~7 CC.

**Proposed: `_reconstruct_game_session(game_state, save_path)`**

Maps to lines 194-208 (section 11-12). Reasonable extraction.

- **Signature assessment:** Adequate.
- **Return type:** `Tuple[Optional[GameSession], Optional[str]]` -- session or error.
- **Purity:** Not pure -- creates and mutates GameSession.
- **Estimated CC:** ~4 (3 exception handlers + success path).
- **Value assessment:** Good. Isolates domain-specific reconstruction.

### Findings for Function 3

#### MAJOR: CC is driven by repetitive exception handling, not algorithmic complexity
**ID:** DS-009
**Location:** `game/strategy/systems/save_game_service.py:112-221`
**Issue:** Of the CC=26, approximately 14 points come from exception handlers (4 for metadata, 4 for turn data, 3 for reconstruction, 3 for outer catch). The actual business logic is linear and simple (load metadata, check version, load turn, reconstruct). The proposed extractions address this by moving exception handlers into sub-methods, but they don't reduce the total number of exception handlers.
**Impact:** The decomposition will succeed at reducing per-method CC, but the fundamental issue is over-catching. Many of these handlers produce near-identical error messages.
**Recommendation:** In addition to the proposed extractions, consolidate exception handlers. For `_load_save_metadata` and `_load_turn_data`, catch `(JSONDecodeError, FileNotFoundError, PermissionError, OSError)` in a single handler with a message template:
```python
except (JSONDecodeError, FileNotFoundError, PermissionError, OSError) as e:
    return None, f"Save file corrupted: Cannot read {context}: {type(e).__name__}"
```
This would reduce the CC of each sub-method by ~3 and eliminate the outer catch-all handlers which duplicate inner handling.
**Effort:** Simple

#### MAJOR: Outer exception handlers (lines 213-221) are redundant
**ID:** DS-010
**Location:** `game/strategy/systems/save_game_service.py:213-221`
**Issue:** The outer try/except at lines 213-221 catches `PermissionError`, `OSError`, and a broad `(KeyError, TypeError, ValueError, AttributeError, ImportError, ValidationException, StateException)`. Every one of these is already caught by inner blocks. The outer handlers are dead code under normal operation.
**Impact:** Adds 3 CC for no practical purpose. After extraction into sub-methods that handle their own exceptions, these outer handlers become even more clearly redundant.
**Recommendation:** Remove the outer try/except entirely after refactoring into sub-methods. Each sub-method returns `(None, error_msg)` on failure, so the orchestrator never sees raw exceptions.
**Effort:** Simple

#### MINOR: Turn number resolution should be in `_load_turn_data`
**ID:** DS-011
**Location:** `game/strategy/systems/save_game_service.py:162-163`
**Issue:** The proposed `_load_turn_data(save_path, turn_number)` expects a resolved turn_number, but the resolution logic (line 162-163: fallback to metadata's latest_turn_number) sits between metadata loading and turn loading. This creates awkward orchestrator coupling.
**Impact:** Minor -- the orchestrator must pass metadata to resolve turn_number before calling _load_turn_data.
**Recommendation:** Either pass metadata to `_load_turn_data` and let it resolve internally, or create `_resolve_turn_number(metadata, turn_number) -> int` as a tiny helper (CC=2). The latter is cleaner.
**Effort:** Simple

#### INFO: Overall strategy is sound
**ID:** DS-012
**Location:** `game/strategy/systems/save_game_service.py:112-221`
**Issue:** The three proposed extractions correctly identify the natural phase boundaries: load metadata, load turn data, reconstruct session. After extraction with exception handler consolidation, the orchestrator CC would be ~5-6 and each sub-method CC would be ~4-6.
**Impact:** Positive. This is the most straightforward decomposition of the four functions.
**Recommendation:** Proceed as proposed, incorporating DS-009 and DS-010 improvements.
**Effort:** Simple overall

---

## Function 4: `FleetNavigationService.project_path` (CC=22)

**File:** `game/strategy/services/fleet_navigation_service.py` (lines 413-562)

### Code Structure Mapping

The function has these logical sections:
1. **Initialization** (lines 439-457): State creation, speed check, turn tracking, first_order_progress
2. **Main while loop** (line 459): Condition checks path/orders and turn limit
3. **Iteration guard** (lines 460-463): max_steps safety
4. **Order handling when no path** (lines 466-519):
   - a. Action order handling (lines 470-499): action_time calculation, first_order_progress adjustment, tick consumption sub-loop, state advancement
   - b. Movement order path computation (lines 501-519): get_destination, warp vs. normal path, state update
5. **Path break** (lines 522-523): No path after order handling
6. **Step execution** (lines 526-539): Pop next hex, detect warp, create PathSegment
7. **State update** (lines 542-554): Order completion on empty path, NavigationState construction
8. **Movement cost / turn advancement** (lines 557-560): Decrement moves, turn rollover

### Evaluation of Proposed Extractions

**Proposed: `_project_action_order(state, order, moves_left_in_turn, turns_left)`**

Maps to lines 470-499 (section 4a). Strong extraction candidate.

- **Signature assessment:** Also needs `fleet` (for _get_action_time_for_projection), `component_registry`, `is_first_order`, `first_order_progress`, `moves_per_turn`, `max_turns`, and `current_turn`. The proposed signature `(state, order, moves_left_in_turn, turns_left)` omits critical parameters.
- **Return type:** Must return updated `(state, moves_left_in_turn, current_turn, is_first_order)` -- four values.
- **Purity:** Not pure -- depends on fleet and component_registry for action_time lookup.
- **Estimated CC:** ~5 (non-movement check, first_order check, inner while loop, moves_left check, current_turn check)
- **Value assessment:** Good. This is a natural sub-algorithm.

**Proposed: `_resolve_path_for_order(state, order, galaxy)`**

Maps to lines 501-519 (section 4b). Good extraction.

- **Signature assessment:** Adequate.
- **Return type:** `Optional[tuple]` -- the computed path or None.
- **Purity:** Depends on galaxy for pathfinding, but no mutation to state.
- **Estimated CC:** ~4 (destination None check, WARP check, empty path check)
- **Value assessment:** Good. Clean boundary.

**Proposed: `_advance_tick(state)`**

Maps to lines 526-560 (sections 6, 7, 8). This conflates three concerns: segment creation, state update, and turn advancement.

- **Signature assessment:** Also needs `current_turn`, `moves_left_in_turn`, `moves_per_turn`, and the `segments` list. Far more than just `state`.
- **Return type:** Would need to return `(new_state, segment, moves_left_in_turn, current_turn)`.
- **Purity:** Not pure -- appends to segments list (or returns segment for caller to append).
- **Estimated CC:** ~4 (path empty check for order completion, warp detection, moves_left check)
- **Value assessment:** Moderate. The code is straightforward; the extraction mostly exists to reduce the main loop's visual size.

### Findings for Function 4

#### MAJOR: `_project_action_order` signature is significantly incomplete
**ID:** DS-013
**Location:** `game/strategy/services/fleet_navigation_service.py:470-499`
**Issue:** The proposed signature `(state, order, moves_left_in_turn, turns_left)` is missing `fleet`, `component_registry`, `is_first_order`, `first_order_progress`, `moves_per_turn`, `max_turns`, and `current_turn`. It needs 9 parameters total, not 4.
**Impact:** If implemented with the proposed signature, it would not compile. The actual parameter list is so large that it suggests the method might need a projection context object.
**Recommendation:** Introduce a `ProjectionContext` dataclass:
```python
@dataclass
class ProjectionContext:
    fleet: Fleet
    galaxy: Any
    component_registry: Any
    moves_per_turn: int
    max_turns: int
    current_turn: int = 0
    moves_left_in_turn: int = 0
    is_first_order: bool = True
    first_order_progress: int = 0
```
Then `_project_action_order(ctx, state, order) -> Tuple[NavigationState, ProjectionContext]` becomes clean. The context is mutable (tracking turn progress) while state remains immutable.
**Effort:** Medium

#### MAJOR: Inner while loop for action_time consumption is a separate concern
**ID:** DS-014
**Location:** `game/strategy/services/fleet_navigation_service.py:481-488`
**Issue:** Lines 481-488 contain a nested while loop that consumes action_time ticks across turn boundaries. This tick-consumption logic is a general-purpose "advance time by N ticks" algorithm that also appears conceptually in the movement cost section (lines 557-560). Neither the proposed extractions nor the original code share this logic.
**Impact:** The nested while loop is a CC driver (+3 from the inner while, conditional, and turn boundary check) and is independently testable.
**Recommendation:** Extract `_consume_ticks(moves_left_in_turn, current_turn, moves_per_turn, max_turns, ticks) -> Tuple[int, int]` returning (new_moves_left, new_current_turn). This pure function can be reused for both action-time consumption and could potentially replace the movement cost section too.
**Effort:** Simple

#### MINOR: `_advance_tick` is too broad -- step execution and turn tracking are distinct
**ID:** DS-015
**Location:** `game/strategy/services/fleet_navigation_service.py:526-560`
**Issue:** The proposed `_advance_tick(state)` merges segment creation (lines 526-539), state mutation (lines 542-554), and movement cost tracking (lines 557-560). These are three different responsibilities crammed into one extraction.
**Impact:** The method would have 3 distinct outputs (segment, new_state, updated turn tracking) which makes it awkward to use.
**Recommendation:** Keep segment creation and state update inline in the main loop (they're simple and readable). Extract only the turn-advancement logic into `_consume_ticks` (see DS-014). The main loop's body for step execution is only ~15 lines of straightforward code.
**Effort:** Simple

#### MINOR: `first_order_progress` tracking adds accidental complexity
**ID:** DS-016
**Location:** `game/strategy/services/fleet_navigation_service.py:451-453, 477-478`
**Issue:** The `first_order_progress` / `is_first_order` tracking exists solely to handle partial progress on the current action order. This special-casing adds two variables and a conditional that only fires once and then never again. It's a minor CC contributor but a readability impediment.
**Impact:** Low CC cost (+2) but hurts readability.
**Recommendation:** Handle this by pre-adjusting the first order's action_time before the main loop starts, rather than tracking it through the loop. Something like: if first order is action type, subtract execution_progress from its action_time upfront.
**Effort:** Simple

---

## Cross-Cutting Findings

#### CRITICAL: No proposed strategy addresses the real CC driver: nested loops with early returns
**ID:** DS-017
**Location:** All four functions
**Issue:** Three of the four functions (production_engine, ship_stats_calculator, fleet_navigation_service) share a pattern: a main loop with multiple conditional branches that contain `return` or `break` statements, plus nested inner loops. The proposed extractions generally try to extract the loop body into a single large method, which does not decompose the nesting. The most effective decomposition pattern for nested-loop-with-early-return code is to extract the inner body into a method that returns a discriminated result (success/skip/stop), and have the outer loop dispatch on that result.
**Impact:** If all four functions are refactored using the proposed strategies without this correction, two of them (production_engine and ship_stats_calculator) will still have methods with CC > 15.
**Recommendation:** For each main-loop function, apply the "extract loop body with result enum" pattern:
```python
class StepResult(Enum):
    CONTINUE = "continue"  # Process next item
    SKIP = "skip"          # Skip current item, try next
    STOP = "stop"          # Stop processing queue
```
This eliminates early returns from the loop and makes control flow explicit.
**Effort:** Medium

#### INFO: Implementation ordering recommendation
**ID:** DS-018
**Location:** All four files
**Issue:** The four decompositions have no code dependencies between them but vary significantly in risk and value.
**Impact:** Ordering affects how quickly value is delivered and how easily regressions can be caught.
**Recommendation:**

**Recommended order:**

1. **`SaveGameService.load_game` (FIRST)** -- Lowest risk, highest confidence. The three-phase split (metadata, turn data, reconstruction) is natural and the strategy is essentially correct with minor improvements. Exception handler consolidation yields the most CC reduction per effort. No behavioral changes needed. Estimated effort: 1-2 hours.

2. **`ProductionEngine._process_queue_tick_dynamic` (SECOND)** -- Medium risk. The validation and expenditure-calculation extractions are straightforward. The revised four-method split (replacing the original three) is more work but gives better results. The method has side effects (empire mutation) that require careful test coverage of resource consumption. Estimated effort: 2-3 hours.

3. **`FleetNavigationService.project_path` (THIRD)** -- Medium risk. Benefits from the `ProjectionContext` dataclass approach. The immutable NavigationState pattern is already in place, making extraction boundaries cleaner. The action_time handling is the trickiest part. Estimated effort: 2-3 hours.

4. **`ShipStatsCalculator.calculate_stats` (LAST)** -- Highest risk. The per-ability accumulation extractions are numerous (7 methods) and the WarpJump block's coupling between WarpJump and ResourceConsumption abilities makes it the most likely to introduce regressions. Also has the most test coverage to validate against. Estimated effort: 3-4 hours.

**Risk levels:**
- `load_game`: LOW (linear code, no algorithmic complexity)
- `_process_queue_tick_dynamic`: MEDIUM (resource mutation, float precision)
- `project_path`: MEDIUM (immutable state helps, but action_time is tricky)
- `calculate_stats`: HIGH (many ability types, formula evaluation, damage model)
**Effort:** N/A

---

## Top 5 Priority Issues

1. **DS-005 (CRITICAL):** `_accumulate_component_stats` does not decompose -- it relocates CC ~20 into a new method. Replace with per-ability accumulator methods.

2. **DS-017 (CRITICAL):** Nested loops with early returns are the real CC driver across 3 of 4 functions. Extract loop bodies with discriminated result types.

3. **DS-009 (MAJOR):** `load_game` CC is inflated by repetitive exception handling. Consolidate exception handlers to reduce per-method CC by ~3 each.

4. **DS-013 (MAJOR):** `_project_action_order` signature is missing 5+ critical parameters. Introduce a `ProjectionContext` dataclass.

5. **DS-001 (MAJOR):** `_apply_production_progress` conflates affordability, mutation, and completion. Split into three focused methods.
