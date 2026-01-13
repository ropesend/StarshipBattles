# Quick Start: Creating Your First TestScenario

This guide will walk you through creating your first test scenario in 5 minutes.

## Step 1: Understand the Pattern

TestScenarios work in both pytest (headless) and Combat Lab (visual) using the EXACT same code.

```python
from simulation_tests.scenarios import TestScenario, TestMetadata

class MyTest(TestScenario):
    metadata = TestMetadata(...)  # Describes the test

    def setup(self, battle_engine):
        # Load ships and position them
        pass

    def verify(self, battle_engine):
        # Return True if test passed
        return True
```

## Step 2: Create Your Scenario File

Create a new file in `simulation_tests/scenarios/`:

**File**: `simulation_tests/scenarios/my_first_test.py`

```python
"""
My First Test Scenario

This test validates that a beam weapon can damage a target.
"""

import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata


class MyFirstBeamTest(TestScenario):
    """My first test scenario."""

    metadata = TestMetadata(
        test_id="MY-001",
        category="MyTests",
        subcategory="Beam Tests",
        name="My first beam test",
        summary="Tests that a beam weapon can damage a target",
        conditions=["Distance: 100px", "Stationary target"],
        edge_cases=["Basic functionality"],
        expected_outcome="Target takes damage",
        pass_criteria="Damage > 0",
        max_ticks=500,
        seed=42,
        tags=["beginner", "beam"]
    )

    def setup(self, battle_engine):
        """Setup the test."""
        # Load ships
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')

        # Position ships 100px apart
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0  # Facing right
        target.position = pygame.math.Vector2(100, 0)
        target.angle = 0

        # Store initial HP
        self.initial_hp = target.hp

        # Start battle with fixed seed
        battle_engine.start([attacker], [target], seed=self.metadata.seed)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Called every tick - make attacker fire."""
        self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine):
        """Check if test passed."""
        # Calculate damage
        damage = self.initial_hp - self.target.hp

        # Store results
        self.results['damage_dealt'] = damage
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp

        # Test passes if damage > 0
        return damage > 0
```

## Step 3: Verify Discovery

Check that your scenario is discovered:

```bash
python -c "from test_framework.registry import TestRegistry; TestRegistry().print_summary()"
```

You should see:

```
MyTests
--------------------------------------------------------------------------------

  Beam Tests:
    MY-001: My first beam test
        Tests that a beam weapon can damage a target
```

## Step 4: Create Pytest Wrapper

Create `simulation_tests/tests/test_my_first_test.py`:

```python
"""
My First Test (Pytest Wrapper)
"""

import pytest
from test_framework.runner import TestRunner
from simulation_tests.scenarios.my_first_test import MyFirstBeamTest


@pytest.mark.simulation
class TestMyFirst:
    """My first test using TestScenario."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        self.runner = TestRunner()

    def test_MY_001_my_first_beam_test(self):
        """MY-001: My first beam test."""
        scenario = self.runner.run_scenario(MyFirstBeamTest, headless=True)
        assert scenario.passed, f"Test failed: {scenario.results}"
```

## Step 5: Run the Test

```bash
pytest simulation_tests/tests/test_my_first_test.py -v
```

You should see:

```
test_my_first_test.py::TestMyFirst::test_MY_001_my_first_beam_test PASSED
```

## Next Steps

### Try Different Scenarios

1. **Different Distances**: Test at 50px, 200px, 500px
2. **Different Weapons**: Use projectile or seeker weapons
3. **Moving Targets**: Load 'Test_Target_Erratic_Small.json'
4. **Multiple Ships**: Add more attackers or targets

### Explore Available Ships

Check what test ships are available:

```bash
ls simulation_tests/data/ships/
```

You'll see:
- `Test_Attacker_Beam360_Low.json` - Low accuracy beam
- `Test_Attacker_Beam360_Med.json` - Medium accuracy beam
- `Test_Attacker_Beam360_High.json` - High accuracy beam
- `Test_Attacker_Proj360.json` - Projectile weapon
- `Test_Attacker_Seeker360.json` - Seeker weapon
- `Test_Target_Stationary.json` - Stationary target
- `Test_Target_Erratic_Small.json` - Moving target

### Read the Full Guide

See `docs/test_migration_guide.md` for:
- Complete examples
- Common patterns
- Best practices
- Troubleshooting

### Look at Examples

Study `simulation_tests/scenarios/example_beam_test.py` for a complete working example.

## Common Mistakes

### 1. Forgetting to Set Seed

```python
# Bad - non-deterministic
battle_engine.start([attacker], [target])

# Good - deterministic
battle_engine.start([attacker], [target], seed=self.metadata.seed)
```

### 2. Not Storing Initial State

```python
# Bad - can't verify damage
def verify(self, battle_engine):
    return self.target.hp < ???  # What was initial HP?

# Good - stored in setup
def setup(self, battle_engine):
    self.initial_hp = target.hp

def verify(self, battle_engine):
    return self.target.hp < self.initial_hp
```

### 3. Not Storing Results

```python
# Bad - no details on failure
def verify(self, battle_engine):
    return damage > 0

# Good - store details
def verify(self, battle_engine):
    damage = self.initial_hp - self.target.hp
    self.results['damage_dealt'] = damage
    self.results['hit_rate'] = hits / shots
    return damage > 0
```

## Tips

1. **Start Simple**: Begin with a basic test and add complexity gradually
2. **Use Fixed Seeds**: Always use fixed seeds for reproducibility
3. **Store Everything**: Store initial values and results for debugging
4. **Clear Metadata**: Write clear descriptions and pass criteria
5. **Test in Pytest First**: Verify in pytest before trying in Combat Lab

## Help

If you get stuck:
1. Check `simulation_tests/scenarios/example_beam_test.py`
2. Read `docs/test_migration_guide.md`
3. Look at `simulation_tests/scenarios/README.md`
4. Check existing tests in `simulation_tests/tests/`

## Summary

Creating a TestScenario involves:
1. Define TestMetadata describing the test
2. Implement setup() to configure ships
3. Implement verify() to check results
4. Optionally implement update() for per-tick logic
5. Create pytest wrapper to run the scenario

That's it! Your test now works in both pytest (headless) and Combat Lab (visual).
