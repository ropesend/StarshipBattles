# Test Framework - Architecture Documentation

## Overview

The test framework provides the core infrastructure for creating, running, and validating simulation tests in Combat Lab.

## Core Components

### 1. TestMetadata (`base.py`)

Stores all metadata about a test:

```python
@dataclass
class TestMetadata:
    test_id: str              # Unique identifier (e.g., "BEAM360-001")
    name: str                 # Display name
    category: str             # Primary category (e.g., "Beam Weapons")
    subcategory: str          # Secondary category (e.g., "Accuracy Tests")
    summary: str              # One-line description
    tags: List[str]           # Searchable tags
    conditions: List[str]     # Test setup conditions (displayed in UI)
    validation_rules: List    # Rules for verifying test results
```

**Purpose**: Self-documenting tests. Everything needed to understand a test is in metadata.

**Example**:
```python
metadata = TestMetadata(
    test_id="BEAM360-001",
    name="Low Accuracy Beam - Point Blank (50px)",
    category="Beam Weapons",
    subcategory="Accuracy Tests",
    summary="Tests beam hit chance at point-blank range with low accuracy weapon",
    tags=["beam", "accuracy", "point-blank", "low-accuracy"],
    conditions=[
        "Distance: 50px center-to-center (20.53px to surface)",
        "Weapon: Low Accuracy Beam (base 50%, falloff 0.2%/px)",
        "Target: Stationary, Mass 400, Defense 0.3316",
        "Expected Hit Rate: 53.18%"
    ],
    validation_rules=[...]
)
```

### 2. TestScenario (`base.py`)

Base class for all test scenarios.

```python
class TestScenario:
    """Base class for all test scenarios."""

    metadata: TestMetadata
    max_ticks: int
    attacker: Ship
    target: Ship
    results: Dict[str, Any]
    passed: bool

    def setup(self, engine) -> None:
        """Initialize test scenario - create ships, position them, calculate expectations."""

    def update(self, engine) -> None:
        """Update test state each tick - track events, collect data."""

    def verify(self, engine) -> bool:
        """Verify test results - run validation rules, determine pass/fail."""

    def run_validation(self) -> List[Dict[str, Any]]:
        """Execute all validation rules and return results."""
```

#### Lifecycle

```
1. __init__()
   - Set max_ticks
   - Initialize state variables
   - Set expected outcomes

2. setup(engine)
   - Load ship JSONs
   - Create Ship instances
   - Position ships
   - Add to engine
   - Store initial state (e.g., initial_hp)

3. update(engine) [called each tick]
   - Track events (shots fired, hits, etc.)
   - Update test-specific state
   - Can end test early if needed

4. verify(engine) [called after simulation ends]
   - Calculate actual outcomes
   - Store in self.results
   - Run validation rules
   - Set self.passed based on all rules passing
   - Return pass/fail

5. Result Display
   - UI or script reads self.results
   - Shows metrics (damage_dealt, hit_rate, etc.)
   - Shows validation results (PASS/FAIL per rule)
```

#### Example Implementation

```python
class MyTestScenario(TestScenario):
    """Example test scenario."""

    metadata = TestMetadata(...)

    def __init__(self):
        super().__init__()
        self.max_ticks = 500
        self.attacker = None
        self.target = None
        self.initial_hp = 0
        self.expected_hit_chance = 0.0

    def setup(self, engine):
        # Load ships
        from game.simulation.entities.ship import Ship
        self.attacker = Ship.from_dict(load_ship_json('Attacker.json'), team_id=1)
        self.target = Ship.from_dict(load_ship_json('Target.json'), team_id=2)

        # Position
        self.attacker.position = pygame.Vector2(100, 100)
        self.target.position = pygame.Vector2(200, 100)

        # Add to engine
        engine.team1_ships = [self.attacker]
        engine.team2_ships = [self.target]

        # Store initial state
        self.initial_hp = self.target.hp

        # Calculate expected outcome
        self.expected_hit_chance = calculate_expected_hit_chance(...)

    def update(self, engine):
        # Track test-specific events
        pass

    def verify(self, engine):
        # Calculate actual outcomes
        damage_dealt = self.initial_hp - self.target.hp
        hit_rate = damage_dealt / engine.tick_count

        # Store results
        self.results['damage_dealt'] = damage_dealt
        self.results['hit_rate'] = hit_rate
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

### 3. TestRunner (`runner.py`)

Handles data loading for test scenarios.

```python
class TestRunner:
    """Runs test scenarios headlessly."""

    def load_data_for_scenario(self, scenario: TestScenario) -> None:
        """
        Load all data needed for a test scenario.

        Steps:
        1. Parse metadata.conditions for ship filenames
        2. Clear component registry
        3. Load modifiers.json
        4. Load components.json
        5. Load vehicleclasses.json

        This ensures clean state for each test run.
        """
