# Combat Lab - Documentation Hub

## Welcome to Combat Lab

Combat Lab is a comprehensive testing system for validating combat mechanics in Starship Battles. This document serves as your entry point to all Combat Lab documentation.

---

## Quick Links

### 🚀 Getting Started
- **[Quick Start Guide](simulation_tests/QUICK_START_GUIDE.md)** - Create your first test in 10 minutes

### 📚 Core Documentation
- **[Main Documentation](simulation_tests/COMBAT_LAB_DOCUMENTATION.md)** - Complete system overview (100+ pages)
- **[Test Framework](test_framework/README.md)** - Architecture and design patterns
- **[Validation System](simulation_tests/validation/README.md)** - TOST equivalence testing
- **[Data Files](simulation_tests/data/README.md)** - Components and ship configurations
- **[Test Scenarios](simulation_tests/scenarios/README.md)** - Beam weapon tests and examples

---

## What is Combat Lab?

Combat Lab provides:

✅ **Visual Test Runner** - UI for browsing and running tests
✅ **Statistical Validation** - TOST (Two One-Sided Tests) equivalence testing
✅ **Data Verification** - Automatic checking of component data
✅ **Headless Execution** - Run tests without UI for CI/CD
✅ **High-Precision Tests** - 100k tick tests with ±1% margins
✅ **Self-Documenting** - Each test includes metadata explaining what it validates

---

## Current Test Suite

### Beam Weapon Tests (18 tests)

| Category | Tests | Description |
|----------|-------|-------------|
| **Standard Accuracy** | 8 tests | Low/Med/High accuracy at various ranges (500 ticks, ±6%) |
| **Moving Targets** | 2 tests | Erratic small targets with high defense (500 ticks) |
| **Boundary Tests** | 1 test | Out of range (deterministic) |
| **High-Tick Precision** | 7 tests | Same as standard but 100k ticks, ±1% margin |

**Total Coverage**: 11 test configurations × 2 variants (standard + high-tick) - 4 = **18 tests**

---

## Documentation Map

### For New Users

