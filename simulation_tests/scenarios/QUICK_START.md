# Quick Start: Creating a Test Scenario

This guide shows how to create a test scenario using the template pattern.

## The Pattern

Every weapon accuracy test extends `StaticTargetScenario` and implements `validate()`:

```python
class MyTest(StaticTargetScenario):
    metadata = TestMetadata(...)

    # Template configuration (replaces manual setup/update)
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 50  # center-to-center pixels

    def validate(self, engine) -> list:
        """Return Check objects. Called after collect_results() populates self.damage_dealt, etc."""
        checks = self._template_preconditions()
        checks.append(check_exact("Target Mass", 400, self.target.mass))
        checks.append(check_tost("Hit Rate", 0.5318, successes=int(self.damage_dealt),
                                  trials=engine.tick_counter, margin=0.06))
        return checks
```

The template handles `setup()`, `update()`, and `collect_results()` automatically.
You only write validation logic.

## Lifecycle

1. **`setup()`** -- Template loads ships, positions them, starts the battle engine
2. **`update()`** -- Template fires the weapon each tick (`force_fire=True` by default)
3. **`collect_results()`** -- Template populates `self.damage_dealt`, `self.results['ticks_run']`, etc.
4. **`validate()`** -- You return a list of `Check` objects (the framework calls `collect_results()` first)

## Check Functions

Import from `simulation_tests.scenarios.validation`:

| Function | Purpose | Default Phase |
|----------|---------|---------------|
| `check_exact(name, expected, actual)` | Exact equality | `data` |
| `check_approx(name, expected, actual, tolerance)` | Float within relative tolerance | `outcome` |
| `check_tost(name, expected_p, successes, trials, margin)` | TOST equivalence test | `outcome` |
| `check_true(name, condition)` | Boolean precondition | `precondition` |

A test passes only when ALL checks pass. If any fail, `ValidationReport.failed_phase` identifies which phase broke first.

## Complete Working Example

**File**: `simulation_tests/scenarios/my_beam_test.py`

```python
"""Point-blank beam accuracy test."""

from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.validation import check_exact, check_tost, check_true
from simulation_tests.scenarios.templates import StaticTargetScenario
from simulation_tests.test_constants import (
    STANDARD_TEST_TICKS, STANDARD_MARGIN, STANDARD_SEED,
    BEAM_LOW_DAMAGE, STATIONARY_TARGET_MASS,
)


class MyBeamPointBlankTest(StaticTargetScenario):
    """MYTEST-001: Low accuracy beam at point-blank range."""

    metadata = TestMetadata(
        test_id="MYTEST-001",
        category="MyTests",
        subcategory="Beam Accuracy",
        name="Low Accuracy Beam - Point Blank",
        summary="Validates low accuracy beam hit rate at 50px",
        conditions=["Distance: 50px", "Weapon: Low Accuracy Beam", "Target: Stationary, 400 tons"],
        edge_cases=["Minimal range penalty"],
        expected_outcome="Hit rate ~53% (TOST equivalence within +/-10%)",
        pass_criteria="TOST p < 0.05",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["beam", "accuracy", "point-blank"],
    )

    # Template configuration -- no need to write setup() or update()
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 50

    def custom_setup(self, battle_engine):
        """Hook called at end of template setup. Calculate expected hit chance."""
        from simulation_tests.scenarios.beam_scenarios import compute_beam_hit_chance
        self.expected_hit_chance = compute_beam_hit_chance(self)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data phase: verify loaded ship stats
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks
        checks.append(check_exact("Beam Damage", BEAM_LOW_DAMAGE, beam.damage))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))

        # Outcome phase: TOST equivalence test on hit rate
        checks.append(check_tost(
            "Hit Rate",
            self.expected_hit_chance,
            successes=int(self.damage_dealt),
            trials=engine.tick_counter,
            margin=STANDARD_MARGIN,
        ))
        return checks
```

**Pytest wrapper**: `simulation_tests/tests/test_my_beam.py`

```python
"""Pytest wrapper for MyBeamPointBlankTest."""

import pytest
from test_framework.runner import TestRunner
from simulation_tests.scenarios.my_beam_test import MyBeamPointBlankTest


@pytest.mark.simulation
class TestMyBeam:
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        self.runner = TestRunner()

    def test_MYTEST_001(self):
        result = self.runner.run_scenario(MyBeamPointBlankTest, headless=True)
        assert result.passed, f"Failed: {result.results.get('validation')}"
```

## Running Tests

```bash
# Run all simulation tests
python -m simulation_tests.run_tests

# Filter by test ID prefix
python -m simulation_tests.run_tests MYTEST

# Run specific test
python -m simulation_tests.run_tests MYTEST-001

# List all registered tests
python -m simulation_tests.run_tests --list

# Run via pytest
pytest simulation_tests/tests/test_my_beam.py -v
```

## Key Points

- **Extend `StaticTargetScenario`**, not raw `TestScenario` -- it handles setup/update/collect_results
- **Implement `validate()`**, not `verify()` -- return `list[Check]`, not `bool`
- **`collect_results()` runs automatically** before `validate()` -- use `self.damage_dealt`, `self.results['ticks_run']`, etc.
- **Use `custom_setup()`** for scenario-specific initialization (called at end of template setup)
- **Use `_template_preconditions()`** as the first line of `validate()` for standard sanity checks
- **Use `get_ability(ship, 'ClassName')`** to extract ability instances from loaded ships

## See Also

- `templates.py` -- All available templates (StaticTargetScenario, DuelScenario, PropulsionScenario, ResourceScenario)
- `beam_scenarios.py` -- Production examples using the parametrized `BeamAccuracyScenario` pattern
- `validation.py` -- Check, ValidationReport, and all check functions
- `../test_constants.py` -- Centralized constants (margins, distances, weapon stats)
