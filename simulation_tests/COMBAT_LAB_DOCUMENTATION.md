# Combat Lab - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Diagram](#component-diagram)
4. [Test Framework](#test-framework)
5. [Pre-Run Validation System](#pre-run-validation-system)
6. [Battle End Conditions](#battle-end-conditions)
7. [Validation System](#validation-system)
8. [Data Files](#data-files)
9. [Creating New Tests](#creating-new-tests)
10. [Beam Weapon Tests](#beam-weapon-tests)
11. [Running Tests](#running-tests)
12. [Troubleshooting](#troubleshooting)
13. [Design Decisions](#design-decisions)

---

## Overview

The **Combat Lab** is a comprehensive testing system for validating combat mechanics in the Starship Battles game. It provides:

- **Visual test runner** - In-game UI for browsing and running tests
- **Statistical validation** - TOST (Two One-Sided Tests) equivalence testing
- **Data verification** - ExactMatchRules for component/ship data validation
- **Headless execution** - Run tests without UI for CI/CD integration
- **High-tick precision tests** - 100k+ tick tests for precise validation (±1% margins)
- **Standard tests** - 500-tick tests for quick validation (±6% margins)

### Key Features

- **Deterministic & Statistical Tests** - Test both exact outcomes and probabilistic behaviors
- **Self-Documenting** - Each test includes rich metadata explaining what it validates
- **Reproducible** - Fixed test scenarios with explicit expected outcomes and seeds
- **Comprehensive** - Validates formulas, component data, and actual combat outcomes
- **Dual-Mode Execution** - Same tests run identically in visual UI and headless CLI

---

## System Architecture

### Directory Structure

```
Starship Battles/
├── game/
│   └── ui/
│       └── screens/
│           └── test_lab_screen.py      # Combat Lab UI (pygame)
│
├── test_framework/
│   ├── registry.py                     # TestRegistry - scenario discovery
│   ├── runner.py                       # TestRunner - execution engine
│   ├── scenario.py                     # CombatScenario base class
│   ├── test_history.py                 # Test execution history
│   └── services/
│       ├── test_lab_controller.py      # UI controller (coordinates services)
│       ├── scenario_data_service.py    # Ship/component data loading
│       ├── test_execution_service.py   # Test execution orchestration
│       ├── test_results_service.py     # Results storage and retrieval
│       ├── ui_state_service.py         # UI state management
│       └── metadata_management_service.py  # Metadata validation
│
├── simulation_tests/
│   ├── COMBAT_LAB_DOCUMENTATION.md     # This file
│   ├── README.md                       # Documentation hub
│   ├── QUICK_START_GUIDE.md            # 10-minute tutorial
│   ├── test_constants.py               # Centralized test constants
│   ├── logging_config.py               # Combat Lab logging
│   │
│   ├── data/                           # Test data files
│   │   ├── components.json             # Component registry
│   │   ├── modifiers.json              # Stat modifiers
│   │   ├── vehicleclasses.json         # Ship hull types
│   │   └── ships/                      # Ship definitions
│   │       ├── Test_Target_Stationary.json
│   │       ├── Test_Target_Stationary_HighTick.json
│   │       ├── Test_Target_Erratic_Small.json
│   │       └── Test_Attacker_*.json
│   │
│   └── scenarios/                      # Test scenario implementations
│       ├── base.py                     # TestScenario, TestMetadata
│       ├── validation.py               # ValidationRule classes
│       ├── templates.py                # Reusable scenario templates
│       ├── beam_scenarios.py           # Beam weapon tests
│       ├── projectile_scenarios.py     # Projectile weapon tests
│       ├── seeker_scenarios.py         # Seeker/missile tests
│       ├── propulsion_scenarios.py     # Movement/physics tests
│       └── resource_scenarios.py       # Energy/ammo tests
```

---

## Component Diagram

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            COMBAT LAB UI                                     │
│                    (game/ui/screens/test_lab_screen.py)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Category   │  │    Test     │  │    Test     │  │   Results   │        │
│  │   Browser   │  │   Browser   │  │   Details   │  │   Panel     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                       TestLabUIController                                    │
│              (test_framework/services/test_lab_controller.py)               │
│                                                                              │
│  Responsibilities:                                                           │
│  - Coordinate UI actions with business logic services                        │
│  - Manage output logging                                                     │
│  - Orchestrate test execution (visual/headless)                             │
│  - Handle user interactions (category click, test selection, run)           │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐
│   TestRunner    │  │  TestRegistry   │  │          Services               │
│  (runner.py)    │  │ (registry.py)   │  │                                 │
│                 │  │                 │  │  - ScenarioDataService          │
│  - Load data    │  │  - Auto-scan    │  │  - TestExecutionService         │
│  - Run loop     │  │    scenarios/   │  │  - TestResultsService           │
│  - Log results  │  │  - Filter by    │  │  - UIStateService               │
│  - Handle       │  │    category/tag │  │  - MetadataManagementService    │
│    errors       │  │  - Singleton    │  │                                 │
└────────┬────────┘  └────────┬────────┘  └─────────────────────────────────┘
         │                    │
         └─────────┬──────────┘
                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TestScenario                                       │
│                (simulation_tests/scenarios/base.py)                          │
│                                                                              │
│  Class Attributes:                                                           │
│  - metadata: TestMetadata (rich test documentation)                          │
│  - max_ticks: int (maximum simulation ticks)                                │
│  - attacker/target: Ship instances                                          │
│  - results: Dict (populated during execution)                               │
│                                                                              │
│  Methods:                                                                    │
│  - setup(engine)    → Initialize ships, positions, expected values          │
│  - update(engine)   → Per-tick logic (optional)                             │
│  - verify(engine)   → Calculate results, run validation, return pass/fail   │
│  - run_validation() → Execute ValidationRules                               │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                        Validation System                                     │
│              (simulation_tests/scenarios/validation.py)                      │
│                                                                              │
│  ┌─────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐ │
│  │ ExactMatchRule  │  │DeterministicMatch  │  │  StatisticalTestRule     │ │
│  │                 │  │      Rule          │  │       (TOST)             │ │
│  │ Zero-tolerance  │  │                    │  │                          │ │
│  │ exact match     │  │ Tiny tolerance     │  │ p < 0.05 = PASS          │ │
│  │ for component   │  │ (1e-9) for         │  │ (proven equivalent)      │ │
│  │ data validation │  │ physics calcs      │  │                          │ │
│  └─────────────────┘  └────────────────────┘  └──────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Validator                                    │   │
│  │  - Runs all rules, aggregates results                               │   │
│  │  - has_failures(), has_warnings(), get_summary()                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User selects test in UI
         │
         ▼
2. TestLabUIController.handle_test_click(test_id)
         │
         ├──> UIStateService.select_test(test_id)
         │
         ▼
3. User clicks "Run Test"
         │
         ▼
4. TestLabUIController.handle_run_headless() or handle_run_visual()
         │
         ├──> TestRegistry.get_by_id(test_id) → scenario_info
         │
         ├──> TestExecutionService.run_headless(scenario_info, engine)
         │         │
         │         ├──> TestRunner.load_data_for_scenario(scenario)
         │         │         │
         │         │         ├──> Clear RegistryManager
         │         │         ├──> Load components.json
         │         │         ├──> Load modifiers.json
         │         │         └──> Load vehicleclasses.json
         │         │
         │         ├──> scenario.setup(engine)
         │         │         │
         │         │         ├──> Load attacker ship from JSON
         │         │         ├──> Load target ship from JSON
         │         │         ├──> Position ships
         │         │         ├──> Calculate expected values
         │         │         └──> Store initial state
         │         │
         │         ├──> SIMULATION LOOP (max_ticks iterations)
         │         │         │
         │         │         ├──> engine.update()
         │         │         ├──> scenario.update(engine)
         │         │         └──> Check battle end condition
         │         │
         │         └──> scenario.verify(engine)
         │                   │
         │                   ├──> Calculate damage_dealt, hit_rate, etc.
         │                   ├──> scenario.run_validation(engine)
         │                   │         │
         │                   │         ├──> ExactMatchRules
         │                   │         ├──> DeterministicMatchRules
         │                   │         └──> StatisticalTestRules (TOST)
         │                   │
         │                   └──> Return passed = True/False
         │
         └──> TestResultsService.add_run(test_id, results)
                   │
                   └──> Update TestHistory, Registry
```

---

## Test Framework

### TestScenario Base Class

All tests inherit from `TestScenario` (`simulation_tests/scenarios/base.py`):

```python
class TestScenario(CombatScenario):
    """Base class for all test scenarios."""

    metadata: TestMetadata          # Test identification and description
    max_ticks: int                  # Maximum simulation ticks
    attacker: Ship                  # Attacker ship instance
    target: Ship                    # Target ship instance
    results: Dict[str, Any]         # Test results (populated during execution)
    passed: bool                    # Test outcome

    def setup(self, battle_engine):
        """Configure ships and initial state. MUST be implemented."""
        raise NotImplementedError

    def verify(self, battle_engine) -> bool:
        """Check if test passed. MUST be implemented."""
        raise NotImplementedError

    def update(self, battle_engine):
        """Optional per-tick update logic."""
        pass

    def _load_ship(self, filename: str) -> Ship:
        """Helper to load ship from simulation_tests/data/ships/"""

    def run_validation(self, battle_engine) -> List[ValidationResult]:
        """Run all validation rules from metadata."""
```

### TestMetadata

Every test has metadata describing what it tests:

```python
from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.validation import ExactMatchRule, StatisticalTestRule

metadata = TestMetadata(
    test_id="BEAMWEAPON-001",              # Unique identifier
    name="Low Accuracy Beam - Point Blank", # Display name
    category="BeamWeaponAbility",           # Category for grouping
    subcategory="Accuracy - Low",           # Subcategory
    summary="Tests beam hit chance at point-blank range",  # One-line summary
    tags=["beam", "accuracy", "point-blank"], # Searchable tags

    # Test conditions (shown in UI)
    conditions=[
        "Distance: 50px center-to-center (20.53px to surface)",
        "Weapon: Low Accuracy (base 0.5, falloff 0.002/px)",
        "Target: Stationary, Mass 400"
    ],

    edge_cases=["Minimal range penalty at close range"],
    expected_outcome="Hit rate ~53% with damage > 0",
    pass_criteria="damage_dealt > 0",

    max_ticks=500,           # Test duration
    seed=42,                 # Random seed for reproducibility
    battle_end_mode="time_based",  # Run full duration

    # Validation rules (checked after test runs)
    validation_rules=[
        ExactMatchRule(name='Beam Damage', path='attacker.weapon.damage', expected=1),
        StatisticalTestRule(
            name='Hit Rate',
            test_type='binomial',
            expected_probability=0.5318,
            equivalence_margin=0.06,  # ±6% for 500-tick test
            trials_expr='ticks_run',
            successes_expr='damage_dealt'
        )
    ]
)
```

### Test Lifecycle

```
1. TEST SELECTION (in UI or headless)
   ↓
2. TestRunner.load_data_for_scenario()
   - Unfreezes RegistryManager (if needed)
   - Clears registry
   - Loads components.json, modifiers.json, vehicleclasses.json
   ↓
3. scenario.setup(engine)
   - Creates attacker and target ships from JSON files
   - Positions ships at specified distances
   - Calculates expected outcomes (defense score, hit chance)
   - Stores initial_hp for damage calculation
   ↓
4. SIMULATION LOOP (up to max_ticks)
   - engine.update()          # Run one tick of combat simulation
   - scenario.update(engine)  # Test-specific per-tick logic
   - Check if battle is over (time_based mode runs full duration)
   ↓
5. scenario.verify(engine)
   - Calculate actual outcomes (damage_dealt, hit_rate, etc.)
   - Run ExactMatchRules (component data validation)
   - Run DeterministicMatchRules (physics validation)
   - Run StatisticalTestRules (TOST equivalence tests)
   - Store results in scenario.results
   - Set self.passed = True/False
   ↓
6. RESULTS DISPLAY
   - Show metrics (damage_dealt, hit_rate, ticks_run)
   - Show validation results (PASS/FAIL for each rule)
   - Show p-values and confidence intervals
```

---

## Pre-Run Validation System

The Combat Lab includes a **pre-run validation system** that verifies test data BEFORE the test executes. This prevents tests from running with incorrect assumptions about ship/component data.

### Why Pre-Run Validation?

Tests often make assumptions about data values (ship mass, engine thrust, weapon damage). If these assumptions don't match the actual JSON data files, test results are meaningless. Pre-run validation:

1. **Catches data drift** - When component data is modified, affected tests fail fast with clear errors
2. **Documents expectations** - Each test explicitly states what values it expects from data files
3. **Shows formulas** - Calculated values show their formulas with actual values substituted
4. **Blocks invalid tests** - Tests cannot run if data mismatches are detected

### Expectation Types

#### 1. DataExpectation - JSON File Values

Validates that test assumptions about JSON data match actual file values.

```python
from simulation_tests.scenarios.prerun_validation import DataExpectation

DataExpectation(
    name='Ship Mass',
    source='ship.mass',           # Path in loaded object
    expected=400,                 # What we expect
    json_file='Test_Engine_1x.json',  # Source file (for display)
    tolerance=0.001               # 0.1% tolerance for floats
)
```

**Display Format:**
```
DATA VALUES (from JSON):
  [✓] Ship Mass: 400 (expected 400) [Test_Engine_1x.json]
  [✗] Engine Thrust: 500 (expected 600) [Test_Engine_1x.json]  ← BLOCKING
```

#### 2. CalculatedExpectation - Physics Formulas

Validates calculated physics values and shows the formula with actual values.

```python
from simulation_tests.scenarios.prerun_validation import CalculatedExpectation

CalculatedExpectation(
    name='Max Speed',
    formula='(thrust × K_SPEED) / mass',  # Human-readable formula
    formula_expr=lambda thrust, K_SPEED, mass: (thrust * K_SPEED) / mass,
    expected=31.25,
    variables={'thrust': 500, 'K_SPEED': 25, 'mass': 400},
    tolerance=0.001
)
```

**Display Format:**
```
CALCULATED VALUES:
  [✓] Max Speed: 31.25 [= (500 × 25) / 400]
      Actual ship value: 31.25
  [✗] Acceleration: 7.8125 [= (500 × 2500) / 400²]  ← FORMULA MISMATCH
```

#### 3. SetupCondition - Test Parameters (Not Validated)

Documents test setup parameters that are defined by the test itself, not from data files.

```python
from simulation_tests.scenarios.prerun_validation import SetupCondition

SetupCondition(
    name='Initial Position',
    value='(0, 0)',
    description='Ship starts at origin'
)
```

**Display Format:**
```
SETUP CONDITIONS:
  Initial Position: (0, 0) - Ship starts at origin
  Test Duration: 100 ticks
  Throttle Command: 100%
```

#### 4. PassCriterion - Success Criteria

Defines what must be true for the test to pass.

```python
from simulation_tests.scenarios.prerun_validation import PassCriterion

PassCriterion(
    description='final_velocity > expected_velocity × 0.99',
    numeric_threshold=30.94,  # 31.25 × 0.99
    expression=lambda results: results['final_velocity'] > 30.94
)
```

**Display Format:**
```
PASS CRITERIA:
  ✓ final_velocity > 30.94
  ✓ distance_traveled > 0
```

### Using Pre-Run Validation in a Test

```python
class PropulsionMaxSpeedTest(TestScenario):
    """PROP-001: Test that ship reaches calculated max speed."""

    # Define expectations as class attributes
    data_expectations = [
        DataExpectation(
            name='Ship Mass',
            source='ship.mass',
            expected=400,
            json_file='Test_Engine_1x_LowMass.json'
        ),
        DataExpectation(
            name='Engine Thrust',
            source='ship.total_thrust',
            expected=500,
            json_file='Test_Engine_1x_LowMass.json'
        ),
    ]

    calculated_expectations = [
        CalculatedExpectation(
            name='Max Speed',
            formula='(thrust × K_SPEED) / mass',
            formula_expr=lambda thrust, K_SPEED, mass: (thrust * K_SPEED) / mass,
            expected=31.25,
            variables={'thrust': 500, 'K_SPEED': 25, 'mass': 400}
        ),
    ]

    setup_conditions = [
        SetupCondition(name='Initial Position', value='(0, 0)'),
        SetupCondition(name='Throttle', value='100%'),
    ]

    pass_criteria = [
        PassCriterion(
            description='final_velocity >= max_speed × 0.99',
            numeric_threshold=30.94
        ),
    ]

    def custom_setup(self, battle_engine):
        """Called during setup to run pre-run validation."""
        from simulation_tests.scenarios.prerun_validation import PreRunValidator

        context = {'ship': self.ship}
        validator = PreRunValidator()
        self.prerun_validation = validator.validate_scenario(self, context)

        # Store for UI display
        self.results['prerun_validation'] = self.prerun_validation.to_dict()

        # BLOCK execution if validation fails
        if not self.prerun_validation.can_run:
            error_msg = "Pre-run validation failed:\n" + "\n".join(
                self.prerun_validation.blocking_errors
            )
            raise ValueError(error_msg)
```

### UI Display

When pre-run validation is present, the Test Details panel shows:

```
┌─────────────────────────────────────────┐
│ PROP-001: Low Mass Engine Ship          │
├─────────────────────────────────────────┤
│ DATA VALUES (from JSON):                │
│   [✓] Ship Mass: 400                    │
│   [✓] Engine Thrust: 500                │
│                                         │
│ CALCULATED VALUES:                      │
│   [✓] Max Speed: 31.25                  │
│       [= (500 × 25) / 400]              │
│   [✓] Acceleration: 7.8125              │
│       [= (500 × 2500) / 400²]           │
│                                         │
│ SETUP CONDITIONS:                       │
│   Initial Position: (0, 0)              │
│   Throttle: 100%                        │
│   Duration: 100 ticks                   │
│                                         │
│ PASS CRITERIA:                          │
│   • final_velocity >= 30.94             │
│   • distance_traveled > 0               │
└─────────────────────────────────────────┘
```

If validation fails:

```
┌─────────────────────────────────────────┐
│ ⚠ VALIDATION FAILED - TEST BLOCKED     │
├─────────────────────────────────────────┤
│ DATA VALUES (from JSON):                │
│   [✗] Ship Mass: 600 (expected 400)     │
│       ↳ BLOCKING: Data mismatch         │
│                                         │
│ [Run Test] button is DISABLED           │
└─────────────────────────────────────────┘
```

---

## Battle End Conditions

Tests need to control when the simulation ends. The Combat Lab supports multiple end condition modes.

### BattleEndMode Options

| Mode | Description | Use Case |
|------|-------------|----------|
| `TIME_BASED` | End after `max_ticks` | Most tests - run for fixed duration |
| `HP_BASED` | End when one team eliminated | Combat outcome tests |
| `CAPABILITY_BASED` | End when team can't fight | Mission-kill scenarios |
| `ESCAPE_BASED` | End when ships exceed distance | Retreat/escape tests |
| `MANUAL` | Never end (except ceiling) | Interactive exploration |

### Configuring End Conditions in TestMetadata

```python
metadata = TestMetadata(
    test_id="PROP-001",
    # ... other fields ...

    # End condition settings
    battle_end_mode="time_based",   # Most common for tests
    max_ticks=100,                  # Run for exactly 100 ticks

    # Safety ceiling (prevents infinite loops)
    absolute_max_ticks=1_000_000,   # Default: 1 million

    # For ESCAPE_BASED mode:
    # battle_end_mode="escape",
    # escape_radius=5000.0,         # Distance from origin
    # escape_team=1,                # Which team (None=any)
    # escape_all_ships=False,       # Any ship or all ships?

    # For HP_BASED mode:
    # battle_end_mode="hp_based",
    # battle_end_check_derelict=True,  # Count derelict as defeated
)
```

### Common Patterns

#### Single-Ship Tests (Physics, Propulsion)

Use `TIME_BASED` to avoid immediate "victory" when testing one ship:

```python
metadata = TestMetadata(
    battle_end_mode="time_based",  # Don't end on victory
    max_ticks=100,                 # Run exactly 100 ticks
)
```

#### Combat Tests (Two Teams)

Use `HP_BASED` for realistic combat or `TIME_BASED` for statistics:

```python
# For combat outcome tests
metadata = TestMetadata(
    battle_end_mode="hp_based",
    max_ticks=10000,  # Safety timeout
)

# For hit rate statistics (need full duration)
metadata = TestMetadata(
    battle_end_mode="time_based",
    max_ticks=500,
)
```

#### Escape/Retreat Tests

Use `ESCAPE_BASED` for testing ship movement away from battle:

```python
metadata = TestMetadata(
    battle_end_mode="escape",
    escape_radius=5000.0,
    escape_team=0,        # End when team 0 escapes
    escape_all_ships=True # All ships must escape
)
```

### Safety Ceiling

ALL modes respect `absolute_max_ticks` as a hard ceiling to prevent infinite loops:

- Default: 1,000,000 ticks
- Can be customized per-test
- Even `MANUAL` mode will eventually end at this ceiling

```python
# Test will end at 100k ticks even if HP_BASED hasn't triggered
metadata = TestMetadata(
    battle_end_mode="hp_based",
    absolute_max_ticks=100_000,
)
```

---

## Validation System

The Combat Lab uses three types of validation rules:

### 1. ExactMatchRule - Data Verification

Validates that test metadata matches actual component data with **zero tolerance**.

**Purpose**: Ensures test expectations accurately reflect component definitions.

```python
from simulation_tests.scenarios.validation import ExactMatchRule

ExactMatchRule(
    name='Beam Weapon Damage',          # Human-readable name
    path='attacker.weapon.damage',      # Dot-notation path to value
    expected=1                          # Expected value (must match exactly)
)
```

**Common Paths**:
- `attacker.weapon.damage` - Weapon damage value
- `attacker.weapon.base_accuracy` - Base accuracy
- `attacker.weapon.accuracy_falloff` - Falloff per pixel
- `attacker.weapon.range` - Maximum range
- `target.mass` - Target ship mass

**How It Works**:
1. Parses dot-notation path to find the value in validation context
2. Compares actual value to expected value
3. PASS if values match exactly
4. FAIL if values differ (with detailed error message)

### 2. DeterministicMatchRule - Physics Validation

Validates floating-point calculations with tiny tolerance (default 1e-9).

**Purpose**: Validates deterministic physics calculations that should be exact.

```python
from simulation_tests.scenarios.validation import DeterministicMatchRule

DeterministicMatchRule(
    name='Expected Hit Chance',
    path='results.expected_hit_chance',
    expected=0.5318,
    tolerance=1e-4,  # Allow for display rounding
    description='P = 1/(1+e^-x) from sigmoid formula'
)
```

### 3. StatisticalTestRule - TOST Equivalence Testing

Validates that measured outcomes are **statistically equivalent** to expected outcomes.

**Purpose**: Proves that the combat system produces correct probabilistic outcomes.

#### TOST (Two One-Sided Tests)

Traditional hypothesis testing proves things are **different** (p < 0.05 = significantly different).
TOST proves things are **equivalent** (p < 0.05 = proven equivalent within margin).

**The Logic**:
- H0 (Null): Actual differs from expected by MORE than margin (system is broken)
- H1 (Alternative): Actual is WITHIN margin of expected (system works)
- Test 1: Is observed > lower_bound? (not too low)
- Test 2: Is observed < upper_bound? (not too high)
- p_value = max(p1, p2) - need BOTH tests to pass

**Interpretation**:
- **p < 0.05** = PASS (proven equivalent within margin)
- **p ≥ 0.05** = FAIL (not proven equivalent, could be different)

```python
from simulation_tests.scenarios.validation import StatisticalTestRule

StatisticalTestRule(
    name='Hit Rate',
    test_type='binomial',                    # Type of test
    expected_probability=0.5318,             # Expected hit rate
    equivalence_margin=0.06,                 # ±6% margin
    trials_expr='ticks_run',                 # Expression for trial count
    successes_expr='damage_dealt',           # Expression for success count
    description='Each beam hit = 1 damage'
)
```

#### Choosing Equivalence Margins

The margin determines how "close" is "close enough" to call it equivalent:

| Test Type | Ticks | Margin | Standard Error | Use Case |
|-----------|-------|--------|----------------|----------|
| **Standard** | 500 | ±6% | ~2.2% | Quick validation, development |
| **High-Tick** | 100,000 | ±1% | ~0.16% | Precise validation, releases |

**Rule of Thumb**: Margin should be ≥3× the standard error for reliable testing.

---

## Data Files

### components.json

Defines all components (weapons, armor, engines, etc.) used in tests.

```json
{
    "components": [
        {
            "id": "test_beam_low_acc_1dmg",
            "name": "Test Beam (Low Accuracy, 1 Damage)",
            "type": "BeamWeaponAbility",
            "mass": 0,
            "hp": 20,
            "abilities": {
                "BeamWeaponAbility": {
                    "damage": 1,
                    "range": 800,
                    "reload": 0.0,
                    "base_accuracy": 0.5,
                    "accuracy_falloff": 0.002
                }
            }
        }
    ]
}
```

**Key Test Components** (defined in `test_constants.py`):

| Component ID | Purpose | Stats |
|--------------|---------|-------|
| `test_beam_low_acc_1dmg` | Low accuracy beam | base_accuracy=0.5, falloff=0.002, range=800 |
| `test_beam_med_acc_1dmg` | Medium accuracy beam | base_accuracy=2.0, falloff=0.001, range=1000 |
| `test_beam_high_acc_1dmg` | High accuracy beam | base_accuracy=5.0, falloff=0.0005, range=1200 |
| `test_armor_extreme_hp` | Indestructible armor | 1 billion HP, mass=0 |

### Zero-Mass Component Architecture

All non-hull components have **mass = 0**. Ship mass comes only from hull components.

**Rationale**: This isolates mass calculations and ensures predictable defense scores in tests.

### Ship JSON Files (simulation_tests/data/ships/)

```json
{
    "name": "Test Target Stationary",
    "color": [0, 0, 255],
    "team_id": 2,
    "ship_class": "TestS_2L",
    "ai_strategy": "test_do_nothing",
    "layers": {
        "CORE": [
            {"id": "test_armor_extreme_hp"}
        ]
    },
    "_test_notes": "Stationary target with extreme HP for beam testing",
    "expected_stats": {
        "max_hp": 1000000100,
        "mass": 400.0
    }
}
```

**Why 1 Billion HP?**
- Ensures targets NEVER die during tests (even 100k tick high-accuracy tests)
- High-accuracy beam: 99% hit rate × 100k ticks = ~99k damage (0.01% of 1B)
- Prevents early battle termination, ensuring full tick count runs

---

## Creating New Tests

### Step-by-Step Guide

#### 1. Identify What to Test

Examples:
- New weapon type (projectiles, missiles)
- New combat mechanic (shields, countermeasures)
- Edge case (out of range, zero defense, etc.)

#### 2. Create Test Components (if needed)

Add to `simulation_tests/data/components.json`.

#### 3. Calculate Expected Outcomes

Use the formulas from the game engine:

```python
import math

# Target radius from mass
target_radius = 40 * ((mass / 1000) ** (1/3))

# Surface distance (what weapons use)
surface_distance = center_distance - target_radius

# Defense score (logarithmic formula from ship_stats.py)
def calculate_defense_score(mass, acceleration=0.0, turn_speed=0.0, ecm_score=0.0):
    # Radius calculation
    base_radius = 40
    actual_mass = max(mass, 100)
    radius = base_radius * ((actual_mass / 1000) ** (1/3))

    # Size score (logarithmic)
    diameter = radius * 2
    d_ratio = max(0.1, diameter / 80.0)
    size_score = -2.5 * math.log10(d_ratio)

    # Maneuver score
    maneuver_score = math.sqrt((acceleration / 20.0) + (turn_speed / 360.0))

    return size_score + maneuver_score + ecm_score

# Hit chance (sigmoid formula)
def calculate_hit_chance(base_acc, falloff, distance, attack_bonus=0.0, defense_penalty=0.0):
    range_penalty = distance * falloff
    net_score = (base_acc + attack_bonus) - (range_penalty + defense_penalty)
    clamped = max(-20.0, min(20.0, net_score))
    return 1.0 / (1.0 + math.exp(-clamped))
```

#### 4. Write Test Scenario Class

```python
from simulation_tests.scenarios.base import TestScenario, TestMetadata
from simulation_tests.scenarios.validation import ExactMatchRule, StatisticalTestRule
from simulation_tests.test_constants import *

class MyBeamTest(TestScenario):
    """BEAMWEAPON-XXX: Description of test."""

    metadata = TestMetadata(
        test_id="BEAMWEAPON-XXX",
        category="BeamWeaponAbility",
        subcategory="Accuracy - Low",
        name="My Beam Test",
        summary="Tests specific beam behavior",
        conditions=["Distance: 50px", "Target: Mass 400"],
        edge_cases=["Specific edge case"],
        expected_outcome="Expected behavior",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        validation_rules=[
            ExactMatchRule(name='Damage', path='attacker.weapon.damage', expected=1),
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.5318,
                equivalence_margin=STANDARD_MARGIN,
                trials_expr='ticks_run',
                successes_expr='damage_dealt'
            )
        ]
    )

    def setup(self, battle_engine):
        self.attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        self.target = self._load_ship('Test_Target_Stationary.json')

        import pygame
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.target.position = pygame.math.Vector2(50, 0)

        battle_engine.start([self.attacker], [self.target], seed=self.metadata.seed)
        self.initial_hp = self.target.hp

    def verify(self, battle_engine) -> bool:
        self.damage_dealt = self.initial_hp - self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter

        self.run_validation(battle_engine)
        return self.damage_dealt > 0
```

#### 5. Add Pre-Run Validation (Recommended)

For physics tests that depend on specific data values, add pre-run validation:

```python
from simulation_tests.scenarios.prerun_validation import (
    DataExpectation, CalculatedExpectation, SetupCondition, PassCriterion
)

class MyPropulsionTest(TestScenario):
    """PROP-XXX: Description of test."""

    # Expected values from JSON files - MUST match actual data
    data_expectations = [
        DataExpectation(
            name='Ship Mass',
            source='ship.mass',
            expected=400,                         # What we expect
            json_file='Test_Ship.json'            # Source file for reference
        ),
        DataExpectation(
            name='Engine Thrust',
            source='ship.total_thrust',
            expected=500,
            json_file='Test_Ship.json'
        ),
    ]

    # Calculated values - show formulas with actual values
    calculated_expectations = [
        CalculatedExpectation(
            name='Max Speed',
            formula='(thrust × K_SPEED) / mass',  # Human-readable
            formula_expr=lambda thrust, K_SPEED, mass: (thrust * K_SPEED) / mass,
            expected=31.25,
            variables={'thrust': 500, 'K_SPEED': 25, 'mass': 400}
        ),
    ]

    # Setup conditions (not validated, just displayed)
    setup_conditions = [
        SetupCondition(name='Initial Position', value='(0, 0)'),
        SetupCondition(name='Throttle Command', value='100%'),
    ]

    # Pass criteria
    pass_criteria = [
        PassCriterion(
            description='final_velocity >= expected × 0.99',
            numeric_threshold=30.94
        ),
    ]

    def setup(self, battle_engine):
        self.ship = self._load_ship('Test_Ship.json')
        # ... position ship, etc ...

        # Run pre-run validation (blocks if data mismatch)
        self._run_prerun_validation()

        battle_engine.start([self.ship], [], seed=self.metadata.seed)

    def _run_prerun_validation(self):
        """Validate expectations before test runs."""
        from simulation_tests.scenarios.prerun_validation import PreRunValidator

        context = {'ship': self.ship}
        validator = PreRunValidator()
        self.prerun_validation = validator.validate_scenario(self, context)
        self.results['prerun_validation'] = self.prerun_validation.to_dict()

        if not self.prerun_validation.can_run:
            errors = "\n".join(self.prerun_validation.blocking_errors)
            raise ValueError(f"Pre-run validation failed:\n{errors}")
```

#### 6. Test is Auto-Discovered

The `TestRegistry` automatically scans `simulation_tests/scenarios/` and registers all `TestScenario` subclasses with metadata.

---

## Beam Weapon Tests

### Current Test Suite

Test IDs follow the pattern: `BEAMWEAPON-XXX` for standard tests, `BEAMWEAPON-XXX-HT` for high-tick variants.

#### Standard Tests (500 ticks, ±6% margin)

| Test ID | Description | Expected Hit Rate |
|---------|-------------|-------------------|
| **BEAMWEAPON-001** | Low Accuracy, Point Blank (50px) | 53.18% |
| **BEAMWEAPON-002** | Low Accuracy, Mid Range (400px) | varies |
| **BEAMWEAPON-003** | Low Accuracy, Max Range (750px) | varies |
| **BEAMWEAPON-004** | Medium Accuracy, Point Blank | varies |
| **BEAMWEAPON-005** | Medium Accuracy, Mid Range | varies |
| **BEAMWEAPON-006** | Medium Accuracy, Max Range | varies |
| **BEAMWEAPON-007** | High Accuracy, Point Blank | ~99% |
| **BEAMWEAPON-008** | High Accuracy, Max Range | varies |
| **BEAMWEAPON-009** | vs Erratic Small Target | varies |
| **BEAMWEAPON-010** | vs Erratic Small, Max Range | varies |
| **BEAMWEAPON-011** | Out of Range (deterministic) | 0% |

#### High-Tick Tests (100,000 ticks, ±1% margin)

| Test ID | Description |
|---------|-------------|
| **BEAMWEAPON-001-HT** | Low Accuracy, Point Blank |
| **BEAMWEAPON-002-HT** | Low Accuracy, Mid Range |
| **BEAMWEAPON-004-HT** | Medium Accuracy, Point Blank |
| ... | ... |

### Beam Weapon Mechanics

#### Surface Distance Calculation

Beam weapons measure distance to target **surface**, not center:

```python
# Target radius formula
target_radius = 40 * (mass / 1000) ** (1/3)

# Examples:
# mass=400 → radius = 40 × (0.4)^(1/3) = 29.47px
# mass=600 → radius = 40 × (0.6)^(1/3) = 33.74px

# Surface distance
surface_distance = center_to_center_distance - target_radius
```

**CRITICAL**: Test expectations MUST use surface distance, not center distance.

#### Hit Chance Calculation (Sigmoid Formula)

```python
def calculate_hit_chance(base_acc, falloff, distance, attack_bonus, defense_penalty):
    """
    P = 1 / (1 + e^-x)
    where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    """
    range_penalty = distance * falloff
    net_score = (base_acc + attack_bonus) - (range_penalty + defense_penalty)
    return 1.0 / (1.0 + math.exp(-net_score))
```

**Sigmoid Curve Properties**:
- net_score = 0 → 50% hit chance
- net_score = +2 → 88% hit chance
- net_score = -2 → 12% hit chance
- net_score > +4 → ~98%+ hit chance
- net_score < -4 → ~2%- hit chance

#### Defense Score Calculation (Logarithmic Formula)

The actual implementation uses a logarithmic formula based on ship diameter:

```python
def calculate_defense_score(mass, acceleration, turn_speed, ecm_score):
    """
    Calculate target's total defense score.

    This matches the calculation in game/simulation/formulas/ship_stats.py
    """
    # Radius calculation
    base_radius = 40
    ref_mass = 1000
    actual_mass = max(mass, 100)
    ratio = actual_mass / ref_mass
    radius = base_radius * (ratio ** (1/3.0))

    # Size score (logarithmic - larger ships are easier to hit)
    diameter = radius * 2
    d_ratio = max(0.1, diameter / 80.0)
    size_score = -2.5 * math.log10(d_ratio)

    # Maneuver score (sqrt-based)
    maneuver_score = math.sqrt((acceleration / 20.0) + (turn_speed / 360.0))

    return size_score + maneuver_score + ecm_score
```

---

## Resource System Tests

Resource tests validate fuel, energy, and ammo consumption, depletion, and regeneration.

### Current Test Suite

Test IDs follow the pattern: `RESOURCE-XXX`.

#### Fuel Tests (500 ticks)

| Test ID | Description | Pass Criteria |
|---------|-------------|---------------|
| **RESOURCE-001** | Engine Fuel Consumption | fuel consumed ≈ 5.0, ship moving |
| **RESOURCE-002** | Engine Fuel Depletion/Starvation | fuel = 0, ship stopped mid-test |
| **RESOURCE-003** | Fuel Regeneration Sustains Engine | fuel stable, ship moving |

#### Energy Tests (100 ticks)

| Test ID | Description | Pass Criteria |
|---------|-------------|---------------|
| **RESOURCE-004** | Beam Energy Consumption | 100 shots, energy consumed = 100 |
| **RESOURCE-005** | Energy Depletion Stops Weapon | 25 shots, energy = 0 |
| **RESOURCE-005a** | Energy Regeneration Sustains Weapon | 100 shots, energy stable |

#### Ammo Tests (100 ticks)

| Test ID | Description | Pass Criteria |
|---------|-------------|---------------|
| **RESOURCE-006** | Projectile Ammo Consumption | 100 shots, ammo consumed = 100 |
| **RESOURCE-007** | Ammo Depletion Stops Projectile | 10 shots, ammo = 0 |
| **RESOURCE-008** | Seeker Ammo Consumption | 100 launches (hits not tracked) |

### Resource System Mechanics

#### ResourceConsumption Ability

Components consume resources via `ResourceConsumption` ability:

```python
# Constant consumption (engines)
"ResourceConsumption": [
    {"resource": "fuel", "amount": 1.0, "trigger": "constant"}
]

# Activation consumption (weapons)
"ResourceConsumption": [
    {"resource": "energy", "amount": 1, "trigger": "activation"}
]
```

#### ResourceGeneration Ability

Generators produce resources via `ResourceGeneration` ability:

```python
"ResourceGeneration": [
    {"resource": "energy", "amount": 100}  # 100/sec = 1/tick
]
```

#### Fuel Starvation Behavior

When fuel runs out:
1. `ResourceConsumption.update()` returns `False`
2. `Component._is_operational` set to `False`
3. Engine contributes 0 thrust (via `operational_only=True`)
4. Ship decelerates to 0

### UI Display for Resource Tests

**TestRunCard (Brief)**:
- Fuel: "Fuel: 1000 → 995 (-5.0), Velocity: 10.5 (moving)"
- Energy: "Energy: 100 → 0 (depleted), Shots: 100"
- Ammo: "Ammo: 100 → 0 (depleted), Shots: 100"

**TestRunDetailsPanel (Detailed)**:
```
RESOURCE CONSUMPTION
  Initial Fuel:     1000.0 units
  Final Fuel:       995.0 units
  Consumed:         5.0 units
  Expected:         5.0 units
  ✓ Within tolerance
  Final Velocity:   10.5 (moving)
```

---

## Running Tests

### In Combat Lab UI

1. Launch game: `python main.py`
2. Navigate to "Combat Lab" from main menu
3. Browse tests by category in left panels
4. Select test to view details (metadata, conditions, validation rules)
5. Click "Run Visual" or "Run Headless"
6. View results:
   - Metrics (damage_dealt, hit_rate, ticks_run)
   - Validation results (PASS/FAIL for each rule)
   - P-values and statistical analysis

### Headless Execution

```python
"""Run test headlessly."""
from simulation_tests.scenarios.beam_scenarios import BeamLowAccuracyPointBlankScenario
from test_framework.runner import TestRunner

# Create and run
runner = TestRunner()
scenario = runner.run_scenario(BeamLowAccuracyPointBlankScenario, headless=True)

# Check results
print(f"Test: {scenario.metadata.test_id}")
print(f"Result: {'PASSED' if scenario.passed else 'FAILED'}")
print(f"Damage Dealt: {scenario.results['damage_dealt']}")
print(f"Hit Rate: {scenario.results.get('hit_rate', 0):.2%}")
```

### Command Line

```bash
python -m test_framework.runner simulation_tests/scenarios/beam_scenarios.py --headless
```

---

## Troubleshooting

### Common Issues

#### Test fails with "Ship stats mismatch after loading"

**Cause**: Ship `expected_stats` don't match actual calculated stats.

**Solution**: Update `expected_stats` in ship JSON file or check component data.

#### Test fails with large deviation in hit rate

**Cause**: Expected hit rate may be using center-to-center distance instead of surface distance.

**Solution**: Recalculate using surface distance:
```python
target_radius = 40 * ((mass / 1000) ** (1/3))
surface_distance = center_distance - target_radius
```

#### TOST test fails with p-value just above 0.05

**Cause**: Statistical variance in small sample sizes.

**Solutions**:
1. Run test multiple times to check consistency
2. Verify expected probability calculation
3. Use high-tick version for critical validation

#### Target dies before test completes

**Cause**: Not enough HP for test duration.

**Solution**: Use extreme HP armor (1 billion HP) for test targets.

#### Pre-run validation fails with "Data mismatch"

**Cause**: Test expectations don't match actual JSON data values.

**Example Error**:
```
Pre-run validation failed:
Data mismatch - Ship Mass: expected 400, got 600
```

**Solutions**:
1. Update the test's `data_expectations` to match current JSON values
2. OR update the JSON file if the test's expectations are correct
3. Check if component mass architecture changed (zero-mass components?)

#### Pre-run validation fails with "path not found"

**Cause**: The `source` path in a DataExpectation doesn't match the object structure.

**Example Error**:
```
Data error - Engine Thrust: Attribute 'thrust' not found on Ship
```

**Solution**: Check the actual attribute names on the loaded object:
- `ship.mass` not `ship.total_mass`
- `ship.total_thrust` not `ship.thrust`
- Use `dir(ship)` to see available attributes

#### Single-ship test ends immediately with "victory"

**Cause**: Using `hp_based` mode with only one team triggers immediate victory.

**Solution**: Use `time_based` mode for single-ship tests:
```python
metadata = TestMetadata(
    battle_end_mode="time_based",
    max_ticks=100,
)
```

#### Test runs forever (or very long)

**Cause**: Using `manual` mode without understanding the ceiling.

**Solution**: Either:
1. Set explicit `max_ticks` with `time_based` mode
2. Or rely on `absolute_max_ticks` ceiling (default 1M ticks)
3. For faster tests, set a lower `absolute_max_ticks`:
```python
metadata = TestMetadata(
    battle_end_mode="manual",
    absolute_max_ticks=10_000,
)
```

---

## Design Decisions

### Why Pre-Run Validation?

**Problem**: Tests make assumptions about JSON data (ship mass = 400, thrust = 500). If these assumptions drift from actual data, tests produce meaningless results.

**Solution**: Validate assumptions BEFORE running. Tests explicitly declare their expectations, and execution is blocked if data doesn't match.

**Benefits**:
- Catches data drift immediately
- Documents what values the test depends on
- Shows formulas with actual values for transparency
- Prevents "false pass" tests that ran with wrong data

### Why Show Formulas with Values?

Instead of just showing `max_speed: 31.25`, we show:
```
max_speed: 31.25 [= (500 × 25) / 400]
```

This makes it obvious:
1. What formula was used
2. What values were plugged in
3. Why the expected result is what it is

If the formula is wrong, reviewers can spot it immediately.

### Why Block Tests on Data Mismatch?

A test running with wrong assumptions is worse than no test:
- It gives false confidence
- Results can't be trusted
- Debugging becomes harder (is the formula wrong or the data wrong?)

By blocking execution, we force the issue to be resolved first.

### Why TOST Instead of Traditional Hypothesis Testing?

Traditional testing proves "difference" - it can only say "we found no significant difference."
TOST proves "equivalence" - it actively proves the observed rate IS equivalent to expected.

**Implication**: p < 0.05 in TOST means PASS (proven equivalent), not FAIL.

### Why Surface Distance?

Beam weapons use raycasting that intersects with the target's collision circle. The hit calculation uses the distance to the first intersection point (the surface), not the center.

### Why Zero-Mass Components?

Isolates mass calculations to hull only. This ensures predictable defense scores and simplifies test setup.

### Why Absolute Max Ticks Safety Ceiling?

**Problem**: A misconfigured test (MANUAL mode with no explicit end condition) could run forever.

**Solution**: All modes respect `absolute_max_ticks` (default 1,000,000) as a hard ceiling.

**Trade-off**: Very long tests must explicitly set a higher ceiling, but infinite loops are prevented.

### Why TIME_BASED for Single-Ship Tests?

**Problem**: Single-ship tests (propulsion, physics) using HP_BASED mode report "victory" immediately because there's no enemy team.

**Solution**: Use `TIME_BASED` mode which runs for exactly `max_ticks` regardless of team status.

**Pattern**:
- Single-ship physics tests: `TIME_BASED`
- Combat outcome tests: `HP_BASED`
- Hit rate statistics: `TIME_BASED` (need full duration)

### Why 1 Billion HP?

Prevents early battle termination. Even with 100k ticks at 99% hit rate, only ~99k damage is dealt (0.01% of 1B HP).

### Why Two Test Tiers?

- **Standard (500 ticks, ±6%)**: Fast feedback during development
- **High-Tick (100k ticks, ±1%)**: Precise validation before releases

The margin is chosen to be ≥3× the standard error for the sample size.

---

## Credits & Version History

**Created**: January 2026
**Last Updated**: January 2026

**Combat Lab System Design**: Claude + User collaboration
**Key Components**:
- TOST equivalence testing for probabilistic validation
- Logarithmic defense score formula
- Surface distance calculations for beam weapons
- Comprehensive test metadata system

**Key Learnings**:
- Beam weapons use surface distance, not center-to-center distance
- Defense score uses logarithmic formula based on diameter
- TOST proves equivalence (p < 0.05 = PASS)
- ±6% margin for 500-tick tests, ±1% for 100k-tick tests