```

**Why separate data loading?**
- Ensures clean state between tests
- Prevents component ID conflicts
- Allows tests to use different component sets

**Usage**:
```python
scenario = BeamLowAccuracyPointBlankScenario()

runner = TestRunner()
runner.load_data_for_scenario(scenario)

engine = BattleEngine()
engine.start([], [])
scenario.setup(engine)

# Run test...
```

## Data Flow

```
TestRunner.load_data_for_scenario()
  ↓
Parse scenario.metadata.conditions
  ↓
Clear RegistryManager
  ↓
Load JSON files:
  - modifiers.json
  - components.json
  - vehicleclasses.json
  ↓
Registry populated with components
  ↓
scenario.setup()
  ↓
Ship.from_dict() creates ships
  ↓
Ships reference components from registry
  ↓
scenario.update() × N ticks
  ↓
scenario.verify()
  ↓
Results available in scenario.results
```

## Component Registry

The registry system ensures components are loaded correctly for each test:

```python
# Registry is a singleton that stores all component definitions
from game.registry import RegistryManager

registry = RegistryManager()

# Before each test:
registry.clear()                # Remove old components
registry.load_components(...)   # Load fresh components
# registry stays unfrozen for ship loading

# Ships reference components:
ship = Ship.from_dict(ship_data)
# Internally: registry.get_component('test_beam_low_acc_1dmg')
```

**Important**: Registry must be cleared between tests to prevent ID conflicts.

## Ship Loading from JSON

Ships are created from JSON files:

```python
ship_data = {
    "name": "Test Attacker",
    "ship_class": "TestS_2L",
    "layers": {
        "CORE": [
            {"id": "test_beam_low_acc_1dmg"}
        ]
    }
}

ship = Ship.from_dict(ship_data, team_id=1)

# Ship now has:
# - ship.name = "Test Attacker"
# - ship.mass = sum of component masses
# - ship.hp = sum of component HPs
# - Components accessible via ship.get_component_with_ability()
```

## Validation Integration

Tests use validation rules defined in metadata:

```python
metadata = TestMetadata(
    ...,
    validation_rules=[
        ExactMatchRule(
            name='Weapon Damage',
            path='attacker.weapon.damage',
            expected=1
        ),
        StatisticalTestRule(
            name='Hit Rate',
            test_type='binomial',
            expected_probability=0.5318,
            equivalence_margin=0.06,
            trials_expr='ticks_run',
            successes_expr='damage_dealt'
        )
    ]
)
```

Validation runs automatically when `verify()` is called:

```python
def verify(self, engine):
    # ... calculate outcomes ...

    # Run validation (from TestScenario base class)
    self.results['validation_results'] = self.run_validation()

    # Each validation result has:
    # {
    #     'name': 'Hit Rate',
    #     'status': 'PASS' or 'FAIL',
    #     'message': 'Hit rate 52.00% equivalent to expected 53.18% within ±6.00%',
    #     'p_value': 0.0134,
    #     'tolerance': 0.05
    # }
```

## Helper Functions

Common helper functions for test scenarios:

### Defense Score Calculation

```python
def calculate_defense_score(mass: float, acceleration: float,
                           turn_speed: float, ecm_score: float) -> float:
    """
    Calculate target defense score using game formulas.

    Args:
        mass: Ship mass in kg
        acceleration: Acceleration rate
        turn_speed: Turn speed in degrees/sec
        ecm_score: ECM component bonus

    Returns:
        Total defense score
    """
    size_score = 0.5 * (1.0 - (mass / 1000.0))
    maneuver_score = (acceleration / 1000.0) + (turn_speed / 500.0)
    return size_score + maneuver_score + ecm_score
