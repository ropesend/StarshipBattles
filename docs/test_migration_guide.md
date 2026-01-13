# Test Migration Guide: From Pytest to TestScenario Pattern

## Overview

This guide explains how to migrate existing pytest tests to the new **TestScenario pattern**, which enables tests to run identically in both **pytest (headless)** and **Combat Lab (visual)** environments.

### Key Principle

**Both pytest and Combat Lab use the EXACT same BattleEngine code.**

The only difference is:
- **pytest**: `headless=True` (fast, no rendering, automated)
- **Combat Lab**: `headless=False` (visual, interactive, debugging)

This ensures that what passes in pytest will behave identically in Combat Lab, and vice versa.

---

## Architecture

### Shared Components

```
┌─────────────────────────────────────────────────────────────┐
│                      BattleEngine                           │
│              (Core Simulation Logic)                        │
└─────────────────┬───────────────────────┬──────────────────┘
                  │                       │
         ┌────────▼──────────┐   ┌───────▼────────────┐
         │      Pytest       │   │    Combat Lab      │
         │   (Headless)      │   │     (Visual)       │
         │                   │   │                    │
         │  TestScenario ────┼───┼──── TestScenario  │
         │     Class         │   │       Class        │
         └───────────────────┘   └────────────────────┘
```

### Data Flow

1. **TestScenario** defines setup, verification, and metadata
2. **TestRunner** executes the scenario:
   - Loads test data (components.json, ships, etc.)
   - Creates BattleEngine
   - Calls scenario.setup()
   - Runs simulation loop
   - Calls scenario.verify()
3. **Result**: Pass/Fail with detailed results

---

## The TestScenario Pattern

### Components

#### 1. TestMetadata

Rich metadata describing the test:

```python
from simulation_tests.scenarios import TestMetadata

metadata = TestMetadata(
    test_id="BEAM-001",              # Unique ID
    category="Weapons",               # Major category
    subcategory="Beam Accuracy",      # Specific area
    name="Point-blank beam test",     # Short name
    summary="Validates beam weapons hit at minimum range",
    conditions=["Distance: 50px", "Stationary target"],
    edge_cases=["Minimum range"],
    expected_outcome="Beam hits consistently",
    pass_criteria="Damage dealt > 0",
    max_ticks=500,
    seed=42,
    ui_priority=0,
    tags=["accuracy", "close_range"]
)
```

#### 2. TestScenario Class

Base class providing:
- Helper methods for loading ships
- Automatic test data path resolution
- Integration with pytest and Combat Lab
- Metadata management

```python
from simulation_tests.scenarios import TestScenario, TestMetadata

class MyTest(TestScenario):
    metadata = TestMetadata(...)

    def setup(self, battle_engine):
        # Configure ships and initial state
        pass

    def verify(self, battle_engine):
        # Return True if test passed
        return True

    def update(self, battle_engine):
        # Optional: per-tick logic
        pass
```

---

## Migration Steps

### Step 1: Understand the Existing Test

Let's migrate a beam weapon test as an example.

**Original pytest test** (test_beam_weapons.py):

```python
@pytest.mark.simulation
class TestBeamWeapons:
    def test_BEAM360_001_low_acc_point_blank(self):
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')

        result = self._run_battle_and_measure_accuracy(
            attacker, target, distance=50, ticks=500
        )

        assert result['damage_dealt'] > 0
```

### Step 2: Create TestMetadata

Extract test information into metadata:

```python
from simulation_tests.scenarios import TestMetadata

metadata = TestMetadata(
    test_id="BEAM360-001",
    category="Weapons",
    subcategory="Beam Accuracy",
    name="Low accuracy beam at point-blank",
    summary="Validates low accuracy beam (0.5) hits at 50px range",
    conditions=[
        "Distance: 50px",
        "Stationary target",
        "Base accuracy: 0.5",
        "Accuracy falloff: 0.002"
    ],
    edge_cases=["Minimum engagement range"],
    expected_outcome="Beam should hit most of the time at close range",
    pass_criteria="Damage dealt > 0",
    max_ticks=500,
    seed=42,
    tags=["beam", "accuracy", "low_accuracy", "point_blank"]
)
```

