# AI & Behaviors Coverage Report

## 1. Coverage Summary
The AI system is split into three main components: `AIController` (state management), `AIBehavior` (maneuver logic), and `StrategyManager/TargetEvaluator` (data-driven decisions).

*   **Current Status**: 
    *   **Core AI Controller**: ~70% Covered. Basic targeting and update loops are tested. Formation management and secondary targeting are NOT tested.
    *   **Behaviors**: ~60% Covered. `KiteBehavior` and `FormationBehavior` are well tested. `RamBehavior` and `AttackRunBehavior` have basic tests. `Flee`, `Orbit`, `Erratic`, `RotateOnly`, `DoNothing` and `StraightLine` are largely untested or rely on implicit coverage.
    *   **Targeting Logic**: ~40% Covered. `TargetEvaluator` has tests for `nearest` and `has_weapons`, but missing tests for 10+ other rule types (e.g., `pdc_arc`, `weakest`, `least_armor`).

## 2. Missing Tests

### A. Targeting Rules (`TargetEvaluator` in `ai.py`)
The following targeting rules allow for complex behavior but are currently unverified:
*   `farthest`
*   `mass` / `largest` / `smallest`
*   `fastest` / `slowest`
*   `most_damaged` / `least_damaged`
*   `least_armor`
*   `pdc_arc` / `missiles_in_pdc_arc` (Critical for Point Defense logic)

### B. AI Controller Logic (`ai.py`)
*   **Secondary Targeting**: `find_secondary_targets()` (Multiplex tracking) is completely untested.
*   **PDC Arc Calculation**: `_stat_is_in_pdc_arc` is a complex geometric check that needs isolated unit tests.
*   **Formation Integrity**: `_check_formation_integrity` logic (checking for component damage) is untested.
*   **Satellite Exception**: Special logic for satellites in `update()` is untested.

### C. Behaviors (`ai_behaviors.py`)
*   **OrbitBehavior**: Completely untested. Complex vector math for maintaining orbit needs verification.
*   **ErraticBehavior**: Random timer logic needs testing (mock random).
*   **FleeBehavior**: Only implicitly tested via strategy dispatch. Needs explicit behavioral test (vector calculation).
*   **Simple Behaviors**: `DoNothing`, `StraightLine`, `RotateOnly` need basic verification to ensure they don't crash or trigger unintended side effects (like firing when they shouldn't).

## 3. Test Plan

To achieve 100% coverage, we will implement the following test suites:

### Suite 1: Extended Target Evaluator (`test_targeting_rules.py`)
Create a dedicated test file to exhaustively test every rule type in `TargetEvaluator`.
*   [ ] Test `fastest`/`slowest` with mocked velocities.
*   [ ] Test `largest`/`smallest` with mocked mass.
*   [ ] Test `most_damaged`/`least_damaged` with mocked HP pools.
*   [ ] Test `pdc_arc` by mocking geometry and weapon angles.

### Suite 2: Advanced Behaviors (`test_advanced_behaviors.py`)
*   [ ] **OrbitBehavior**: Verify ship maintains distance + tolerance. Test inward/outward correction vectors.
*   [ ] **FleeBehavior**: Verify vector calculation points away from target.
*   [ ] **ErraticBehavior**: Mock `random` to verify state changes and intervals.
*   [ ] **Simple Behaviors**: Verify `DoNothing` sets trigger=False. Verify `RotateOnly` issues rotation but no thrust.

### Suite 3: Controller Edge Cases (`test_ai_controller_extended.py`)
*   [ ] **Multiplex Tracking**: Test `find_secondary_targets` with `max_targets > 1`.
*   [ ] **Formation integrity**: Mock damaged thrusters and verify `in_formation` becomes False.
*   [ ] **Satellite Logic**: Verify satellites do not execute behavior logic.
