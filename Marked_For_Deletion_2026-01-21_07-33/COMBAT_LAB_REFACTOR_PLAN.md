# Combat Lab Refactoring Plan

## Overview

This plan addresses the remaining refactoring tasks for the Combat Lab test framework, incorporating user feedback about test quality and documentation improvements.

## Current Status

### Completed Work
- ✅ Template migration complete (32 scenarios migrated)
  - 18 beam weapon scenarios → StaticTargetScenario
  - 11 seeker weapon scenarios → StaticTargetScenario
  - 3 propulsion scenarios → PropulsionScenario
- ✅ JSON schema validation system implemented
- ✅ Test data validation with referential integrity checks
- ✅ Pytest integration with schema validation
- ✅ All 23 active tests passing

### Issues Identified

**1. Test Documentation Quality Gaps**
- **Railgun/Projectile tests** lack expected_stats and clear pass/fail criteria
- **Seeker weapon tests** have minimal expected outcome documentation
- **Propulsion tests** don't display ship configuration or component details
- **Test explanations** unclear - difficult to understand why tests pass or fail

**2. UI Test Execution Logging Gap**
- Visual tests run in UI are not logged
- Can't verify UI tests match headless test results
- No confirmation that UI tests produce same results as pytest

**3. Physics Constants Duplication**
- K_SPEED, K_THRUST, K_TURN defined in multiple locations:
  - `game/simulation/entities/ship_physics.py` (2 constants)
  - `game/simulation/entities/ship_stats.py` (3 constants)
  - `simulation_tests/scenarios/propulsion_scenarios.py` (3 constants)
  - `simulation_tests/tests/test_engine_physics.py` (2 constants)
- Risk of divergence and incorrect test calculations
- Should be centralized in one canonical location

**4. Print Statement Usage (168 remaining)**
- Still using print() throughout Combat Lab code
- Should be replaced with proper logging module
- Original plan exists but not yet implemented

---

## Phase 1: Centralize Physics Constants [HIGH PRIORITY]

### Goal
Create single source of truth for all physics constants used in both game engine and Combat Lab tests.

### Current State Analysis

**Constants in Game Code:**
```python
# game/simulation/entities/ship_physics.py (lines 22-40)
K_THRUST = 2500  # Thrust-to-acceleration conversion
K_SPEED = 25     # Thrust-to-speed conversion

# game/simulation/entities/ship_stats.py (lines 244-252)
K_THRUST = 2500  # Acceleration calculation
K_TURN = 25000   # Turn rate calculation
K_SPEED = 25     # Max speed calculation
```

**Constants in Combat Lab:**
```python
# simulation_tests/scenarios/propulsion_scenarios.py (lines 20-21)
K_SPEED = 25
K_THRUST = 2500

# simulation_tests/tests/test_engine_physics.py (lines 16-17)
K_SPEED = 25
K_THRUST = 2500

# simulation_tests/scenarios/propulsion_scenarios.py (line 290)
K_TURN = 25000  # In scenario code
```

### Implementation Plan

#### Step 1.1: Create Physics Constants Module
**New File:** `game/simulation/physics_constants.py`

```python
"""
Physics Constants - Single Source of Truth

These constants define the core physics parameters used throughout the game engine
and Combat Lab test framework. They determine how ship stats (thrust, mass, turn rate)
convert to gameplay behavior (speed, acceleration, turn speed).

DO NOT DUPLICATE THESE CONSTANTS. Import from this module instead.
"""

# Speed Calculation
# Formula: max_speed = (total_thrust * K_SPEED) / mass
K_SPEED = 25

# Acceleration Calculation
# Formula: acceleration = (total_thrust * K_THRUST) / (mass ** 2)
K_THRUST = 2500

# Turn Speed Calculation
# Formula: turn_speed = (raw_turn_speed * K_TURN) / (mass ** 1.5)
K_TURN = 25000

# Documentation of formulas for reference
FORMULA_MAX_SPEED = "max_speed = (total_thrust * K_SPEED) / mass"
FORMULA_ACCELERATION = "acceleration = (total_thrust * K_THRUST) / (mass ** 2)"
FORMULA_TURN_SPEED = "turn_speed = (raw_turn_speed * K_TURN) / (mass ** 1.5)"
```

