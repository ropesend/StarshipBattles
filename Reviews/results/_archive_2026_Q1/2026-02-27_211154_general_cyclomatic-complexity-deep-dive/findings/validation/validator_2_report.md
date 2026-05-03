# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 26
- **Confirmed:** 19
- **Downgraded:** 3
- **Rejected:** 4
- **Rejection Rate:** 15.4%

## Verdicts

#### Finding: CQ-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `empire`, `galaxy`, and `colony_or_fleet` parameters at lines 180, 182, and 185 of `_process_queue_tick_dynamic` are indeed untyped.

#### Finding: CQ-010
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** `queue.pop(0)` at lines 227 and 362 is O(n) on Python lists. Construction queues are typically small, so Info severity is appropriate.

#### Finding: CQ-011
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** The loop spans lines 161-284 (~124 lines, not 136 as claimed) and processes ~7 ability types, not 8. It is a large accumulation loop but well-structured with clear sections -- Critical overstates the urgency.

#### Finding: CQ-012
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Adding a new ability type requires modifying the main loop body in `calculate_stats`. Each ability type is handled by hardcoded `if`/`for` blocks with no extension mechanism.

#### Finding: CQ-013
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** ResourceStorage (200-210), CargoStorage (213-222), and ResourceConsumption (234-249) all follow the same iterate-evaluate-multiply-accumulate pattern with minor variations.

#### Finding: CQ-014
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 252-284 have 4 levels of nesting with a ternary-within-ternary on lines 264-268 handling non-dict warp data.

#### Finding: CQ-015
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `formula_context` is created at line 134 and threaded through approximately 11 helper call sites within `calculate_stats`. The count of ~15 in the finding is slightly overstated but the data clump pattern is real.

#### Finding: CQ-016
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The return dict at lines 286-297 has 9 keys with no TypedDict/dataclass. The fallback path at lines 149-159 duplicates the exact same 9-key structure.

#### Finding: CQ-017
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** All helper methods are `@staticmethod` and are consistently called via `ShipStatsCalculator._method()` throughout. This is the explicit, recommended pattern for calling static methods and is not inconsistent.

#### Finding: CQ-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Lines 146-159 silently fall back to `expected_stats` when no components are found, which could mask registry configuration errors. The comment explains the intent but no warning is logged.

#### Finding: CQ-019
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `load_game` has 4 try/except blocks: 1 outer (catching 9 exception types at line 219) + 3 inner (metadata at 135, turn at 172, reconstruction at 194). The nesting makes error flow hard to follow.

#### Finding: CQ-020
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 135-148 and 172-185 have identical 4-exception-type try/except patterns (JSONDecodeError, FileNotFoundError, PermissionError, OSError) with only the context strings differing.

#### Finding: CQ-021
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The outer handler catches PermissionError/OSError that could theoretically be thrown by code between inner blocks (e.g., `os.path.exists` at line 169), so it is not fully redundant. It is merely overly broad.

#### Finding: CQ-022
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Version validation (line 158) and metadata key checking (lines 151-154) are inline in the load flow rather than extracted into a reusable `_validate_metadata` method.

#### Finding: CQ-023
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 112 declares return type as `Tuple[Optional[object], str]` but the actual return is a GameSession instance. The docstring correctly says "GameSession or None" but the type annotation is imprecise.

#### Finding: CQ-024
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The claim that `load_game` "could benefit from instance configuration" is purely speculative with no concrete use case. The method works correctly as a static method and there is no demonstrated need for instance state.

#### Finding: CQ-025
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The `project_path` while loop (lines 459-561) mixes high-level order processing logic (destination computation, path computation) with low-level tick management (moves_left_in_turn, current_turn tracking).

#### Finding: CQ-026
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** NavigationState construction appears 3 times in `project_path` (lines 491-497, 513-519, 548-554), not 4 as claimed. All three could use `dataclasses.replace()` since NavigationState is a frozen dataclass.

#### Finding: CQ-027
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `is_first_order` is set to False at two separate points (lines 498 and 520) and used only once (line 477). It is a tracking flag for partial progress that could be simplified.

#### Finding: CQ-028
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 456 `max_steps = max_turns * moves_per_turn + 100` has an undocumented magic number `100` as a safety margin with no explanation for why that specific value.

#### Finding: CQ-029
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The `galaxy` parameter is untyped across all methods in `fleet_navigation_service.py` (8+ methods) and in `production_engine.py` (2 methods).

#### Finding: CQ-030
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The claim that "3 of 4 functions use Dict[str, Any] for structured data" is factually incorrect. Only `ship_stats_calculator.py` returns Dict[str, Any]. `production_engine.py` returns None (mutates in place), and `save_game_service.py` returns tuples.

#### Finding: CX-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** The warp jump block (lines 252-284) has 4 nesting levels, a ternary-within-ternary, and a nested loop -- making it the highest complexity contributor in `calculate_stats`.

#### Finding: CX-002
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** The while loop body in `_process_queue_tick_dynamic` (lines 221-350) is ~130 lines with 6 mutable variables (tick_capacity, iterations, remaining_cost, max_ticks_needed, cost_this_step, is_complete).

#### Finding: CX-003
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** `project_path` threads 5-6 mutable variables through nested while loops (main at line 459, inner at line 481). Turn-advancement logic is duplicated at lines 486-488 and 558-560.

#### Finding: CX-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Identical 4-exception-type patterns at lines 135-148 and 172-185 in `save_game_service.py`. Note: this duplicates finding CQ-020.
