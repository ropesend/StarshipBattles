# Agent 5: AI, Research, Combat Test Suite Cleanup Findings

**Directories analyzed:**
- `tests/unit/ai/` (24 files, ~9K lines)
- `tests/unit/research/` (19 files, ~6K lines)
- `tests/unit/combat/` (20 files, ~3K lines)

**Analysis date:** 2026-02-16

---

## HIGH Confidence Findings

### H-1: Trivially Obvious Interface Checks - `test_interface_definition.py`
- **File:** `tests/unit/ai/controllable_interface/test_interface_definition.py` (~259 lines)
- **Pattern:** Trivially obvious tests
- **Evidence:** Every single test in this file is a `hasattr` check on the `IControllable` abstract class. Example:
  ```python
  def test_has_get_position(self):
      assert hasattr(IControllable, 'get_position')
  ```
  There are ~30 such tests. These are classic "import checks" that verify the ABC definition has certain method names. The ABC's `__abstractmethods__` enforcement already guarantees this at instantiation time, and `test_controllable_adapter_edge_cases.py` has a `test_all_abstract_methods_implemented` test that verifies the full set in one test.
- **Recommendation:** DELETE entire file. The interface definition is already validated by Python's ABC mechanism and by the adapter completeness test.
- **Lines saved:** ~259
- **Risk:** None - ABC mechanism and adapter tests provide the same coverage.

### H-2: Scaffold/Placeholder Tests - `test_combat_endurance_edge_cases.py`
- **File:** `tests/unit/combat/test_combat_endurance_edge_cases.py` (~27 lines)
- **Pattern:** Scaffold/repro tests
- **Evidence:** Two tests, one is a `hasattr` import check, the other is an empty `pass`:
  ```python
  def test_full_resources_baseline(self):
      from game.simulation.entities import ship
      assert hasattr(ship, 'Ship')

  def test_resource_levels_affect_combat(self):
      pass
  ```
  These are clearly scaffolds that were never filled in.
- **Recommendation:** DELETE entire file.
- **Lines saved:** ~27
- **Risk:** None - these tests verify nothing.

### H-3: Scaffold/Placeholder Tests - `test_targeting_edge_cases.py`
- **File:** `tests/unit/combat/test_targeting_edge_cases.py` (~23 lines)
- **Pattern:** Scaffold/repro tests, trivially obvious
- **Evidence:** Two tests that are pure import/hasattr checks:
  ```python
  def test_targeting_system_exists(self):
      from game.simulation.combat import targeting_system
      assert hasattr(targeting_system, 'TargetingSystem')

  def test_damage_calculator_exists(self):
      from game.simulation.combat import damage_calculator
      assert damage_calculator is not None
  ```
- **Recommendation:** DELETE entire file.
- **Lines saved:** ~23
- **Risk:** None - import validity is tested by any test that actually uses these modules.

### H-4: Major Duplicate - Three Behavior Test Files
- **Files:**
  - `tests/unit/ai/test_advanced_behaviors.py` (~178 lines)
  - `tests/unit/ai/test_ai_behaviors.py` (~340 lines)
  - `tests/unit/ai/test_behavior_units.py` (~736 lines)
  - `tests/unit/ai/formation_prediction/test_other_behaviors.py` (~164 lines)
- **Pattern:** Duplicate tests
- **Evidence:** All four files test the same set of AI behavior classes (KiteBehavior, RamBehavior, FleeBehavior, AttackRunBehavior, OrbitBehavior, FormationBehavior, DoNothing, StationaryFire, StraightLine, RotateOnly, Erratic). `test_behavior_units.py` is the most comprehensive, covering ALL behaviors systematically. The other three files contain significant subsets:
  - `test_advanced_behaviors.py` tests KiteBehavior, AttackRunBehavior, OrbitBehavior - all present in `test_behavior_units.py`
  - `test_ai_behaviors.py` tests KiteBehavior, FormationBehavior, RamBehavior - all present in `test_behavior_units.py`
  - `test_other_behaviors.py` tests Flee, Ram, AttackRun, Orbit, DoNothing, StationaryFire, StraightLine, RotateOnly - all present in `test_behavior_units.py`
- **Recommendation:** CONSOLIDATE. Keep `test_behavior_units.py` and merge any unique test scenarios from the other three files into it, then delete the three redundant files.
- **Lines saved:** ~682 (after merging unique tests)
- **Risk:** Low - need to verify no unique test scenarios are lost during merge.

### H-5: Major Duplicate - Two Capabilities Cache Test Files
- **Files:**
  - `tests/unit/ai/test_ai_capabilities_cache.py` (~225 lines)
  - `tests/unit/ai/target_evaluator/test_capabilities_cache.py` (~232 lines)