#### Step 1.2: Update Game Engine Files
**Files to modify:**
- `game/simulation/entities/ship_physics.py`
- `game/simulation/entities/ship_stats.py`

**Pattern:**
```python
# Add import at top
from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN

# Remove local constant definitions
# Delete lines like: K_SPEED = 25

# Use imported constants directly
# (no code changes needed - just remove local definitions)
```

#### Step 1.3: Update Combat Lab Test Files
**Files to modify:**
- `simulation_tests/scenarios/propulsion_scenarios.py`
- `simulation_tests/tests/test_engine_physics.py`

**Pattern:**
```python
# Add import at top
from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN

# Remove local constant definitions
# Update docstrings to reference canonical location
```

#### Step 1.4: Verification
```bash
# Search for any remaining local definitions
grep -n "K_SPEED = \|K_THRUST = \|K_TURN = " game/**/*.py simulation_tests/**/*.py

# Should only find them in physics_constants.py

# Run all tests to ensure no breakage
pytest simulation_tests/tests/ -v
```

### Benefits
- Single source of truth eliminates divergence risk
- Easy to adjust physics tuning (change in one place)
- Clear documentation of physics formulas
- Tests always use same constants as game engine

### Estimated Effort: 1 hour

---

## Phase 2: Enhance Test Documentation [MEDIUM PRIORITY]

### Goal
Make all tests self-documenting with clear expected outcomes, ship configurations, and pass/fail criteria visible in both pytest output and UI.

### Problem Details

**Current Issues:**
1. **Beam weapon tests** - GOOD EXAMPLE ✅
   - Have expected_stats in ship JSON
   - Clear expected hit chances documented
   - Pass/fail criteria explained in test output

2. **Projectile/Railgun tests** - NEEDS WORK ❌
   - No expected_stats in ship JSON
   - Vague assertions like `assert damage_dealt > 0`
   - Unclear why 150 damage is expected minimum
   - No explanation of weapon stats

3. **Seeker weapon tests** - NEEDS WORK ❌
   - Minimal documentation of expected behavior
   - "At least one missile should hit" - but why?
   - No tracking accuracy expectations

4. **Propulsion tests** - NEEDS WORK ❌
   - No ship component info shown in output
   - Can't see engine thrust/mass values
   - No verification of physics formula

### Implementation Plan

#### Step 2.1: Add expected_stats to All Ship JSON Files

**Files needing expected_stats:**
- `Test_Attacker_Proj360.json`
- `Test_Attacker_Proj90.json`
- `Test_Attacker_Seeker360.json`
- All propulsion test ships (Test_Engine_*.json)

**Pattern (example for projectile weapon ship):**
```json
{
  "name": "Test Attacker Proj360",
  "_test_notes": "360° Projectile weapon attacker - Tests accuracy and damage",
  "expected_stats": {
    "max_hp": 145,
    "mass": 50.0,
    "max_speed": 0,
    "acceleration_rate": 0.0,
    "turn_speed": 0.0,
    "total_thrust": 0,
    "weapon_type": "Projectile360",
    "weapon_damage": 50,
    "weapon_accuracy": 0.8,
    "weapon_range": 1000,
    "fire_rate": 1.0
  },
  "resources": {
    "fuel": 0.0,
    "energy": 500.0,
    "ammo": 100.0
  }
}
```

**Pattern (example for propulsion ship):**
```json
{
  "name": "Test Engine 1x Low Mass",
  "_test_notes": "Single standard engine (500 thrust) with minimal mass (40 tons) - Tests high acceleration",
  "expected_stats": {
    "max_hp": 170,
    "mass": 40.0,
    "total_thrust": 500,
    "max_speed": 312.5,
    "acceleration_rate": 781.25,
    "turn_speed": 0.0
  },
  "expected_physics": {
    "formula_max_speed": "max_speed = (thrust * K_SPEED) / mass = (500 * 25) / 40",
    "formula_acceleration": "acceleration = (thrust * K_THRUST) / mass² = (500 * 2500) / 40²"
  }
}
```

#### Step 2.2: Enhance Scenario verify() Methods

**Current pattern (minimal):**
```python
def verify(self, battle_engine) -> bool:
    """Check if at least one missile hit."""
    self.damage_dealt = self.initial_hp - self.target.hp
    self.results['damage_dealt'] = self.damage_dealt
    return self.damage_dealt >= 100
```

