# Combat Lab - Quick Start Guide

## Creating Your First Test in 10 Minutes

This guide walks you through creating a complete test scenario from scratch.

### Prerequisites

- Familiarity with Python
- Basic understanding of the game's combat mechanics
- Access to the Starship Battles codebase

---

## Step 1: Identify What to Test (1 minute)

**Example**: Let's test a medium accuracy beam weapon at mid-range (400px).

**Expected Behavior**:
- Weapon: 80% base accuracy, 0.1%/px falloff
- Distance: 400px center-to-center
- Target: Stationary, mass 400
- Should hit around 40-45% of the time

---

## Step 2: Check if Components Exist (1 minute)

Look in `simulation_tests/data/components.json`:

```bash
# Search for beam weapon
grep -A 10 "test_beam_med_acc" simulation_tests/data/components.json
```

**Found**:
```json
{
    "id": "test_beam_med_acc_1dmg",
    "abilities": {
        "BeamWeaponAbility": {
            "damage": 1,
            "base_accuracy": 0.8,
            "accuracy_falloff": 0.001,
            "range": 800
        }
    }
}
```

✓ Component exists, no need to create new one.

---

## Step 3: Calculate Expected Outcome (3 minutes)

```python
import math

# Target configuration
target_mass = 400.0
target_radius = 40 * ((target_mass / 1000) ** (1/3))
# target_radius = 29.47px

# Distance
center_distance = 400.0
surface_distance = center_distance - target_radius
# surface_distance = 370.53px

# Target defense (stationary)
size_score = 0.5 * (1.0 - (target_mass / 1000.0))
# size_score = 0.5 * 0.6 = 0.30
maneuver_score = 0.0  # Stationary
defense_score = size_score + maneuver_score
# defense_score = 0.30

# Weapon accuracy
base_acc = 0.8
falloff = 0.001
attack_bonus = 0.0  # No sensors

range_penalty = surface_distance * falloff
# range_penalty = 370.53 * 0.001 = 0.3705

net_score = (base_acc + attack_bonus) - (range_penalty + defense_score)
# net_score = 0.8 - 0.3705 - 0.30 = 0.1295

expected_hit_chance = 1.0 / (1.0 + math.exp(-net_score))
# expected_hit_chance = 1/(1+e^-0.1295) = 0.5323 = 53.23%
```

**Result**: Expected hit rate ≈ **53.23%**

---

## Step 4: Create Test Scenario Class (3 minutes)

Create file: `simulation_tests/scenarios/my_test_scenarios.py`

