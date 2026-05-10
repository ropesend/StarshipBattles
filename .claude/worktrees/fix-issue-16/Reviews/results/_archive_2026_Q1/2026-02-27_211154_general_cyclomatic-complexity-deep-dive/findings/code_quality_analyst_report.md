# Code Quality Analyst Report

**Review:** Cyclomatic Complexity Deep Dive
**Date:** 2026-02-27
**Agent:** Code Quality Analyst
**Finding Prefix:** CQ

---

## Summary

- **Total issues found:** 28
- **Critical:** 3, **Major:** 10, **Minor:** 11, **Info:** 4

### Per-Function Overview

| Function | Lines | Max Nesting | Issues | Most Severe |
|----------|-------|-------------|--------|-------------|
| `_process_queue_tick_dynamic` | 173 | 4 | 10 | Critical |
| `calculate_stats` | 210 | 4 | 8 | Critical |
| `load_game` | 109 | 4 | 6 | Major |
| `project_path` | 149 | 4 | 4 | Major |

---

## Findings

---

### Function 1: `_process_queue_tick_dynamic` (production_engine.py:177-351)

---

#### CRITICAL: Single Responsibility Violation - Function Does 5+ Distinct Jobs
**ID:** CQ-001
**Location:** `game/strategy/engine/production_engine.py:177-351`
**Issue:** This function handles (1) queue item validation, (2) fleet location constraints, (3) cost initialization fallback, (4) remaining cost calculation, (5) limiting resource/time calculation, (6) per-resource consumption calculation, (7) affordability checks, (8) resource mutation on the empire, (9) UI turns_remaining estimation, and (10) completion detection with delegation. These are at least 5 distinct responsibilities crammed into a single method.
**Impact:** Any change to resource consumption, cost tracking, validation, or completion logic forces a developer to understand and re-read the entire 173-line function. Bug risk during modification is high.
**Recommendation:** Extract into the proposed helpers: `_validate_queue_item`, `_calculate_tick_expenditure`, `_apply_production_progress`. Each becomes independently testable and has a single concern.
**Effort:** Medium

---

#### CRITICAL: Defensive Code Masking Bugs - Silent `pass` After Fallback
**ID:** CQ-002
**Location:** `game/strategy/engine/production_engine.py:253-260`
**Issue:** When `total_cost` is missing from a queue item, the code attempts `self._calculate_design_cost(item)` but then immediately follows with `pass`. The comment says "Should have been set by controller, but safety fallback" and "we can assume if it's missing, we can't process it accurately yet." The `_calculate_design_cost` expects `design_data` (a full design dict with layers), not a queue item dict. This fallback is structurally broken -- it will either fail silently or produce incorrect costs, and the `pass` ensures no one is alerted.
**Impact:** If a queue item ever reaches this code without `total_cost`, the function will silently produce incorrect resource consumption. This is the kind of defensive code that actively hides bugs rather than preventing them.
**Recommendation:** Replace with a clear guard clause: if `total_cost` is missing, log a warning and skip the item (or return). Do not attempt a fallback that cannot work correctly.
**Effort:** Simple

---

#### MAJOR: Magic Numbers Throughout
**ID:** CQ-003
**Location:** `game/strategy/engine/production_engine.py:221,291,297,309,344`
**Issue:** Multiple magic numbers: `0.0001` (tick capacity epsilon), `10` (max iterations), `100.0` (ticks per turn), `0.001` (completion epsilon). The `100.0` divisor appears twice (lines 291 and 309). None of these are named constants.
**Impact:** The relationship between these numbers and the game's tick system is implicit. A developer changing the tick rate would need to grep for `100.0` and hope they find all instances. The two different epsilon values (`0.0001` and `0.001`) add confusion -- are they intentionally different?
**Recommendation:** Define `TICKS_PER_TURN = 100`, `TICK_CAPACITY_EPSILON = 0.0001`, `COMPLETION_EPSILON = 0.001`, `MAX_QUEUE_ITERATIONS = 10` as module-level or class-level constants.
**Effort:** Simple

---