**Enhanced pattern (with explanations):**
```python
def verify(self, battle_engine) -> bool:
    """
    Check if seeker missiles successfully tracked and hit target.

    Expected Behavior:
    - Seeker speed: 1000 px/s, Turn rate: 90°/s
    - Distance: 500px → Travel time ~0.5 seconds (50 ticks)
    - Endurance: 5.0 seconds (plenty of time to reach target)
    - Damage: 100 per missile

    Pass Criteria:
    - At least 1 missile hits (damage_dealt >= 100)
    - Target should be destroyed or heavily damaged
    """
    self.damage_dealt = self.initial_hp - self.target.hp

    # Store all results
    self.results['damage_dealt'] = self.damage_dealt
    self.results['initial_hp'] = self.initial_hp
    self.results['final_hp'] = self.target.hp
    self.results['ticks_run'] = battle_engine.tick_counter
    self.results['target_alive'] = self.target.is_alive

    # Store expected values for documentation
    self.results['expected_missile_speed'] = 1000
    self.results['expected_missile_turn_rate'] = 90
    self.results['expected_damage_per_missile'] = 100
    self.results['expected_travel_time_ticks'] = 50

    # Calculate pass/fail
    passed = self.damage_dealt >= 100

    if not passed:
        self.results['failure_reason'] = (
            f"No missiles hit target. Expected at least 100 damage, got {self.damage_dealt}. "
            f"Check missile tracking and collision detection."
        )

    return passed
```

#### Step 2.3: Enhance Test Output in pytest

**Current pattern:**
```python
def test_PROJ360_001_accuracy_vs_stationary(self):
    scenario = self.runner.run_scenario(ProjectileStationaryTargetScenario, headless=True)
    assert scenario.passed, f"PROJ360-001 failed: {scenario.results.get('error', 'Unknown error')}"
    damage_dealt = scenario.results.get('damage_dealt', 0)
    assert damage_dealt > 0, "Projectile should deal damage to stationary target"
```

**Enhanced pattern:**
```python
def test_PROJ360_001_accuracy_vs_stationary(self):
    """
    PROJ360-001: 100% accuracy vs stationary target at point-blank range.

    Expected: All shots should hit. Minimum 3 shots in 500 ticks = 150 damage.
    """
    scenario = self.runner.run_scenario(ProjectileStationaryTargetScenario, headless=True)

    # Print expected configuration
    print(f"\n{'='*60}")
    print(f"PROJ360-001: Projectile Accuracy vs Stationary Target")
    print(f"{'='*60}")
    print(f"\nAttacker Configuration:")
    print(f"  Ship: {scenario.attacker.name}")
    print(f"  Weapon Type: Projectile360")
    print(f"  Weapon Damage: 50")
    print(f"  Weapon Accuracy: 0.8 (80% base)")
    print(f"  Fire Rate: 1.0 shots/sec")
    print(f"\nTarget Configuration:")
    print(f"  Ship: {scenario.target.name}")
    print(f"  Initial HP: {scenario.results['initial_hp']}")
    print(f"  Distance: {scenario.distance}px (point-blank)")
    print(f"\nExpected Outcome:")
    print(f"  Hit Rate: ~100% (stationary, close range)")
    print(f"  Expected Damage: ≥150 (3+ hits in 500 ticks)")
    print(f"\nActual Results:")
    print(f"  Damage Dealt: {scenario.results['damage_dealt']}")
    print(f"  Ticks Run: {scenario.results['ticks_run']}")
    print(f"  Target Final HP: {scenario.results['final_hp']}")
    print(f"  Target Alive: {scenario.results['target_alive']}")
    print(f"\n{'='*60}")

    # Assertions with clear error messages
    assert scenario.passed, (
        f"PROJ360-001 failed: {scenario.results.get('failure_reason', 'Unknown')}\n"
        f"Expected all shots to hit stationary target at close range."
    )

    damage_dealt = scenario.results.get('damage_dealt', 0)
    expected_min_damage = 150
    assert damage_dealt >= expected_min_damage, (
        f"Expected at least {expected_min_damage} damage (3 hits × 50 dmg), "
        f"got {damage_dealt}. Check fire rate and hit detection."
    )
```