- **Pattern:** Duplicate tests
- **Evidence:** Both files test `_build_capabilities_cache` and its integration with `_score_and_sort_enemies`. The test patterns are highly similar: creating mocked ships with/without weapons, testing cache population, testing capabilities dict structure.
- **Recommendation:** CONSOLIDATE into one file. Keep the more thorough one.
- **Lines saved:** ~225
- **Risk:** Low.

### H-6: Major Duplicate - Two Target Evaluator Rules Files
- **Files:**
  - `tests/unit/ai/test_target_evaluator_rules.py` (~753 lines)
  - `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (~599 lines)
- **Pattern:** Duplicate tests
- **Evidence:** Both files test the same TargetEvaluator rule types using parametrized tests. `test_target_evaluator_rules.py` covers all 14 rule types with extensive parametrization; `test_evaluation_rules.py` covers the same rules with slightly different fixture patterns. The specific rules tested overlap completely: nearest, lowest_hp, highest_hp, highest_threat, most_valuable, weakest_shields, largest, smallest, fastest, slowest, missiles_in_pdc_arc, random, lowest_hp_percent, highest_hp_percent.
- **Recommendation:** CONSOLIDATE. Keep `test_target_evaluator_rules.py` (more comprehensive). Delete `target_evaluator/test_evaluation_rules.py`.
- **Lines saved:** ~599
- **Risk:** Low.

### H-7: Significant Duplicate - Two Evaluation Integration/Edge Case Files
- **Files:**
  - `tests/unit/ai/test_target_evaluator_edge_cases.py` (~315 lines)
  - `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (~286 lines)
- **Pattern:** Duplicate tests
- **Evidence:** Both files test TargetEvaluator edge cases: zero weight rules, required flag filtering, empty rules, distance cache, capabilities cache, missile rules, multiple rules. `test_evaluation_integration.py` has some integration-level tests mixing multiple features, but the core test scenarios heavily overlap with the edge cases file.
- **Recommendation:** CONSOLIDATE. Merge unique integration scenarios into edge cases file.
- **Lines saved:** ~250 (after merge)
- **Risk:** Low.

---

## MEDIUM Confidence Findings

### M-1: Significant Overlap - Three Controllable Adapter Test Files
- **Files:**
  - `tests/unit/ai/controllable_interface/test_adapter_basics.py` (~233 lines)
  - `tests/unit/ai/controllable_interface/test_adapter_methods.py` (~263 lines)
  - `tests/unit/ai/test_controllable_adapter_edge_cases.py` (~476 lines)
  - `tests/unit/ai/test_controllable_adapter.py` (~247 lines)
- **Pattern:** Duplicate tests
- **Evidence:** `test_adapter_basics.py` tests position, movement, combat methods; `test_adapter_methods.py` tests advanced/formation methods; `test_controllable_adapter.py` tests IControllable contract and mock implementation; `test_controllable_adapter_edge_cases.py` covers missing attributes, all getter/setter methods, formation methods, interface completeness, and identity/state. The edge cases file alone has a `test_all_abstract_methods_implemented` and `test_interface_methods_dont_raise_on_normal_ship` that subsume much of the basic/methods tests.
- **Recommendation:** CONSOLIDATE into two files: `test_controllable_adapter.py` (core contract) and `test_controllable_adapter_edge_cases.py` (comprehensive coverage). Delete `controllable_interface/test_adapter_basics.py` and `controllable_interface/test_adapter_methods.py`.
- **Lines saved:** ~496
- **Risk:** Medium - need to verify unique test patterns from basics/methods are covered in the edge cases file.

### M-2: Over-Mocked UI Logic Tests - `research_controls/test_handle_event.py`
- **File:** `tests/unit/research/research_controls/test_handle_event.py` (~274 lines)
- **Pattern:** Over-mocked tests
- **Evidence:** Many tests don't test actual production code. Instead they recreate the logic inline and test their own reimplementation. For example:
  ```python
  def test_toggle_flips_enabled_state_from_false(self, mock_tracker):
      mock_tracker.auto_spread_enabled = False
      mock_tracker.auto_spread_enabled = not mock_tracker.auto_spread_enabled
      assert mock_tracker.auto_spread_enabled is True
  ```
  This just tests Python's `not` operator on a mock attribute. Similarly, the button callback tests just call `callback()` and assert it was called. The slider range tests just do basic arithmetic on mock return values. None of these exercise any production code paths.
