# Validate Designs

Validates ship and complex design JSON files against the component registry.

## Purpose

Catches design errors before they cause runtime failures. Checks each design for component existence, crew housing sufficiency, life support sufficiency, layer mass budgets, and mass consistency with `expected_stats`. Use this after editing design files or adding new components.

## Requirements

No additional dependencies beyond the base project.

## Usage

```bash
python Tools/validate_designs/validate_designs.py [directory]
```

### Arguments

| Argument    | Description                                                                  |
|-------------|------------------------------------------------------------------------------|
| `directory` | Path to a directory containing `.json` design files. Optional; defaults to `tests/fixtures/quickstart/designs/`. |

## Checks Performed

- **Component existence** -- All referenced components exist in the game registry.
- **Crew housing** -- Design provides enough crew quarters for its crew requirements.
- **Life support** -- Design provides enough life support modules.
- **Layer mass budgets** -- Components fit within their layer's mass allowance.
- **Mass consistency** -- If the design has `expected_stats.mass`, the calculated mass from `Ship.recalculate_stats()` must match (within 0.5 tolerance).

## Output

Per-design pass/fail status with detailed error and warning messages:

```
  [PASS] Frigate (frigate.json)
  [FAIL] Battleship (battleship.json)
        ERROR: Component 'nonexistent_gun' not found in registry
        WARN:  Layer ARMOR is 95% full

3 designs checked: 1 errors, 1 warnings
```

## Exit Code

- `0` if all designs are valid.
- `1` if any design has errors.