#### Step 2.4: Add Propulsion Test Component Display

**New helper function for propulsion tests:**
```python
def print_propulsion_test_header(scenario, test_id, description):
    """Print detailed configuration for propulsion tests."""
    print(f"\n{'='*60}")
    print(f"{test_id}: {description}")
    print(f"{'='*60}")
    print(f"\nShip Configuration:")
    print(f"  Name: {scenario.ship.name}")
    print(f"  Mass: {scenario.ship.mass} tons")
    print(f"  Total Thrust: {scenario.ship.total_thrust}")
    print(f"  Max Speed: {scenario.ship.max_speed} px/s")
    print(f"  Acceleration: {scenario.ship.acceleration_rate} px/s²")
    print(f"  Turn Speed: {scenario.ship.turn_speed}°/s")
    print(f"\nComponents:")
    for component in scenario.ship.components:
        if hasattr(component, 'thrust_power') and component.thrust_power > 0:
            print(f"  - {component.name}: {component.thrust_power} thrust")
    print(f"\nPhysics Constants:")
    print(f"  K_SPEED = {K_SPEED}")
    print(f"  K_THRUST = {K_THRUST}")
    print(f"\nExpected Physics:")
    print(f"  max_speed = (thrust × K_SPEED) / mass")
    print(f"            = ({scenario.ship.total_thrust} × {K_SPEED}) / {scenario.ship.mass}")
    print(f"            = {scenario.ship.max_speed:.2f}")
    print(f"\n{'='*60}")
```

### Benefits
- Clear understanding of test purpose and expected outcomes
- Easy debugging when tests fail (can see exactly what was expected)
- Documentation serves as specification for game mechanics
- Propulsion tests show formula verification

### Estimated Effort: 4 hours

---

## Phase 3: Implement UI Test Logging [MEDIUM PRIORITY]

### Goal
Log all Combat Lab test executions (both UI and headless) so results can be compared and verified.

### Problem
- Tests run in UI produce no log output
- Can't verify UI tests match headless pytest results
- No way to debug discrepancies between UI and headless modes

### Implementation Plan

#### Step 3.1: Update TestRunner for Dual Logging

**File:** `test_framework/runner.py`

```python
class TestRunner:
    def __init__(self):
        self.engine = None
        self.scenario = None
        self.test_log = []  # NEW: Store log of all test executions

    def run_scenario(self, scenario_class, headless=True, log_results=True):
        """
        Run a test scenario in headless or UI mode.

        Args:
            scenario_class: TestScenario class to instantiate and run
            headless: If True, run without UI; if False, run with visualization
            log_results: If True, log results to test_log and optionally file

        Returns:
            Completed scenario instance with results
        """
        scenario = scenario_class()

        # ... existing setup code ...

        # Run simulation
        scenario.run(self.engine)

        # NEW: Log results if enabled
        if log_results:
            self._log_test_execution(scenario, headless)

        return scenario

    def _log_test_execution(self, scenario, headless):
        """Log test execution results for comparison."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'test_id': scenario.metadata.test_id,
            'test_name': scenario.metadata.name,
            'mode': 'headless' if headless else 'ui',
            'passed': scenario.passed,
            'results': scenario.results.copy(),
            'ticks_run': scenario.results.get('ticks_run', 0),
            'damage_dealt': scenario.results.get('damage_dealt', 0)
        }

        self.test_log.append(log_entry)

        # Also write to file for persistence
        log_file = Path("combat_lab_test_log.jsonl")
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        print(f"[TEST LOG] {scenario.metadata.test_id} - "
              f"Mode: {'Headless' if headless else 'UI'} - "
              f"Result: {'PASS' if scenario.passed else 'FAIL'}")
```

#### Step 3.2: Add Log Comparison Utility

**New File:** `simulation_tests/utils/test_log_analyzer.py`

