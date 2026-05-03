# Test Coverage Gaps Report - Foundation Shard

**Sweep Date:** 2026-02-13
**Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
**Auditor:** Claude Opus 4.5 (claude-opus-4-5-20251101)

---

## Executive Summary

This report analyzes test coverage for the Foundation modules of Starship Battles. The analysis followed a 6-phase methodology covering untested modules, undertested public APIs, critical path coverage, test quality issues, integration test gaps, and missing test categories.

**Overall Assessment:** The Foundation shard has **good unit test coverage** for most modules, with comprehensive tests for AI behaviors, combat utilities, research systems, and core utilities. However, there are notable gaps in integration tests, UI component tests, and certain edge cases.

---

## Phase 1: Untested Modules

### game/core/

#### INFO: game/core/resources.py - No dedicated test file
**File:** `C:\Dev\Starship Battles\game\core\resources.py`

The `resources.py` module handles loading resource type definitions from JSON into the RegistryManager. While functions like `load_resources_data()` and `load_resources()` are defined, there is no dedicated `test_resources.py` file in `tests/unit/core/`.

Related tests exist in:
- `tests/unit/strategy/ship_stats/test_resources.py`
- `tests/unit/entities/test_resources.py`

These test resource-related functionality but not the core loading functions in `game/core/resources.py`.

**Recommendation:** Add unit tests for:
- `load_resources_data()` with missing files, invalid JSON, permission errors
- `_resolve_resource_path()` path resolution logic
- `_get_default_resources()` returns correct defaults

---

### game/ai/

#### INFO: game/ai/controller.py - Excellent coverage exists
**File:** `C:\Dev\Starship Battles\game\ai\controller.py`

The `AIController` class is thoroughly tested in `tests/unit/ai/test_ai_controller_unit.py` with 1149 lines of comprehensive tests covering:
- Behavior selection logic
- Engage distance multipliers
- Formation handling
- Target acquisition
- Navigation
- Avoidance

**Status:** Well-covered

---

### game/research/

#### MAJOR: game/research/data/tech_tree.py - Missing dedicated test file
**File:** `C:\Dev\Starship Battles\game\research\data\tech_tree.py`

The `TechTree` class contains significant functionality:
- `load_from_json()` - JSON loading with validation
- `resolve_all_requirements()` - Fuzzy requirement resolution
- `calculate_depth()` - Layout depth calculation
- `get_nodes_at_depth()`, `get_max_depth()` - Layout helpers
- `validate_requirements()` - Requirement validation
- `detect_cycles()` - Cycle detection in dependency graph
- `validate()` - Combined validation

No dedicated `test_tech_tree.py` exists. The `TechNode` class is tested in `test_tech_node.py`, but `TechTree` container logic is not covered.

**Recommendation:** Create `tests/unit/research/test_tech_tree.py` covering:
- JSON loading with valid/invalid/missing files
- Fuzzy requirement resolution determinism
- Depth calculation for various tree shapes
- Cycle detection with cyclic/acyclic graphs
- Validation error reporting

---

#### MAJOR: game/research/ui/research_controls.py - No dedicated tests
**File:** `C:\Dev\Starship Battles\game\research\ui\research_controls.py`

The `ResearchControlPanel` class (471 lines) contains significant UI logic:
- `_create_ui()` - Complex UI element creation
- `handle_event()` - Event routing for buttons and sliders
- `update_selected_node()` - Node detail display
- `update_turn_log()` - Event log formatting
- `_toggle_auto_spread()` - Auto-spread feature
- `reset()` - Panel reset

No tests exist for this module.

**Recommendation:** Create `tests/unit/research/ui/test_research_controls.py` with mocked pygame_gui testing:
- Button callbacks (next turn, reset, close)
- Slider value changes (budget, allocation)
- Event log formatting
- Auto-spread toggle behavior

---

#### MAJOR: game/research/ui/research_scene.py - No dedicated tests
**File:** `C:\Dev\Starship Battles\game\research\ui\research_scene.py`

The `ResearchTreeScene` class (381 lines) is a complex scene manager:
- Layout calculation for node positioning
- Camera management for pan/zoom
- Node click handling and selection
- Turn processing integration
- Session reset functionality

No tests exist for this module.

**Recommendation:** Test the non-UI logic:
- `_calculate_layout()` - Node position calculation
- `_get_node_at_position()` - Hit testing
- `_center_camera()` - Camera positioning
- Callback wiring verification

---

### game/engine/

