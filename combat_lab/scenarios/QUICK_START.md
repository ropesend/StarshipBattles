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

    def validate(self, outcome, telemetry=None) -> list:
        """Return Check objects consuming the finalized BattleOutcome.

        `outcome` is the frozen `BattleOutcome` DTO from `run_battle`;
        `telemetry` is an optional `CombatLabTelemetry` bundle with
        per-tick forensic data (projectile tracks, per-weapon shots).
        """
        checks = self._template_preconditions(outcome, telemetry)
        checks.append(check_exact("Target Mass", 400, self.target.mass))
        checks.append(check_tost("Hit Rate", 0.5318,
                                  successes=int(self.damage_dealt),
                                  trials=outcome.duration_ticks, margin=0.06))
        return checks
```

The template handles spec compilation, ship materialization, per-tick
firing, and result collection automatically. You only write validation
logic.

## Lifecycle

1. **`to_spec(registries)`** — Template compiles the scenario into a
   `BattleSpec` (inherits default shape; override for custom specs)
2. **`wire_ships(ships_by_role, engine, initial_state)`** — Template
   binds `self.attacker` / `self.target` from the materialized role dict
3. **`custom_setup(engine)`** — Optional hook for per-scenario tweaks
4. **`run_battle`** drives the tick loop; template's `per_tick` hook
   fires the weapon and captures forensic telemetry
5. **`validate(outcome, telemetry)`** — You return a list of `Check`
   objects. The template populates `self.damage_dealt`, `self.results`, etc.
   before calling you.

## Check Functions

Import from `combat_lab.scenarios.validation`:

| Function | Purpose | Default Phase |
|----------|---------|---------------|
| `check_exact(name, expected, actual)` | Exact equality | `data` |
| `check_approx(name, expected, actual, tolerance)` | Float within relative tolerance | `outcome` |
| `check_tost(name, expected_p, successes, trials, margin)` | TOST equivalence test | `outcome` |
| `check_true(name, condition)` | Boolean precondition | `precondition` |

A test passes only when ALL checks pass. If any fail, `ValidationReport.failed_phase` identifies which phase broke first.

## Complete Working Example

**File**: `combat_lab/scenarios/my_beam_test.py`

```python
"""Point-blank beam accuracy test."""

from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.validation import check_exact, check_tost, check_true
from combat_lab.scenarios.templates import StaticTargetScenario
from combat_lab.test_constants import (
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
        tags=["beam", "accuracy", "point-blank"],
    )

    # Template configuration -- no need to write setup() or update()
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 50

    def custom_setup(self, engine):
        """Hook called after engine.start_teams(). Calculate expected hit chance."""
        from combat_lab.scenarios.beam_scenarios import compute_beam_hit_chance
        self.expected_hit_chance = compute_beam_hit_chance(self)

    def validate(self, outcome, telemetry=None) -> list:
        """Consume the finalized BattleOutcome + Combat Lab telemetry."""
        checks = self._template_preconditions(outcome, telemetry)

        # Data phase: verify loaded ship stats (accessible via wire_ships bindings)
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
            trials=outcome.duration_ticks,
            margin=STANDARD_MARGIN,
        ))
        return checks
```

## Running Tests

Scenario files in `combat_lab/scenarios/` are auto-discovered by `run_tests.py` (it globs `*_scenarios.py`). No wrapper needed -- just create your scenario file and run:

```bash
# Run all simulation tests
python -m combat_lab.run_tests

# Filter by test ID prefix
python -m combat_lab.run_tests MYTEST

# Run specific test
python -m combat_lab.run_tests MYTEST-001

# Skip high-tick tests (fast mode)
python -m combat_lab.run_tests --fast

# List all registered tests
python -m combat_lab.run_tests --list

# Skip writing to combat_lab/test_history/ shards
python -m combat_lab.run_tests --no-history
```

## Key Points

- **Extend `StaticTargetScenario`**, not raw `TestScenario` -- it handles setup/update/collect_results
- **Implement `validate()`**, not `verify()` -- return `list[Check]`, not `bool`
- **`collect_results()` runs automatically** before `validate()` -- use `self.damage_dealt`, `self.results['ticks_run']`, etc.
- **Use `custom_setup()`** for scenario-specific initialization (called at end of template setup)
- **Use `_template_preconditions()`** as the first line of `validate()` for standard sanity checks
- **Use `get_ability(ship, 'ClassName')`** to extract ability instances from loaded ships

## See Also

- `templates.py` -- All available templates (StaticTargetScenario, DuelScenario, PropulsionScenario, ResourceScenario, ComparisonScenario)
- `ComparisonScenario` -- A/B comparison: runs baseline + variant battles, compares outcomes.
  Used by ability-specific tests (ToHit*, Shield*, Emissive*, CNC, SRA, Pipeline).
  See `templates.py` for configuration attributes.
- `beam_scenarios.py` -- Production examples using the parametrized `BeamAccuracyScenario` pattern
- `validation.py` -- Check, ValidationReport, and all check functions
- `../test_constants.py` -- Centralized constants (margins, distances, weapon stats)
