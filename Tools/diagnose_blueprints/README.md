# Diagnose Blueprints

Verification tool that tests star system blueprints against expected generation outcomes.

## Purpose

Generates multiple star systems from each blueprint definition and checks whether the results match expected characteristics (star counts, planet counts, star types, presence of gas giants, hot Jupiters, etc.). Use this after modifying blueprint data or the generation pipeline to catch regressions.

## Requirements

No additional dependencies beyond the base project.

## Usage

```bash
python Tools/diagnose_blueprints/diagnose_blueprints.py
```

### Arguments

| Argument | Short | Default | Description |
|---|---|---|---|
| `--samples` | `-n` | 3 | Number of sample systems to generate per blueprint |
| `--quiet` | `-q` | off | Suppress detailed per-system output (show summaries only) |

### Examples

```bash
# Quick check with default 3 samples
python Tools/diagnose_blueprints/diagnose_blueprints.py

# Thorough test with 10 samples per blueprint
python Tools/diagnose_blueprints/diagnose_blueprints.py -n 10

# Summary-only mode
python Tools/diagnose_blueprints/diagnose_blueprints.py -q
```

## Blueprints Tested

The tool validates these blueprint types against hardcoded expectations:

| Blueprint | Expected Characteristics |
|---|---|
| `binary_no_planets` | 2 stars, 0-1 planets |
| `solar_like` | 1 G/K star (0.5-1.5 Msol), 4-8 planets |
| `red_dwarf_pack` | 1 red dwarf (0.08-0.5 Msol), 5-10 small planets |
| `empty_warp_hub` | 1 star, 0-1 planets |
| `gas_giant_system` | 1 star (0.8-3.0 Msol), 2-5 planets, majority gas giants |
| `trinary_system` | 3 stars, 0-3 planets |
| `quad_system` | 4 stars, 0-1 planets |
| `hot_jupiter` | 1 F/G star, 1-3 planets with a gas giant in close orbit |

## Output

Prints a per-blueprint pass/fail summary to stdout with issue counts and descriptions. Each check shows `[OK]` or `[FAIL]` with occurrence frequency across samples.

Final summary lists all blueprints with overall PASS/FAIL status and total issue count.
