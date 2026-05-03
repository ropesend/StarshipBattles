# Cyclomatic Complexity Deep-Dive Analysis

## Summary
- Total issues found: 19
- Critical: 3, Major: 7, Minor: 6, Info: 3

---

## Function 1: `_process_queue_tick_dynamic` (CC=27)
**File:** `game/strategy/engine/production_engine.py`, lines 177-350

### Complexity Driver Map

| Line(s) | Construct | CC Contribution | Description |
|---------|-----------|----------------|-------------|
| 213 | `if not queue` | +1 | Early return guard |
| 221 | `while tick_capacity > 0.0001 and queue and iterations < 10` | +3 | Main loop + 2 boolean `and` |
| 226 | `if not isinstance(item, dict)` | +1 | Validation guard |
| 234 | `if is_complex_only and vehicle_type != 'complex'` | +2 | Filter check + `and` |
| 244 | `if isinstance(colony_or_fleet, Fleet) and vehicle_type == 'complex'` | +2 | Fleet complex check + `and` |
| 245 | `if not galaxy` | +1 | Nested null guard |
| 248 | `if not planets_at_hex` | +1 | Nested empty-list guard |
| 253 | `if 'total_cost' not in item` | +1 | Cost initialization fallback |
| 270 | `if remaining > 0` | +1 | Inside `for` loop over remaining_cost |
| 267 | `for res, amount in total_cost.items()` | +1 | Loop: calculate remaining |
| 274 | `if not remaining_cost` | +1 | Free/completed item check |
| 283 | `for res, amount in remaining_cost.items()` | +1 | Loop: limiting resource |
| 285 | `if p_rate_per_turn <= 0` | +1 | Zero-rate guard |
| 293 | `if ticks_needed > max_ticks_needed` | +1 | Track max |
| 301 | `for res, amount in total_cost.items()` | +1 | Loop: cost calculation |
| 319 | `if not empire.has_resources(cost_this_step)` | +1 | Affordability check |
| 323 | `for res, amount in cost_this_step.items()` | +1 | Loop: consume resources |
| 324 | `if amount > 0` | +1 | Skip zero consumption |
| 333 | `if max_ticks_needed > 0` | +1 | UI turns_remaining update |
| 342 | `for res, total in total_cost.items()` | +1 | Loop: completion check |
| 344 | `if consumed < total - 0.001` | +1 | Epsilon comparison |
| 348 | `if is_complete` | +1 | Completion dispatch |

**Total mapped: ~26 CC points** (base 1 + 26 branches = CC 27)

### Complexity Breakdown by Section

| Section | Lines | CC Contribution | % of Total |
|---------|-------|----------------|------------|
| Guards & validation | 213-249 | 8 | 30% |
| Cost initialization | 251-276 | 4 | 15% |
| Limiting resource calc | 278-295 | 4 | 15% |
| Resource consumption calc | 297-317 | 2 | 7% |
| Affordability & spend | 318-330 | 3 | 11% |
| Completion check | 331-350 | 4 | 15% |
| Main loop condition | 221 | 3 | 11% |

### Assessment of Proposed Decomposition

**Proposed extractions:**
1. `_validate_queue_item(item, colony_or_fleet, galaxy, is_complex_only)` -- targets guards section
2. `_calculate_tick_expenditure(item, tick_capacity, production_rate)` -- targets limiting resource calc
3. `_apply_production_progress(item, ticks_to_spend, production_rate)` -- targets consumption calc

**Analysis:**

The proposed decomposition targets 3 sections contributing roughly 8 + 4 + 2 = 14 CC points (52%). This is a good start, but it misses two significant CC clusters:

- **Cost initialization** (lines 251-276): The remaining-cost calculation loop with its inner conditional contributes 4 CC points and could be extracted as `_calculate_remaining_cost(item)`.
- **Completion check** (lines 331-350): The loop-based completion verification contributes 4 CC points. This could be `_check_and_finalize_completion(item, total_cost)`.

**Estimated residual CC after proposed extraction:** ~13-15 (the `while` loop itself, affordability check, completion check, cost init, and remaining dispatching logic). This is still above the typical CC=10 threshold.

**With the two additional extractions above:** Residual CC would drop to ~7-9, which is acceptable.

### Additional Complexity Issues

- **Nesting depth:** Maximum 3 levels (while > if isinstance Fleet > if not planets_at_hex). Manageable but the while-loop body is 130 lines, which is very hard to read.
- **Variable mutation:** `tick_capacity`, `item['resources_consumed']`, `item['turns_remaining']`, `remaining_cost`, `cost_this_step` are all mutated within the loop. The item dict is mutated in-place, making it hard to reason about state between iterations.
- **Cognitive complexity:** The function mixes validation, calculation, side effects (empire.consume_resources), and completion spawning in a single loop body. The mental model requires tracking 6+ mutable variables simultaneously.
- **Dead code smell:** Lines 255-260 have a "safety fallback" that calls `_calculate_design_cost(item)` which expects `design_data` not a queue item, followed by a bare `pass`. This is likely a bug or dead code path.

