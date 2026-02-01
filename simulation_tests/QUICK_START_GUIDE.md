# Combat Lab - Quick Start Guide

## Creating Your First Test in 10 Minutes

This guide walks you through creating a complete test scenario from scratch.

### Prerequisites

- Familiarity with Python
- Basic understanding of the game's combat mechanics
- Access to the Starship Battles codebase

---

## Step 1: Identify What to Test

**Example**: Let's test a low accuracy beam weapon at point-blank range (50px).

**Expected Behavior**:
- Weapon: 0.5 base accuracy, 0.002/px falloff
- Distance: 50px center-to-center
- Target: Stationary, mass 400
- Should hit around 53% of the time

---

## Step 2: Check if Components Exist

Look in `simulation_tests/data/components.json`:

```bash
# Search for beam weapon
grep -A 10 "test_beam_low_acc" simulation_tests/data/components.json
```

**Found** (values from `test_constants.py`):
```json
{
    "id": "test_beam_low_acc_1dmg",
    "abilities": {
        "BeamWeaponAbility": {
            "damage": 1,
            "base_accuracy": 0.5,
            "accuracy_falloff": 0.002,
            "range": 800
        }
    }
}
```

Component exists, no need to create a new one.

---

## Step 3: Calculate Expected Outcome

Use the actual game formulas:

```python
import math

# Target configuration
target_mass = 400.0
target_radius = 40 * ((target_mass / 1000) ** (1/3))
# target_radius = 29.47px

# Distance (surface, not center!)
center_distance = 50.0
surface_distance = center_distance - target_radius
# surface_distance = 20.53px

# Defense score (LOGARITHMIC formula from ship_stats.py)
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

defense_score = calculate_defense_score(400.0, 0.0, 0.0, 0.0)
# defense_score = 0.3316 (approximately)

# Hit chance calculation
base_acc = 0.5
falloff = 0.002
range_penalty = surface_distance * falloff
# range_penalty = 20.53 * 0.002 = 0.0411

net_score = (base_acc + 0.0) - (range_penalty + defense_score)
# net_score = 0.5 - 0.0411 - 0.3316 = 0.1273

expected_hit_chance = 1.0 / (1.0 + math.exp(-net_score))
# expected_hit_chance = 0.5318 = 53.18%
```

**Result**: Expected hit rate = **53.18%**

---

## Step 4: Create Test Scenario Class

Create file: `simulation_tests/scenarios/my_test_scenarios.py`

```python
"""My custom test scenarios."""
import math
import pygame
from simulation_tests.scenarios.base import TestScenario, TestMetadata
from simulation_tests.scenarios.validation import ExactMatchRule, StatisticalTestRule
from simulation_tests.test_constants import (
    STANDARD_TEST_TICKS,
    STANDARD_MARGIN,
    STANDARD_SEED,
    BEAM_LOW_ACCURACY,
    BEAM_LOW_FALLOFF,
    BEAM_LOW_RANGE,
    BEAM_LOW_DAMAGE,
    STATIONARY_TARGET_MASS
)


class MyBeamPointBlankTest(TestScenario):
    """
    MYTEST-001: Low Accuracy Beam at Point-Blank Range

    Tests beam weapon hit chance at point-blank range.
    """

    metadata = TestMetadata(
        test_id="MYTEST-001",
        name="Low Accuracy Beam - Point Blank (50px)",
        category="My Tests",
        subcategory="Beam Weapons",
        summary="Tests low accuracy beam at 50px distance",
        tags=["beam", "accuracy", "point-blank", "custom"],

        conditions=[
            "Distance: 50px center-to-center (20.53px to surface)",
            "Weapon: Low Accuracy Beam (base 0.5, falloff 0.002/px)",
            "Target: Stationary, Mass 400",
            "Expected Hit Rate: 53.18%"
        ],

        edge_cases=["Minimal range penalty at close range"],
        expected_outcome="Hit rate ~53% with damage > 0",
        pass_criteria="damage_dealt > 0",

        max_ticks=STANDARD_TEST_TICKS,  # 500
        seed=STANDARD_SEED,             # 42
        battle_end_mode="time_based",

        validation_rules=[
            # Component data verification
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=BEAM_LOW_DAMAGE
            ),
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=BEAM_LOW_ACCURACY
            ),
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=BEAM_LOW_FALLOFF
            ),
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=BEAM_LOW_RANGE
            ),
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=STATIONARY_TARGET_MASS
            ),

            # Statistical validation (TOST)
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.5318,
                equivalence_margin=STANDARD_MARGIN,  # ±6%
                trials_expr='ticks_run',
                successes_expr='damage_dealt',
                description='Each beam hit = 1 damage'
            )
        ]
    )

    def setup(self, battle_engine):
        """Initialize test scenario."""
        # Load ships using helper method
        self.attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        self.target = self._load_ship('Test_Target_Stationary.json')

        # Position ships
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.target.position = pygame.math.Vector2(50, 0)  # 50px away

        # Start battle
        battle_engine.start(
            [self.attacker],
            [self.target],
            seed=self.metadata.seed
        )

        # Store initial state
        self.initial_hp = self.target.hp

    def verify(self, battle_engine) -> bool:
        """Verify test results."""
        # Calculate actual outcomes
        self.damage_dealt = self.initial_hp - self.target.hp
        ticks_run = battle_engine.tick_counter

        # Store results (required for validation)
        self.results['damage_dealt'] = self.damage_dealt
        self.results['ticks_run'] = ticks_run
        self.results['hit_rate'] = self.damage_dealt / ticks_run if ticks_run > 0 else 0
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp

        # Run automatic validation
        self.run_validation(battle_engine)

        # Pass if any damage was dealt
        return self.damage_dealt > 0
```