#### INFO: game/engine/spatial.py - Good coverage in tests/unit/systems/
**File:** `C:\Dev\Starship Battles\game\engine\spatial.py`

Tests exist in:
- `tests/unit/systems/test_spatial.py`
- `tests/unit/systems/test_spatial_extended.py`
- `tests/unit/systems/test_spatial_edge_cases.py`

**Status:** Well-covered

---

#### INFO: game/engine/physics.py - Good coverage in tests/unit/systems/
**File:** `C:\Dev\Starship Battles\game\engine\physics.py`

Tests exist in:
- `tests/unit/systems/test_physics.py`
- `tests/unit/systems/test_physics_edge_cases.py`
- `tests/unit/simulation/test_physics_constants.py`
- `tests/unit/simulation/test_physics_formulas.py`

**Status:** Well-covered

---

#### INFO: game/engine/collision.py - Good coverage
**File:** `C:\Dev\Starship Battles\game\engine\collision.py`

Tests exist in:
- `tests/unit/engine/collision_edge_cases/test_ccd.py`
- `tests/unit/engine/collision_edge_cases/test_damage_tracking.py`
- `tests/unit/engine/collision_edge_cases/test_beam_ramming.py`

**Status:** Well-covered

---

## Phase 2: Undertested Public APIs

### game/core/profiling.py

#### INFO: Profiler.toggle() not explicitly tested
**File:** `C:\Dev\Starship Battles\game\core\profiling.py`

The `Profiler.toggle()` method that toggles profiling state and returns the new state is not explicitly tested in `test_profiling_edge_cases.py`.

```python
def toggle(self):
    """Toggle profiling state."""
    if self.active:
        self.stop()
    else:
        self.start()
    return self.active
```

**Recommendation:** Add test for toggle behavior and return value.

---

### game/ai/target_evaluator.py

#### INFO: TargetEvaluator._eval_speed_rule() - Partial coverage
**File:** `C:\Dev\Starship Battles\game\ai\target_evaluator.py`

The speed rules (`fastest`, `slowest`) are tested only indirectly through the main `evaluate()` function. Direct unit tests for `_eval_speed_rule()` are missing.

**Recommendation:** Add explicit tests for speed rule scoring with various velocity values.

---

### game/ai/target_evaluator.py

#### INFO: TargetEvaluator._eval_least_armor_rule() - Not directly tested
**File:** `C:\Dev\Starship Battles\game\ai\target_evaluator.py`

The `least_armor` rule that scores targets by armor HP is not directly tested.

```python
@staticmethod
def _eval_least_armor_rule(candidate, rule):
    """Evaluate least_armor rule."""
    armor_comps = candidate.get_components_by_layer(LayerType.ARMOR)
    armor_hp = sum(getattr(c, 'hp', 0) for c in armor_comps)
    val = -armor_hp * (weight if weight > 0 else -factor)
    return (val, True)
```

**Recommendation:** Add test for least_armor rule with mocked armor components.

---

### game/research/data/research_tracker.py

#### INFO: ResearchTracker.spread_rp_evenly() - Complex logic partially tested
**File:** `C:\Dev\Starship Battles\game\research\data\research_tracker.py`

The auto-spread functionality that distributes RP evenly across available nodes has complex logic but test coverage focuses mainly on happy paths.

**Recommendation:** Add edge case tests for:
- All nodes at max level
- Single available node
- Budget smaller than node count
- Nodes with different price multipliers

---

## Phase 3: Critical Path Coverage

### AI Decision Making

#### INFO: AI targeting critical path - Well covered
The critical path from `AIController.update()` -> `find_target()` -> `TargetEvaluator.evaluate()` is thoroughly tested with:
- 15+ test classes in `test_ai_controller_unit.py`
- 12+ test classes in `test_target_evaluator_edge_cases.py`
- Comprehensive behavior tests in `test_behavior_units.py`

**Status:** Good critical path coverage

---

### Research Breakthrough Mechanics

#### INFO: Research breakthrough critical path - Well covered
The critical path for research breakthroughs in `ResearchService.process_turn()` is tested in `test_research_service.py` with:
- Chance accumulation tests
- Decay mechanics tests
- Breakthrough event generation
- Boundary condition tests

**Status:** Good critical path coverage

---

## Phase 4: Test Quality Issues

### game/ai/test_ai_controller_unit.py

#### MINOR: Excessive mocking may hide real issues
**File:** `C:\Dev\Starship Battles\tests\unit\ai\test_ai_controller_unit.py`

