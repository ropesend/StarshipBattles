# Test Review Report: Research Domain

## Scope
- Source files reviewed:
  - `game/research/data/tech_node.py` (158 lines)
  - `game/research/data/research_tracker.py` (262 lines)
  - `game/research/data/tech_tree.py` (265 lines)
  - `game/research/systems/research_service.py` (232 lines)
  - `game/research/__init__.py` (8 lines)
  - `game/research/data/__init__.py` (6 lines)
  - `game/research/systems/__init__.py` (4 lines)
  - Total: 935 source LOC
- UI source files referenced by tests (in `game/ui/research/`):
  - `research_controls.py` (473 lines)
  - `research_renderer.py` (322 lines)
  - `research_scene.py` (399 lines)
  - Total: 1202 UI LOC
- Test files reviewed:
  - `tests/unit/research/conftest.py` (55 lines)
  - `tests/unit/research/test_tech_node.py` (672 lines)
  - `tests/unit/research/test_research_tracker.py` (595 lines)
  - `tests/unit/research/test_research_service.py` (644 lines)
  - `tests/unit/research/test_research_tracker_edge_cases.py` (149 lines)
  - `tests/unit/research/test_research_service_edge_cases.py` (253 lines)
  - `tests/unit/research/test_tech_requirement_negation.py` (290 lines)
  - `tests/unit/research/test_research_renderer.py` (259 lines)
  - `tests/unit/research/test_research_scene_di.py` (97 lines)
  - `tests/unit/research/tech_tree/test_cycle_detection.py` (342 lines)
  - `tests/unit/research/tech_tree/test_loading.py` (346 lines)
  - `tests/unit/research/tech_tree/test_queries.py` (240 lines)
  - `tests/unit/research/tech_tree/test_validation.py` (258 lines)
  - `tests/unit/research/research_controls/conftest.py` (88 lines)
  - `tests/unit/research/research_controls/test_reset_state.py` (269 lines)
  - `tests/unit/research/research_scene/conftest.py` (36 lines)
  - `tests/unit/research/research_scene/test_callbacks.py` (323 lines)
  - `tests/unit/research/research_scene/test_initialization.py` (263 lines)
  - `tests/unit/research/research_scene/test_interaction.py` (330 lines)
  - `tests/integration/research_workflow/conftest.py` (69 lines)
  - `tests/integration/research_workflow/test_persistence.py` (240 lines)
  - `tests/integration/research_workflow/test_workflow.py` (257 lines)
  - Total: 6075 test LOC
- Coverage data referenced: Yes
  - `game/research/` core: 100% across all 7 files (351 statements covered)
  - `game/ui/research/research_controls.py`: 19% (40/206 stmts)
  - `game/ui/research/research_renderer.py`: 25% (36/143 stmts)
  - `game/ui/research/research_scene.py`: 72% (119/165 stmts)

## Summary
- Test files reviewed: 22 (including conftest files)
- Source files reviewed: 7 core + 3 UI = 10
- Tests flagged for removal: 4 (estimated LOC: 185)
- Tests flagged as happy-path-only: 4
- Source files with inadequate coverage: 2

## A. Tests Recommended for Removal

### A1. Duplicate serialization tests across files
- **File:** `tests/unit/research/test_research_tracker_edge_cases.py`
- **Test(s):** `TestNodeStateSerialization` (all 5 methods), `TestResearchTrackerSerialization` (all 7 methods)
- **Reason:** DUPLICATE_OF:`tests/unit/research/test_research_tracker.py`
- **Confidence:** HIGH
- **Evidence:** `TestNodeStateSerialization.test_node_state_roundtrip` (line 16) duplicates `TestNodeState.test_to_dict_serialization` + `test_from_dict_deserialization` in `test_research_tracker.py` lines 32-55. `test_node_state_from_dict_defaults` (line 32) duplicates `test_from_dict_with_missing_keys` (line 57). `test_node_state_from_dict_partial_data` (line 39) duplicates `test_from_dict_with_partial_data` (line 64). `TestResearchTrackerSerialization` similarly duplicates `TestResearchTrackerSerialization` and `TestResearchTrackerEdgeCases` in the main file. The "edge case" file adds `test_node_state_zero_rp` and `test_node_state_max_chance` which test trivial round-trips already covered by the general round-trip test.
- **Estimated LOC saved:** 149

