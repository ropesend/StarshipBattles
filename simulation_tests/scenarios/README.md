# Test Scenarios Directory

This directory contains **TestScenario** subclasses that define reproducible test cases for the Starship Battles combat simulator.

## Purpose

TestScenarios work identically in both:
- **pytest** (headless, automated testing)
- **Combat Lab** (visual, interactive debugging)

This ensures that automated tests and visual debugging use the exact same simulation logic.

## Structure

```
simulation_tests/scenarios/
    base.py              # TestScenario base class and TestMetadata
    __init__.py          # Exports TestScenario and TestMetadata
    example_beam_test.py # Example scenario demonstrating the pattern

    # Future scenario files:
    beam_accuracy.py     # BEAM360-001 through BEAM360-011
    projectile_damage.py # PROJ360-001 through PROJ360-010
    seeker_tracking.py   # SEEK360-001 through SEEK360-008
    # ... more scenarios
```

## Creating a New Scenario

### 1. Define TestMetadata

```python
from simulation_tests.scenarios import TestMetadata

metadata = TestMetadata(
    test_id="BEAM-001",           # Unique identifier
    category="Weapons",            # Major category
    subcategory="Beam Accuracy",   # Specific area
    name="Point-blank beam test",  # Short name
    summary="Validates beam weapons hit at minimum range",
    conditions=["Distance: 50px", "Stationary target"],
    edge_cases=["Minimum range"],
    expected_outcome="Beam hits consistently",
    pass_criteria="Damage dealt > 0",
    max_ticks=500,
    seed=42
)
```

### 2. Create TestScenario Class

```python
import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata

class MyWeaponTest(TestScenario):
    """Description of what this test validates."""

    metadata = TestMetadata(...)  # From step 1

    def setup(self, battle_engine):
        """Configure ships and initial state."""
        attacker = self._load_ship('Test_Attacker.json')
        target = self._load_ship('Test_Target.json')

        attacker.position = pygame.math.Vector2(0, 0)
        target.position = pygame.math.Vector2(50, 0)

        self.initial_hp = target.hp

        battle_engine.start([attacker], [target], seed=self.metadata.seed)

        attacker.current_target = target
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Optional: Called every tick."""
        self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine):
        """Return True if test passed."""
        damage_dealt = self.initial_hp - self.target.hp
        self.results['damage_dealt'] = damage_dealt
        return damage_dealt > 0
```

### 3. Save the File

Save to a `.py` file in this directory (e.g., `my_test.py`).

The **TestRegistry** will automatically discover it.

### 4. Create Pytest Wrapper

```python
# In simulation_tests/tests/test_my_scenarios.py
import pytest
from test_framework.runner import TestRunner
from simulation_tests.scenarios.my_test import MyWeaponTest

@pytest.mark.simulation
class TestMyScenarios:
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        self.runner = TestRunner()

    def test_my_weapon_test(self):
        scenario = self.runner.run_scenario(MyWeaponTest, headless=True)
        assert scenario.passed
```

## Helper Methods

### _load_ship(filename)

Loads a ship from `simulation_tests/data/ships/`:

```python
attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
```

### _get_test_data_path(relative_path)

Gets absolute path to test data:

```python
path = self._get_test_data_path('ships/Test_Ship.json')
```

## Discovery

The **TestRegistry** automatically discovers all scenarios:

```python
from test_framework.registry import TestRegistry

registry = TestRegistry()

# Get all scenarios
all_scenarios = registry.get_all_scenarios()

# Filter by category
weapon_tests = registry.get_by_category("Weapons")

# Get specific scenario
scenario_info = registry.get_by_id("BEAM-001")
scenario_cls = scenario_info['class']
```

## Running Scenarios

### In Pytest (Headless)

```bash
pytest simulation_tests/tests/ -v -m simulation
```

### In Combat Lab (Visual)

```python
from test_framework.registry import TestRegistry
from test_framework.runner import TestRunner

registry = TestRegistry()
scenario_info = registry.get_by_id("BEAM-001")
scenario_cls = scenario_info['class']

runner = TestRunner()
runner.run_scenario(scenario_cls, headless=False, render_callback=draw_fn)
```

## Best Practices

1. **Use Fixed Seeds**: Always set `seed` in metadata for reproducibility
2. **Simplified Data**: Use minimal test data in `simulation_tests/data/`
3. **Clear Metadata**: Provide detailed conditions, edge cases, and pass criteria
4. **Store State**: Save initial values in `setup()` for use in `verify()`
5. **Detailed Results**: Store detailed results in `self.results` dict

## Example

See `example_beam_test.py` for a complete working example demonstrating:
- TestMetadata definition
- Ship loading
- Setup configuration
- Per-tick updates
- Verification logic
- Result storage

## Documentation

See `docs/test_migration_guide.md` for:
- Complete migration guide
- Before/after examples
- Common patterns
- Troubleshooting

## Categories

Organize scenarios by category:
- **Weapons**: Beam, projectile, seeker weapon tests
- **Propulsion**: Engine physics, maneuvering
- **Abilities**: Special abilities and effects
- **Resources**: Energy, fuel, ammo consumption
- **Shields**: Shield mechanics
- **Damage**: Damage calculations and armor

Each category can have multiple subcategories for organization.