#### MAJOR: Feature Envy - Excessive Manipulation of External Objects
**ID:** CQ-004
**Location:** `game/strategy/engine/production_engine.py:319-326`
**Issue:** The function directly queries and mutates `empire` (via `has_resources`, `consume_resources`) and `item` dict internals (setting nested dict values). It reaches deep into the `item` dict structure multiple times per iteration: `item.get('total_cost', {})`, `item.get('resources_consumed', {})`, `item['resources_consumed'][res]`, `item['turns_remaining']`. This is classic feature envy -- the function knows too much about the internal structure of queue items.
**Impact:** If the queue item schema changes, this function must be updated in multiple places. The knowledge of the item dict schema is spread across the entire function body.
**Recommendation:** Introduce a `QueueItemProgress` helper class or at minimum extract `_calculate_remaining_cost(item)` and `_consume_resources_for_step(item, empire, cost_this_step)` to encapsulate dict access patterns.
**Effort:** Medium

---

#### MAJOR: Inconsistent Error Handling - Mix of `return` and `continue` and `pop`
**ID:** CQ-005
**Location:** `game/strategy/engine/production_engine.py:226-249`
**Issue:** Invalid items are handled with `queue.pop(0)` + `continue`. Complex-only filter violations cause `return` (stopping entire queue). Fleet location failures cause `return`. Zero production rate causes `return`. Insufficient resources causes `return`. The inconsistency between "skip this item" and "stop processing entirely" is confusing, and the rationale for each choice is only partially documented.
**Impact:** When debugging production stalls, it's difficult to determine which error path was taken. The distinction between "item blocks queue" and "skip item" behaviors is only explained in ad-hoc comments.
**Recommendation:** Establish a clear, documented error taxonomy: items that are "invalid and removable" vs "valid but blocked." Return an enum/status from the validation extract rather than relying on control flow.
**Effort:** Medium

---

#### MINOR: Narrative Comments Replace Readable Code
**ID:** CQ-006
**Location:** `game/strategy/engine/production_engine.py:300-316`
**Issue:** Multiple inline comments explain what the code is doing step-by-step, e.g., "Rate * Fraction * 1/100", "Actually, wait. We consume ALL resources proportionally." and "Clamp to remaining (handle floating point errors)". These comments exist because the code structure doesn't communicate intent clearly.
**Impact:** Comments describing "what" rather than "why" become stale as code evolves. The need for these comments signals the code should be restructured into well-named functions.
**Recommendation:** Extracting into `_calculate_tick_expenditure` with clear parameter names would eliminate the need for most of these comments.
**Effort:** Simple (as part of decomposition)

---

#### MINOR: Long Parameter List (8 Parameters)
**ID:** CQ-007
**Location:** `game/strategy/engine/production_engine.py:177-187`
**Issue:** The function takes 8 parameters: `self`, `queue`, `empire`, `tick`, `galaxy`, `save_path`, `production_rate`, `colony_or_fleet`, `is_complex_only`. This exceeds the typical threshold of 5.
**Impact:** Call sites are hard to read (as evidenced by the multi-line calls in `process_construction_tick`). The parameter list reveals the function is doing too much -- it needs galaxy for location checks, save_path for spawning, production_rate for consumption, etc.
**Recommendation:** After decomposition, completion/spawning parameters (`galaxy`, `save_path`) can be isolated to `_complete_item`. A `ProductionContext` dataclass grouping `empire`, `colony_or_fleet`, `galaxy`, `save_path` would reduce parameter sprawl.
**Effort:** Medium

---

#### MINOR: `process_construction_tick` Contains Stream-of-Consciousness Comments
**ID:** CQ-008
**Location:** `game/strategy/engine/production_engine.py:133-158`
**Issue:** Lines 133-158 contain a 25-line block of rambling comments that read like developer notes/thinking-out-loud: "Wait, BuildQueueSource splits fleet queue into multiple sources for UI, but the Fleet data object has a single `construction_queue` list..." This is reasoning preserved in production code, not documentation.
**Impact:** Future developers will be confused about whether these comments describe current behavior or historical speculation. They add significant noise to the file.
**Recommendation:** Replace with a single concise comment explaining the decided behavior: "Multiple shipyards on a fleet multiply production rate for the shared queue."
**Effort:** Simple

---