Many tests use heavy mocking which could mask integration issues:
```python
with patch('game.ai.controller.StrategyManager') as mock_sm:
    with patch('game.ai.controller.TargetEvaluator.evaluate', return_value=50.0):
        with patch('game.ai.controller.is_combatant', return_value=True):
            with patch('game.ai.controller.get_hp_percent', return_value=0.5):
```

**Recommendation:** Add some integration-style tests using real collaborators where practical.

---

### game/research/test_research_renderer.py

#### INFO: Test isolation technique is good
**File:** `C:\Dev\Starship Battles\tests\unit\research\test_research_renderer.py`

The test file uses `importlib.util.spec_from_file_location` to bypass pygame_gui import issues under xdist. This is a good isolation technique but adds complexity.

**Status:** Acceptable workaround for pygame/xdist issues

---

## Phase 5: Integration Test Gaps

#### MAJOR: No integration tests for AI module
**Directory:** `tests/integration/ai/`

No integration test directory exists for the AI module. The AI system integrates with:
- Physics/spatial grid for target queries
- Strategy system for behavior configuration
- Ship component system for capability checks

**Recommendation:** Create integration tests for:
- AI controller with real spatial grid
- Target evaluation with real ship components
- Behavior execution with physics integration

---

#### MAJOR: No integration tests for Research module
**Directory:** `tests/integration/research/`

No integration test directory exists for the research module. The research system integrates with:
- JSON data loading
- UI rendering
- Session persistence

**Recommendation:** Create integration tests for:
- Full research session lifecycle
- JSON loading with real data files
- Multi-turn simulations

---

#### INFO: No integration tests for Engine module
**Directory:** `tests/integration/engine/`

No integration test directory exists for the engine module. However, physics/collision integration is likely tested through simulation tests.

**Status:** Lower priority - likely covered by simulation tests

---

## Phase 6: Missing Test Categories

### Performance/Stress Tests

#### MINOR: No performance tests for SpatialGrid
**File:** `C:\Dev\Starship Battles\game\engine\spatial.py`

The `SpatialGrid.query_radius()` method is performance-critical for combat. No stress tests verify performance with large entity counts.

**Recommendation:** Add performance tests with:
- 1000+ entities
- Various cell sizes
- Large query radii

---

### Regression Tests

#### MINOR: No regression test suite for combat formulas
The combat formula calculations in `game/simulation/formulas/` are critical for game balance. No dedicated regression suite exists to catch formula changes.

**Recommendation:** Create golden file tests that verify formula outputs against known-good values.

---

### Fuzz Testing

#### INFO: No fuzz tests for JSON parsing
JSON parsing in `game/core/json_utils.py` and data loaders could benefit from fuzz testing to catch edge cases in malformed input.

**Recommendation:** Consider adding fuzz tests for critical JSON loaders (lower priority).

---

## Summary by Severity

### CRITICAL (0)
None identified.

### MAJOR (4)
1. `game/research/data/tech_tree.py` - Missing dedicated test file
2. `game/research/ui/research_controls.py` - No dedicated tests
3. `game/research/ui/research_scene.py` - No dedicated tests
4. No integration tests for AI module

### MINOR (4)
1. `Profiler.toggle()` not explicitly tested
2. Excessive mocking in AI controller tests
3. No performance tests for SpatialGrid
4. No regression test suite for combat formulas

### INFO (10)
1. `game/core/resources.py` - No dedicated test file (related tests exist)
2. `game/ai/controller.py` - Excellent coverage exists
3. `game/engine/spatial.py` - Good coverage
4. `game/engine/physics.py` - Good coverage
5. `game/engine/collision.py` - Good coverage
6. `TargetEvaluator._eval_speed_rule()` - Partial coverage
7. `TargetEvaluator._eval_least_armor_rule()` - Not directly tested
8. `ResearchTracker.spread_rp_evenly()` - Complex logic partially tested
9. Research renderer test isolation technique is good
10. No integration tests for Engine module (likely covered elsewhere)

---

## Recommendations Priority Order

1. **High Priority:** Create `tests/unit/research/test_tech_tree.py` for TechTree class
2. **High Priority:** Create integration tests for AI module (`tests/integration/ai/`)
3. **Medium Priority:** Add UI tests for ResearchControlPanel with mocked pygame_gui
4. **Medium Priority:** Create integration tests for research session lifecycle
5. **Low Priority:** Add performance tests for SpatialGrid
6. **Low Priority:** Create regression test suite for combat formulas

---

*Report generated by Test Coverage Gaps Sweep Agent*