- **Recommendation:** DELETE entire file. The actual event handling logic is tested in `test_reset_state.py` (which uses `ResearchControlPanel.handle_event`) and through integration tests.
- **Lines saved:** ~274
- **Risk:** Medium - verify that actual handle_event() paths are covered elsewhere (they are in `test_reset_state.py`'s `TestStateReferenceConsistency` class).

### M-3: Over-Mocked UI Logic Tests - `research_controls/test_event_formatting.py`
- **File:** `tests/unit/research/research_controls/test_event_formatting.py` (~182 lines)
- **Pattern:** Over-mocked tests
- **Evidence:** Tests recreate event formatting logic inline rather than calling any production formatting function:
  ```python
  def test_format_breakthrough_event(self):
      events = [{'node_id': 'test', 'event': 'breakthrough', ...}]
      lines = []
      for evt in events:
          # ... manual inline formatting ...
          lines.append(f"<font color='#80FF80'>BREAKTHROUGH!</font> ...")
      log_text = "<br>".join(lines)
      assert "BREAKTHROUGH!" in log_text
  ```
  This tests the test's own string formatting, not any production code. The `TestAutoSpreadLogic` and `TestBudgetDisplay` classes similarly test mock attribute manipulation.
- **Recommendation:** DELETE entire file or rewrite to test actual formatting functions from production code.
- **Lines saved:** ~182
- **Risk:** Medium - check if these inline patterns match actual production formatting logic. If they don't, these tests are actively misleading.

### M-4: Over-Mocked UI Logic Tests - `research_controls/test_node_selection.py`
- **File:** `tests/unit/research/research_controls/test_node_selection.py` (~113 lines)
- **Pattern:** Over-mocked tests
- **Evidence:** Tests basic arithmetic on mock return values and string formatting:
  ```python
  def test_slider_range_calculation(self, mock_tracker, mock_node):
      mock_tracker.get_state.return_value.rp_allocation = 50
      mock_tracker.get_remaining_rp.return_value = 150
      current_allocation = mock_tracker.get_state(mock_node.id).rp_allocation
      remaining = mock_tracker.get_remaining_rp()
      max_allocation = current_allocation + remaining
      assert max_allocation == 200
  ```
  This tests `50 + 150 == 200`, not any production code. The `TestClearSelection` tests verify hardcoded dict values against themselves.
- **Recommendation:** DELETE entire file.
- **Lines saved:** ~113
- **Risk:** Medium.

### M-5: Partial Overlap - Research Tracker Edge Cases
- **Files:**
  - `tests/unit/research/test_research_tracker.py` (~596 lines) - has `TestTrackerSerialization` class
  - `tests/unit/research/test_research_tracker_edge_cases.py` (~150 lines) - has `TestNodeStateSerialization`, `TestTrackerSerializationEdgeCases`
- **Pattern:** Duplicate tests
- **Evidence:** `test_research_tracker.py` already has serialization tests in its `TestTrackerSerialization` class. The edge cases file adds a few extra scenarios (empty allocations, zero values, NodeState fields), but some overlap exists. The edge cases file is small enough that its unique tests could be merged.
- **Recommendation:** MERGE unique edge case tests from `test_research_tracker_edge_cases.py` into `test_research_tracker.py`, then delete the edge cases file.
- **Lines saved:** ~100 (after merging unique tests)
- **Risk:** Medium.

### M-6: Overlap - TechTree Validation Tests
- **Files:**
  - `tests/unit/research/tech_tree/test_validation.py` (~455 lines)
  - `tests/unit/research/tech_tree/test_cycle_detection.py` (~343 lines)
  - `tests/unit/research/tech_tree/test_queries.py` (~241 lines)
- **Pattern:** Duplicate tests
- **Evidence:** `test_validation.py` contains `TestDetectCycles` and `TestDepthCalculation` classes that overlap significantly with `test_cycle_detection.py` and `test_queries.py`:
  - `test_validation.py::TestDetectCycles` tests simple cycle, complex cycle, self-reference, negated requirements, diamond dependency - all also in `test_cycle_detection.py`
  - `test_validation.py::TestDepthCalculation` tests missing node and caching - also in `test_queries.py`
  - `test_validation.py::TestValidateRequirements` overlaps with tests in `test_queries.py::TestTechTreeValidation`
- **Recommendation:** Remove duplicate test classes from `test_validation.py`. Keep the specialized files (`test_cycle_detection.py`, `test_queries.py`) and trim `test_validation.py` to only test the combined `validate()` method.
- **Lines saved:** ~200
- **Risk:** Medium - the specialized files are more thorough; `test_validation.py` adds some unique format-checking tests.

### M-7: Layout Constants Tests Are Trivially Obvious
- **File:** `tests/unit/research/research_scene/test_initialization.py` (lines 264-287)
- **Pattern:** Trivially obvious tests
- **Evidence:** `TestLayoutConstants` class tests that class constants are positive:
  ```python
  def test_sidebar_width_is_positive(self):
      assert ResearchTreeScene.SIDEBAR_WIDTH > 0
  def test_column_spacing_is_positive(self):
      assert ResearchTreeScene.COLUMN_SPACING > 0
  ```
  These are trivially obvious - named constants set to literal positive values in source code will always be positive.
- **Recommendation:** DELETE the `TestLayoutConstants` class (4 tests, ~24 lines).
- **Lines saved:** ~24
- **Risk:** Low.

---

## LOW Confidence Findings

### L-1: Potential Overlap - AI Controller Test Files
- **Files:**
  - `tests/unit/ai/test_ai_controller_unit.py` (~1149 lines)
  - `tests/unit/ai/test_ai_controller_edge_cases.py` (~404 lines)
  - `tests/unit/ai/test_ai_controller_interface.py` (~467 lines)
  - `tests/unit/ai/test_ai.py` (~316 lines)
- **Pattern:** Possible duplicate coverage
- **Evidence:** All four files test AIController from different angles. `test_ai_controller_unit.py` is comprehensive (engage distance, behavior selection, satellite, dead ship, find target, formations, avoidance, navigation). Some of these overlap with the edge cases and interface files, but each file has a distinct focus (unit.py = comprehensive mocked, edge_cases.py = StrategyManager integration, interface.py = adapter integration, test_ai.py = real ship integration).
- **Recommendation:** REVIEW for specific overlapping test scenarios, but these four files likely serve complementary purposes. A careful audit could find 10-20% overlap.
- **Lines saved:** ~200 (estimated, after removing specific duplicates)
- **Risk:** High - need line-by-line comparison to avoid losing coverage.

### L-2: Overlap Between test_lead.py and test_weapons.py Lead Tests
- **Files:**
  - `tests/unit/combat/test_lead.py` (~143 lines) - standalone lead calculation with custom Vector
  - `tests/unit/combat/test_weapons.py` `TestLeadCalculation` class (~50 lines)
- **Pattern:** Duplicate tests
- **Evidence:** `test_lead.py` has its own `solve_lead` implementation and `MockVector` class that test the lead calculation algorithm independently. `test_weapons.py::TestLeadCalculation` tests `solve_lead` via the real `ShipCombatEngine`. The test_lead.py tests are more algorithm-focused (static target, perpendicular, moving away, toward, matched velocities). There is conceptual overlap but test_lead.py tests its own reimplementation rather than production code.
- **Recommendation:** Consider converting `test_lead.py` to use the actual `ShipCombatEngine.solve_lead` instead of its own reimplementation, then merge with `test_weapons.py::TestLeadCalculation`.
- **Lines saved:** ~100
- **Risk:** Medium - the standalone implementation may intentionally test the algorithm in isolation.

### L-3: CCD Test Uses Local Algorithm Instead of Production Code
- **File:** `tests/unit/combat/test_ccd.py` (~208 lines)
- **Pattern:** Over-mocked / not testing production code
- **Evidence:** `test_ccd.py` defines its own `Vector` class and `check_collision` function, then tests those. It does NOT import or test any production CCD code. It is testing a local reimplementation of the algorithm rather than the actual game code.
- **Recommendation:** Rewrite to test the actual production CCD implementation, or mark clearly as an algorithm reference test. If production CCD is tested elsewhere, this file could be removed.
- **Lines saved:** ~208 (if removed) or 0 (if rewritten)
- **Risk:** Medium - need to verify production CCD coverage exists elsewhere.

---

## Summary

| Confidence | Count | Estimated Lines Saved |
|-----------|-------|--------------------|
| HIGH      | 7     | ~2,065             |
| MEDIUM    | 7     | ~1,389             |
| LOW       | 3     | ~508               |
| **TOTAL** | **17**| **~3,962**         |

### Priority Actions (HIGH confidence, immediate wins):
1. **Delete** `test_interface_definition.py` - 259 lines of pure `hasattr` checks
2. **Delete** `test_combat_endurance_edge_cases.py` - 27 lines of empty scaffolds
3. **Delete** `test_targeting_edge_cases.py` - 23 lines of import checks
4. **Consolidate** 4 behavior test files into `test_behavior_units.py` - save ~682 lines
5. **Consolidate** 2 capabilities cache test files - save ~225 lines
6. **Consolidate** 2 target evaluator rules test files - save ~599 lines
7. **Consolidate** 2 evaluation integration/edge case test files - save ~250 lines

### Secondary Actions (MEDIUM confidence, good cleanup):
8. **Delete** 3 over-mocked `research_controls/` test files that test inline reimplementations instead of production code (~569 lines)
9. **Consolidate** adapter test files (save ~496 lines)
10. **Merge** research tracker edge cases into main tracker test file
11. **Trim** duplicate validation/cycle/query tests in tech_tree/
12. **Remove** trivially obvious layout constant tests