---

## Step 5: Run Your Test

### Option A: Using TestRunner (Recommended)

```python
from simulation_tests.scenarios.my_test_scenarios import MyBeamPointBlankTest
from test_framework.runner import TestRunner

runner = TestRunner()
scenario = runner.run_scenario(MyBeamPointBlankTest, headless=True)

print(f"Test: {scenario.metadata.test_id}")
print(f"Result: {'PASSED' if scenario.passed else 'FAILED'}")
print(f"Damage Dealt: {scenario.results['damage_dealt']}")
print(f"Hit Rate: {scenario.results['hit_rate']:.2%}")
```

### Option B: In Combat Lab UI

1. Launch game: `python main.py`
2. Navigate to "Combat Lab"
3. Look for "My Tests" category
4. Select "MYTEST-001"
5. Click "Run Headless" or "Run Visual"
6. View results

---

## Test Auto-Discovery

The `TestRegistry` automatically scans `simulation_tests/scenarios/` and registers all `TestScenario` subclasses that have a `metadata` attribute. Your test will appear in Combat Lab immediately.

---

## Common Pitfalls to Avoid

### Mistake 1: Using Center Distance

```python
# WRONG
surface_distance = 50.0  # Center-to-center
expected_hit_chance = calculate(...)  # FAILS!

# CORRECT
target_radius = 40 * ((400 / 1000) ** (1/3))  # 29.47px
surface_distance = 50.0 - target_radius       # 20.53px
expected_hit_chance = calculate(...)          # PASSES!
```

### Mistake 2: Wrong Defense Formula

```python
# WRONG (old linear formula)
defense_score = 0.5 * (1.0 - (mass / 1000.0))

# CORRECT (logarithmic formula from ship_stats.py)
radius = 40 * ((mass / 1000) ** (1/3))
diameter = radius * 2
d_ratio = max(0.1, diameter / 80.0)
size_score = -2.5 * math.log10(d_ratio)
```

### Mistake 3: Not Storing Results

```python
def verify(self, battle_engine):
    damage_dealt = self.initial_hp - self.target.hp
    # WRONG: Forgot to store!
    self.run_validation(battle_engine)  # FAILS - validation needs results

    # CORRECT: Store results first
    self.results['damage_dealt'] = damage_dealt
    self.results['ticks_run'] = battle_engine.tick_counter
    self.run_validation(battle_engine)  # Now works
```

### Mistake 4: Wrong Imports

```python
# WRONG
from test_framework.base import TestScenario, TestMetadata
from validation.rules import ExactMatchRule

# CORRECT
from simulation_tests.scenarios.base import TestScenario, TestMetadata
from simulation_tests.scenarios.validation import ExactMatchRule, StatisticalTestRule
```

### Mistake 5: Margin Too Tight

```python
# WRONG - ±1% margin with only 500 ticks (SE ≈ 2.2%)
StatisticalTestRule(
    expected_probability=0.5318,
    equivalence_margin=0.01,  # Too tight, will fail randomly
)

# CORRECT - ±6% margin for 500 ticks
StatisticalTestRule(
    expected_probability=0.5318,
    equivalence_margin=0.06,  # 3× SE, reliable
)
```

---

## Understanding TOST Validation

Combat Lab uses TOST (Two One-Sided Tests) equivalence testing:

- **Traditional testing**: Proves things are different (p < 0.05 = different)
- **TOST testing**: Proves things are equivalent (p < 0.05 = equivalent)