#### MINOR: Untyped `empire` and `galaxy` Parameters
**ID:** CQ-009
**Location:** `game/strategy/engine/production_engine.py:177-187`
**Issue:** `empire`, `galaxy`, and `colony_or_fleet` parameters lack type annotations. The method signature uses bare names with no hints, contradicting the project's type hint conventions.
**Impact:** IDE tooling cannot provide autocomplete or type checking for these parameters. Developers must read the implementation to understand what methods are called on these objects.
**Recommendation:** Add proper type annotations. If avoiding circular imports is the concern, use `TYPE_CHECKING` guard with string annotations.
**Effort:** Simple

---

#### INFO: `queue.pop(0)` is O(n) on Python Lists
**ID:** CQ-010
**Location:** `game/strategy/engine/production_engine.py:227,362`
**Issue:** `queue.pop(0)` on a Python list is O(n) because it requires shifting all remaining elements. This is called potentially multiple times per tick.
**Impact:** For typical queue sizes (< 20 items), this is negligible. Only relevant if queue sizes grow significantly.
**Recommendation:** Consider `collections.deque` if performance profiling ever indicates this is a bottleneck. Low priority.
**Effort:** Simple

---

### Function 2: `calculate_stats` (ship_stats_calculator.py:87-297)

---

#### CRITICAL: Monolithic Accumulation Loop - 136 Lines of Sequential Ability Processing
**ID:** CQ-011
**Location:** `game/strategy/services/ship_stats_calculator.py:161-285`
**Issue:** The main component iteration loop (lines 161-285) processes 8 different ability types sequentially: mass, HP, ResourceStorage, CargoStorage, StrategicMovement, ResourceConsumption, WarpJump, and warp resource costs. Each ability type has its own block of 5-20 lines with similar patterns (get ability data, evaluate formula, apply multiplier, accumulate). This violates Single Responsibility -- the function is simultaneously a mass calculator, HP calculator, storage calculator, movement calculator, and warp calculator.
**Impact:** Adding a new ability type requires modifying this already-complex function. Each block has subtle variations (some apply `capacity_mult`, others apply `consumption_mult`, warp uses separate effectiveness) that are easy to get wrong when copying patterns.
**Recommendation:** The proposed Policy object pattern (MassCalculator, HpCalculator, ResourceStorageCalculator) is the correct approach. Each ability accumulator becomes a separate, testable unit with a common interface.
**Effort:** Complex

---

#### MAJOR: Open/Closed Violation - Adding Abilities Requires Modifying calculate_stats
**ID:** CQ-012
**Location:** `game/strategy/services/ship_stats_calculator.py:161-285`
**Issue:** To add support for a new ability type (e.g., `StealthField`, `ShieldBoost`), a developer must add a new block to the middle of this 136-line loop, following the pattern of existing blocks but adapting for the new ability's specifics. This directly violates the Open/Closed Principle.
**Impact:** Each addition increases the function's cyclomatic complexity and length. The function has already grown from what was likely a simpler design to its current CC=26.
**Recommendation:** Registry of ability processors: `Dict[str, AbilityProcessor]` where each processor handles its own accumulation. The `calculate_stats` loop becomes: iterate components, for each ability call `processor.accumulate(...)`.
**Effort:** Complex

---

#### MAJOR: DRY Violation - Repeated Ability Processing Pattern
**ID:** CQ-013
**Location:** `game/strategy/services/ship_stats_calculator.py:200-284`
**Issue:** The pattern `for ability_data in _get_ability_list(abilities, 'X'): evaluate_value, apply_multiplier, accumulate_to_dict` repeats for ResourceStorage (lines 200-210), CargoStorage (lines 213-222), and ResourceConsumption (lines 234-249). Each follows the same structure with minor variations (different dict keys, different multipliers).
**Impact:** If the formula evaluation or multiplier application logic changes, it must be updated in 3+ places. Bugs in one copy may not be replicated in the fix for others.
**Recommendation:** Extract a generic `_accumulate_resource_ability(abilities, ability_name, multiplier, target_dict, effectiveness, formula_context)` helper.
**Effort:** Medium

---

