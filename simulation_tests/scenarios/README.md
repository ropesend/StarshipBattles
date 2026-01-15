# Test Scenarios

## Overview

This directory contains all test scenario implementations for Combat Lab.

## Current Scenario Files

### beam_scenarios.py

Complete test suite for beam weapon mechanics (18 tests).

**Test Categories**:
- Accuracy tests (point blank, mid-range, max range)
- Moving target tests (erratic small targets)
- Boundary tests (out of range)
- High-tick precision tests (100k ticks)

**See**: Full beam weapon test documentation below.

## Beam Weapon Tests

### Test Suite Overview (18 Total Tests)

#### Standard Tests (11 tests, 500 ticks, ±6% margin)

| Test ID | Weapon | Distance | Target | Expected Hit Rate |
|---------|--------|----------|--------|-------------------|
| BEAM360-001 | Low Acc | 50px PB | Stat. 400 | 53.18% |
| BEAM360-002 | Low Acc | 400px MR | Stat. 400 | 36.06% |
| BEAM360-003 | Low Acc | 750px Max | Stat. 400 | 21.86% |
| BEAM360-004 | Med Acc | 50px PB | Stat. 400 | 83.86% |
| BEAM360-005 | Med Acc | 400px MR | Stat. 400 | 78.55% |
| BEAM360-006 | Med Acc | 750px Max | Stat. 400 | 72.07% |
| BEAM360-007 | High Acc | 50px PB | Stat. 400 | 99.06% |
| BEAM360-008 | High Acc | 750px Max | Stat. 400 | 98.66% |
| BEAM360-009 | Med Acc | 400px MR | Erratic 65 | 4.84% |
| BEAM360-010 | Med Acc | 750px Max | Erratic 65 | 3.47% |
| BEAM360-011 | Low Acc | 900px OOR | Stat. 400 | 0% (deterministic) |

#### High-Tick Tests (7 tests, 100k ticks, ±1% margin)

| Test ID | Weapon | Distance | Target | Expected Hit Rate |
|---------|--------|----------|--------|-------------------|
| BEAM360-001-HT | Low Acc | 50px PB | Stat. 600 | 57.02% |
| BEAM360-002-HT | Low Acc | 400px MR | Stat. 600 | 39.71% |
| BEAM360-004-HT | Med Acc | 50px PB | Stat. 600 | 85.82% |
| BEAM360-005-HT | Med Acc | 400px MR | Stat. 600 | 80.98% |
| BEAM360-006-HT | Med Acc | 750px Max | Stat. 600 | 75.00% |
| BEAM360-007-HT | High Acc | 50px PB | Stat. 600 | 99.19% |
| BEAM360-008-HT | High Acc | 750px Max | Stat. 600 | 98.85% |

### Critical Implementation Details

#### Surface Distance Calculation

**ALWAYS use surface distance, not center-to-center distance:**

```python
# Target radius formula
target_radius = 40 * (mass / 1000) ** (1/3)

# Surface distance (what beam weapon actually uses)
surface_distance = center_distance - target_radius

# Use this in expected hit chance calculation!
expected_hit_chance = calculate_expected_hit_chance(
    base_acc, falloff, surface_distance, attack_bonus, defense_penalty
)
```

**Why**: Beam weapons use raycasting to find intersection with target's collision circle. The hit distance is to the circle surface, not the center.

#### Helper Functions

Located at top of `beam_scenarios.py`:

```python
def calculate_defense_score(mass, acceleration, turn_speed, ecm_score):
    """Calculate target defense score."""
    size_score = 0.5 * (1.0 - (mass / 1000.0))
    maneuver_score = (acceleration / 1000.0) + (turn_speed / 500.0)
    return size_score + maneuver_score + ecm_score

def calculate_expected_hit_chance(base_acc, falloff, distance,
                                  attack_bonus, defense_penalty):
    """Calculate beam weapon hit chance using sigmoid formula."""
    range_penalty = distance * falloff
    net_score = (base_acc + attack_bonus) - (range_penalty + defense_penalty)
    return 1.0 / (1.0 + math.exp(-net_score))
```

## See Also

- **Main Documentation**: `../COMBAT_LAB_DOCUMENTATION.md` - Complete system overview
- **Quick Start**: `../QUICK_START_GUIDE.md` - Create your first test in 10 minutes
- **Test Framework**: `../../test_framework/README.md` - Architecture details
- **Validation**: `../validation/README.md` - TOST and validation rules
- **Data Files**: `../data/README.md` - Components and ship configurations