**Interpretation**:
- `p < 0.05` = **PASS** (proven equivalent within margin)
- `p >= 0.05` = **FAIL** (not proven equivalent)

---

## Constants Reference

Use constants from `simulation_tests/test_constants.py`:

```python
# Test durations
STANDARD_TEST_TICKS = 500
HIGH_TICK_TEST_TICKS = 100000

# Distances
POINT_BLANK_DISTANCE = 50
MID_RANGE_DISTANCE = 400

# Beam weapons
BEAM_LOW_ACCURACY = 0.5
BEAM_LOW_FALLOFF = 0.002
BEAM_LOW_RANGE = 800
BEAM_LOW_DAMAGE = 1

# Margins
STANDARD_MARGIN = 0.06      # ±6% for 500-tick tests
HIGH_PRECISION_MARGIN = 0.01 # ±1% for 100k-tick tests

# Seeds
STANDARD_SEED = 42
```

---

## Next Steps

### Create a High-Tick Version

For precise validation, create a 100k-tick variant:

```python
class MyBeamPointBlankHighTickTest(TestScenario):
    """MYTEST-001-HT: High-tick version."""

    metadata = TestMetadata(
        test_id="MYTEST-001-HT",
        name="Low Accuracy Beam - Point Blank [100k Ticks]",
        # ... same settings ...
        max_ticks=HIGH_TICK_TEST_TICKS,  # 100,000

        validation_rules=[
            # ... same ExactMatchRules ...
            StatisticalTestRule(
                name='Hit Rate',
                test_type='binomial',
                expected_probability=0.5318,
                equivalence_margin=HIGH_PRECISION_MARGIN,  # ±1%
                trials_expr='ticks_run',
                successes_expr='damage_dealt'
            )
        ]
    )
```

### Create Tests for Other Weapons

Apply the same pattern to projectiles, seekers, etc.

### Create Resource System Tests

Resource tests validate consumption, depletion, and regeneration:

```python
class MyFuelConsumptionTest(TestScenario):
    """RESOURCE-XXX: Custom fuel consumption test."""

    metadata = TestMetadata(
        test_id="RESOURCE-XXX",
        name="Custom Fuel Consumption Test",
        category="Resource System",
        subcategory="Fuel",
        summary="Tests engine fuel consumption rate",
        conditions=[
            "Ship: Test_Engine_FuelConsumption.json",
            "Fuel Consumption: 1.0 per second",
            "Initial Fuel: 1000 units",
            "Duration: 500 ticks (5 seconds)"
        ],
        expected_outcome="Fuel decreases by 5.0 units",
        pass_criteria="final_fuel ≈ 995.0",
        max_ticks=500,
        seed=42,
        battle_end_mode="time_based",
        tags=["resource", "fuel", "consumption"]
    )

    def setup(self, battle_engine):
        ship = self._load_ship("Test_Engine_FuelConsumption.json")
        ship.position = pygame.math.Vector2(0, 0)
        self.initial_fuel = ship.resources.get_value('fuel')

        end_condition = self._create_end_condition()
        battle_engine.start([ship], [], seed=self.metadata.seed,
                           end_condition=end_condition)
        ship.engine_throttle = 1.0
        self.ship = ship

    def verify(self, battle_engine) -> bool:
        final_fuel = self.ship.resources.get_value('fuel')
        fuel_consumed = self.initial_fuel - final_fuel

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_fuel'] = self.initial_fuel
        self.results['final_fuel'] = final_fuel
        self.results['fuel_consumed'] = fuel_consumed
        self.results['expected_fuel_consumed'] = 5.0  # 1.0/sec × 5 sec

        # Pass if fuel consumed is close to expected
        return abs(fuel_consumed - 5.0) < 0.5
```

See `simulation_tests/scenarios/resource_scenarios.py` for complete examples.

### Use Templates

See `simulation_tests/scenarios/templates.py` for reusable base classes like `StaticTargetScenario`.

---

## Resources

- **[Main Documentation](COMBAT_LAB_DOCUMENTATION.md)** - Complete system reference
- **[README](README.md)** - Documentation hub
- **[test_constants.py](test_constants.py)** - Centralized constants
- **[beam_scenarios.py](scenarios/beam_scenarios.py)** - Working examples

---

## Getting Help

If tests fail unexpectedly:

1. **Check surface distance** - Not center-to-center!
2. **Verify defense formula** - Use logarithmic, not linear
3. **Check imports** - Use `simulation_tests.scenarios.*`
4. **Verify margin** - ±6% for 500 ticks, ±1% for 100k
5. **Run multiple times** - 5% chance of random failure
6. **Consult examples** - See `beam_scenarios.py`
