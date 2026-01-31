# Combat Lab - Documentation Hub

## Welcome to Combat Lab

Combat Lab is a comprehensive testing system for validating combat mechanics in Starship Battles. This document serves as your entry point to all Combat Lab documentation.

---

## Quick Links

### Getting Started
- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Create your first test in 10 minutes

### Core Documentation
- **[Main Documentation](COMBAT_LAB_DOCUMENTATION.md)** - Complete system overview
- **[Test Constants](test_constants.py)** - Centralized constants for tests

### Key Files
- **UI**: `game/ui/screens/test_lab_screen.py` - Combat Lab pygame interface
- **Controller**: `test_framework/services/test_lab_controller.py` - UI coordinator
- **Registry**: `test_framework/registry.py` - Auto-discovers test scenarios
- **Runner**: `test_framework/runner.py` - Executes test scenarios
- **Base Classes**: `simulation_tests/scenarios/base.py` - TestScenario, TestMetadata
- **Validation**: `simulation_tests/scenarios/validation.py` - ValidationRule classes

---

## What is Combat Lab?

Combat Lab provides:

- **Visual Test Runner** - In-game UI for browsing and running tests
- **Statistical Validation** - TOST (Two One-Sided Tests) equivalence testing
- **Data Verification** - ExactMatchRules for component data validation
- **Headless Execution** - Run tests without UI for CI/CD integration
- **High-Precision Tests** - 100k tick tests with ±1% margins
- **Self-Documenting** - Each test includes rich metadata explaining what it validates

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Combat Lab UI                               │
│                (game/ui/screens/test_lab_screen.py)                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                     TestLabUIController                              │
│          (test_framework/services/test_lab_controller.py)           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐  ┌─────────────────────┐  ┌────────────────┐
│  TestRunner   │  │    TestRegistry     │  │   Services     │
│  (runner.py)  │  │   (registry.py)     │  │ (services/)    │
└───────┬───────┘  └──────────┬──────────┘  └────────────────┘
        │                     │
        └─────────┬───────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TestScenario                                 │
│             (simulation_tests/scenarios/base.py)                     │
│  - setup(engine): Initialize ships, positions                        │
│  - update(engine): Per-tick logic (optional)                        │
│  - verify(engine): Calculate results, run validation                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                       Validation System                              │
│           (simulation_tests/scenarios/validation.py)                 │
│  - ExactMatchRule: Zero-tolerance data verification                  │
│  - DeterministicMatchRule: Physics with tiny tolerance               │
│  - StatisticalTestRule: TOST equivalence testing                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current Test Suite

### Beam Weapon Tests

Test IDs follow the pattern: `BEAMWEAPON-XXX` for standard, `BEAMWEAPON-XXX-HT` for high-tick.

| Category | Tests | Description |
|----------|-------|-------------|
| **Standard Accuracy** | 8 tests | Low/Med/High accuracy at various ranges (500 ticks, ±6%) |
| **Moving Targets** | 2 tests | Erratic small targets with high defense (500 ticks) |
| **Boundary Tests** | 1 test | Out of range (deterministic) |
| **High-Tick Precision** | 7 tests | Same as standard but 100k ticks, ±1% margin |

---

## Key Concepts

### TOST (Two One-Sided Tests)

Traditional hypothesis testing proves things are **different**.
TOST proves things are **equivalent** within a margin.

- **p < 0.05** = PASS (proven equivalent)
- **p >= 0.05** = FAIL (not proven equivalent)

### Surface Distance (CRITICAL)

Beam weapons measure distance to target **surface**, not center:

```python
# Target radius from mass
target_radius = 40 * (mass / 1000) ** (1/3)

# Surface distance (what weapons use)
surface_distance = center_distance - target_radius

# Example: mass=400, center_distance=50
# radius = 29.47px, surface_distance = 20.53px
```

### Defense Score (Logarithmic Formula)

```python
def calculate_defense_score(mass, acceleration=0.0, turn_speed=0.0, ecm_score=0.0):
    # Radius calculation
    radius = 40 * ((max(mass, 100) / 1000) ** (1/3))

    # Size score (logarithmic)
    diameter = radius * 2
    d_ratio = max(0.1, diameter / 80.0)
    size_score = -2.5 * math.log10(d_ratio)

    # Maneuver score
    maneuver_score = math.sqrt((acceleration / 20.0) + (turn_speed / 360.0))

    return size_score + maneuver_score + ecm_score
```