### A2. Redundant cycle detection call test
- **File:** `tests/unit/research/research_scene/test_interaction.py`
- **Test(s):** `TestCycleDetectionCall.test_detect_cycles_called_during_init`, `TestCycleDetectionCall.test_detect_cycles_errors_logged`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** `test_detect_cycles_called_during_init` (lines 281-308) creates a `MagicMock(spec=ResearchTreeScene)` and manually calls `mock_tree.detect_cycles()` then asserts that it was called. This tests the test itself, not any production code -- it never instantiates or exercises `ResearchTreeScene.__init__`. Similarly `test_detect_cycles_errors_logged` (lines 310-330) manually calls `mock_logger.info()` and then asserts `mock_logger.info.call_count == 2` -- verifying that the test's own logger calls happened, not that the production code logs.
- **Estimated LOC saved:** 36

## B. Tests That Are Happy-Path-Only

### B1. ResearchService.process_turn - No test for negative RP allocation during turn
- **File:** `tests/unit/research/test_research_service.py`
- **Test(s):** `TestProcessTurnInvestment` (all methods)
- **What's tested:** Investment increases chance, progress events generated, effective price reduces RP
- **What's missing:**
  - No test for what happens when `state.rp_allocation` is somehow negative (e.g., corrupted state). The production code checks `state.rp_allocation <= 0` at line 103 of `research_service.py` which silently skips, but this branch is only tested indirectly via "no allocations" (zero, not negative)
  - No test for `effective_price` returning 0 or very close to 0 (division producing infinity in `effective_rp`)
  - No test for the interaction between price curves and `process_turn` (all `process_turn` tests use flat price)
- **Source method(s) affected:** `game/research/systems/research_service.py:117-122` (effective_rp calculation)
- **Priority:** LOW (production code handles gracefully via math.log(1+x) which is always finite for finite x)

### B2. TechTree.calculate_depth - No test for infinite recursion protection
- **File:** `tests/unit/research/tech_tree/test_queries.py`
- **Test(s):** `TestTechTreeDepthCalculation`
- **What's tested:** Root depth=0, chain depth, multiple prereqs, OR groups, nonexistent nodes, dangling references, caching
- **What's missing:**
  - No test for cyclic dependency input to `calculate_depth()`. The method uses `_depth_cache` to avoid recomputation but has no explicit cycle guard. If a cycle exists (A requires B, B requires A, both in tree), `calculate_depth` would recurse infinitely (Python RecursionError). The `detect_cycles()` method exists but is separate -- nothing prevents calling `calculate_depth` on an invalid tree.
  - No test validates that `_depth_cache` is cleared when nodes are added/removed
- **Source method(s) affected:** `game/research/data/tech_tree.py:112-147` (calculate_depth recursive DFS)
- **Priority:** MEDIUM (circular dependency in real data would cause a stack overflow crash)

### B3. TechTree.load_from_json - No test for malformed requirement data
- **File:** `tests/unit/research/tech_tree/test_loading.py`
- **Test(s):** `TestTechTreeLoadFromJson`
- **What's tested:** Empty tree, single node, all fields, requirements with level_range, single level, default level, comment skipping, missing required fields, complex requirements, missing file, default values
- **What's missing:**
  - No test for requirement entry missing `node_id` key (the parser would raise `KeyError` at line 70 of `tech_tree.py`: `req["node_id"]`)
  - No test for `level_range` with invalid values (e.g., strings, negative numbers, min > max)
  - No test for `tech_tree` key missing entirely from JSON (only empty list tested)
  - No test for non-list `level_range` (e.g., integer instead of array)
- **Source method(s) affected:** `game/research/data/tech_tree.py:63-71` (requirement parsing)
- **Priority:** MEDIUM (malformed data file would crash with unhelpful KeyError)