```python
"""My custom test scenarios."""
import math
import pygame
from test_framework.base import TestScenario, TestMetadata
from validation.rules import ExactMatchRule, StatisticalTestRule
from game.simulation.entities.ship import Ship
import json
from pathlib import Path


def load_ship_json(filename):
    """Load ship JSON from data/ships/ directory."""
    ship_path = Path(__file__).parent.parent / 'data' / 'ships' / filename
    with open(ship_path, 'r') as f:
        return json.load(f)


class MyMediumBeamMidRangeTest(TestScenario):
    """
    MY-TEST-001: Medium Accuracy Beam at Mid-Range

    Tests beam weapon hit chance at mid-range with medium accuracy.
    """

    metadata = TestMetadata(
        test_id="MY-TEST-001",
        name="Medium Accuracy Beam - Mid Range (400px)",
        category="My Tests",
        subcategory="Beam Weapons",
        summary="Tests medium accuracy beam at 400px distance",
        tags=["beam", "accuracy", "mid-range", "custom"],

        conditions=[
            "Distance: 400px center-to-center (370.53px to surface)",
            "Weapon: Medium Accuracy Beam (base 80%, falloff 0.1%/px)",
            "Target: Stationary, Mass 400, Defense 0.30",
            "Expected Hit Rate: 53.23%"
        ],

        validation_rules=[
            # Component data verification
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=1
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=0.8
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=0.001
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=800
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0
            ),

            # Statistical validation
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.5323,  # From calculation above
                equivalence_margin=0.06,      # ±6% for 500 ticks
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage, so damage_dealt = hit count'
            )
        ]
    )

    def __init__(self):
        super().__init__()
        self.max_ticks = 500
        self.attacker = None
        self.target = None
        self.initial_hp = 0
        self.expected_hit_chance = 0.5323

    def setup(self, engine):
        """Initialize test scenario."""
        # Load ships
        attacker_data = load_ship_json('Test_Attacker_Beam360_Med.json')
        target_data = load_ship_json('Test_Target_Stationary.json')

        self.attacker = Ship.from_dict(attacker_data, team_id=1)
        self.target = Ship.from_dict(target_data, team_id=2)

        # Position ships
        self.attacker.position = pygame.Vector2(100, 100)
        self.target.position = pygame.Vector2(500, 100)  # 400px away

        # Set attacker to face target
        self.attacker.current_target = self.target
        direction = (self.target.position - self.attacker.position).normalize()
        self.attacker.direction = direction

        # Add to engine
        engine.team1_ships = [self.attacker]
        engine.team2_ships = [self.target]

        # Store initial state
        self.initial_hp = self.target.hp

    def update(self, engine):
        """Update test state each tick."""
        # Keep attacker aimed at target
        if self.attacker.is_alive and self.target.is_alive:
            direction = (self.target.position - self.attacker.position).normalize()
            self.attacker.direction = direction

    def verify(self, engine):
        """Verify test results."""
        # Calculate actual outcomes
        damage_dealt = self.initial_hp - self.target.hp
        ticks_run = min(engine.tick_count, self.max_ticks)
        hit_rate = damage_dealt / ticks_run if ticks_run > 0 else 0

        # Store results
        self.results['damage_dealt'] = damage_dealt
        self.results['hit_rate'] = hit_rate
        self.results['ticks_run'] = ticks_run
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp

        # Run validation
        self.results['validation_results'] = self.run_validation()

        # Determine pass/fail
        self.passed = all(
            r['status'] == 'PASS'
            for r in self.results['validation_results']
        )

        return self.passed
```

---

## Step 5: Create Validation Script (2 minutes)

Create file: `test_my_scenario.py` in project root:

```python
"""Quick validation for MY-TEST-001."""
import sys
from simulation_tests.scenarios.my_test_scenarios import MyMediumBeamMidRangeTest
from game.simulation.systems.battle_engine import BattleEngine
from test_framework.runner import TestRunner


def validate():
    print("="*80)
    print("VALIDATING: MY-TEST-001")
    print("="*80)

    # Create scenario
    scenario = MyMediumBeamMidRangeTest()

    # Load data
    runner = TestRunner()
    runner.load_data_for_scenario(scenario)

    # Setup engine
    engine = BattleEngine()
    engine.start([], [])
    scenario.setup(engine)

    # Print configuration
    print(f"Test ID: {scenario.metadata.test_id}")
    print(f"Max ticks: {scenario.max_ticks}")
    print(f"Attacker: {scenario.attacker.name}, Mass: {scenario.attacker.mass}")
    print(f"Target: {scenario.target.name}, Mass: {scenario.target.mass}")
    print(f"Expected Hit Chance: {scenario.expected_hit_chance:.4f} ({scenario.expected_hit_chance*100:.2f}%)")

    # Run simulation
    print(f"\nRunning {scenario.max_ticks} ticks...")
    for tick in range(scenario.max_ticks):
        scenario.update(engine)
        engine.update()
        if engine.is_battle_over():
            print(f"Battle ended early at tick {tick}")
            break

    # Verify results
    passed = scenario.verify(engine)

    # Print results
    print(f"\nTest Result: {'PASSED' if passed else 'FAILED'}")
    print(f"\nMetrics:")
    print(f"  Damage Dealt: {scenario.results['damage_dealt']}")
    print(f"  Hit Rate: {scenario.results['hit_rate']:.4f} ({scenario.results['hit_rate']*100:.2f}%)")
    print(f"  Expected: {scenario.expected_hit_chance:.4f} ({scenario.expected_hit_chance*100:.2f}%)")

    print(f"\nValidation Results:")
    for result in scenario.results['validation_results']:
        status = "[PASS]" if result['status'] == 'PASS' else "[FAIL]"
        print(f"  {status} {result['name']}")
        print(f"    {result['message']}")
        if result['p_value'] is not None:
            print(f"    P-value: {result['p_value']:.4f}")

    return passed


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
```

