# Galaxy Screenshot

Headless galaxy screenshot generator using Pillow for rendering (no display needed).

## Purpose

Generates galaxy layouts using the real game generation pipeline and saves them as PNG screenshots for visual review. Supports single-galaxy and batch modes, with options for warp lane visibility, region coloring, and inter-region warp lane control. Use this for rapid visual feedback when tuning galaxy generation parameters.

## Requirements

- `Pillow` (PIL)

## Usage

```bash
python Tools/galaxy_screenshot/galaxy_screenshot.py [options]
```

### Arguments

| Argument | Short | Default | Description |
|---|---|---|---|
| `--type` | `-t` | `spiral` | Galaxy type (`spiral`, `cluster`, `random`, `spiral_no_core`, `barred_spiral`, `ring`, `irregular`, `diamond`, `uniform`) |
| `--count` | `-c` | 250 | Number of star systems |
| `--radius` | `-r` | auto | Galaxy radius in hex units (auto-calculated from count if omitted) |
| `--seed` | `-s` | random | Random seed for reproducibility |
| `--no-warp` | | off | Hide warp lane lines |
| `--batch` | | off | Run batch mode across multiple galaxy types and sizes |
| `--output` | `-o` | `docs/screenshots/galaxy` | Output directory (relative to project root) |
| `--region-mode` | `-m` | `auto` | Inter-region warp mode: `normal`, `limited`, `minimal`, or `auto` |

### Examples

```bash
# Single spiral galaxy with 250 systems
python Tools/galaxy_screenshot/galaxy_screenshot.py --type spiral --count 250 --seed 12345

# Cluster galaxy without warp lines
python Tools/galaxy_screenshot/galaxy_screenshot.py --type cluster --count 500 --no-warp

# Batch mode: generates spiral, cluster, and random at 50/250/1000 systems each
python Tools/galaxy_screenshot/galaxy_screenshot.py --batch --seed 42

# Minimal inter-region warp connections
python Tools/galaxy_screenshot/galaxy_screenshot.py --type spiral --count 250 --region-mode minimal
```

## Output

Saves 1920x1080 PNG images to the output directory. Filenames encode the parameters:

```
{type}_{count}_{warp|nowarp}_{regionmode}_seed{seed}.png
```

Systems are color-coded by region. Warp lanes are drawn in dark blue (intra-region) and bright red (inter-region). Batch mode produces both warp and no-warp variants for each combination.