```python
"""
Test Log Analyzer - Compare UI vs Headless Test Results

Reads combat_lab_test_log.jsonl and checks for discrepancies between
UI mode and headless mode test executions.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

def load_test_log(log_file="combat_lab_test_log.jsonl") -> List[Dict]:
    """Load all test log entries from JSONL file."""
    entries = []
    if Path(log_file).exists():
        with open(log_file, 'r') as f:
            for line in f:
                entries.append(json.loads(line.strip()))
    return entries

def compare_test_modes(test_id: str, log_entries: List[Dict]) -> Dict:
    """
    Compare UI vs headless results for a specific test.

    Returns:
        Dictionary with comparison results
    """
    # Filter entries for this test
    test_entries = [e for e in log_entries if e['test_id'] == test_id]

    ui_runs = [e for e in test_entries if e['mode'] == 'ui']
    headless_runs = [e for e in test_entries if e['mode'] == 'headless']

    if not ui_runs or not headless_runs:
        return {
            'test_id': test_id,
            'status': 'incomplete',
            'message': f"Missing runs (UI: {len(ui_runs)}, Headless: {len(headless_runs)})"
        }

    # Compare most recent runs
    latest_ui = sorted(ui_runs, key=lambda e: e['timestamp'])[-1]
    latest_headless = sorted(headless_runs, key=lambda e: e['timestamp'])[-1]

    discrepancies = []

    # Check pass/fail match
    if latest_ui['passed'] != latest_headless['passed']:
        discrepancies.append(
            f"Pass/Fail mismatch: UI={'PASS' if latest_ui['passed'] else 'FAIL'}, "
            f"Headless={'PASS' if latest_headless['passed'] else 'FAIL'}"
        )

    # Check damage dealt (within tolerance)
    ui_dmg = latest_ui.get('damage_dealt', 0)
    headless_dmg = latest_headless.get('damage_dealt', 0)
    if abs(ui_dmg - headless_dmg) > 1.0:  # Allow 1 damage difference
        discrepancies.append(
            f"Damage mismatch: UI={ui_dmg}, Headless={headless_dmg}"
        )

    # Check tick count (within tolerance)
    ui_ticks = latest_ui.get('ticks_run', 0)
    headless_ticks = latest_headless.get('ticks_run', 0)
    if abs(ui_ticks - headless_ticks) > 1:  # Allow 1 tick difference
        discrepancies.append(
            f"Tick count mismatch: UI={ui_ticks}, Headless={headless_ticks}"
        )

    if discrepancies:
        return {
            'test_id': test_id,
            'status': 'mismatch',
            'discrepancies': discrepancies,
            'ui_run': latest_ui,
            'headless_run': latest_headless
        }
    else:
        return {
            'test_id': test_id,
            'status': 'match',
            'message': 'UI and headless results match within tolerance'
        }

def generate_comparison_report(log_file="combat_lab_test_log.jsonl"):
    """Generate full comparison report for all tests."""
    entries = load_test_log(log_file)

    # Get unique test IDs
    test_ids = sorted(set(e['test_id'] for e in entries))

    print(f"\n{'='*70}")
    print(f"Combat Lab Test Log Comparison Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    print(f"Total Tests: {len(test_ids)}")
    print(f"Total Log Entries: {len(entries)}\n")

    matches = 0
    mismatches = 0
    incomplete = 0

    for test_id in test_ids:
        result = compare_test_modes(test_id, entries)

        if result['status'] == 'match':
            matches += 1
            print(f"✓ {test_id}: Results match")
        elif result['status'] == 'mismatch':
            mismatches += 1
            print(f"✗ {test_id}: MISMATCH DETECTED")
            for disc in result['discrepancies']:
                print(f"    - {disc}")
        else:
            incomplete += 1
            print(f"? {test_id}: {result['message']}")

    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  Matching: {matches}")
    print(f"  Mismatches: {mismatches}")
    print(f"  Incomplete: {incomplete}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    generate_comparison_report()
```

#### Step 3.3: Add UI Test Logging to test_lab_scene.py

**File:** `ui/test_lab_scene.py`

Find where tests are executed in UI and ensure TestRunner is called with `log_results=True`.

### Benefits
- Can verify UI and headless tests produce identical results
- Catch rendering or timing issues specific to UI mode
- Build confidence in test framework consistency
- Historical log for debugging regressions

### Estimated Effort: 2 hours

---

## Phase 4: Replace print() with Logging [LOW PRIORITY]

### Status
Detailed plan already exists in the previous plan file. This should be the last phase since it's mainly about code quality/maintenance.

### Quick Summary
- Create `simulation_tests/logging_config.py`
- Replace 168 print() statements across 16 files
- Use proper logging levels (DEBUG, INFO, WARNING, ERROR)
- Console shows INFO+, file logs show DEBUG+