#### MAJOR: Nested Conditional Complexity in WarpJump Handling
**ID:** CQ-014
**Location:** `game/strategy/services/ship_stats_calculator.py:252-284`
**Issue:** The WarpJump block has 4 levels of nesting: `if 'WarpJump' in abilities` -> `if warp_effectiveness > 0` -> `if isinstance(warp_data, dict)` / `else` -> `if isinstance(warp_data, str) and warp_data.startswith("=")`. The `else` branch (lines 264-268) contains a ternary-within-ternary expression that is particularly hard to read.
**Impact:** The triple-nested ternary on lines 264-268 is a readability hazard. A developer modifying warp logic must trace through multiple type-check branches to understand what value `tonnage` receives.
**Recommendation:** Extract `_calculate_warp_tonnage(warp_data, formula_context) -> int` to isolate the type-juggling logic.
**Effort:** Simple

---

#### MAJOR: Data Clump - Formula Context Passed to Every Helper
**ID:** CQ-015
**Location:** `game/strategy/services/ship_stats_calculator.py:134-141, 174, 185, 190, etc.`
**Issue:** `formula_context` is constructed once (lines 134-141) and then threaded through every `_get_numeric_value`, `_evaluate_value`, and `_get_ability_value` call. It's a required parameter for ~15 call sites within this single function.
**Impact:** Every helper method needs the context parameter, adding visual noise. The context construction and usage are separated by 150+ lines.
**Recommendation:** Make `formula_context` an instance variable set at the start of `calculate_stats`, or wrap the accumulation in a small state object that carries context.
**Effort:** Simple

---

#### MINOR: 9-Key Return Dictionary - Implicit Contract
**ID:** CQ-016
**Location:** `game/strategy/services/ship_stats_calculator.py:286-297`
**Issue:** The return value is a 9-key dictionary with no type definition. The expected keys are documented in the docstring but not enforced by a TypedDict or dataclass. The fallback path (lines 148-159) must duplicate this same 9-key structure.
**Impact:** Consumers must know the exact key names. Misspellings fail silently (returning `None` from `.get()`). The duplication between the normal return and the fallback return means adding a new stat key requires updating two places.
**Recommendation:** Define a `ShipStats` TypedDict or dataclass to formalize the return contract. Both the normal and fallback paths populate the same type.
**Effort:** Medium

---

#### MINOR: Inconsistent Static vs Instance Method Usage
**ID:** CQ-017
**Location:** `game/strategy/services/ship_stats_calculator.py:174-284`
**Issue:** Inside the instance method `calculate_stats`, every helper is called as `ShipStatsCalculator._get_numeric_value(...)` or `ShipStatsCalculator._evaluate_value(...)` -- using the explicit class name rather than `self._get_numeric_value(...)` (which would also work for static methods). This verbose calling convention adds visual noise throughout the function.
**Impact:** Readability is reduced by the repeated `ShipStatsCalculator.` prefix. If any of these methods are ever changed from `@staticmethod` to instance methods, every call site in this function must be updated.
**Recommendation:** Use `self.` for calling static methods from within instance methods. Python allows this and it's more concise.
**Effort:** Simple

---

#### INFO: Expected Stats Fallback May Hide Missing Registry Entries
**ID:** CQ-018
**Location:** `game/strategy/services/ship_stats_calculator.py:146-159`
**Issue:** When no components are found in the registry, the function silently falls back to `expected_stats` from the design data. This is documented as handling "test fixtures and designs without component registry entries," but it means a misconfigured registry will produce no error -- just quietly use cached stats.
**Impact:** In production, if the component registry fails to load, all ships would silently use their `expected_stats` cache, which may be outdated. This could mask registry initialization bugs.
**Recommendation:** Log a warning when falling back to `expected_stats`, or distinguish between "design has no components" (legitimate) and "registry lookup failed for all components" (likely bug).
**Effort:** Simple

---

### Function 3: `load_game` (save_game_service.py:112-221)

---