---

## Function 2: `calculate_stats` (CC=26)
**File:** `game/strategy/services/ship_stats_calculator.py`, lines 87-297

### Complexity Driver Map

| Line(s) | Construct | CC Contribution | Description |
|---------|-----------|----------------|-------------|
| 114 | `if component_damage is None` | +1 | Default argument init |
| 116 | `if component_toggles is None` | +1 | Default argument init |
| 137 | `if ship_class` | +1 | Formula context setup |
| 139 | `if isinstance(class_data, dict)` | +1 | Type guard |
| 147 | `if not components_found` | +1 | Fallback to expected_stats |
| 162 | `if comp_def is None` | +1 | Skip missing components |
| 172 | `if not component_toggles.get(comp_id, True)` | +1 | Toggle-off check |
| 200 | `for ability_data in ... 'ResourceStorage'` | +1 | Loop: resource storage |
| 207 | `if resource_type` | +1 | Guard empty resource type |
| 213 | `for ability_data in ... 'CargoStorage'` | +1 | Loop: cargo storage |
| 225 | `if 'StrategicMovement' in abilities` | +1 | Strategic movement check |
| 234 | `for ability_data in ... 'ResourceConsumption'` | +1 | Loop: consumption |
| 241 | `if trigger == 'strategic_per_hex'` | +1 | Trigger dispatch |
| 245 | `elif trigger == 'per_turn'` | +1 | Trigger dispatch |
| 252 | `if 'WarpJump' in abilities` | +1 | Warp jump check |
| 256 | `if warp_effectiveness > 0` | +1 | Warp active check |
| 258 | `if isinstance(warp_data, dict)` | +1 | Type dispatch for warp |
| 263-267 | `else` with chained `isinstance` checks | +2 | Fallback warp value parsing |
| 271 | `if tonnage > warp_max_tonnage` | +1 | Max tonnage tracking |
| 275 | `for ability_data in ... 'ResourceConsumption'` | +1 | Loop: warp costs |
| 276 | `if ability_data.get('trigger') == 'warp_jump'` | +1 | Filter warp trigger |
| 161 | `for layer_name, comp_entry, comp_def in components_found` | +1 | Main component loop |

**Total mapped: ~24 CC points** (base 1 + 24 branches = CC ~25-26)

### Complexity Breakdown by Section

| Section | Lines | CC Contribution | % of Total |
|---------|-------|----------------|------------|
| Parameter defaults & context setup | 114-141 | 4 | 15% |
| Fallback path (no components) | 147-159 | 1 | 4% |
| Main loop guards (toggle, None) | 161-177 | 3 | 12% |
| HP/Mass accumulation | 180-192 | 0 | 0% |
| Resource/Cargo storage | 200-222 | 3 | 12% |
| Strategic movement | 225-228 | 1 | 4% |
| Resource consumption dispatch | 234-249 | 3 | 12% |
| Warp jump handling | 252-284 | 8 | 31% |

### Assessment of Proposed Decomposition

**Proposed extractions:**
1. `_initialize_base_stats(design_data, vehicle_classes)` -- targets context setup (4 CC)
2. `_accumulate_component_stats(components, modifiers, damage)` -- targets the entire main loop
3. Registry of Policy objects (MassCalculator, HpCalculator, ResourceStorageCalculator) -- strategy pattern

**Analysis:**

The **Warp jump handling** section (lines 252-284) is the single biggest CC driver at 8 points (31%). None of the three proposed extractions specifically targets it. `_accumulate_component_stats` would move the warp logic inside another function, but it wouldn't reduce that function's CC -- it would just relocate it.

A more effective decomposition:
- Extract `_accumulate_warp_stats(abilities, comp_id, comp_def, component_damage, formula_context)` to encapsulate the entire warp block. This alone removes 8 CC points.
- Extract `_accumulate_resource_consumption(abilities, effectiveness, formula_context, consumption_mult)` for the trigger-dispatched consumption (3 CC).
- The Policy object pattern is elegant but is a larger refactor. It would be most impactful for the ResourceStorage/CargoStorage/Consumption blocks which follow an identical pattern.

**Estimated residual CC after proposed extraction:** If `_accumulate_component_stats` absorbs the main loop body, the orchestrator drops to ~6 CC, but the extracted function inherits ~20 CC. The problem is merely relocated unless further decomposed internally.