```

### Hit Chance Calculation

```python
def calculate_expected_hit_chance(base_acc: float, falloff: float,
                                  distance: float, attack_bonus: float,
                                  defense_penalty: float) -> float:
    """
    Calculate expected hit chance using sigmoid formula.

    Args:
        base_acc: Base accuracy (0.0-1.0)
        falloff: Accuracy reduction per pixel
        distance: Distance to TARGET SURFACE (not center!)
        attack_bonus: Attacker sensor score
        defense_penalty: Target defense score

    Returns:
        Hit probability (0.0-1.0)
    """
    range_penalty = distance * falloff
    net_score = (base_acc + attack_bonus) - (range_penalty + defense_penalty)
    return 1.0 / (1.0 + math.exp(-net_score))
```

### Ship JSON Loading

```python
def load_ship_json(filename: str) -> Dict[str, Any]:
    """
    Load ship JSON file from simulation_tests/data/ships/.

    Args:
        filename: Ship JSON filename (e.g., 'Test_Attacker_Beam360_Low.json')

    Returns:
        Ship data dictionary
    """
    import json
    from pathlib import Path

    ship_path = Path(__file__).parent.parent / 'simulation_tests' / 'data' / 'ships' / filename
    with open(ship_path, 'r') as f:
        return json.load(f)
```

## Best Practices

### 1. Always Use setup() for Initialization

```python
# GOOD
def setup(self, engine):
    self.attacker = Ship.from_dict(...)
    self.initial_hp = self.target.hp

# BAD - Don't create ships in __init__
def __init__(self):
    self.attacker = Ship.from_dict(...)  # Registry not loaded yet!
```

### 2. Store Initial State

```python
def setup(self, engine):
    # ...
    self.initial_hp = self.target.hp  # Store before simulation runs
    self.initial_position = self.target.position.copy()
```

### 3. Use Surface Distance for Beam Tests

```python
# GOOD
target_radius = 40 * ((target_mass / 1000) ** (1/3))
surface_distance = center_distance - target_radius
expected_hit_chance = calculate_expected_hit_chance(..., surface_distance, ...)

# BAD - Uses center distance
expected_hit_chance = calculate_expected_hit_chance(..., center_distance, ...)
```

### 4. Document Test Expectations in Conditions

```python
conditions=[
    "Distance: 50px center-to-center (20.53px to surface)",  # Show both!
    "Expected Hit Rate: 53.18% (calculated from surface distance)",
    "Target Radius: 29.47px (from mass 400)",
    "Range Penalty: 0.0411 (20.53 × 0.002)"
]
```

### 5. Validate Component Data

Always include ExactMatchRules to verify component data matches expectations:

```python
validation_rules=[
    ExactMatchRule(name='Damage', path='attacker.weapon.damage', expected=1),
    ExactMatchRule(name='Base Accuracy', path='attacker.weapon.base_accuracy', expected=0.5),
    # ...
]
```

This catches bugs where:
- Component JSON was edited but test wasn't updated
- Wrong component is loaded
- Component properties don't match test design

## Testing Your Tests

Quick validation script template:

```python
"""Validate test scenario setup."""
from your_scenarios import YourTestScenario
from test_framework.runner import TestRunner
from game.simulation.systems.battle_engine import BattleEngine

def validate():
    print("="*80)
    print("VALIDATING: Your Test")
    print("="*80)

    scenario = YourTestScenario()

    # Load data
    runner = TestRunner()
    runner.load_data_for_scenario(scenario)

    # Setup
    engine = BattleEngine()
    engine.start([], [])
    scenario.setup(engine)

    # Print configuration
    print(f"Test ID: {scenario.metadata.test_id}")
    print(f"Max ticks: {scenario.max_ticks}")
    print(f"Attacker: {scenario.attacker.name}, Mass: {scenario.attacker.mass}")
    print(f"Target: {scenario.target.name}, Mass: {scenario.target.mass}")

    # Run quick test (100 ticks)
    for _ in range(100):
        scenario.update(engine)
        engine.update()
        if engine.is_battle_over():
            break

    # Check results
    damage_dealt = scenario.initial_hp - scenario.target.hp
    print(f"Damage dealt: {damage_dealt}")
    print(f"[PASS] Test configured correctly")

if __name__ == "__main__":
    validate()
```

## See Also

- `../COMBAT_LAB_DOCUMENTATION.md` - Complete system documentation
- `../validation/README.md` - Validation rules documentation
- `../scenarios/beam_scenarios.py` - Example implementations