### Step 3: Create TestScenario Class

Convert the test to a scenario:

```python
import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata

class BEAM360_001_LowAccPointBlank(TestScenario):
    """Low accuracy beam at point-blank range."""

    metadata = TestMetadata(
        test_id="BEAM360-001",
        category="Weapons",
        subcategory="Beam Accuracy",
        name="Low accuracy beam at point-blank",
        summary="Validates low accuracy beam (0.5) hits at 50px range",
        conditions=[
            "Distance: 50px",
            "Stationary target",
            "Base accuracy: 0.5",
            "Accuracy falloff: 0.002"
        ],
        edge_cases=["Minimum engagement range"],
        expected_outcome="Beam should hit most of the time at close range",
        pass_criteria="Damage dealt > 0",
        max_ticks=500,
        seed=42,
        tags=["beam", "accuracy", "low_accuracy", "point_blank"]
    )

    def setup(self, battle_engine):
        """Configure the test scenario."""
        # Load ships
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')

        # Position ships
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0  # Facing right
        target.position = pygame.math.Vector2(50, 0)
        target.angle = 0

        # Store initial HP for verification
        self.initial_target_hp = target.hp

        # Start battle with fixed seed
        battle_engine.start([attacker], [target], seed=self.metadata.seed)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Called every tick - ensure weapon fires."""
        # Force weapon firing for consistent testing
        self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine):
        """Check if test passed."""
        damage_dealt = self.initial_target_hp - self.target.hp

        # Pass if any damage was dealt
        passed = damage_dealt > 0

        # Store results for reporting
        self.results['damage_dealt'] = damage_dealt
        self.results['initial_hp'] = self.initial_target_hp
        self.results['final_hp'] = self.target.hp
        self.results['target_alive'] = self.target.is_alive

        return passed
```

### Step 4: Save the Scenario

Save to `simulation_tests/scenarios/beam_accuracy.py`:

```python
"""
Beam Accuracy Test Scenarios

Validates beam weapon accuracy mechanics across different ranges and conditions.
"""

import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata

class BEAM360_001_LowAccPointBlank(TestScenario):
    # ... (as above)

class BEAM360_002_LowAccMidRange(TestScenario):
    # ... (similar pattern)

# Add more scenarios...
```

### Step 5: Create Pytest Wrapper

Create a pytest test that uses the scenario:

```python
"""
Pytest wrapper for beam accuracy scenarios.

These tests use the TestScenario pattern, allowing them to run in both
pytest (headless) and Combat Lab (visual) with identical behavior.
"""
import pytest
from test_framework.runner import TestRunner
from simulation_tests.scenarios.beam_accuracy import (
    BEAM360_001_LowAccPointBlank,
    BEAM360_002_LowAccMidRange,
    # ... other scenarios
)

@pytest.mark.simulation
class TestBeamAccuracy:
    """Beam accuracy tests using TestScenario pattern."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for test isolation."""
        self.runner = TestRunner()

    def test_BEAM360_001_low_acc_point_blank(self):
        """BEAM360-001: Low accuracy beam at point-blank."""
        scenario = self.runner.run_scenario(
            BEAM360_001_LowAccPointBlank,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_BEAM360_002_low_acc_mid_range(self):
        """BEAM360-002: Low accuracy beam at mid-range."""
        scenario = self.runner.run_scenario(
            BEAM360_002_LowAccMidRange,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"
```

---

## Complete Example: Before and After

### Before (Old Pytest Style)