**Better approach:** Extract warp (8 CC) + consumption dispatch (3 CC) + storage (3 CC) as separate methods. Orchestrator drops to ~12, each extracted method is CC 3-8 individually. Then the warp method could be further split.

### Additional Complexity Issues

- **Cognitive complexity is high:** The reader must mentally track 8 accumulator variables, understand the effectiveness model, the modifier system, the formula evaluation system, and the warp special-case simultaneously.
- **Warp value parsing (lines 263-267)** has a particularly nasty ternary chain: `ShipStatsCalculator._evaluate_value(warp_data, 0, formula_context) if isinstance(warp_data, str) and warp_data.startswith("=") else (warp_data if isinstance(warp_data, (int, float)) else 0)`. This is a 3-way type dispatch crammed into a single expression.
- **Duplicate iteration:** ResourceConsumption abilities are iterated twice -- once at line 234 for per_hex/per_turn triggers, and again at line 275 for warp_jump triggers. This is confusing and could be unified.

---

## Function 3: `load_game` (CC=26)
**File:** `game/strategy/systems/save_game_service.py`, lines 112-221

### Complexity Driver Map

| Line(s) | Construct | CC Contribution | Description |
|---------|-----------|----------------|-------------|
| 123 | `try` (outer) | +0 | Try itself doesn't add CC |
| 125 | `if not os.path.isabs(save_path)` | +1 | Path resolution |
| 130 | `if not is_valid` | +1 | Validation check |
| 135 | `try` (metadata load) | +0 | |
| 137 | `except JSONDecodeError` | +1 | |
| 140 | `except FileNotFoundError` | +1 | |
| 143 | `except PermissionError` | +1 | |
| 146 | `except OSError` | +1 | |
| 153 | `if missing_keys` | +1 | Metadata key validation |
| 158 | `if not ... _is_compatible_version` | +1 | Version check |
| 162 | `if turn_number is None` | +1 | Default turn resolution |
| 169 | `if not os.path.exists(turn_file)` | +1 | File existence check |
| 172 | `try` (turn load) | +0 | |
| 174 | `except JSONDecodeError` | +1 | |
| 178 | `except FileNotFoundError` | +1 | |
| 181 | `except PermissionError` | +1 | |
| 184 | `except OSError` | +1 | |
| 189 | `if missing_keys` (state keys) | +1 | State key validation |
| 194 | `try` (reconstruct) | +0 | |
| 197 | `except KeyError` | +1 | |
| 200 | `except (TypeError, ValueError, ValidationException)` | +1 | |
| 203 | `except (AttributeError, ImportError, RuntimeError, StateException)` | +1 | |
| 213 | `except PermissionError` (outer) | +1 | |
| 215 | `except OSError` (outer) | +1 | |
| 219 | `except (KeyError, TypeError, ...)` (outer) | +1 | |

**Total mapped: ~21 explicit CC drivers + 5 implicit from compound except tuples = CC ~26**

### Complexity Breakdown by Section

| Section | Lines | CC Contribution | % of Total |
|---------|-------|----------------|------------|
| Path resolution & validation | 125-131 | 2 | 8% |
| Metadata loading + error handling | 134-148 | 4 | 15% |
| Metadata validation | 151-159 | 2 | 8% |
| Turn number resolution | 162-163 | 1 | 4% |
| Turn file loading + error handling | 166-185 | 5 | 19% |
| State validation | 188-191 | 1 | 4% |
| Game session reconstruction + errors | 194-205 | 3 | 12% |
| Outer exception handlers | 213-221 | 3 | 12% |
| Happy path logic | 207-211 | 0 | 0% |

### Assessment of Proposed Decomposition

**Proposed extractions:**
1. `_load_save_metadata(save_path)` -- targets metadata loading section (4 CC)
2. `_load_turn_data(save_path, turn_number)` -- targets turn loading section (5 CC)
3. `_reconstruct_game_session(game_state, save_path)` -- targets reconstruction (3 CC)

**Analysis:**

This decomposition is well-targeted. The CC is overwhelmingly driven by **exception handlers** (15 of the 25 branch points come from except clauses). The proposed extraction maps cleanly onto the three I/O operations, each of which carries its own error-handling burden.

**Estimated residual CC after extraction:** The orchestrator would contain: path resolution (1), validation call (1), metadata validation (2), turn number resolution (1), state validation (1), plus calls to the 3 extracted functions. With proper error propagation (each extracted method returns a Result/tuple or raises), the orchestrator drops to ~7-8 CC.

**One concern:** The outer try/except at lines 213-221 catches 8 exception types that duplicate the inner handlers. If the extracted functions handle their own exceptions (returning error tuples), this outer handler becomes redundant except as a safety net. The decomposition should address whether to keep the outer handler.

