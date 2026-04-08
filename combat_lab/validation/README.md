# Validation System

## Overview

The validation system uses four check functions that return `Check` objects,
aggregated into a `ValidationReport`. Validation is split into three phases
so that failures point directly to their root cause.

**Source:** `combat_lab/scenarios/validation.py`

---

## Three Validation Phases

| Phase | Purpose | Typical checks |
|-------|---------|----------------|
| `data` | Loaded JSON matches expectations (ship mass, weapon damage, etc.) | `check_exact` |
| `precondition` | Simulation behaved correctly (weapon fired, target moved) | `check_true` |
| `outcome` | Final results match expectations (hit rate, distance, fuel) | `check_approx`, `check_tost` |

A test passes only when ALL checks across all three phases pass.
`ValidationReport.failed_phase` returns the first phase containing a failure.

---

## Check Functions

### `check_exact(name, expected, actual, phase="data") -> Check`

Exact equality (`==`). Use for integers, strings, or any discrete value.

```python
check_exact("Ship Mass", 400, ship.mass)
check_exact("Team ID", 1, ship.team_id)
```

### `check_approx(name, expected, actual, tolerance=1e-9, phase="outcome") -> Check`

Float comparison within relative tolerance (`|actual - expected| / |expected| <= tolerance`).

```python
check_approx("Max Speed", 31.25, ship.max_speed)
check_approx("Shield Capacity", 500.0, ship.max_shields, tolerance=1e-6)
```

### `check_tost(name, expected_p, successes, trials, margin=0.02, phase="outcome") -> Check`

TOST (Two One-Sided Tests) equivalence test for proportions. Proves the
observed proportion is within `+/- margin` of `expected_p` at 95% confidence.
`p < 0.05` means equivalence is proven (PASS). Requires `scipy`.

Scipy's `norm.cdf()` returns `numpy.float64`, so `check_tost` explicitly casts
the p-value to `float()` and the pass/fail result to `bool()` before constructing
the `Check`. This prevents numpy types from leaking into downstream serialization.

```python
check_tost("Hit Rate", expected_p=0.5318, successes=260, trials=500, margin=0.06)
```

### `check_true(name, condition, actual=None, detail="", phase="precondition") -> Check`

Boolean precondition check. Use for any true/false assertion.

```python
check_true("Weapon Fired", ticks_fired > 0)
check_true("Target Alive", target.hp > 0, actual=target.hp)
```

---

## Data Model

### `Check`

Dataclass with fields: `phase`, `name`, `expected`, `actual`, `passed`, `detail`.

`__post_init__` coerces `passed` to native Python `bool`. This is necessary
because `check_tost` uses scipy, which returns `numpy.bool_` from comparisons
— a type that is not JSON-serializable. The coercion happens at the data-model
boundary so all consumers (serialization, UI, history) receive a native `bool`.

### `_safe_serialize(value)`

Converts `expected` and `actual` values to JSON-safe types for
`ValidationReport.to_dict()`. Handles:

- Native Python types (`bool`, `int`, `float`, `str`, `None`) — passed through
- `float('nan')` — converted to `None`
- Numpy scalars (`float64`, `int64`, `bool_`) — coerced to native Python via `.item()`
- `dict` — recursively serialized
- `list` / `tuple` — recursively serialized
- Unknown types — converted to `str(value)`

Numpy scalars are checked **first** (before `isinstance` checks on native types)
because `numpy.float64` is a subclass of Python `float` and would otherwise pass
through unconverted.

### `ValidationReport`

Holds a list of `Check` objects. Key members:

| Member | Description |
|--------|-------------|
| `checks` | List of all `Check` objects |
| `passed` | `True` only when every check passes |
| `failed_phase` | First phase containing a failure, or `None` |
| `phase_checks(phase)` | Returns checks for a specific phase |
| `summary()` | Dict of `{phase: {total, passed, failed}}` |
| `to_dict()` | JSON-serializable representation |

---

## Usage in Scenarios

Scenarios implement a `validate(engine)` method that returns a list of `Check`
objects. The runner collects these into a `ValidationReport`.

```python
def validate(self, engine) -> List[Check]:
    checks = []

    # Phase 1: data — verify loaded values match expectations
    checks.append(check_exact("Weapon Damage", 1, self.attacker.weapon.damage))
    checks.append(check_exact("Target Mass", 400, self.target.mass))

    # Phase 2: precondition — verify simulation ran correctly
    checks.append(check_true("Ticks Ran", engine.tick_count > 0))

    # Phase 3: outcome — verify results
    damage_dealt = self.initial_hp - self.target.hp
    checks.append(check_tost(
        "Hit Rate",
        expected_p=0.5318,
        successes=damage_dealt,
        trials=engine.tick_count,
        margin=0.06,
    ))

    return checks
```

---

## TOST Margin Guidelines

| Ticks | Standard Error (p~0.5) | Recommended Margin |
|-------|------------------------|--------------------|
| 500 | ~2.2–4.4% | +/-10% |
| 10,000 | ~0.5% | +/-2% |
| 100,000 | ~0.16% | +/-1% |

Margin should be at least 2.5–3x the standard error for reliable testing.
The 500-tick margin was increased from 6% to 10% because low-accuracy beam
tests near 50% hit rate have SE ~4.4%, making 6% only ~1.4x SE (45% failure rate).
