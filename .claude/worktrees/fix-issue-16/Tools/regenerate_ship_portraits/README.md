# regenerate_ship_portraits

Generate and audit ship-theme portrait assets for the PROJ-314 `theme.json`
schema.

## Purpose

This tool backfills missing ship portraits through the `ImageProvider`
abstraction, using OpenAI `gpt-image-2` by default. It is intended for
ship themes under `assets/ShipThemes/<Theme>/` that already use the
canonical `assets:` manifest schema.

## Requirements

No additional dependencies beyond the base project development environment.
Generation requires `OPENAI_API_KEY` in the environment.

## Usage

Run from the repository root with either invocation form:

```powershell
python -m Tools.regenerate_ship_portraits.cli --theme Aetherwake
python Tools/regenerate_ship_portraits/cli.py --theme Aetherwake
```

Run the audit script separately:

```powershell
python -m Tools.regenerate_ship_portraits.audit
python Tools/regenerate_ship_portraits/audit.py
```

## Flags

- `--theme` -- restrict work to one ship theme.
- `--ship-class` -- restrict work to one ship class; requires `--theme`.
- `--dry-run` -- print the planned generations without calling the provider.
- `--force` -- regenerate even when the target portrait file exists.
- `--cost-cap` -- maximum estimated spend for one run, default `$5.00`.
- `--model` -- image model, default `gpt-image-2`.
- `--size` -- requested output size, default `2048x2048`.
- `--batch` -- batch label written to the last-run manifest.
- `--list-themes` -- print discoverable theme names and exit.
- `--list-classes` -- print canonical ship classes and exit.
- `--verbose` -- enable verbose logging.

## Output

The CLI prints a per-request run summary to stdout and writes
`Tools/regenerate_ship_portraits/last_run.json`. Generated portraits are
written to the `portrait` path declared in each theme's `theme.json`.

The audit script prints coverage, filename-casing, and image-size findings
for each theme. Use `--json` for machine-readable output.

## Cost

The default estimate is `$0.04` per generated `2048x2048` portrait. The
tool enforces `--cost-cap` before generation starts; adjust
`--cost-per-image` when provider pricing changes.

## Examples

```powershell
python -m Tools.regenerate_ship_portraits.cli --list-themes
python -m Tools.regenerate_ship_portraits.cli --theme Aetherwake --dry-run
python -m Tools.regenerate_ship_portraits.cli --theme Atlantians --ship-class "Light Cruiser"
python -m Tools.regenerate_ship_portraits.cli --theme Aetherwake --force --cost-cap 10
python -m Tools.regenerate_ship_portraits.audit --theme Federation
```