---

## Step 6: Run Your Test

```bash
python test_my_scenario.py
```

**Expected Output**:
```
================================================================================
VALIDATING: MY-TEST-001
================================================================================
Test ID: MY-TEST-001
Max ticks: 500
Attacker: Test Attacker Beam360 Med, Mass: 25.0
Target: Test Target Stationary, Mass: 400.0
Expected Hit Chance: 0.5323 (53.23%)

Running 500 ticks...

Test Result: PASSED

Metrics:
  Damage Dealt: 267
  Hit Rate: 0.5340 (53.40%)
  Expected: 0.5323 (53.23%)

Validation Results:
  [PASS] Beam Weapon Damage
    Expected: 1, Actual: 1, Difference: 0.0
  [PASS] Base Accuracy
    Expected: 0.8, Actual: 0.8, Difference: 0.0
  [PASS] Accuracy Falloff
    Expected: 0.001, Actual: 0.001, Difference: 0.0
  [PASS] Weapon Range
    Expected: 800, Actual: 800, Difference: 0.0
  [PASS] Target Mass
    Expected: 400.0, Actual: 400.0, Difference: 0.0
  [PASS] Hit Rate
    Hit rate 53.40% equivalent to expected 53.23% within ±6.00% (p=0.0234)
    P-value: 0.0234
```

✅ **Success!** Your test is working correctly.

---

## Step 7: Run in Combat Lab UI

1. Launch game: `python main.py`
2. Navigate to "Combat Lab"
3. Look for "My Tests" category
4. Select "MY-TEST-001"
5. Click "Run Test"
6. View results in UI

---

## Common Pitfalls to Avoid

### ❌ Mistake 1: Using Center Distance

```python
# WRONG
surface_distance = 400.0
expected_hit_chance = calculate_hit_chance(..., 400.0, ...)

# Result: Expected hit rate too low, test FAILS
```

**Fix**: Always subtract target radius
```python
# CORRECT
target_radius = 40 * ((400 / 1000) ** (1/3))  # 29.47px
surface_distance = 400.0 - target_radius       # 370.53px
expected_hit_chance = calculate_hit_chance(..., 370.53, ...)
```

### ❌ Mistake 2: Forgetting to Store Results

```python
def verify(self, engine):
    damage_dealt = self.initial_hp - self.target.hp
    # Forgot to store!
    self.results['validation_results'] = self.run_validation()  # FAILS
```

**Fix**: Store all metrics before validation
```python
def verify(self, engine):
    damage_dealt = self.initial_hp - self.target.hp
    self.results['damage_dealt'] = damage_dealt  # Store it!
    self.results['ticks_run'] = engine.tick_count
    self.results['validation_results'] = self.run_validation()  # Now works
```

### ❌ Mistake 3: Wrong trials/successes Expression

```python
StatisticalTestRule(
    trials_expr='ticks_run',     # 500
    successes_expr='hit_rate'    # 0.5340 (float, not count!)
)
# FAILS - binomial test expects INTEGER count
```

**Fix**: Use damage_dealt (count)
```python
StatisticalTestRule(
    trials_expr='ticks_run',        # 500
    successes_expr='damage_dealt'   # 267 (count)
)
```

### ❌ Mistake 4: Margin Too Tight

```python
StatisticalTestRule(
    expected_probability=0.5323,
    equivalence_margin=0.01,  # ±1% with only 500 ticks
    trials_expr='ticks_run'   # SE ≈ 2.2%, margin < 3×SE
)
# Test may fail due to random variance
```