### Standard vs High-Tick Tests

| Type | Ticks | Margin | Standard Error | Use Case |
|------|-------|--------|----------------|----------|
| **Standard** | 500 | ±6% | ~2.2% | Quick validation, development |
| **High-Tick** | 100,000 | ±1% | ~0.16% | Precise validation, releases |

---

## Running Tests

### In Combat Lab UI

```bash
python main.py
# Navigate to "Combat Lab"
# Browse tests by category
# Select test and click "Run Visual" or "Run Headless"
```

### Headless (Python)

```python
from simulation_tests.scenarios.beam_scenarios import BeamLowAccuracyPointBlankScenario
from test_framework.runner import TestRunner

runner = TestRunner()
scenario = runner.run_scenario(BeamLowAccuracyPointBlankScenario, headless=True)

print(f"Test: {scenario.metadata.test_id}")
print(f"Result: {'PASSED' if scenario.passed else 'FAILED'}")
print(f"Hit Rate: {scenario.results.get('hit_rate', 0):.2%}")
```

---

## File Structure

```
Starship Battles/
├── game/
│   └── ui/screens/
│       └── test_lab_screen.py      # Combat Lab UI
│
├── test_framework/
│   ├── registry.py                 # Test discovery
│   ├── runner.py                   # Test execution
│   └── services/
│       └── test_lab_controller.py  # UI controller
│
└── simulation_tests/
    ├── README.md                   # This file
    ├── COMBAT_LAB_DOCUMENTATION.md # Full documentation
    ├── QUICK_START_GUIDE.md        # Tutorial
    ├── test_constants.py           # Centralized constants
    │
    ├── data/
    │   ├── components.json         # Test components
    │   ├── modifiers.json          # Stat modifiers
    │   ├── vehicleclasses.json     # Ship hulls
    │   └── ships/                  # Ship configurations
    │
    └── scenarios/
        ├── base.py                 # TestScenario, TestMetadata
        ├── validation.py           # ValidationRule classes
        ├── templates.py            # Reusable templates
        ├── beam_scenarios.py       # Beam weapon tests
        ├── projectile_scenarios.py # Projectile tests
        ├── seeker_scenarios.py     # Seeker/missile tests
        ├── propulsion_scenarios.py # Movement tests
        └── resource_scenarios.py   # Energy/ammo tests
```

---

## Common Tasks

| I want to... | See... |
|--------------|--------|
| Create a new test | [Quick Start Guide](QUICK_START_GUIDE.md) |
| Understand TOST | [Main Docs - Validation System](COMBAT_LAB_DOCUMENTATION.md#validation-system) |
| Calculate hit rates | [Main Docs - Beam Weapon Mechanics](COMBAT_LAB_DOCUMENTATION.md#beam-weapon-mechanics) |
| Debug failing tests | [Main Docs - Troubleshooting](COMBAT_LAB_DOCUMENTATION.md#troubleshooting) |
| Run tests headlessly | [Main Docs - Running Tests](COMBAT_LAB_DOCUMENTATION.md#running-tests) |

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **TOST validation** | Proves equivalence, not just "no difference detected" |
| **Surface distance** | Beam raycasting hits target surface, not center |
| **Logarithmic defense** | Better scaling across ship size range |
| **Zero-mass components** | Isolates hull mass for predictable defense scores |
| **1 billion HP targets** | Survives 100k ticks at 99% hit rate |
| **Two test tiers** | Fast feedback (500) + precise validation (100k) |

---

## System Requirements

- Python 3.10+
- pygame-ce 2.5+
- scipy (for TOST calculations)

---

## Credits

**Created**: January 2026
**Combat Lab System**: Claude + User collaboration

---

## Next Steps

1. **Read**: [Quick Start Guide](QUICK_START_GUIDE.md)
2. **Try**: Run a test in Combat Lab UI (`python main.py`)
3. **Create**: Follow Quick Start to create your first test
4. **Explore**: Read [Main Documentation](COMBAT_LAB_DOCUMENTATION.md) for deep dive