### B4. ResearchTracker.set_allocation - concurrent multi-node allocation race
- **File:** `tests/unit/research/test_research_tracker.py`
- **Test(s):** `TestResearchTrackerRPAllocation`
- **What's tested:** Single allocation, exceeds budget, negative, updates remaining, replace existing, clear
- **What's missing:**
  - No test for rapidly alternating allocations that stress the budget tracking (e.g., allocate full budget to A, then full budget to B without clearing A -- this does work because `set_allocation` recomputes remaining including old_allocation, but there's no test proving this correctness)
  - No test for setting allocation on a node after `set_rp_budget` lowers the budget below current total (does existing allocation get retroactively reduced?)
- **Source method(s) affected:** `game/research/data/research_tracker.py:112-151` (set_allocation), `game/research/data/research_tracker.py:206-213` (set_rp_budget)
- **Priority:** MEDIUM (budget lowering does NOT retroactively reduce existing allocations, meaning `get_remaining_rp()` would return 0 but total allocated could exceed budget -- this is a potential bug)

## C. Source Code with Inadequate Coverage

### C1. research_controls.py
- **Source file:** `game/ui/research/research_controls.py` (473 LOC)
- **Coverage:** 19% (40/206 statements)
- **Untested areas:**
  - `__init__` constructor (builds all pygame_gui widgets) -- not tested at all, only mock-based reset tests exist
  - `select_node()` method -- sets the selected node and updates display
  - `clear_selection()` -- clears selection state
  - `update_budget_display()` -- updates budget label text
  - `update_turn_log()` -- formats and displays turn events
  - `_update_auto_spread_button()` -- toggles button text
  - `handle_event()` -- only 2 of ~10 event branches tested (slider move and no-selection guard)
  - `clear_log()` -- clears log display
- **Risk:** UI control panel is the primary user-facing interface for the research system. Untested event handling could silently break allocation adjustments, budget changes, and turn processing. The heavy mocking in `test_reset_state.py` means the real pygame_gui widget interactions are never exercised.
- **Priority:** LOW (UI layer, heavily dependent on pygame_gui, hard to unit test meaningfully)

### C2. research_renderer.py
- **Source file:** `game/ui/research/research_renderer.py` (322 LOC)
- **Coverage:** 25% (36/143 statements)
- **Untested areas:**
  - `draw()` method -- the main rendering function (draws nodes, connections, status indicators)
  - `_draw_node()` -- draws individual node rectangles with status colors
  - `_draw_connections()` -- draws dependency lines between nodes
  - `_draw_node_text()` -- renders text labels on nodes
  - Only `_get_font()` (quantization) and `_is_visible()` (viewport bounds) are tested
- **Risk:** Rendering bugs would be invisible to users (wrong colors, missing connections, misaligned text). However, rendering code is inherently hard to test and typically caught by manual testing.
- **Priority:** LOW (rendering layer, visual correctness is better tested manually)

## D. Cross-Domain Observations

### D1. UI test isolation fragility
The `tests/unit/research/research_scene/conftest.py` and `tests/unit/research/research_controls/conftest.py` both contain complex autouse fixtures to handle pygame_gui module corruption under xdist parallel execution. The `ensure_fresh_research_scene_import` fixture (research_scene conftest) checks if `pygame_gui` is a `MagicMock` and reloads. The research_controls conftest patches `sys.modules` and then cleans up stale references. This is a cross-domain concern: **any test file that imports `game.ui.research` can corrupt pygame_gui state for other tests running in parallel**. This is not a research-specific problem but a broader test infrastructure issue.

### D2. Integration test overlap with unit tests
The integration tests in `tests/integration/research_workflow/` substantially overlap with unit tests:
- `TestResearchPersistence` (6 tests) largely duplicates `TestResearchTrackerSerialization` from `test_research_tracker.py` and `test_research_tracker_edge_cases.py`
- `TestEffectivePriceCalculation` (4 tests) duplicates price curve tests from `test_tech_node.py`
- `TestBudgetManagement` (3 tests) duplicates budget tests from `test_research_tracker.py`
- However, some integration tests (like `test_complete_tech_path`, `test_breakthrough_unlocks_dependent_node`, `test_multiple_turns_lead_to_breakthrough`) provide genuine end-to-end value by exercising multiple components together

### D3. Potential bug: Budget reduction does not clamp existing allocations
In `ResearchTracker.set_rp_budget()` (line 213), the budget is clamped to `[MIN, MAX]` but existing allocations are not retroactively reduced. If a user allocates 200 RP (full budget), then reduces budget to 100, the `get_remaining_rp()` would return `max(0, 100 - 200) = 0` (correct), but `get_total_allocated()` would return 200 (exceeding the budget). This inconsistency is not tested and could cause confusing UI behavior. This affects `game/research/data/research_tracker.py:206-213`.

### D4. Test-to-source ratio
The research domain has 6075 test LOC covering 935 source LOC (core) -- a 6.5:1 ratio. Including UI source (2137 total), the ratio is 2.8:1. The core logic tests are thorough with good edge case coverage. The parametrized price curve tests in `test_tech_node.py` alone account for 180+ lines testing a 20-line function -- reasonable for ensuring correctness but borderline over-tested. The real gaps are in the UI layer, not the core domain.