**Missing from proposal:** The outer exception handler (3 CC) is not addressed. If extracted methods return `(result, error_msg)` tuples, the outer handler can be simplified or removed.

### Additional Complexity Issues

- **Cognitive complexity is moderate:** The function is essentially a linear pipeline of "load, validate, load, validate, reconstruct" with error handling at each step. The structure is actually quite readable despite high CC.
- **Exception handler duplication:** The metadata `try` block and the turn `try` block have identical 4-exception patterns (JSONDecodeError, FileNotFoundError, PermissionError, OSError). These could share a common loader helper.
- **The outer try/except is defensive overkill:** Lines 219-221 catch `KeyError, TypeError, ValueError, AttributeError, ImportError, ValidationException, StateException` -- 7 exception types. Most of these are already caught in inner blocks. This suggests the outer handler was added "just in case" and may mask real bugs.

---

## Function 4: `project_path` (CC=22)
**File:** `game/strategy/services/fleet_navigation_service.py`, lines 413-562

### Complexity Driver Map

| Line(s) | Construct | CC Contribution | Description |
|---------|-----------|----------------|-------------|
| 443 | `if moves_per_turn <= 0` | +1 | Early return |
| 452 | `if fleet.orders` (ternary for first_order_progress) | +1 | Conditional init |
| 459 | `while (state.path or state.orders) and current_turn < max_turns` | +3 | Main loop + `or` + `and` |
| 461 | `if iterations > max_steps` | +1 | Safety limit |
| 466 | `if not state.path and state.orders` | +2 | Path-empty + orders-exist |
| 470 | `if order.type not in MOVEMENT_ORDER_TYPES` | +1 | Action order branch |
| 477 | `if is_first_order and first_order_progress > 0` | +2 | Partial progress + `and` |
| 481 | `while action_time > 0 and current_turn < max_turns` | +2 | Inner loop + `and` |
| 486 | `if moves_left_in_turn <= 0` | +1 | Turn advancement |
| 502 | `if destination is None` | +1 | No-destination guard |
| 506 | `if order.type == OrderType.WARP` | +1 | Warp path specialization |
| 510 | `if not new_path` | +1 | No-path guard |
| 522 | `if not state.path` | +1 | Post-path-resolution guard |
| 531 | `is_warp = hex_distance(...) > 1` (boolean) | +0 | Not a branch, just assignment |
| 542 | `if not remaining_path` | +1 | Order completion check |
| 543 | `if state.orders` (ternary within) | +1 | Conditional order pop |
| 558 | `if moves_left_in_turn <= 0` | +1 | Turn advancement (second instance) |

**Total mapped: ~21 CC points** (base 1 + 21 = CC 22)

### Complexity Breakdown by Section

| Section | Lines | CC Contribution | % of Total |
|---------|-------|----------------|------------|
| Initialization & guards | 439-457 | 2 | 9% |
| Main loop condition | 459 | 3 | 14% |
| Safety limit | 461 | 1 | 5% |
| Action order handling | 466-499 | 7 | 32% |
| Movement order resolution | 501-520 | 3 | 14% |
| Step execution & advancement | 522-560 | 5 | 23% |

### Assessment of Proposed Decomposition

**Proposed extractions:**
1. `_project_action_order(state, order, moves_left_in_turn, turns_left)` -- targets action order handling (7 CC)
2. `_resolve_path_for_order(state, order, galaxy)` -- targets movement order resolution (3 CC)
3. `_advance_tick(state)` -- targets step execution

**Analysis:**

This decomposition correctly identifies the **action order handling** as the highest CC section (7 points, 32%). Extracting it would be the single most impactful change.

**However**, `_advance_tick(state)` as proposed is somewhat vague. The step execution section (lines 522-560) involves segment creation, state mutation, order popping, and turn advancement. This is more of a "process one movement step" than just "advance tick." A better name would be `_execute_movement_step(state, segments, moves_left_in_turn, current_turn)` returning updated state and counters.

**Estimated residual CC after proposed extraction:** The main `while` loop (3 CC) + safety (1) + guards (2) + calls (3 simple if-checks for None/empty returns) = ~9-10 CC. This is on the boundary but acceptable.

**Missing from proposal:** The `moves_left_in_turn` and `current_turn` tracking is duplicated in two places (action order handler at line 486 and movement step at line 558). This duplication would persist after extraction unless the turn-tracking logic is unified.

### Additional Complexity Issues

