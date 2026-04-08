# Inspect Galaxy

Comprehensive galaxy generation inspector that outputs structured stats for balancing feedback.

## Purpose

Generates galaxies using the real game pipeline and produces detailed balance metrics covering planet types, star types, resource distribution, habitability scores, connectivity, storm coverage, spatial distribution, and moon/co-orbital analysis. Outputs structured JSON (optimized for automated parsing) plus human-readable console summaries. Supports single-galaxy inspection, batch comparison across multiple seeds, and optional chart generation.

## Requirements

- `Pillow` (PIL) -- for galaxy map generation with `--charts`
- `matplotlib` -- for chart generation with `--charts`

Both are optional; the tool works without them if `--charts` is not used.

## Usage

```bash
python Tools/inspect_galaxy/inspect_galaxy.py [options]
```

### Arguments

| Argument | Short | Default | Description |
|---|---|---|---|
| `--seed` | | random | RNG seed for reproducibility |
| `--systems` | | 25 | Number of star systems to generate |
| `--type` | | `random` | Galaxy layout type (`random`, `cluster`, `spiral`, `spiral_no_core`, `barred_spiral`, `ring`, `irregular`, `diamond`, `uniform`) |
| `--radius` | | auto | Galaxy radius in hex units (auto-calculated if omitted) |
| `--output` | `-o` | `./output/galaxy_inspect` | Output directory for JSON and charts |
| `--batch` | | off | Batch mode: generate N galaxies and compute aggregate stats |
| `--charts` | | off | Generate PNG charts (planet types, star types, resources, habitability, galaxy map) |
| `-v` / `--verbosity` | | 1 | `0` = JSON only, `1` = console summary, `2` = per-system detailed breakdown |
| `--region-mode` | | `normal` | Inter-region warp mode: `normal`, `limited`, `minimal` |

### Examples

```bash
# Basic inspection
python Tools/inspect_galaxy/inspect_galaxy.py --seed 42

# Spiral galaxy with 100 systems and charts
python Tools/inspect_galaxy/inspect_galaxy.py --seed 42 --systems 100 --type spiral --charts

# Batch mode: 10 galaxies for aggregate statistics
python Tools/inspect_galaxy/inspect_galaxy.py --batch 10 --seed 1000 --type cluster

# JSON-only output (no console summary)
python Tools/inspect_galaxy/inspect_galaxy.py --seed 42 -v 0
```

## Output

### JSON (always produced)

Saved to `{output_dir}/galaxy_{seed}.json` (single mode) or `{output_dir}/batch_{seed}_{N}runs.json` (batch mode).

Single-galaxy JSON structure:
- `metadata` -- seed, type, radius, generation time
- `galaxy.systems[]` -- full star, planet, storm, and warp point data per system
- `balance_metrics` -- aggregate statistics (see below)

### Balance Metrics

| Category | Details |
|---|---|
| Planet type distribution | Count and percentage for each PlanetType |
| Star type distribution | Count and percentage for each StarType |
| Resource distribution | Per-resource quantity/quality stats (min/max/avg/stddev) |
| Habitability | Earth-like reference score distribution with 10-bucket histogram |
| System richness | Planets per system, resources per system, storms per system |
| Storm coverage | Systems with storms, storm type breakdown, total storm hexes |
| Connectivity | Warp lane count, connections per system, isolated systems, inter/intra-region breakdown |
| Spatial distribution | System distances, systems per region |
| Moons/co-orbitals | Occupied hexes, moon counts, bodies-per-hex histogram |

### Charts (with `--charts`)

Saved to `{output_dir}/charts/`:
- `planet_types.png` -- planet type histogram
- `star_types.png` -- star type histogram
- `resource_distribution.png` -- resource quantity box plots
- `habitability.png` -- habitability score histogram
- `galaxy_map.png` -- top-down galaxy map with region coloring

Batch mode produces additional cross-run comparison charts (`batch_resources.png`, `batch_planet_counts.png`, `batch_habitability.png`).

### Console Summary (verbosity >= 1)

Printed to stdout: planet/star type distributions, resource tables, habitability stats, connectivity, storm coverage, and moon analysis. Verbosity 2 adds per-system breakdowns with individual star, planet, and storm details.
