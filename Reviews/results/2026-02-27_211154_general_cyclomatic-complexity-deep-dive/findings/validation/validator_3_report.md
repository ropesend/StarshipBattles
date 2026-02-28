# Validation Report: Validator 3

## Summary
- **Findings Reviewed:** 26
- **Confirmed:** 16
- **Downgraded:** 8
- **Rejected:** 2
- **Rejection Rate:** 7.7%

## Verdicts

#### Finding: CX-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The outer try/except at lines 213-221 does catch exception types (KeyError, TypeError, ValueError, AttributeError, ImportError, ValidationException, StateException) that are already caught by inner handlers at lines 197-205. PermissionError and OSError are also caught by inner blocks at lines 143-148 and 180-184. This is genuinely redundant defensive layering.

#### Finding: CX-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** ResourceConsumption abilities are iterated at line 234 (for per_hex/per_turn triggers) and again at line 275 (for warp_jump trigger). Both use `_get_ability_list(abilities, 'ResourceConsumption')` on the same ability data. This is a genuine double iteration, though the second is semantically gated behind the `WarpJump` ability check.

#### Finding: CX-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** At line 255, `_calculate_design_cost(item)` is called with `item` (a queue dict with design_id, type, etc.) rather than design data containing layers/components. The method expects a design_data dict with component layers. The comments at lines 256-260 acknowledge this problem ("Need to load design?") and the `pass` at line 260 confirms it silently falls through. This is a real dead/broken code path.

#### Finding: CX-008
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Lines 263-268 do show a nested ternary for handling warp_data that could be a string formula, int/float, or dict. However, this is a 3-way type dispatch that is locally comprehensible and only 6 lines. Major severity is overstated for what amounts to a readability nit.

#### Finding: CX-009
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The action order handling block at lines 466-499 contains a nested while loop (line 481), compound boolean conditions, tick accounting logic, and state mutation. This is the most complex section of `project_path` and the CC contribution claim is credible.

#### Finding: CX-010
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The while condition at line 221 (`while tick_capacity > 0.0001 and queue and iterations < 10`) does contain 3 boolean clauses. However, each is simple and clearly readable: epsilon guard, empty-queue guard, and iteration safety limit. This is a standard loop guard pattern, not genuinely problematic complexity.

#### Finding: CX-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `is_first_order` is set to True at line 453, then set to False at line 498 (after action order processing) and line 520 (after path computation). This is a textbook boolean flag pattern that adds cognitive load, though the scope is limited.

#### Finding: CX-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The turn advancement pattern (`if moves_left_in_turn <= 0: current_turn += 1; moves_left_in_turn = moves_per_turn`) appears at lines 486-488 (inside action order while loop) and lines 558-560 (after movement step). These are structurally identical.

#### Finding: CX-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 123-131 declare 9 accumulators (total_mass, total_hp, resource_storage, cargo_storage, resource_consumption_per_hex, resource_consumption_per_turn, warp_resource_costs, total_strategic_movement, warp_max_tonnage). The finding claims 8 but there are actually 9 -- the issue is real regardless.

#### Finding: CX-014
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The `missing_keys = [k for k in required... if k not in ...]` pattern with subsequent error return appears at lines 151-154 (metadata validation) and lines 188-191 (game state validation). Same structure, different required key lists. A minor DRY violation but real.

#### Finding: CX-015
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 344 uses `consumed < total - 0.001` while line 221 uses `tick_capacity > 0.0001`. These are different epsilons (0.001 vs 0.0001) in the same file, which could lead to edge-case inconsistencies. The finding accurately identifies this discrepancy.

#### Finding: CX-016
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 219 catches `(KeyError, TypeError, ValueError, AttributeError, ImportError, ValidationException, StateException)` -- that is 7 exception types in a single except clause. ImportError is unusual for a load operation at this level since inner blocks already catch it at line 203. The compound clause is real.

#### Finding: CX-017
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Lines 147-159 show a fallback to `expected_stats` when no components are found in design layers. The comment says "handles test fixtures and designs without component registry entries." This is indeed a legacy compatibility path that couples the calculator to the old expected_stats format.