**See existing plan document for full details.**

### Estimated Effort: 5 hours (from original plan)

---

## Implementation Order (Recommended)

### Sprint 1: Physics Constants (1 hour) ⭐ HIGHEST VALUE
**Why first:** Eliminates risk of test/game divergence, affects all physics tests

1. Create `game/simulation/physics_constants.py`
2. Update game engine files to import constants
3. Update Combat Lab files to import constants
4. Verify all tests still pass

### Sprint 2: Enhanced Test Documentation (4 hours) ⭐ HIGH VALUE
**Why second:** Directly addresses user concerns about test clarity

1. Add expected_stats to all ship JSON files (1.5 hours)
2. Enhance scenario verify() methods with explanations (1 hour)
3. Enhance pytest test output (1 hour)
4. Add propulsion test component display (0.5 hours)

### Sprint 3: UI Test Logging (2 hours) ⭐ MEDIUM VALUE
**Why third:** Enables verification but not blocking for test quality

1. Update TestRunner with logging (1 hour)
2. Create test log analyzer utility (0.5 hours)
3. Hook into UI test execution (0.5 hours)

### Sprint 4: Logging Migration (5 hours) ⭐ LOW VALUE
**Why last:** Code quality improvement, doesn't affect functionality

1. Follow existing detailed plan
2. Can be done incrementally
3. Non-breaking change

---

## Total Estimated Effort

- **Phase 1 (Physics Constants):** 1 hour
- **Phase 2 (Test Documentation):** 4 hours
- **Phase 3 (UI Logging):** 2 hours
- **Phase 4 (Print to Logging):** 5 hours

**Total: ~12 hours** (can be spread across multiple sessions)

**Minimum Viable Improvement:** Phases 1-2 only = 5 hours

---

## Success Criteria

### Phase 1 Success
- [ ] No physics constants duplicated in codebase
- [ ] All tests pass after centralization
- [ ] Single import point: `from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN`

### Phase 2 Success
- [ ] All ship JSON files have expected_stats
- [ ] All tests print clear configuration and expected outcomes
- [ ] Propulsion tests show component details and physics formulas
- [ ] Test failures have detailed explanations
- [ ] Can understand test purpose without reading code

### Phase 3 Success
- [ ] UI test executions logged to combat_lab_test_log.jsonl
- [ ] Can run comparison report: `python simulation_tests/utils/test_log_analyzer.py`
- [ ] Verify UI and headless results match within tolerance
- [ ] No silent discrepancies between modes

### Phase 4 Success
- [ ] No print() statements in Combat Lab code
- [ ] Logging outputs to console (INFO+) and file (DEBUG+)
- [ ] All tests pass with logging enabled
- [ ] combat_lab.log contains detailed execution trace

---

## Risk Assessment

**Phase 1 (Physics Constants):** LOW RISK
- Pure refactoring, no logic changes
- Tests will catch any import issues
- Easy rollback if problems occur

**Phase 2 (Test Documentation):** LOW RISK
- Additive changes only (new fields, more output)
- Doesn't change test logic
- Can improve incrementally

**Phase 3 (UI Logging):** MEDIUM RISK
- New file I/O operations
- Could affect UI performance if logging is heavy
- Mitigation: Make logging optional, buffer writes

**Phase 4 (Logging):** LOW RISK
- Non-breaking change (output similar to print)
- Existing detailed plan reduces unknowns
- Can phase incrementally per file

---

## User Concerns Addressed

| User Concern | Solution Phase | Status |
|--------------|---------------|---------|
| Railgun tests lack expected data | Phase 2 | Planned |
| Unclear pass/fail criteria | Phase 2 | Planned |
| Propulsion tests don't show components | Phase 2 | Planned |
| Can't verify UI vs headless | Phase 3 | Planned |
| Physics constants centralization | Phase 1 | Planned |
| Print statements (from code review) | Phase 4 | Planned |

---

## Next Steps

1. **Review this plan** - Confirm priorities and approach
2. **Execute Phase 1** - Start with physics constants (highest value, lowest risk)
3. **Execute Phase 2** - Enhanced documentation (addresses main user concerns)
4. **Evaluate progress** - Decide if Phase 3-4 are needed immediately