```python
# test_beam_weapons.py
@pytest.mark.simulation
class TestBeamWeapons:
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry, ships_dir):
        self.ships_dir = ships_dir

    def _load_ship(self, filename: str) -> Ship:
        path = os.path.join(self.ships_dir, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        ship = Ship.from_dict(data)
        ship.recalculate_stats()
        return ship

    def _run_battle_and_measure_accuracy(
        self, attacker, target, distance, ticks=500, seed=42
    ):
        attacker.position = pygame.math.Vector2(0, 0)
        target.position = pygame.math.Vector2(distance, 0)

        initial_hp = target.hp

        engine = BattleEngine()
        engine.start([attacker], [target], seed=seed)
        attacker.current_target = target

        for _ in range(ticks):
            if not target.is_alive:
                break
            attacker.comp_trigger_pulled = True
            engine.update()

        damage_dealt = initial_hp - target.hp
        engine.shutdown()

        return {'damage_dealt': damage_dealt}

    def test_BEAM360_001_low_acc_point_blank(self):
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')

        result = self._run_battle_and_measure_accuracy(
            attacker, target, distance=50, ticks=500
        )

        assert result['damage_dealt'] > 0
```

### After (New TestScenario Pattern)

```python
# simulation_tests/scenarios/beam_accuracy.py
"""Beam Accuracy Test Scenarios"""

import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata

class BEAM360_001_LowAccPointBlank(TestScenario):
    """Low accuracy beam at point-blank range."""

    metadata = TestMetadata(
        test_id="BEAM360-001",
        category="Weapons",
        subcategory="Beam Accuracy",
        name="Low accuracy beam at point-blank",
        summary="Validates low accuracy beam (0.5) hits at 50px range",
        conditions=["Distance: 50px", "Stationary target"],
        edge_cases=["Minimum engagement range"],
        expected_outcome="Beam hits most of the time at close range",
        pass_criteria="Damage dealt > 0",
        max_ticks=500,
        seed=42
    )

    def setup(self, battle_engine):
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')

        attacker.position = pygame.math.Vector2(0, 0)
        target.position = pygame.math.Vector2(50, 0)

        self.initial_target_hp = target.hp

        battle_engine.start([attacker], [target], seed=self.metadata.seed)

        attacker.current_target = target
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine):
        damage_dealt = self.initial_target_hp - self.target.hp
        self.results['damage_dealt'] = damage_dealt
        return damage_dealt > 0


# simulation_tests/tests/test_beam_accuracy.py
"""Pytest wrapper for beam accuracy scenarios."""

import pytest
from test_framework.runner import TestRunner
from simulation_tests.scenarios.beam_accuracy import BEAM360_001_LowAccPointBlank

@pytest.mark.simulation
class TestBeamAccuracy:
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        self.runner = TestRunner()

    def test_BEAM360_001_low_acc_point_blank(self):
        scenario = self.runner.run_scenario(
            BEAM360_001_LowAccPointBlank,
            headless=True
        )
        assert scenario.passed
```

---

## Benefits of TestScenario Pattern

### 1. Pytest and Combat Lab Use Same Code

```python
# Pytest (headless, automated)
scenario = runner.run_scenario(MyTest, headless=True)
assert scenario.passed

# Combat Lab (visual, interactive)
scenario = runner.run_scenario(MyTest, headless=False, render_callback=draw)
# User can see the battle play out
```

### 2. Rich Metadata for Documentation

```python
metadata = TestMetadata(
    test_id="BEAM360-001",
    category="Weapons",
    summary="Validates beam accuracy at point-blank",
    conditions=["Distance: 50px"],
    expected_outcome="High hit rate"
)

# Automatically generates documentation
# Displayed in Combat Lab UI
# Used for test organization
```

### 3. Simplified Test Data Management

```python
# Before: Manual path construction
path = os.path.join(self.ships_dir, 'Test_Attacker.json')
with open(path, 'r') as f:
    data = json.load(f)
ship = Ship.from_dict(data)

# After: Helper method
ship = self._load_ship('Test_Attacker.json')
```

### 4. Discoverable by TestRegistry

```python
from test_framework.registry import TestRegistry

registry = TestRegistry()

# Get all beam tests
beam_tests = registry.get_by_category("Weapons")

# Display in Combat Lab UI
for test_id, info in beam_tests.items():
    print(f"{test_id}: {info['metadata'].name}")
```

---

## Best Practices

### 1. Use Simplified Test Data

Tests should use minimal, purpose-built data:

```json
// Test_Attacker_Beam360_Low.json
{
  "name": "Low Accuracy Beam Attacker",
  "team_id": 0,
  "position": {"x": 0, "y": 0},
  "ship_class": "TestAttacker",
  "components": [
    {"id": "Test_Beam_Low", "layer": "OUTER", "slot": 0}
  ]
}
```

### 2. Make Tests Deterministic

Always use fixed seeds:

```python
metadata = TestMetadata(
    test_id="TEST-001",
    seed=42,  # Fixed seed for reproducibility
    # ...
)

def setup(self, battle_engine):
    battle_engine.start([attacker], [target], seed=self.metadata.seed)
```

### 3. Store Data for Verification

Save state in setup for use in verify:

```python
def setup(self, battle_engine):
    self.initial_hp = target.hp
    self.initial_energy = attacker.current_energy

def verify(self, battle_engine):
    damage_dealt = self.initial_hp - self.target.hp
    energy_used = self.initial_energy - self.attacker.current_energy
    return damage_dealt > 0 and energy_used > 0
```

### 4. Provide Detailed Pass Criteria

```python
metadata = TestMetadata(
    pass_criteria="Damage dealt > 0 AND hit rate > 90%",
    # ...
)

def verify(self, battle_engine):
    hits = self.results['hits']
    shots = self.results['shots']
    hit_rate = hits / shots if shots > 0 else 0

    passed = (
        self.results['damage_dealt'] > 0 and
        hit_rate > 0.90
    )

    self.results['hit_rate'] = hit_rate
    return passed
```

### 5. Organize Tests by Category

```
simulation_tests/scenarios/
    beam_accuracy.py      # BEAM360-001 through BEAM360-011
    projectile_damage.py  # PROJ360-001 through PROJ360-010
    seeker_tracking.py    # SEEK360-001 through SEEK360-008
    shield_defense.py     # SHLD-001 through SHLD-015
```

---

## Common Patterns

### Pattern 1: Distance-Based Tests

```python
class BeamRangeTest(TestScenario):
    metadata = TestMetadata(
        test_id="BEAM-RANGE-001",
        name="Beam accuracy at 400px",
        # ...
    )

    def setup(self, battle_engine):
        attacker = self._load_ship('Test_Attacker_Beam.json')
        target = self._load_ship('Test_Target.json')

        # Position at specific distance
        attacker.position = pygame.math.Vector2(0, 0)
        target.position = pygame.math.Vector2(400, 0)

        # ...
```

### Pattern 2: Resource Consumption Tests

```python
class EnergyConsumptionTest(TestScenario):
    metadata = TestMetadata(
        test_id="ENERGY-001",
        name="Beam weapon energy consumption",
        # ...
    )

    def setup(self, battle_engine):
        self.attacker = self._load_ship('Test_Attacker.json')
        self.initial_energy = self.attacker.current_energy
        # ...

    def verify(self, battle_engine):
        energy_used = self.initial_energy - self.attacker.current_energy
        shots_fired = self.results['shots_fired']

        # Expected: 10 energy per shot
        expected_energy = shots_fired * 10

        # Allow 5% tolerance
        return abs(energy_used - expected_energy) < (expected_energy * 0.05)
```

### Pattern 3: Timing Tests

```python
class WeaponCooldownTest(TestScenario):
    metadata = TestMetadata(
        test_id="COOLDOWN-001",
        name="Weapon cooldown timing",
        # ...
    )

    def setup(self, battle_engine):
        self.attacker = self._load_ship('Test_Attacker.json')
        self.shot_ticks = []

    def update(self, battle_engine):
        # Track when shots are fired
        weapon = self.attacker.get_component_by_id('Test_Weapon')
        if weapon.just_fired:
            self.shot_ticks.append(battle_engine.tick_counter)

    def verify(self, battle_engine):
        if len(self.shot_ticks) < 2:
            return False

        # Check cooldown between shots
        intervals = [
            self.shot_ticks[i+1] - self.shot_ticks[i]
            for i in range(len(self.shot_ticks) - 1)
        ]

        expected_cooldown = 60  # ticks

        # All intervals should match expected cooldown
        return all(abs(interval - expected_cooldown) <= 1 for interval in intervals)
```