#### MAJOR: Excessive Exception Handling - 7 Separate Try/Except Blocks
**ID:** CQ-019
**Location:** `game/strategy/services/save_game_service.py:123-221`
**Issue:** The function contains an outer try/except (line 123) wrapping the entire body, plus 2 inner try/except blocks for metadata loading (line 135) and turn data loading (line 172), and a separate try/except for game session reconstruction (line 194). The outer catch-all on line 219 catches `KeyError, TypeError, ValueError, AttributeError, ImportError, ValidationException, StateException` -- 7 exception types. The inner blocks also catch 4 types each (`JSONDecodeError, FileNotFoundError, PermissionError, OSError`).
**Impact:** The layered exception handling is the primary driver of CC=26. Many of these exception types are redundant between layers (e.g., `PermissionError` is caught both at line 143 and line 213). The catch-all outer block makes it impossible for inner handlers to propagate meaningful error context upward.
**Recommendation:** The proposed decomposition (`_load_save_metadata`, `_load_turn_data`, `_reconstruct_game_session`) naturally isolates exception handling. Each extracted method can have focused error handling, and the outer method becomes a simple orchestrator with minimal catch logic.
**Effort:** Medium

---

#### MAJOR: DRY Violation - Duplicate Error Handling Pattern for JSON Loading
**ID:** CQ-020
**Location:** `game/strategy/services/save_game_service.py:135-148 vs 172-185`
**Issue:** The metadata loading block (lines 135-148) and the turn data loading block (lines 172-185) follow the identical pattern: `try: load_json_required(path)` / `except JSONDecodeError` / `except FileNotFoundError` / `except PermissionError` / `except OSError`. Each exception handler logs an error and returns `(None, error_message)`. The only differences are the file path and the user-facing message text.
**Impact:** Adding a new exception type (or changing the error message format) requires updating both blocks identically. This duplication is the most straightforward DRY violation in all four functions.
**Recommendation:** Extract `_load_json_safely(path, description) -> Tuple[Optional[dict], Optional[str]]` that encapsulates the try/except pattern and returns either the data or a user-facing error message.
**Effort:** Simple

---

#### MAJOR: Redundant Outer Exception Handler Catches Already-Handled Types
**ID:** CQ-021
**Location:** `game/strategy/services/save_game_service.py:213-221`
**Issue:** The outer `except` block on line 213 catches `PermissionError` and `OSError`, both of which are already handled by the inner blocks at lines 143-148 and 181-185. The only way execution reaches the outer handler is if these exceptions occur outside the inner try blocks (e.g., during path resolution at line 126, or `_validate_save` at line 129). But `_validate_save` only calls `os.path.exists` and `os.path.isdir`, which don't raise `PermissionError` in typical usage.
**Impact:** The redundant catch creates confusion about which handler will actually catch errors. The catch-all for 7 exception types (line 219) is a code smell indicating the developer wasn't sure what could go wrong.
**Recommendation:** After extracting `_load_save_metadata` and `_load_turn_data`, the outer function only needs to handle the orchestration-level exceptions. The 7-type catch-all should be replaced with a single `except Exception` with logging, or ideally removed entirely.
**Effort:** Simple (as part of decomposition)

---

#### MINOR: Validation Logic Embedded in Loading Flow
**ID:** CQ-022
**Location:** `game/strategy/services/save_game_service.py:129-159`
**Issue:** Version validation, metadata key checking, and save structure validation are all inline in the load flow. Lines 151-154 perform metadata key validation, lines 157-159 perform version compatibility check. These are validation concerns mixed with I/O concerns.
**Impact:** The validation logic cannot be reused (e.g., for a "validate save without loading" feature) without extracting it.
**Recommendation:** Group validation into `_validate_metadata(metadata) -> Optional[str]` returning an error message or None.
**Effort:** Simple

---

#### MINOR: Inconsistent Return Type Documentation
**ID:** CQ-023
**Location:** `game/strategy/services/save_game_service.py:112-121`
**Issue:** The return type is `Tuple[Optional[object], str]` where the first element is documented as "GameSession or None". Using `object` instead of the actual type (even as a string annotation `'GameSession'`) provides no type safety.
**Impact:** Static analysis tools and IDE autocomplete cannot determine the return type. Callers must cast or assert the type.
**Recommendation:** Use `TYPE_CHECKING` import to annotate as `Tuple[Optional['GameSession'], str]`.
**Effort:** Simple

---

