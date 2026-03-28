# Combat Lab - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Diagram](#component-diagram)
4. [Test Framework](#test-framework)
5. [Battle End Conditions](#battle-end-conditions)
6. [Validation System](#validation-system)
7. [Data Files](#data-files)
8. [Creating New Tests](#creating-new-tests)
9. [Beam Weapon Tests](#beam-weapon-tests)
10. [Running Tests](#running-tests)
11. [Troubleshooting](#troubleshooting)
12. [Design Decisions](#design-decisions)

---

## Overview

The **Combat Lab** is a comprehensive testing system for validating combat mechanics in the Starship Battles game. It provides:

- **Visual test runner** - In-game UI for browsing and running tests
- **Statistical validation** - TOST (Two One-Sided Tests) equivalence testing
- **Data verification** - Exact-match checks for component/ship data validation
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
│   ├── run_tests.py                    # Headless test runner (python -m simulation_tests.run_tests)
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
│   ├── validation/                     # Validation system docs
│   │
│   └── scenarios/                      # Test scenario implementations
│       ├── base.py                     # TestScenario, TestMetadata
│       ├── validation.py               # Check, ValidationReport, check functions
│       ├── templates.py                # Reusable scenario templates
│       ├── beam_scenarios.py           # Beam weapon tests
│       ├── defense_scenarios.py        # Defense/armor/shield tests
│       ├── modifier_scenarios.py       # Stat modifier tests
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
│  - setup(engine)           → Initialize ships, positions, expected values   │
│  - update(engine)          → Per-tick logic (optional)                      │
│  - collect_results(engine) → Populate measurement attributes                │
│  - validate(engine)        → Return list of Check objects                   │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                        Validation System                                     │
│              (simulation_tests/scenarios/validation.py)                      │
│                                                                              │
│  ┌─────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐ │
│  │  check_exact    │  │   check_approx     │  │    check_tost            │ │
│  │                 │  │                    │  │       (TOST)             │ │
│  │ Zero-tolerance  │  │ Tolerance-based    │  │                          │ │
│  │ exact match     │  │ approximate match  │  │ p < 0.05 = PASS          │ │
│  │ for component   │  │ for physics calcs  │  │ (proven equivalent)      │ │
│  │ data validation │  │                    │  │                          │ │
│  └─────────────────┘  └────────────────────┘  └──────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Check: Single validation check (phase, name, expected, actual)      │   │
│  │  ValidationReport: Aggregates checks, determines pass/fail           │   │
│  │  - passed, failed_phase, summary(), to_dict()                       │   │
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
         │         └──> scenario._run_validation(engine)
         │                   │
         │                   ├──> scenario.collect_results(engine)
         │                   │         └──> Calculate damage_dealt, hit_rate, etc.
         │                   ├──> scenario.validate(engine)
         │                   │         └──> Return list of Check objects
         │                   ├──> Build ValidationReport from checks
         │                   │
         │                   └──> Return report (passed = True/False)
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

    def validate(self, engine) -> List[Check]:
        """Return all validation checks. MUST be implemented."""
        raise NotImplementedError

    def collect_results(self, engine):
        """Populate measurement attributes before validate() runs. Optional."""
        pass

    def update(self, battle_engine):
        """Optional per-tick update logic."""
        pass

    def _load_ship(self, filename: str) -> Ship:
        """Helper to load ship from simulation_tests/data/ships/"""
```

### TestMetadata

Every test has metadata describing what it tests:

```python
from simulation_tests.scenarios.base import TestMetadata

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
5. scenario._run_validation(engine)
   - Call collect_results(engine) to populate measurement attributes
   - Call validate(engine) to get list of Check objects
   - Build ValidationReport from checks
   - Store results in scenario.results['validation']
   - Set self.passed from report.passed
   ↓
6. RESULTS DISPLAY
   - Show metrics (damage_dealt, hit_rate, ticks_run)
   - Show validation results (PASS/FAIL for each check, grouped by phase)
   - Show failed_phase if any checks failed
   - Show p-values and confidence intervals for statistical checks
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

The Combat Lab uses a three-phase validation system based on `Check` objects and `ValidationReport`.

Scenarios implement `validate(self, engine) -> list` which returns a list of `Check` objects.
Each check is tagged with a phase (`"data"`, `"precondition"`, `"outcome"`) so the framework
knows what failed and why.

### Check Functions

#### check_exact - Data Verification

Validates that a value matches expected with **zero tolerance**.

**Purpose**: Ensures test expectations accurately reflect component definitions.

```python
from simulation_tests.scenarios.validation import check_exact

check_exact("Beam Weapon Damage", expected=1, actual=weapon.damage)
```

#### check_approx - Physics Validation

Validates floating-point calculations with configurable tolerance.

**Purpose**: Validates deterministic physics calculations that should be approximately exact.

```python
from simulation_tests.scenarios.validation import check_approx

check_approx("Expected Hit Chance", expected=0.5318, actual=computed_chance, tolerance=1e-4)
```

#### check_true - Boolean Condition

Validates that a condition is true.

```python
from simulation_tests.scenarios.validation import check_true

check_true("Ship Moved", self.distance > 0)
```

#### check_tost - TOST Equivalence Testing

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
from simulation_tests.scenarios.validation import check_tost

check_tost(
    name='Hit Rate',
    expected_p=0.5318,           # Expected hit rate
    successes=damage_dealt,      # Number of successes
    trials=ticks_run,            # Number of trials
    margin=0.06,                 # ±6% margin
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
from simulation_tests.scenarios.validation import check_exact, check_tost
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
    )

    def setup(self, battle_engine):
        self.attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        self.target = self._load_ship('Test_Target_Stationary.json')

        import pygame
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.target.position = pygame.math.Vector2(50, 0)

        battle_engine.start([self.attacker], [self.target], seed=self.metadata.seed)
        self.initial_hp = self.target.hp

    def collect_results(self, engine):
        """Populate measurement attributes."""
        self.damage_dealt = self.initial_hp - self.target.hp
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = engine.tick_counter
        self.results['hit_rate'] = self.damage_dealt / engine.tick_counter

    def validate(self, engine) -> list:
        """Return Check objects for three-phase validation."""
        checks = []
        # Data phase - verify component data
        weapon = self.attacker.weapon
        checks.append(check_exact('Damage', expected=1, actual=weapon.damage))
        # Outcome phase - verify statistical equivalence
        checks.append(check_tost(
            'Hit Rate',
            expected_p=0.5318,
            successes=self.damage_dealt,
            trials=engine.tick_counter,
            margin=STANDARD_MARGIN,
        ))
        return checks
```

#### 5. Test is Auto-Discovered

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
4. Select test to view details (metadata, conditions, checks)
5. Click "Run Visual" or "Run Headless"
6. View results:
   - Metrics (damage_dealt, hit_rate, ticks_run)
   - Validation results (PASS/FAIL for each check, grouped by phase)
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
python -m simulation_tests.run_tests                # Run all
python -m simulation_tests.run_tests BEAM           # Filter by ID prefix
python -m simulation_tests.run_tests PROP-001       # Run specific test
python -m simulation_tests.run_tests --list         # List all tests
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

#### Data check fails with unexpected value

**Cause**: Test expectations (in `check_exact` calls) don't match actual component/ship data values.

**Solutions**:
1. Update the test's `validate()` method with correct expected values
2. OR update the JSON file if the test's expectations are correct
3. Check if component mass architecture changed (zero-mass components?)

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

### Why Three-Phase Validation?

**Problem**: When a test fails, it can be hard to tell whether the issue is bad data, a broken precondition, or an incorrect outcome.

**Solution**: Each Check is tagged with a phase (`data`, `precondition`, `outcome`). The `ValidationReport.failed_phase` property identifies the root cause immediately.

**Benefits**:
- Data drift caught in the `data` phase before blaming the simulation
- Precondition failures (weapon didn't fire, ship didn't move) separated from outcome failures
- Clear failure attribution simplifies debugging

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