### Pattern 4: Multi-Ship Tests

```python
class TeamBattleTest(TestScenario):
    metadata = TestMetadata(
        test_id="TEAM-001",
        name="2v2 team battle",
        # ...
    )

    def setup(self, battle_engine):
        # Team 0
        attacker1 = self._load_ship('Team0_Ship1.json')
        attacker2 = self._load_ship('Team0_Ship2.json')

        # Team 1
        target1 = self._load_ship('Team1_Ship1.json')
        target2 = self._load_ship('Team1_Ship2.json')

        # Position ships
        attacker1.position = pygame.math.Vector2(0, 0)
        attacker2.position = pygame.math.Vector2(0, 100)
        target1.position = pygame.math.Vector2(500, 0)
        target2.position = pygame.math.Vector2(500, 100)

        battle_engine.start(
            [attacker1, attacker2],
            [target1, target2],
            seed=self.metadata.seed
        )

    def verify(self, battle_engine):
        # Team 0 should win
        return all(ship.is_alive for ship in battle_engine.teams[0])
```

---

## Running Tests

### In Pytest (Headless)

```bash
# Run all simulation tests
pytest simulation_tests/tests/ -v -m simulation

# Run specific test file
pytest simulation_tests/tests/test_beam_accuracy.py -v

# Run specific test
pytest simulation_tests/tests/test_beam_accuracy.py::TestBeamAccuracy::test_BEAM360_001_low_acc_point_blank -v
```

### In Combat Lab (Visual)

```python
# In Combat Lab UI
from test_framework.registry import TestRegistry

registry = TestRegistry()

# User selects "Weapons" category
weapon_tests = registry.get_by_category("Weapons")

# User selects "BEAM360-001"
scenario_info = registry.get_by_id("BEAM360-001")
scenario_cls = scenario_info['class']

# Run with rendering
runner = TestRunner()
runner.run_scenario(scenario_cls, headless=False, render_callback=draw_fn)
```

---

## TestRegistry Usage

### Discovery

```python
from test_framework.registry import TestRegistry

registry = TestRegistry()

# Registry automatically discovers all scenarios in
# simulation_tests/scenarios/*.py
```

### Filtering

```python
# By category
weapon_tests = registry.get_by_category("Weapons")

# By subcategory
beam_tests = registry.get_by_subcategory("Weapons", "Beam Accuracy")

# By tag
accuracy_tests = registry.get_by_tag("accuracy")

# By ID
test = registry.get_by_id("BEAM360-001")
```

### Display

```python
# Get all categories
categories = registry.get_categories()
# ['Abilities', 'Propulsion', 'Resources', 'Weapons']

# Print summary
registry.print_summary()
```

---

## Troubleshooting

### Issue: Ship file not found

```python
# Error: FileNotFoundError: Ship file not found: ...

# Solution: Ensure ship files are in simulation_tests/data/ships/
ship_path = "simulation_tests/data/ships/Test_Attacker.json"
```

### Issue: Test not discovered

```python
# Problem: Scenario not showing up in registry

# Check:
1. File is in simulation_tests/scenarios/
2. Class extends TestScenario
3. Class has metadata attribute
4. File doesn't start with underscore
```

### Issue: Test fails in Combat Lab but passes in pytest

```python
# This should NOT happen if done correctly
# But if it does:

# Check:
1. Using fixed seed?
2. Test depends on rendering/timing?
3. Calling update() properly?
```

---

## Next Steps

1. **Migrate one test** as practice
2. **Run it in pytest** to verify it works
3. **Test discovery** with TestRegistry
4. **Migrate remaining tests** following the pattern
5. **Update Combat Lab** to use TestRegistry

---

## Summary

The TestScenario pattern provides:

1. **Unified Testing**: Same code in pytest and Combat Lab
2. **Rich Metadata**: Self-documenting tests
3. **Discoverability**: Automatic registration
4. **Simplified Data**: Helper methods for test data
5. **Reproducibility**: Fixed seeds and deterministic tests

By following this pattern, we ensure that automated tests and visual debugging use identical simulation logic, eliminating subtle bugs and inconsistencies.