#### INFO: Static Method Could Benefit from Instance Context
**ID:** CQ-024
**Location:** `game/strategy/services/save_game_service.py:111`
**Issue:** `load_game` is a `@staticmethod` but internally imports and constructs `GameSession`. If `SaveGameService` were instantiated with configuration (e.g., save directory, version), the static method limitation would be unnecessary.
**Impact:** Minor -- the current design works. However, making `save_path` resolution and version checking configurable would improve testability.
**Recommendation:** Consider converting to an instance method in future refactoring, accepting configuration via constructor DI.
**Effort:** Medium

---

### Function 4: `project_path` (fleet_navigation_service.py:413-562)

---

#### MAJOR: Mixed Abstraction Levels in Main Loop
**ID:** CQ-025
**Location:** `game/strategy/services/fleet_navigation_service.py:459-561`
**Issue:** The main `while` loop mixes high-level order processing (action orders vs movement orders, path computation) with low-level tick management (decrementing `moves_left_in_turn`, incrementing `current_turn`). The action order handling block (lines 470-499) contains its own inner `while` loop for consuming action time ticks, creating a loop-within-a-loop pattern.
**Impact:** The two levels of concern (order processing and tick accounting) are entangled. Changing the tick system (e.g., fractional movement costs) requires understanding both concerns simultaneously.
**Recommendation:** The proposed `_project_action_order` and `_advance_tick` extractions directly address this. The main loop should only deal with order-level decisions, delegating tick management to helpers.
**Effort:** Medium

---

#### MAJOR: NavigationState Reconstruction Repeated 4 Times
**ID:** CQ-026
**Location:** `game/strategy/services/fleet_navigation_service.py:491-497, 513-519, 548-554`
**Issue:** The pattern of constructing a new `NavigationState` with most fields copied from the current state appears 3 times within `project_path` (lines 491, 513, 548) and multiple times in `compute_next_step`. Each construction repeats `speed=state.speed, can_warp=state.can_warp`.
**Impact:** If `NavigationState` gains a new field, every construction site must be updated. This is a maintenance trap.
**Recommendation:** Add a `NavigationState.with_updates(location=..., path=..., orders=...)` method that creates a copy with specified fields changed, similar to `dataclasses.replace()`. Since `NavigationState` is a frozen dataclass, `dataclasses.replace(state, location=next_hex, path=remaining)` already works.
**Effort:** Simple

---

#### MINOR: Inconsistent First-Order Progress Tracking
**ID:** CQ-027
**Location:** `game/strategy/services/fleet_navigation_service.py:452-453, 477-478, 498, 520`
**Issue:** `is_first_order` and `first_order_progress` are special-case variables that track whether the current order is the first one (to account for partial progress). `is_first_order` is set to `False` in two different places (lines 498 and 520), creating subtle timing concerns. This is a "temporary field" code smell -- variables that only matter for one specific iteration.
**Impact:** The first-order special case adds 2 variables and 3 conditional checks to a function that's already complex. If the logic for tracking partial progress changes, all three touch points must be coordinated.
**Recommendation:** Handle first-order adjustment before entering the main loop by pre-adjusting `moves_left_in_turn` based on `execution_progress`, eliminating the need for in-loop special casing.
**Effort:** Medium

---

#### MINOR: Magic Number for Safety Limit Calculation
**ID:** CQ-028
**Location:** `game/strategy/services/fleet_navigation_service.py:456`
**Issue:** `max_steps = max_turns * moves_per_turn + 100` -- the `+ 100` is an arbitrary safety buffer with no documentation of why 100 was chosen.
**Impact:** Minor -- the safety limit is reasonable in practice. But the number lacks justification.
**Recommendation:** Define as `PROJECTION_SAFETY_MARGIN = 100` with a comment explaining the rationale (e.g., accounts for order transitions and path recalculations).
**Effort:** Simple

---

## Cross-Function Patterns

---