1. Start here: [Quick Start Guide](simulation_tests/QUICK_START_GUIDE.md)
2. Read overview: [Main Documentation - Overview](simulation_tests/COMBAT_LAB_DOCUMENTATION.md#overview)
3. Try running a test in Combat Lab UI
4. Create your first test following the Quick Start

### For Test Authors

1. [Quick Start Guide](simulation_tests/QUICK_START_GUIDE.md) - Step-by-step test creation
2. [Creating New Tests](simulation_tests/COMBAT_LAB_DOCUMENTATION.md#creating-new-tests) - Detailed guide
3. [Test Framework](test_framework/README.md) - TestScenario lifecycle and patterns
4. [Beam Scenarios](simulation_tests/scenarios/README.md) - Working examples

### For System Architects

1. [System Architecture](simulation_tests/COMBAT_LAB_DOCUMENTATION.md#system-architecture) - Component relationships
2. [Test Framework](test_framework/README.md) - Base classes and data flow
3. [Validation System](simulation_tests/validation/README.md) - TOST mathematics and implementation

### For Data Engineers

1. [Data Files](simulation_tests/data/README.md) - Components, ships, modifiers
2. [Ship Configurations](simulation_tests/data/README.md#ship-files-ships-directory) - Ship JSON structure
3. [Component Registry](simulation_tests/data/README.md#data-loading-sequence) - Loading sequence

### For Validation Specialists

1. [Validation System](simulation_tests/validation/README.md) - Complete validation guide
2. [TOST Explanation](simulation_tests/validation/README.md#tost-two-one-sided-tests) - Statistical testing
3. [ExactMatchRule](simulation_tests/validation/README.md#exactmatchrule-data-verification) - Data verification
4. [StatisticalTestRule](simulation_tests/validation/README.md#statisticaltestrule-tost-equivalence-testing) - Equivalence testing

---

## Key Concepts

### TOST (Two One-Sided Tests)

Traditional hypothesis testing proves things are **different**.
TOST proves things are **equivalent** within a margin.

- **p < 0.05** = PASS (proven equivalent)
- **p ≥ 0.05** = FAIL (not proven equivalent)

**Example**: 50% hit rate weapon should hit 50% ± 6% of the time
TOST proves the observed rate is statistically equivalent to 50% within that margin.

**See**: [Validation System - TOST](simulation_tests/validation/README.md#tost-two-one-sided-tests)

### Surface Distance (CRITICAL for Beam Tests)

Beam weapons use raycasting to find the intersection with the target's collision circle.

```python
# WRONG - Using center distance
distance = 50.0  # Center-to-center
expected_hit_rate = calculate(..., 50.0, ...)  # FAILS!

# CORRECT - Using surface distance
target_radius = 40 * (mass/1000)**(1/3)  # e.g., 29.47px for mass=400
surface_distance = 50.0 - 29.47  # 20.53px
expected_hit_rate = calculate(..., 20.53, ...)  # PASSES!
```

**See**: [Beam Tests - Surface Distance](simulation_tests/scenarios/README.md#surface-distance-calculation)

### Standard vs High-Tick Tests

| Type | Ticks | Margin | Standard Error | Use Case |
|------|-------|--------|----------------|----------|
| **Standard** | 500 | ±6% | ~2.2% | Quick validation, development |
| **High-Tick** | 100,000 | ±1% | ~0.16% | Precise validation, final verification |

**See**: [Main Docs - Equivalence Margins](simulation_tests/COMBAT_LAB_DOCUMENTATION.md#choosing-equivalence-margins)

### Validation Rules

Every test includes:

**5 ExactMatchRules** (component data verification):
- Beam Weapon Damage
- Base Accuracy
- Accuracy Falloff
- Weapon Range
- Target Mass

**1 StatisticalTestRule** (hit rate validation):
- Expected Probability (calculated from game formulas)
- Equivalence Margin (±6% or ±1%)
- TOST p-value < 0.05 = PASS

**See**: [Validation System](simulation_tests/validation/README.md)

---

## Running Tests

### In Combat Lab UI

```bash
python main.py
# Navigate to "Combat Lab"
# Browse tests by category
# Select test and click "Run Test"
```

### Headless (Command Line)

```python
"""Run test headlessly."""
from simulation_tests.scenarios.beam_scenarios import BeamLowAccuracyPointBlankScenario
from game.simulation.systems.battle_engine import BattleEngine
from test_framework.runner import TestRunner

scenario = BeamLowAccuracyPointBlankScenario()
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
print(f"Test {'PASSED' if passed else 'FAILED'}")
```

**See**: [Running Tests](simulation_tests/COMBAT_LAB_DOCUMENTATION.md#running-tests)

---

## Example: Complete Test

```python
class MyTestScenario(TestScenario):
    """Example beam weapon test."""

    metadata = TestMetadata(
        test_id="MY-TEST-001",
        name="Medium Accuracy Beam - Mid Range",
        category="My Tests",
        subcategory="Beam Weapons",
        summary="Tests medium accuracy beam at 400px",
        tags=["beam", "accuracy", "mid-range"],
        conditions=[
            "Distance: 400px (370.53px to surface)",
            "Weapon: 80% base, 0.1%/px falloff",
            "Target: Stationary, Mass 400"
        ],
        validation_rules=[
            ExactMatchRule(name='Damage', path='attacker.weapon.damage', expected=1),
            StatisticalTestRule(
                name='Hit Rate',
                expected_probability=0.5323,  # Calculated
                equivalence_margin=0.06,
                trials_expr='ticks_run',
                successes_expr='damage_dealt'
            )
        ]
    )

    def __init__(self):
        super().__init__()
        self.max_ticks = 500
        self.expected_hit_chance = 0.5323

    def setup(self, engine):
        self.attacker = Ship.from_dict(load_ship_json('Test_Attacker_Beam360_Med.json'))
        self.target = Ship.from_dict(load_ship_json('Test_Target_Stationary.json'))

        self.attacker.position = pygame.Vector2(100, 100)
        self.target.position = pygame.Vector2(500, 100)  # 400px away

        self.attacker.current_target = self.target
        engine.team1_ships = [self.attacker]
        engine.team2_ships = [self.target]

        self.initial_hp = self.target.hp

    def update(self, engine):
        # Keep attacker aimed at target
        direction = (self.target.position - self.attacker.position).normalize()
        self.attacker.direction = direction

    def verify(self, engine):
        damage_dealt = self.initial_hp - self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = engine.tick_count
        self.results['hit_rate'] = damage_dealt / engine.tick_count

        self.results['validation_results'] = self.run_validation()
        self.passed = all(r['status'] == 'PASS' for r in self.results['validation_results'])
        return self.passed
```

**See**: [Quick Start Guide](simulation_tests/QUICK_START_GUIDE.md) for complete walkthrough

---

## File Structure

```
Starship Battles/
├── COMBAT_LAB_README.md              # This file - documentation hub
│
├── simulation_tests/
│   ├── COMBAT_LAB_DOCUMENTATION.md   # Main documentation (100+ pages)
│   ├── QUICK_START_GUIDE.md          # Create first test in 10 minutes
│   │
│   ├── data/                         # Test data
│   │   ├── README.md                 # Data files documentation
│   │   ├── components.json           # Component definitions
│   │   ├── modifiers.json            # Stat modifiers
│   │   ├── vehicleclasses.json       # Ship hull types
│   │   └── ships/                    # Ship configurations
│   │       ├── Test_Attacker_*.json
│   │       └── Test_Target_*.json
│   │
│   ├── scenarios/                    # Test implementations
│   │   ├── README.md                 # Scenario documentation
│   │   └── beam_scenarios.py         # 18 beam weapon tests
│   │
│   └── validation/                   # Validation system
│       ├── README.md                 # Validation documentation
│       ├── rules.py                  # ExactMatchRule, StatisticalTestRule
│       └── validators.py             # Validation execution
│
└── test_framework/                   # Core framework
    ├── README.md                     # Framework architecture
    ├── base.py                       # TestScenario, TestMetadata
    └── runner.py                     # TestRunner for headless execution
```

---

## Common Tasks

### I want to...

**Create a new test**
→ [Quick Start Guide](simulation_tests/QUICK_START_GUIDE.md)

**Understand TOST testing**
→ [Validation System - TOST](simulation_tests/validation/README.md#tost-two-one-sided-tests)

**Calculate expected hit rates**
→ [Beam Tests - Calculation Example](simulation_tests/scenarios/README.md#critical-implementation-details)

**Add new components**
→ [Data Files - Adding Components](simulation_tests/data/README.md#adding-new-test-components)

**Create new ship configurations**
→ [Data Files - Creating Ships](simulation_tests/data/README.md#creating-new-test-ships)

**Debug failing tests**
→ [Validation - Debugging](simulation_tests/validation/README.md#debugging-validation-failures)

**Understand test lifecycle**
→ [Test Framework - Lifecycle](test_framework/README.md#lifecycle)

**Run tests headlessly**
→ [Main Docs - Headless Execution](simulation_tests/COMBAT_LAB_DOCUMENTATION.md#headless-execution)

---

## System Requirements

- Python 3.10+
- pygame-ce 2.5+
- numpy (for statistical tests)
- scipy (for TOST calculations)

---

## Credits

**Combat Lab System**: Designed and implemented by Claude Sonnet 4.5 + User
**TOST Implementation**: Statistical equivalence testing for game mechanics
**Beam Weapon Test Suite**: 18 comprehensive tests validating beam weapon mechanics

**Created**: January 2026
**Last Updated**: January 2026

---

## Getting Help

### Documentation Not Clear?

All documentation files are markdown and can be searched with standard tools:

```bash
# Find all mentions of "surface distance"
grep -r "surface distance" simulation_tests/

# Find validation examples
grep -r "StatisticalTestRule" simulation_tests/
```

### Test Failing Unexpectedly?

1. Check expected value calculation - Most common issue
2. Verify surface distance - Not center-to-center!
3. Print debug info - Add print statements in setup()
4. Run multiple times - 5% chance of random failure
5. Consult troubleshooting: [Main Docs - Troubleshooting](simulation_tests/COMBAT_LAB_DOCUMENTATION.md#troubleshooting)

### Need More Examples?

See `simulation_tests/scenarios/beam_scenarios.py` for 18 complete working examples.

---

## Next Steps

1. **Read**: [Quick Start Guide](simulation_tests/QUICK_START_GUIDE.md)
2. **Try**: Run a test in Combat Lab UI (`python main.py`)
3. **Create**: Follow Quick Start to create your first test
4. **Explore**: Read [Main Documentation](simulation_tests/COMBAT_LAB_DOCUMENTATION.md) for deep dive

**Happy Testing!** 🚀
