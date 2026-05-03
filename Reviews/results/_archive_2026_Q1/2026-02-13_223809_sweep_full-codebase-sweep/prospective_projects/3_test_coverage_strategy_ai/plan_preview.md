# PROJ-XXX: Test Coverage - Strategy and AI Systems

## Project Goal
Add comprehensive test coverage to core gameplay systems in the Strategy layer and AI/Foundation, focusing on critical paths that affect game balance and player experience.

## Current State
- commands.py: 19 command dataclasses with 0% coverage
- TargetEvaluator: 14 rule types, only subset tested
- FleetNavigationService: Complex methods with thin edge case coverage
- ShipStatsCalculator: Formula evaluation undertested

## Target State
- All command dataclasses have construction tests
- Physics calculations verified with edge cases
- All 14 targeting rule types tested
- Navigation edge cases (zero speed, max iterations) covered
- Formula error handling verified

---

## Phase 1: Critical Module Tests
**Status:** Not Started

### Tasks
- [ ] 1.1 Create `tests/unit/strategy/engine/test_commands.py`
- [ ] 1.2 Test each command's `__init__` sets type correctly
- [ ] 1.3 Test required vs optional parameters
- [ ] 1.4 Test edge cases (None targets in colonize commands)
- [ ] 1.9 Add AIController edge case tests for invalid strategy refs
- [ ] 1.10 Run test suite

### Files Created
- `tests/unit/strategy/engine/test_commands.py`

---

## Phase 2: AI and Targeting
**Status:** Not Started

### Tasks
- [ ] 2.1 Enhance `tests/unit/ai/test_target_evaluator_edge_cases.py`
- [ ] 2.2 Add parametrized tests for all 14 rule types
- [ ] 2.3 Test negative factor values
- [ ] 2.4 Test rule with weight=0 and factor=0
- [ ] 2.5 Create `tests/unit/ai/test_ai_factory.py`
- [ ] 2.6 Test factory registration/lookup
- [ ] 2.7 Test default AI type fallback
- [ ] 2.8 Test invalid AI type handling
- [ ] 2.9 Enhance `tests/unit/ai/test_controllable_adapter.py`
- [ ] 2.10 Test ships with missing optional attributes
- [ ] 2.11 Run test suite

### Files Affected
- `tests/unit/ai/test_target_evaluator_edge_cases.py`
- `tests/unit/ai/test_ai_factory.py` (new)
- `tests/unit/ai/test_controllable_adapter.py`

---

## Phase 3: Strategy Services
**Status:** Not Started

### Tasks
- [ ] 3.1 Add FleetNavigationService edge case tests
- [ ] 3.2 Test `project_path()` with zero/negative speed
- [ ] 3.3 Test max_iterations safety limit triggering
- [ ] 3.4 Test `compute_next_step()` with non-movement orders
- [ ] 3.5 Add ShipStatsCalculator edge case tests
- [ ] 3.6 Test malformed formula strings return default
- [ ] 3.7 Test indexed component ID lookups
- [ ] 3.8 Test zero mass ships for warp capability
- [ ] 3.9 Add superweapon handler validation failure tests
- [ ] 3.10 Test each handler returns specific error message
- [ ] 3.11 Run test suite

### Files Affected
- `tests/unit/strategy/fleet_navigation/` files
- `tests/unit/strategy/ship_stats/` files
- `tests/unit/strategy/engine/test_superweapon_command_handlers.py`

---

## Phase 4: Minor Coverage Gaps
**Status:** Not Started

### Tasks
- [ ] 4.1 Create `tests/unit/strategy/facade/test_empire_dto.py`
- [ ] 4.2 Create `tests/unit/strategy/facade/test_planet_dto.py`
- [ ] 4.3 Create `tests/unit/strategy/facade/test_system_dto.py`
- [ ] 4.4 Add TransferValidator species_id edge cases
- [ ] 4.5 Add ColonizeValidator pod/planet type matching tests
- [ ] 4.6 Add PlacementStrategies determinism tests with fixed seeds
- [ ] 4.7 Add FleetResourceAggregator empty/damaged fleet tests
- [ ] 4.8 Review game/core/resources.py and add tests if needed
- [ ] 4.9 Run full test suite
- [ ] 4.10 Final coverage report

### Files Created
- `tests/unit/strategy/facade/test_empire_dto.py`
- `tests/unit/strategy/facade/test_planet_dto.py`
- `tests/unit/strategy/facade/test_system_dto.py`

---

## Success Metrics
- [ ] commands.py 100% covered
- [ ] All 14 targeting rules tested
- [ ] Navigation edge cases covered
- [ ] Formula error handling verified
- [ ] All tests passing