#### Finding: CX-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The production loop body (lines 221-350) does contain extensive inline comments explaining rationale for rate calculations, clamping, and completion checks. While comments are generally good, the density here suggests the code itself could be clearer.

#### Finding: CX-019
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Lines 132-165 contain a ~33-line comment block that reads as a stream-of-consciousness debate about how fleet shipyard processing should work ("Wait, BuildQueueSource splits...", "If so, 'parallel' processing means...", "So I should multiply rate by shipyard count"). This is design deliberation left in production code.

#### Finding: DS-001
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** This is a design critique about a proposed extraction, not about actual code in the repository. The method `_apply_production_progress` does not exist in the codebase. The finding is critiquing a hypothetical refactoring suggestion. As a design observation it has minor value, but it is not a code defect.

#### Finding: DS-002
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 274-276 handle the "no remaining cost, complete immediately" case. This sits between cost validation and the resource expenditure logic. The finding correctly notes this is an edge case (free items) that would need explicit handling in any extraction-based refactoring.

#### Finding: DS-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** This is the same issue as CX-007 viewed from a design perspective. `_calculate_design_cost(item)` at line 255 receives a queue item dict, not a design data dict with component layers. The method then falls through with `pass`. This is a genuine code smell.

#### Finding: DS-004
**Original Severity:** Info
**Verdict:** DOWNGRADED(Info)
**Reason:** This is a design analysis observation about hypothetical CC reduction from proposed extractions. The claim that the orchestrator would still be CC ~8-10 after 3 extractions is reasonable given the remaining branching, but this is speculative analysis about unimplemented changes, not a code issue. Confirmed as Info-level observation.

#### Finding: DS-005
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** The finding critiques a proposed extraction (`_accumulate_component_stats`) that does not exist in the codebase. The underlying observation is valid: lines 161-284 of ship_stats_calculator.py do have high CC (~20) with many branches for different ability types. However, "Critical" is too high for a critique of a proposed (not implemented) refactoring approach. The actual code complexity is real and Major-worthy.

#### Finding: DS-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The WarpJump block at lines 252-284 is the most complex section of `calculate_stats`, with a nested conditional for warp_data type dispatch (dict vs string vs number), warp effectiveness gating, and a second ResourceConsumption iteration for warp_jump triggers. The observation that no targeted extraction addresses this specific block is valid design feedback.

#### Finding: DS-007
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** This critiques a hypothetical "policy pattern" that is not implemented in the codebase. The ship_stats_calculator.py has no registry-based policy abstraction -- it directly handles ability types in if/elif chains. As a warning against overengineering a future refactor, this is valid at Minor level, but Major is too high for something that doesn't exist in the code.

#### Finding: DS-008
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** This critiques a proposed extraction (`_initialize_base_stats`) that does not exist. The observation that extracting lines 123-140 would require returning 9+ values for only CC~3 reduction is reasonable design feedback, but it's about a hypothetical change. Downgraded to Info.

#### Finding: DS-009
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** In save_game_service.py, the `load_game` method has inner exception handlers at lines 135-148 (metadata loading: 4 except clauses), lines 172-185 (turn loading: 4 except clauses), and lines 197-205 (reconstruction: 3 except clauses), totaling ~11 except clauses plus outer handlers. Each contributes to CC. The observation that consolidating handlers would reduce CC is accurate.

#### Finding: DS-010
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** This is the same issue as CX-005 from a design perspective. The outer try/except at lines 213-221 catches PermissionError, OSError, and 7 other types that are all already handled by inner blocks. Under normal execution flow, the outer handlers are dead code. Confirmed as redundant.

#### Finding: DS-011
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Lines 162-163 (`if turn_number is None: turn_number = metadata.get(...)`) resolve which turn to load based on metadata. This sits logically between loading metadata (which contains the latest turn number) and loading the turn file (which needs the turn number). This is a natural sequential flow, not an awkward coupling. The turn number resolution depends on metadata and feeds into turn loading -- it must sit between them.