- **State threading is the real problem:** The function manually threads 5 mutable variables through the loop: `state`, `moves_left_in_turn`, `current_turn`, `is_first_order`, `first_order_progress`. This makes it fragile and hard to test individual parts.
- **Cognitive complexity is very high:** The reader must understand the outer `while` loop, the inner `while` loop for action time, the path resolution branching, the movement step logic, and the turn advancement -- all interleaved. The nesting depth reaches 4 levels (while > if > while > if).
- **Two "types" of loop iteration:** The while loop body handles two fundamentally different cases (action orders vs movement orders) which have completely different logic. This is a classic "two algorithms in one function" smell.
- **`is_first_order` flag:** This boolean flag is set once and then cleared, adding cognitive load. It would be cleaner to handle the first-order partial progress before entering the main loop.

---

## Findings

### CX-001
#### CRITICAL: Warp Jump Handling is Highest CC Driver in calculate_stats But Not Specifically Targeted
**ID:** CX-001
**Location:** `game/strategy/services/ship_stats_calculator.py:252-284`
**Issue:** The warp jump handling block contributes 8 CC points (31% of the function's complexity) through nested type checks, effectiveness gates, dual iteration of ResourceConsumption abilities, and a particularly ugly ternary chain for warp data parsing. The proposed decomposition's `_accumulate_component_stats` would absorb this complexity wholesale without reducing it.
**Impact:** The proposed refactor would relocate CC=20+ into `_accumulate_component_stats`, creating a new god function. The warp block's type-dispatch ternary (lines 263-267) is also a maintenance hazard -- any new warp data format requires modifying a nested conditional expression.
**Recommendation:** Extract `_accumulate_warp_stats(abilities, comp_id, comp_def, component_damage, formula_context, warp_max_tonnage)` as a dedicated method. Additionally, refactor the warp data parsing ternary into a `_parse_warp_tonnage(warp_data, formula_context)` helper.
**Effort:** Medium

### CX-002
#### CRITICAL: _process_queue_tick_dynamic Has 130-Line While Loop Body With 6 Mutable Variables
**ID:** CX-002
**Location:** `game/strategy/engine/production_engine.py:221-350`
**Issue:** The while loop body spans 130 lines and mutates `tick_capacity`, `item['resources_consumed']`, `item['turns_remaining']`, `remaining_cost`, `cost_this_step`, and calls `empire.consume_resources()`. The proposed decomposition covers only 52% of the CC drivers, leaving the completion check (4 CC) and cost initialization (4 CC) in the orchestrator.
**Impact:** After the proposed 3 extractions, the residual function would still have CC ~13-15, above the CC=10 threshold. The heavy variable mutation makes unit testing the inner logic difficult because each iteration depends on side effects from previous iterations.
**Recommendation:** Add two more extractions: `_calculate_remaining_cost(item) -> Dict` and `_check_completion(item, total_cost) -> bool`. This brings residual CC to ~7-9. Consider making the resource consumption step return a result object rather than mutating `item` in-place.
**Effort:** Medium

### CX-003
#### CRITICAL: project_path Threads 5 Mutable Variables Through Nested Loops
**ID:** CX-003
**Location:** `game/strategy/services/fleet_navigation_service.py:439-562`
**Issue:** The function manually threads `state`, `moves_left_in_turn`, `current_turn`, `is_first_order`, and `first_order_progress` through a while loop with an inner while loop for action time. The turn-advancement logic is duplicated at lines 486-488 and 558-560.
**Impact:** High cognitive complexity. The interleaving of action-order handling and movement-order handling in the same loop body makes it very difficult to verify correctness. The duplicate turn-advancement logic is a maintenance risk -- changes to one must be mirrored in the other.
**Recommendation:** Introduce a `ProjectionState` dataclass to bundle `state`, `moves_left_in_turn`, `current_turn`, and `segments`. Expose a `_consume_ticks(projection_state, ticks)` method that handles turn boundary crossing uniformly. This eliminates the duplication and reduces the variable threading problem.
**Effort:** Medium

### CX-004
#### MAJOR: Duplicate Exception Handler Patterns in load_game
**ID:** CX-004
**Location:** `game/strategy/systems/save_game_service.py:135-148, 172-185`
**Issue:** The metadata loading try/except block (lines 135-148) and the turn loading try/except block (lines 172-185) have identical 4-exception patterns: JSONDecodeError, FileNotFoundError, PermissionError, OSError. Each returns a different error message string but follows the same structure.
**Impact:** 8 CC points (31% of total) come from duplicated exception handling. Adding a new exception type requires updating both blocks. The pattern will be duplicated again if a third file needs loading.
**Recommendation:** Extract a `_load_json_safe(path, description) -> Tuple[Optional[dict], Optional[str]]` helper that wraps `load_json_required` with the standard 4-exception handler, returning `(data, None)` on success or `(None, error_msg)` on failure. This eliminates 4 CC points immediately.
**Effort:** Simple

### CX-005
#### MAJOR: Outer Exception Handler in load_game Is Defensive Overkill
**ID:** CX-005
**Location:** `game/strategy/systems/save_game_service.py:213-221`
**Issue:** The outer try/except catches 9 exception types (PermissionError, OSError, KeyError, TypeError, ValueError, AttributeError, ImportError, ValidationException, StateException). Most of these are already caught by inner handlers. The outer handler masks the specific inner error messages with a generic "Unexpected error" message.
**Impact:** 3 CC points contributed by handlers that may never trigger. More importantly, if an inner handler is accidentally removed during refactoring, the outer handler would silently swallow the error with a less informative message, making debugging harder.
**Recommendation:** After extracting the three helper methods (each with their own error handling), remove or significantly reduce the outer handler. If kept, limit it to truly unexpected exceptions (e.g., only `Exception` with a re-raise after logging in debug mode).
**Effort:** Simple

### CX-006
#### MAJOR: ResourceConsumption Abilities Iterated Twice in calculate_stats
**ID:** CX-006
**Location:** `game/strategy/services/ship_stats_calculator.py:234-249, 275-284`
**Issue:** `ResourceConsumption` abilities are iterated at line 234 for `strategic_per_hex` and `per_turn` triggers, then again at line 275 for `warp_jump` triggers. The second iteration is nested inside the `WarpJump` ability check, creating an asymmetric code structure where the same ability type is processed in two different places.
**Impact:** Confusing to maintain -- a developer adding a new trigger type must know to check both locations. The second iteration also only runs when `warp_effectiveness > 0`, meaning warp resource costs are silently zeroed when the warp drive is damaged, which may or may not be intended.
**Recommendation:** Unify all `ResourceConsumption` processing into a single loop that dispatches based on trigger type. Handle the warp-effectiveness gating as a post-filter rather than a structural nesting.
**Effort:** Medium

### CX-007
#### MAJOR: Dead Code Path in _process_queue_tick_dynamic Cost Initialization
**ID:** CX-007
**Location:** `game/strategy/engine/production_engine.py:253-260`
**Issue:** Lines 253-260 contain a "safety fallback" that calls `self._calculate_design_cost(item)` when `'total_cost' not in item`. However, `_calculate_design_cost` expects a `design_data` dict (with layers and components), not a queue item dict (with `design_id`, `type`, `turns_remaining`). The call would likely fail or return an empty dict. The code then has a bare `pass` after a comment acknowledging the issue.
**Impact:** This is effectively dead code that would produce incorrect results if ever reached. It adds 1 CC point and significant cognitive load (the developer reading this wonders "does this work?"). If a queue item arrives without `total_cost`, the function would proceed with `total_cost = {}`, causing `remaining_cost = {}`, triggering the `if not remaining_cost` branch, and immediately completing the item -- spawning it for free.
**Recommendation:** Replace with an explicit error: log a warning and `return` (or `queue.pop(0); continue`) when `total_cost` is missing. Do not attempt a fallback that cannot work.
**Effort:** Simple

### CX-008
#### MAJOR: Warp Data Parsing Ternary Chain
**ID:** CX-008
**Location:** `game/strategy/services/ship_stats_calculator.py:263-268`
**Issue:** The `else` branch for warp tonnage parsing uses a deeply nested ternary: `ShipStatsCalculator._evaluate_value(warp_data, 0, formula_context) if isinstance(warp_data, str) and warp_data.startswith("=") else (warp_data if isinstance(warp_data, (int, float)) else 0)`. This is a 3-way type dispatch compressed into a single expression.
**Impact:** Very low readability. The ternary contributes 2 CC points and approximately 5x the cognitive load of an equivalent if/elif/else. It also duplicates logic already present in `_evaluate_value()` which handles string formulas and numeric values.
**Recommendation:** Replace with a simple call: `tonnage = ShipStatsCalculator._evaluate_value(warp_data, 0, formula_context)`. The `_evaluate_value` method already handles str/formula, numeric, and None cases. The ternary is redundant.
**Effort:** Simple

### CX-009
#### MAJOR: Action Order Handling Block is 32% of project_path Complexity
**ID:** CX-009
**Location:** `game/strategy/services/fleet_navigation_service.py:466-499`
**Issue:** The action order handling block (lines 466-499) contains a nested while loop, two compound boolean conditions, state reconstruction, and the `is_first_order` flag management. It contributes 7 CC points (32% of the function total). This is correctly identified by the proposed `_project_action_order` extraction.
**Impact:** The inner `while` loop (lines 481-488) for consuming action time ticks is the deepest nesting point in the function (4 levels: while > if > if > while). This makes the control flow very hard to trace mentally.
**Recommendation:** The proposed `_project_action_order` extraction is correct. Return a tuple of `(new_state, moves_left_in_turn, current_turn)` from the extracted method. Handle the `is_first_order` / `first_order_progress` adjustment before entering the main loop (compute adjusted action_time for the first order once, upfront).
**Effort:** Medium

### CX-010
#### MAJOR: While Loop Condition in _process_queue_tick_dynamic Has 3 CC Points
**ID:** CX-010
**Location:** `game/strategy/engine/production_engine.py:221`
**Issue:** `while tick_capacity > 0.0001 and queue and iterations < 10` contributes 3 CC points from a single line. The `0.0001` epsilon, the `iterations < 10` safety limit, and the `queue` truthiness check are all defensive guards that add complexity.
**Impact:** The compound condition makes it unclear what the "normal" termination condition is vs. the safety conditions. The `iterations < 10` limit is especially problematic -- it silently stops processing if a tick would complete more than 10 items, which could happen with many cheap/free items.
**Recommendation:** Document the 10-iteration limit explicitly (or raise it). Consider extracting the loop body into a method that returns a status enum (CONTINUE, DONE, PAUSED, ERROR) to clarify loop termination semantics.
**Effort:** Simple

### CX-011
#### MINOR: `is_first_order` Flag Pattern in project_path
**ID:** CX-011
**Location:** `game/strategy/services/fleet_navigation_service.py:453, 477, 498, 520`
**Issue:** The `is_first_order` boolean flag is set to `True` at line 453, checked at line 477, and set to `False` at lines 498 and 520. This "flag that's set once then cleared" pattern increases cognitive load because the reader must track when it transitions.
**Impact:** Minor readability concern. The flag exists only to apply `first_order_progress` adjustment to the first action order's action_time. This special case could be handled before the main loop.
**Recommendation:** Compute the adjusted action_time for the first order (if it's an action order) before entering the main loop. Store it in a local variable or modify the first order's effective action_time. Remove the `is_first_order` flag entirely.
**Effort:** Simple

### CX-012
#### MINOR: Turn Advancement Logic Duplicated in project_path
**ID:** CX-012
**Location:** `game/strategy/services/fleet_navigation_service.py:486-488, 558-560`
**Issue:** The pattern `if moves_left_in_turn <= 0: current_turn += 1; moves_left_in_turn = moves_per_turn` appears at two locations in the function.
**Impact:** If the turn advancement logic changes (e.g., fractional movement points), both locations must be updated. Small duplication but symptomatic of the function doing too many things.
**Recommendation:** Extract `_advance_turn_if_needed(moves_left, current_turn, moves_per_turn) -> (moves_left, current_turn)` or use the `ProjectionState` dataclass from CX-003 with a `consume_tick()` method.
**Effort:** Simple

### CX-013
#### MINOR: calculate_stats Has 8 Accumulator Variables
**ID:** CX-013
**Location:** `game/strategy/services/ship_stats_calculator.py:123-131`
**Issue:** Eight accumulator variables are initialized at lines 123-131: `total_mass`, `total_hp`, `resource_storage`, `cargo_storage`, `resource_consumption_per_hex`, `resource_consumption_per_turn`, `warp_resource_costs`, `total_strategic_movement`, plus `warp_max_tonnage`. All are mutated independently in the main loop.
**Impact:** High cognitive load. The reader must mentally track which accumulators are updated by which ability type. The return dict at lines 286-297 must exactly match the set of accumulators, creating a fragile coupling.
**Recommendation:** Introduce a `StatsAccumulator` dataclass or dictionary that is passed through the loop. Each ability handler would call `accumulator.add_resource_storage(type, amount)` etc. This bundles the state and makes the accumulation pattern self-documenting.
**Effort:** Medium

### CX-014
#### MINOR: load_game Missing Keys Validation is Repeated
**ID:** CX-014
**Location:** `game/strategy/systems/save_game_service.py:151-154, 188-191`
**Issue:** The pattern `missing_keys = [k for k in required_keys if k not in data]; if missing_keys: return None, error_msg` appears twice, once for metadata keys and once for game state keys.
**Impact:** Minor duplication (2 CC). The list comprehension + conditional is small but follows the same pattern.
**Recommendation:** Extract `_validate_required_keys(data, required_keys, context_name) -> Optional[str]` that returns an error message or None. This removes 2 CC points and standardizes validation messaging.
**Effort:** Simple

### CX-015
#### MINOR: Epsilon Comparison in Completion Check
**ID:** CX-015
**Location:** `game/strategy/engine/production_engine.py:344`
**Issue:** `if consumed < total - 0.001` uses a hardcoded epsilon for floating-point comparison. This is combined with the `tick_capacity > 0.0001` epsilon at line 221 (different value). Two different epsilon values for related floating-point comparisons in the same function.
**Impact:** Inconsistent epsilon values could cause edge-case bugs where an item is "almost complete" but the capacity check says "done" or vice versa. Minor but a potential source of subtle production bugs.
**Recommendation:** Define a module-level constant `PRODUCTION_EPSILON = 0.001` (or similar) and use it consistently for all floating-point comparisons in the production engine.
**Effort:** Simple

### CX-016
#### MINOR: Compound Except Clause in load_game Outer Handler
**ID:** CX-016
**Location:** `game/strategy/systems/save_game_service.py:219`
**Issue:** `except (KeyError, TypeError, ValueError, AttributeError, ImportError, ValidationException, StateException) as e:` catches 7 exception types in a single clause. Each exception type in a compound except contributes to CC.
**Impact:** Catching this many exception types suggests uncertainty about what can go wrong. `ImportError` is particularly concerning -- if an import fails during `load_game`, that's likely a code bug, not a corrupt save file.
**Recommendation:** After refactoring inner error handling, remove or narrow this to `except Exception as e` with explicit logging that this is an unexpected error, not a known failure mode.
**Effort:** Simple

### CX-017
#### INFO: calculate_stats Fallback to expected_stats Maintains Legacy Coupling
**ID:** CX-017
**Location:** `game/strategy/services/ship_stats_calculator.py:147-159`
**Issue:** When no components are found in the design, the function falls back to reading `expected_stats` from the design data. This is a legacy compatibility path for "test fixtures and designs without component registry entries."
**Impact:** This fallback adds 1 CC point and 13 lines. Per the project's System Migration Policy ("ERADICATE the old system completely"), this fallback should eventually be removed once all test fixtures use proper component definitions.
**Recommendation:** Flag for future removal. Add a deprecation warning log when this path is taken to track how often it occurs in practice.
**Effort:** Simple (to add warning), Complex (to remove all callers)

### CX-018
#### INFO: _process_queue_tick_dynamic Has Extensive Inline Comments
**ID:** CX-018
**Location:** `game/strategy/engine/production_engine.py:221-350`
**Issue:** The function contains 25+ lines of inline comments explaining the math and logic. While individually helpful, the sheer volume of comments in a 130-line loop body contributes to the visual complexity and makes it harder to see the control flow structure.
**Impact:** Cognitive overhead. Comments like "Rate is per TURN. Rate per tick is Rate / 100." and "Clamp to remaining (handle floating point errors)" are valuable but their density suggests the code itself isn't self-explanatory enough.
**Recommendation:** After decomposition, each extracted method should be small enough that its purpose is clear from its name and parameters, reducing the need for inline commentary. Move explanatory comments to method-level docstrings.
**Effort:** Simple (done naturally as part of decomposition)

### CX-019
#### INFO: process_construction_tick Has Extensive Comments About Fleet Queue Semantics
**ID:** CX-019
**Location:** `game/strategy/engine/production_engine.py:132-165`
**Issue:** Lines 132-165 contain a 35-line stream-of-consciousness comment block debating whether fleet shipyards process queues in parallel or serial. This exploratory comment was likely written during initial implementation and left in.
**Impact:** Zero runtime impact but significant cognitive noise. A developer reading this function must parse 35 lines of deliberation before reaching the actual logic at line 166.
**Recommendation:** Condense to a 2-3 line summary comment explaining the decision (multiple yards increase speed on a single shared queue). Move the detailed reasoning to a design document or commit message.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **CX-001 (CRITICAL):** Warp jump handling in `calculate_stats` contributes 31% of CC but is not specifically targeted by the proposed decomposition. Extract `_accumulate_warp_stats` and simplify the ternary chain (CX-008 is a quick-win sub-task).

2. **CX-002 (CRITICAL):** `_process_queue_tick_dynamic` has a 130-line while loop body. The proposed 3 extractions cover only 52% of CC drivers. Add `_calculate_remaining_cost` and `_check_completion` extractions to bring residual CC below 10.

3. **CX-003 (CRITICAL):** `project_path` threads 5 mutable variables through nested loops with duplicated turn-advancement logic. Introduce a `ProjectionState` dataclass with `consume_ticks()` method to unify state management.

4. **CX-004 (MAJOR):** `load_game` has identical 4-exception handler blocks for metadata and turn loading. Extract a shared `_load_json_safe()` helper to eliminate 4 CC points with minimal effort.

5. **CX-007 (MAJOR):** Dead code in `_process_queue_tick_dynamic` cost initialization (lines 253-260) calls `_calculate_design_cost` with wrong argument type, followed by bare `pass`. Replace with explicit error handling to prevent silent free-spawn bugs.
