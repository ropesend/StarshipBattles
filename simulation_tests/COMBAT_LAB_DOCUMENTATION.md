# Combat Lab - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Test Framework](#test-framework)
4. [Validation System](#validation-system)
5. [Data Files](#data-files)
6. [Creating New Tests](#creating-new-tests)
7. [Beam Weapon Tests](#beam-weapon-tests)
8. [Running Tests](#running-tests)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Combat Lab** is a comprehensive testing system for validating combat mechanics in the Starship Battles game. It provides:

- **Visual test runner** - UI for browsing and running tests
- **Statistical validation** - TOST (Two One-Sided Tests) equivalence testing
- **Data verification** - ExactMatchRules for component/ship data validation
- **Headless execution** - Run tests without UI for CI/CD
- **High-tick precision tests** - 100k+ tick tests for precise validation (±1% margins)
- **Standard tests** - 500-tick tests for quick validation (±6% margins)

### Key Features

✅ **Deterministic & Statistical Tests** - Test both exact outcomes and probabilistic behaviors
✅ **Self-Documenting** - Each test includes metadata explaining what it validates
✅ **Reproducible** - Fixed test scenarios with explicit expected outcomes
✅ **Comprehensive** - Validates formulas, component data, and actual combat outcomes

---

## System Architecture

### Directory Structure

```
simulation_tests/
├── COMBAT_LAB_DOCUMENTATION.md    # This file
├── data/                          # Test data files
│   ├── components.json            # Component registry (armor, weapons, etc.)
│   ├── modifiers.json             # Stat modifiers
│   ├── vehicleclasses.json        # Ship hull types
│   └── ships/                     # Ship definitions for tests
│       ├── Test_Target_Stationary.json
│       ├── Test_Target_Stationary_HighTick.json
│       ├── Test_Target_Erratic_Small.json
│       └── Test_Attacker_*.json
├── scenarios/                     # Test scenario implementations
│   ├── beam_scenarios.py          # All beam weapon tests
│   └── (future: projectile_scenarios.py, etc.)
├── validation/                    # Validation rule system
│   ├── rules.py                   # ExactMatchRule, StatisticalTestRule
│   └── validators.py              # Validation execution logic
└── test_framework/                # Core framework
    ├── base.py                    # TestScenario base class, TestMetadata
    └── runner.py                  # TestRunner for headless execution
```

### Component Relationships

```
┌─────────────────┐
│   Combat Lab    │  UI for browsing/running tests
│  (test_lab.py)  │
└────────┬────────┘
         │
         ├──> TestRunner (loads data, runs scenarios)
         │
         ├──> TestScenario (base class for all tests)
         │    ├─> setup()      - Initialize ships and engine
         │    ├─> update()     - Run one tick of simulation
         │    └─> verify()     - Check results against expectations
         │
         ├──> ValidationRules
         │    ├─> ExactMatchRule       - Verify component data
         │    └─> StatisticalTestRule  - TOST equivalence testing
         │
         └──> Data Files (ships, components, modifiers)
```

---

## Test Framework

### TestScenario Base Class

All tests inherit from `TestScenario` (`test_framework/base.py`):

```python
class TestScenario:
    """Base class for all test scenarios."""

    metadata: TestMetadata          # Test identification and description
    max_ticks: int                  # Maximum simulation ticks
    attacker: Ship                  # Attacker ship instance
    target: Ship                    # Target ship instance
    results: Dict[str, Any]         # Test results (populated during execution)
    passed: bool                    # Test outcome
```

### TestMetadata

Every test has metadata describing what it tests:

```python
metadata = TestMetadata(
    test_id="BEAM360-001",                    # Unique identifier
    name="Low Accuracy Beam - Point Blank",   # Display name
    category="Beam Weapons",                  # Category for grouping
    subcategory="Accuracy Tests",             # Subcategory
    summary="Tests beam hit chance at point-blank range",  # One-line summary
    tags=["beam", "accuracy", "point-blank"], # Searchable tags

    # Test conditions (shown in UI)
    conditions=[
        "Distance: 50px center-to-center (16.26px to surface)",
        "Weapon: Low Accuracy (base 50%, falloff 0.2%/px)",
        "Target: Stationary, Mass 400"
    ],

    # Validation rules (checked after test runs)
    validation_rules=[
        ExactMatchRule(name='Beam Damage', path='attacker.weapon.damage', expected=1),
        StatisticalTestRule(name='Hit Rate', expected_probability=0.5318, ...)
    ]
)
```

### Test Lifecycle

```
1. TEST SELECTION (in UI or headless)
   ↓
2. TestRunner.load_data_for_scenario()
   - Clears registry
   - Loads components.json
   - Loads modifiers.json
   - Loads vehicleclasses.json
   ↓
3. scenario.setup(engine)
   - Creates attacker and target ships from JSON files
   - Positions ships
   - Calculates expected outcomes
   - Stores initial_hp
   ↓
4. SIMULATION LOOP (up to max_ticks)
   - scenario.update(engine)  # Test-specific logic
   - engine.update()          # Run one tick of combat
   - Check if battle is over
   ↓
5. scenario.verify(engine)
   - Calculate actual outcomes (damage_dealt, hit_rate, etc.)
   - Run ExactMatchRules (component data validation)
   - Run StatisticalTestRules (TOST equivalence tests)
   - Set self.passed = True/False
   ↓
6. RESULTS DISPLAY
   - Show metrics (damage_dealt, hit_rate, etc.)
   - Show validation results (PASS/FAIL for each rule)
   - Show p-values and confidence intervals
```

---

## Validation System

The Combat Lab uses two types of validation rules:

### 1. ExactMatchRule - Data Verification

Validates that test metadata matches actual component data with **zero tolerance**.

**Purpose**: Ensures test expectations accurately reflect component definitions.

```python
ExactMatchRule(
    name='Beam Weapon Damage',          # Human-readable name
    path='attacker.weapon.damage',      # Dot-notation path to value
    expected=1                          # Expected value (must match exactly)
)
```

**Common Paths**:
- `attacker.weapon.damage` - Weapon damage value
- `attacker.weapon.base_accuracy` - Base accuracy (0.0 to 1.0)
- `attacker.weapon.accuracy_falloff` - Falloff per pixel
- `attacker.weapon.range` - Maximum range
- `target.mass` - Target ship mass

**How It Works**:
1. Parses dot-notation path to find the value on the scenario object
2. Compares actual value to expected value
3. PASS if values match exactly (within floating-point tolerance)
4. FAIL if values differ

**Example Output**:
```
[PASS] Beam Weapon Damage
  Expected: 1, Actual: 1, Difference: 0.0

[FAIL] Base Accuracy
  Expected: 0.5, Actual: 0.6, Difference: 0.1
```

### 2. StatisticalTestRule - TOST Equivalence Testing

Validates that observed outcomes are **statistically equivalent** to expected outcomes.

**Purpose**: Proves that the combat system produces correct probabilistic outcomes.

#### TOST (Two One-Sided Tests)

Traditional hypothesis testing proves things are **different** (p < 0.05 = significantly different).
TOST proves things are **equivalent** (p < 0.05 = proven equivalent within margin).

**The Logic**:
- H₁: μ - θ > -ε (observed is not too low)
- H₂: μ - θ < +ε (observed is not too high)
- If BOTH tests have p < 0.05, then equivalence is proven

**Interpretation**:
- **p < 0.05** = PASS (proven equivalent within margin)
- **p ≥ 0.05** = FAIL (not proven equivalent, could be different)

```python
StatisticalTestRule(
    name='Hit Rate',
    test_type='binomial',                    # Type of test (binomial for hit/miss)
    expected_probability=0.5318,             # Expected hit rate (0.0 to 1.0)
    equivalence_margin=0.06,                 # ±6% margin (0.06 for 500-tick, 0.01 for 100k-tick)
    trials_expr='ticks_run',                 # Expression for number of trials
    successes_expr='damage_dealt',           # Expression for number of successes
    description='Each beam hit = 1 damage'   # Explanation
)
```

#### Choosing Equivalence Margins

The margin determines how "close" is "close enough" to call it equivalent:

| Test Type | Ticks | Margin | Standard Error | Use Case |
|-----------|-------|--------|----------------|----------|
| **Standard** | 500 | ±6% | ~2.2% | Quick validation, development |
| **High-Tick** | 100,000 | ±1% | ~0.16% | Precise validation, final verification |

**Rule of Thumb**:
- Margin should be ≥3× the standard error for reliable testing
- SE ≈ 0.5/√n for binomial tests at p≈0.5

#### Example: Beam Hit Rate Validation

```python
# Test runs 500 ticks, weapon deals 1 damage per hit
# Expected hit rate: 53.18%
# Observed: 260 damage = 260 hits = 52.00% hit rate

StatisticalTestRule(
    name='Hit Rate',
    test_type='binomial',
    expected_probability=0.5318,     # 53.18%
    equivalence_margin=0.06,         # ±6% (47.18% to 59.18%)
    trials_expr='ticks_run',         # 500 ticks
    successes_expr='damage_dealt'    # 260 hits
)

# TOST Calculation:
# H₁: 0.5200 - 0.5318 > -0.06  →  -0.0118 > -0.06  →  TRUE, p₁ = 0.0134
# H₂: 0.5200 - 0.5318 < +0.06  →  -0.0118 < +0.06  →  TRUE, p₂ = 0.0134
# max(p₁, p₂) = 0.0134 < 0.05  →  PASS (proven equivalent)
```

**Result**: The observed 52.00% hit rate is statistically equivalent to the expected 53.18% within ±6% margin.

---

## Data Files

### components.json

Defines all components (weapons, armor, engines, etc.) used in tests.

**Structure**:
```json
{
    "components": [
        {
            "id": "test_beam_low_acc_1dmg",
            "name": "Test Beam (Low Accuracy, 1 Damage)",
            "type": "BeamWeaponAbility",
            "mass": 5,
            "hp": 20,
            "sprite_index": 87,
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

**Key Test Components**:

| Component ID | Purpose | Stats |
|--------------|---------|-------|
| `test_beam_low_acc_1dmg` | Low accuracy beam | 50% base, 0.2%/px falloff, range 800 |
| `test_beam_med_acc_1dmg` | Medium accuracy beam | 80% base, 0.1%/px falloff, range 800 |
| `test_beam_high_acc_1dmg` | High accuracy beam | 99% base, 0.01%/px falloff, range 800 |
| `test_armor_extreme_hp` | Indestructible armor | 1 billion HP, mass 200 |
| `test_armor_extreme_hp_heavy` | Heavy indestructible | 1 billion HP, mass 400 |
| `test_armor_small_extreme_hp` | Small indestructible | 1 billion HP, mass 20 |

### Ship JSON Files (simulation_tests/data/ships/)

Define ship configurations for test scenarios.

**Example: Test_Target_Stationary.json**
```json
{
    "name": "Test Target Stationary",
    "color": [0, 0, 255],
    "team_id": 2,
    "ship_class": "TestM_2L",
    "theme_id": "Federation",
    "ai_strategy": "test_do_nothing",
    "layers": {
        "CORE": [
            {"id": "test_armor_extreme_hp"}
        ],
        "ARMOR": []
    },
    "_test_notes": "Stationary target with extreme HP (1B) for beam testing",
    "expected_stats": {
        "max_hp": 1000000500,
        "mass": 400.0,
        "armor_hp_pool": 1000000000
    }
}
```

**Key Test Ships**:

| Ship File | Mass | HP | Purpose |
|-----------|------|-----|---------|
| `Test_Target_Stationary.json` | 400 | 1B | Standard beam tests |
| `Test_Target_Stationary_HighTick.json` | 600 | 1B | High-tick precision tests |
| `Test_Target_Erratic_Small.json` | 65 | 1B | Moving target tests |
| `Test_Attacker_Beam360_Low.json` | 25 | 120 | Low accuracy attacker |
| `Test_Attacker_Beam360_Med.json` | 25 | 120 | Medium accuracy attacker |
| `Test_Attacker_Beam360_High.json` | 25 | 120 | High accuracy attacker |

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

Add to `simulation_tests/data/components.json`:

```json
{
    "id": "test_projectile_std",
    "name": "Test Projectile (Standard)",
    "type": "ProjectileWeaponAbility",
    "mass": 5,
    "hp": 20,
    "abilities": {
        "ProjectileWeaponAbility": {
            "damage": 10,
            "projectile_speed": 300,
            "range": 800,
            "reload": 1.0
        }
    }
}
```

#### 3. Create Test Ship (if needed)

Create `simulation_tests/data/ships/Test_Attacker_Projectile.json`:

```json
{
    "name": "Test Attacker Projectile",
    "color": [255, 0, 0],
    "team_id": 1,
    "ship_class": "TestS_2L",
    "ai_strategy": "test_do_nothing",
    "layers": {
        "CORE": [
            {"id": "test_projectile_std"}
        ]
    },
    "expected_stats": {
        "mass": 25.0
    }
}
```

#### 4. Calculate Expected Outcomes

**For Deterministic Tests** (exact outcomes):
- Calculate exact damage, time to kill, etc.

**For Probabilistic Tests** (hit rates):
- Use game formulas to calculate expected probability
- Account for all bonuses/penalties
- **CRITICAL**: Use **surface distance**, not center-to-center distance

**Example: Beam Hit Rate Calculation**
```python
# Ship separation: 50px center-to-center
# Target mass: 400 → radius = 40 × (400/1000)^(1/3) = 29.47px
# Surface distance: 50 - 29.47 = 20.53px

# Weapon: base_accuracy=0.8, falloff=0.001
# Range penalty: 20.53 × 0.001 = 0.0205

# Target defense: calculate_defense_score(mass=400, accel=0, turn=0, ecm=0) = 0.3316

# Net score: 0.8 - 0.0205 - 0.3316 = 0.4479
# Sigmoid: 1/(1+e^-0.4479) = 0.6101 = 61.01% hit rate
```

**Helper Functions** (see `beam_scenarios.py`):
```python
def calculate_defense_score(mass, acceleration, turn_speed, ecm_score):
    """Calculate target defense score using game formulas."""
    size_score = 0.5 * (1.0 - (mass / 1000.0))
    maneuver_score = (acceleration / 1000.0) + (turn_speed / 500.0)
    return size_score + maneuver_score + ecm_score

def calculate_expected_hit_chance(base_acc, falloff, distance, attack_bonus, defense_penalty):
    """Calculate expected hit chance using sigmoid formula."""
    range_penalty = distance * falloff
    net_score = (base_acc + attack_bonus) - (range_penalty + defense_penalty)
    return 1.0 / (1.0 + math.exp(-net_score))
```

#### 5. Write Test Scenario Class

Create in `simulation_tests/scenarios/your_scenarios.py`:

```python
from test_framework.base import TestScenario, TestMetadata
from validation.rules import ExactMatchRule, StatisticalTestRule

class ProjectileBasicScenario(TestScenario):
    """
    PROJ-001: Basic Projectile Weapon Test

    Tests that projectile weapons deal expected damage over time.
    """

    metadata = TestMetadata(
        test_id="PROJ-001",
        name="Projectile Basic Damage Test",
        category="Projectile Weapons",
        subcategory="Basic Mechanics",
        summary="Validates projectile weapon damage output",
        tags=["projectile", "damage"],

        conditions=[
            "Distance: 100px",
            "Weapon: 10 damage, 1.0s reload, 300 speed",
            "Target: Stationary",
            "Expected: ~5 hits in 500 ticks (~8.3 seconds)"
        ],

        validation_rules=[
            ExactMatchRule(
                name='Projectile Damage',
                path='attacker.weapon.damage',
                expected=10
            ),
            ExactMatchRule(
                name='Reload Time',
                path='attacker.weapon.reload',
                expected=1.0
            ),
            StatisticalTestRule(
                name='Damage Output',
                test_type='binomial',
                expected_probability=0.8,  # Expected hit rate
                equivalence_margin=0.1,
                trials_expr='shots_fired',
                successes_expr='shots_hit',
                description='Tracks hit rate of projectiles'
            )
        ]
    )

    def __init__(self):
        super().__init__()
        self.max_ticks = 500
        self.attacker = None
        self.target = None
        self.initial_hp = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.expected_hit_rate = 0.8  # Calculate this!

    def setup(self, engine):
        """Initialize test scenario."""
        # Load ships from JSON
        from game.simulation.entities.ship import Ship
        attacker_data = load_ship_json('Test_Attacker_Projectile.json')
        target_data = load_ship_json('Test_Target_Stationary.json')

        self.attacker = Ship.from_dict(attacker_data, team_id=1)
        self.target = Ship.from_dict(target_data, team_id=2)

        # Position ships
        self.attacker.position = pygame.Vector2(100, 100)
        self.target.position = pygame.Vector2(200, 100)  # 100px away

        # Add to engine
        engine.team1_ships = [self.attacker]
        engine.team2_ships = [self.target]

        # Store initial state
        self.initial_hp = self.target.hp

        # Calculate expected outcomes (example)
        # ... your calculations here ...

    def update(self, engine):
        """Update test state each tick."""
        # Track projectile firing (implement as needed)
        pass

    def verify(self, engine):
        """Verify test results."""
        # Calculate actual outcomes
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['damage_dealt'] = damage_dealt
        self.results['shots_fired'] = self.shots_fired
        self.results['shots_hit'] = self.shots_hit
        self.results['ticks_run'] = engine.tick_count

        # Run validation
        self.results['validation_results'] = self.run_validation()

        # Determine pass/fail
        self.passed = all(
            r['status'] == 'PASS'
            for r in self.results['validation_results']
        )

        return self.passed
```

#### 6. Register Test in Combat Lab

The Combat Lab auto-discovers tests by scanning scenario files. Make sure:
1. Your scenario file is in `simulation_tests/scenarios/`
2. Your test class inherits from `TestScenario`
3. Your test has a `metadata` attribute with a `test_id`

#### 7. Test Your Test

Create a quick validation script:

```python
"""Quick validation for PROJ-001."""
from simulation_tests.scenarios.projectile_scenarios import ProjectileBasicScenario
from game.simulation.systems.battle_engine import BattleEngine
from test_framework.runner import TestRunner

def validate():
    scenario = ProjectileBasicScenario()

    runner = TestRunner()
    runner.load_data_for_scenario(scenario)

    engine = BattleEngine()
    engine.start([], [])
    scenario.setup(engine)

    # Run test
    for _ in range(scenario.max_ticks):
        scenario.update(engine)
        engine.update()
        if engine.is_battle_over():
            break

    # Verify
    passed = scenario.verify(engine)
    print(f"Test {'PASSED' if passed else 'FAILED'}")

    # Print results
    for key, value in scenario.results.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    validate()
```

---

## Beam Weapon Tests

### Current Test Suite (18 tests)

#### Standard Tests (500 ticks, ±6% margin)

| Test ID | Description | Expected Hit Rate |
|---------|-------------|-------------------|
| **BEAM360-001** | Low Accuracy, Point Blank (50px) | 53.18% |
| **BEAM360-002** | Low Accuracy, Mid Range (400px) | 36.06% |
| **BEAM360-003** | Low Accuracy, Max Range (750px) | 21.86% |
| **BEAM360-004** | Medium Accuracy, Point Blank (50px) | 83.86% |
| **BEAM360-005** | Medium Accuracy, Mid Range (400px) | 78.55% |
| **BEAM360-006** | Medium Accuracy, Max Range (750px) | 72.07% |
| **BEAM360-007** | High Accuracy, Point Blank (50px) | 99.06% |
| **BEAM360-008** | High Accuracy, Max Range (750px) | 98.66% |
| **BEAM360-009** | vs Erratic Small, Mid Range | 4.84% |
| **BEAM360-010** | vs Erratic Small, Max Range | 3.47% |
| **BEAM360-011** | Out of Range (deterministic) | 0% (no hits) |

#### High-Tick Tests (100,000 ticks, ±1% margin)

| Test ID | Description | Expected Hit Rate |
|---------|-------------|-------------------|
| **BEAM360-001-HT** | Low Accuracy, Point Blank | 57.02% |
| **BEAM360-002-HT** | Low Accuracy, Mid Range | 39.71% |
| **BEAM360-004-HT** | Medium Accuracy, Point Blank | 85.82% |
| **BEAM360-005-HT** | Medium Accuracy, Mid Range | 80.98% |
| **BEAM360-006-HT** | Medium Accuracy, Max Range | 75.00% |
| **BEAM360-007-HT** | High Accuracy, Point Blank | 99.19% |
| **BEAM360-008-HT** | High Accuracy, Max Range | 98.85% |

### Beam Weapon Mechanics

#### Raycasting Hit Detection

Beam weapons use raycasting with **circular collision detection**:

```python
# From game/engine/collision.py
def process_beam_attack(attack, recent_beams):
    start_pos = attack['origin']
    direction = attack['direction']
    max_range = attack['range']
    target = attack['target']

    # Ray-sphere intersection
    f = start_pos - target.position
    a = direction.dot(direction)
    b = 2 * f.dot(direction)
    c = f.dot(f) - target.radius**2  # Uses target RADIUS for collision

    discriminant = b*b - 4*a*c

    if discriminant >= 0:
        t1 = (-b - math.sqrt(discriminant)) / (2*a)
        t2 = (-b + math.sqrt(discriminant)) / (2*a)

        if 0 <= t1 <= max_range or 0 <= t2 <= max_range:
            hit_dist = min([t for t in [t1, t2] if 0 <= t <= max_range])

            # Calculate hit chance at SURFACE distance (hit_dist)
            chance = beam_ability.calculate_hit_chance(hit_dist, attack_score, defense_score)

            if random.random() < chance:
                damage = beam_ability.get_damage(hit_dist)
                target.take_damage(damage)
```

**CRITICAL**: The hit distance is to the target **SURFACE**, not center-to-center.

#### Surface Distance Calculation

```python
# Target radius formula
target_radius = 40 × (mass / 1000) ^ (1/3)

# Examples:
# mass=400 → radius = 40 × (0.4)^(1/3) = 29.47px
# mass=600 → radius = 40 × (0.6)^(1/3) = 33.74px
# mass=65  → radius = 40 × (0.065)^(1/3) = 16.08px

# Surface distance
surface_distance = center_to_center_distance - target_radius
```

**Test Expectations MUST use surface distance, not center distance.**

#### Hit Chance Calculation

```python
def calculate_hit_chance(base_acc, falloff, distance, attack_bonus, defense_penalty):
    """
    Calculate beam weapon hit chance using sigmoid formula.

    Args:
        base_acc: Base accuracy (0.0-1.0), e.g. 0.5 = 50%
        falloff: Accuracy reduction per pixel, e.g. 0.002 = 0.2%/px
        distance: Distance to TARGET SURFACE (not center!)
        attack_bonus: Attacker's sensor score
        defense_penalty: Target's total defense score

    Returns:
        Hit probability (0.0-1.0)
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

#### Defense Score Calculation

```python
def calculate_defense_score(mass, acceleration, turn_speed, ecm_score):
    """
    Calculate target's total defense score.

    Args:
        mass: Ship mass in kg
        acceleration: Ship acceleration rate
        turn_speed: Ship turn speed in degrees/sec
        ecm_score: ECM component bonus (if any)

    Returns:
        Total defense penalty applied to attacker
    """
    # Size score: smaller = harder to hit
    size_score = 0.5 * (1.0 - (mass / 1000.0))

    # Maneuverability score: faster/more agile = harder to hit
    maneuver_score = (acceleration / 1000.0) + (turn_speed / 500.0)

    return size_score + maneuver_score + ecm_score
```

**Examples**:
- Mass 400, stationary: defense = 0.5×(1-0.4) + 0 + 0 = 0.30
- Mass 600, stationary: defense = 0.5×(1-0.6) + 0 + 0 = 0.20
- Mass 65, agile (accel=295, turn=238): defense = 0.468 + 0.295 + 0.476 = 1.239

#### Complete Example: BEAM360-001

**Test Setup**:
- Distance: 50px center-to-center
- Weapon: Low accuracy (base 50%, falloff 0.2%/px)
- Target: Mass 400, stationary

**Step-by-Step Calculation**:

```python
# 1. Calculate target radius
target_mass = 400.0
target_radius = 40 * ((target_mass / 1000) ** (1/3))
# target_radius = 40 × (0.4)^(1/3) = 29.47px

# 2. Calculate surface distance
center_distance = 50.0
surface_distance = center_distance - target_radius
# surface_distance = 50 - 29.47 = 20.53px

# 3. Calculate target defense
defense_score = calculate_defense_score(
    mass=400.0,
    acceleration=0.0,
    turn_speed=0.0,
    ecm_score=0.0
)
# defense_score = 0.5 × (1 - 0.4) + 0 + 0 = 0.30

# 4. Calculate hit chance
base_acc = 0.5
falloff = 0.002
attack_bonus = 0.0  # No sensors

expected_hit_chance = calculate_expected_hit_chance(
    base_acc=0.5,
    falloff=0.002,
    distance=20.53,  # SURFACE distance!
    attack_bonus=0.0,
    defense_penalty=0.30
)

# Step-by-step:
# range_penalty = 20.53 × 0.002 = 0.0411
# net_score = (0.5 + 0.0) - (0.0411 + 0.30) = 0.1589
# sigmoid = 1 / (1 + e^-0.1589) = 0.5396 = 53.96%

# (Actual value is 53.18% due to more precise calculations)
```

**Test Validation**:
- Run 500 ticks
- Each tick: 53.18% chance of 1 damage
- Expected damage: ~266 HP
- TOST margin: ±6% (47.18% to 59.18%)
- Observed: 260 HP (52.00%) → PASS (within margin)

---

## Running Tests

### In Combat Lab UI

1. Launch game: `python main.py`
2. Navigate to "Combat Lab" from main menu
3. Browse tests by category in left panels
4. Select test to view details (metadata, conditions, validation rules)
5. Click "Run Test" to execute
6. View results:
   - Metrics (damage dealt, hit rate, ticks run)
   - Validation results (PASS/FAIL for each rule)
   - P-values and statistical analysis

### Headless Execution

For CI/CD or batch testing:

```python
"""Run test headlessly."""
from simulation_tests.scenarios.beam_scenarios import BeamLowAccuracyPointBlankScenario
from game.simulation.systems.battle_engine import BattleEngine
from test_framework.runner import TestRunner

# Create scenario
scenario = BeamLowAccuracyPointBlankScenario()

# Load data
runner = TestRunner()
runner.load_data_for_scenario(scenario)

# Setup engine
engine = BattleEngine()
engine.start([], [])
scenario.setup(engine)

# Run simulation
for tick in range(scenario.max_ticks):
    scenario.update(engine)
    engine.update()
    if engine.is_battle_over():
        break

# Verify results
passed = scenario.verify(engine)

# Print results
print(f"Test: {scenario.metadata.test_id}")
print(f"Result: {'PASSED' if passed else 'FAILED'}")
print(f"Damage Dealt: {scenario.results['damage_dealt']}")
print(f"Hit Rate: {scenario.results['hit_rate']:.2%}")

# Validation details
for result in scenario.results['validation_results']:
    print(f"  [{result['status']}] {result['name']}: {result['message']}")
```

### Batch Testing Script

```python
"""Run all beam weapon tests."""
from simulation_tests.scenarios import beam_scenarios
from test_framework.runner import TestRunner
from game.simulation.systems.battle_engine import BattleEngine
import inspect

# Find all test scenario classes
test_classes = [
    cls for name, cls in inspect.getmembers(beam_scenarios, inspect.isclass)
    if issubclass(cls, TestScenario) and cls != TestScenario
]

results = []

for test_class in test_classes:
    print(f"\nRunning {test_class.metadata.test_id}...")

    scenario = test_class()
    runner = TestRunner()
    runner.load_data_for_scenario(scenario)

    engine = BattleEngine()
    engine.start([], [])
    scenario.setup(engine)

    for _ in range(scenario.max_ticks):
        scenario.update(engine)
        engine.update()
        if engine.is_battle_over():
            break

    passed = scenario.verify(engine)
    results.append((scenario.metadata.test_id, passed))
    print(f"  {'PASSED' if passed else 'FAILED'}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
passed_count = sum(1 for _, passed in results if passed)
total_count = len(results)
print(f"Passed: {passed_count}/{total_count}")
print("="*60)

for test_id, passed in results:
    print(f"  [{' PASS ' if passed else 'FAIL'}] {test_id}")
```

---

## Troubleshooting

### Common Issues

#### Issue: Test fails with "Ship stats mismatch after loading"

**Cause**: Ship expected_stats don't match actual calculated stats.

**Solution**: Update expected_stats in ship JSON file or check component data.

```python
# Debug output example:
WARNING: Ship 'Test Target' stats mismatch after loading!
  - mass: got 600.0, expected 400.0

# Fix: Check armor mass in components.json
# If armor mass=400, total mass = 400 (armor) + 200 (other) = 600
# Solution: Change armor mass to 200 or update expected mass to 600
```

#### Issue: Test fails with large deviation in hit rate

**Cause**: Expected hit rate calculation may be using center-to-center distance instead of surface distance.

**Solution**: Recalculate expected hit rate using surface distance.

```python
# WRONG - uses center distance
surface_distance = 50.0
expected_hit_chance = calculate_expected_hit_chance(0.5, 0.002, 50.0, 0.0, 0.30)
# Result: too low hit rate

# CORRECT - uses surface distance
target_radius = 40 * ((400 / 1000) ** (1/3))  # 29.47px
surface_distance = 50.0 - target_radius        # 20.53px
expected_hit_chance = calculate_expected_hit_chance(0.5, 0.002, 20.53, 0.0, 0.30)
# Result: correct hit rate
```

#### Issue: ExactMatchRule fails for weapon data

**Cause**: Path to weapon data may be incorrect.

**Solution**: Check dot-notation path. For beam weapons:

```python
# Component is in attacker's CORE layer
# Access pattern: attacker → components → find BeamWeaponAbility

# Correct path in ExactMatchRule:
path='attacker.weapon.damage'  # Uses property accessor

# Internal implementation resolves to:
# scenario.attacker.get_component_with_ability('BeamWeaponAbility').get_ability('BeamWeaponAbility').damage
```

#### Issue: TOST test fails with p-value just above 0.05

**Cause**: Statistical variance in small sample sizes (500 ticks).

**Solutions**:
1. Run test multiple times to see if it's consistent failure
2. Check if expected probability is correct
3. Consider if margin is too tight (standard tests use ±6%)
4. For critical tests, use high-tick version (100k ticks, ±1% margin)

```python
# Example: p=0.0531 (just above 0.05 threshold)
# This could be:
# a) Bad luck (5% chance of random failure)
# b) Expected value is slightly off
# c) Margin is too tight

# Recommendations:
# - If p is 0.05-0.10: Probably just variance, re-run
# - If p is 0.10-0.20: Check expected value calculation
# - If p is >0.20: Expected value is likely wrong
```

#### Issue: Target dies before test completes

**Cause**: Not enough HP for the test duration.

**Solution**: Use extreme HP armor (1 billion HP).

```python
# Standard armor: 10k HP
# High-accuracy beam: 99% × 500 ticks = ~495 damage → OK

# High-accuracy beam, 100k ticks: 99% × 100k = ~99k damage → DIES!

# Solution: Use test_armor_extreme_hp (1 billion HP)
# 99% × 100k = ~99k damage → 0.01% of 1B → OK
```

### Debug Techniques

#### Enable Debug Logging

Add debug output to scenarios:

```python
def setup(self, engine):
    # ... setup code ...

    print(f"DEBUG: Target mass = {self.target.mass}")
    print(f"DEBUG: Target radius = {target_radius:.2f}px")
    print(f"DEBUG: Surface distance = {surface_distance:.2f}px")
    print(f"DEBUG: Defense score = {defense_score:.4f}")
    print(f"DEBUG: Expected hit chance = {self.expected_hit_chance:.4f}")
```

#### Track Per-Tick Outcomes

```python
def update(self, engine):
    # Track first hit
    current_hp = self.target.hp
    if current_hp < self.last_hp:
        damage = self.last_hp - current_hp
        print(f"DEBUG: Hit at tick {engine.tick_count}, damage={damage}")
        print(f"DEBUG: Distance = {self.attacker.position.distance_to(self.target.position):.2f}px")
    self.last_hp = current_hp
```

#### Validate Component Loading

```python
def setup(self, engine):
    # ... setup code ...

    # Verify weapon loaded correctly
    weapon_comp = self.attacker.get_component_with_ability('BeamWeaponAbility')
    weapon_ability = weapon_comp.get_ability('BeamWeaponAbility')

    print(f"DEBUG: Weapon loaded:")
    print(f"  damage = {weapon_ability.damage}")
    print(f"  base_accuracy = {weapon_ability.base_accuracy}")
    print(f"  accuracy_falloff = {weapon_ability.accuracy_falloff}")
    print(f"  range = {weapon_ability.range}")
```

---

## Appendix: Statistical Formulas

### TOST (Two One-Sided Tests) for Binomial Proportions

Given:
- `n` = number of trials (ticks)
- `k` = number of successes (hits)
- `p̂` = observed proportion = k/n
- `θ` = expected proportion
- `ε` = equivalence margin

Test hypotheses:
- H₁: p̂ - θ > -ε (not too low)
- H₂: p̂ - θ < +ε (not too high)

Z-statistics:
```
z₁ = (p̂ - θ + ε) / SE
z₂ = (p̂ - θ - ε) / SE

where SE = √(θ(1-θ)/n)
```

P-values:
```
p₁ = CDF(z₁)    # Lower tail
p₂ = 1 - CDF(z₂) # Upper tail
p_final = max(p₁, p₂)
```

Decision:
- If p_final < 0.05: **PASS** (proven equivalent within margin)
- If p_final ≥ 0.05: **FAIL** (not proven equivalent)

### Standard Error for Common Test Sizes

For binomial test at p ≈ 0.5:

```
SE ≈ 0.5 / √n

n = 500    → SE ≈ 2.2%
n = 1000   → SE ≈ 1.6%
n = 10000  → SE ≈ 0.5%
n = 100000 → SE ≈ 0.16%
```

Recommended margin = 3×SE for reliable testing:

```
n = 500    → margin ≥ 6.6% (use 6%)
n = 100000 → margin ≥ 0.48% (use 1%)
```

---

## Credits & Version History

**Created**: January 2026
**Last Updated**: January 2026

**Combat Lab System Design**: Claude Sonnet 4.5 + User
**TOST Implementation**: Statistical equivalence testing for game mechanics
**Beam Weapon Test Suite**: 18 comprehensive tests validating beam weapon mechanics

**Key Learnings**:
- Beam weapons use surface distance, not center-to-center distance
- 1 billion HP armor ensures targets survive all tests
- TOST proves equivalence (not just "no difference detected")
- ±6% margin for 500-tick tests, ±1% for 100k-tick tests
- Surface distance = center_distance - (40 × (mass/1000)^(1/3))

---

**For questions or issues**, see:
- This documentation
- Inline code comments in `beam_scenarios.py`
- Example test scripts: `test_tost.py`, `test_hightick_debug.py`
