# Fix Designs

Automatically fixes common design validation errors and recalculates `expected_stats`.

## Purpose

When designs fail validation due to missing crew quarters or life support modules, this tool adds the necessary components to the CORE layer and recalculates all `expected_stats` fields. Useful after bulk component changes or when creating new designs that need stats populated.

## Requirements

No additional dependencies beyond the base project.

## Usage

```bash
python Tools/fix_designs/fix_designs.py [directory]
```

### Arguments

| Argument    | Description                                                                  |
|-------------|------------------------------------------------------------------------------|
| `directory` | Path to a directory containing `.json` design files. Optional; defaults to `data/designs/`. |

## Fixes Applied

- **Crew housing deficit** -- Adds `crew_quarters` components to the CORE layer (10 crew per module).
- **Life support deficit** -- Adds `life_support` components to the CORE layer (25 capacity per module).
- **Expected stats** -- Recalculates and writes `max_hp`, `mass`, `max_speed`, `acceleration_rate`, `turn_speed`, and `total_thrust` using `Ship.recalculate_stats()` as the single source of truth.

## Output

Per-design summary of changes made:

```
  [FIXED] Battleship: +2 crew_quarters (was short 15), updated expected_stats
  [OK]    Frigate: no changes needed

3 designs processed.
```

Design files are modified in-place.