**Fix**: Use appropriate margin
```python
StatisticalTestRule(
    expected_probability=0.5323,
    equivalence_margin=0.06,  # ±6% for 500 ticks
    trials_expr='ticks_run'
)
```

---

## Next Steps

### Create a High-Tick Version

Add high-precision validation with 100k ticks:

```python
class MyMediumBeamMidRangeHighTickTest(TestScenario):
    """MY-TEST-001-HT: High-tick version of MY-TEST-001."""

    metadata = TestMetadata(
        test_id="MY-TEST-001-HT",
        name="Medium Accuracy Beam - Mid Range [100k Ticks]",
        # ... same category/subcategory ...
        tags=["beam", "accuracy", "mid-range", "custom", "high-tick", "precision"],

        # Update ship to use high-tick target
        conditions=[
            "Ship: Test_Target_Stationary_HighTick.json (mass 600)",
            # ... recalculate expected hit rate for mass 600 ...
        ],

        validation_rules=[
            # Same 5 ExactMatchRules...
            ExactMatchRule(name='Target Mass', path='target.mass', expected=600.0),  # Changed

            # Tighter margin for high sample count
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.4571,  # Recalculated for mass 600
                equivalence_margin=0.01,      # ±1% for 100k ticks
                trials_expr='ticks_run',
                successes_expr='damage_dealt'
            )
        ]
    )

    def __init__(self):
        super().__init__()
        self.max_ticks = 100000  # 100k ticks!
        # ... rest same as standard test ...
```

**Recalculation for mass 600**:
```python
target_mass = 600.0
target_radius = 40 * ((600 / 1000) ** (1/3))  # 33.74px
surface_distance = 400.0 - 33.74               # 366.26px

defense_score = 0.5 * (1.0 - 0.6)             # 0.20 (smaller penalty)
range_penalty = 366.26 * 0.001                # 0.3663

net_score = 0.8 - 0.3663 - 0.20               # 0.2337
expected_hit_chance = 1/(1+exp(-0.2337))      # 0.5582 = 55.82%
```

### Create Tests for Other Weapons

Apply same pattern to projectile weapons, missiles, etc.

### Add Edge Case Tests

- Out of range (deterministic, no StatisticalTestRule)
- Zero defense target
- Maximum defense target
- Multiple weapons firing

---

## Templates

### Projectile Weapon Test Template

```python
class MyProjectileTest(TestScenario):
    """Projectile weapon test template."""

    def __init__(self):
        super().__init__()
        self.max_ticks = 1000  # Longer for projectile travel time
        self.projectiles_fired = 0
        self.projectiles_hit = 0

    def update(self, engine):
        """Track projectiles."""
        # Implement projectile tracking
        # Count projectiles_fired and projectiles_hit

    def verify(self, engine):
        damage_dealt = self.initial_hp - self.target.hp

        self.results['damage_dealt'] = damage_dealt
        self.results['projectiles_fired'] = self.projectiles_fired
        self.results['projectiles_hit'] = self.projectiles_hit
        self.results['ticks_run'] = engine.tick_count

        # StatisticalTestRule uses projectiles_fired/hit
        self.results['validation_results'] = self.run_validation()
        self.passed = all(r['status'] == 'PASS' for r in self.results['validation_results'])
        return self.passed
```

---

## Resources

- **Main Documentation**: `simulation_tests/COMBAT_LAB_DOCUMENTATION.md`
- **Test Framework**: `test_framework/README.md`
- **Validation System**: `simulation_tests/validation/README.md`
- **Data Files**: `simulation_tests/data/README.md`
- **Example Tests**: `simulation_tests/scenarios/beam_scenarios.py`

---

## Getting Help

If tests fail unexpectedly:

1. **Check expected value calculation** - Most common issue
2. **Verify surface distance** - Not center-to-center!
3. **Print debug info** - Add print statements in setup()
4. **Run multiple times** - 5% chance of random failure
5. **Check component data** - ExactMatchRule failures indicate mismatch
6. **Consult documentation** - Detailed troubleshooting in COMBAT_LAB_DOCUMENTATION.md

**Happy Testing!** 🚀