#### MINOR: Untyped `galaxy` Parameter Across All 4 Functions
**ID:** CQ-029 (Cross-cutting)
**Location:** All four files
**Issue:** The `galaxy` parameter appears in `_process_queue_tick_dynamic`, `project_path`, `compute_next_step`, `calculate_fleet_next_hex`, and `_complete_item` without type annotations. This is the most common untyped parameter across all four functions.
**Impact:** Makes it impossible to understand the Galaxy API contract without reading implementation code.
**Recommendation:** Create a `Galaxy` protocol or use `TYPE_CHECKING` imports to annotate consistently.
**Effort:** Simple

---

#### INFO: Consistent Use of Dict Returns Instead of Typed Objects
**ID:** CQ-030 (Cross-cutting)
**Location:** `production_engine.py` (queue items as dicts), `ship_stats_calculator.py` (stats as dict), `save_game_service.py` (metadata as dict)
**Issue:** Three of the four functions heavily use `Dict[str, Any]` for structured data (queue items, ship stats, save metadata). Only `fleet_navigation_service.py` uses proper dataclasses (`NavigationState`, `PathSegment`, `NavigationStep`).
**Impact:** Dict-based data lacks IDE support, type checking, and self-documentation. Key typos produce silent `None` returns instead of `AttributeError`.
**Recommendation:** `fleet_navigation_service.py` demonstrates the better pattern. Apply similar dataclass/TypedDict definitions for queue items and ship stats.
**Effort:** Medium (cross-project)

---

## Top 5 Priority Issues

1. **CQ-001 (CRITICAL):** `_process_queue_tick_dynamic` SRP violation -- 5+ responsibilities in 173 lines. This is the highest-impact decomposition target because the function's breadth makes every modification risky.

2. **CQ-011 (CRITICAL):** `calculate_stats` monolithic accumulation loop -- 136 lines processing 8 ability types. The Open/Closed violation (CQ-012) means this function grows with every new ability type.

3. **CQ-002 (CRITICAL):** Silent broken fallback in `_process_queue_tick_dynamic` -- the `total_cost` initialization fallback calls `_calculate_design_cost` with the wrong data type and then `pass`es. This is a latent production bug.

4. **CQ-019/CQ-020 (MAJOR):** `load_game` duplicated exception handling -- the identical 4-exception-type try/except pattern appears twice, and the outer catch-all adds a third redundant layer. Extracting `_load_json_safely` would cut the CC nearly in half.

5. **CQ-026 (MAJOR):** `NavigationState` reconstruction duplication in `project_path` -- using `dataclasses.replace()` is a simple fix that eliminates 3 copies of the same 6-line construction pattern.

---

## Decomposition Impact Assessment

### Will the proposed decompositions address the identified quality issues?

| Proposed Extraction | Issues Addressed | Issues NOT Addressed |
|---|---|---|
| `_validate_queue_item` | CQ-001, CQ-005 | CQ-002 (needs separate fix), CQ-009 |
| `_calculate_tick_expenditure` | CQ-001, CQ-003, CQ-006 | CQ-004 (partially) |
| `_apply_production_progress` | CQ-001, CQ-004, CQ-006 | CQ-007 (needs context object) |
| `_initialize_base_stats` | CQ-015, CQ-016 (partially) | CQ-011, CQ-012 (need policy pattern) |
| `_accumulate_component_stats` | CQ-011 (partially) | CQ-012, CQ-013 (need ability processors) |
| Policy objects | CQ-011, CQ-012, CQ-013, CQ-014 | CQ-015, CQ-016 (need separate fixes) |
| `_load_save_metadata` | CQ-019, CQ-020, CQ-022 | CQ-021 (still needs outer cleanup) |
| `_load_turn_data` | CQ-019, CQ-020 | -- |
| `_reconstruct_game_session` | CQ-019, CQ-021 | CQ-023 (needs type annotation) |
| `_project_action_order` | CQ-025, CQ-027 | CQ-026 (needs `replace()`) |
| `_resolve_path_for_order` | CQ-025 | -- |
| `_advance_tick` | CQ-025, CQ-028 | -- |

**Conclusion:** The proposed decompositions are well-targeted and would address ~70% of identified issues. The remaining 30% require supplementary fixes: named constants (CQ-003, CQ-028), type annotations (CQ-009, CQ-023, CQ-029), TypedDict/dataclass returns (CQ-016, CQ-030), and the broken fallback fix (CQ-002).
